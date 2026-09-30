"""
Unit and Integration Tests for Google Gemini AI Service and Routes
"""
import sys
import os
import pytest
import json
from unittest.mock import patch, MagicMock

# Ensure backend directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app import create_app
from utils.db import init_db
from utils.seed_data import seed_demo_data

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            init_db()
            seed_demo_data()
        yield client

def test_explain_risk_fallback(client):
    payload = {
        "region_name": "South 24 Parganas",
        "cyclone_name": "Amphan",
        "risk_payload": {
            "vulnerability_score": 84.5,
            "risk_category": "EXTREME",
            "infrastructure_summary": {"hospitals": 4, "shelters": 3, "power_facilities": 2},
            "contributing_factors": [{"factor": "Wind", "description": "High wind velocity"}]
        }
    }
    response = client.post('/api/ai/explain', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    res = data['data']
    assert 'summary' in res
    assert 'risk_factors' in res
    assert 'priority_infrastructure' in res
    assert 'recommended_actions' in res
    assert 'uncertainty' in res

def test_chat_assistant_success(client):
    payload = {
        "query": "Why is this area high risk?",
        "context": {
            "vulnerability_score": 84.5,
            "risk_category": "EXTREME",
            "cyclone_name": "Amphan"
        }
    }
    response = client.post('/api/ai/chat', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'answer' in data['data']
    assert data['data']['query'] == "Why is this area high risk?"

def test_chat_assistant_missing_query(client):
    response = client.post('/api/ai/chat', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert data['error']['code'] == 'MISSING_PARAMETER'

def test_scenario_analysis(client):
    payload = {
        "base_cyclone_id": "amphan_2020",
        "baseline": {"vulnerability_score": 84.5},
        "simulated": {"vulnerability_score": 92.1},
        "delta": {"score_delta": 7.6, "is_increased_risk": True}
    }
    response = client.post('/api/ai/scenario-analysis', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'scenario_analysis' in data['data']

def test_generate_advisory(client):
    payload = {
        "cyclone_name": "AMPHAN",
        "vulnerability_score": 84.5,
        "risk_category": "EXTREME"
    }
    response = client.post('/api/ai/advisory', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    res = data['data']
    assert 'advisory_markdown' in res
    assert 'disclaimer' in res
    assert "NOT AN OFFICIAL GOVERNMENT ORDER" in res['disclaimer']
    assert "NOT AN OFFICIAL GOVERNMENT ORDER" in res['advisory_markdown']

def test_satellite_analysis(client):
    payload = {
        "cyclone_id": "amphan_2020",
        "risk_payload": {"vulnerability_score": 84.5}
    }
    response = client.post('/api/ai/satellite-analysis', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'findings' in data['data']

@patch('services.gemini_service.genai.Client')
@patch.dict(os.environ, {"GEMINI_API_KEY": "test_mock_api_key"})
def test_explain_risk_with_mocked_gemini(mock_client_cls, client):
    # Setup mock return
    mock_client_instance = MagicMock()
    mock_client_cls.return_value = mock_client_instance

    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "summary": "Mocked Gemini summary for test region.",
        "risk_factors": ["High wind speed 115kt", "Storm surge inundation"],
        "priority_infrastructure": ["Kakdwip Hospital"],
        "recommended_actions": ["Evacuate coastal belt"],
        "uncertainty": ["Dynamic track shift probability"]
    })
    mock_client_instance.models.generate_content.return_value = mock_response

    payload = {
        "region_name": "South 24 Parganas",
        "cyclone_name": "Amphan",
        "risk_payload": {"vulnerability_score": 84.5, "risk_category": "EXTREME"}
    }
    
    with patch('services.gemini_service.GENAI_AVAILABLE', True):
        response = client.post('/api/ai/explain', json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        res = data['data']
        assert res['summary'] == "Mocked Gemini summary for test region."
        assert len(res['risk_factors']) == 2

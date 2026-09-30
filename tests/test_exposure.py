"""
Unit Tests for Infrastructure Exposure Service & Endpoints
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app import create_app
from services.exposure_service import ExposureService
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

def test_calculate_exposure_service(client):
    with client.application.app_context():
        result = ExposureService.calculate_exposure(cyclone_id='amphan_2020', buffer_km=50.0)
        assert result is not None
        assert result['cyclone_id'] == 'amphan_2020'
        assert 'summary_counts' in result
        counts = result['summary_counts']
        assert counts['hospitals'] > 0
        assert counts['shelters'] > 0
        assert counts['power_facilities'] > 0
        assert counts['exposed_road_distance_km'] >= 0.0
        assert counts['exposed_railway_distance_km'] >= 0.0
        assert 'exposed_infrastructure' in result
        assert len(result['exposed_infrastructure']) > 0

def test_exposed_asset_item_attributes(client):
    with client.application.app_context():
        result = ExposureService.calculate_exposure(cyclone_id='amphan_2020', buffer_km=50.0)
        assets = result['exposed_infrastructure']
        for item in assets:
            assert 'id' in item
            assert 'name' in item
            assert 'type' in item
            assert 'coordinates' in item
            assert 'risk_score' in item
            assert 0.0 <= item['risk_score'] <= 100.0
            assert item['risk_level'] in ['LOW', 'MODERATE', 'HIGH', 'EXTREME']
            assert 'exposure_reason' in item
            assert len(item['exposure_reason']) > 10

def test_exposure_service_filtering(client):
    with client.application.app_context():
        res_hosp = ExposureService.calculate_exposure(cyclone_id='amphan_2020', buffer_km=50.0, category_filter='hospital')
        for item in res_hosp['exposed_infrastructure']:
            assert item['type'] == 'hospital'

        res_extreme = ExposureService.calculate_exposure(cyclone_id='amphan_2020', buffer_km=50.0, risk_level_filter='EXTREME')
        for item in res_extreme['exposed_infrastructure']:
            assert item['risk_level'] == 'EXTREME'

def test_api_infrastructure_exposed_endpoint(client):
    response = client.get('/api/infrastructure/exposed?cyclone_id=amphan_2020&buffer_km=50.0')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    res = data['data']
    assert res['cyclone_id'] == 'amphan_2020'
    assert 'summary_counts' in res
    assert 'exposed_infrastructure' in res

def test_api_infrastructure_exposed_filtering(client):
    response = client.get('/api/infrastructure/exposed?cyclone_id=amphan_2020&category=shelter&risk_level=HIGH')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    res = data['data']
    for item in res['exposed_infrastructure']:
        assert item['type'] == 'shelter'
        assert item['risk_level'] == 'HIGH'

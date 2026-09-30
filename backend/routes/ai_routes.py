"""
Google Gemini AI REST API Route Blueprint
Exposes risk explanation, grounded chat, scenario analysis, advisory generation, and satellite interpretation endpoints.
"""
from flask import Blueprint, request
from services.gemini_service import GeminiService
from utils.response import success_response, error_response

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/ai/explain', methods=['POST'])
@ai_bp.route('/v1/ai/explain', methods=['POST'])
def explain_risk():
    try:
        payload = request.get_json() or {}
        res = GeminiService.explain_risk(payload)
        return success_response(
            data=res,
            message="Generated structured AI risk explanation."
        )
    except Exception as e:
        return error_response(
            code="AI_EXPLAIN_ERROR",
            message=f"Failed to generate risk explanation: {str(e)}",
            status_code=500
        )

@ai_bp.route('/ai/chat', methods=['POST'])
@ai_bp.route('/v1/ai/chat', methods=['POST'])
def chat_assistant():
    try:
        payload = request.get_json() or {}
        query = payload.get('query') or payload.get('user_query') or payload.get('question')
        if not query or not str(query).strip():
            return error_response(
                code="MISSING_PARAMETER",
                message="Please enter a message.",
                status_code=400
            )
        context = payload.get('context') or payload.get('risk_payload') or {}
        history = payload.get('history') or []
        print(f"AI USER QUESTION: '{query}' [History items: {len(history)}]")
        res = GeminiService.chat_assistant(query, context, history=history)
        return success_response(
            data=res,
            message="Conversational AI response generated."
        )
    except Exception as e:
        print(f"Error in AI Chat endpoint: {e}")
        return error_response(
            code="AI_CHAT_ERROR",
            message="Sorry, I couldn't reach the AI service right now. Please try again.",
            status_code=500
        )

@ai_bp.route('/ai/scenario-analysis', methods=['POST'])
@ai_bp.route('/v1/ai/scenario-analysis', methods=['POST'])
def scenario_analysis():
    try:
        payload = request.get_json() or {}
        res = GeminiService.analyze_scenario(payload)
        return success_response(
            data=res,
            message="Generated what-if scenario analysis."
        )
    except Exception as e:
        return error_response(
            code="AI_SCENARIO_ERROR",
            message=f"Failed to analyze scenario: {str(e)}",
            status_code=500
        )

@ai_bp.route('/ai/advisory', methods=['POST'])
@ai_bp.route('/v1/ai/advisory', methods=['POST'])
def generate_advisory():
    try:
        payload = request.get_json() or {}
        res = GeminiService.generate_advisory(payload)
        return success_response(
            data=res,
            message="Generated pre-landfall decision-support advisory."
        )
    except Exception as e:
        return error_response(
            code="AI_ADVISORY_ERROR",
            message=f"Failed to generate emergency advisory: {str(e)}",
            status_code=500
        )

@ai_bp.route('/ai/satellite-analysis', methods=['POST'])
@ai_bp.route('/v1/ai/satellite-analysis', methods=['POST'])
def satellite_analysis():
    try:
        payload = request.get_json() or {}
        res = GeminiService.analyze_satellite(payload)
        return success_response(
            data=res,
            message="Generated multimodal satellite visual interpretation."
        )
    except Exception as e:
        return error_response(
            code="AI_SATELLITE_ERROR",
            message=f"Failed to interpret satellite imagery: {str(e)}",
            status_code=500
        )

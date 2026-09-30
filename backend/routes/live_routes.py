"""
CycloneShield AI - Live Real-Time Data & SSE Stream Routes
Exposes real-time telemetry REST endpoints and Server-Sent Events (SSE) streaming.
"""
import queue
import json
from flask import Blueprint, Response, request, jsonify
from services.live_manager import LiveManager
from services.cyclone_service import LiveCycloneService
from services.weather_service import WeatherService
from utils.response import success_response, error_response

live_bp = Blueprint('live', __name__)

@live_bp.route('/live/status', methods=['GET'])
def get_live_status():
    manager = LiveManager.get_instance()
    state = manager.last_state or manager.update_live_state()
    return success_response(
        data={
            "mode": manager.mode,
            "status": state.get("status", "LIVE"),
            "updated_at": state.get("updated_at"),
            "data_freshness": {
                "cyclone_telemetry": state.get("cyclone", {}).get("status", "LIVE"),
                "weather_telemetry": state.get("weather", {}).get("status", "LIVE"),
                "risk_engine": "COMPUTED",
                "infrastructure_exposure": "COMPUTED"
            }
        },
        message="System real-time telemetry status retrieved."
    )

@live_bp.route('/live/cyclone', methods=['GET'])
def get_live_cyclone():
    res = LiveCycloneService.get_live_cyclone_telemetry()
    return success_response(data=res, message="Live cyclone telemetry retrieved.")

@live_bp.route('/live/weather', methods=['GET'])
def get_live_weather():
    lat = float(request.args.get('lat', 21.7))
    lon = float(request.args.get('lon', 88.3))
    res = WeatherService.fetch_live_weather(lat, lon)
    return success_response(data=res, message="Live regional weather telemetry retrieved.")

@live_bp.route('/live/risk', methods=['GET'])
def get_live_risk():
    manager = LiveManager.get_instance()
    state = manager.last_state or manager.update_live_state()
    return success_response(data=state.get("risk", {}), message="Real-time vulnerability risk calculated.")

@live_bp.route('/live/infrastructure', methods=['GET'])
def get_live_infrastructure():
    manager = LiveManager.get_instance()
    state = manager.last_state or manager.update_live_state()
    return success_response(data=state.get("infrastructure", {}), message="Real-time exposed infrastructure calculated.")

@live_bp.route('/live/mode', methods=['POST'])
def set_live_mode():
    payload = request.get_json() or {}
    new_mode = payload.get('mode', 'LIVE').upper()
    if new_mode not in ['LIVE', 'DEMO']:
        return error_response(code="INVALID_MODE", message="Mode must be 'LIVE' or 'DEMO'.", status_code=400)
    
    manager = LiveManager.get_instance()
    manager.mode = new_mode
    updated_state = manager.update_live_state()
    return success_response(data=updated_state, message=f"Application mode switched to {new_mode}.")

@live_bp.route('/live/stream', methods=['GET'])
def live_sse_stream():
    """
    Server-Sent Events (SSE) Streaming Endpoint.
    Pushes real-time updates directly to connected browser clients without full page reloads.
    """
    def event_stream():
        q = queue.Queue()
        manager = LiveManager.get_instance()
        manager.register_listener(q)
        
        # Send initial state immediately
        initial_state = manager.last_state or manager.update_live_state()
        yield f"data: {json.dumps(initial_state)}\n\n"

        try:
            while True:
                msg = q.get()
                yield msg
        except GeneratorExit:
            manager.unregister_listener(q)

    return Response(event_stream(), content_type='text/event-stream')

"""
Health Check Route Endpoint
"""
from flask import Blueprint
from utils.response import success_response

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
@health_bp.route('/v1/health', methods=['GET'])
def health_check():
    return success_response(
        data={
            "status": "healthy",
            "service": "CycloneShield AI Backend Foundation",
            "version": "1.0.0-mvp",
            "database": "SQLite",
            "is_demo_mode": True
        },
        message="System operational."
    )

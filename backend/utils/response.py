"""
CycloneShield AI - Standardized API Response Helper
"""
import datetime
from flask import jsonify


def success_response(data=None, message="Operation completed successfully.", status_code=200):
    return jsonify({
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }), status_code

def error_response(code="INTERNAL_ERROR", message="An unexpected error occurred.", details=None, status_code=500):
    return jsonify({
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details
        },
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }), status_code


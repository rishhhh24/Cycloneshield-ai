"""
CycloneShield AI - Flask Application Entry Point
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import config_by_name
from utils.db import init_db
from utils.seed_data import seed_demo_data
from utils.response import error_response

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Initialize CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize DB & Seed Demo Data
    with app.app_context():
        try:
            init_db()
            seed_demo_data()
        except Exception as e:
            print(f"Demo data initialization note: {e}")

    # Serve Frontend Single Page App
    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    # Register Blueprints
    from routes.health_routes import health_bp
    from routes.cyclone_routes import cyclone_bp
    from routes.infrastructure_routes import infrastructure_bp
    from routes.forecast_routes import forecast_bp
    from routes.simulation_routes import simulation_bp
    from routes.gee_routes import gee_bp
    from routes.ai_routes import ai_bp
    from routes.live_routes import live_bp
    from routes.location_routes import location_bp

    blueprints = [
        (health_bp, 'health'),
        (cyclone_bp, 'cyclone'),
        (infrastructure_bp, 'infrastructure'),
        (forecast_bp, 'forecast'),
        (simulation_bp, 'simulation'),
        (gee_bp, 'gee'),
        (ai_bp, 'ai'),
        (live_bp, 'live'),
        (location_bp, 'location'),
    ]

    for bp, name in blueprints:
        app.register_blueprint(bp, url_prefix='/api', name=f"{name}_api")
        app.register_blueprint(bp, url_prefix='', name=f"{name}_raw")

    # Start Live Telemetry Update Loop (only when not running on Vercel serverless)
    if not os.getenv('VERCEL') and not os.getenv('AWS_LAMBDA_FUNCTION_NAME'):
        try:
            from services.live_manager import LiveManager
            LiveManager.get_instance().start()
        except Exception as e:
            print(f"LiveManager start note: {e}")



    # Global Error Handlers
    @app.errorhandler(404)
    def handle_404(e):
        return error_response(code="ENDPOINT_NOT_FOUND", message="The requested endpoint does not exist.", status_code=404)

    @app.errorhandler(500)
    def handle_500(e):
        return error_response(code="SERVER_ERROR", message="An unexpected server error occurred.", status_code=500)

    return app

# Expose app WSGI entrypoint for Vercel serverless deployment
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"Starting CycloneShield AI Backend Engine on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)

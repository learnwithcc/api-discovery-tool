"""
API Discovery Tool Flask Application

This is the main Flask application that provides a REST API for the API Discovery Tool.
It orchestrates various endpoints for health monitoring, URL validation, and API discovery
result processing.

Application Architecture:

1. Flask Configuration
   - Debug logging in development mode
   - Production-grade logging in non-debug mode
   - SQLAlchemy for database operations
   - SQLite database for simplicity (can be upgraded to PostgreSQL/MySQL)

2. Blueprints (Modular Route Organization)
   - health_bp (/api/health): Health check endpoint for monitoring
   - validation_bp (/api/validate-url): URL validation and robots.txt checking

3. Middleware and Extensions
   - Flask-Limiter: Rate limiting to prevent API abuse
   - Flask-SQLAlchemy: Database ORM
   - ResultProcessor: API discovery result processing pipeline

4. Rate Limiting Configuration
   - Default: 200 requests per day, 50 requests per hour
   - In-memory storage (consider Redis for production)
   - Per-IP address limiting
   - Custom limits can be applied to specific endpoints

5. Error Handlers
   - 400 Bad Request: Invalid client input
   - 404 Not Found: Endpoint doesn't exist
   - 500 Internal Server Error: Server-side errors with logging

6. Request Logging
   - Logs all incoming requests (method, path, remote address)
   - Optional header and body logging for debugging
   - Helps with troubleshooting and security monitoring

Blueprint URL Prefixes:
   - /api/health -> Health check endpoint
   - /api/validate-url -> URL validation endpoint
   - /api/process -> API discovery result processing endpoint

Main Endpoints:

GET /
    Renders the main web interface (if templates/index.html exists)

POST /api/process
    Processes API discovery results through the processing pipeline
    Rate limit: 60 requests per minute
    Request body:
        {
            "discovery_method": "openapi_spec|mitmproxy|combined_source",
            "data": {...},
            "openapi_spec": {...} (optional),
            "http_interactions": [...] (optional)
        }

Database Configuration:
    - SQLite database: app.db in the application directory
    - SQLALCHEMY_TRACK_MODIFICATIONS: Disabled for performance
    - Database models can be added in api/models.py

Production Deployment Considerations:
    - Use a production WSGI server (Gunicorn, uWSGI)
    - Set debug=False
    - Use environment variables for configuration
    - Implement proper database migrations (Alembic)
    - Use Redis for rate limiting storage
    - Configure proper logging (file rotation, external logging service)
    - Add authentication/authorization middleware
    - Enable CORS if needed for frontend applications
    - Implement request ID tracking for distributed tracing

Environment Variables (Optional):
    - FLASK_ENV: development|production
    - DATABASE_URL: Database connection string
    - SECRET_KEY: Flask secret key for sessions
    - RATE_LIMIT_STORAGE_URL: Redis URL for rate limiting

Usage:
    Development:
        python app.py

    Production:
        gunicorn -w 4 -b 0.0.0.0:5001 app:app
"""

from flask import Flask, jsonify, request, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from api.routes.health import health_bp
from api.routes.validation import validation_bp
from api_discovery_tool.processing import ResultProcessor
import logging
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

# Configure basic logging
if not app.debug:
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize ResultProcessor instance (can be configured further if needed)
result_processor = ResultProcessor(cache_ttl_seconds=3600)

# Initialize Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Register Blueprints
app.register_blueprint(health_bp, url_prefix='/api')
app.register_blueprint(validation_bp, url_prefix='/api')

# Error Handlers
@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({"error": "Bad Request", "message": str(error)}), 400

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found", "message": str(error)}), 404

@app.errorhandler(500)
def internal_server_error(error):
    # Log the error for debugging purposes
    app.logger.error(f'Server Error: {error}', exc_info=True)
    return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred."}), 500

# Request Logger
@app.before_request
def log_request_info():
    app.logger.info('Request: %s %s %s', request.method, request.path, request.remote_addr)
    # To log headers or body (be careful with sensitive data):
    # app.logger.debug('Headers: %s', request.headers)
    # if request.is_json:
    #     app.logger.debug('Body: %s', request.get_json(silent=True) or request.data)

# Apply rate limiting to blueprints as well if needed, or specific routes
# For example, to apply to all routes in validation_bp:
# limiter.limit("10 per minute")(validation_bp)

# New endpoint for processing API data
@app.route('/api/process', methods=['POST'])
@limiter.limit("60 per minute") # Example: limit this specific endpoint
def process_api_data():
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "Bad Request", "message": "No JSON data provided."}), 400

        discovery_method = json_data.get('discovery_method')
        data = json_data.get('data')
        openapi_spec = json_data.get('openapi_spec')
        http_interactions = json_data.get('http_interactions')

        if not discovery_method or data is None: # data can be an empty dict or list
            return jsonify({"error": "Bad Request", "message": "Missing 'discovery_method' or 'data'."}), 400

        app.logger.info(f"Processing API data via /api/process for method: {discovery_method}")
        
        processed_results = result_processor.process_results(
            discovery_method=discovery_method,
            data=data,
            openapi_spec=openapi_spec,
            http_interactions=http_interactions
        )
        return jsonify(processed_results), 200

    except Exception as e:
        app.logger.error(f"Error in /api/process: {e}", exc_info=True)
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

# Example Model (can be moved to api/models.py later)
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)

# with app.app_context(): # Create tables if they don't exist
#    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001) 
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
from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from api.routes.health import health_bp
from api.routes.validation import validation_bp
import logging
import os

app = Flask(__name__)

# Configure basic logging
if not app.debug:
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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

# Example Model (can be moved to api/models.py later)
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)

# with app.app_context(): # Create tables if they don't exist
#    db.create_all()

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True) 
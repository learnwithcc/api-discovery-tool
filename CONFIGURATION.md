# API Discovery Tool - Configuration Guide

**Last Updated:** 2025-11-18
**Version:** 1.0.0

---

## Table of Contents

1. [Overview](#overview)
2. [Environment Variables](#environment-variables)
3. [Flask Application Configuration](#flask-application-configuration)
4. [Cache Configuration](#cache-configuration)
5. [Rate Limiting Configuration](#rate-limiting-configuration)
6. [Database Configuration](#database-configuration)
7. [Selenium/ChromeDriver Configuration](#seleniumchromedriver-configuration)
8. [Logging Configuration](#logging-configuration)
9. [Configuration Files](#configuration-files)
10. [Production Configuration](#production-configuration)
11. [Troubleshooting](#troubleshooting)

---

## Overview

The API Discovery Tool can be configured through environment variables, configuration files, and command-line arguments. This guide covers all configuration options and best practices.

### Configuration Hierarchy

1. **Command-line arguments** (highest priority)
2. **Environment variables** (`.env` file or system environment)
3. **Configuration files** (`api_discovery_config.json` - optional)
4. **Default values** (lowest priority)

---

## Environment Variables

Environment variables are stored in a `.env` file in the project root directory.

### Creating Your .env File

```bash
# Copy the example file
cp .env.example .env

# Edit with your preferred editor
nano .env
```

### Available Environment Variables

#### API Keys (Optional)

These API keys are **optional** and only needed if you plan to integrate with specific AI/LLM services for advanced analysis features (currently not used by core functionality).

```bash
# Anthropic Claude
ANTHROPIC_API_KEY="sk-ant-api03-..."
# Format: sk-ant-api03-[random-string]
# Get from: https://console.anthropic.com/

# Perplexity AI
PERPLEXITY_API_KEY="pplx-..."
# Format: pplx-[random-string]
# Get from: https://perplexity.ai/settings/api

# OpenAI / OpenRouter
OPENAI_API_KEY="sk-proj-..."
# Format: sk-proj-[random-string] or sk-[random-string]
# Get from: https://platform.openai.com/api-keys

# Google Gemini
GOOGLE_API_KEY="..."
# Get from: https://makersuite.google.com/app/apikey

# Mistral AI
MISTRAL_API_KEY="..."
# Get from: https://console.mistral.ai/

# xAI
XAI_API_KEY="..."
# Get from: https://x.ai/

# Azure OpenAI
AZURE_OPENAI_API_KEY="..."
# Get from: https://portal.azure.com/
# Requires additional configuration in config file

# Ollama (for local models)
OLLAMA_API_KEY="..."
# Only needed for remote Ollama servers with authentication
# Local Ollama typically doesn't require authentication
```

#### Application Settings

```bash
# Flask environment
FLASK_ENV="development"
# Options: development, production
# Default: development

# Flask debug mode
FLASK_DEBUG="1"
# Options: 0 (off), 1 (on)
# Default: 1 in development, 0 in production
# WARNING: Never enable debug mode in production

# Flask application port
FLASK_PORT="5001"
# Default: 5001
# Change if port 5001 is already in use

# Database URL
DATABASE_URL="sqlite:///app.db"
# Default: sqlite:///app.db (SQLite database in project root)
# Format: dialect://[user:password@]host[:port]/database
# Examples:
#   SQLite: sqlite:///path/to/database.db
#   PostgreSQL: postgresql://user:pass@localhost/dbname
#   MySQL: mysql://user:pass@localhost/dbname

# Cache TTL (Time To Live) in seconds
CACHE_TTL_SECONDS="3600"
# Default: 3600 (1 hour)
# Set to 0 to disable caching
# Examples:
#   1 hour: 3600
#   1 day: 86400
#   1 week: 604800

# Cache directory
CACHE_DIR="~/.cache/api_discovery_tool"
# Default: ~/.cache/api_discovery_tool/
# Or fallback to: ./.cache/api_discovery_tool/

# Log level
LOG_LEVEL="INFO"
# Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
# Default: INFO
```

### Example .env File

```bash
# API Discovery Tool Configuration

# API Keys (Optional - only needed for AI integrations)
# ANTHROPIC_API_KEY="your_key_here"
# OPENAI_API_KEY="your_key_here"

# Application Settings
FLASK_ENV="development"
FLASK_DEBUG="1"
FLASK_PORT="5001"

# Database
DATABASE_URL="sqlite:///app.db"

# Cache Settings
CACHE_TTL_SECONDS="3600"

# Logging
LOG_LEVEL="INFO"
```

### Loading Environment Variables

The application automatically loads environment variables from the `.env` file on startup. You can verify this works by checking the logs.

**Manual loading** (if needed):

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file

api_key = os.getenv('ANTHROPIC_API_KEY')
port = int(os.getenv('FLASK_PORT', 5001))
```

---

## Flask Application Configuration

Configuration settings for the Flask web application.

### Basic Configuration (app.py)

```python
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Development/Production mode
app.config['DEBUG'] = True  # False in production
app.config['ENV'] = 'development'  # 'production' in production

# Secret key (for sessions, if needed in future)
# app.config['SECRET_KEY'] = 'your-secret-key-here'

# Max content length (prevent large uploads)
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
```

### Custom Configuration File

You can create a `config.py` file for more structured configuration:

```python
# config.py
import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev_app.db'
    CACHE_TTL_SECONDS = 600  # 10 minutes

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    CACHE_TTL_SECONDS = 3600  # 1 hour

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    CACHE_TTL_SECONDS = 0  # No caching during tests

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

**Usage in app.py**:

```python
from config import config

app = Flask(__name__)
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])
```

---

## Cache Configuration

The API Discovery Tool uses a persistent cache to store processed results.

### Cache Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `max_age_seconds` | 604800 (7 days) | Cache TTL for CLI tool |
| `cache_ttl_seconds` | 3600 (1 hour) | Cache TTL for Flask API |
| Cache location | `~/.cache/api_discovery_tool/` | Primary cache directory |
| Fallback location | `./.cache/api_discovery_tool/` | Used if home directory not writable |

### Configuring Cache in Code

**CLI Tool** (`api-discovery-tool.py`):
```python
# Cache is managed automatically by ResultProcessor
# Cache TTL defaults to 7 days for CLI usage
```

**Flask API** (`app.py`):
```python
# Initialize with custom TTL
result_processor = ResultProcessor(cache_ttl_seconds=3600)  # 1 hour

# Or from environment variable
import os
cache_ttl = int(os.getenv('CACHE_TTL_SECONDS', 3600))
result_processor = ResultProcessor(cache_ttl_seconds=cache_ttl)
```

### Cache Location

The cache is stored in a shelve database. Priority order:

1. `~/.cache/api_discovery_tool/result_cache.db` (primary)
2. `./.cache/api_discovery_tool/result_cache.db` (fallback)

**Change cache location**:

```python
from api_discovery_tool.processing.result_cache import ResultCache

# Custom cache path
cache = ResultCache(
    max_age_seconds=3600,
    cache_dir='/custom/path/to/cache'
)
```

### Cache Management

**Clear all cache**:
```python
from api_discovery_tool.processing.result_cache import ResultCache

with ResultCache() as cache:
    cache.clear_all()
```

**Clear stale entries**:
```python
with ResultCache() as cache:
    cache.clear_stale()  # Removes expired entries
```

**Disable caching**:
```python
# Set TTL to 0 or negative value
result_processor = ResultProcessor(cache_ttl_seconds=0)
```

---

## Rate Limiting Configuration

Rate limiting prevents API abuse and ensures fair usage.

### Default Rate Limits

Configured in `app.py`:

```python
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)
```

| Scope | Limit | Description |
|-------|-------|-------------|
| Global | 200 per day | All endpoints combined |
| Global | 50 per hour | All endpoints combined |
| `/api/process` | 60 per minute | Processing endpoint only |

### Customizing Rate Limits

**In app.py**:

```python
# Change global limits
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["1000 per day", "100 per hour"],
    storage_uri="memory://",
)

# Change endpoint-specific limit
@app.route('/api/process', methods=['POST'])
@limiter.limit("120 per minute")  # Increased from 60
def process_api_data():
    # ...
```

**Storage backends**:

```python
# Memory (default, resets on restart)
storage_uri="memory://"

# Redis (persistent, for production)
storage_uri="redis://localhost:6379"

# Memcached
storage_uri="memcached://localhost:11211"
```

### Disable Rate Limiting

**For development** (not recommended for production):

```python
# In app.py
limiter.enabled = False
```

### Per-User Rate Limiting

**Custom key function** (requires authentication):

```python
def get_user_id():
    # Example: get user from auth token
    return request.headers.get('X-User-ID', get_remote_address())

limiter = Limiter(
    get_user_id,
    app=app,
    default_limits=["200 per day"],
)
```

---

## Database Configuration

The API uses SQLAlchemy for database operations.

### SQLite (Default)

**Configuration**:
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
```

**Location**: `app.db` in project root

**Pros**: Simple, no setup required
**Cons**: Not suitable for high-concurrency production

### PostgreSQL (Recommended for Production)

**Install driver**:
```bash
pip install psycopg2-binary
```

**Configuration**:
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost:5432/api_discovery'
```

**Environment variable**:
```bash
DATABASE_URL="postgresql://user:password@localhost:5432/api_discovery"
```

### MySQL

**Install driver**:
```bash
pip install mysqlclient
```

**Configuration**:
```python
SQLALCHEMY_DATABASE_URI = 'mysql://user:password@localhost/api_discovery'
```

### Database Migrations

**Install Flask-Migrate**:
```bash
pip install Flask-Migrate
```

**Setup** (in `app.py`):
```python
from flask_migrate import Migrate

migrate = Migrate(app, db)
```

**Usage**:
```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

---

## Selenium/ChromeDriver Configuration

For browser-based API discovery using the CLI tool.

### ChromeDriver Installation

**Option 1: Manual installation**

1. Check Chrome version: `google-chrome --version`
2. Download matching ChromeDriver: https://chromedriver.chromium.org/
3. Add to PATH:
   ```bash
   sudo mv chromedriver /usr/local/bin/
   sudo chmod +x /usr/local/bin/chromedriver
   ```

**Option 2: webdriver-manager (recommended)**

```bash
pip install webdriver-manager
```

Update `api-discovery-tool.py`:
```python
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
```

### Chrome Options

**Headless mode** (no GUI):
```python
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
```

**Custom user agent**:
```python
chrome_options.add_argument('user-agent=Mozilla/5.0 ...')
```

**Window size**:
```python
chrome_options.add_argument('--window-size=1920,1080')
```

**Disable images** (faster loading):
```python
prefs = {'profile.managed_default_content_settings.images': 2}
chrome_options.add_experimental_option('prefs', prefs)
```

### CLI Arguments

```bash
# Headless mode (default)
python api-discovery-tool.py https://example.com --headless

# Headed mode (see browser)
python api-discovery-tool.py https://example.com --no-headless

# Respect robots.txt (default)
python api-discovery-tool.py https://example.com --respect-robots

# Ignore robots.txt
python api-discovery-tool.py https://example.com --no-respect-robots

# Custom output file
python api-discovery-tool.py https://example.com -o custom_report.json
```

---

## Logging Configuration

Control logging verbosity and format.

### Log Levels

```python
# In app.py or api-discovery-tool.py
import logging

# Set log level
logging.basicConfig(level=logging.INFO)

# Available levels (in order of severity):
# DEBUG    - Detailed diagnostic information
# INFO     - Confirmation that things are working
# WARNING  - Something unexpected happened
# ERROR    - Serious problem, function failed
# CRITICAL - Very serious error, program may crash
```

### Log Format

**Default format** (in `app.py`):
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
)
```

**Custom format**:
```python
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)-8s %(name)-20s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

### Log to File

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s : %(message)s',
    handlers=[
        logging.FileHandler('api_discovery.log'),
        logging.StreamHandler()  # Also log to console
    ]
)
```

### Module-Specific Logging

```python
# Reduce verbosity of specific modules
logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('selenium').setLevel(logging.ERROR)
```

---

## Configuration Files

### api_discovery_config.json (Optional)

Create a JSON configuration file for advanced settings:

```json
{
  "discovery": {
    "methods": ["html_analysis", "javascript_analysis", "selenium", "common_endpoints"],
    "timeout_seconds": 30,
    "max_retries": 3,
    "user_agent": "API Discovery Tool/1.0"
  },
  "selenium": {
    "headless": true,
    "window_size": [1920, 1080],
    "page_load_timeout": 30,
    "implicit_wait": 10
  },
  "processing": {
    "cache_ttl_seconds": 3600,
    "enable_deduplication": true,
    "enable_categorization": true
  },
  "rate_limiting": {
    "enabled": true,
    "requests_per_minute": 60,
    "requests_per_hour": 1000,
    "requests_per_day": 10000
  },
  "output": {
    "format": "json",
    "pretty_print": true,
    "include_raw_data": false
  }
}
```

**Loading configuration**:

```python
import json

def load_config(config_path='api_discovery_config.json'):
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

config = load_config()
cache_ttl = config.get('processing', {}).get('cache_ttl_seconds', 3600)
```

---

## Production Configuration

### Recommended Production Settings

```python
# app.py for production
import os

# Environment
app.config['ENV'] = 'production'
app.config['DEBUG'] = False

# Database (use PostgreSQL)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Security
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
# app.config['SESSION_COOKIE_SECURE'] = True  # If using HTTPS
# app.config['SESSION_COOKIE_HTTPONLY'] = True

# Rate limiting (use Redis)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["500 per day", "100 per hour"],
    storage_uri=os.environ.get('REDIS_URL', 'redis://localhost:6379'),
)

# Logging (to file)
if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler

    file_handler = RotatingFileHandler(
        'logs/api_discovery.log',
        maxBytes=10240000,  # 10 MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('API Discovery Tool startup')
```

### Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Use strong `SECRET_KEY` from environment variable
- [ ] Use production database (PostgreSQL/MySQL)
- [ ] Enable HTTPS with SSL certificates
- [ ] Use Redis for rate limiting storage
- [ ] Configure proper logging (file rotation)
- [ ] Set up monitoring and alerts
- [ ] Use WSGI server (Gunicorn/uWSGI)
- [ ] Configure reverse proxy (Nginx/Apache)
- [ ] Set appropriate CORS headers (if needed)
- [ ] Enable security headers (CSP, X-Frame-Options, etc.)

### Example Production Deployment

**With Gunicorn**:
```bash
gunicorn -w 4 -b 0.0.0.0:5001 --access-logfile - --error-logfile - app:app
```

**With systemd service**:
```ini
# /etc/systemd/system/api-discovery.service
[Unit]
Description=API Discovery Tool
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/api-discovery-tool
Environment="PATH=/var/www/api-discovery-tool/venv/bin"
ExecStart=/var/www/api-discovery-tool/venv/bin/gunicorn -w 4 -b 127.0.0.1:5001 app:app

[Install]
WantedBy=multi-user.target
```

**Nginx reverse proxy**:
```nginx
server {
    listen 80;
    server_name api-discovery.example.com;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Troubleshooting

### Common Configuration Issues

#### Issue: "No module named 'dotenv'"

**Solution**: Install python-dotenv
```bash
pip install python-dotenv
```

---

#### Issue: "ChromeDriver version mismatch"

**Solution**: Update ChromeDriver to match Chrome version
```bash
# Use webdriver-manager for automatic version matching
pip install webdriver-manager
```

---

#### Issue: "Database locked" (SQLite)

**Solution**: SQLite doesn't handle concurrent writes well. Use PostgreSQL for production.

---

#### Issue: "Rate limit not working"

**Solution**: Check storage URI configuration
```python
# Use Redis instead of memory for persistent rate limiting
storage_uri="redis://localhost:6379"
```

---

#### Issue: "Cache not persisting"

**Solution**: Check cache directory permissions
```bash
# Check permissions
ls -la ~/.cache/api_discovery_tool/

# Fix permissions
chmod 755 ~/.cache/api_discovery_tool/
```

---

#### Issue: "Import errors in production"

**Solution**: Ensure all dependencies are installed
```bash
pip install -r requirements.txt
```

---

### Debugging Configuration

**Print active configuration**:

```python
# In app.py
@app.route('/api/debug/config')
def debug_config():
    if not app.debug:
        return jsonify({"error": "Debug mode disabled"}), 403

    return jsonify({
        "debug": app.config['DEBUG'],
        "env": app.config['ENV'],
        "database": app.config['SQLALCHEMY_DATABASE_URI'],
        "cache_ttl": result_processor.cache_ttl_seconds,
    })
```

**Check environment variables**:

```python
import os
print("FLASK_ENV:", os.getenv('FLASK_ENV'))
print("CACHE_TTL_SECONDS:", os.getenv('CACHE_TTL_SECONDS'))
print("DATABASE_URL:", os.getenv('DATABASE_URL'))
```

---

## Additional Resources

- [README.md](README.md) - User documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [CONTRIBUTING.md](CONTRIBUTING.md) - Developer guide
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API reference

---

**Document Status:** Complete
**Maintained By:** Development Team
**Review Cycle:** Quarterly or with configuration changes

# API Discovery Tool - REST API Documentation

**Version:** 1.0.0
**Base URL:** `http://localhost:5001/api`
**Last Updated:** 2025-11-18

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Rate Limiting](#rate-limiting)
4. [Error Handling](#error-handling)
5. [Endpoints](#endpoints)
   - [Health Check](#health-check)
   - [URL Validation](#url-validation)
   - [Process API Data](#process-api-data)
6. [Web Interface](#web-interface)
7. [Request Examples](#request-examples)
8. [Response Examples](#response-examples)
9. [Client Libraries](#client-libraries)
10. [OpenAPI Specification](#openapi-specification)

---

## Overview

The API Discovery Tool provides a RESTful API for processing and analyzing API discovery results. The API accepts data from various discovery methods (network monitoring, OpenAPI specs, etc.) and returns confidence scores, pattern analysis, and API conventions.

### Key Features

- **Health monitoring**: Check service status
- **URL validation**: Validate URLs and check robots.txt compliance
- **API processing**: Analyze API discovery data with confidence scoring and pattern recognition
- **Caching**: Automatic result caching with configurable TTL (default: 1 hour)
- **Rate limiting**: Protects against abuse (60 requests/minute for processing endpoint)

### Technology Stack

- **Framework**: Flask 2.0+
- **Database**: SQLite with SQLAlchemy ORM
- **Rate Limiting**: Flask-Limiter
- **Caching**: Persistent shelve-based cache

---

## Authentication

**Current Status**: No authentication required

The API currently operates without authentication. All endpoints are publicly accessible.

### Future Authentication (Planned)

Future versions may implement:
- API key authentication (Header: `X-API-Key`)
- OAuth 2.0 for third-party integrations
- JWT tokens for session management

---

## Rate Limiting

Rate limiting is enforced to prevent abuse and ensure fair usage.

### Default Limits

- **Global limits**:
  - 200 requests per day per IP
  - 50 requests per hour per IP

- **Endpoint-specific limits**:
  - `/api/process`: 60 requests per minute per IP

### Rate Limit Headers

Response headers include rate limit information:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1700000000
```

### Rate Limit Exceeded Response

**Status Code**: `429 Too Many Requests`

```json
{
  "error": "ratelimit exceeded",
  "message": "60 per 1 minute"
}
```

---

## Error Handling

All errors return JSON responses with consistent structure.

### Error Response Format

```json
{
  "error": "Error Type",
  "message": "Detailed error message"
}
```

### HTTP Status Codes

| Status Code | Description | Common Causes |
|-------------|-------------|---------------|
| `200 OK` | Successful request | - |
| `400 Bad Request` | Invalid request data | Missing required fields, invalid JSON |
| `404 Not Found` | Endpoint not found | Invalid URL path |
| `429 Too Many Requests` | Rate limit exceeded | Too many requests in time window |
| `500 Internal Server Error` | Server error | Unexpected processing error |

### Example Error Responses

**400 Bad Request**:
```json
{
  "error": "Bad Request",
  "message": "No JSON data provided."
}
```

**500 Internal Server Error**:
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred."
}
```

---

## Endpoints

### Health Check

Check if the API service is running and healthy.

**Endpoint**: `GET /api/health`
**Authentication**: None
**Rate Limit**: Global limits apply

#### Request

```http
GET /api/health HTTP/1.1
Host: localhost:5001
```

#### Response

**Status Code**: `200 OK`

```json
{
  "status": "healthy"
}
```

#### Example with curl

```bash
curl http://localhost:5001/api/health
```

#### Example with Python

```python
import requests

response = requests.get('http://localhost:5001/api/health')
print(response.json())
# Output: {'status': 'healthy'}
```

---

### URL Validation

Validate a URL and check robots.txt compliance.

**Endpoint**: `POST /api/validate-url`
**Authentication**: None
**Rate Limit**: Global limits apply

#### Request

**Content-Type**: `application/json`

**Body Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | URL to validate |

**Request Body**:
```json
{
  "url": "https://example.com/api/users"
}
```

#### Response

**Status Code**: `200 OK` (if valid)

```json
{
  "message": "URL is valid",
  "url": "https://example.com/api/users",
  "robots_check": {
    "allowed": true,
    "message": "robots.txt allows crawling https://example.com/api/users"
  }
}
```

**Status Code**: `400 Bad Request` (if invalid)

```json
{
  "error": "Invalid URL provided",
  "url": "not-a-valid-url"
}
```

#### Validation Rules

- URL must be a valid HTTP/HTTPS URL
- URL must include protocol (http:// or https://)
- URL must have a valid domain name

#### robots.txt Compliance

The endpoint automatically checks robots.txt for the provided URL:
- Fetches `/robots.txt` from the URL's origin
- Checks if the path is allowed for the default user-agent
- Returns `allowed: true/false` with explanatory message

#### Example with curl

```bash
curl -X POST http://localhost:5001/api/validate-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://api.github.com/users"}'
```

#### Example with Python

```python
import requests

response = requests.post(
    'http://localhost:5001/api/validate-url',
    json={'url': 'https://api.github.com/users'}
)

print(response.json())
```

---

### Process API Data

Process API discovery results with confidence scoring and pattern recognition.

**Endpoint**: `POST /api/process`
**Authentication**: None
**Rate Limit**: 60 requests per minute

#### Request

**Content-Type**: `application/json`

**Body Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `discovery_method` | string | Yes | Discovery method used (e.g., "mitmproxy", "selenium", "openapi") |
| `data` | any | Yes | Raw discovery data (can be object, array, string) |
| `openapi_spec` | object | No | OpenAPI/Swagger specification (if available) |
| `http_interactions` | array | No | HTTP traffic data (requests/responses) |

**Request Body**:
```json
{
  "discovery_method": "mitmproxy",
  "data": [
    {"endpoint": "/api/users", "method": "GET"},
    {"endpoint": "/api/posts", "method": "POST"}
  ],
  "openapi_spec": {
    "openapi": "3.0.0",
    "info": {"title": "Example API", "version": "1.0.0"},
    "paths": {
      "/api/users": {
        "get": {
          "summary": "Get users",
          "responses": {"200": {"description": "Success"}}
        }
      }
    }
  },
  "http_interactions": [
    {
      "method": "GET",
      "url": "https://example.com/api/users",
      "status_code": 200,
      "request_headers": {"Accept": "application/json"},
      "response_headers": {"Content-Type": "application/json"}
    }
  ]
}
```

#### Response

**Status Code**: `200 OK`

```json
{
  "discovery_method": "mitmproxy",
  "raw_data_summary": "List with 2 items",
  "analysis_summary": {
    "confidence_score": 0.75,
    "confidence_details": {
      "completeness": 0.8,
      "reliability": 0.7,
      "recency": 0.9,
      "validation": 1.0
    },
    "api_conventions": {
      "naming_conventions": {
        "path_segments": {"snake_case": 5, "camelCase": 2},
        "query_params": {"snake_case": 3},
        "predominant_style": "snake_case"
      },
      "versioning": {
        "strategies": ["path"],
        "versions_found": ["v1", "v2"],
        "path_patterns": ["/api/v1", "/api/v2"]
      },
      "authentication": {
        "schemes": ["bearer"],
        "locations": ["header"],
        "headers_observed": ["Authorization"]
      },
      "pagination": {
        "patterns_found": ["page-based", "size-based"],
        "page_params": ["page"],
        "size_params": ["limit", "per_page"]
      },
      "data_formats": {
        "content_types": ["application/json"],
        "request_formats": ["json"],
        "response_formats": ["json"]
      },
      "http_methods": {
        "GET": 15,
        "POST": 5,
        "PUT": 2,
        "DELETE": 1
      },
      "status_codes": {
        "200": 18,
        "201": 3,
        "400": 1,
        "404": 1
      }
    }
  }
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `discovery_method` | string | Echo of request discovery method |
| `raw_data_summary` | string | Human-readable summary of input data |
| `analysis_summary` | object | Complete analysis results |
| `analysis_summary.confidence_score` | number | Overall confidence (0.0-1.0) |
| `analysis_summary.confidence_details` | object | Individual confidence factors |
| `analysis_summary.api_conventions` | object | Detected API patterns |

#### Confidence Score Details

**completeness** (0.0-1.0):
- Ratio of present fields to expected fields
- Higher score indicates more complete API documentation

**reliability** (0.0-1.0):
- Based on data source type
- `official_doc`: 0.9, `known_api_db`: 0.8, `code_repository`: 0.6, etc.

**recency** (0.0-1.0):
- Time-based decay (10% per year)
- Higher score for more recently updated APIs

**validation** (0.0 or 1.0):
- Binary: validated or not validated
- Based on metadata validation status

**overall** (weighted average):
```
overall = completeness * 0.3 +
          reliability * 0.4 +
          recency * 0.15 +
          validation * 0.15
```

#### Caching Behavior

- Results are cached for 1 hour (3600 seconds) by default
- Cache key: SHA256 hash of `(discovery_method, data)`
- Subsequent identical requests return cached results instantly
- Cache stored in `~/.cache/api_discovery_tool/result_cache.db`

#### Example with curl

```bash
curl -X POST http://localhost:5001/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "discovery_method": "openapi",
    "data": {"endpoints": 10, "documented": true},
    "openapi_spec": {
      "openapi": "3.0.0",
      "info": {"title": "My API", "version": "1.0.0"},
      "paths": {"/users": {"get": {}}}
    }
  }'
```

#### Example with Python

```python
import requests

data = {
    "discovery_method": "selenium",
    "data": [
        {"url": "https://api.example.com/v1/users", "method": "GET"},
        {"url": "https://api.example.com/v1/posts", "method": "POST"}
    ],
    "http_interactions": [
        {
            "method": "GET",
            "url": "https://api.example.com/v1/users",
            "status_code": 200,
            "response_headers": {"Content-Type": "application/json"}
        }
    ]
}

response = requests.post('http://localhost:5001/api/process', json=data)
results = response.json()

print(f"Confidence Score: {results['analysis_summary']['confidence_score']}")
print(f"API Conventions: {results['analysis_summary']['api_conventions']}")
```

---

## Web Interface

The API also provides a web-based user interface.

**Endpoint**: `GET /`
**URL**: `http://localhost:5001/`

### Features

- Visual interface for API discovery
- Form-based input for URL analysis
- Real-time results display
- Interactive API pattern visualization

### Accessing the Web UI

```bash
# Start the Flask application
python app.py

# Open in browser
http://localhost:5001/
```

---

## Request Examples

### Complete Processing Example

```bash
curl -X POST http://localhost:5001/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "discovery_method": "mitmproxy",
    "data": {
      "total_endpoints": 25,
      "documented": 20,
      "undocumented": 5
    },
    "openapi_spec": {
      "openapi": "3.0.0",
      "info": {
        "title": "E-Commerce API",
        "version": "2.0.0",
        "description": "API for e-commerce platform"
      },
      "servers": [
        {"url": "https://api.example.com/v2"}
      ],
      "paths": {
        "/products": {
          "get": {
            "summary": "List products",
            "parameters": [
              {"name": "page", "in": "query", "schema": {"type": "integer"}},
              {"name": "limit", "in": "query", "schema": {"type": "integer"}}
            ],
            "responses": {
              "200": {"description": "Success"}
            }
          }
        },
        "/products/{id}": {
          "get": {
            "summary": "Get product by ID",
            "parameters": [
              {"name": "id", "in": "path", "schema": {"type": "string"}}
            ]
          }
        }
      },
      "components": {
        "securitySchemes": {
          "bearerAuth": {
            "type": "http",
            "scheme": "bearer"
          }
        }
      }
    },
    "http_interactions": [
      {
        "method": "GET",
        "url": "https://api.example.com/v2/products?page=1&limit=20",
        "status_code": 200,
        "request_headers": {
          "Authorization": "Bearer token123",
          "Accept": "application/json"
        },
        "response_headers": {
          "Content-Type": "application/json",
          "X-RateLimit-Limit": "1000",
          "X-RateLimit-Remaining": "999"
        }
      },
      {
        "method": "GET",
        "url": "https://api.example.com/v2/products/abc123",
        "status_code": 200,
        "request_headers": {
          "Authorization": "Bearer token123"
        },
        "response_headers": {
          "Content-Type": "application/json"
        }
      }
    ]
  }'
```

---

## Response Examples

### Minimal Processing Response

```json
{
  "discovery_method": "manual",
  "raw_data_summary": "Dict with 3 keys",
  "analysis_summary": {
    "confidence_score": 0.5,
    "confidence_details": {
      "completeness": 0.4,
      "reliability": 0.6,
      "recency": 0.5,
      "validation": 0.0
    },
    "api_conventions": {
      "naming_conventions": {},
      "versioning": {},
      "authentication": {},
      "pagination": {},
      "data_formats": {},
      "http_methods": {},
      "status_codes": {}
    }
  }
}
```

### Full Processing Response

```json
{
  "discovery_method": "mitmproxy",
  "raw_data_summary": "Dict with 3 keys",
  "analysis_summary": {
    "confidence_score": 0.82,
    "confidence_details": {
      "completeness": 0.85,
      "reliability": 0.8,
      "recency": 0.95,
      "validation": 1.0
    },
    "api_conventions": {
      "naming_conventions": {
        "path_segments": {
          "snake_case": 12,
          "camelCase": 3,
          "kebab-case": 1
        },
        "query_params": {
          "snake_case": 8,
          "camelCase": 2
        },
        "header_keys": {
          "PascalCase": 5,
          "kebab-case": 3
        },
        "request_body_keys": {
          "camelCase": 15,
          "snake_case": 2
        },
        "response_body_keys": {
          "camelCase": 20,
          "snake_case": 1
        },
        "schema_names": {
          "PascalCase": 10
        },
        "predominant_style": "camelCase"
      },
      "versioning": {
        "strategies": ["path", "header"],
        "versions_found": ["v1", "v2", "v2.0"],
        "path_patterns": ["/api/v1/", "/api/v2/"],
        "header_patterns": ["X-API-Version: 2.0"],
        "query_patterns": []
      },
      "authentication": {
        "schemes": ["bearer", "apiKey"],
        "locations": ["header", "query"],
        "headers_observed": ["Authorization", "X-API-Key"],
        "query_params_observed": ["api_key"],
        "security_schemes": {
          "bearerAuth": {"type": "http", "scheme": "bearer"},
          "apiKeyAuth": {"type": "apiKey", "name": "X-API-Key", "in": "header"}
        }
      },
      "pagination": {
        "patterns_found": ["page-based", "size-based", "cursor-based"],
        "page_params": ["page", "page_number"],
        "size_params": ["limit", "per_page", "pagesize"],
        "offset_params": ["offset"],
        "cursor_params": ["cursor", "next_token"],
        "link_headers": ["rel=\"next\"", "rel=\"prev\""]
      },
      "data_formats": {
        "content_types": ["application/json", "application/xml"],
        "request_formats": ["json", "xml"],
        "response_formats": ["json", "xml"],
        "accept_headers": ["application/json", "*/*"]
      },
      "http_methods": {
        "GET": 45,
        "POST": 12,
        "PUT": 5,
        "PATCH": 3,
        "DELETE": 2,
        "OPTIONS": 8
      },
      "status_codes": {
        "200": 50,
        "201": 10,
        "204": 2,
        "400": 3,
        "401": 5,
        "403": 1,
        "404": 4,
        "500": 1
      }
    }
  }
}
```

---

## Client Libraries

### Python Client Example

```python
import requests
from typing import Dict, List, Optional, Any


class APIDiscoveryClient:
    """Python client for API Discovery Tool."""

    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def health_check(self) -> Dict:
        """Check if the API is healthy."""
        response = self.session.get(f"{self.base_url}/api/health")
        response.raise_for_status()
        return response.json()

    def validate_url(self, url: str) -> Dict:
        """Validate a URL and check robots.txt compliance."""
        response = self.session.post(
            f"{self.base_url}/api/validate-url",
            json={"url": url}
        )
        response.raise_for_status()
        return response.json()

    def process_api_data(
        self,
        discovery_method: str,
        data: Any,
        openapi_spec: Optional[Dict] = None,
        http_interactions: Optional[List[Dict]] = None
    ) -> Dict:
        """Process API discovery data."""
        payload = {
            "discovery_method": discovery_method,
            "data": data
        }

        if openapi_spec:
            payload["openapi_spec"] = openapi_spec

        if http_interactions:
            payload["http_interactions"] = http_interactions

        response = self.session.post(
            f"{self.base_url}/api/process",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def get_confidence_score(self, discovery_method: str, data: Any) -> float:
        """Get just the confidence score from processing."""
        results = self.process_api_data(discovery_method, data)
        return results["analysis_summary"]["confidence_score"]


# Usage example
if __name__ == "__main__":
    client = APIDiscoveryClient()

    # Health check
    print("Health:", client.health_check())

    # URL validation
    validation = client.validate_url("https://api.github.com/users")
    print("URL valid:", validation["message"])
    print("Robots.txt allows:", validation["robots_check"]["allowed"])

    # Process API data
    results = client.process_api_data(
        discovery_method="openapi",
        data={"endpoints": 10},
        openapi_spec={
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {"/users": {"get": {}}}
        }
    )

    print(f"Confidence score: {results['analysis_summary']['confidence_score']}")
    print(f"Patterns found: {results['analysis_summary']['api_conventions']}")
```

### JavaScript/Node.js Client Example

```javascript
const axios = require('axios');

class APIDiscoveryClient {
  constructor(baseURL = 'http://localhost:5001') {
    this.client = axios.create({
      baseURL,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  async healthCheck() {
    const response = await this.client.get('/api/health');
    return response.data;
  }

  async validateUrl(url) {
    const response = await this.client.post('/api/validate-url', { url });
    return response.data;
  }

  async processApiData(discoveryMethod, data, openapiSpec = null, httpInteractions = null) {
    const payload = {
      discovery_method: discoveryMethod,
      data
    };

    if (openapiSpec) payload.openapi_spec = openapiSpec;
    if (httpInteractions) payload.http_interactions = httpInteractions;

    const response = await this.client.post('/api/process', payload);
    return response.data;
  }

  async getConfidenceScore(discoveryMethod, data) {
    const results = await this.processApiData(discoveryMethod, data);
    return results.analysis_summary.confidence_score;
  }
}

// Usage
(async () => {
  const client = new APIDiscoveryClient();

  // Health check
  const health = await client.healthCheck();
  console.log('Health:', health);

  // Process data
  const results = await client.processApiData('selenium', [
    { url: 'https://api.example.com/users', method: 'GET' }
  ]);

  console.log('Confidence:', results.analysis_summary.confidence_score);
})();
```

---

## OpenAPI Specification

### Generating OpenAPI Spec

You can generate an OpenAPI 3.0 specification for this API:

```yaml
openapi: 3.0.0
info:
  title: API Discovery Tool
  version: 1.0.0
  description: RESTful API for processing and analyzing API discovery results
  contact:
    name: API Support
    url: https://github.com/yourusername/api-discovery-tool

servers:
  - url: http://localhost:5001
    description: Local development server

paths:
  /api/health:
    get:
      summary: Health check
      description: Check if the API service is running
      responses:
        '200':
          description: Service is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: "healthy"

  /api/validate-url:
    post:
      summary: Validate URL
      description: Validate a URL and check robots.txt compliance
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - url
              properties:
                url:
                  type: string
                  format: uri
                  example: "https://example.com/api/users"
      responses:
        '200':
          description: URL is valid
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                  url:
                    type: string
                  robots_check:
                    type: object
                    properties:
                      allowed:
                        type: boolean
                      message:
                        type: string
        '400':
          description: Invalid URL
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

  /api/process:
    post:
      summary: Process API data
      description: Process API discovery results with confidence scoring and pattern recognition
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - discovery_method
                - data
              properties:
                discovery_method:
                  type: string
                  example: "mitmproxy"
                data:
                  oneOf:
                    - type: object
                    - type: array
                    - type: string
                openapi_spec:
                  type: object
                http_interactions:
                  type: array
                  items:
                    type: object
      responses:
        '200':
          description: Processing successful
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ProcessingResult'
        '400':
          description: Invalid request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '429':
          description: Rate limit exceeded
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

components:
  schemas:
    Error:
      type: object
      properties:
        error:
          type: string
        message:
          type: string

    ProcessingResult:
      type: object
      properties:
        discovery_method:
          type: string
        raw_data_summary:
          type: string
        analysis_summary:
          type: object
          properties:
            confidence_score:
              type: number
              minimum: 0
              maximum: 1
            confidence_details:
              type: object
            api_conventions:
              type: object
```

---

## Configuration

### Environment Variables

See [CONFIGURATION.md](CONFIGURATION.md) for detailed configuration options.

### Flask Application Settings

```python
# Database
SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Rate Limiting
DEFAULT_LIMITS = ["200 per day", "50 per hour"]
STORAGE_URI = "memory://"

# Logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'

# Cache TTL
CACHE_TTL_SECONDS = 3600  # 1 hour
```

---

## Running the API

### Local Development

```bash
# Start Flask development server
python app.py

# Server will start on http://localhost:5001
# API endpoints available at http://localhost:5001/api/
```

### Production Deployment

```bash
# Using Gunicorn (recommended)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app

# Using uWSGI
pip install uwsgi
uwsgi --http :5001 --wsgi-file app.py --callable app --processes 4

# With Nginx reverse proxy
# See deployment documentation for Nginx configuration
```

---

## Testing the API

### Manual Testing with curl

```bash
# Health check
curl http://localhost:5001/api/health

# Validate URL
curl -X POST http://localhost:5001/api/validate-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://api.github.com"}'

# Process data
curl -X POST http://localhost:5001/api/process \
  -H "Content-Type: application/json" \
  -d '{"discovery_method": "test", "data": {"test": true}}'
```

### Automated Testing

See [CONTRIBUTING.md](CONTRIBUTING.md) for testing guidelines.

---

## Troubleshooting

### Common Issues

**Issue**: `Connection refused` error

**Solution**: Ensure Flask app is running on port 5001
```bash
python app.py
```

---

**Issue**: `429 Too Many Requests`

**Solution**: Wait for rate limit window to reset or reduce request frequency

---

**Issue**: `400 Bad Request - Missing discovery_method or data`

**Solution**: Ensure required fields are present in request body
```json
{
  "discovery_method": "required_value",
  "data": "required_value"
}
```

---

## Additional Resources

- [README.md](README.md) - User documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [CONTRIBUTING.md](CONTRIBUTING.md) - Developer guide
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration reference

---

**Document Status:** Complete
**Maintained By:** Development Team
**Review Cycle:** Quarterly or with API changes

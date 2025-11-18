# API Discovery Tool - Architecture Documentation

**Last Updated:** 2025-11-18
**Version:** 1.0.0

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Project Structure](#project-structure)
4. [Processing Pipeline](#processing-pipeline)
5. [Module Relationships](#module-relationships)
6. [Data Flow](#data-flow)
7. [Design Decisions](#design-decisions)
8. [Discovery Methods](#discovery-methods)
9. [Extension Points](#extension-points)

---

## Overview

The API Discovery Tool is a sophisticated Python-based system designed to analyze websites and discover hidden or undocumented APIs. It provides both a command-line interface (CLI) and a Flask-based REST API for integration into larger systems.

### Key Capabilities

- **Multi-Method Discovery**: HTML analysis, JavaScript parsing, network monitoring, common endpoint probing
- **Intelligent Processing**: Confidence scoring, pattern recognition, API categorization
- **Ethical Operation**: Respects robots.txt, implements rate limiting
- **Persistent Caching**: Reduces redundant processing with TTL-based cache
- **Comprehensive Analysis**: Identifies API conventions, versioning, authentication, pagination patterns

### Architecture Type

**Modular, Layered Pipeline** with dual CLI/API interfaces

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface Layer                  │
├────────────────────────────────┬────────────────────────────┤
│   CLI (api-discovery-tool.py)  │  Web API (Flask - app.py)  │
└────────────────────────────────┴────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────┐
│                      Application Layer                       │
├──────────────────────────────────────────────────────────────┤
│  • Flask Routes (health, validation, processing)             │
│  • Service Layer (compliance checking)                       │
│  • API Discovery Engine                                      │
└──────────────────────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────┐
│                    Processing Pipeline Layer                 │
├──────────────────────────────────────────────────────────────┤
│                     ResultProcessor                          │
│  ┌────────────────┬─────────────────┬──────────────────┐   │
│  │ Confidence     │ Pattern         │ Result Cache     │   │
│  │ Scorer         │ Recognizer      │                  │   │
│  └────────────────┴─────────────────┴──────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────┐
│                        Utility Layer                         │
├──────────────────────────────────────────────────────────────┤
│  • Categorizer (API type classification)                     │
│  • Deduplicator (endpoint normalization)                     │
│  • Validators (URL validation)                               │
└──────────────────────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────┐
│                       External Layer                         │
├──────────────────────────────────────────────────────────────┤
│  • Selenium WebDriver (browser automation)                   │
│  • BeautifulSoup (HTML parsing)                              │
│  • Requests (HTTP client)                                    │
│  • SQLAlchemy (database)                                     │
│  • Shelve (persistent cache storage)                         │
└──────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
api-discovery-tool/
│
├── api-discovery-tool.py          # CLI entry point for standalone discovery
├── app.py                         # Flask web application entry point
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variable template
├── README.md                      # User documentation
├── ARCHITECTURE.md                # This file
├── CONTRIBUTING.md                # Developer guide
├── API_DOCUMENTATION.md           # API endpoint reference
├── CONFIGURATION.md               # Configuration guide
├── DOCUMENTATION_TODO.md          # Documentation tracking
│
├── api_discovery_tool/            # Main package
│   ├── __init__.py
│   └── processing/                # Core processing modules
│       ├── __init__.py
│       ├── result_processor.py    # Main orchestrator
│       ├── confidence_scorer.py   # Confidence calculation
│       ├── pattern_recognizer.py  # Pattern detection
│       ├── result_cache.py        # Caching layer
│       ├── categorizer.py         # API type classification
│       ├── deduplicator.py        # Endpoint deduplication
│       └── tests/                 # Unit tests
│           ├── test_scoring.py
│           ├── test_pattern_recognizer.py
│           ├── test_caching.py
│           ├── test_categorizer.py
│           ├── test_deduplicator.py
│           └── __init__.py
│
├── api/                           # Flask API layer
│   ├── routes/                    # HTTP endpoints
│   │   ├── health.py             # Health check
│   │   └── validation.py         # URL validation
│   └── services/                 # Business logic
│       └── compliance.py         # robots.txt checking
│
├── static/                        # Frontend assets
│   ├── app.js                    # JavaScript UI
│   └── style.css                 # Styling
│
├── templates/                     # HTML templates
│   └── index.html                # Web interface
│
└── scripts/                       # Utility scripts
    └── prd.txt                   # Product requirements
```

---

## Processing Pipeline

The processing pipeline is the core of the API Discovery Tool, transforming raw discovery data into structured, analyzed results.

### Pipeline Flow

```
┌─────────────────┐
│  Raw Data Input │
│  • OpenAPI Spec │
│  • HTTP Traffic │
│  • HTML/JS Code │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      ResultProcessor                │
│  • Cache lookup                     │
│  • Data summarization               │
│  • Orchestrates analysis            │
└────────┬────────────────────────────┘
         │
         ├──────────────┬──────────────┐
         ▼              ▼              ▼
┌────────────────┐ ┌──────────┐ ┌──────────────┐
│ Confidence     │ │ Pattern  │ │ Result Cache │
│ Scorer         │ │ Recognizer│ │              │
│ • Completeness │ │ • Naming │ │ • Shelve DB  │
│ • Reliability  │ │ • Versions│ │ • TTL-based  │
│ • Recency      │ │ • Auth    │ │ • SHA256 keys│
│ • Validation   │ │ • Pagination│              │
└────────┬───────┘ └────┬─────┘ └──────┬───────┘
         │              │              │
         └──────────────┴──────────────┘
                        │
                        ▼
         ┌──────────────────────────┐
         │   Processed Results      │
         │  • Confidence score      │
         │  • API patterns          │
         │  • Conventions detected  │
         │  • Cached for reuse      │
         └──────────────────────────┘
```

### Pipeline Components

#### 1. ResultProcessor (`result_processor.py`)

**Role:** Main orchestrator that coordinates all processing steps

**Responsibilities:**
- Accepts discovery method results (OpenAPI specs, HTTP interactions)
- Manages caching (check cache, store results)
- Coordinates scoring and pattern recognition
- Aggregates and structures output

**Key Method:**
```python
def process_results(
    discovery_method: str,
    data: Any,
    openapi_spec: Dict | None = None,
    http_interactions: List[Dict] | None = None
) -> Dict
```

**Output Structure:**
```json
{
  "discovery_method": "string",
  "raw_data_summary": "string",
  "analysis_summary": {
    "confidence_score": 0.0-1.0,
    "confidence_details": {...},
    "api_conventions": {...}
  }
}
```

---

#### 2. ConfidenceScorer (`confidence_scorer.py`)

**Role:** Calculates reliability and quality metrics for discovered APIs

**Scoring Components:**

1. **Completeness Score** (Weight: 0.3)
   - Ratio of present fields to expected fields
   - Formula: `fields_present / total_expected_fields`

2. **Reliability Score** (Weight: 0.4)
   - Based on data source type
   - Range: 0.2 (unknown) to 0.95 (official_doc)
   - Source types: official_doc, known_api_db, partner_api, code_repository, blog, web_search, forum, unknown

3. **Recency Score** (Weight: 0.15)
   - Time-based decay (10% per year)
   - Formula: `max(0, 1 - (age_in_years * 0.1))`

4. **Validation Score** (Weight: 0.15)
   - Boolean: 1.0 if validated, 0.0 if not

**Weighted Overall Score:**
```python
overall_score = (
    completeness * 0.3 +
    reliability * 0.4 +
    recency * 0.15 +
    validation * 0.15
)
```

---

#### 3. APIPatternRecognizer (`pattern_recognizer.py`)

**Role:** Identifies API design patterns and conventions

**Pattern Detection Areas:**

1. **Naming Conventions**
   - Analyzes: paths, parameters, body keys, schema names
   - Detects: snake_case, camelCase, PascalCase, UPPER_SNAKE_CASE, kebab-case
   - Output: Convention type and usage count

2. **Versioning Strategies**
   - Path-based: `/api/v1`, `/v2.0/users`
   - Header-based: `X-API-Version`, `Accept: application/vnd.api+json;version=1`
   - Query parameter: `?version=1`, `?api_version=2.0`
   - Output: Detected strategy and all versions found

3. **Authentication Schemes**
   - OpenAPI security schemes (apiKey, http, oauth2)
   - Observed auth headers (Authorization, X-API-Key, etc.)
   - Query parameter auth (apikey, access_token, token)
   - Output: Scheme types and locations (header/query)

4. **Pagination Patterns**
   - Page-based: page, page_number
   - Size-based: limit, per_page, pagesize
   - Offset-based: offset, skip
   - Cursor-based: cursor, next_token, continuation_token
   - Link headers: rel="next", rel="prev"

5. **Data Formats**
   - Content-Type analysis (application/json, text/xml, etc.)
   - Request/response format detection
   - Accept header parsing

6. **HTTP Methods**
   - Usage patterns: GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD, etc.
   - Method distribution across endpoints

7. **Status Codes**
   - Response code patterns: 200, 201, 400, 401, 404, 500, etc.
   - Status code frequency analysis

---

#### 4. ResultCache (`result_cache.py`)

**Role:** Persistent caching layer to reduce redundant processing

**Features:**
- **Storage:** Python shelve (persistent key-value store)
- **TTL:** Configurable max age (default: 7 days / 604800 seconds)
- **Key Generation:** SHA256 hash of JSON-serialized parameters
- **Auto-cleanup:** Removes stale entries on access
- **Thread-safe:** Context manager support

**Cache Locations** (in priority order):
1. `~/.cache/api_discovery_tool/result_cache.db`
2. `./.cache/api_discovery_tool/result_cache.db` (fallback)

**Usage Example:**
```python
with ResultCache(max_age_seconds=3600) as cache:
    # Check cache
    cached_result = cache.get(params)
    if cached_result:
        return cached_result

    # Process data
    result = expensive_processing(params)

    # Store in cache
    cache.put(params, result)
    return result
```

---

#### 5. Categorizer (`categorizer.py`)

**Role:** Classifies API endpoints by protocol and design pattern

**Supported API Types:**
- **REST** - RESTful HTTP APIs with standard methods
- **GraphQL** - GraphQL APIs with query/mutation support
- **SOAP** - SOAP/WSDL-based web services
- **WebSocket** - Real-time WebSocket connections
- **Unknown** - Unclassified or static content

**Classification Logic** (priority order):
1. Check protocol (`ws://`, `wss://`) → WebSocket
2. Check GraphQL indicators (path `/graphql`, query/mutation in body) → GraphQL
3. Check SOAP indicators (WSDL, SOAP envelope, XML content-type) → SOAP
4. Check REST indicators (OpenAPI spec, standard HTTP methods, JSON) → REST
5. Default → Unknown

---

#### 6. Deduplicator (`deduplicator.py`)

**Role:** Removes duplicate API endpoints from discovery results

**Deduplication Strategy:**
- Normalizes URLs (lowercase, remove protocol/www, strip trailing slashes)
- Creates unique signatures: `(normalized_url, HTTP_METHOD)`
- Preserves first occurrence, discards duplicates

**Normalization Example:**
```
HTTPS://WWW.Example.COM/api/users/ (GET)
http://example.com/api/users (GET)
→ Same normalized signature: (example.com/api/users, GET)
```

---

## Module Relationships

### Dependency Graph

```
app.py (Flask Application)
├── Flask Framework
│   ├── Flask-Limiter (rate limiting)
│   ├── Flask-SQLAlchemy (ORM)
│   └── SQLAlchemy (database)
├── api.routes.health (health check endpoint)
├── api.routes.validation (URL validation endpoint)
│   └── api.services.compliance (robots.txt checking)
└── api_discovery_tool.processing.ResultProcessor
    ├── confidence_scorer.ConfidenceScorer
    ├── result_cache.ResultCache
    └── pattern_recognizer.APIPatternRecognizer

api-discovery-tool.py (CLI)
├── Selenium WebDriver
├── BeautifulSoup
├── Requests
└── urllib.robotparser (robots.txt compliance)
```

### Communication Patterns

1. **Flask Routes → Services → Processing Pipeline**
   - HTTP request → Route handler → Service layer → ResultProcessor → Response

2. **ResultProcessor Orchestration**
   - Input validation → Cache lookup → Scoring + Pattern recognition → Cache store → Output

3. **Independent Utilities**
   - Categorizer and Deduplicator can be used standalone or integrated into pipeline

4. **Caching Layer**
   - Transparent to callers, managed by ResultProcessor

---

## Data Flow

### CLI Discovery Flow

```
User executes: python api-discovery-tool.py <URL>
        │
        ▼
┌────────────────────────────────┐
│  APIDiscoveryTool.__init__()   │
│  • Parse arguments             │
│  • Initialize logging          │
│  • Set headless mode           │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│  check_robots_txt()            │
│  • Parse robots.txt            │
│  • Check user-agent rules      │
│  • Respect disallow directives │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  run_discovery() - Multi-Method Discovery  │
│                                            │
│  1. analyze_html_source()                  │
│     ├─ Parse inline JavaScript             │
│     ├─ Find data-* attributes              │
│     ├─ Analyze forms and actions           │
│     └─ Extract external scripts            │
│                                            │
│  2. analyze_javascript_code()              │
│     ├─ Regex patterns for fetch()          │
│     ├─ Regex patterns for axios            │
│     ├─ Regex patterns for $.ajax          │
│     └─ Extract API endpoints               │
│                                            │
│  3. discover_common_endpoints()            │
│     ├─ Test /api, /v1, /graphql, etc.     │
│     └─ Check HTTP response codes           │
│                                            │
│  4. discover_with_selenium()               │
│     ├─ Start Chrome with DevTools          │
│     ├─ Monitor network traffic             │
│     ├─ Detect JavaScript frameworks        │
│     ├─ Trigger user interactions           │
│     └─ Capture XHR/Fetch requests          │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│  generate_report()             │
│  • Aggregate all discoveries   │
│  • Deduplicate endpoints       │
│  • Calculate statistics        │
│  • Format as JSON              │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│  save_report(filename)         │
│  • Write to file               │
│  • Display summary             │
└────────────────────────────────┘
```

### Flask API Processing Flow

```
POST /api/process
   {
     "discovery_method": "mitmproxy",
     "data": [...],
     "openapi_spec": {...},
     "http_interactions": [...]
   }
        │
        ▼
┌─────────────────────────┐
│  Request Validation     │
│  • Check JSON format    │
│  • Validate required    │
│    fields               │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  ResultProcessor.process_results()  │
│                                     │
│  1. Generate cache key              │
│     └─ SHA256(method + data)        │
│                                     │
│  2. Check cache                     │
│     └─ Return if fresh cached data  │
│                                     │
│  3. Initialize ConfidenceScorer     │
│     └─ With spec + interactions     │
│                                     │
│  4. Calculate confidence            │
│     ├─ Completeness score           │
│     ├─ Reliability score            │
│     ├─ Recency score                │
│     └─ Validation score             │
│                                     │
│  5. Run APIPatternRecognizer        │
│     ├─ Naming conventions           │
│     ├─ Versioning strategies        │
│     ├─ Authentication schemes       │
│     ├─ Pagination patterns          │
│     ├─ Data formats                 │
│     ├─ HTTP methods                 │
│     └─ Status codes                 │
│                                     │
│  6. Aggregate results               │
│     └─ Combine scores + patterns    │
│                                     │
│  7. Store in cache                  │
│     └─ With TTL                     │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│  JSON Response          │
│  {                      │
│    "discovery_method",  │
│    "analysis_summary",  │
│    "confidence_score",  │
│    "api_conventions"    │
│  }                      │
└─────────────────────────┘
```

---

## Design Decisions

### 1. Modular Processing Pipeline

**Decision:** Separate concerns into independent, composable modules

**Rationale:**
- Easier testing (each module has dedicated unit tests)
- Flexible composition (use only what you need)
- Clear responsibilities (single responsibility principle)
- Independent evolution (modules can be updated separately)

**Trade-offs:**
- More files to maintain
- Requires orchestration layer (ResultProcessor)

---

### 2. Dual Interface (CLI + API)

**Decision:** Provide both command-line and web API interfaces

**Rationale:**
- CLI for standalone usage, scripting, and quick analysis
- API for integration into larger systems and web UIs
- Different use cases without code duplication

**Trade-offs:**
- Two codebases to maintain
- Some logic duplication (but minimal due to shared processing modules)

---

### 3. Persistent Caching with TTL

**Decision:** Use shelve-based persistent cache with configurable expiry

**Rationale:**
- Reduce redundant processing (some analyses are expensive)
- Persistent across sessions (survives application restarts)
- Configurable TTL (balance freshness vs. performance)
- Simple implementation (no external cache server needed)

**Trade-offs:**
- Disk I/O overhead
- Cache invalidation complexity
- Not suitable for distributed deployments (file-based)

---

### 4. Pattern Recognition Over Hard-Coded Rules

**Decision:** Analyze actual API usage patterns rather than assuming standards

**Rationale:**
- APIs don't always follow conventions
- Detect actual patterns used (not just documented ones)
- Flexible analysis (works with partial or missing specs)
- Useful for undocumented APIs

**Trade-offs:**
- More complex analysis logic
- May miss uncommon patterns
- Requires sufficient sample data

---

### 5. Ethical Operation by Default

**Decision:** Respect robots.txt and implement rate limiting

**Rationale:**
- Legal compliance (robots.txt is a web standard)
- Respectful of server resources
- Reduces risk of IP blocking
- Professional tool design

**Trade-offs:**
- May miss disallowed endpoints
- Slower discovery (rate limiting)
- Additional implementation complexity

---

### 6. Multi-Method Discovery

**Decision:** Combine static analysis, dynamic monitoring, and probing

**Rationale:**
- Different methods find different APIs
- Comprehensive coverage (no single method is complete)
- Redundancy increases confidence
- Handles various API documentation approaches

**Trade-offs:**
- Longer execution time
- More complex orchestration
- Potential duplicate findings (requires deduplication)

---

## Discovery Methods

The CLI tool (`api-discovery-tool.py`) uses five complementary discovery methods:

### 1. HTML Source Analysis

**Approach:** Parse HTML for inline JavaScript, data attributes, forms

**Finds:**
- Data attributes (`data-api-url`, `data-endpoint`)
- Form action URLs
- Inline JavaScript with API calls
- External script references

**Pros:** Fast, no browser needed
**Cons:** Misses dynamically loaded content

---

### 2. JavaScript Code Analysis

**Approach:** Regex pattern matching for API call syntax

**Patterns Detected:**
- `fetch('...')` calls
- `axios.get/post/...` calls
- `$.ajax({ url: '...' })` calls
- `XMLHttpRequest.open('...', '...')` calls

**Pros:** Finds hardcoded API endpoints
**Cons:** May miss dynamic URL construction

---

### 3. Network Monitoring (Selenium)

**Approach:** Browser automation with Chrome DevTools Protocol

**Captures:**
- XHR requests
- Fetch API calls
- WebSocket connections
- Network traffic metadata (headers, status codes, timing)

**Pros:** Sees actual API traffic
**Cons:** Requires browser, slower, complex setup

---

### 4. Common Endpoint Probing

**Approach:** Test well-known API paths

**Tests:**
- `/api`, `/api/v1`, `/api/v2`
- `/graphql`, `/rest`, `/services`
- `/swagger.json`, `/openapi.json`
- `/api-docs`, `/.well-known/`

**Pros:** Finds undocumented APIs
**Cons:** May trigger security alerts, not all sites use standard paths

---

### 5. JavaScript Framework Detection

**Approach:** Identify frameworks to understand API patterns

**Detects:**
- React, Vue, Angular, Svelte
- jQuery, Axios
- GraphQL clients
- API SDK libraries

**Pros:** Context for API usage patterns
**Cons:** Indirect signal, not guaranteed to find APIs

---

## Extension Points

The architecture provides several extension points for customization:

### 1. Adding New Discovery Methods

**Location:** `api-discovery-tool.py` → `APIDiscoveryTool` class

**Steps:**
1. Add new method to `APIDiscoveryTool` class
2. Call method in `run_discovery()`
3. Aggregate results in `generate_report()`

**Example:**
```python
def discover_with_har_file(self, har_file_path):
    """Analyze HAR file for API endpoints"""
    # Implementation
    pass
```

---

### 2. Adding New Pattern Recognition

**Location:** `api_discovery_tool/processing/pattern_recognizer.py`

**Steps:**
1. Add new method to `APIPatternRecognizer` class
2. Call method in `identify_all_patterns()`
3. Add unit tests in `tests/test_pattern_recognizer.py`

**Example:**
```python
def identify_error_handling(self):
    """Detect error response patterns"""
    # Implementation
    return {"error_formats": [...]}
```

---

### 3. Custom Categorization Rules

**Location:** `api_discovery_tool/processing/categorizer.py`

**Steps:**
1. Add new constants for API types
2. Add detection logic to `categorize_api_type()`
3. Update tests in `tests/test_categorizer.py`

**Example:**
```python
API_TYPE_GRPC = 'gRPC'

def _is_grpc(endpoint_data):
    """Detect gRPC APIs"""
    # Implementation
    return False
```

---

### 4. Adding New Scoring Factors

**Location:** `api_discovery_tool/processing/confidence_scorer.py`

**Steps:**
1. Add new scoring method
2. Update `WEIGHTS` dictionary
3. Include in `calculate_overall_score()`
4. Add tests in `tests/test_scoring.py`

**Example:**
```python
def calculate_documentation_score(self):
    """Score based on documentation quality"""
    # Implementation
    return 0.5
```

---

### 5. Custom Flask Endpoints

**Location:** `api/routes/` (create new blueprint)

**Steps:**
1. Create new route file (e.g., `custom_analysis.py`)
2. Define Flask Blueprint
3. Register blueprint in `app.py`
4. Add endpoint documentation

**Example:**
```python
# api/routes/custom_analysis.py
from flask import Blueprint

custom_bp = Blueprint('custom', __name__)

@custom_bp.route('/api/custom-analysis', methods=['POST'])
def custom_analysis():
    # Implementation
    return {"result": "..."}
```

---

## Performance Considerations

### Caching Strategy

- **Cache Hit:** ~10ms (shelve lookup)
- **Cache Miss:** 100-500ms (full processing)
- **Cache Effectiveness:** ~60-80% hit rate (depends on workload)

### Bottlenecks

1. **Selenium WebDriver:** 5-15 seconds per URL (browser startup, page load, network monitoring)
2. **External HTTP Requests:** 100-300ms per endpoint test
3. **Pattern Recognition:** 50-100ms (regex intensive for large specs)

### Optimization Strategies

- Enable caching with appropriate TTL
- Use headless mode for Selenium (faster than headed)
- Implement request pooling for common endpoint probing
- Consider parallel processing for multiple URLs

---

## Security Considerations

### Input Validation

- All user-provided URLs validated with `validators` library
- JSON input sanitized before processing
- SQL injection protection via SQLAlchemy ORM

### robots.txt Compliance

- Checks before any HTTP request
- Configurable with `--respect-robots` flag
- Logs violations (does not proceed)

### Rate Limiting

- Flask API: 60 requests/minute per IP (default)
- Configurable via Flask-Limiter
- Prevents abuse of processing resources

### Secrets Management

- API keys via environment variables (`.env` file)
- No hardcoded credentials
- `.env.example` for documentation only

---

## Testing Architecture

### Test Organization

```
api_discovery_tool/processing/tests/
├── test_caching.py              # ResultCache tests
├── test_scoring.py              # ConfidenceScorer tests
├── test_pattern_recognizer.py   # Pattern recognition tests
├── test_categorizer.py          # API categorization tests
└── test_deduplicator.py         # Deduplication tests
```

### Test Coverage

- **Unit Tests:** Each processing module has dedicated tests
- **Coverage:** ~80% of processing pipeline code
- **Mocking:** External dependencies (HTTP requests, file I/O) mocked
- **Edge Cases:** Empty inputs, malformed data, missing fields

### Running Tests

```bash
# All tests
python -m unittest discover -s api_discovery_tool/processing/tests

# Specific module
python -m unittest api_discovery_tool.processing.tests.test_scoring

# With coverage
coverage run -m unittest discover
coverage report
```

---

## Deployment Considerations

### CLI Deployment

**Requirements:**
- Python 3.7+
- Chrome/Chromium browser (for Selenium)
- ChromeDriver (matching Chrome version)

**Installation:**
```bash
pip install -r requirements.txt
python api-discovery-tool.py --help
```

---

### Flask API Deployment

**Production Setup:**
- Use WSGI server (Gunicorn, uWSGI)
- Reverse proxy (Nginx, Apache)
- Database migration for SQLAlchemy models
- Environment-specific configuration

**Example with Gunicorn:**
```bash
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

**Docker Deployment:**
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app:app"]
```

---

## Future Architecture Enhancements

### Planned Improvements

1. **Distributed Caching:** Redis/Memcached for multi-instance deployments
2. **Async Processing:** Celery task queue for long-running discoveries
3. **WebSocket Support:** Real-time progress updates for CLI and API
4. **Plugin System:** Dynamic loading of custom discovery methods
5. **Database Models:** Store discovery history, user preferences
6. **GraphQL API:** Alternative to REST for flexible queries
7. **Observability:** Prometheus metrics, OpenTelemetry tracing

### Scalability Roadmap

- Horizontal scaling with load balancer
- Database read replicas for high query load
- CDN for static assets
- Microservices architecture (discovery, processing, storage as separate services)

---

## References

- [README.md](README.md) - User documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) - Developer guide
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API reference
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration guide
- [requirements.txt](requirements.txt) - Python dependencies
- [DOCUMENTATION_TODO.md](DOCUMENTATION_TODO.md) - Documentation backlog

---

**Document Status:** Complete
**Maintained By:** Development Team
**Review Cycle:** Quarterly or with major architectural changes

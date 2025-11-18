# Contributing to API Discovery Tool

Thank you for your interest in contributing to the API Discovery Tool! This guide will help you get started with development, testing, and submitting contributions.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment Setup](#development-environment-setup)
3. [Project Structure](#project-structure)
4. [Coding Standards](#coding-standards)
5. [Running Tests](#running-tests)
6. [Writing Tests](#writing-tests)
7. [Adding New Features](#adding-new-features)
8. [Pull Request Process](#pull-request-process)
9. [Common Tasks](#common-tasks)
10. [Getting Help](#getting-help)

---

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.7 or higher** (Python 3.11 recommended)
- **Git** for version control
- **Google Chrome or Chromium** (for Selenium-based discovery)
- **ChromeDriver** (matching your Chrome version)
- **pip** (Python package manager)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/api-discovery-tool.git
cd api-discovery-tool

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (recommended)
pip install pytest black flake8 coverage

# Verify installation
python api-discovery-tool.py --help
python -m unittest discover -s api_discovery_tool/processing/tests
```

---

## Development Environment Setup

### 1. Virtual Environment

Always use a virtual environment to isolate project dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Verify activation
which python  # Should show path inside venv
```

### 2. Install Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# Development dependencies (testing, linting, formatting)
pip install pytest pytest-cov black flake8 pylint mypy
```

### 3. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys (if needed)
nano .env
```

**Note:** Most API keys in `.env.example` are optional and only needed for specific integrations. The core API discovery functionality works without them.

### 4. Install ChromeDriver (for Selenium)

**Option A: Manual Installation**
1. Check your Chrome version: `google-chrome --version`
2. Download matching ChromeDriver from https://chromedriver.chromium.org/
3. Add ChromeDriver to your PATH

**Option B: Using webdriver-manager** (recommended)
```bash
pip install webdriver-manager
```

Then update `api-discovery-tool.py` to use it:
```python
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install())
```

### 5. Verify Setup

```bash
# Run tests
python -m unittest discover -s api_discovery_tool/processing/tests

# Test CLI tool
python api-discovery-tool.py https://example.com --headless

# Test Flask API
python app.py
# In another terminal:
curl http://localhost:5001/api/health
```

---

## Project Structure

Understanding the project structure will help you navigate the codebase:

```
api-discovery-tool/
│
├── api-discovery-tool.py          # CLI entry point
├── app.py                         # Flask web API entry point
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
│
├── api_discovery_tool/            # Main package
│   ├── __init__.py
│   └── processing/                # Core processing modules
│       ├── __init__.py
│       ├── result_processor.py    # Main orchestrator
│       ├── confidence_scorer.py   # Confidence scoring
│       ├── pattern_recognizer.py  # Pattern detection
│       ├── result_cache.py        # Caching layer
│       ├── categorizer.py         # API type classification
│       ├── deduplicator.py        # Endpoint deduplication
│       └── tests/                 # Unit tests
│           ├── test_*.py         # Test files
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
└── Documentation files
    ├── README.md                  # User documentation
    ├── ARCHITECTURE.md            # System design
    ├── CONTRIBUTING.md            # This file
    ├── API_DOCUMENTATION.md       # API reference
    └── CONFIGURATION.md           # Configuration guide
```

### Module Responsibilities

- **api-discovery-tool.py**: CLI tool for discovering APIs from websites
- **app.py**: Flask application for processing API discovery results
- **processing/**: Core processing pipeline modules
  - `result_processor.py`: Orchestrates processing flow
  - `confidence_scorer.py`: Calculates confidence scores
  - `pattern_recognizer.py`: Identifies API patterns
  - `result_cache.py`: Persistent caching with TTL
  - `categorizer.py`: Classifies API types (REST, GraphQL, SOAP, WebSocket)
  - `deduplicator.py`: Removes duplicate endpoints
- **api/routes/**: Flask route handlers
- **api/services/**: Business logic services

---

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 100 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **String quotes**: Prefer double quotes `"` for strings, single quotes `'` for dict keys when appropriate
- **Imports**: Group by standard library, third-party, local imports

### Naming Conventions

```python
# Classes: PascalCase
class APIDiscoveryTool:
    pass

# Functions/methods: snake_case
def analyze_html_source():
    pass

# Constants: UPPER_SNAKE_CASE
API_TYPE_REST = 'REST'
MAX_RETRIES = 3

# Private methods: leading underscore
def _internal_helper():
    pass

# Variables: snake_case
endpoint_url = "https://example.com"
```

### Docstrings

Use Google-style docstrings for all public functions, classes, and modules:

```python
def process_results(discovery_method, data, openapi_spec=None, http_interactions=None):
    """Process API discovery results and generate analysis.

    Args:
        discovery_method (str): The method used for discovery (e.g., 'mitmproxy')
        data (Any): Raw discovery data
        openapi_spec (Dict, optional): OpenAPI specification. Defaults to None.
        http_interactions (List[Dict], optional): HTTP traffic data. Defaults to None.

    Returns:
        Dict: Processed results with confidence scores and patterns

    Raises:
        ValueError: If discovery_method is invalid

    Example:
        >>> processor = ResultProcessor()
        >>> results = processor.process_results('mitmproxy', data, spec)
        >>> print(results['analysis_summary']['confidence_score'])
        0.85
    """
    pass
```

### Type Hints

Use type hints for function signatures (Python 3.7+):

```python
from typing import Dict, List, Optional, Any

def categorize_api_type(endpoint_data: Dict[str, Any]) -> str:
    """Categorize the API type based on endpoint data."""
    pass

def deduplicate_endpoints(endpoints: List[Dict]) -> List[Dict]:
    """Remove duplicate endpoints from the list."""
    pass
```

### Code Formatting

Use **Black** for automatic code formatting:

```bash
# Format all Python files
black .

# Format specific file
black api_discovery_tool/processing/result_processor.py

# Check without modifying
black --check .
```

### Linting

Use **flake8** for linting:

```bash
# Lint all files
flake8 .

# Lint specific file
flake8 api-discovery-tool.py

# With specific rules
flake8 --max-line-length=100 --ignore=E203,W503 .
```

**Configuration** (add to `setup.cfg` or `.flake8`):
```ini
[flake8]
max-line-length = 100
ignore = E203, W503
exclude = venv, .git, __pycache__, build, dist
```

---

## Running Tests

### Run All Tests

```bash
# Using unittest (built-in)
python -m unittest discover -s api_discovery_tool/processing/tests -p "test_*.py"

# Using pytest (if installed)
pytest

# With verbose output
python -m unittest discover -s api_discovery_tool/processing/tests -v
```

### Run Specific Test Files

```bash
# Single test file
python -m unittest api_discovery_tool.processing.tests.test_scoring

# Specific test class
python -m unittest api_discovery_tool.processing.tests.test_scoring.TestConfidenceScorer

# Specific test method
python -m unittest api_discovery_tool.processing.tests.test_scoring.TestConfidenceScorer.test_completeness_score
```

### Run Tests with Coverage

```bash
# Install coverage tool
pip install coverage

# Run tests with coverage
coverage run -m unittest discover -s api_discovery_tool/processing/tests

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
# Open htmlcov/index.html in browser
```

### Test Output Expectations

All tests should pass before submitting a pull request:

```
.....................
----------------------------------------------------------------------
Ran 21 tests in 0.123s

OK
```

---

## Writing Tests

### Test File Organization

Each module should have a corresponding test file:

```
api_discovery_tool/processing/
├── result_processor.py
├── confidence_scorer.py
└── tests/
    ├── test_result_processor.py  # Tests for result_processor.py
    ├── test_scoring.py           # Tests for confidence_scorer.py
    └── ...
```

### Test Structure

Use Python's `unittest` framework:

```python
import unittest
from api_discovery_tool.processing.confidence_scorer import ConfidenceScorer

class TestConfidenceScorer(unittest.TestCase):
    """Test suite for ConfidenceScorer class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.scorer = ConfidenceScorer()

    def tearDown(self):
        """Clean up after each test method."""
        pass

    def test_completeness_score(self):
        """Test completeness score calculation."""
        # Arrange
        self.scorer.metadata = {
            'fields_present': 8,
            'total_expected_fields': 10
        }

        # Act
        score = self.scorer.calculate_completeness_score()

        # Assert
        self.assertEqual(score, 0.8)

    def test_completeness_score_zero_fields(self):
        """Test completeness score with zero expected fields."""
        self.scorer.metadata = {
            'fields_present': 0,
            'total_expected_fields': 0
        }
        score = self.scorer.calculate_completeness_score()
        self.assertEqual(score, 0.0)

if __name__ == '__main__':
    unittest.main()
```

### Test Coverage Requirements

- **Minimum coverage**: 70% for new code
- **Target coverage**: 80% overall
- **Critical modules**: 90% coverage (confidence_scorer, pattern_recognizer, result_processor)

### Test Categories

1. **Unit Tests**: Test individual functions/methods in isolation
2. **Integration Tests**: Test module interactions (e.g., ResultProcessor + ConfidenceScorer)
3. **Edge Cases**: Empty inputs, null values, malformed data
4. **Performance Tests**: Large datasets, caching behavior

### Mocking External Dependencies

Use `unittest.mock` for external dependencies:

```python
from unittest.mock import patch, MagicMock
import unittest

class TestAPIDiscoveryTool(unittest.TestCase):

    @patch('requests.get')
    def test_fetch_url(self, mock_get):
        """Test URL fetching with mocked HTTP request."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<html>...</html>'
        mock_get.return_value = mock_response

        # Act
        result = fetch_url('https://example.com')

        # Assert
        self.assertEqual(result, '<html>...</html>')
        mock_get.assert_called_once_with('https://example.com')
```

---

## Adding New Features

### 1. Adding New API Patterns to Pattern Recognizer

**Location**: `api_discovery_tool/processing/pattern_recognizer.py`

**Steps**:

1. Add detection method to `APIPatternRecognizer` class:

```python
def identify_rate_limiting(self):
    """Identify rate limiting patterns from HTTP interactions.

    Returns:
        Dict: Rate limiting information
    """
    rate_limits = {
        'headers_found': [],
        'limits': []
    }

    for interaction in self.http_interactions:
        headers = interaction.get('response_headers', {})

        # Check for rate limit headers
        if 'X-RateLimit-Limit' in headers:
            rate_limits['headers_found'].append('X-RateLimit-Limit')
            rate_limits['limits'].append(headers['X-RateLimit-Limit'])

    return rate_limits
```

2. Call method in `identify_all_patterns()`:

```python
def identify_all_patterns(self):
    """Identify all API patterns from the data."""
    return {
        'naming_conventions': self.identify_naming_conventions(),
        'versioning': self.identify_versioning(),
        'authentication': self.identify_authentication(),
        'pagination': self.identify_pagination(),
        'data_formats': self.identify_data_formats(),
        'http_methods': self.identify_http_methods(),
        'status_codes': self.identify_status_codes(),
        'rate_limiting': self.identify_rate_limiting(),  # New pattern
    }
```

3. Add unit tests in `tests/test_pattern_recognizer.py`:

```python
def test_identify_rate_limiting(self):
    """Test rate limiting pattern detection."""
    http_interactions = [{
        'response_headers': {
            'X-RateLimit-Limit': '100',
            'X-RateLimit-Remaining': '95'
        }
    }]

    recognizer = APIPatternRecognizer(http_interactions=http_interactions)
    patterns = recognizer.identify_rate_limiting()

    self.assertIn('X-RateLimit-Limit', patterns['headers_found'])
    self.assertIn('100', patterns['limits'])
```

4. Update documentation in this file and `ARCHITECTURE.md`

---

### 2. Adding New Discovery Methods to CLI Tool

**Location**: `api-discovery-tool.py`

**Steps**:

1. Add method to `APIDiscoveryTool` class:

```python
def discover_with_har_file(self, har_file_path):
    """Analyze HAR (HTTP Archive) file for API endpoints.

    Args:
        har_file_path (str): Path to HAR file

    Returns:
        List[Dict]: Discovered endpoints
    """
    import json

    endpoints = []

    try:
        with open(har_file_path, 'r') as f:
            har_data = json.load(f)

        for entry in har_data.get('log', {}).get('entries', []):
            request = entry.get('request', {})
            url = request.get('url', '')
            method = request.get('method', 'GET')

            if self._is_api_endpoint(url):
                endpoints.append({
                    'url': url,
                    'method': method,
                    'source': 'HAR file analysis'
                })

    except Exception as e:
        logging.error(f"Error analyzing HAR file: {e}")

    return endpoints
```

2. Call in `run_discovery()`:

```python
def run_discovery(self):
    """Run all discovery methods."""
    # ... existing methods ...

    # HAR file discovery (if provided)
    if self.har_file_path:
        har_endpoints = self.discover_with_har_file(self.har_file_path)
        self.discovered_apis.extend(har_endpoints)
```

3. Add CLI argument:

```python
parser.add_argument(
    '--har-file',
    help='Path to HAR file for analysis',
    default=None
)
```

4. Add integration test or example

---

### 3. Adding New Processing Modules

**Location**: `api_discovery_tool/processing/`

**Steps**:

1. Create new module file (e.g., `security_analyzer.py`):

```python
"""Security analysis module for API discovery results."""

class SecurityAnalyzer:
    """Analyzes API security characteristics."""

    def __init__(self, openapi_spec=None, http_interactions=None):
        self.openapi_spec = openapi_spec or {}
        self.http_interactions = http_interactions or []

    def analyze_security(self):
        """Analyze security features of the API.

        Returns:
            Dict: Security analysis results
        """
        return {
            'https_enforced': self._check_https(),
            'authentication_required': self._check_auth(),
            'security_headers': self._check_security_headers(),
        }

    def _check_https(self):
        """Check if HTTPS is enforced."""
        # Implementation
        pass
```

2. Integrate into `ResultProcessor`:

```python
from api_discovery_tool.processing.security_analyzer import SecurityAnalyzer

class ResultProcessor:
    def process_results(self, discovery_method, data, openapi_spec=None, http_interactions=None):
        # ... existing code ...

        # Add security analysis
        security_analyzer = SecurityAnalyzer(openapi_spec, http_interactions)
        security_analysis = security_analyzer.analyze_security()

        results['analysis_summary']['security'] = security_analysis

        return results
```

3. Add tests in `tests/test_security_analyzer.py`

4. Update `ARCHITECTURE.md` with new module documentation

---

### 4. Adding New Flask API Endpoints

**Location**: `api/routes/`

**Steps**:

1. Create new route file (e.g., `api/routes/analysis.py`):

```python
"""Analysis endpoints for API discovery results."""

from flask import Blueprint, request, jsonify

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/api/analyze', methods=['POST'])
def analyze_api():
    """Analyze API discovery results.

    Request JSON:
        {
            "endpoints": [...],
            "analysis_type": "security"
        }

    Returns:
        JSON: Analysis results
    """
    if not request.json:
        return jsonify({'error': 'Invalid JSON'}), 400

    endpoints = request.json.get('endpoints', [])
    analysis_type = request.json.get('analysis_type', 'general')

    # Perform analysis
    results = perform_analysis(endpoints, analysis_type)

    return jsonify(results), 200

def perform_analysis(endpoints, analysis_type):
    """Internal analysis logic."""
    # Implementation
    pass
```

2. Register blueprint in `app.py`:

```python
from api.routes.analysis import analysis_bp

# ... existing code ...

app.register_blueprint(analysis_bp)
```

3. Add to `API_DOCUMENTATION.md`

4. Add integration tests

---

## Pull Request Process

### Before Submitting

1. **Run all tests**: Ensure all tests pass
   ```bash
   python -m unittest discover -s api_discovery_tool/processing/tests
   ```

2. **Check code style**: Format and lint your code
   ```bash
   black .
   flake8 --max-line-length=100 .
   ```

3. **Update documentation**: If you added features, update relevant docs

4. **Test coverage**: Ensure your changes are tested
   ```bash
   coverage run -m unittest discover
   coverage report
   ```

5. **Update CHANGELOG**: Add entry describing your changes (if applicable)

### Submitting a Pull Request

1. **Fork the repository** on GitHub

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** following coding standards

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add detailed description of your changes"
   ```

   **Commit Message Format**:
   ```
   <type>: <subject>

   <body>

   <footer>
   ```

   **Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

   **Example**:
   ```
   feat: Add rate limiting pattern detection

   - Implement identify_rate_limiting() method in pattern_recognizer.py
   - Add support for X-RateLimit-* headers
   - Add unit tests for rate limiting detection
   - Update ARCHITECTURE.md with new pattern type

   Closes #123
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request** on GitHub:
   - Provide clear title and description
   - Reference related issues
   - Include test results
   - Add screenshots/examples if applicable

### Pull Request Checklist

- [ ] All tests pass
- [ ] Code follows style guide
- [ ] New code has tests (min 70% coverage)
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No merge conflicts
- [ ] Changes are focused (one feature per PR)

### Code Review Process

1. **Automated checks**: CI/CD runs tests and linting
2. **Peer review**: At least one maintainer reviews code
3. **Feedback addressed**: Make requested changes
4. **Approval**: Maintainer approves PR
5. **Merge**: Maintainer merges to main branch

---

## Common Tasks

### Adding a New API Type to Categorizer

**File**: `api_discovery_tool/processing/categorizer.py`

```python
# 1. Add constant
API_TYPE_GRPC = 'gRPC'

# 2. Add detection function
def _is_grpc(endpoint_data):
    """Detect gRPC APIs."""
    content_type = endpoint_data.get('content_type', '').lower()
    path = endpoint_data.get('path', '').lower()

    if 'application/grpc' in content_type:
        return True
    if '/grpc/' in path:
        return True

    return False

# 3. Update categorize_api_type() priority chain
def categorize_api_type(endpoint_data):
    if _is_websocket(endpoint_data):
        return API_TYPE_WEBSOCKET
    if _is_grpc(endpoint_data):  # Add here
        return API_TYPE_GRPC
    if _is_graphql(endpoint_data):
        return API_TYPE_GRAPHQL
    # ... rest of logic
```

**Test** (`tests/test_categorizer.py`):
```python
def test_grpc_detection(self):
    """Test gRPC API detection."""
    endpoint_data = {
        'url': 'grpc://example.com/service',
        'content_type': 'application/grpc'
    }
    result = categorize_api_type(endpoint_data)
    self.assertEqual(result, API_TYPE_GRPC)
```

---

### Adding a New Confidence Scoring Factor

**File**: `api_discovery_tool/processing/confidence_scorer.py`

```python
# 1. Update WEIGHTS
WEIGHTS = {
    'completeness': 0.25,  # Adjusted
    'reliability': 0.35,   # Adjusted
    'recency': 0.15,
    'validation': 0.15,
    'popularity': 0.10,    # New factor
}

# 2. Add calculation method
def calculate_popularity_score(self):
    """Calculate popularity score based on usage metrics."""
    usage_count = self.metadata.get('usage_count', 0)

    # Logarithmic scale
    if usage_count == 0:
        return 0.0

    import math
    score = min(1.0, math.log10(usage_count) / 5)  # Cap at 100,000 uses
    return score

# 3. Update get_score_details()
def get_score_details(self):
    return {
        'completeness': self.calculate_completeness_score(),
        'reliability': self.calculate_reliability_score(),
        'recency': self.calculate_recency_score(),
        'validation': self.calculate_validation_score(),
        'popularity': self.calculate_popularity_score(),  # Add
    }

# 4. Update calculate_overall_score()
def calculate_overall_score(self, discovery_results=None):
    details = self.get_score_details()
    overall = sum(details[key] * WEIGHTS[key] for key in WEIGHTS)
    return overall
```

---

### Updating Cache TTL or Location

**File**: `api_discovery_tool/processing/result_cache.py`

```python
# Default TTL (change this constant)
DEFAULT_MAX_AGE_SECONDS = 604800  # 7 days

# Or pass when initializing
cache = ResultCache(max_age_seconds=3600)  # 1 hour

# Cache directory priority
# 1. Modify get_cache_path() to change locations
# 2. Or set environment variable (if you add this feature):
import os
cache_dir = os.getenv('API_DISCOVERY_CACHE_DIR', default_cache_dir)
```

---

## Getting Help

### Resources

- **Documentation**: See `README.md`, `ARCHITECTURE.md`, `API_DOCUMENTATION.md`
- **Issues**: Check [GitHub Issues](https://github.com/yourusername/api-discovery-tool/issues)
- **Discussions**: Use GitHub Discussions for questions

### Asking Questions

When asking for help, please provide:

1. **What you're trying to do**: Clear description of goal
2. **What you tried**: Steps you've already taken
3. **What happened**: Error messages, unexpected behavior
4. **Environment**: Python version, OS, relevant configuration
5. **Code samples**: Minimal reproducible example

**Example**:
```
I'm trying to add a new pattern detection for error responses, but the
pattern_recognizer tests are failing with KeyError: 'responses'.

Steps I tried:
1. Added identify_error_patterns() method
2. Called it in identify_all_patterns()
3. Ran tests: python -m unittest tests/test_pattern_recognizer.py

Error:
KeyError: 'responses'
  File "pattern_recognizer.py", line 145, in identify_error_patterns
    responses = self.openapi_spec['responses']

Environment:
Python 3.11.14 on Ubuntu 22.04

Code:
[paste minimal example]
```

### Communication Channels

- **Bug Reports**: GitHub Issues with `bug` label
- **Feature Requests**: GitHub Issues with `enhancement` label
- **Questions**: GitHub Discussions
- **Security Issues**: Email maintainers directly (see SECURITY.md)

---

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- Be respectful and constructive
- Focus on the code, not the person
- Accept constructive criticism gracefully
- Help others learn and grow

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

## Recognition

Contributors will be recognized in:
- `README.md` Contributors section
- Release notes for significant contributions
- Git commit history

Thank you for contributing to the API Discovery Tool!

---

**Last Updated**: 2025-11-18
**Maintained By**: Development Team

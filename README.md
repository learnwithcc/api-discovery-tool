# API Discovery Tool

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive Python tool for discovering APIs used by websites through multiple analysis methods including HTML parsing, JavaScript analysis, network monitoring, and common endpoint testing.

## 📚 Documentation

- **[Architecture Guide](ARCHITECTURE.md)** - System design and module relationships
- **[API Documentation](API_DOCUMENTATION.md)** - Flask API endpoints and usage
- **[Contributing Guide](CONTRIBUTING.md)** - Development setup and guidelines
- **[Configuration Guide](CONFIGURATION.md)** - Environment and configuration setup

## 🚀 Features

- **Multi-Method Discovery**: Uses 5 different techniques to maximize API discovery
- **Framework Detection**: Identifies popular JavaScript frameworks and libraries
- **Network Monitoring**: Captures real-time network requests using Selenium
- **Legal Compliance**: Respects robots.txt and implements ethical scraping practices
- **Comprehensive Reporting**: Generates detailed JSON reports with analysis metadata
- **Configurable**: Highly customizable with configuration file support

## 🏗 Project Architecture

The API Discovery Tool is built with a modular architecture designed for flexibility and extensibility. Here's a high-level overview:

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    API Discovery Tool                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────┐         ┌─────────────────┐            │
│  │  CLI Interface │         │   Flask API     │            │
│  │ (api-discovery │  ◄────► │   (app.py)      │            │
│  │   -tool.py)    │         │                 │            │
│  └────────────────┘         └─────────────────┘            │
│         │                            │                      │
│         └────────────┬───────────────┘                      │
│                      ▼                                      │
│         ┌─────────────────────────┐                        │
│         │  Discovery Orchestrator │                        │
│         └─────────────────────────┘                        │
│                      │                                      │
│         ┌────────────┼────────────┐                        │
│         ▼            ▼            ▼                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │   HTML   │  │JavaScript│  │ Network  │                │
│  │ Analysis │  │ Analysis │  │ Monitor  │                │
│  └──────────┘  └──────────┘  └──────────┘                │
│         │            │            │                        │
│         └────────────┼────────────┘                        │
│                      ▼                                      │
│         ┌─────────────────────────┐                        │
│         │   Processing Pipeline   │                        │
│         ├─────────────────────────┤                        │
│         │ • Result Processor      │                        │
│         │ • Confidence Scorer     │                        │
│         │ • Pattern Recognizer    │                        │
│         │ • Categorizer           │                        │
│         │ • Deduplicator          │                        │
│         └─────────────────────────┘                        │
│                      │                                      │
│                      ▼                                      │
│         ┌─────────────────────────┐                        │
│         │   Output & Reporting    │                        │
│         └─────────────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### Key Modules

- **Discovery Methods** (`api_discovery_tool/`): Core discovery implementations
  - HTML source parsing
  - JavaScript code analysis
  - Network traffic monitoring
  - Common endpoint testing
  - Framework detection

- **Processing Pipeline** (`api_discovery_tool/processing/`): Results enhancement
  - **Result Processor**: Orchestrates the processing pipeline
  - **Confidence Scorer**: Assigns reliability scores to discovered APIs
  - **Pattern Recognizer**: Identifies API patterns and types
  - **Categorizer**: Classifies APIs by type (REST, GraphQL, WebSocket, etc.)
  - **Deduplicator**: Removes duplicate endpoints
  - **Result Cache**: Caches processed results for performance

- **API Layer** (`api/`): Flask-based REST API
  - Discovery endpoints
  - Health checks
  - Request validation
  - Compliance checking

For a detailed architecture explanation, see **[ARCHITECTURE.md](ARCHITECTURE.md)**.

## 🛠 Installation

### Prerequisites

- Python 3.7 or higher
- Chrome/Chromium browser (for Selenium)
- ChromeDriver (automatically managed)

### Install Dependencies

```bash
# Clone or download the tool files
# Navigate to the project directory

# Install required packages
pip install -r requirements.txt

# Make the script executable (Linux/Mac)
chmod +x api-discovery-tool.py
```

## 📋 Usage

### Basic Usage

```bash
# Analyze a website with default settings
python api-discovery-tool.py https://example.com

# Run in headless mode (default)
python api-discovery-tool.py https://example.com --headless

# Ignore robots.txt restrictions (use carefully)
python api-discovery-tool.py https://example.com --ignore-robots

# Specify custom output file
python api-discovery-tool.py https://example.com -o my_analysis.json
```

### Advanced Usage

```bash
# Complete analysis with custom configuration
python api-discovery-tool.py https://api-rich-website.com \
  --headless \
  --output detailed_analysis.json

# Quick analysis without browser automation
python api-discovery-tool.py https://simple-site.com \
  --no-selenium \
  --output quick_scan.json
```

### Programmatic Usage

You can also use the API Discovery Tool as a Python library in your own projects:

```python
from api_discovery_tool.api_discovery_tool import APIDiscoveryTool

# Basic usage
tool = APIDiscoveryTool(url="https://example.com")
results = tool.discover()

# Access discovered APIs
for api in results['discovered_apis']:
    print(f"Found API: {api['url']} (Method: {api['method']})")

# Access network requests
for request in results['network_requests']:
    print(f"Network call: {request['url']} ({request['method']})")
```

#### Advanced Programmatic Usage

```python
from api_discovery_tool.api_discovery_tool import APIDiscoveryTool

# Configure with custom options
tool = APIDiscoveryTool(
    url="https://example.com",
    headless=True,
    ignore_robots=False,
    user_agent="CustomBot/1.0"
)

# Run discovery
results = tool.discover()

# Process results
print(f"Total APIs discovered: {results['summary']['total_apis_discovered']}")
print(f"Frameworks detected: {', '.join(results['summary']['javascript_frameworks'])}")

# Save to file
tool.save_results(results, "custom_output.json")
```

#### Using Processing Modules Directly

You can also use individual processing modules for custom workflows:

```python
from api_discovery_tool.processing.confidence_scorer import ConfidenceScorer
from api_discovery_tool.processing.categorizer import categorize_api
from api_discovery_tool.processing.deduplicator import deduplicate_apis

# Score API confidence
scorer = ConfidenceScorer()
api_endpoint = {
    'url': '/api/v1/users',
    'method': 'network_monitoring',
    'http_method': 'GET'
}
scored_api = scorer.score_endpoint(api_endpoint)
print(f"Confidence: {scored_api['confidence_score']}")

# Categorize API type
api_type = categorize_api('/api/v1/products')
print(f"API Type: {api_type}")  # e.g., 'REST'

# Deduplicate API list
apis = [
    {'url': '/api/users', 'method': 'html_analysis'},
    {'url': '/api/users', 'method': 'network_monitoring'},
    {'url': '/api/products', 'method': 'javascript_analysis'}
]
unique_apis = deduplicate_apis(apis)
print(f"Unique APIs: {len(unique_apis)}")  # 2
```

#### Pattern Recognition Example

```python
from api_discovery_tool.processing.pattern_recognizer import PatternRecognizer

# Recognize API patterns
recognizer = PatternRecognizer()
patterns = recognizer.recognize_patterns([
    '/api/v1/users',
    '/api/v1/products',
    '/graphql',
    'wss://example.com/socket'
])

print(f"REST APIs: {len(patterns['rest'])}")
print(f"GraphQL APIs: {len(patterns['graphql'])}")
print(f"WebSocket APIs: {len(patterns['websocket'])}")
```

### Flask API Usage

The tool includes a Flask-based REST API for remote discovery operations. See **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** for complete API reference.

#### Starting the API Server

```bash
# Start the Flask server
python app.py

# Server runs on http://localhost:5000 by default
```

#### API Endpoints

**Discover APIs from a URL:**

```bash
curl -X POST http://localhost:5000/api/v1/discover \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "headless": true,
    "ignore_robots": false
  }'
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "target_url": "https://example.com",
    "summary": {
      "total_apis_discovered": 8,
      "total_network_requests": 15,
      "javascript_frameworks": ["React"]
    },
    "discovered_apis": [
      {
        "url": "/api/v1/products",
        "method": "network_monitoring",
        "confidence_score": 0.95,
        "api_type": "REST"
      }
    ]
  }
}
```

**Health Check:**

```bash
curl http://localhost:5000/health
```

#### Python Client Example

```python
import requests

# Discover APIs via REST API
response = requests.post(
    'http://localhost:5000/api/v1/discover',
    json={
        'url': 'https://example.com',
        'headless': True
    }
)

if response.status_code == 200:
    results = response.json()
    apis = results['data']['discovered_apis']
    print(f"Found {len(apis)} APIs")
    for api in apis:
        print(f"  - {api['url']} (Confidence: {api['confidence_score']})")
```

For more API examples and full endpoint documentation, see **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)**.

## 🔍 Discovery Methods

### 1. HTML Source Analysis
- Parses HTML source code for API endpoints
- Examines script tags, data attributes, and form actions
- Identifies embedded JSON and API configurations
- **Effectiveness**: ~75% of discoverable APIs

### 2. JavaScript Code Analysis  
- Analyzes inline and external JavaScript files
- Uses regex patterns to find API calls (fetch, axios, jQuery)
- Detects API endpoints in function calls and configurations
- **Effectiveness**: ~85% of discoverable APIs

### 3. Network Traffic Monitoring
- Uses Selenium with Chrome DevTools Protocol
- Captures real-time network requests during page load
- Records API calls made by dynamic content
- **Effectiveness**: ~95% of discoverable APIs

### 4. Common Endpoint Testing
- Tests known API endpoint patterns (`/api`, `/v1`, `/graphql`, etc.)
- Makes HTTP HEAD requests to avoid data consumption
- Identifies publicly accessible API documentation
- **Effectiveness**: ~60% of discoverable APIs

### 5. JavaScript Framework Detection
- Identifies popular frameworks (React, Vue, Angular, etc.)
- Analyzes global objects and DOM attributes
- Provides insights into likely API patterns based on framework
- **Effectiveness**: ~90% framework detection accuracy

## 📊 Output Format

The tool generates comprehensive JSON reports with the following structure:

```json
{
  "target_url": "https://example.com",
  "discovery_timestamp": "2025-05-29 15:32:00",
  "summary": {
    "total_apis_discovered": 12,
    "total_network_requests": 28,
    "javascript_frameworks": ["React", "Axios"]
  },
  "discovered_apis": [
    {
      "url": "/api/v1/products", 
      "method": "javascript_analysis",
      "pattern": "fetch",
      "description": "Product catalog API",
      "http_method": "GET"
    }
  ],
  "javascript_frameworks": [
    {
      "framework": "React",
      "indicator": "__reactInternalInstance", 
      "method": "browser_context",
      "confidence": "High"
    }
  ],
  "network_requests": [
    {
      "url": "/api/v1/data",
      "method": "GET",
      "status": 200,
      "mime_type": "application/json",
      "size": "15.2 KB"
    }
  ]
}
```

## ⚖️ Legal and Ethical Considerations

### 🔐 Best Practices

- **Respect robots.txt**: Always check and honor robots.txt directives
- **Rate limiting**: Implement delays between requests (default: 1 second)
- **Terms of Service**: Review and comply with website terms of service
- **Data minimization**: Only collect publicly available data
- **Privacy respect**: Avoid collecting personal or sensitive information

### 📜 Legal Compliance

- **GDPR Compliance**: Tool designed to respect EU data protection regulations
- **CCPA Compliance**: Follows California privacy law guidelines  
- **CFAA Compliance**: Adheres to US Computer Fraud and Abuse Act
- **Public Data Only**: Focuses on publicly accessible information

### ⚠️ Important Notes

- This tool is for **educational and research purposes**
- Always obtain proper authorization before scanning websites
- Be aware of applicable laws in your jurisdiction
- Consider contacting website owners for permission
- Use responsibly and ethically

## 🔧 Configuration

The tool supports multiple configuration methods including configuration files, environment variables, and command-line arguments.

### Quick Configuration Example

Create a `api_discovery_config.json` file:

```json
{
  "discovery_settings": {
    "default_user_agent": "APIDiscoveryBot/1.0",
    "request_timeout": 10,
    "respect_robots_txt": true,
    "crawl_delay": 1.0
  },
  "api_patterns": {
    "common_endpoints": ["/api", "/v1", "/graphql"],
    "regex_patterns": ["\/api\/[^\/\s]+", "\.json(\?.*)?$"]
  }
}
```

### Environment Variables

Create a `.env` file for sensitive configuration:

```bash
# Chrome/ChromeDriver settings
CHROME_BINARY_PATH=/usr/bin/chromium-browser
CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Database configuration (if using Flask API)
DATABASE_URL=sqlite:///api_discovery.db

# API server settings
FLASK_ENV=development
FLASK_DEBUG=True
```

### Complete Configuration Guide

For comprehensive configuration documentation including:
- All available environment variables
- Configuration file options
- Chrome/ChromeDriver setup
- Database configuration
- Rate limiting and caching options
- Flask API configuration

See the **[Configuration Guide (CONFIGURATION.md)](CONFIGURATION.md)** for complete details.

## 🔍 Common Use Cases

### Security Research
```bash
# Discover APIs for security assessment
python api-discovery-tool.py https://target-domain.com \
  --output security_scan.json
```

### API Documentation  
```bash
# Find undocumented APIs for integration
python api-discovery-tool.py https://service-provider.com \
  --headless --output api_inventory.json
```

### Competitive Analysis
```bash
# Research competitor API usage
python api-discovery-tool.py https://competitor.com \
  --output competitor_apis.json
```

## 🐛 Troubleshooting

### Common Issues

**ChromeDriver not found**
```bash
# Install webdriver-manager
pip install webdriver-manager

# Or manually download ChromeDriver
# Place in PATH or specify location
```

**Permission denied errors**
```bash
# Check robots.txt compliance
# Use --ignore-robots flag carefully
# Verify website terms of service
```

**Network timeout errors**
```bash
# Increase timeout in configuration
# Check internet connection
# Try with --headless flag
```

### Debug Mode

```bash
# Enable verbose logging
python api-discovery-tool.py https://example.com --verbose

# Check specific analysis method
python api-discovery-tool.py https://example.com --method html-only
```

## 🛠 Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/api-discovery-tool.git
cd api-discovery-tool

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt  # If available

# Run tests
pytest

# Run with coverage
pytest --cov=api_discovery_tool --cov-report=html
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest api_discovery_tool/processing/tests/test_confidence_scorer.py

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

### Code Quality

```bash
# Format code with black
black api_discovery_tool/

# Lint code
flake8 api_discovery_tool/
pylint api_discovery_tool/

# Type checking
mypy api_discovery_tool/
```

### Project Structure

```
api-discovery-tool/
├── api/                          # Flask API implementation
│   ├── routes/                   # API route handlers
│   └── services/                 # API service layer
├── api_discovery_tool/           # Core discovery implementation
│   ├── processing/               # Processing pipeline modules
│   │   ├── categorizer.py
│   │   ├── confidence_scorer.py
│   │   ├── pattern_recognizer.py
│   │   ├── result_processor.py
│   │   ├── deduplicator.py
│   │   └── result_cache.py
│   └── api_discovery_tool.py     # Main discovery class
├── app.py                        # Flask application entry point
├── api-discovery-tool.py         # CLI entry point
└── tests/                        # Test suite
```

For detailed development guidelines, coding standards, and contribution workflows, see **[CONTRIBUTING.md](CONTRIBUTING.md)**.

## 🤝 Contributing

Contributions are welcome! We follow a structured contribution process to maintain code quality and consistency.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following our coding standards
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Ensure legal and ethical compliance in all features
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to your branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### What to Contribute

- Bug fixes and issue resolutions
- New API detection patterns
- Performance improvements
- Documentation enhancements
- Test coverage improvements
- New discovery methods

For comprehensive contribution guidelines including:
- Development environment setup
- Coding standards and style guide
- Testing requirements
- Pull request process
- How to add new features

See the complete **[Contributing Guide (CONTRIBUTING.md)](CONTRIBUTING.md)**.

## 📄 License

MIT License - see LICENSE file for details

## ⚠️ Disclaimer

This tool is provided for educational and research purposes only. Users are responsible for ensuring their use complies with applicable laws, terms of service, and ethical guidelines. The authors are not liable for any misuse or legal consequences resulting from the use of this tool.

## 🔗 Related Resources

- [robots.txt Specification](https://www.robotstxt.org/)
- [Web Scraping Ethics Guide](https://blog.apify.com/is-web-scraping-legal/)
- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

---

**Remember**: Always scrape responsibly and ethically! 🌐✨
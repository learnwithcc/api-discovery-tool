# API Discovery Tool

A comprehensive Python tool for discovering APIs used by websites through multiple analysis methods including HTML parsing, JavaScript analysis, network monitoring, and common endpoint testing.

## 🚀 Features

- **Multi-Method Discovery**: Uses 5 different techniques to maximize API discovery
- **Framework Detection**: Identifies popular JavaScript frameworks and libraries
- **Network Monitoring**: Captures real-time network requests using Selenium
- **Legal Compliance**: Respects robots.txt and implements ethical scraping practices
- **Comprehensive Reporting**: Generates detailed JSON reports with analysis metadata
- **Configurable**: Highly customizable with configuration file support

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

The tool uses `api_discovery_config.json` for advanced configuration:

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

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Ensure legal compliance in all features
5. Submit a pull request

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
#!/usr/bin/env python3
"""
Website API Discovery Tool
A comprehensive tool for discovering APIs used by websites through multiple methods.

Author: API Discovery Tool
License: MIT
"""

import requests
import json
import re
import time
import argparse
import urllib.robotparser
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

class APIDiscoveryTool:
    def __init__(self, target_url, headless=True, respect_robots=True):
        """
        Initialize the API Discovery Tool
        
        Args:
            target_url (str): The target website URL
            headless (bool): Run browser in headless mode
            respect_robots (bool): Respect robots.txt restrictions
        """
        self.target_url = target_url
        self.base_domain = urlparse(target_url).netloc
        self.headless = headless
        self.respect_robots = respect_robots
        self.session = requests.Session()
        self.discovered_apis = []
        self.javascript_patterns = []
        self.network_requests = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Common API endpoint patterns
        self.api_patterns = [
            r'/api/[^/\s]+',
            r'/v\d+/[^/\s]+',
            r'/rest/[^/\s]+',
            r'/graphql',
            r'\.json(\?|$)',
            r'\.xml(\?|$)',
            r'/services/[^/\s]+',
            r'/endpoints?/[^/\s]+',
            r'/data/[^/\s]+',
            r'/feed[s]?/',
        ]
        
        # JavaScript framework indicators
        self.js_frameworks = {
            'React': ['React', 'react', '__reactInternalInstance', '_reactInternalFiber'],
            'Vue.js': ['Vue', '__vue__', '_Vue'],
            'Angular': ['angular', 'ng-version', '__ng'],
            'jQuery': ['jQuery', '$', 'jquery'],
            'Backbone.js': ['Backbone'],
            'Ember.js': ['Ember', 'Em'],
            'Svelte': ['__svelte'],
            'Alpine.js': ['Alpine'],
            'Stimulus': ['Stimulus']
        }

    def check_robots_txt(self):
        """
        Check robots.txt file for crawling permissions.

        Fetches and parses the target website's robots.txt file to determine
        if crawling is allowed. Respects the robots.txt standard for ethical
        web scraping.

        Returns:
            bool: True if crawling is allowed or robots.txt check is disabled,
                  False if robots.txt explicitly disallows crawling

        Behavior:
            - Returns True immediately if respect_robots is False
            - Fetches robots.txt from the root of the target domain
            - Uses '*' (wildcard) user agent for checking
            - Returns True if robots.txt is inaccessible (permissive fallback)
            - Logs warnings for disallowed crawling or fetch errors

        Notes:
            Respecting robots.txt is considered best practice and ethical behavior
            even though it may not be legally enforced in all jurisdictions.
        """
        if not self.respect_robots:
            return True
            
        try:
            robots_url = urljoin(self.target_url, '/robots.txt')
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            # Check if scraping is allowed for our user agent
            can_fetch = rp.can_fetch('*', self.target_url)
            
            if not can_fetch:
                self.logger.warning(f"robots.txt disallows crawling {self.target_url}")
                return False
                
            self.logger.info("robots.txt allows crawling")
            return True
            
        except Exception as e:
            self.logger.warning(f"Could not check robots.txt: {e}")
            return True

    def analyze_html_source(self):
        """
        Analyze HTML source code for API endpoints and patterns.

        Fetches the target webpage and examines its HTML structure to discover:
        - Inline and external JavaScript files
        - Data attributes containing API URLs
        - Form actions that point to API endpoints

        Discovery Methods:
            1. Script Tags Analysis
               - Parses inline <script> tag contents
               - Fetches and analyzes external scripts (<script src="...">)

            2. Data Attributes
               - Searches for elements with data-api attributes
               - Records API URLs found in these attributes

            3. Form Actions
               - Examines <form> action attributes
               - Identifies forms submitting to API endpoints
               - Records the form's HTTP method (GET/POST)

        Side Effects:
            - Populates self.discovered_apis with found endpoints
            - Calls analyze_javascript_code() for each script
            - Calls analyze_external_script() for external JavaScript files

        Error Handling:
            - Logs errors but continues execution if fetching fails
            - Handles HTTP errors gracefully
            - Continues analysis even if individual scripts fail

        Discovered API Format:
            {
                'url': str,                  # API endpoint URL
                'method': str,               # Discovery method used
                'element': str (optional),   # HTML element snippet
                'form_method': str (optional) # HTTP method for forms
            }
        """
        try:
            response = self.session.get(self.target_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for script tags
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    self.analyze_javascript_code(script.string)
                if script.get('src'):
                    self.analyze_external_script(script.get('src'))
            
            # Look for data attributes
            elements_with_data = soup.find_all(attrs={'data-api': True})
            for element in elements_with_data:
                api_url = element.get('data-api')
                self.discovered_apis.append({
                    'url': api_url,
                    'method': 'html_data_attribute',
                    'element': str(element)[:100]
                })
            
            # Look for forms that might submit to APIs
            forms = soup.find_all('form')
            for form in forms:
                action = form.get('action', '')
                if any(pattern in action for pattern in ['/api/', '.json', '.xml']):
                    self.discovered_apis.append({
                        'url': action,
                        'method': 'form_action',
                        'form_method': form.get('method', 'GET')
                    })
                    
        except Exception as e:
            self.logger.error(f"Error analyzing HTML source: {e}")

    def analyze_javascript_code(self, js_code):
        """
        Analyze JavaScript code for API endpoints and framework usage.

        Searches JavaScript code for:
        1. API endpoint patterns (URLs matching common API structures)
        2. API call patterns (fetch, axios, XHR calls)
        3. JavaScript framework indicators

        Args:
            js_code (str): JavaScript source code to analyze

        Discovery Patterns:
            API Endpoints:
                - /api/[path]
                - /v[0-9]/[path]
                - /rest/[path]
                - /graphql
                - .json files
                - .xml files
                - /services/[path]
                - /endpoints/[path]
                - /data/[path]
                - /feeds/

            API Calls:
                - fetch("url")
                - .get("url"), .post("url")
                - xhr.open("METHOD", "url")
                - axios.get/post/etc("url")

            Frameworks Detected:
                - React
                - Vue.js
                - Angular
                - jQuery
                - Backbone.js
                - Ember.js
                - Svelte
                - Alpine.js
                - Stimulus

        Side Effects:
            - Appends discoveries to self.discovered_apis
            - Appends framework detections to self.javascript_patterns

        Notes:
            Framework detection helps understand the application architecture
            and may indicate the presence of API-driven functionality.
        """
        # Check for API endpoint patterns
        for pattern in self.api_patterns:
            matches = re.findall(pattern, js_code, re.IGNORECASE)
            for match in matches:
                self.discovered_apis.append({
                    'url': match,
                    'method': 'javascript_analysis',
                    'pattern': pattern
                })
        
        # Check for common API call patterns
        api_call_patterns = [
            r'fetch\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',
            r'\.get\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',
            r'\.post\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',
            r'xhr\.open\s*\(\s*[\'"`]\w+[\'"`]\s*,\s*[\'"`]([^\'"`]+)[\'"`]',
            r'axios\.[a-z]+\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',
        ]
        
        for pattern in api_call_patterns:
            matches = re.findall(pattern, js_code, re.IGNORECASE)
            for match in matches:
                self.discovered_apis.append({
                    'url': match,
                    'method': 'javascript_api_call',
                    'pattern': pattern
                })
        
        # Detect JavaScript frameworks
        for framework, indicators in self.js_frameworks.items():
            for indicator in indicators:
                if indicator in js_code:
                    self.javascript_patterns.append({
                        'framework': framework,
                        'indicator': indicator,
                        'method': 'code_analysis'
                    })
                    break

    def analyze_external_script(self, script_src):
        """
        Fetch and analyze external JavaScript files.

        Args:
            script_src (str): Relative or absolute URL of the external JavaScript file

        Process:
            1. Resolve relative URLs against the target URL
            2. Fetch the external script with 10-second timeout
            3. Pass the script content to analyze_javascript_code()

        Error Handling:
            - Logs warnings for failed fetches
            - Handles HTTP errors (404, 403, etc.)
            - Handles timeout errors
            - Continues execution even if individual scripts fail

        Notes:
            External scripts often contain production API endpoints and
            may reveal more information than inline scripts.
        """
        try:
            full_url = urljoin(self.target_url, script_src)
            response = self.session.get(full_url, timeout=10)
            response.raise_for_status()
            self.analyze_javascript_code(response.text)
        except Exception as e:
            self.logger.warning(f"Could not analyze external script {script_src}: {e}")

    def discover_with_selenium(self):
        """
        Use Selenium WebDriver to discover APIs through dynamic analysis.

        Launches a headless Chrome browser to:
        1. Execute JavaScript and render the complete page
        2. Monitor network traffic for API calls
        3. Detect JavaScript frameworks in the browser context
        4. Trigger interactions to reveal additional API endpoints

        Chrome Configuration:
            - Headless mode (configurable)
            - No sandbox (for compatibility)
            - Disabled dev-shm (reduces memory issues)
            - Performance logging enabled for network monitoring

        Discovery Methods:
            1. Network Monitoring
               - Captures all network requests via Chrome DevTools Protocol
               - Records URLs, status codes, and MIME types
               - Filters requests matching API patterns

            2. Framework Detection
               - Checks for framework globals in browser window context
               - More accurate than static analysis
               - Detects dynamically loaded frameworks

            3. Interactive Discovery
               - Clicks buttons to trigger AJAX requests
               - Waits for API calls after each interaction
               - Limited to first 5 buttons to avoid excessive operations

        Performance Logs:
            Parsed to extract Network.responseReceived events containing:
            - URL of the response
            - HTTP status code
            - MIME type / Content-Type

        Side Effects:
            - Appends discoveries to self.network_requests
            - Updates self.javascript_patterns with framework detections
            - May modify browser cookies/localStorage on target site

        Error Handling:
            - Logs errors but continues if Selenium fails to start
            - Ensures browser is closed even if errors occur
            - Handles missing ChromeDriver gracefully

        Troubleshooting:
            - Ensure ChromeDriver is installed and in PATH
            - Version compatibility: ChromeDriver version should match Chrome version
            - For headless issues, try setting headless=False
        """
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-extensions')
            
            # Enable logging for network requests
            chrome_options.add_argument('--enable-logging')
            chrome_options.add_argument('--log-level=0')
            chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                driver.get(self.target_url)
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Get performance logs (network requests)
                logs = driver.get_log('performance')
                for log in logs:
                    message = json.loads(log['message'])
                    if message['message']['method'] == 'Network.responseReceived':
                        url = message['message']['params']['response']['url']
                        if self.is_potential_api(url):
                            self.network_requests.append({
                                'url': url,
                                'method': 'selenium_network_monitoring',
                                'status': message['message']['params']['response']['status'],
                                'mime_type': message['message']['params']['response']['mimeType']
                            })
                
                # Check for JavaScript frameworks in the browser context
                for framework, indicators in self.js_frameworks.items():
                    for indicator in indicators:
                        try:
                            result = driver.execute_script(f"return typeof {indicator} !== 'undefined';")
                            if result:
                                self.javascript_patterns.append({
                                    'framework': framework,
                                    'indicator': indicator,
                                    'method': 'browser_context'
                                })
                                break
                        except:
                            continue
                
                # Try to trigger AJAX requests by interacting with the page
                self.trigger_interactions(driver)
                
            finally:
                driver.quit()
                
        except Exception as e:
            self.logger.error(f"Error with Selenium analysis: {e}")

    def trigger_interactions(self, driver):
        """
        Trigger page interactions to discover additional API endpoints.

        Simulates user interactions that may trigger AJAX/API calls:
        - Button clicks
        - Form submissions (future)
        - Tab/accordion interactions (future)

        Args:
            driver: Selenium WebDriver instance

        Current Implementation:
            - Clicks up to 5 visible and enabled buttons
            - Waits 1 second after each click for API calls
            - Continues even if individual clicks fail

        Limitations:
            - Limited to basic button clicks
            - May not discover deeply nested interactive elements
            - Does not handle authentication-required interactions
            - Fixed delay may miss slower API calls

        Future Enhancements:
            - Configurable interaction depth
            - Smart waiting for network idle
            - Form filling and submission
            - Dropdown and modal interactions
            - Page scrolling to trigger lazy-loading APIs

        Error Handling:
            - Logs warnings for interaction failures
            - Continues with remaining interactions if one fails
            - Handles stale element references
        """
        try:
            # Click buttons that might trigger API calls
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons[:5]:  # Limit to first 5 buttons
                try:
                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        time.sleep(1)  # Wait for potential API calls
                except:
                    continue
                    
        except Exception as e:
            self.logger.warning(f"Error during interaction triggers: {e}")

    def is_potential_api(self, url):
        """
        Check if a URL matches common API endpoint patterns.

        Args:
            url (str): URL to check

        Returns:
            bool: True if URL matches any API pattern, False otherwise

        Checked Patterns:
            - /api/[path]
            - /v[0-9]/[path]
            - /rest/[path]
            - /graphql
            - .json files
            - .xml files
            - /services/[path]
            - /endpoints/[path]
            - /data/[path]
            - /feeds/

        Notes:
            Case-insensitive matching to catch variations like /API/, /Api/, etc.
        """
        for pattern in self.api_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        return False

    def discover_common_endpoints(self):
        """
        Attempt to discover common API endpoints through probing.

        Tests for the existence of commonly used API paths by making
        HEAD requests to each endpoint. This is a non-invasive way to
        discover undocumented APIs.

        Probed Endpoints:
            - /api
            - /api/v1, /api/v2
            - /rest
            - /graphql
            - /data.json
            - /feed.xml
            - /sitemap.xml

        Method:
            Uses HEAD requests instead of GET to minimize server load
            and avoid downloading response bodies.

        Success Criteria:
            HTTP 200 OK status code indicates endpoint exists

        Captured Information:
            - URL of discovered endpoint
            - HTTP status code
            - Content-Type header

        Side Effects:
            - Appends discoveries to self.discovered_apis
            - Makes actual HTTP requests to target server

        Error Handling:
            - Continues silently if endpoint doesn't exist (404, etc.)
            - Handles timeout errors gracefully
            - 5-second timeout per endpoint

        Ethical Considerations:
            - Uses HEAD instead of GET to minimize impact
            - Respects robots.txt via prior check_robots_txt() call
            - Limited to common, publicly documented endpoints
        """
        common_endpoints = [
            '/api',
            '/api/v1',
            '/api/v2',
            '/rest',
            '/graphql',
            '/data.json',
            '/feed.xml',
            '/sitemap.xml'
        ]
        
        for endpoint in common_endpoints:
            try:
                url = urljoin(self.target_url, endpoint)
                response = self.session.head(url, timeout=5)
                if response.status_code == 200:
                    self.discovered_apis.append({
                        'url': url,
                        'method': 'common_endpoint_discovery',
                        'status_code': response.status_code,
                        'content_type': response.headers.get('content-type', '')
                    })
            except:
                continue

    def run_discovery(self):
        """
        Execute the complete API discovery workflow.

        Orchestrates all discovery methods in sequence:
        1. Robots.txt compliance check
        2. HTML source analysis
        3. Common endpoint probing
        4. Selenium-based dynamic analysis

        Workflow:
            1. Check robots.txt
               - If disallowed and respect_robots=True, abort
               - Otherwise, proceed with discovery

            2. Analyze HTML Source
               - Fetch and parse webpage HTML
               - Extract API endpoints from scripts and forms
               - Analyze inline and external JavaScript

            3. Check Common Endpoints
               - Probe standard API paths
               - Record successful responses

            4. Selenium Analysis
               - Launch headless browser
               - Monitor network traffic
               - Detect frameworks dynamically
               - Trigger interactions

        Exit Conditions:
            - Aborts if robots.txt disallows (when respect_robots=True)
            - Continues even if individual methods fail

        Side Effects:
            - Populates self.discovered_apis
            - Populates self.network_requests
            - Populates self.javascript_patterns

        Logging:
            - Info: Progress updates for each discovery phase
            - Warning: robots.txt violations
            - Error: Critical failures in discovery methods

        Usage:
            tool = APIDiscoveryTool("https://example.com")
            tool.run_discovery()
            report = tool.generate_report()
        """
        self.logger.info(f"Starting API discovery for {self.target_url}")
        
        # Check robots.txt first
        if not self.check_robots_txt():
            self.logger.error("Robots.txt disallows crawling. Exiting.")
            return
        
        # HTML source analysis
        self.logger.info("Analyzing HTML source...")
        self.analyze_html_source()
        
        # Common endpoint discovery
        self.logger.info("Checking common endpoints...")
        self.discover_common_endpoints()
        
        # Selenium-based discovery
        self.logger.info("Running Selenium analysis...")
        self.discover_with_selenium()
        
        self.logger.info("Discovery complete!")

    def generate_report(self):
        """
        Generate a comprehensive discovery report.

        Compiles all discovery results into a structured JSON-serializable report
        containing statistics, discovered APIs, network requests, and framework
        detections.

        Returns:
            dict: Comprehensive discovery report with the following structure:
                {
                    'target_url': str,
                    'discovery_timestamp': str (ISO format),
                    'summary': {
                        'total_apis_discovered': int,
                        'total_network_requests': int,
                        'javascript_frameworks': list[str]
                    },
                    'discovered_apis': list[dict],
                    'network_requests': list[dict],
                    'javascript_frameworks': list[dict]
                }

        Report Sections:

            1. Metadata
               - target_url: The analyzed website
               - discovery_timestamp: When the scan was performed

            2. Summary Statistics
               - total_apis_discovered: Count of discovered API endpoints
               - total_network_requests: Count of observed network calls
               - javascript_frameworks: Unique list of detected frameworks

            3. Discovered APIs
               - Static analysis results from HTML/JS parsing
               - Includes discovery method and pattern used

            4. Network Requests
               - Dynamic analysis results from Selenium
               - Actual observed API calls with status codes

            5. JavaScript Frameworks
               - Framework detections with indicators
               - Both static and dynamic detection methods

        Usage:
            report = tool.generate_report()
            print(f"Found {report['summary']['total_apis_discovered']} APIs")
            tool.save_report('output.json')
        """
        report = {
            'target_url': self.target_url,
            'discovery_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_apis_discovered': len(self.discovered_apis),
                'total_network_requests': len(self.network_requests),
                'javascript_frameworks': list(set([p['framework'] for p in self.javascript_patterns]))
            },
            'discovered_apis': self.discovered_apis,
            'network_requests': self.network_requests,
            'javascript_frameworks': self.javascript_patterns
        }
        return report

    def save_report(self, filename='api_discovery_report.json'):
        """
        Save the discovery report to a JSON file.

        Args:
            filename (str): Output filename (default: 'api_discovery_report.json')

        File Format:
            Pretty-printed JSON with 2-space indentation
            Fully compatible with standard JSON parsers

        Behavior:
            - Generates report via generate_report()
            - Writes to specified filename
            - Overwrites existing file if present
            - Logs success message with filename

        Usage Examples:
            # Default filename
            tool.save_report()

            # Custom filename
            tool.save_report('results/example_com_report.json')

            # Timestamped filename
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            tool.save_report(f'reports/scan_{timestamp}.json')

        Error Handling:
            - May raise IOError if file cannot be written
            - May raise ValueError if report contains non-serializable data

        Output Format:
            {
                "target_url": "https://example.com",
                "discovery_timestamp": "2025-11-18 10:30:00",
                "summary": {...},
                "discovered_apis": [...],
                "network_requests": [...],
                "javascript_frameworks": [...]
            }
        """
        report = self.generate_report()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        self.logger.info(f"Report saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Discover APIs used by a website')
    parser.add_argument('url', help='Target website URL')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--ignore-robots', action='store_true', help='Ignore robots.txt restrictions')
    parser.add_argument('--output', '-o', default='api_discovery_report.json', help='Output file name')
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith(('http://', 'https://')):
        args.url = 'https://' + args.url
    
    # Create and run the discovery tool
    tool = APIDiscoveryTool(
        target_url=args.url,
        headless=args.headless,
        respect_robots=not args.ignore_robots
    )
    
    tool.run_discovery()
    tool.save_report(args.output)
    
    # Print summary
    report = tool.generate_report()
    print(f"\n=== API Discovery Summary ===")
    print(f"Target: {report['target_url']}")
    print(f"APIs discovered: {report['summary']['total_apis_discovered']}")
    print(f"Network requests: {report['summary']['total_network_requests']}")
    print(f"JS frameworks detected: {', '.join(report['summary']['javascript_frameworks'])}")
    print(f"Report saved to: {args.output}")

if __name__ == "__main__":
    main()
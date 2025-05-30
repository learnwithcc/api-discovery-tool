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
        """Check robots.txt file for crawling permissions"""
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
        """Analyze HTML source code for API endpoints and patterns"""
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
        """Analyze JavaScript code for API endpoints and frameworks"""
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
        """Analyze external JavaScript files"""
        try:
            full_url = urljoin(self.target_url, script_src)
            response = self.session.get(full_url, timeout=10)
            response.raise_for_status()
            self.analyze_javascript_code(response.text)
        except Exception as e:
            self.logger.warning(f"Could not analyze external script {script_src}: {e}")

    def discover_with_selenium(self):
        """Use Selenium to discover APIs through network monitoring"""
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
        """Trigger interactions that might reveal additional APIs"""
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
        """Check if a URL looks like an API endpoint"""
        for pattern in self.api_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        return False

    def discover_common_endpoints(self):
        """Try to discover common API endpoints by making requests"""
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
        """Run the complete API discovery process"""
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
        """Generate a comprehensive report of discovered APIs"""
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
        """Save the discovery report to a file"""
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
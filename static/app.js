// Demo data
const demoData = {
  ecommerce: {
    target_url: "https://example-ecommerce.com",
    discovery_timestamp: "2025-05-29 15:32:00",
    summary: {
      total_apis_discovered: 12,
      total_network_requests: 28,
      javascript_frameworks: ["React", "Redux", "Axios"]
    },
    discovered_apis: [
      {
        url: "/api/v1/products",
        method: "javascript_analysis",
        pattern: "fetch",
        description: "Product catalog API",
        http_method: "GET"
      },
      {
        url: "/api/v1/cart",
        method: "network_monitoring",
        status_code: 200,
        content_type: "application/json",
        description: "Shopping cart management"
      },
      {
        url: "/api/v1/auth/login",
        method: "form_action",
        http_method: "POST",
        description: "User authentication endpoint"
      },
      {
        url: "/api/v1/search",
        method: "javascript_api_call",
        pattern: "axios.get",
        description: "Product search functionality"
      },
      {
        url: "/api/v1/reviews",
        method: "html_data_attribute",
        description: "Product reviews API"
      },
      {
        url: "/api/v1/recommendations",
        method: "selenium_network_monitoring",
        description: "Product recommendations"
      }
    ],
    javascript_frameworks: [
      {
        framework: "React",
        indicator: "__reactInternalInstance",
        method: "browser_context",
        confidence: "High"
      },
      {
        framework: "Redux",
        indicator: "__REDUX_DEVTOOLS_EXTENSION__",
        method: "code_analysis",
        confidence: "High"
      },
      {
        framework: "Axios",
        indicator: "axios",
        method: "javascript_analysis",
        confidence: "Medium"
      }
    ],
    network_requests: [
      {
        url: "/api/v1/products?page=1&limit=20",
        method: "GET",
        status: 200,
        mime_type: "application/json",
        size: "15.2 KB"
      },
      {
        url: "/api/v1/user/profile",
        method: "GET", 
        status: 200,
        mime_type: "application/json",
        size: "2.1 KB"
      },
      {
        url: "/api/v1/analytics/track",
        method: "POST",
        status: 204,
        mime_type: "text/plain",
        size: "0 KB"
      }
    ]
  },
  news: {
    target_url: "https://example-news.com",
    discovery_timestamp: "2025-05-29 16:15:00",
    summary: {
      total_apis_discovered: 8,
      total_network_requests: 22,
      javascript_frameworks: ["Vue.js", "Vuex"]
    },
    discovered_apis: [
      {
        url: "/api/v2/articles",
        method: "javascript_analysis",
        pattern: "fetch",
        description: "News articles API",
        http_method: "GET"
      },
      {
        url: "/api/v2/categories",
        method: "html_data_attribute",
        description: "Article categories"
      },
      {
        url: "/api/v2/comments",
        method: "network_monitoring",
        status_code: 200,
        content_type: "application/json",
        description: "Comments system"
      },
      {
        url: "/api/v2/newsletter/subscribe",
        method: "form_action",
        http_method: "POST",
        description: "Newsletter subscription"
      }
    ],
    javascript_frameworks: [
      {
        framework: "Vue.js",
        indicator: "__vue__",
        method: "browser_context",
        confidence: "High"
      },
      {
        framework: "Vuex",
        indicator: "$store",
        method: "code_analysis",
        confidence: "High"
      }
    ],
    network_requests: [
      {
        url: "/api/v2/articles?category=tech&limit=10",
        method: "GET",
        status: 200,
        mime_type: "application/json",
        size: "12.8 KB"
      },
      {
        url: "/api/v2/trending",
        method: "GET",
        status: 200,
        mime_type: "application/json",
        size: "3.2 KB"
      }
    ]
  },
  social: {
    target_url: "https://example-social.com",
    discovery_timestamp: "2025-05-29 17:05:00",
    summary: {
      total_apis_discovered: 15,
      total_network_requests: 45,
      javascript_frameworks: ["Angular", "RxJS", "Socket.io"]
    },
    discovered_apis: [
      {
        url: "/api/v1/posts",
        method: "javascript_analysis",
        pattern: "http.get",
        description: "Social media posts",
        http_method: "GET"
      },
      {
        url: "/api/v1/posts",
        method: "javascript_analysis",
        pattern: "http.post",
        description: "Create new post",
        http_method: "POST"
      },
      {
        url: "/api/v1/users/profile",
        method: "network_monitoring",
        status_code: 200,
        content_type: "application/json",
        description: "User profile data"
      },
      {
        url: "/api/v1/notifications",
        method: "websocket_detection",
        description: "Real-time notifications"
      },
      {
        url: "/api/v1/friends",
        method: "javascript_analysis",
        pattern: "http.get",
        description: "Friends list API",
        http_method: "GET"
      }
    ],
    javascript_frameworks: [
      {
        framework: "Angular",
        indicator: "ng-version",
        method: "browser_context",
        confidence: "High"
      },
      {
        framework: "RxJS",
        indicator: "rxjs",
        method: "code_analysis",
        confidence: "High"
      },
      {
        framework: "Socket.io",
        indicator: "io.socket",
        method: "javascript_analysis",
        confidence: "Medium"
      }
    ],
    network_requests: [
      {
        url: "/api/v1/posts?limit=20&offset=0",
        method: "GET",
        status: 200,
        mime_type: "application/json",
        size: "24.1 KB"
      },
      {
        url: "/api/v1/notifications/unread",
        method: "GET",
        status: 200,
        mime_type: "application/json",
        size: "1.8 KB"
      },
      {
        url: "/socket.io/?transport=websocket",
        method: "WS",
        status: 101,
        mime_type: "text/plain",
        size: "0 KB"
      }
    ]
  }
};

// Theme management
class ThemeManager {
  constructor() {
    this.currentTheme = this.getInitialTheme();
    this.init();
  }

  getInitialTheme() {
    const stored = localStorage.getItem('theme');
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  init() {
    this.applyTheme(this.currentTheme);
    this.setupToggle();
  }

  applyTheme(theme) {
    document.documentElement.setAttribute('data-color-scheme', theme);
    const themeIcon = document.getElementById('themeIcon');
    themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
    try {
      localStorage.setItem('theme', theme);
    } catch (e) {
      // Ignore localStorage errors in sandbox
    }
  }

  setupToggle() {
    const toggle = document.getElementById('themeToggle');
    toggle.addEventListener('click', () => {
      this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
      this.applyTheme(this.currentTheme);
    });
  }
}

// Analysis simulation
class AnalysisSimulator {
  constructor() {
    this.analyzeBtn = document.getElementById('analyzeBtn');
    this.demoBtn = document.getElementById('demoBtn');
    this.urlInput = document.getElementById('urlInput');
    this.resultsSection = document.getElementById('resultsSection');
    this.loadingSpinner = document.getElementById('loadingSpinner');
    this.analyzeText = document.getElementById('analyzeText');

    // Summary elements
    this.targetUrlElement = document.getElementById('targetUrl');
    this.discoveryTimeElement = document.getElementById('discoveryTime');
    this.totalApisElement = document.getElementById('totalApis');
    this.totalRequestsElement = document.getElementById('totalRequests');
    this.totalFrameworksElement = document.getElementById('totalFrameworks');
    
    // Table body elements
    this.apisTableBody = document.getElementById('apisTableBody');
    this.frameworksTableBody = document.getElementById('frameworksTableBody');
    this.networkTableBody = document.getElementById('networkTableBody');

    this.setupEventListeners();
  }

  setupEventListeners() {
    this.analyzeBtn.addEventListener('click', () => this.startAnalysis());
    this.demoBtn.addEventListener('click', () => this.showDemoResults());
  }

  async startAnalysis() {
    const targetUrl = this.urlInput.value.trim();
    if (!targetUrl) {
      alert('Please enter a valid URL.');
      return;
    }

    this.showLoadingState(true);
    this.resultsSection.classList.add('hidden'); // Hide previous results

    // Clear previous results from tables and summary
    this.targetUrlElement.textContent = '-';
    this.discoveryTimeElement.textContent = '-';
    this.totalApisElement.textContent = '0';
    this.totalRequestsElement.textContent = '0';
    this.totalFrameworksElement.textContent = '0';
    this.apisTableBody.innerHTML = '';
    this.frameworksTableBody.innerHTML = '';
    this.networkTableBody.innerHTML = '';

    try {
      // Prepare data for the backend /api/process endpoint
      const requestData = {
        discovery_method: "website_analysis", // Or another appropriate method name
        data: { url: targetUrl }, // The backend will decide how to handle this
        openapi_spec: null,       // No pre-existing spec for this type of analysis
        http_interactions: null   // No pre-existing interactions for this type of analysis
      };

      console.log("Sending request to /api/process:", requestData);

      const response = await fetch('/api/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: response.statusText }));
        throw new Error(`HTTP error ${response.status}: ${errorData.message || 'Failed to analyze website.'}`);
      }

      const results = await response.json();
      console.log("Received results from /api/process:", results);
      
      // Assuming the backend returns a structure that can be used by displayResults
      // We might need to adapt what displayResults expects or what the backend returns.
      // For now, let's construct a similar structure to the demo data
      // based on what `ResultProcessor` is expected to return.

      const frontendFormattedResults = {
        target_url: targetUrl,
        discovery_timestamp: new Date().toISOString(), // Use current time
        summary: {
          total_apis_discovered: results.analysis_summary?.api_conventions ? Object.keys(results.analysis_summary.api_conventions).length : 0, // Example
          total_network_requests: results.analysis_summary?.api_conventions?.http_methods?.observed_methods ? Object.values(results.analysis_summary.api_conventions.http_methods.observed_methods).reduce((a, b) => a + b, 0) : 0, // Example
          javascript_frameworks: results.analysis_summary?.api_conventions?.frameworks || [] // Example
        },
        // The `ResultProcessor` output under `api_conventions` would need to be mapped
        // to these structures if we want to display them in the current tables.
        // This is a placeholder and needs careful mapping.
        discovered_apis: [], // Placeholder - map from results.analysis_summary.api_conventions
        javascript_frameworks: [], // Placeholder - map from results.analysis_summary.api_conventions
        network_requests: [] // Placeholder - map from results.analysis_summary.api_conventions
      };
      
      // TODO: Map data from `results.analysis_summary.api_conventions` (and other parts of `results`)
      // to `discovered_apis`, `javascript_frameworks`, `network_requests` tables.
      // For now, we'll just log what we got and show that the analysis is "done"
      // by hiding the spinner. The tables will be empty.
      
      this.displayResults(frontendFormattedResults); // This will show empty tables for now.
      
    } catch (error) {
      console.error('Analysis error:', error);
      alert(`Analysis failed: ${error.message}`);
      // Potentially display error in the UI
    } finally {
      this.showLoadingState(false);
    }
  }

  showLoadingState(show) {
    if (show) {
      this.analyzeBtn.disabled = true;
      this.analyzeText.classList.add('hidden');
      this.loadingSpinner.classList.remove('hidden');
      this.createLoadingOverlay(); // Create overlay when loading starts
    } else {
      this.analyzeBtn.disabled = false;
      this.analyzeText.classList.remove('hidden');
      this.loadingSpinner.classList.add('hidden');
      const overlay = document.getElementById('loadingOverlay');
      if (overlay) {
        overlay.remove(); // Remove overlay when loading finishes
      }
    }
  }

  showDemoResults() {
    const selectedDemo = document.getElementById('demoSelector').value;
    this.loadDemoData(selectedDemo);
  }

  loadDemoData(demoType) {
    const results = demoData[demoType];
    this.displayResults(results);
  }

  displayResults(results) {
    this.resultsSection.classList.remove('hidden');
    
    this.targetUrlElement.textContent = results.target_url || '-';
    this.discoveryTimeElement.textContent = results.discovery_timestamp ? new Date(results.discovery_timestamp).toLocaleString() : '-';
    
    if (results.summary) {
        this.totalApisElement.textContent = results.summary.total_apis_discovered || 0;
        this.totalRequestsElement.textContent = results.summary.total_network_requests || 0;
        this.totalFrameworksElement.textContent = results.summary.javascript_frameworks?.length || 0;
    } else {
        this.totalApisElement.textContent = '0';
        this.totalRequestsElement.textContent = '0';
        this.totalFrameworksElement.textContent = '0';
    }

    this.populateApisTable(results.discovered_apis || []);
    this.populateFrameworksTable(results.javascript_frameworks || []);
    this.populateNetworkTable(results.network_requests || []);

    // Scroll to results
    this.resultsSection.scrollIntoView({ behavior: 'smooth' });
  }

  populateApisTable(apis) {
    const tbody = document.getElementById('apisTableBody');
    tbody.innerHTML = '';

    apis.forEach(api => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td><code>${api.url}</code></td>
        <td><span class="status status--info">${api.http_method || 'N/A'}</span></td>
        <td><span class="method-indicator">${api.method.replace(/_/g, ' ')}</span></td>
        <td>${api.description}</td>
      `;
      tbody.appendChild(row);
    });
  }

  populateFrameworksTable(frameworks) {
    const tbody = document.getElementById('frameworksTableBody');
    tbody.innerHTML = '';

    frameworks.forEach(framework => {
      const row = document.createElement('tr');
      const confidenceClass = `confidence-${framework.confidence.toLowerCase()}`;
      row.innerHTML = `
        <td><strong>${framework.framework}</strong></td>
        <td><code>${framework.indicator}</code></td>
        <td>${framework.method.replace(/_/g, ' ')}</td>
        <td><span class="status ${confidenceClass}">${framework.confidence}</span></td>
      `;
      tbody.appendChild(row);
    });
  }

  populateNetworkTable(requests) {
    const tbody = document.getElementById('networkTableBody');
    tbody.innerHTML = '';

    requests.forEach(request => {
      const row = document.createElement('tr');
      const statusClass = request.status >= 200 && request.status < 300 ? 'status--success' : 'status--error';
      row.innerHTML = `
        <td><code>${request.url}</code></td>
        <td><span class="status status--info">${request.method}</span></td>
        <td><span class="status ${statusClass}">${request.status}</span></td>
        <td>${request.mime_type}</td>
        <td>${request.size}</td>
      `;
      tbody.appendChild(row);
    });
  }

  createLoadingOverlay() {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
      <div class="loading-content">
        <h3>🔍 Analyzing Website</h3>
        <p class="loading-text">Initializing analysis...</p>
        <div class="progress-bar">
          <div class="progress-fill" style="width: 0%"></div>
        </div>
        <p style="font-size: var(--font-size-sm); color: var(--color-text-secondary);">
          This may take a few moments...
        </p>
      </div>
    `;
    return overlay;
  }
}

// Tab management
class TabManager {
  constructor() {
    this.setupTabs();
  }

  setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const targetTab = btn.getAttribute('data-tab');

        // Remove active class from all buttons and contents
        tabBtns.forEach(b => b.classList.remove('active'));
        tabContents.forEach(c => c.classList.remove('active'));

        // Add active class to clicked button and corresponding content
        btn.classList.add('active');
        document.getElementById(`${targetTab}Tab`).classList.add('active');
      });
    });
  }
}

// Export functionality
class ExportManager {
  constructor() {
    this.setupExport();
  }

  setupExport() {
    document.getElementById('exportBtn').addEventListener('click', () => {
      this.exportResults();
    });
  }

  exportResults() {
    const analyzer = window.analysisSimulator;
    if (!analyzer.currentResults) {
      alert('No results to export. Please run an analysis first.');
      return;
    }

    const exportData = {
      export_timestamp: new Date().toISOString(),
      analysis_results: analyzer.currentResults,
      export_format: "JSON",
      tool_version: "1.0.0"
    };

    this.showExportModal(exportData);
  }

  showExportModal(data) {
    const modal = document.createElement('div');
    modal.className = 'export-modal';
    modal.innerHTML = `
      <div class="export-content">
        <div class="flex justify-between items-center" style="margin-bottom: var(--space-16);">
          <h3>📁 Export Results</h3>
          <button class="btn btn--outline btn--sm" onclick="this.closest('.export-modal').remove()">✕ Close</button>
        </div>
        <p style="margin-bottom: var(--space-16); color: var(--color-text-secondary);">
          Copy the JSON data below or download it as a file:
        </p>
        <div class="flex gap-8" style="margin-bottom: var(--space-16);">
          <button class="btn btn--primary btn--sm" onclick="navigator.clipboard.writeText(this.getAttribute('data-json'));" data-json='${JSON.stringify(data, null, 2)}'>
            📋 Copy to Clipboard
          </button>
          <button class="btn btn--secondary btn--sm" onclick="window.exportManager.downloadJSON(${JSON.stringify(data).replace(/"/g, '&quot;')})">
            💾 Download File
          </button>
        </div>
        <pre><code>${JSON.stringify(data, null, 2)}</code></pre>
      </div>
    `;

    document.body.appendChild(modal);

    // Close modal when clicking outside
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.remove();
      }
    });
  }

  downloadJSON(data) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `api-discovery-results-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
}

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
  // Initialize all managers
  window.themeManager = new ThemeManager();
  window.analysisSimulator = new AnalysisSimulator();
  window.tabManager = new TabManager();
  window.exportManager = new ExportManager();

  // Add smooth scrolling for internal links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

  // Add keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to start analysis
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      document.getElementById('analyzeBtn').click();
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
      const modals = document.querySelectorAll('.export-modal, .loading-overlay');
      modals.forEach(modal => modal.remove());
    }
  });

  // Initialize with demo data visible by default
  setTimeout(() => {
    window.analysisSimulator.showDemoResults();
  }, 500);
});
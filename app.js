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
    this.isAnalyzing = false;
    this.setupEventListeners();
  }

  setupEventListeners() {
    document.getElementById('analyzeBtn').addEventListener('click', () => {
      this.startAnalysis();
    });

    document.getElementById('demoBtn').addEventListener('click', () => {
      this.showDemoResults();
    });

    document.getElementById('demoSelector').addEventListener('change', (e) => {
      this.loadDemoData(e.target.value);
    });
  }

  async startAnalysis() {
    if (this.isAnalyzing) return;

    const url = document.getElementById('urlInput').value;
    if (!url) {
      alert('Please enter a website URL');
      return;
    }

    this.isAnalyzing = true;
    this.showLoadingState(true);

    // Simulate analysis progress
    await this.simulateProgress();

    // Show results with entered URL
    const selectedDemo = document.getElementById('demoSelector').value;
    const results = { ...demoData[selectedDemo] };
    results.target_url = url;
    results.discovery_timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);

    this.displayResults(results);
    this.showLoadingState(false);
    this.isAnalyzing = false;
  }

  async simulateProgress() {
    const steps = [
      'Fetching website content...',
      'Analyzing HTML source code...',
      'Parsing JavaScript files...',
      'Monitoring network requests...',
      'Detecting frameworks...',
      'Compiling results...'
    ];

    const overlay = this.createLoadingOverlay();
    document.body.appendChild(overlay);

    for (let i = 0; i < steps.length; i++) {
      const progress = ((i + 1) / steps.length) * 100;
      overlay.querySelector('.loading-text').textContent = steps[i];
      overlay.querySelector('.progress-fill').style.width = `${progress}%`;
      await new Promise(resolve => setTimeout(resolve, 800));
    }

    document.body.removeChild(overlay);
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

  showLoadingState(show) {
    const btn = document.getElementById('analyzeBtn');
    const text = document.getElementById('analyzeText');
    const spinner = document.getElementById('loadingSpinner');

    if (show) {
      text.classList.add('hidden');
      spinner.classList.remove('hidden');
      btn.disabled = true;
    } else {
      text.classList.remove('hidden');
      spinner.classList.add('hidden');
      btn.disabled = false;
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
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.classList.remove('hidden');
    resultsSection.classList.add('fade-in');

    // Update summary
    document.getElementById('targetUrl').textContent = results.target_url;
    document.getElementById('discoveryTime').textContent = results.discovery_timestamp;
    document.getElementById('totalApis').textContent = results.summary.total_apis_discovered;
    document.getElementById('totalRequests').textContent = results.summary.total_network_requests;
    document.getElementById('totalFrameworks').textContent = results.summary.javascript_frameworks.length;

    // Populate tables
    this.populateApisTable(results.discovered_apis);
    this.populateFrameworksTable(results.javascript_frameworks);
    this.populateNetworkTable(results.network_requests);

    // Store current results for export
    this.currentResults = results;

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
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
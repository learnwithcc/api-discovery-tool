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
    this.analyzeBtn = document.getElementById('analyzeBtn');
    this.demoBtn = document.getElementById('demoBtn');
    this.urlInput = document.getElementById('urlInput');
    this.discoveryMethodSelector = document.getElementById('discoveryMethodSelector'); // Added
    this.resultsSection = document.getElementById('resultsSection');
    this.loadingSpinner = document.getElementById('loadingSpinner');
    this.analyzeText = document.getElementById('analyzeText');
    this.currentResults = null; // Added: To store the latest results for export

    // Summary elements (Updated for new structure)
    this.targetUrlDisplay = document.getElementById('targetUrlDisplay');
    this.timestampDisplay = document.getElementById('timestamp');
    this.discoveredCountDisplay = document.getElementById('discoveredCount');
    this.confidenceScoreDisplay = document.getElementById('confidenceScore');
    this.discoveryMethodDisplay = document.getElementById('discoveryMethod');
    
    // Table body elements (Updated for new structure)
    // These IDs must exist in index.html
    this.apiEndpointsTableBody = document.getElementById('apiEndpointsTableBody');
    this.versioningTableBody = document.getElementById('versioningTableBody');
    this.securityPatternsTableBody = document.getElementById('securityPatternsTableBody');
    this.authTableBody = document.getElementById('authTableBody');
    this.dataFormatsTableBody = document.getElementById('dataFormatsTableBody');
    this.paginationTableBody = document.getElementById('paginationTableBody');
    this.rawUrlsTableBody = document.getElementById('rawUrlsTableBody'); // New table for website analysis

    // Old demo table bodies - will be cleared or repurposed
    // Ensure these IDs exist if you plan to use them, otherwise remove references.
    this.apisTableBody = document.getElementById('apisTableBody'); // Potentially old, re-check usage
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

    // Clear previous results from tables and summary (new structure)
    this.targetUrlDisplay.textContent = '-';
    this.timestampDisplay.textContent = '-';
    this.discoveredCountDisplay.textContent = '0';
    this.confidenceScoreDisplay.textContent = '0';
    this.discoveryMethodDisplay.textContent = '-';

    const tableBodiesToClear = [
        this.apiEndpointsTableBody, this.versioningTableBody,
        this.securityPatternsTableBody, this.authTableBody,
        this.dataFormatsTableBody, this.paginationTableBody,
        this.rawUrlsTableBody,
        this.apisTableBody, // old demo table
        this.frameworksTableBody, // old demo table
        this.networkTableBody // old demo table
    ];
    tableBodiesToClear.forEach(tbody => { if(tbody) tbody.innerHTML = ''; });

    try {
      const discoveryMethod = this.discoveryMethodSelector.value;
      let requestDataPayload;
      let openApiSpecForPayload = null;

      if (discoveryMethod === "website_analysis") {
        if (!targetUrl) {
          alert('Please enter a URL for Website Analysis.');
          this.showLoadingState(false);
          return;
        }
        requestDataPayload = { url: targetUrl };
      } else if (discoveryMethod === "openapi_spec") {
        const openapiContentInput = document.getElementById('openapiSpecInput'); // Assuming this ID exists
        const openapiContent = openapiContentInput ? openapiContentInput.value : '';
        if (!openapiContent) {
          alert('Please provide OpenAPI spec content (JSON) or a URL to a spec.');
          this.showLoadingState(false);
          return;
        }
        try {
          // Attempt to parse as JSON first
          requestDataPayload = JSON.parse(openapiContent);
          openApiSpecForPayload = requestDataPayload;
        } catch (e) {
          // If not JSON, assume it's a URL (basic check)
          if (openapiContent.startsWith('http://') || openapiContent.startsWith('https://')) {
            // The backend would need to be able to fetch this URL.
            // For now, the 'data' field for 'openapi_spec' in backend expects the spec itself.
            // This part of UI might need a backend change or a more complex UI flow for URL input.
            // Current backend `ResultProcessor` for `openapi_spec` uses `data` as the spec.
            alert('Pasting spec URL is not directly supported yet. Please paste raw JSON content of the OpenAPI spec.');
            // requestDataPayload = { url: openapiContent }; // If backend were to fetch it
            this.showLoadingState(false);
            return;
          } else {
            alert('Invalid OpenAPI Spec: Not valid JSON and not a recognizable URL.');
            this.showLoadingState(false);
            return;
          }
        }
      } else {
        alert('Selected discovery method is not yet implemented in this UI.');
        this.showLoadingState(false);
        return;
      }

      const requestFullPayload = {
        discovery_method: discoveryMethod,
        data: requestDataPayload,
        openapi_spec: openApiSpecForPayload, // Only send if it's an actual spec object
        http_interactions: null
      };

      console.log("Sending request to /api/process:", JSON.stringify(requestFullPayload, null, 2));

      const response = await fetch('/api/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestFullPayload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: response.statusText, message: 'Analysis failed (could not parse error).', details:'' }));
        throw new Error(`HTTP error ${response.status}: ${errorData.error || errorData.message} ${errorData.details || ''}`);
      }

      const backendResponse = await response.json();
      console.log("Received results from /api/process:", backendResponse);
      
      this.currentResults = backendResponse; // Store for export
      this.processAndDisplayResults(backendResponse, targetUrl);
      
    } catch (error) {
      console.error('Analysis error:', error);
      alert(`Analysis failed: ${error.message || String(error)}`);
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

  // processAndDisplayResults replaces the old displayResults and its helpers
  processAndDisplayResults(response, targetUrlInput) {
    this.resultsSection.classList.remove('hidden');
    
    // Update summary fields
    this.targetUrlDisplay.textContent = targetUrlInput || response.target_url || response.data?.url || '-';
    // Assuming backend response has a root 'timestamp' field. If not, generate one.
    this.timestampDisplay.textContent = response.timestamp ? new Date(response.timestamp).toLocaleString() : new Date().toLocaleString();
    this.discoveryMethodDisplay.textContent = response.discovery_method || 'N/A';
    
    const analysisSummary = response.analysis_summary || {};
    this.confidenceScoreDisplay.textContent = analysisSummary.confidence_score?.toFixed(2) || 'N/A';

    // Clear all potentially populated tables first
    const allTableBodies = [
        this.apiEndpointsTableBody, this.versioningTableBody,
        this.securityPatternsTableBody, this.authTableBody,
        this.dataFormatsTableBody, this.paginationTableBody,
        this.rawUrlsTableBody,
        this.apisTableBody, // old demo table
        this.frameworksTableBody, // old demo table
        this.networkTableBody // old demo table
    ];
    allTableBodies.forEach(tbody => { if(tbody) tbody.innerHTML = ''; });

    const patterns = analysisSummary.api_conventions || {};

    if (response.discovery_method === "website_analysis") {
        // raw_extracted_data should be at response.raw_extracted_data as per subtask.
        // Backend's ResultProcessor puts this into raw_data_summary for website_analysis if it's an object.
        // Let's assume `response.raw_data_summary` holds `{urls: [], text_content: []}` for website_analysis
        const rawExtracted = response.raw_data_summary || {};

        let discoveredEndpointsCount = 0;

        // Populate API Endpoints/Paths Table
        if (this.apiEndpointsTableBody) {
            (patterns.common_paths || []).forEach(path => {
                const row = this.apiEndpointsTableBody.insertRow();
                row.innerHTML = `<td>${escapeHtml(path)}</td><td>Common Path Segment</td><td>-</td>`;
                discoveredEndpointsCount++;
            });
            (patterns.keyword_matches_in_urls || []).forEach(match => {
                const row = this.apiEndpointsTableBody.insertRow();
                row.innerHTML = `<td>${escapeHtml(match.url)}</td><td>URL with Keyword (${escapeHtml(match.keyword)})</td><td>-</td>`;
                discoveredEndpointsCount++;
            });
            if (this.apiEndpointsTableBody.rows.length === 0) {
                 this.apiEndpointsTableBody.innerHTML = '<tr><td colspan="3">No specific API paths or keyworded URLs identified.</td></tr>';
            }
        }
        this.discoveredCountDisplay.textContent = discoveredEndpointsCount;

        // Populate Versioning Table
        if (this.versioningTableBody) {
            (patterns.versioning_schemes || []).forEach(scheme => {
                const row = this.versioningTableBody.insertRow();
                row.innerHTML = `<td>${escapeHtml(scheme)}</td><td>Path</td>`;
            });
             if (this.versioningTableBody.rows.length === 0) {
                this.versioningTableBody.innerHTML = '<tr><td colspan="2">No versioning schemes identified.</td></tr>';
            }
        }

        // Populate Raw Discovered URLs Table
        if (this.rawUrlsTableBody) {
            // Assuming rawExtracted.urls is the correct path from backend response
            const urlsToDisplay = (rawExtracted.urls || []).slice(0, 100);
            urlsToDisplay.forEach(url => {
                const row = this.rawUrlsTableBody.insertRow();
                row.innerHTML = `<td>${escapeHtml(url)}</td>`;
            });
            if (this.rawUrlsTableBody.rows.length === 0) {
                this.rawUrlsTableBody.innerHTML = '<tr><td>No raw URLs extracted or available. (Expected in response.raw_data_summary.urls)</td></tr>';
            }
        }

        // Set "Not Applicable" for other tables not populated by website analysis
        const नाMessage = '<tr><td colspan="100%">Not Applicable for Website Analysis</td></tr>';
        if(this.securityPatternsTableBody) this.securityPatternsTableBody.innerHTML = नाMessage;
        if(this.authTableBody) this.authTableBody.innerHTML = नाMessage;
        if(this.dataFormatsTableBody) this.dataFormatsTableBody.innerHTML = नाMessage;
        if(this.paginationTableBody) this.paginationTableBody.innerHTML = नाMessage;
        // Clear or hide old demo tables
        if(this.apisTableBody) this.apisTableBody.innerHTML = नाMessage;
        if(this.frameworksTableBody) this.frameworksTableBody.innerHTML = नाMessage;
        if(this.networkTableBody) this.networkTableBody.innerHTML = नाMessage;

    } else if (response.discovery_method === "openapi_spec") {
        // Handle OpenAPI spec results
        // This part needs to map openapi_spec patterns to the tables
        let discoveredEndpointsCount = 0;
        if (patterns.spec_methods) {
            Object.values(patterns.spec_methods).forEach(count => discoveredEndpointsCount += count);
        } else if (patterns.http_methods && patterns.http_methods.spec_methods) { // older structure
             Object.values(patterns.http_methods.spec_methods).forEach(count => discoveredEndpointsCount += count);
        }
        this.discoveredCountDisplay.textContent = discoveredEndpointsCount;

        // Example: Populate API Endpoints from OpenAPI paths (if available in patterns)
        // This is a simplified example. Actual paths/endpoints are in response.raw_data_summary (the spec itself)
        // or need to be structured better in `patterns`.
        if (this.apiEndpointsTableBody) {
            this.apiEndpointsTableBody.innerHTML = '<tr><td colspan="3">OpenAPI path details need specific mapping from patterns (TODO)</td></tr>';
        }
        if (this.versioningTableBody) {
            (patterns.versioning?.path_versions || patterns.versioning_schemes || []).forEach(scheme => {
                const row = this.versioningTableBody.insertRow();
                row.innerHTML = `<td>${escapeHtml(scheme)}</td><td>Path</td>`;
            });
            if (this.versioningTableBody.rows.length === 0) {
                this.versioningTableBody.innerHTML = '<tr><td colspan="2">No versioning schemes identified in OpenAPI spec.</td></tr>';
            }
        }
        // TODO: Populate other tables (Security, Auth, Data Formats, Pagination) based on `patterns`
        // For now, show placeholder messages.
        const todoMsg = (name) => `<tr><td colspan="100%">${name} details from OpenAPI spec (TODO)</td></tr>`;
        if(this.securityPatternsTableBody) this.securityPatternsTableBody.innerHTML = todoMsg("Security");
        if(this.authTableBody) this.authTableBody.innerHTML = todoMsg("Authentication");
        if(this.dataFormatsTableBody) this.dataFormatsTableBody.innerHTML = todoMsg("Data Formats");
        if(this.paginationTableBody) this.paginationTableBody.innerHTML = todoMsg("Pagination");
        if(this.rawUrlsTableBody) this.rawUrlsTableBody.innerHTML = todoMsg("Raw URLs (N/A for OpenAPI usually)");

    } else {
        // Fallback for demo or other/unknown methods
        this.discoveredCountDisplay.textContent = analysisSummary.total_apis_discovered || patterns?.discovered_apis?.length || 0;
        const notSupportedMsg = '<tr><td colspan="100%">This discovery method is not fully visualized or data is missing.</td></tr>';
        allTableBodies.forEach(tbody => { if(tbody) tbody.innerHTML = notSupportedMsg; });
    }

    this.resultsSection.scrollIntoView({ behavior: 'smooth' });
  }

  // Comment out or remove old displayResults and its helpers if no longer used by demo mode
  /*
  displayResults(results) { ... }
  populateApisTable(apis) { ... }
  populateFrameworksTable(frameworks) { ... }
  populateNetworkTable(requests) { ... }
  */

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

  // Initialize with demo data visible by default - REMOVED, user triggers analysis or demo
  // setTimeout(() => {
  //   window.analysisSimulator.showDemoResults();
  // }, 500);
});

// Helper function to prevent XSS (should be defined globally or within AnalysisSimulator scope)
function escapeHtml(unsafe) {
  if (typeof unsafe !== 'string') {
    if (unsafe === null || typeof unsafe === 'undefined') {
      return ''; // Return empty string for null or undefined
    }
    try {
      unsafe = String(unsafe); // Try to convert to string
    } catch (e) {
      return ''; // Return empty string if conversion fails
    }
  }
  return unsafe
       .replace(/&/g, "&amp;")
       .replace(/</g, "&lt;")
       .replace(/>/g, "&gt;")
       .replace(/"/g, "&quot;")
       .replace(/'/g, "&#039;");
}
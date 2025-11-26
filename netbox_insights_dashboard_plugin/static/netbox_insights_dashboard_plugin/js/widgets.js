/**
 * NetBox Insights Dashboard - Widget Auto-Refresh and Interactivity
 */

(function() {
    'use strict';
    
    // Configuration
    const REFRESH_INTERVALS = {};
    let refreshTimers = {};
    
    /**
     * Initialize dashboard
     */
    function initDashboard() {
        console.log('Initializing NetBox Insights Dashboard...');
        
        // Initialize all widgets
        document.querySelectorAll('.widget-card').forEach(function(card) {
            const slug = card.id.replace('widget-', '');
            initWidget(slug, card);
        });
        
        // Setup global refresh button
        const refreshAllBtn = document.getElementById('refresh-all');
        if (refreshAllBtn) {
            refreshAllBtn.addEventListener('click', refreshAllWidgets);
        }
        
        // Update refresh time display
        updateRefreshTimeDisplay();
        setInterval(updateRefreshTimeDisplay, 30000); // Update every 30 seconds
    }
    
    /**
     * Initialize a single widget
     */
    function initWidget(slug, cardElement) {
        // Get refresh interval from card footer
        const footer = cardElement.querySelector('.card-footer');
        if (footer) {
            const intervalMatch = footer.textContent.match(/(\d+)s/);
            if (intervalMatch) {
                REFRESH_INTERVALS[slug] = parseInt(intervalMatch[1]) * 1000;
            }
        }
        
        // Load widget data immediately
        loadWidgetData(slug, cardElement);
        
        // Setup auto-refresh
        if (REFRESH_INTERVALS[slug]) {
            refreshTimers[slug] = setInterval(function() {
                loadWidgetData(slug, cardElement);
            }, REFRESH_INTERVALS[slug]);
        }
    }
    
    /**
     * Load widget data via AJAX
     */
    function loadWidgetData(slug, cardElement) {
        const loadingDiv = cardElement.querySelector('.widget-loading');
        const contentDiv = cardElement.querySelector('.widget-content');
        const errorDiv = cardElement.querySelector('.widget-error');
        
        // Show loading state
        if (loadingDiv) loadingDiv.style.display = 'block';
        if (contentDiv) contentDiv.style.display = 'none';
        if (errorDiv) errorDiv.style.display = 'none';
        
        // Make AJAX request
        const url = `/plugins/insights/widgets/${slug}/`;
        
        fetch(url, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            // Widget loaded successfully
            if (loadingDiv) loadingDiv.style.display = 'none';
            if (contentDiv) {
                updateWidgetContent(contentDiv, data);
                contentDiv.style.display = 'block';
            }
            
            console.log(`Widget ${slug} loaded successfully`);
        })
        .catch(error => {
            // Show error state
            console.error(`Error loading widget ${slug}:`, error);
            
            if (loadingDiv) loadingDiv.style.display = 'none';
            if (errorDiv) {
                const errorMsg = errorDiv.querySelector('.widget-error-message');
                if (errorMsg) {
                    errorMsg.textContent = error.message;
                }
                errorDiv.style.display = 'block';
            }
        });
    }
    
    /**
     * Update widget content with new data
     * This would ideally re-render the template, but for now we just reload
     */
    function updateWidgetContent(contentDiv, data) {
        // For now, just trigger a page reload if needed
        // In a production version, we'd use a template engine to re-render
        // or implement incremental DOM updates
        
        // Update last_updated time if element exists
        const lastUpdated = contentDiv.querySelector('[data-last-updated]');
        if (lastUpdated && data.last_updated) {
            lastUpdated.textContent = formatDateTime(data.last_updated);
        }
    }
    
    /**
     * Refresh all widgets
     */
    function refreshAllWidgets() {
        console.log('Refreshing all widgets...');
        
        const refreshBtn = document.getElementById('refresh-all');
        if (refreshBtn) {
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<i class="mdi mdi-loading mdi-spin"></i> Refreshing...';
        }
        
        document.querySelectorAll('.widget-card').forEach(function(card) {
            const slug = card.id.replace('widget-', '');
            loadWidgetData(slug, card);
        });
        
        // Re-enable button after 2 seconds
        setTimeout(function() {
            if (refreshBtn) {
                refreshBtn.disabled = false;
                refreshBtn.innerHTML = '<i class="mdi mdi-refresh"></i> Refresh';
            }
            updateRefreshTimeDisplay();
        }, 2000);
    }
    
    /**
     * Update the "last refreshed" time display
     */
    function updateRefreshTimeDisplay() {
        const refreshTime = document.getElementById('refresh-time');
        if (refreshTime) {
            const now = new Date();
            refreshTime.textContent = now.toLocaleTimeString();
        }
    }
    
    /**
     * Format ISO datetime string
     */
    function formatDateTime(isoString) {
        try {
            const date = new Date(isoString);
            return date.toLocaleString();
        } catch (e) {
            return isoString;
        }
    }
    
    /**
     * Cleanup on page unload
     */
    function cleanup() {
        Object.keys(refreshTimers).forEach(function(slug) {
            clearInterval(refreshTimers[slug]);
        });
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDashboard);
    } else {
        initDashboard();
    }
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', cleanup);
    
})();

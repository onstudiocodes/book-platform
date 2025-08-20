/**
 * Real-time Analytics Dashboard
 * Handles live updates and interactive features
 */

class AnalyticsDashboard {
    constructor() {
        this.updateInterval = 30000; // 30 seconds
        this.charts = {};
        this.isLiveMode = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startLiveUpdates();
    }

    setupEventListeners() {
        // Live mode toggle
        const liveToggle = document.getElementById('liveToggle');
        if (liveToggle) {
            liveToggle.addEventListener('change', (e) => {
                this.isLiveMode = e.target.checked;
                if (this.isLiveMode) {
                    this.startLiveUpdates();
                } else {
                    this.stopLiveUpdates();
                }
            });
        }

        // Export data button
        const exportBtn = document.getElementById('exportData');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportData());
        }

        // Refresh button
        const refreshBtn = document.getElementById('refreshData');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }
    }

    async startLiveUpdates() {
        if (!this.isLiveMode) return;

        try {
            await this.updateRealtimeStats();
            
            if (this.isLiveMode) {
                setTimeout(() => this.startLiveUpdates(), this.updateInterval);
            }
        } catch (error) {
            console.error('Error updating realtime stats:', error);
            if (this.isLiveMode) {
                setTimeout(() => this.startLiveUpdates(), this.updateInterval);
            }
        }
    }

    stopLiveUpdates() {
        this.isLiveMode = false;
    }

    async updateRealtimeStats() {
        try {
            const response = await fetch('/author/api/realtime-stats/');
            const result = await response.json();

            if (result.success) {
                this.updateRealtimeUI(result.data);
            }
        } catch (error) {
            console.error('Failed to fetch realtime stats:', error);
        }
    }

    updateRealtimeUI(data) {
        // Update total followers
        const totalFollowersEl = document.getElementById('totalFollowers');
        if (totalFollowersEl) {
            this.animateNumber(totalFollowersEl, data.total_followers);
        }

        // Update total views
        const totalViewsEl = document.getElementById('totalViews');
        if (totalViewsEl) {
            this.animateNumber(totalViewsEl, data.total_views);
        }

        // Update 24h stats
        const recent24hViewsEl = document.getElementById('recent24hViews');
        if (recent24hViewsEl) {
            this.animateNumber(recent24hViewsEl, data.recent_views_24h);
        }

        const recent24hFollowersEl = document.getElementById('recent24hFollowers');
        if (recent24hFollowersEl) {
            this.animateNumber(recent24hFollowersEl, data.recent_followers_24h);
        }

        // Update timestamp
        const timestampEl = document.getElementById('lastUpdated');
        if (timestampEl) {
            const timestamp = new Date(data.timestamp);
            timestampEl.textContent = `Last updated: ${timestamp.toLocaleTimeString()}`;
        }

        // Show live indicator
        this.showLiveIndicator();
    }

    animateNumber(element, targetValue) {
        const currentValue = parseInt(element.textContent.replace(/,/g, '')) || 0;
        const difference = targetValue - currentValue;
        const duration = 1000; // 1 second
        const steps = 20;
        const stepValue = difference / steps;
        const stepDuration = duration / steps;

        let currentStep = 0;
        const interval = setInterval(() => {
            currentStep++;
            const newValue = Math.round(currentValue + (stepValue * currentStep));
            element.textContent = newValue.toLocaleString();

            if (currentStep >= steps) {
                clearInterval(interval);
                element.textContent = targetValue.toLocaleString();
            }
        }, stepDuration);
    }

    showLiveIndicator() {
        const indicator = document.getElementById('liveIndicator');
        if (indicator) {
            indicator.classList.remove('opacity-0');
            indicator.classList.add('opacity-100');
            
            setTimeout(() => {
                indicator.classList.remove('opacity-100');
                indicator.classList.add('opacity-0');
            }, 2000);
        }
    }

    async refreshData() {
        const refreshBtn = document.getElementById('refreshData');
        if (refreshBtn) {
            refreshBtn.classList.add('animate-spin');
            refreshBtn.disabled = true;
        }

        try {
            await this.updateRealtimeStats();
            
            // Also refresh charts if needed
            const currentDays = new URLSearchParams(window.location.search).get('days') || 28;
            await this.updateChartData(currentDays);
            
        } catch (error) {
            console.error('Error refreshing data:', error);
        } finally {
            if (refreshBtn) {
                refreshBtn.classList.remove('animate-spin');
                refreshBtn.disabled = false;
            }
        }
    }

    async updateChartData(days) {
        try {
            const response = await fetch(`/author/api/analytics/?days=${days}`);
            const result = await response.json();

            if (result.success && this.charts.main) {
                const viewsData = result.data.views.time_series;
                const labels = viewsData.map(item => item.date);
                const data = viewsData.map(item => item.count);

                this.charts.main.data.labels = labels;
                this.charts.main.data.datasets[0].data = data;
                this.charts.main.update('none'); // No animation for smoother updates
            }
        } catch (error) {
            console.error('Failed to update chart data:', error);
        }
    }

    async exportData() {
        try {
            const days = new URLSearchParams(window.location.search).get('days') || 28;
            const response = await fetch(`/author/api/analytics/?days=${days}`);
            const result = await response.json();

            if (result.success) {
                this.downloadJSON(result.data, `analytics-${days}days-${new Date().toISOString().split('T')[0]}.json`);
            }
        } catch (error) {
            console.error('Failed to export data:', error);
            alert('Failed to export data. Please try again.');
        }
    }

    downloadJSON(data, filename) {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    registerChart(name, chartInstance) {
        this.charts[name] = chartInstance;
    }

    // Utility method for formatting numbers
    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    // Method to show tooltips on charts
    showTooltip(chart, point, message) {
        // Implementation for custom tooltips
        const tooltip = document.createElement('div');
        tooltip.className = 'chart-tooltip';
        tooltip.innerHTML = message;
        tooltip.style.position = 'absolute';
        tooltip.style.background = 'rgba(0, 0, 0, 0.8)';
        tooltip.style.color = 'white';
        tooltip.style.padding = '8px 12px';
        tooltip.style.borderRadius = '4px';
        tooltip.style.fontSize = '12px';
        tooltip.style.pointerEvents = 'none';
        tooltip.style.zIndex = '1000';

        document.body.appendChild(tooltip);

        // Position tooltip
        const rect = chart.canvas.getBoundingClientRect();
        tooltip.style.left = (rect.left + point.x) + 'px';
        tooltip.style.top = (rect.top + point.y - 40) + 'px';

        // Remove tooltip after delay
        setTimeout(() => {
            if (tooltip.parentNode) {
                tooltip.parentNode.removeChild(tooltip);
            }
        }, 3000);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.analyticsDashboard = new AnalyticsDashboard();
});

// Additional utility functions for analytics
function formatDateForChart(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function calculateGrowthRate(current, previous) {
    if (previous === 0) return current > 0 ? 100 : 0;
    return ((current - previous) / previous * 100).toFixed(1);
}

function getGrowthIndicator(rate) {
    if (rate > 0) return { icon: 'fa-arrow-up', class: 'text-green-600', text: `+${rate}%` };
    if (rate < 0) return { icon: 'fa-arrow-down', class: 'text-red-600', text: `${rate}%` };
    return { icon: 'fa-minus', class: 'text-gray-600', text: '0%' };
}

// Export for use in templates
window.AnalyticsUtils = {
    formatDateForChart,
    calculateGrowthRate,
    getGrowthIndicator
};

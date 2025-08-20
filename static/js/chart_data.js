/**
 * Enhanced chart rendering for analytics
 */

function render_chart(chartId, labels_array, data_array, label, options = {}) {
    const ctx = document.getElementById(chartId).getContext('2d');

    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            intersect: false,
            mode: 'index'
        },
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                callbacks: {
                    title: function(context) {
                        return context[0].label;
                    },
                    label: function(context) {
                        return `${context.dataset.label}: ${context.parsed.y.toLocaleString()}`;
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return value.toLocaleString();
                    }
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        }
    };

    const chartOptions = { ...defaultOptions, ...options };

    return new Chart(ctx, {
        type: options.type || 'line',
        data: {
            labels: labels_array,
            datasets: [{
                label: label,
                data: data_array,
                backgroundColor: options.backgroundColor || 'rgba(54, 162, 235, 0.1)',
                borderColor: options.borderColor || 'rgba(54, 162, 235, 1)',
                borderWidth: options.borderWidth || 2,
                fill: options.fill !== false,
                tension: options.tension || 0.3
            }]
        },
        options: chartOptions
    });
}

function render_multi_chart(chartId, labels_array, datasets, options = {}) {
    const ctx = document.getElementById(chartId).getContext('2d');

    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            intersect: false,
            mode: 'index'
        },
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                callbacks: {
                    title: function(context) {
                        return context[0].label;
                    },
                    label: function(context) {
                        return `${context.dataset.label}: ${context.parsed.y.toLocaleString()}`;
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return value.toLocaleString();
                    }
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        }
    };

    const chartOptions = { ...defaultOptions, ...options };

    return new Chart(ctx, {
        type: options.type || 'line',
        data: {
            labels: labels_array,
            datasets: datasets
        },
        options: chartOptions
    });
}

function render_comparison_chart(chartId, data, options = {}) {
    const ctx = document.getElementById(chartId).getContext('2d');

    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return `${context.label}: ${context.parsed.toLocaleString()}`;
                    }
                }
            }
        }
    };

    const chartOptions = { ...defaultOptions, ...options };

    return new Chart(ctx, {
        type: options.type || 'doughnut',
        data: data,
        options: chartOptions
    });
}

// Utility functions for chart management
function toggleChart(chart1Id, chart2Id) {
    const chart1Container = document.getElementById(chart1Id).parentElement;
    const chart2Container = document.getElementById(chart2Id).parentElement;
    
    if (chart1Container.classList.contains('hidden')) {
        chart1Container.classList.remove('hidden');
        chart2Container.classList.add('hidden');
    } else {
        chart1Container.classList.add('hidden');
        chart2Container.classList.remove('hidden');
    }
}

function updateChartTimeRange(chartInstance, newLabels, newData) {
    chartInstance.data.labels = newLabels;
    chartInstance.data.datasets[0].data = newData;
    chartInstance.update();
}
/**
 * Stock Market Signal Processing Web App - Main JavaScript
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            html: true
        });
    });

    // File Upload Handling
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const uploadForm = document.getElementById('upload-form');
    const uploadFileName = document.getElementById('upload-filename');

    // Handle the upload area click
    if (uploadArea) {
        uploadArea.addEventListener('click', function() {
            fileInput.click();
        });

        // Update UI when a file is selected
        fileInput.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                uploadFileName.textContent = this.files[0].name;
                uploadArea.classList.add('border-primary');
            }
        });

        // Handle drag and drop
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', function() {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                fileInput.files = e.dataTransfer.files;
                uploadFileName.textContent = e.dataTransfer.files[0].name;
                uploadArea.classList.add('border-primary');
            }
        });
    }

    // Handle form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            // Validate form before submission
            const fileInput = document.getElementById('file-input');
            const tickerInput = document.getElementById('ticker-input');
            
            // If neither file nor ticker is provided, prevent submission
            if ((!fileInput.files || fileInput.files.length === 0) && 
                (!tickerInput.value || tickerInput.value.trim() === '')) {
                e.preventDefault();
                showAlert('Please provide a CSV file or enter a ticker symbol', 'warning');
            }
            
            // Show loading state
            const submitBtn = document.querySelector('button[type="submit"]');
            if (submitBtn && (fileInput.files.length > 0 || tickerInput.value.trim() !== '')) {
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';
                submitBtn.disabled = true;
            }
        });
    }

    // Handle ticker search/suggestion (simplified implementation)
    const tickerInput = document.getElementById('ticker-input');
    const suggestionsList = document.getElementById('ticker-suggestions');
    
    if (tickerInput && suggestionsList) {
        // Sample suggestions (in a real implementation, these would come from an API)
        const popularTickers = [
            { ticker: 'AAPL', name: 'Apple Inc.' },
            { ticker: 'MSFT', name: 'Microsoft Corporation' },
            { ticker: 'GOOGL', name: 'Alphabet Inc.' },
            { ticker: 'AMZN', name: 'Amazon.com, Inc.' },
            { ticker: 'META', name: 'Meta Platforms, Inc.' },
            { ticker: 'TSLA', name: 'Tesla, Inc.' },
            { ticker: 'NVDA', name: 'NVIDIA Corporation' },
            { ticker: 'JPM', name: 'JPMorgan Chase & Co.' }
        ];
        
        tickerInput.addEventListener('input', function() {
            const query = this.value.toUpperCase().trim();
            
            // Clear previous suggestions
            suggestionsList.innerHTML = '';
            
            if (query.length > 0) {
                // Filter suggestions based on input
                const matches = popularTickers.filter(item => 
                    item.ticker.includes(query) || 
                    item.name.toUpperCase().includes(query)
                );
                
                // Display matches
                matches.slice(0, 5).forEach(match => {
                    const item = document.createElement('a');
                    item.classList.add('list-group-item', 'list-group-item-action', 'bg-dark', 'text-white');
                    item.innerHTML = `<strong>${match.ticker}</strong> - ${match.name}`;
                    item.href = '#';
                    
                    item.addEventListener('click', function(e) {
                        e.preventDefault();
                        tickerInput.value = match.ticker;
                        suggestionsList.innerHTML = '';
                    });
                    
                    suggestionsList.appendChild(item);
                });
            }
        });
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (e.target !== tickerInput) {
                suggestionsList.innerHTML = '';
            }
        });
    }

    // Initialize charts if on results page
    const timeSeriesChart = document.getElementById('time-series-chart');
    const frequencyChart = document.getElementById('frequency-chart');
    const forecastChart = document.getElementById('forecast-chart');
    
    if (timeSeriesChart || frequencyChart || forecastChart) {
        initializeCharts();
    }

    // Helper Functions
    function showAlert(message, type = 'info') {
        const alertsContainer = document.getElementById('alerts-container');
        if (!alertsContainer) return;
        
        const alert = document.createElement('div');
        alert.classList.add('alert', `alert-${type}`, 'alert-dismissible', 'fade', 'show');
        alert.role = 'alert';
        
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        alertsContainer.appendChild(alert);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    }

    function initializeCharts() {
        const analysisId = document.getElementById('analysis-data')?.dataset.analysisId;
        if (!analysisId) return;
        
        // Load Time Series Chart
        if (timeSeriesChart) {
            fetch(`/api/plots/${analysisId}/time_series`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to load time series data');
                    }
                    return response.json();
                })
                .then(plotData => {
                    Plotly.newPlot('time-series-chart', plotData.data, plotData.layout, {responsive: true});
                })
                .catch(error => {
                    console.error('Error loading time series chart:', error);
                    timeSeriesChart.innerHTML = `<div class="alert alert-danger">Error loading chart: ${error.message}</div>`;
                });
        }
        
        // Load Frequency Chart
        if (frequencyChart) {
            fetch(`/api/plots/${analysisId}/frequency`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to load frequency data');
                    }
                    return response.json();
                })
                .then(plotData => {
                    Plotly.newPlot('frequency-chart', plotData.data, plotData.layout, {responsive: true});
                })
                .catch(error => {
                    console.error('Error loading frequency chart:', error);
                    frequencyChart.innerHTML = `<div class="alert alert-danger">Error loading chart: ${error.message}</div>`;
                });
        }
        
        // Load Forecast Chart
        if (forecastChart) {
            fetch(`/api/plots/${analysisId}/forecast`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to load forecast data');
                    }
                    return response.json();
                })
                .then(plotData => {
                    Plotly.newPlot('forecast-chart', plotData.data, plotData.layout, {responsive: true});
                })
                .catch(error => {
                    console.error('Error loading forecast chart:', error);
                    forecastChart.innerHTML = `<div class="alert alert-danger">Error loading chart: ${error.message}</div>`;
                });
        }
    }
});

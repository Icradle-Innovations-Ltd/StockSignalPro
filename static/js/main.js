// main.js - JavaScript for CycleTrader

document.addEventListener('DOMContentLoaded', function() {
    // Toggle Advanced Features
    const toggleButton = document.getElementById('toggle-features');
    if (toggleButton) {
        const toggleText = document.getElementById('toggle-text');
        const toggleIcon = document.getElementById('toggle-icon');
        const featureItems = document.querySelectorAll('.feature-item');
        
        toggleButton.addEventListener('click', function() {
            const isExpanded = toggleText.textContent === 'Show less';
            
            featureItems.forEach(item => {
                if (isExpanded) {
                    item.classList.add('d-none');
                } else {
                    item.classList.remove('d-none');
                }
            });
            
            if (isExpanded) {
                toggleText.textContent = 'Show more';
                toggleIcon.classList.remove('fa-chevron-up');
                toggleIcon.classList.add('fa-chevron-down');
            } else {
                toggleText.textContent = 'Show less';
                toggleIcon.classList.remove('fa-chevron-down');
                toggleIcon.classList.add('fa-chevron-up');
            }
        });
    }
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });
    
    // Add active class to current nav item
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentLocation || currentLocation.startsWith(href) && href !== '/') {
            link.classList.add('active');
            
            // If it's in a dropdown, also activate the dropdown
            const dropdown = link.closest('.dropdown');
            if (dropdown) {
                dropdown.querySelector('.dropdown-toggle').classList.add('active');
            }
        }
    });
    
    // File upload handling
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const uploadArea = document.querySelector('.upload-area');
    
    if (uploadArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            uploadArea.classList.add('highlight');
        }
        
        function unhighlight() {
            uploadArea.classList.remove('highlight');
        }
        
        uploadArea.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            fileInput.files = files;
            
            // Show file name
            if (files.length > 0) {
                const fileNameElement = uploadArea.querySelector('#upload-filename');
                if (fileNameElement) {
                    fileNameElement.textContent = files[0].name;
                    
                    // Add visual feedback
                    uploadArea.classList.add('border-primary');
                    uploadArea.querySelector('.upload-icon i').classList.add('text-primary');
                }
            }
        }
        
        // Click to upload
        uploadArea.addEventListener('click', function() {
            fileInput.click();
        });
        
        // Show file name when selected via dialog
        fileInput.addEventListener('change', function() {
            const fileNameElement = uploadArea.querySelector('#upload-filename');
            if (fileNameElement && this.files.length > 0) {
                fileNameElement.textContent = this.files[0].name;
                
                // Add visual feedback
                uploadArea.classList.add('border-primary');
                uploadArea.querySelector('.upload-icon i').classList.add('text-primary');
            }
        });
    }
    
    // Initialize charts on results page
    initializeCharts();
    
    // Add loading spinner to form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            }
        });
    });
    
    // Ticker search autocomplete
    // This would normally connect to a real API for stock symbols
    // For demonstration purposes, we'll just have a simple example
    const tickerInput = document.getElementById('ticker-input');
    if (tickerInput) {
        tickerInput.addEventListener('input', function() {
            // Real implementation would fetch suggestions from server
            console.log('Would fetch suggestions for:', this.value);
        });
    }
    
    // Show alert function for dynamic notifications
    function showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alert-container');
        if (!alertContainer) return;
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.role = 'alert';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        alertContainer.appendChild(alert);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    }
    
    // Initialize Plotly charts if they exist
    function initializeCharts() {
        console.log("Initializing charts...");
        
        // Time Series Chart
        const timeSeriesContainer = document.getElementById('time-series-chart');
        console.log("Time series container:", timeSeriesContainer);
        console.log("Time series data-analysis-id:", timeSeriesContainer ? timeSeriesContainer.dataset.analysisId : "not found");
        
        if (timeSeriesContainer && timeSeriesContainer.dataset.analysisId) {
            const analysisId = timeSeriesContainer.dataset.analysisId;
            console.log("Found analysis ID for time series chart:", analysisId);
            
            fetch(`/api/plots/${analysisId}/time_series`)
                .then(response => {
                    console.log("Time series response status:", response.status);
                    if (!response.ok) {
                        console.error("Error response:", response.status, response.statusText);
                        throw new Error(`HTTP error ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("Time series data received:", data);
                    Plotly.newPlot('time-series-chart', data.data, data.layout, {responsive: true});
                })
                .catch(error => {
                    console.error('Error loading time series chart:', error);
                    timeSeriesContainer.innerHTML = '<div class="alert alert-danger">Error loading chart data</div>';
                });
        }
        
        // Frequency Chart
        const frequencyContainer = document.getElementById('frequency-chart');
        if (frequencyContainer && frequencyContainer.dataset.analysisId) {
            const analysisId = frequencyContainer.dataset.analysisId;
            
            fetch(`/api/plots/${analysisId}/frequency`)
                .then(response => response.json())
                .then(data => {
                    Plotly.newPlot('frequency-chart', data.data, data.layout, {responsive: true});
                })
                .catch(error => {
                    console.error('Error loading frequency chart:', error);
                    frequencyContainer.innerHTML = '<div class="alert alert-danger">Error loading chart data</div>';
                });
        }
        
        // Forecast Chart
        const forecastContainer = document.getElementById('forecast-chart');
        if (forecastContainer && forecastContainer.dataset.analysisId) {
            const analysisId = forecastContainer.dataset.analysisId;
            
            fetch(`/api/plots/${analysisId}/forecast`)
                .then(response => response.json())
                .then(data => {
                    Plotly.newPlot('forecast-chart', data.data, data.layout, {responsive: true});
                })
                .catch(error => {
                    console.error('Error loading forecast chart:', error);
                    forecastContainer.innerHTML = '<div class="alert alert-danger">Error loading chart data</div>';
                });
        }
    }
    
    // Expose utility functions to global scope if needed
    window.showAlert = showAlert;
    window.initializeCharts = initializeCharts;
});

// Add smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if (!targetElement) return;
        
        window.scrollTo({
            top: targetElement.offsetTop - 80,
            behavior: 'smooth'
        });
    });
});
// dashboard.js - Handles the dashboard functionality

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const interviewCards = document.querySelectorAll('.interview-card');
    const statisticsCharts = document.getElementById('statistics-charts');
    const filterDropdown = document.getElementById('filter-dropdown');
    const interviewTypeFilter = document.getElementById('interview-type-filter');
    const dateFilter = document.getElementById('date-filter');
    const searchInput = document.getElementById('search-input');
    const exportButton = document.getElementById('export-data');
    
    // Initialize charts if they exist
    if (statisticsCharts) {
        initializeCharts();
    }
    
    // Initialize filters
    if (interviewTypeFilter) {
        interviewTypeFilter.addEventListener('change', filterInterviews);
    }
    
    if (dateFilter) {
        dateFilter.addEventListener('change', filterInterviews);
    }
    
    if (searchInput) {
        searchInput.addEventListener('input', filterInterviews);
    }
    
    // Handle interview card clicks
    interviewCards.forEach(card => {
        card.addEventListener('click', function() {
            const interviewId = this.getAttribute('data-id');
            if (interviewId) {
                window.location.href = `/interview/${interviewId}`;
            }
        });
    });
    
    // Export data functionality
    if (exportButton) {
        exportButton.addEventListener('click', function() {
            // In a real app, this would trigger a download
            alert('Exporting interview data...');
        });
    }
    
    // Filter interviews based on selected filters
    function filterInterviews() {
        const type = interviewTypeFilter ? interviewTypeFilter.value : 'all';
        const date = dateFilter ? dateFilter.value : 'all';
        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        
        interviewCards.forEach(card => {
            const cardType = card.getAttribute('data-type');
            const cardDate = card.getAttribute('data-date');
            const cardTitle = card.querySelector('.interview-title').textContent.toLowerCase();
            const cardContent = card.querySelector('.interview-description').textContent.toLowerCase();
            
            let showCard = true;
            
            // Filter by type
            if (type !== 'all' && cardType !== type) {
                showCard = false;
            }
            
            // Filter by date
            if (date !== 'all') {
                const today = new Date();
                const cardDateTime = new Date(cardDate);
                
                if (date === 'today') {
                    if (!isSameDay(today, cardDateTime)) {
                        showCard = false;
                    }
                } else if (date === 'week') {
                    const weekAgo = new Date(today);
                    weekAgo.setDate(today.getDate() - 7);
                    if (cardDateTime < weekAgo) {
                        showCard = false;
                    }
                } else if (date === 'month') {
                    const monthAgo = new Date(today);
                    monthAgo.setMonth(today.getMonth() - 1);
                    if (cardDateTime < monthAgo) {
                        showCard = false;
                    }
                }
            }
            
            // Filter by search term
            if (searchTerm && !cardTitle.includes(searchTerm) && !cardContent.includes(searchTerm)) {
                showCard = false;
            }
            
            // Show or hide the card
            if (showCard) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
        
        // Show empty state if no results
        const visibleCards = document.querySelectorAll('.interview-card[style=""]');
        const emptyState = document.querySelector('.empty-state');
        
        if (visibleCards.length === 0 && emptyState) {
            emptyState.style.display = 'block';
        } else if (emptyState) {
            emptyState.style.display = 'none';
        }
    }
    
    // Helper function to check if two dates are the same day
    function isSameDay(date1, date2) {
        return date1.getFullYear() === date2.getFullYear() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getDate() === date2.getDate();
    }
    
    // Initialize charts for the dashboard
    function initializeCharts() {
        // Mock data for charts
        const performanceData = {
            labels: ['Technical', 'Communication', 'Problem Solving', 'Cultural Fit', 'Leadership'],
            datasets: [{
                label: 'Your Score',
                data: [85, 70, 80, 90, 65],
                backgroundColor: 'rgba(59, 130, 246, 0.5)',
                borderColor: 'rgba(59, 130, 246, 1)',
                borderWidth: 1
            }, {
                label: 'Average Score',
                data: [75, 65, 70, 80, 60],
                backgroundColor: 'rgba(209, 213, 219, 0.5)',
                borderColor: 'rgba(209, 213, 219, 1)',
                borderWidth: 1
            }]
        };
        
        const progressData = {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Score Trend',
                data: [65, 68, 72, 75, 82, 85],
                fill: false,
                borderColor: 'rgba(59, 130, 246, 1)',
                tension: 0.1
            }]
        };
        
        // Create canvas elements
        const performanceCanvas = document.createElement('canvas');
        performanceCanvas.id = 'performance-chart';
        const progressCanvas = document.createElement('canvas');
        progressCanvas.id = 'progress-chart';
        
        // Add to container
        const performanceContainer = document.createElement('div');
        performanceContainer.classList.add('chart-container');
        performanceContainer.appendChild(document.createElement('h3')).textContent = 'Performance Breakdown';
        performanceContainer.appendChild(performanceCanvas);
        
        const progressContainer = document.createElement('div');
        progressContainer.classList.add('chart-container');
        progressContainer.appendChild(document.createElement('h3')).textContent = 'Progress Over Time';
        progressContainer.appendChild(progressCanvas);
        
        statisticsCharts.appendChild(performanceContainer);
        statisticsCharts.appendChild(progressContainer);
        
        // Note: In a real implementation, you would use a charting library 
        // like Chart.js to render these charts. Since we can't include external 
        // libraries in this demo, we'll just show placeholders.
        
        performanceCanvas.width = 400;
        performanceCanvas.height = 300;
        progressCanvas.width = 400;
        progressCanvas.height = 300;
        
        const perfCtx = performanceCanvas.getContext('2d');
        const progCtx = progressCanvas.getContext('2d');
        
        // Draw placeholder charts
        drawPlaceholderBarChart(perfCtx, performanceData);
        drawPlaceholderLineChart(progCtx, progressData);
    }
    
    // Draw a simple placeholder bar chart
    function drawPlaceholderBarChart(ctx, data) {
        const width = ctx.canvas.width;
        const height = ctx.canvas.height;
        const barCount = data.labels.length;
        const barWidth = (width - 100) / (barCount * 2);
        const maxValue = Math.max(...data.datasets[0].data, ...data.datasets[1].data);
        
        // Draw background
        ctx.fillStyle = '#f9fafb';
        ctx.fillRect(0, 0, width, height);
        
        // Draw title
        ctx.fillStyle = '#111827';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Performance Comparison', width / 2, 30);
        
        // Draw bars
        for (let i = 0; i < barCount; i++) {
            // First dataset
            const x1 = 50 + i * (barWidth * 2.5);
            const barHeight1 = (data.datasets[0].data[i] / maxValue) * (height - 100);
            const y1 = height - 50 - barHeight1;
            
            ctx.fillStyle = data.datasets[0].backgroundColor;
            ctx.fillRect(x1, y1, barWidth, barHeight1);
            
            ctx.strokeStyle = data.datasets[0].borderColor;
            ctx.strokeRect(x1, y1, barWidth, barHeight1);
            
            // Second dataset
            const x2 = x1 + barWidth * 1.2;
            const barHeight2 = (data.datasets[1].data[i] / maxValue) * (height - 100);
            const y2 = height - 50 - barHeight2;
            
            ctx.fillStyle = data.datasets[1].backgroundColor;
            ctx.fillRect(x2, y2, barWidth, barHeight2);
            
            ctx.strokeStyle = data.datasets[1].borderColor;
            ctx.strokeRect(x2, y2, barWidth, barHeight2);
            
            // Label
            ctx.fillStyle = '#4b5563';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(data.labels[i], x1 + barWidth * 1.1, height - 30);
        }
        
        // Draw legend
        ctx.fillStyle = data.datasets[0].backgroundColor;
        ctx.fillRect(width - 150, 20, 15, 15);
        ctx.strokeStyle = data.datasets[0].borderColor;
        ctx.strokeRect(width - 150, 20, 15, 15);
        ctx.fillStyle = '#111827';
        ctx.textAlign = 'left';
        ctx.fillText('Your Score', width - 130, 32);
        
        ctx.fillStyle = data.datasets[1].backgroundColor;
        ctx.fillRect(width - 150, 45, 15, 15);
        ctx.strokeStyle = data.datasets[1].borderColor;
        ctx.strokeRect(width - 150, 45, 15, 15);
        ctx.fillStyle = '#111827';
        ctx.fillText('Average', width - 130, 57);
    }
    
    // Draw a simple placeholder line chart
    function drawPlaceholderLineChart(ctx, data) {
        const width = ctx.canvas.width;
        const height = ctx.canvas.height;
        const pointCount = data.labels.length;
        const maxValue = Math.max(...data.datasets[0].data);
        
        // Draw background
        ctx.fillStyle = '#f9fafb';
        ctx.fillRect(0, 0, width, height);
        
        // Draw title
        ctx.fillStyle = '#111827';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Progress Over Time', width / 2, 30);
        
        // Draw grid lines
        ctx.strokeStyle = '#e5e7eb';
        ctx.beginPath();
        for (let i = 0; i <= 5; i++) {
            const y = 50 + i * (height - 100) / 5;
            ctx.moveTo(50, y);
            ctx.lineTo(width - 50, y);
        }
        ctx.stroke();
        
        // Draw line chart
        ctx.strokeStyle = data.datasets[0].borderColor;
        ctx.lineWidth = 2;
        ctx.beginPath();
        
        for (let i = 0; i < pointCount; i++) {
            const x = 50 + i * (width - 100) / (pointCount - 1);
            const y = height - 50 - (data.datasets[0].data[i] / maxValue) * (height - 100);
            
            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
            
            // Draw point
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(x, y, 5, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
        }
        
        ctx.stroke();
        
        // Draw x-axis labels
        ctx.fillStyle = '#4b5563';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        
        for (let i = 0; i < pointCount; i++) {
            const x = 50 + i * (width - 100) / (pointCount - 1);
            ctx.fillText(data.labels[i], x, height - 30);
        }
        
        // Draw y-axis labels
        ctx.textAlign = 'right';
        for (let i = 0; i <= 5; i++) {
            const y = height - 50 - i * (height - 100) / 5;
            ctx.fillText((maxValue * i / 5).toFixed(0), 45, y + 4);
        }
    }
});
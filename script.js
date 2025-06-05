// Initialize the map
const map = L.map('map').setView([51.505, -0.09], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Store markers for later reference
const markers = {};

// Function to fetch and display reports
function loadReports() {
    fetch('/api/reports')
        .then(response => response.json())
        .then(reports => {
            // Clear existing markers
            Object.values(markers).forEach(marker => map.removeLayer(marker));
            
            // Add new markers
            reports.forEach(report => {
                const marker = L.marker([report.latitude, report.longitude])
                    .addTo(map)
                    .bindPopup(`
                        <b>${report.location_name}</b><br>
                        Queue: ${report.queue_length} people<br>
                        Reported: ${new Date(report.report_time).toLocaleString()}<br>
                        Votes: ${report.votes}
                        <button onclick="voteForReport(${report.id})" class="vote-button">Vote Accurate</button>
                    `);
                
                markers[report.id] = marker;
            });
            
            // Update reports list
            updateReportsList(reports);
        });
}

// Function to update the reports list
function updateReportsList(reports) {
    const reportsList = document.getElementById('reports-list');
    reportsList.innerHTML = '';
    
    reports.forEach(report => {
        const reportElement = document.createElement('div');
        reportElement.className = 'report-item';
        reportElement.innerHTML = `
            <h3>${report.location_name}</h3>
            <p>Queue: ${report.queue_length} people</p>
            <p>Reported: ${new Date(report.report_time).toLocaleString()}</p>
            <p>Votes: ${report.votes}</p>
            <button onclick="voteForReport(${report.id})" class="vote-button">Vote Accurate</button>
        `;
        reportsList.appendChild(reportElement);
    });
}

// Function to handle voting
function voteForReport(reportId) {
    fetch(`/api/vote/${reportId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadReports(); // Refresh the reports
        }
    });
}

// Load reports when page loads
document.addEventListener('DOMContentLoaded', loadReports);

// Set up click event to get coordinates
map.on('click', function(e) {
    // This is just for demonstration - in a real app you might
    // want to use this to help users select locations
    console.log(`Latitude: ${e.latlng.lat}, Longitude: ${e.latlng.lng}`);
});
// static/script.js for logic static = "src" being defined in Flask app = Flask(__name__, static_folder="src")

const API_BASE = "http://127.0.0.1:8000/api";
        let primaryChart, secondaryChart, map, mapLayerGroup;

        const cityCoords = {
             'Saigon': [10.7769, 106.7009], 'Hanoi': [21.0285, 105.8542],
             'Bangkok': [13.7563, 100.5018], 'Singapore': [1.3521, 103.8198],
             'Jakarta': [-6.2088, 106.8456], 'Manila': [14.5995, 120.9842],
             'Beijing': [39.9042, 116.4074], 'Shanghai': [31.2304, 121.4737],
             'Kuala Lumpur': [3.1390, 101.6869], 'Perth': [-31.9505, 115.8605]
        };
        
        const cityColors = { 
            'Saigon': '#2563eb', 'Hanoi': '#dc2626', 'Jakarta': '#059669', 
            'Manila': '#d946ef', 'Perth': '#4b5563', 'Bangkok': '#d97706', 
            'Beijing': '#c2410c', 'Shanghai': '#7c3aed', 'Kuala Lumpur': '#0891b2', 
            'Singapore': '#db2777' 
        };


        function initMap() {
            if (map) return; 
            map = L.map('aqiMap').setView([15.0, 108.0], 5);
            L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; OpenStreetMap',
                crossOrigin: true  // ALLOWS CAPTURING TILES INTO PDF
            }).addTo(map);
            mapLayerGroup = L.layerGroup().addTo(map);
            
            setTimeout(() => { map.invalidateSize(); }, 400);
        }

        function updateTrendIndicators(historyData) {
            const cities = ['Saigon', 'Hanoi'];
            
            cities.forEach(city => {
                // Filter history for this city and sort by date descending
                const cityHistory = historyData
                    .filter(item => item.City === city)
                    .sort((a, b) => new Date(b.Date) - new Date(a.Date));

                if (cityHistory.length >= 2) {
                    const current = cityHistory[0].AQI;
                    const previous = cityHistory[1].AQI;
                    const diff = current - previous;
                    const trendElement = document.getElementById(`${city.toLowerCase()}-trend`);

                    if (diff > 0) {
                        // AQI went UP (Worse)
                        trendElement.innerHTML = `<span class="text-red-500">▲ +${diff}</span> <span class="text-slate-400 font-normal">vs yesterday</span>`;
                    } else if (diff < 0) {
                        // AQI went DOWN (Better)
                        trendElement.innerHTML = `<span class="text-emerald-500">▼ ${diff}</span> <span class="text-slate-400 font-normal">vs yesterday</span>`;
                    } else {
                        trendElement.innerHTML = `<span class="text-slate-400">▬ No change</span>`;
                    }
                }
            });
        }

        
        function getAqiTheme(aqi) {
            const goodMax = parseInt(document.getElementById('threshold-good').value) || 50;
            const moderateMax = parseInt(document.getElementById('threshold-moderate').value) || 100;

            if (aqi <= goodMax) {
                return { label: 'Healthy', color: '#10b981', tailwind: 'border-green-500', bg: 'bg-green-100', text: 'text-green-700' };
            } else if (aqi <= moderateMax) {
                return { label: 'Moderate', color: '#facc15', tailwind: 'border-yellow-400', bg: 'bg-yellow-100', text: 'text-yellow-700' };
            } else {
                return { label: 'Unhealthy', color: '#ef4444', tailwind: 'border-red-600', bg: 'bg-red-100', text: 'text-red-700' };
            }
        }

        async function triggerScrape() {
            const btn = document.getElementById('scrape-btn');
            
            btn.disabled = true;
            btn.innerHTML = `
                <svg class="animate-spin-custom h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Scraping Data...</span>
            `;

            try {
                const response = await fetch(`${API_BASE}/scrape`, { method: 'POST' });
                const result = await response.json();
                
                if (result.status === "success") {
                    showToast("New air quality data fetched successfully!"); // Replaces alert
                    await updateDashboard(); 
                } else {
                    showToast("Scrape failed: " + result.message, "error"); // Replaces alert
                }
            } catch (e) {
                showToast("Server connection failed.", "error"); // Replaces alert
            } finally {
                btn.disabled = false;
                btn.innerHTML = "<span>🔄</span> Run New API Scrape";
            }
        }
                
        async function updateDashboard() {
            // 1. FETCH CURRENT DATA (For Nodes and Header Time)
            try {
                const currResp = await fetch(`${API_BASE}/current`);
                const currJson = await currResp.json();
                const currentData = currJson.data;

                if (currentData.length > 0) {
                    // Update Scrape Time from air_quality.json
                    document.getElementById('last-scrape-time').innerText = currentData[0].Date || currentData[0].Time;
                    
                    ['Saigon', 'Hanoi'].forEach(city => {
                        const cityInfo = currentData.find(d => d.City === city);
                        if (cityInfo) {
                            const theme = getAqiTheme(cityInfo.AQI);
                            document.getElementById(`aqi-${city}`).innerText = Math.round(cityInfo.AQI);
                            document.getElementById(`pm25-${city}`).innerText = cityInfo.PM25 || '--';
                            document.getElementById(`pm10-${city}`).innerText = cityInfo.PM10 || '--';
                            document.getElementById(`label-${city}`).innerText = theme.label;
                            document.getElementById(`label-${city}`).className = `px-2 py-1 rounded text-[10px] font-black uppercase ${theme.bg} ${theme.text}`;
                            document.getElementById(`card-${city}`).className = `p-6 rounded-2xl bg-white shadow-sm border-l-8 ${theme.tailwind}`;
                        }
                    });
                }
            } catch (e) { console.error("Current data fetch error:", e); }

            // 2. FETCH HISTORICAL DATA (For Charts and Map)
            const type1 = document.getElementById('type-top').value;
            const type2 = document.getElementById('type-bottom').value;
            const selectedParams = Array.from(document.querySelectorAll('.param-toggle:checked')).map(p => p.value);
            const selectedCities = Array.from(document.querySelectorAll('.city-toggle:checked')).map(cb => cb.value);
            const citiesToChart = [...new Set(['Saigon', 'Hanoi', ...selectedCities])];
            
            mapLayerGroup.clearLayers();
            let labels = [], aqids = [], paramds = [], totalAqi = 0, cityCount = 0;
            let snapshotLabels = [], snapshotValues = [];

            for (const city of citiesToChart) {
                try {
                    const response = await fetch(`${API_BASE}/history/${city}`);
                    const json = await response.json();
                    const data = json.data.sort((a,b) => new Date(a.Date || a.Time) - new Date(b.Date || b.Time));
                    
                    if (data.length > 0) {
                        // ------------------------
                        updateTrendIndicators(data);
                        // ------------------------
                        const latest = data[data.length-1];
                        const theme = getAqiTheme(latest.AQI);
                        totalAqi += latest.AQI; cityCount++;

                        L.circle(cityCoords[city], { color: theme.color, fillColor: theme.color, fillOpacity: 0.5, radius: 50000 + (latest.AQI * 600) })
                         .bindTooltip(`<b>${city}</b>: ${latest.AQI} AQI`).addTo(mapLayerGroup);

                        if (labels.length === 0) labels = data.map(d => (d.Date || d.Time).split(' ')[0]);
                        
                        snapshotLabels.push(city);
                        snapshotValues.push(latest.AQI);

                        aqids.push({ 
                                label: city, 
                                data: data.map(d => d.AQI), 
                                borderColor: cityColors[city], // Keep city color for the line
                                pointBackgroundColor: data.map(d => getAQIColor(d.AQI)), // Color dots by AQI level
                                backgroundColor: cityColors[city] + '44', 
                                fill: type1 === 'area' 
                            });
                        
                        selectedParams.forEach(p => {
                            paramds.push({ 
                                label: `${city} ${p}`, data: data.map(d => d[p]), 
                                borderColor: cityColors[city], 
                                backgroundColor: cityColors[city] + (type2 === 'bar' ? 'e6' : '22'), 
                                fill: type2==='area'
                            });
                        });
                    }
                } catch (e) { console.warn(city + " history fetch error"); }
            }

            const avgVal = Math.round(totalAqi / cityCount);
            document.getElementById('avg-aqi').innerText = avgVal || '--';
            document.getElementById('avg-status').innerText = `REGIONAL STATUS: ${getAqiTheme(avgVal).label}`;
                        
            renderChart('primaryChart', 
                (type1.includes('pie') || type1 === 'bar' ? snapshotLabels : labels), 
                (type1.includes('pie') || type1 === 'bar' 
                    ? [{ 
                        data: snapshotValues, 
                        backgroundColor: snapshotValues.map(v => getAQIColor(v)), // Dynamic AQI Colors
                        borderColor: snapshotValues.map(v => getAQIColor(v)),
                        borderWidth: 1
                    }] 
                    : aqids), 
                type1, primaryChart, (c) => primaryChart = c);
            

            renderChart('secondaryChart', (type2.includes('pie') ? snapshotLabels : labels), 
                (type2.includes('pie') ? [{ data: snapshotValues, backgroundColor: snapshotLabels.map(c => cityColors[c]) }] : paramds), 
                type2, secondaryChart, (c) => secondaryChart = c);
        }

        function renderChart(id, labels, datasets, type, oldChart, setChart) {
            const ctx = document.getElementById(id).getContext('2d');
            if (oldChart) oldChart.destroy();
            const config = {
                type: (type === 'area' ? 'line' : type),
                data: { labels: labels, datasets: datasets },
                options: { 
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 10, weight: 'bold' } } } },
                    scales: (type.includes('pie') || type.includes('doughnut')) ? { x: { display: false }, y: { display: false } } : { 
                        y: { beginAtZero: true }, x: { ticks: { maxRotation: 45, minRotation: 45 } } 
                    }
                }
            };
            setChart(new Chart(ctx, config));
        }


        async function exportToPDF() {
            const { jsPDF } = window.jspdf;
            const mainContent = document.querySelector('main');
            const exportButton = event.currentTarget;

            exportButton.innerText = "⌛ Fitting to Page...";
            exportButton.disabled = true;

            if (map) map.invalidateSize();

            try {
                const canvas = await html2canvas(mainContent, {
                    scale: 2,
                    useCORS: true,
                    logging: false,
                    backgroundColor: "#ffffff",
                    windowWidth: 1200 // Consistent width for predictable layout
                });

                const imgData = canvas.toDataURL('image/png');
                const pdf = new jsPDF('p', 'mm', 'a4');
                
                const pageWidth = pdf.internal.pageSize.getWidth();
                const pageHeight = pdf.internal.pageSize.getHeight();
                const margin = 10;
                
                const targetWidth = pageWidth - (margin * 2);
                const targetHeight = pageHeight - (margin * 3); // Extra space for title

                // Calculate ratios
                const imgWidth = canvas.width;
                const imgHeight = canvas.height;
                const ratio = Math.min(targetWidth / imgWidth, targetHeight / imgHeight);

                // Final dimensions to fit one page
                const finalWidth = imgWidth * ratio;
                const finalHeight = imgHeight * ratio;

                // Center horizontally
                const xOffset = (pageWidth - finalWidth) / 2;

                // Add Report Title
                pdf.setFontSize(16);
                pdf.setTextColor(30, 41, 59);
                pdf.text("Air Quality Monitoring Report", pageWidth / 2, 12, { align: "center" });
                
                // Add the content
                pdf.addImage(imgData, 'PNG', xOffset, 18, finalWidth, finalHeight);
                
                pdf.save(`AQI_Report_SinglePage_${new Date().toISOString().split('T')[0]}.pdf`);
                
                showToast("Single-page report generated!");
            } catch (err) {
                console.error(err);
                showToast("Export failed", "error");
            } finally {
                exportButton.innerHTML = "📥 Export Report (PDF)";
                exportButton.disabled = false;
            }
        }   
        
        function showToast(message, type = 'success') {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            
            // Define colors based on type
            const bgColor = type === 'success' ? 'bg-emerald-600' : 'bg-red-600';
            const icon = type === 'success' ? '✅' : '❌';

            toast.className = `${bgColor} text-white px-6 py-4 rounded-xl shadow-2xl flex items-center gap-3 transform transition-all duration-300 translate-y-10 opacity-0 min-w-[300px]`;
            toast.innerHTML = `
                <span class="text-xl">${icon}</span>
                <div class="flex-1 font-medium">${message}</div>
                <button onclick="this.parentElement.remove()" class="ml-2 hover:opacity-70">✕</button>
            `;

            container.appendChild(toast);

            // Trigger animation
            setTimeout(() => {
                toast.classList.remove('translate-y-10', 'opacity-0');
            }, 10);

            // Auto-remove after 4 seconds
            setTimeout(() => {
                toast.classList.add('translate-y-10', 'opacity-0');
                setTimeout(() => toast.remove(), 300);
            }, 4000);
        }
// =========================================
// Robust deleteRecord and editRecord
        async function deleteRecord(id) {
            // Confirm with user
            if (!confirm(`Are you sure you want to delete record #${id}?`)) return;

            try {
                const response = await fetch(`${API_BASE}/history/${id}`, { 
                    method: 'DELETE' 
                });
                const result = await response.json();

                if (result.status === "success") {
                    showToast(`Record #${id} deleted!`);
                    loadManagementData(); // Refresh table
                    updateDashboard();    // Refresh charts
                } else {
                    showToast(result.message || "Delete failed", "error");
                }
            } catch (e) {
                console.error("Delete error:", e);
                showToast("Server error during deletion", "error");
            }
        }

// Multi-parameter Edit
// Function to open the modal and fill data
function editRecord(id, aqi, pm25, pm10) {
    document.getElementById('edit-id').value = id;
    document.getElementById('edit-aqi').value = aqi;
    document.getElementById('edit-pm25').value = pm25;
    document.getElementById('edit-pm10').value = pm10;
    document.getElementById('modal-subtitle').innerText = `Record #${id}`;
    
    document.getElementById('editModal').classList.remove('hidden');
}

function closeEditModal() {
    document.getElementById('editModal').classList.add('hidden');
}

// Function to handle the actual API update
        async function submitEdit() {
            const id = document.getElementById('edit-id').value;
            const aqi = document.getElementById('edit-aqi').value;
            const pm25 = document.getElementById('edit-pm25').value;
            const pm10 = document.getElementById('edit-pm10').value;

            try {
                const response = await fetch(`${API_BASE}/history/${id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        AQI: parseInt(aqi),
                        PM25: parseFloat(pm25),
                        PM10: parseFloat(pm10)
                    })
                });
                
                const result = await response.json();
                if (result.status === "success") {
                    showToast(`Record #${id} updated successfully!`);
                    closeEditModal();
                    loadManagementData(); // Refresh the table
                    updateDashboard();    // Refresh the charts
                } else {
                    showToast(result.message || "Update failed", "error");
                }
            } catch (e) {
                showToast("Server connection error", "error");
            }
        }

// FILTER FUNCTION
//Combined Search and Date-Range Filter
        function filterTable() {
            const searchText = document.getElementById("table-search").value.toUpperCase();
            const dateFrom = document.getElementById("date-from").value;
            const dateTo = document.getElementById("date-to").value;
            
            const rows = document.querySelectorAll("#management-table-body tr");

            rows.forEach(row => {
                const cityText = row.children[1].textContent.toUpperCase();
                const rowDate = row.getAttribute('data-date').split(' ')[0]; // Extract YYYY-MM-DD
                
                const matchesSearch = cityText.includes(searchText);
                let matchesDate = true;

                if (dateFrom && rowDate < dateFrom) matchesDate = false;
                if (dateTo && rowDate > dateTo) matchesDate = false;

                row.style.display = (matchesSearch && matchesDate) ? "" : "none";
            });
        }

        function updateThresholds() {
            const goodMax = parseInt(document.getElementById('threshold-good').value) || 50;
            const moderateMax = parseInt(document.getElementById('threshold-moderate').value) || 100;

            // Validate inputs to ensure Moderate is higher than Good
            if (moderateMax <= goodMax) {
                showToast("Moderate threshold must be higher than Good.", "error");
                return;
            }

            // Update the Sidebar Guide Text
            document.getElementById('range-good').innerText = `0 - ${goodMax}`;
            document.getElementById('range-moderate').innerText = `${goodMax + 1} - ${moderateMax}`;
            document.getElementById('range-unhealthy').innerText = `${moderateMax + 1}+`;

            // Refresh the dashboard (Cards & Map)
            updateDashboard(); 
            showToast("Thresholds applied to dashboard");
        }

        function resetThresholds() {
            // 1. Set input values back to standard defaults
            document.getElementById('threshold-good').value = 50;
            document.getElementById('threshold-moderate').value = 100;

            // 2. Run the update function to refresh the UI
            updateThresholds();
            showToast("Thresholds reset to standard defaults");
        }     

        function clearFilters() {
            document.getElementById("table-search").value = "";
            document.getElementById("date-from").value = "";
            document.getElementById("date-to").value = "";
            filterTable(); // Refresh the view to show all rows
            showToast("Filters cleared");
        }

// the AQI Color Helper Function
        function getAQIColor(value) {
            if (value <= 50) return '#00e400'; // Good (Green)
            if (value <= 100) return '#ffff00'; // Moderate (Yellow)
            if (value <= 150) return '#ff7e00'; // Unhealthy for Sensitive Groups (Orange)
            if (value <= 200) return '#ff0000'; // Unhealthy (Red)
            if (value <= 300) return '#8f3f97'; // Very Unhealthy (Purple)
            return '#7e0023'; // Hazardous (Maroon)
        }

// Load Function for Table
        async function loadManagementData() {
            try {
                const response = await fetch(`${API_BASE}/history`);
                const json = await response.json();
                const tbody = document.getElementById('management-table-body');
                tbody.innerHTML = ''; 

                const actualData = Array.isArray(json) ? json : (json.data || []);
                // Sort by date descending
                const displayData = [...actualData].sort((a,b) => new Date(b.Date || b.Time) - new Date(a.Date || a.Time));

                displayData.forEach(record => {
                    const row = document.createElement('tr');
                    row.className = "border-b border-slate-50 hover:bg-slate-50 transition-colors text-sm";
                    row.setAttribute('data-date', record.Date || record.Time); // Store date for filtering
                    
                    // Inside loadManagementData function
                    const recId = Number(record.id);
                    const aqi = Number(record.AQI || 0);
                    const pm25 = Number(record.PM25 || 0); // Ensure these are numbers
                    const pm10 = Number(record.PM10 || 0);

                    row.innerHTML = `
                        <td class="p-2 text-xs font-mono text-slate-400">#${recId}</td>
                        <td class="p-2 font-semibold text-slate-700">${record.City || 'N/A'}</td>
                        <td class="p-2 text-xs text-slate-500">${record.Date || record.Time || 'N/A'}</td>
                        <td class="p-2 font-bold text-blue-600">${aqi}</td>
                        <td class="p-2 font-bold text-blue-600">${pm25}</td>
                        <td class="p-2 font-bold text-blue-600">${pm10}</td>
                        <td class="p-2 text-right space-x-1">
                            <button onclick="editRecord(${recId}, ${aqi}, ${pm25}, ${pm10})" class="hover:bg-blue-50 p-1 rounded-lg text-blue-500">✏️</button>
                            <button onclick="deleteRecord(${recId})" class="hover:bg-red-50 p-1 rounded-lg text-red-500">🗑️</button>
                        </td>
                    `;
                                                            
                    tbody.appendChild(row);
                });
                showToast("Table data refreshed");
            } catch (e) {
                showToast("Error loading table records", "error");
            }
        }

// Call this inside your window.onload so it loads initially
        window.onload = () => { initMap(); updateDashboard(); loadManagementData(); };
/**
 * CycloneShield AI - Chart.js Controllers
 */

class ChartController {
    static initRadarChart(canvasId, hazardData) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        // Destroy existing chart instance if attached
        if (window.hazardRadarChart) {
            window.hazardRadarChart.destroy();
        }

        const data = {
            labels: [
                'Wind Load',
                'Rainfall Inundation',
                'Storm Surge',
                'Infra Exposure',
                'Topographic Vulnerability'
            ],
            datasets: [{
                label: 'Hazard Index (0-100)',
                data: [
                    hazardData?.wind_hazard_score || 90.0,
                    hazardData?.rainfall_hazard_score || 82.0,
                    hazardData?.surge_hazard_score || 88.0,
                    hazardData?.infrastructure_exposure_score || 85.0,
                    80.0 // Elevation vulnerability
                ],
                fill: true,
                backgroundColor: 'rgba(239, 68, 68, 0.25)',
                borderColor: '#ef4444',
                pointBackgroundColor: '#ef4444',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#ef4444'
            }]
        };

        const config = {
            type: 'radar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    r: {
                        angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        pointLabels: {
                            color: '#94a3b8',
                            font: { size: 11, family: 'Inter' }
                        },
                        ticks: {
                            backdropColor: 'transparent',
                            color: '#64748b',
                            stepSize: 20
                        },
                        min: 0,
                        max: 100
                    }
                }
            }
        };

        window.hazardRadarChart = new Chart(ctx, config);
        return window.hazardRadarChart;
    }

    static initComparisonChart(canvasId, baselineScore, simScore) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        if (window.simComparisonChart) {
            window.simComparisonChart.destroy();
        }

        const config = {
            type: 'bar',
            data: {
                labels: ['Baseline Risk', 'Simulated Risk'],
                datasets: [{
                    label: 'Vulnerability Risk Score',
                    data: [baselineScore, simScore],
                    backgroundColor: [
                        'rgba(245, 158, 11, 0.7)',
                        'rgba(239, 68, 68, 0.85)'
                    ],
                    borderColor: [
                        '#f59e0b',
                        '#ef4444'
                    ],
                    borderWidth: 1.5,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: 'rgba(255, 255, 255, 0.08)' },
                        ticks: { color: '#94a3b8' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#e2e8f0', font: { weight: 'bold' } }
                    }
                }
            }
        };

        window.simComparisonChart = new Chart(ctx, config);
        return window.simComparisonChart;
    }
}

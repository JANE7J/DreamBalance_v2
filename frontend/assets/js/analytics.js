// --- Core Application Logic for the Analytics Page ---
const API_URL = "http://127.0.0.1:5001";
let authHeader = {}; // Will be set on load

document.addEventListener('DOMContentLoaded', () => {
    // --- Authentication Check ---
    const token = localStorage.getItem('authToken');
    if (!token) {
        window.location.href = 'index.html'; // Redirect to login if not authenticated
        return; // Stop further execution
    }
    authHeader = { 'Authorization': `Bearer ${token}` };

    // --- Initial Setup ---
    fetchAnalyticsData();
    initializeUserProfile();
});

async function fetchAnalyticsData() {
    try {
        const response = await fetch(`${API_URL}/api/analytics`, { headers: authHeader });
        if (response.status === 401) { logout(); } // Token expired or invalid
        if (!response.ok) throw new Error('Failed to fetch analytics');
        
        const data = await response.json();
        renderSustainabilityChart(data.mental_sustainability_index);
renderStateChart(data.state_distribution);
renderStateLegend(data.state_distribution);


if (data.ai_agent && data.ai_agent.ai_insight) {
    console.log("AI Insight received:", data.ai_agent.ai_insight);

    renderEmotionChart(
        data.ai_agent.week_summary?.emotion_summary || {}
    );

    renderAIInsight(data.ai_agent.ai_insight);
} else {
    document.getElementById('ai-reasoning').textContent =
        "Not enough dream data this week to generate AI insight.";
}



        // Assuming other chart functions exist
        // renderEmotionChart(data.emotion_frequency);
        // renderConsistencyChart(data.sleep_consistency);
        
    } catch (error) {
        console.error("Error fetching analytics data:", error);
    }
}

// --- User Profile & Auth ---
function initializeUserProfile() {
    const username = localStorage.getItem('userName');
    if (username) {
        document.getElementById('user-name').textContent = username;
        document.getElementById('user-initial').textContent = username.charAt(0).toUpperCase();
    } else {
        logout(); // If no username, something is wrong, force logout.
    }
}

function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userName');
    window.location.href = 'index.html';
}

// --- Chart Rendering Functions ---
// (Assume chart rendering functions are here as before)
function renderSustainabilityChart(index) {
    const ctx = document.getElementById('sustainability-chart').getContext('2d');
    document.getElementById('sustainability-index').innerHTML = `<span class="text-4xl">${index}</span><span>INDEX</span>`;
    new Chart(ctx, { /* ... chart config ... */ });
}
function renderStateChart(distribution) {
    const ctx = document.getElementById('state-chart').getContext('2d');

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(distribution),
            datasets: [{
                data: Object.values(distribution),
                backgroundColor: ['#22c55e', '#ef4444']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: {
                        color: '#e5e7eb'
                    }
                }
            }
        }
    });
}


function renderEmotionChart(emotionSummary) {
    const ctx = document.getElementById('emotion-chart').getContext('2d');

    const labels = Object.keys(emotionSummary);
    const values = Object.values(emotionSummary);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Emotion Frequency',
                data: values,
                backgroundColor: '#6366f1'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#9ca3af' }
                },
                x: {
                    ticks: { color: '#9ca3af' }
                }
            }
        }
    });
}
function renderStateLegend(distribution) {
    const legend = document.getElementById('state-legend');
    legend.innerHTML = '';

    for (const [state, value] of Object.entries(distribution)) {
        legend.innerHTML += `
            <div class="flex justify-between text-sm">
                <span>${state}</span>
                <span class="text-indigo-400">${value}%</span>
            </div>
        `;
    }
}

function renderAIInsight(aiInsight) {
    const reasoningEl = document.getElementById('ai-reasoning');
    const recommendationsEl = document.getElementById('ai-recommendations');

    if (!aiInsight || !aiInsight.reasoning) {
        reasoningEl.textContent =
            "AI needs more dream entries to generate insights.";
        return;
    }

    reasoningEl.textContent = aiInsight.reasoning;

    recommendationsEl.innerHTML = '';

    if (Array.isArray(aiInsight.recommendations)) {
        aiInsight.recommendations.forEach(rec => {
            const li = document.createElement('li');
            li.textContent = rec;
            recommendationsEl.appendChild(li);
        });
    }
}




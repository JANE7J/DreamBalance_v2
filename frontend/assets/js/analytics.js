// --- Core Application Logic for the Analytics Page ---
const API_URL = "https://dreambalance-backend.onrender.com";
let authHeader = {};

document.addEventListener("DOMContentLoaded", () => {
    // --- Authentication Check ---
    const token = localStorage.getItem("authToken");
    if (!token) {
        window.location.href = "index.html";
        return;
    }

    authHeader = { Authorization: `Bearer ${token}` };

    initializeUserProfile();
    fetchAnalyticsData();
});

// ---------------- FETCH ANALYTICS ----------------

async function fetchAnalyticsData() {
    try {
        const response = await fetch(`${API_URL}/api/analytics`, {
            headers: authHeader
        });

        if (response.status === 401) {
            logout();
            return;
        }

        const text = await response.text();
        let data;

        try {
            data = JSON.parse(text);
        } catch {
            throw new Error("Invalid JSON from server");
        }

        if (!response.ok) {
            throw new Error(data.error || "Failed to fetch analytics");
        }

        // ---------------- RENDER ALL ANALYTICS ----------------
        renderSustainabilityChart(data.mental_index);

        // Calm vs Stress (RIGHT DONUT)
        renderStateChart(data.calm_stress_distribution);
        renderStateLegend(data.calm_stress_distribution);

        // Emotion frequency (BAR)
        renderEmotionChart(data.emotion_frequency);

        // AI Insight
        renderAIInsight(data.ai_insight);

    } catch (error) {
        console.error("Analytics error:", error);
        document.getElementById("ai-reasoning").textContent =
            "Unable to load analytics at the moment.";
    }
}

// ---------------- USER PROFILE ----------------

function initializeUserProfile() {
    const username = localStorage.getItem("userName");
    if (!username) {
        logout();
        return;
    }

    document.getElementById("user-name").textContent = username;
    document.getElementById("user-initial").textContent =
        username.charAt(0).toUpperCase();
}

function logout() {
    localStorage.removeItem("authToken");
    localStorage.removeItem("userName");
    window.location.href = "index.html";
}

// ---------------- CHARTS ----------------

function renderSustainabilityChart(index = 0) {
    const ctx = document
        .getElementById("sustainability-chart")
        .getContext("2d");

    document.getElementById("sustainability-index").innerHTML = `
        <span class="text-4xl">${index}</span>
        <span class="text-xs text-gray-400">INDEX</span>
    `;

    new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Progress", "Remaining"],
            datasets: [{
                data: [index, 100 - index],
                backgroundColor: ["#6366f1", "#2a2a35"],
                borderWidth: 0
            }]
        },
        options: {
            cutout: "80%",
            responsive: true,
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// Calm vs Stress donut
function renderStateChart(distribution = {}) {
    const ctx = document.getElementById("state-chart").getContext("2d");

    const labels = Object.keys(distribution);
    const values = Object.values(distribution);

    if (!labels.length) return;

    new Chart(ctx, {
        type: "doughnut",
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: ["#22c55e", "#ef4444"],
                borderWidth: 2,
                borderColor: "#0f0f17"
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: "#e5e7eb" }
                }
            }
        }
    });
}

// Emotion Frequency bar chart
function renderEmotionChart(emotionSummary = {}) {
    const ctx = document.getElementById("emotion-chart").getContext("2d");

    const labels = Object.keys(emotionSummary);
    const values = Object.values(emotionSummary);

    if (!labels.length) return;

    new Chart(ctx, {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label: "Emotion Frequency",
                data: values,
                backgroundColor: "#6366f1"
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: "#9ca3af" }
                },
                x: {
                    ticks: { color: "#9ca3af" }
                }
            }
        }
    });
}

// Legend for Calm / Stress
function renderStateLegend(distribution = {}) {
    const legend = document.getElementById("state-legend");
    legend.innerHTML = "";

    for (const [state, value] of Object.entries(distribution)) {
        legend.innerHTML += `
            <div class="flex justify-between text-sm">
                <span>${state}</span>
                <span class="text-indigo-400">${value}%</span>
            </div>
        `;
    }
}

// ---------------- AI INSIGHT ----------------

function renderAIInsight(aiInsight) {
    const reasoningEl = document.getElementById("ai-reasoning");
    const recommendationsEl = document.getElementById("ai-recommendations");

    if (!aiInsight || !aiInsight.reasoning) {
        reasoningEl.textContent =
            "Not enough dream data to generate insights.";
        return;
    }

    reasoningEl.textContent = aiInsight.reasoning;
    recommendationsEl.innerHTML = "";

    if (Array.isArray(aiInsight.recommendations)) {
        aiInsight.recommendations.forEach(rec => {
            const li = document.createElement("li");
            li.textContent = rec;
            recommendationsEl.appendChild(li);
        });
    }
}

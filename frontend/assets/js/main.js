// --- Core Application Logic for the Calendar / Journal Page ---
const API_URL = "https://dreambalance-backend.onrender.com";

let currentDate = new Date();
let monthlyEntries = {};
let selectedDateStr = new Date().toISOString().split("T")[0];
let authHeader = {};
let selectedMood = null;
let editingEntryId = null;

// ---------------- INIT ----------------

document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("authToken");
    if (!token) {
        window.location.href = "index.html";
        return;
    }

    authHeader = { Authorization: `Bearer ${token}` };

    setupEventListeners();
    initializeUserProfile();
    renderCalendar();
});

// ---------------- EVENT LISTENERS ----------------

function setupEventListeners() {
    document.getElementById("prev-month-btn")
        ?.addEventListener("click", () => changeMonth(-1));

    document.getElementById("next-month-btn")
        ?.addEventListener("click", () => changeMonth(1));
}

// ---------------- CALENDAR ----------------

function changeMonth(direction) {
    currentDate.setMonth(currentDate.getMonth() + direction);
    renderCalendar();
}

async function renderCalendar() {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    document.getElementById("month-year-header").textContent =
        `${currentDate.toLocaleString("default", { month: "long" })} ${year}`;

    await fetchMonthlyData(year, month + 1);

    const calendarGrid = document.getElementById("calendar-grid");
    calendarGrid.innerHTML = "";

    ["SUN","MON","TUE","WED","THU","FRI","SAT"].forEach(d =>
        calendarGrid.innerHTML += `<div class="text-xs text-gray-400 font-bold">${d}</div>`
    );

    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    for (let i = 0; i < firstDay; i++) {
        calendarGrid.appendChild(document.createElement("div"));
    }

    for (let day = 1; day <= daysInMonth; day++) {
        const dayEl = document.createElement("div");
        dayEl.textContent = day;
        dayEl.className = "day";

        const cellDate = new Date(year, month, day);
        if (cellDate <= new Date()) {
            dayEl.addEventListener("click", () => selectDate(day, month, year));
        } else {
            dayEl.classList.add("disabled");
        }

        const dateStr = `${year}-${String(month + 1).padStart(2,"0")}-${String(day).padStart(2,"0")}`;
        if (monthlyEntries[dateStr]) {
            dayEl.innerHTML += `
                <div class="absolute bottom-1.5 h-1.5 w-1.5 rounded-full
                ${getEmotionColor(monthlyEntries[dateStr][0].dominant_emotion)}"></div>`;
        }

        calendarGrid.appendChild(dayEl);
    }

    const d = new Date(selectedDateStr);
    selectDate(d.getDate(), d.getMonth(), d.getFullYear());
}

async function fetchMonthlyData(year, month) {
    const res = await fetch(
        `${API_URL}/api/entries/calendar?year=${year}&month=${month}`,
        { headers: authHeader }
    );

    if (res.status === 401) {
        logout();
        return;
    }

    const entries = await res.json();
    monthlyEntries = {};

    entries.forEach(e => {
        if (!monthlyEntries[e.entry_date]) monthlyEntries[e.entry_date] = [];
        monthlyEntries[e.entry_date].push(e);
    });
}

function selectDate(day, month, year) {
    selectedDateStr = `${year}-${String(month + 1).padStart(2,"0")}-${String(day).padStart(2,"0")}`;

    document.getElementById("selected-date-header").textContent =
        new Date(year, month, day).toLocaleDateString("en-US", { month: "long", day: "numeric" });

    const list = document.getElementById("daily-entries-list");
    list.innerHTML = "";

    if (!monthlyEntries[selectedDateStr]) {
        list.innerHTML = `<p class="text-gray-400 text-center pt-16">No entries for this date.</p>`;
        return;
    }

    monthlyEntries[selectedDateStr].forEach(entry => {
        list.innerHTML += `
            <div class="p-4 rounded-lg bg-black/20 hover:bg-white/10 cursor-pointer"
                 onclick="openEditEntry(${entry.id})">
                <p class="font-bold">Dream Entry</p>
                <p class="text-sm text-gray-400">${entry.feeling_after_waking}</p>
                <p class="text-xs text-gray-500 mt-1 line-clamp-2">
                    ${entry.dream_text || "No description"}
                </p>
            </div>`;
    });
}

// ---------------- EDIT ENTRY ----------------

function openEditEntry(entryId) {
    const entry = monthlyEntries[selectedDateStr]?.find(e => e.id === entryId);
    if (!entry) return;

    editingEntryId = entry.id;

    document.getElementById("dream-title").value = "";
    document.getElementById("dream-desc").value = entry.dream_text || "";

    selectedMood = entry.feeling_after_waking;

    document.querySelectorAll(".mood-btn").forEach(btn =>
        btn.classList.toggle("active", btn.textContent === selectedMood)
    );

    document.getElementById("save-btn").textContent = "Update Dream";
    document.getElementById("delete-btn").classList.remove("hidden");

    document.getElementById("new-entry-modal").classList.remove("hidden");
}

// ---------------- SAVE / UPDATE ----------------

async function saveNewEntry() {
    if (!selectedMood) {
        alert("Please select how you felt after waking up.");
        return;
    }

    const payload = {
        description: document.getElementById("dream-desc").value.trim(),
        mood: selectedMood
    };

    const isEdit = editingEntryId !== null;
    const url = isEdit
        ? `${API_URL}/api/entries/${editingEntryId}`
        : `${API_URL}/api/entries`;

    if (!isEdit) payload.entry_date = selectedDateStr;

    const res = await fetch(url, {
        method: isEdit ? "PUT" : "POST",
        headers: { ...authHeader, "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    if (!res.ok) {
        alert("Save failed");
        return;
    }

    closeNewEntryModal();
    renderCalendar();
}

// ---------------- DELETE ----------------

async function deleteEntry() {
    if (!editingEntryId) return;

    if (!confirm("Delete this dream?")) return;

    await fetch(`${API_URL}/api/entries/${editingEntryId}`, {
        method: "DELETE",
        headers: authHeader
    });

    closeNewEntryModal();
    renderCalendar();
}

// ---------------- UI HELPERS ----------------

function openNewEntryModal() {
    editingEntryId = null;
    selectedMood = null;

    document.getElementById("dream-title").value = "";
    document.getElementById("dream-desc").value = "";

    document.querySelectorAll(".mood-btn").forEach(b => b.classList.remove("active"));
    document.getElementById("save-btn").textContent = "Save Dream";
    document.getElementById("delete-btn").classList.add("hidden");

    document.getElementById("new-entry-modal").classList.remove("hidden");
}

function closeNewEntryModal() {
    document.getElementById("new-entry-modal").classList.add("hidden");
}

function setMood(button, mood) {
    document.querySelectorAll(".mood-btn").forEach(b => b.classList.remove("active"));
    button.classList.add("active");
    selectedMood = mood;
}

function getEmotionColor(emotion) {
    return {
        Happy: "bg-yellow-400",
        Peaceful: "bg-teal-400",
        Energized: "bg-green-400",
        Sad: "bg-blue-400",
        Anxious: "bg-purple-400",
        Scared: "bg-red-400",
        Confused: "bg-gray-400"
    }[emotion] || "bg-white";
}

// ---------------- AUTH ----------------

function initializeUserProfile() {
    const name = localStorage.getItem("userName") || "User";
    document.getElementById("user-name").textContent = name;
    document.getElementById("user-initial").textContent = name[0].toUpperCase();
}

function logout() {
    localStorage.clear();
    window.location.href = "index.html";
}

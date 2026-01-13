const API_URL = "https://dreambalance-backend.onrender.com";

// ---------------- TOGGLE FORMS ----------------
function toggleForms() {
    document.getElementById("login-form").classList.toggle("hidden");
    document.getElementById("register-form").classList.toggle("hidden");
    document.getElementById("login-error").classList.add("hidden");
    document.getElementById("register-error").classList.add("hidden");
}

// ---------------- REGISTER ----------------
async function registerUser(event) {
    event.preventDefault();

    const username = document.getElementById("register-username").value.trim();
    const email = document.getElementById("register-email").value.trim();
    const password = document.getElementById("register-password").value.trim();
    const gender = document.getElementById("register-gender").value;

    const errorEl = document.getElementById("register-error");
    errorEl.classList.add("hidden");

    try {
        const response = await fetch(`${API_URL}/api/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password, gender })
        });

        const contentType = response.headers.get("content-type");

        // 🔥 IMPORTANT FIX
        if (!contentType || !contentType.includes("application/json")) {
            throw new Error("Server is waking up. Please wait 5 seconds and try again.");
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Registration failed");
        }

        localStorage.setItem("authToken", data.token);
        localStorage.setItem("userName", data.username);

        window.location.href = "calendar.html";

    } catch (error) {
        errorEl.textContent = error.message;
        errorEl.classList.remove("hidden");
    }
}

// ---------------- LOGIN ----------------
async function loginUser(event) {
    event.preventDefault();

    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value.trim();

    const errorEl = document.getElementById("login-error");
    errorEl.classList.add("hidden");

    try {
        const response = await fetch(`${API_URL}/api/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const contentType = response.headers.get("content-type");

        // 🔥 IMPORTANT FIX
        if (!contentType || !contentType.includes("application/json")) {
            throw new Error("Server is waking up. Please wait 5 seconds and try again.");
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Login failed");
        }

        if (!data.token || !data.username) {
            throw new Error("Invalid server response");
        }

        localStorage.setItem("authToken", data.token);
        localStorage.setItem("userName", data.username);

        window.location.href = "calendar.html";

    } catch (error) {
        errorEl.textContent = error.message;
        errorEl.classList.remove("hidden");
    }
}

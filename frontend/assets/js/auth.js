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

        const text = await response.text(); // 👈 SAFE
        let data;

        try {
            data = JSON.parse(text);
        } catch {
            throw new Error("Server returned invalid response");
        }

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

        const text = await response.text(); // 👈 SAFE
        let data;

        try {
            data = JSON.parse(text);
        } catch {
            throw new Error("Server returned invalid response");
        }

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
        console.error(error);
        errorEl.textContent = error.message;
        errorEl.classList.remove("hidden");
    }
}


        if (!data.token || !data.username) {
            throw new Error("Invalid server response");
        }

        localStorage.setItem("authToken", data.token);
        localStorage.setItem("userName", data.username);

        window.location.href = "calendar.html";

    } catch (error) {
        console.error(error);
        errorEl.textContent = error.message;
        errorEl.classList.remove("hidden");
    }
}

const email = document.getElementById("email");
const password = document.getElementById("password");
const cnfrmPassword = document.getElementById("cnfrmPassword");
const firstname = document.getElementById("firstName");
const lastname = document.getElementById("lastName");
const registerForm = document.getElementById("register");
const alertBox = document.getElementById("registerAlert");
const registrationCode = document.getElementById("registrationCode");


function showError(message) {
    alertBox.textContent = message;
    alertBox.className = "alert error";
}


function showSuccess(message) {
    alertBox.textContent = message;
    alertBox.className = "alert success";
}


async function Register(e) {
    e.preventDefault();

    await ensureFrontendConfig();

    alertBox.textContent = "";
    alertBox.className = "alert";

    if (password.value !== cnfrmPassword.value) {
        showError("Passwords do not match.");
        return;
    }

    const credentials = {
        university_email: email.value.trim(),
        password: password.value,
        first_name: firstname.value.trim(),
        last_name: lastname.value.trim(),
        registration_code: registrationCode.value.trim()
    };

    try {
        const response = await fetch(
            `${API_URL}/register`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                credentials: "include",

                body: JSON.stringify(credentials)
            }
        );

        const data = await response.json();

        if (!response.ok) {
            console.error(data);

            let message = "Registration failed.";

            if (typeof data.detail === "string") {
                message = data.detail;
            } else if (Array.isArray(data.detail)) {
                message = data.detail
                    .map(error => error.msg)
                    .join(", ");
            }

            showError(message);
            return;
        }

        showSuccess("Registered successfully.");

        window.location.href = "/frontend/complete_profile.html";

    } catch (error) {
        console.error(error);

        showError("Could not connect to the server.");
    }
}


registerForm.addEventListener("submit", Register);

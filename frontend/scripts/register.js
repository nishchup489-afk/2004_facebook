const email = document.getElementById("email");
const password = document.getElementById("password");
const cnfrmPassword = document.getElementById("cnfrmPassword");
const university = document.getElementById("university");
const firstname = document.getElementById("firstName");
const lastname = document.getElementById("lastName");
const registerForm = document.getElementById("register");
const alertBox = document.getElementById("registerAlert");


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

    alertBox.textContent = "";
    alertBox.className = "alert";

    if (password.value !== cnfrmPassword.value) {
        showError("Passwords do not match.");
        return;
    }

    const credentials = {
        email: email.value.trim(),
        password: password.value,
        cnfrmPassword: cnfrmPassword.value,
        university: university.value.trim(),
        firstname: firstname.value.trim(),
        lastname: lastname.value.trim()
    };

    try {
        const response = await fetch("http://127.0.0.1:8000/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(credentials)
        });

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

        console.log("Registered successfully");

        showSuccess("Registered successfully.");

    } catch (error) {
        console.error(error);

        showError("Could not connect to the server.");
    }
}


registerForm.addEventListener("submit", Register);
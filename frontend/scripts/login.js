const loginForm = document.getElementById("loginForm");
const email = document.getElementById("email");
const password = document.getElementById("password");
const registerButtons = document.querySelectorAll(".registerButton");
const loginButtonAtBottom = document.querySelectorAll(".loginButton")


registerButtons.forEach((button) => {
    button.addEventListener("click", () => {
        window.location.href = "/register.html";
    });
});


loginButtonAtBottom.forEach((button) => {
    button.addEventListener("click" , () => {
        window.location.href = "/#loginForm";
    })
})

async function logIn(e) {
    e.preventDefault();

    await ensureFrontendConfig();

    const credentials = {
        university_email: email.value.trim(),
        password: password.value
    };

    try {
        const response = await fetch(
            `${API_URL}/login`,
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
            return;
        }

        console.log("Logged in:", data);

        window.location.href = "/home.html";

    } catch (error) {
        console.error(error);
    }
}


loginForm.addEventListener("submit", logIn);

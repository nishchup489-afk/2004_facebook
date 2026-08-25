const loginForm = document.getElementById("loginForm");
const email = document.getElementById("email");
const password = document.getElementById("password");
const registerButtons = document.querySelectorAll(".registerButton");
const loginButtonAtBottom = document.querySelectorAll(".loginButton")


registerButtons.forEach((button) => {
    button.addEventListener("click", () => {
        window.location.href = "/frontend/register.html";
    });
});


loginButtonAtBottom.forEach((button) => {
    button.addEventListener("click" , () => {
        window.location.href = "/frontend/index.html#loginForm";
    })
})

async function logIn(e) {
    e.preventDefault();

    const credentials = {
        university_email: email.value.trim(),
        password: password.value
    };

    try {
        const response = await fetch(
            "http://127.0.0.1:8000/login",
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

        window.location.href = "/frontend/home.html";

    } catch (error) {
        console.error(error);
    }
}


loginForm.addEventListener("submit", logIn);
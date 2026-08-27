const university = document.getElementById("universities");
const first_name = document.getElementById("first_name");
const last_name = document.getElementById("last_name");
const university_form = document.getElementById("university_form");
const alertBox = document.getElementById("alert");


function showError(message) {
    alertBox.textContent = message;
    alertBox.className = "alert error";
}


function showSuccess(message) {
    alertBox.textContent = message;
    alertBox.className = "alert success";
}


async function admitToUniversity(e) {
    e.preventDefault();

    await ensureFrontendConfig();

    alertBox.textContent = "";
    alertBox.className = "alert";


    if (!university.value) {
        showError("Please select a university.");
        return;
    }


    if (!first_name.value.trim()) {
        showError("Please enter your first name.");
        return;
    }


    if (!last_name.value.trim()) {
        showError("Please enter your last name.");
        return;
    }


    const credentials = {
        university: university.value,
        first_name: first_name.value.trim(),
        last_name: last_name.value.trim()
    };


    try {
        const response = await fetch(
            `${API_URL}/university`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(credentials)
            }
        );


        const data = await response.json();


        if (!response.ok) {
            console.error(data);

            let message = "University admission failed.";

            if (typeof data.detail === "string") {
                message = data.detail;
            }

            else if (Array.isArray(data.detail)) {
                message = data.detail
                    .map(error => error.msg)
                    .join(", ");
            }

            showError(message);
            return;
        }


        showSuccess("University admission successful.");

        sessionStorage.setItem(
            "universityAdmission",
            JSON.stringify(data)
        );

        window.location.href =
            `/frontend/university_portfolio.html?student_id=${data.student_id}`;


    }

    catch (error) {
        console.error(error);

        showError("Could not connect to the server.");
    }
}


university_form.addEventListener(
    "submit",
    admitToUniversity
);

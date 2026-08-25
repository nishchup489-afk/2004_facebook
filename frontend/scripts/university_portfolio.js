const params = new URLSearchParams(
    window.location.search
);

const studentId = Number(
    params.get("student_id")
);


const admissionData = sessionStorage.getItem(
    "universityAdmission"
);


if (!admissionData) {
    window.location.href =
        "/frontend/university.html";
}


const student = JSON.parse(admissionData);


if (student.student_id !== studentId) {
    window.location.href =
        "/frontend/university.html";
}


document.getElementById(
    "student_name"
).textContent =
    `${student.first_name} ${student.last_name}`;


document.getElementById(
    "university"
).textContent =
    student.university;


document.getElementById(
    "university_email"
).textContent =
    student.university_email;


document.getElementById(
    "registration_number"
).textContent =
    student.registration_number;


document.getElementById(
    "registration_code"
).textContent =
    student.registration_code;


document.getElementById(
    "student_url"
).textContent =
    window.location.href;



const actionMessage =
    document.getElementById("action_message");


function showMessage(message) {
    actionMessage.textContent = message;

    setTimeout(() => {
        actionMessage.textContent = "";
    }, 2500);
}



async function copyText(text, message) {
    try {
        await navigator.clipboard.writeText(text);

        showMessage(message);
    }

    catch (error) {
        console.error(error);

        showMessage("Could not copy.");
    }
}



document
    .getElementById("copy_email")
    .addEventListener(
        "click",
        () => {
            copyText(
                student.university_email,
                "University email copied."
            );
        }
    );



document
    .getElementById("copy_code")
    .addEventListener(
        "click",
        () => {
            copyText(
                student.registration_code,
                "Registration code copied."
            );
        }
    );



document
    .getElementById("copy_url")
    .addEventListener(
        "click",
        () => {
            copyText(
                window.location.href,
                "Student card URL copied."
            );
        }
    );



document
    .getElementById("print_card")
    .addEventListener(
        "click",
        () => {
            window.print();
        }
    );



document
    .getElementById("download_card")
    .addEventListener(
        "click",
        () => {

            const content = `
THEFACEBOOK UNIVERSITY STUDENT IDENTITY

Student:
${student.first_name} ${student.last_name}

University:
${student.university}

University Email:
${student.university_email}

Registration Number:
${student.registration_number}

Thefacebook Registration Code:
${student.registration_code}

Student Card:
${window.location.href}


IMPORTANT

The registration code is a one-time code.

Use the university email and registration code
to create your Thefacebook account.

After registration, use the university email
and your Thefacebook password to log in.

Save this information somewhere safe.
            `.trim();


            const blob = new Blob(
                [content],
                {
                    type: "text/plain"
                }
            );


            const url =
                URL.createObjectURL(blob);


            const downloadLink =
                document.createElement("a");


            downloadLink.href = url;

            downloadLink.download =
                `thefacebook-student-${student.student_id}.txt`;


            document.body.appendChild(
                downloadLink
            );


            downloadLink.click();


            downloadLink.remove();

            URL.revokeObjectURL(url);


            showMessage(
                "Student card downloaded."
            );
        }
    );
const completeProfileForm =
    document.getElementById("completeProfileForm");

const alertBox =
    document.getElementById("profileAlert");


function showError(message) {
    alertBox.textContent = message;
    alertBox.className = "alert error";
}


function showSuccess(message) {
    alertBox.textContent = message;
    alertBox.className = "alert success";
}


function commaSeparatedToArray(value) {
    return value
        .split(",")
        .map(item => item.trim())
        .filter(item => item.length > 0);
}


async function saveProfile(e) {
    e.preventDefault();

    alertBox.textContent = "";
    alertBox.className = "alert";


    const username =
        document.getElementById("username").value.trim();

    const gender =
        document.getElementById("gender").value;

    const status =
        document.getElementById("status").value.trim();

    const residence =
        document.getElementById("residence").value.trim();

    const birthDate =
        document.getElementById("birth_date").value;

    const homeTown =
        document.getElementById("home_town").value.trim();

    const highSchool =
        document.getElementById("high_school").value.trim();

    const mobile =
        document.getElementById("mobile").value.trim();

    const websites =
        document.getElementById("websites").value.trim();

    const lookingFor =
        document.getElementById("looking_for").value;

    const interestedIn =
        document.getElementById("interested_in").value;

    const relationshipStatus =
        document.getElementById("relationship_status").value;

    const politicalViews =
        document.getElementById("political_views").value.trim();

    const interests =
        document.getElementById("interests").value.trim();

    const favoriteMusic =
        document.getElementById("favorite_music").value.trim();

    const favoriteMovies =
        document.getElementById("favorite_movies").value.trim();

    const bio =
        document.getElementById("bio").value.trim();


    if (!username) {
        showError("Please choose a username.");
        return;
    }


    const profile = {
        username: username,

        gender: gender || null,
        status: status || null,
        residence: residence || null,
        birth_date: birthDate || null,
        home_town: homeTown || null,
        high_school: highSchool || null,
        mobile: mobile || null,

        websites: commaSeparatedToArray(websites),

        looking_for: lookingFor || null,
        interested_in: interestedIn || null,

        relationship_status:
            relationshipStatus || null,

        political_views:
            politicalViews || null,

        interests:
            commaSeparatedToArray(interests),

        favorite_music:
            commaSeparatedToArray(favoriteMusic),

        favorite_movies:
            commaSeparatedToArray(favoriteMovies),

        bio: bio || null
    };


    try {
        const response = await fetch(
            "http://127.0.0.1:8000/profile",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                credentials: "include",

                body: JSON.stringify(profile)
            }
        );


        const data = await response.json();


        if (!response.ok) {
            console.error(data);

            let message =
                "Could not save profile.";

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


        showSuccess(
            "Profile created successfully."
        );


        window.location.href =
            "/frontend/profile.html";

    } catch (error) {
        console.error(error);

        showError(
            "Could not connect to the server."
        );
    }
}


completeProfileForm.addEventListener(
    "submit",
    saveProfile
);
const completeProfileForm =
    document.getElementById("completeProfileForm");

const alertBox =
    document.getElementById("profileAlert");

const profilePicture =
    document.getElementById("profile_pic");


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


    const formData = new FormData();

    formData.append("username", username);

    formData.append("gender", gender);
    formData.append("status", status);
    formData.append("residence", residence);
    formData.append("birth_date", birthDate);
    formData.append("home_town", homeTown);
    formData.append("high_school", highSchool);
    formData.append("mobile", mobile);

    formData.append(
        "websites",
        JSON.stringify(
            commaSeparatedToArray(websites)
        )
    );

    formData.append("looking_for", lookingFor);
    formData.append("interested_in", interestedIn);

    formData.append(
        "relationship_status",
        relationshipStatus
    );

    formData.append(
        "political_views",
        politicalViews
    );

    formData.append(
        "interests",
        JSON.stringify(
            commaSeparatedToArray(interests)
        )
    );

    formData.append(
        "favorite_music",
        JSON.stringify(
            commaSeparatedToArray(favoriteMusic)
        )
    );

    formData.append(
        "favorite_movies",
        JSON.stringify(
            commaSeparatedToArray(favoriteMovies)
        )
    );

    formData.append("bio", bio);


    if (profilePicture.files[0]) {
        formData.append(
            "profile_pic",
            profilePicture.files[0]
        );
    }


    try {
        const response = await fetch(
            "http://127.0.0.1:8000/profile",
            {
                method: "POST",

                credentials: "include",

                body: formData
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
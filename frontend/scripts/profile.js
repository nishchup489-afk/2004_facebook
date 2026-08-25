const API_URL = "http://127.0.0.1:8000";


const logoutLink =
    document.getElementById("logoutLink");

const quickSearch =
    document.getElementById("quickSearch");

const quickSearchButton =
    document.getElementById("quickSearchButton");


function displayValue(value) {
    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "-";
    }

    return value;
}


function displayList(value) {
    if (!Array.isArray(value)) {
        return "-";
    }

    if (value.length === 0) {
        return "-";
    }

    return value.join(", ");
}


function formatDate(value) {
    if (!value) {
        return "-";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleDateString();
}


function setText(id, value) {
    const element =
        document.getElementById(id);

    if (!element) {
        return;
    }

    element.textContent =
        displayValue(value);
}


function populateProfile(profile) {

    /*
        PROFILE TITLE
    */

    const fullName = [
        profile.first_name,
        profile.last_name
    ]
        .filter(Boolean)
        .join(" ");


    setText(
        "profileTitle",
        fullName
            ? `${fullName}'s Profile`
            : "Profile"
    );


    /*
        PROFILE PICTURE
    */

    const profilePicture =
        document.getElementById(
            "profilePicture"
        );

    if (profile.profile_pic) {
        profilePicture.src =
            profile.profile_pic;
    }


    /*
        ACCOUNT INFO
    */

    setText(
        "fullName",
        fullName || "-"
    );

    setText(
        "memberSince",
        formatDate(profile.created_at)
    );

    setText(
        "lastUpdated",
        formatDate(profile.updated_at)
    );


    /*
        BASIC INFO
    */

    setText(
        "school",
        profile.university_name
    );

    setText(
        "status",
        profile.status
    );

    setText(
        "gender",
        profile.gender
    );

    setText(
        "residence",
        profile.residence
    );

    setText(
        "birthDate",
        formatDate(profile.birth_date)
    );

    setText(
        "homeTown",
        profile.home_town
    );

    setText(
        "highSchool",
        profile.high_school
    );


    /*
        CONTACT INFO
    */

    setText(
        "email",
        profile.university_email
    );

    setText(
        "username",
        profile.username
    );

    setText(
        "mobile",
        profile.mobile
    );

    setText(
        "websites",
        displayList(profile.websites)
    );


    /*
        PERSONAL INFO
    */

    setText(
        "lookingFor",
        profile.looking_for
    );

    setText(
        "interestedIn",
        profile.interested_in
    );

    setText(
        "relationshipStatus",
        profile.relationship_status
    );

    setText(
        "politicalViews",
        profile.political_views
    );

    setText(
        "interests",
        displayList(profile.interests)
    );

    setText(
        "favoriteMusic",
        displayList(
            profile.favorite_music
        )
    );

    setText(
        "favoriteMovies",
        displayList(
            profile.favorite_movies
        )
    );

    setText(
        "bio",
        profile.bio
    );


    /*
        This is currently MY profile.

        So "Add as Friend" makes no sense here.
    */

    const friendActionBox =
        document.getElementById(
            "friendActionBox"
        );

    if (friendActionBox) {
        friendActionBox.style.display =
            "none";
    }


    const connectionStatus =
        document.getElementById(
            "connectionStatus"
        );

    if (connectionStatus) {
        connectionStatus.textContent =
            "This is your profile.";
    }
}


async function loadProfile() {

    try {

        const response = await fetch(
            `${API_URL}/profile`,
            {
                method: "GET",

                credentials: "include"
            }
        );


        if (response.status === 401) {

            window.location.href =
                "/frontend/index.html";

            return;
        }


        const data =
            await response.json();


        if (!response.ok) {

            console.error(
                "Could not load profile:",
                data
            );

            return;
        }


        populateProfile(data);


    } catch (error) {

        console.error(
            "Could not connect to server:",
            error
        );
    }
}


async function logOut(event) {

    event.preventDefault();


    try {

        const response = await fetch(
            `${API_URL}/logout`,
            {
                method: "POST",

                credentials: "include"
            }
        );


        if (!response.ok) {

            console.error(
                "Logout failed."
            );

            return;
        }


        window.location.href =
            "/frontend/index.html";


    } catch (error) {

        console.error(
            "Could not logout:",
            error
        );
    }
}


function search() {

    const query =
        quickSearch.value.trim();

    if (!query) {
        return;
    }


    window.location.href =
        `/frontend/search.html?q=${
            encodeURIComponent(query)
        }`;
}


logoutLink.addEventListener(
    "click",
    logOut
);


quickSearchButton.addEventListener(
    "click",
    search
);


quickSearch.addEventListener(
    "keydown",
    event => {

        if (event.key === "Enter") {

            event.preventDefault();

            search();
        }
    }
);


loadProfile();
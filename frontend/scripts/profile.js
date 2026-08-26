const API_URL = "http://127.0.0.1:8000";


/*
    GET USER ID FROM URL

    profile.html?user_id=15
                     ↓
                userId = "15"
*/

const params = new URLSearchParams(
    window.location.search
);

const userId = params.get("user_id");


/*
    HTML ELEMENTS
*/

const logoutLink =
    document.getElementById("logoutLink");

const quickSearch =
    document.getElementById("quickSearch");

const quickSearchButton =
    document.getElementById("quickSearchButton");

const friendActionBox =
    document.getElementById("friendActionBox");

const friendButton =
    document.getElementById("friendButton");

const connectionStatus =
    document.getElementById("connectionStatus");


/*
    DISPLAY HELPERS
*/

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


/*
    PROFILE OWNER / FRIEND UI
*/

function setupProfileActions(profile) {

    /*
        Backend should return:

        is_self: true / false
    */

    if (profile.is_self) {

        if (friendActionBox) {
            friendActionBox.style.display =
                "none";
        }

        if (connectionStatus) {
            connectionStatus.textContent =
                "This is your profile.";
        }

        return;
    }


    /*
        Someone else's profile
    */

    if (friendActionBox) {
        friendActionBox.style.display =
            "block";
    }

    if (friendButton) {
        friendButton.textContent =
            "Add as Friend";
    }

    if (connectionStatus) {
        connectionStatus.textContent =
            "You are not connected.";
    }
}


/*
    PUT PROFILE DATA INTO HTML
*/

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

    if (
        profilePicture &&
        profile.profile_pic
    ) {
        profilePicture.src =
            profile.profile_pic;
    }


    /*
        ACCOUNT INFO
    */

    setText(
        "fullName",
        fullName
    );

    setText(
        "memberSince",
        formatDate(
            profile.created_at
        )
    );

    setText(
        "lastUpdated",
        formatDate(
            profile.updated_at
        )
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
        formatDate(
            profile.birth_date
        )
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
        displayList(
            profile.websites
        )
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
        displayList(
            profile.interests
        )
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
        PROFILE OWNER / FRIEND UI
    */

    setupProfileActions(profile);
}


/*
    LOAD PROFILE FROM BACKEND
*/

async function loadProfile() {

    /*
        A profile page needs:

        profile.html?user_id=X
    */

    if (!userId) {

        console.error(
            "No user_id provided in URL."
        );

        return;
    }


    try {

        const response = await fetch(
            `${API_URL}/profile/${userId}`,
            {
                method: "GET",

                credentials: "include"
            }
        );


        /*
            Not logged in / expired session
        */

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


/*
    LOGOUT
*/

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


/*
    QUICK SEARCH
*/

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


/*
    EVENT LISTENERS
*/

if (logoutLink) {

    logoutLink.addEventListener(
        "click",
        logOut
    );
}


if (quickSearchButton) {

    quickSearchButton.addEventListener(
        "click",
        search
    );
}


if (quickSearch) {

    quickSearch.addEventListener(
        "keydown",
        event => {

            if (event.key === "Enter") {

                event.preventDefault();

                search();
            }
        }
    );
}


/*
    PAGE START
*/

loadProfile();
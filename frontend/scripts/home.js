const API_URL = "http://127.0.0.1:8000";


// =========================
// ELEMENTS
// =========================

const logoutLink = document.getElementById("logoutLink");

const profileLink = document.getElementById("profileLink");
const sideProfileLink = document.getElementById("sideProfileLink");
const directoryProfileLink = document.getElementById("directoryProfileLink");

const quickSearch = document.getElementById("quickSearch");
const quickSearchButton = document.getElementById("quickSearchButton");


// =========================
// HELPERS
// =========================

function setText(id, value) {
    const element = document.getElementById(id);

    if (!element) {
        return;
    }

    element.textContent = value ?? "-";
}

function setProfile(id , value){
    const element = document.getElementById(id);

    if(!element) return;

    element.src = value ?? "/frontend/assets/default-profile.png";
}


function profileUrl(userId) {
    return `/frontend/profile.html?user_id=${userId}`;
}


// =========================
// POPULATE HOME
// =========================

function populateHome(user) {
    const fullName = [
        user.first_name,
        user.last_name
    ]
        .filter(Boolean)
        .join(" ");


    // Welcome
    setText(
        "welcomeTitle",
        fullName ? `Welcome, ${fullName}` : "Welcome"
    );

    setText(
        "welcomeName",
        user.first_name
    );


    // Sidebar
    setText(
        "homeUserName",
        fullName
    );

    setText(
        "homeUniversity",
        user.university_name
    );

    setProfile(
        "homeProfilePicture",
        user.profile_pic
    );


    // Profile picture
    const profilePicture =
        document.getElementById("homeProfilePicture");

    if (profilePicture && user.profile_pic) {
        profilePicture.src = user.profile_pic;
    }


    // Profile links
    const url = profileUrl(user.user_id);

    if (profileLink) {
        profileLink.href = url;
    }

    if (sideProfileLink) {
        sideProfileLink.href = url;
    }

    if (directoryProfileLink) {
        directoryProfileLink.href = url;
    }
}


// =========================
// LOAD CURRENT USER
// =========================

async function loadCurrentUser() {
    try {
        const response = await fetch(
            `${API_URL}/me`,
            {
                method: "GET",
                credentials: "include"
            }
        );


        // Session expired / not logged in
        if (response.status === 401) {
            window.location.href =
                "/frontend/index.html";

            return;
        }


        const data = await response.json();


        if (!response.ok) {
            console.error(
                "Could not load current user:",
                data
            );

            return;
        }


        console.log("Current user:", data);

        populateHome(data);

    } catch (error) {
        console.error(
            "Could not connect to server:",
            error
        );
    }
}


// =========================
// LOGOUT
// =========================

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
            console.error("Logout failed.");
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


// =========================
// SEARCH
// =========================

function search() {
    if (!quickSearch) {
        return;
    }

    const query = quickSearch.value.trim();

    if (!query) {
        return;
    }

    window.location.href =
        `/frontend/search.html?q=${encodeURIComponent(query)}`;
}


// =========================
// EVENT LISTENERS
// =========================

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


// =========================
// START
// =========================

loadCurrentUser();
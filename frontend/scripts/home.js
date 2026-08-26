const API_URL = "http://127.0.0.1:8000";


/*
    URL:

    home.html?user_id=15

    We keep this for navigation consistency,
    but the backend session is the real identity.
*/

const params = new URLSearchParams(
    window.location.search
);

const urlUserId = params.get("user_id");


/*
    HTML ELEMENTS
*/

const logoutLink =
    document.getElementById("logoutLink");

const quickSearch =
    document.getElementById("quickSearch");

const quickSearchButton =
    document.getElementById(
        "quickSearchButton"
    );

const profileLink =
    document.getElementById("profileLink");

const sideProfileLink =
    document.getElementById(
        "sideProfileLink"
    );

const directoryProfileLink =
    document.getElementById(
        "directoryProfileLink"
    );


/*
    HELPERS
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


function setText(id, value) {

    const element =
        document.getElementById(id);

    if (!element) {
        return;
    }

    element.textContent =
        displayValue(value);
}


function profileUrl(userId) {

    return (
        `/frontend/profile.html` +
        `?user_id=${userId}`
    );
}


/*
    PROFILE LINKS

    All "My Profile" links should point
    to the authenticated user's profile.
*/

function setupProfileLinks(userId) {

    const url = profileUrl(userId);


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


/*
    FRIEND REQUESTS
*/

function renderFriendRequests(
    requests
) {

    const container =
        document.getElementById(
            "friendRequests"
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";


    if (
        !Array.isArray(requests) ||
        requests.length === 0
    ) {

        container.innerHTML = `
            <p class="empty_message">
                You have no new friend requests.
            </p>
        `;

        return;
    }


    requests.forEach(request => {

        const item =
            document.createElement("div");

        item.className =
            "friend_request";


        /*
            Profile picture
        */

        const image =
            document.createElement("img");

        image.src =
            request.profile_pic ||
            "/frontend/assets/default-profile.png";

        image.alt =
            "Profile picture";


        /*
            Request information
        */

        const info =
            document.createElement("div");

        info.className =
            "friend_request_info";


        const name =
            document.createElement("div");

        name.className =
            "friend_request_name";


        const profileAnchor =
            document.createElement("a");

        profileAnchor.href =
            profileUrl(
                request.user_id
            );

        profileAnchor.textContent =
            [
                request.first_name,
                request.last_name
            ]
                .filter(Boolean)
                .join(" ");


        name.appendChild(
            profileAnchor
        );


        /*
            Buttons
        */

        const actions =
            document.createElement("div");

        actions.className =
            "friend_request_actions";


        const acceptButton =
            document.createElement("button");

        acceptButton.textContent =
            "Accept";


        const rejectButton =
            document.createElement("button");

        rejectButton.textContent =
            "Reject";


        acceptButton.addEventListener(
            "click",
            () => {
                respondToFriendRequest(
                    request.user_id,
                    "accept"
                );
            }
        );


        rejectButton.addEventListener(
            "click",
            () => {
                respondToFriendRequest(
                    request.user_id,
                    "reject"
                );
            }
        );


        actions.appendChild(
            acceptButton
        );

        actions.appendChild(
            rejectButton
        );


        info.appendChild(
            name
        );

        info.appendChild(
            actions
        );


        item.appendChild(
            image
        );

        item.appendChild(
            info
        );


        container.appendChild(
            item
        );
    });
}


/*
    FRIEND REQUEST ACTION

    These endpoints are for when your
    friendship backend exists.
*/

async function respondToFriendRequest(
    userId,
    action
) {

    try {

        const response = await fetch(
            `${API_URL}/friends/${userId}/${action}`,
            {
                method: "POST",

                credentials: "include"
            }
        );


        const data =
            await response.json();


        if (!response.ok) {

            console.error(
                "Friend request action failed:",
                data
            );

            return;
        }


        /*
            Reload dashboard after
            accepting/rejecting.
        */

        await loadHome();


    } catch (error) {

        console.error(
            "Could not update friend request:",
            error
        );
    }
}


/*
    COURSES
*/

function renderCourses(courses) {

    const container =
        document.getElementById(
            "myCourses"
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";


    if (
        !Array.isArray(courses) ||
        courses.length === 0
    ) {

        container.innerHTML = `
            <p class="empty_message">
                You have not added any courses.
            </p>
        `;

        return;
    }


    courses.forEach(course => {

        const item =
            document.createElement("div");

        item.className =
            "course_item";


        const code =
            document.createElement("div");

        code.className =
            "course_code";

        code.textContent =
            course.course_code;


        const name =
            document.createElement("div");

        name.className =
            "course_name";

        name.textContent =
            course.course_name;


        item.appendChild(code);
        item.appendChild(name);


        container.appendChild(item);
    });
}


/*
    POPULATE HOME PAGE
*/

function populateHome(data) {

    const fullName = [
        data.first_name,
        data.last_name
    ]
        .filter(Boolean)
        .join(" ");


    /*
        TOP / WELCOME
    */

    setText(
        "welcomeTitle",
        fullName
            ? `Welcome, ${fullName}`
            : "Welcome"
    );


    setText(
        "welcomeName",
        data.first_name
    );


    /*
        SIDEBAR ACCOUNT CARD
    */

    setText(
        "homeUserName",
        fullName
    );


    setText(
        "homeUniversity",
        data.university_name
    );


    const profilePicture =
        document.getElementById(
            "homeProfilePicture"
        );


    if (
        profilePicture &&
        data.profile_pic
    ) {

        profilePicture.src =
            data.profile_pic;
    }


    /*
        PROFILE LINKS
    */

    setupProfileLinks(
        data.user_id
    );


    /*
        NETWORK
    */

    setText(
        "networkSchool",
        data.university_name
    );


    setText(
        "friendCount",
        data.friend_count ?? 0
    );


    setText(
        "studentCount",
        data.student_count ?? 0
    );


    /*
        FRIEND REQUESTS
    */

    renderFriendRequests(
        data.friend_requests
    );


    /*
        COURSES
    */

    renderCourses(
        data.courses
    );


    /*
        SUMMARY
    */

    setText(
        "summaryFriends",
        data.friend_count ?? 0
    );


    setText(
        "summaryRequests",
        data.friend_requests?.length ?? 0
    );


    setText(
        "summaryCourses",
        data.courses?.length ?? 0
    );
}


/*
    LOAD HOME DASHBOARD
*/

async function loadHome() {

    try {

        /*
            IMPORTANT:

            No user_id is sent here.

            Backend determines user from
            the session cookie.
        */

        const response = await fetch(
            `${API_URL}/home`,
            {
                method: "GET",

                credentials: "include"
            }
        );


        /*
            Not authenticated
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
                "Could not load home:",
                data
            );

            return;
        }


        /*
            Keep browser URL:

            home.html?user_id=X

            But X comes from authenticated
            backend response, not user input.
        */

        if (
            !urlUserId ||
            String(data.user_id)
                !== String(urlUserId)
        ) {

            const correctUrl =
                `/frontend/home.html` +
                `?user_id=${data.user_id}`;


            window.history.replaceState(
                {},
                "",
                correctUrl
            );
        }


        populateHome(data);


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
    SEARCH
*/

function search() {

    if (!quickSearch) {
        return;
    }


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
    START PAGE
*/

loadHome();
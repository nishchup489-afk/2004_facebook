const DEFAULT_PROFILE_PICTURE =
    "/frontend/assets/default-profile.png";


// =========================
// ELEMENTS
// =========================

const logoutLink =
    document.getElementById("logoutLink");

const profileLink =
    document.getElementById("profileLink");

const sideProfileLink =
    document.getElementById("sideProfileLink");

const directoryProfileLink =
    document.getElementById("directoryProfileLink");

const quickSearch =
    document.getElementById("quickSearch");

const quickSearchButton =
    document.getElementById("quickSearchButton");

const friendRequests =
    document.getElementById("friendRequests");

const homeSuggestions =
    document.getElementById("homeSuggestions");

const homeSuggestionCount =
    document.getElementById("homeSuggestionCount");

const myCourses =
    document.getElementById("myCourses");


let currentUser = null;


// =========================
// HELPERS
// =========================

function setText(id, value) {

    const element =
        document.getElementById(id);

    if (!element) {
        return;
    }

    element.textContent =
        value ?? "-";
}


function setProfile(id, value) {

    const element =
        document.getElementById(id);

    if (!element) {
        return;
    }

    element.src =
        value ||
        DEFAULT_PROFILE_PICTURE;
}


function profileUrl(userId) {

    return (
        `/frontend/profile.html` +
        `?user_id=${userId}`
    );
}


function fullName(user) {

    return [
        user.first_name,
        user.last_name
    ]
        .filter(Boolean)
        .join(" ");
}


function profilePicture(user) {

    return (
        user.profile_pic ||
        DEFAULT_PROFILE_PICTURE
    );
}


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


function createFriendshipLabel(
    text,
    extraClass = ""
) {

    const label =
        document.createElement("span");

    label.className =
        `home_friend_label ${extraClass}`.trim();

    label.textContent =
        text;

    return label;
}


async function getJson(path) {

    try {

        const response = await fetch(
            `${API_URL}${path}`,
            {
                method: "GET",
                credentials: "include"
            }
        );


        if (response.status === 401) {

            window.location.href =
                "/frontend/index.html";

            return null;
        }


        const data =
            await response.json();


        if (!response.ok) {

            console.error(
                `Could not load ${path}:`,
                data
            );

            return null;
        }


        return data;


    } catch (error) {

        console.error(
            `Could not connect to ${path}:`,
            error
        );

        return null;
    }
}


// =========================
// POPULATE HOME
// =========================

function populateHome(user) {

    const name =
        fullName(user);


    setText(
        "welcomeTitle",
        name
            ? `Welcome, ${name}`
            : "Welcome"
    );

    setText(
        "welcomeName",
        user.first_name
    );

    setText(
        "homeUserName",
        name
    );

    setText(
        "homeUniversity",
        user.university_name
    );

    setText(
        "networkSchool",
        user.university_name
    );

    setProfile(
        "homeProfilePicture",
        user.profile_pic
    );


    const url =
        profileUrl(user.user_id);


    [
        profileLink,
        sideProfileLink,
        directoryProfileLink,
        document.getElementById(
            "homeUserName"
        )
    ].forEach(link => {

        if (link) {
            link.href = url;
        }
    });
}


// =========================
// SOCIAL DATA
// =========================

async function loadCurrentUser() {

    const data =
        await getJson("/me");

    if (!data) {
        return false;
    }

    currentUser = data;

    populateHome(data);

    return true;
}


async function loadHomeSocialData() {

    const [
        friendsData,
        requestsData,
        suggestionsData,
        coursesData
    ] = await Promise.all([
        getJson("/friends"),
        getJson("/friends/requests"),
        getJson("/friends/suggestions"),
        getJson("/courses/mine"),
    ]);


    const friends =
        friendsData?.friends || [];

    const requests =
        requestsData?.requests || [];

    const suggestions =
        suggestionsData?.suggestions || [];

    const courses =
        coursesData?.courses || [];


    setText(
        "friendCount",
        friends.length
    );

    setText(
        "summaryFriends",
        friends.length
    );

    setText(
        "summaryRequests",
        requests.length
    );

    setText(
        "summaryCourses",
        courses.length
    );

    setText(
        "studentCount",
        suggestions.length
    );

    if (homeSuggestionCount) {
        homeSuggestionCount.textContent =
            suggestions.length;
    }


    renderHomeRequests(
        requests
    );

    renderHomeSuggestions(
        suggestions
    );

    renderHomeCourses(
        courses
    );
}


function createHomePerson(
    user,
    showReason = false
) {

    const row =
        document.createElement("div");

    row.className =
        "home_person";


    const image =
        document.createElement("img");

    image.src =
        profilePicture(user);

    image.alt =
        `${fullName(user)} profile picture`;


    const info =
        document.createElement("div");

    info.className =
        "home_person_info";


    const link =
        document.createElement("a");

    link.href =
        profileUrl(user.user_id);

    link.textContent =
        fullName(user) || "Unknown User";


    const meta =
        document.createElement("div");

    meta.className =
        "home_person_meta";

    meta.innerHTML = `
        ${displayValue(user.university_name)}
        <br>
        ${displayValue(user.status)}
    `;


    info.appendChild(link);
    info.appendChild(meta);


    if (user.looking_for) {

        const lookingFor =
            document.createElement("div");

        lookingFor.className =
            "home_person_meta";

        lookingFor.textContent =
            `Looking for ${user.looking_for}`;

        info.appendChild(
            lookingFor
        );
    }


    if (user.relationship_status) {

        const relationship =
            document.createElement("div");

        relationship.className =
            "home_person_meta";

        relationship.textContent =
            user.relationship_status;

        info.appendChild(
            relationship
        );
    }


    if (
        showReason &&
        user.suggestion_reason
    ) {

        const reason =
            document.createElement("div");

        reason.className =
            "home_suggestion_reason";

        reason.textContent =
            user.suggestion_reason;

        info.appendChild(
            reason
        );
    }


    const actions =
        document.createElement("div");

    actions.className =
        "home_person_actions";


    const profile =
        document.createElement("a");

    profile.href =
        profileUrl(user.user_id);

    profile.textContent =
        "view";

    actions.appendChild(
        profile
    );


    row.appendChild(image);
    row.appendChild(info);
    row.appendChild(actions);


    return {
        row,
        actions,
    };
}


function addFriendshipActions(
    actions,
    user
) {

    const friendshipStatus =
        user.friendship_status || "none";


    if (friendshipStatus === "accepted") {

        actions.appendChild(
            createFriendshipLabel("Friends")
        );

        return;
    }


    if (friendshipStatus === "pending_sent") {

        actions.appendChild(
            createFriendshipLabel(
                "Requested",
                "pending_label"
            )
        );

        return;
    }


    if (friendshipStatus === "pending_received") {

        actions.appendChild(
            createFriendshipLabel(
                "Pending",
                "pending_label"
            )
        );


        const acceptButton =
            document.createElement("button");

        acceptButton.textContent =
            "accept";

        acceptButton.addEventListener(
            "click",
            () => {
                acceptFriend(
                    user.user_id,
                    acceptButton
                );
            }
        );


        const rejectButton =
            document.createElement("button");

        rejectButton.textContent =
            "reject";

        rejectButton.addEventListener(
            "click",
            () => {
                rejectFriend(
                    user.user_id,
                    rejectButton
                );
            }
        );


        actions.appendChild(
            acceptButton
        );

        actions.appendChild(
            rejectButton
        );

        return;
    }


    const addButton =
        document.createElement("button");

    addButton.textContent =
        "add";

    addButton.addEventListener(
        "click",
        () => {
            sendFriendRequest(
                user.user_id,
                addButton
            );
        }
    );

    actions.appendChild(
        addButton
    );
}


function renderHomeRequests(requests) {

    if (!friendRequests) {
        return;
    }

    friendRequests.innerHTML = "";


    if (requests.length === 0) {

        friendRequests.innerHTML = `
            <p class="empty_message">
                You have no new friend requests.
            </p>
        `;

        return;
    }


    requests.slice(0, 3).forEach(user => {

        const person =
            createHomePerson(user);

        addFriendshipActions(
            person.actions,
            {
                ...user,
                friendship_status:
                    "pending_received"
            }
        );

        friendRequests.appendChild(
            person.row
        );
    });
}


function renderHomeSuggestions(suggestions) {

    if (!homeSuggestions) {
        return;
    }

    homeSuggestions.innerHTML = "";


    const visibleSuggestions =
        suggestions
            .filter(user => (
                !currentUser ||
                user.user_id !== currentUser.user_id
            ))
            .slice(0, 4);


    if (visibleSuggestions.length === 0) {

        homeSuggestions.innerHTML = `
            <p class="empty_message">
                No suggestions available.
            </p>
        `;

        return;
    }


    visibleSuggestions.forEach(user => {

        const person =
            createHomePerson(
                user,
                true
            );

        addFriendshipActions(
            person.actions,
            user
        );

        homeSuggestions.appendChild(
            person.row
        );
    });
}


function renderHomeCourses(
    courses
) {

    if (!myCourses) {
        return;
    }

    myCourses.innerHTML = "";


    if (courses.length === 0) {

        myCourses.innerHTML = `
            <p class="empty_message">
                You have not added any courses.
            </p>
        `;

        return;
    }


    courses.slice(0, 4).forEach(course => {

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


        const meta =
            document.createElement("div");

        meta.className =
            "course_meta";

        meta.textContent =
            `${course.semester} ${course.academic_year}`;


        item.appendChild(code);
        item.appendChild(name);
        item.appendChild(meta);

        myCourses.appendChild(item);
    });
}


async function sendFriendRequest(
    targetUserId,
    button
) {

    button.disabled = true;
    button.textContent = "...";


    try {

        const response = await fetch(
            `${API_URL}/friends/${targetUserId}`,
            {
                method: "POST",
                credentials: "include"
            }
        );

        const data =
            await response.json();


        if (!response.ok) {

            console.error(
                "Could not send friend request:",
                data
            );

            await loadHomeSocialData();

            return;
        }


        await loadHomeSocialData();


    } catch (error) {

        console.error(
            "Could not send friend request:",
            error
        );

        button.disabled = false;
        button.textContent = "add";
    }
}


async function acceptFriend(
    targetUserId,
    button
) {

    button.disabled = true;


    try {

        const response = await fetch(
            `${API_URL}/friends/${targetUserId}/accept`,
            {
                method: "POST",
                credentials: "include"
            }
        );


        if (!response.ok) {
            button.disabled = false;
            return;
        }


        await loadHomeSocialData();


    } catch (error) {

        console.error(
            "Could not accept friend:",
            error
        );

        button.disabled = false;
    }
}


async function rejectFriend(
    targetUserId,
    button
) {

    button.disabled = true;


    try {

        const response = await fetch(
            `${API_URL}/friends/${targetUserId}/reject`,
            {
                method: "POST",
                credentials: "include"
            }
        );


        if (!response.ok) {
            button.disabled = false;
            return;
        }


        await loadHomeSocialData();


    } catch (error) {

        console.error(
            "Could not reject friend:",
            error
        );

        button.disabled = false;
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

async function startPage() {

    await ensureFrontendConfig();

    const authenticated =
        await loadCurrentUser();

    if (!authenticated) {
        return;
    }

    await loadHomeSocialData();
}


startPage();

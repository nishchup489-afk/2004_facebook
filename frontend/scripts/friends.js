const API_URL = "http://127.0.0.1:8000";

const DEFAULT_PROFILE_PICTURE =
    "/frontend/assets/default-profile.png";


/*
    ELEMENTS
*/

const logoutLink =
    document.getElementById("logoutLink");

const homeLink =
    document.getElementById("homeLink");

const profileLink =
    document.getElementById("profileLink");

const sideProfileLink =
    document.getElementById("sideProfileLink");

const quickSearch =
    document.getElementById("quickSearch");

const quickSearchButton =
    document.getElementById(
        "quickSearchButton"
    );


const friendsList =
    document.getElementById(
        "friendsList"
    );

const friendRequests =
    document.getElementById(
        "friendRequests"
    );

const friendSuggestions =
    document.getElementById(
        "friendSuggestions"
    );


/*
    COUNTERS
*/

const friendCount =
    document.getElementById(
        "friendCount"
    );

const requestCount =
    document.getElementById(
        "requestCount"
    );

const suggestionCount =
    document.getElementById(
        "suggestionCount"
    );

const friendsSectionCount =
    document.getElementById(
        "friendsSectionCount"
    );

const friendRequestCount =
    document.getElementById(
        "friendRequestCount"
    );

const suggestionsSectionCount =
    document.getElementById(
        "suggestionsSectionCount"
    );


/*
    CURRENT USER
*/

let currentUser = null;


/*
    HELPERS
*/

function profileUrl(userId) {

    return (
        `/frontend/profile.html` +
        `?user_id=${userId}`
    );
}


function homeUrl(userId) {

    return (
        `/frontend/home.html` +
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


function setCount(
    element,
    value,
    suffix = ""
) {

    if (!element) {
        return;
    }

    element.textContent =
        `${value}${suffix}`;
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
        `friend_label ${extraClass}`.trim();

    label.textContent =
        text;

    return label;
}


/*
    LOAD CURRENT USER
*/

async function loadCurrentUser() {

    try {

        const response = await fetch(
            `${API_URL}/me`,
            {
                method: "GET",
                credentials: "include"
            }
        );


        if (response.status === 401) {

            window.location.href =
                "/frontend/index.html";

            return false;
        }


        const data =
            await response.json();


        if (!response.ok) {

            console.error(
                "Could not load current user:",
                data
            );

            return false;
        }


        currentUser = data;


        if (homeLink) {
            homeLink.href =
                homeUrl(data.user_id);
        }


        if (profileLink) {
            profileLink.href =
                profileUrl(data.user_id);
        }


        if (sideProfileLink) {
            sideProfileLink.href =
                profileUrl(data.user_id);
        }


        return true;


    } catch (error) {

        console.error(
            "Could not connect to server:",
            error
        );

        return false;
    }
}


/*
    CREATE PERSON IMAGE
*/

function createPicture(user) {

    const pictureContainer =
        document.createElement("div");

    pictureContainer.className =
        "person_picture";


    const image =
        document.createElement("img");

    image.src =
        profilePicture(user);

    image.alt =
        `${fullName(user)} profile picture`;


    pictureContainer.appendChild(
        image
    );


    return pictureContainer;
}


/*
    CREATE PERSON INFO
*/

function createPersonInfo(
    user,
    showMutualFriends = false
) {

    const info =
        document.createElement("div");

    info.className =
        "person_info";


    /*
        NAME
    */

    const name =
        document.createElement("div");

    name.className =
        "person_name";


    const link =
        document.createElement("a");

    link.href =
        profileUrl(user.user_id);

    link.textContent =
        fullName(user) || "Unknown User";


    name.appendChild(link);


    /*
        DETAILS
    */

    const details =
        document.createElement("div");

    details.className =
        "person_details";


    const university =
        document.createElement("div");

    university.innerHTML = `
        <span class="label">
            School:
        </span>

        ${
            user.university_name ||
            "-"
        }
    `;


    const status =
        document.createElement("div");

    status.innerHTML = `
        <span class="label">
            Status:
        </span>

        ${
            displayValue(user.status)
        }
    `;


    details.appendChild(
        university
    );

    details.appendChild(
        status
    );


    if (user.looking_for) {

        const lookingFor =
            document.createElement("div");

        lookingFor.innerHTML = `
            <span class="label">
                Looking For:
            </span>

            ${displayValue(user.looking_for)}
        `;

        details.appendChild(
            lookingFor
        );
    }


    if (user.relationship_status) {

        const relationship =
            document.createElement("div");

        relationship.innerHTML = `
            <span class="label">
                Relationship:
            </span>

            ${displayValue(user.relationship_status)}
        `;

        details.appendChild(
            relationship
        );
    }


    info.appendChild(name);
    info.appendChild(details);


    /*
        MUTUAL FRIENDS
    */

    if (showMutualFriends) {

        const mutual =
            document.createElement("div");

        mutual.className =
            "mutual_friends";


        const count =
            user.mutual_friend_count ?? 0;


        mutual.textContent =
            count === 1
                ? "1 mutual friend"
                : `${count} mutual friends`;


        info.appendChild(
            mutual
        );
    }


    if (user.suggestion_reason) {

        const reason =
            document.createElement("div");

        reason.className =
            "suggestion_reason";

        reason.textContent =
            user.suggestion_reason;

        info.appendChild(
            reason
        );
    }


    return info;
}


/*
    VIEW PROFILE LINK
*/

function createViewProfileLink(
    userId
) {

    const link =
        document.createElement("a");

    link.href =
        profileUrl(userId);

    link.textContent =
        "View Profile";


    return link;
}


function addFriendshipActions(
    actions,
    user,
    refreshAfterChange
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
            document.createElement(
                "button"
            );

        acceptButton.className =
            "accept_button";

        acceptButton.textContent =
            "Accept";

        acceptButton.addEventListener(
            "click",
            () => {

                acceptFriend(
                    user.user_id,
                    acceptButton,
                    refreshAfterChange
                );
            }
        );


        const rejectButton =
            document.createElement(
                "button"
            );

        rejectButton.className =
            "reject_button";

        rejectButton.textContent =
            "Reject";

        rejectButton.addEventListener(
            "click",
            () => {

                rejectFriend(
                    user.user_id,
                    rejectButton,
                    refreshAfterChange
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
        document.createElement(
            "button"
        );

    addButton.textContent =
        "Add as Friend";

    addButton.addEventListener(
        "click",
        () => {

            sendFriendRequest(
                user.user_id,
                addButton,
                refreshAfterChange
            );
        }
    );


    actions.appendChild(
        addButton
    );
}


/*
    LOAD FRIENDS
*/

async function loadFriends() {

    try {

        const response = await fetch(
            `${API_URL}/friends`,
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
                "Could not load friends:",
                data
            );

            return;
        }


        const friends =
            Array.isArray(data)
                ? data
                : data.friends || [];


        renderFriends(friends);


    } catch (error) {

        console.error(
            "Could not load friends:",
            error
        );
    }
}


/*
    RENDER FRIENDS
*/

function renderFriends(friends) {

    friendsList.innerHTML = "";


    const count =
        friends.length;


    setCount(
        friendCount,
        count
    );


    setCount(
        friendsSectionCount,
        count,
        count === 1
            ? " friend"
            : " friends"
    );


    if (count === 0) {

        friendsList.innerHTML = `
            <div class="empty_message">
                You have not added any friends yet.
            </div>
        `;

        return;
    }


    friends.forEach(user => {

        const row =
            document.createElement("div");

        row.className =
            "person_row";


        const picture =
            createPicture(user);


        const info =
            createPersonInfo(user);


        const actions =
            document.createElement("div");

        actions.className =
            "person_actions";


        actions.appendChild(
            createViewProfileLink(
                user.user_id
            )
        );


        const friendLabel =
            document.createElement("span");

        friendLabel.className =
            "friend_label";

        friendLabel.textContent =
            "Friends";


        actions.appendChild(
            friendLabel
        );


        row.appendChild(
            picture
        );

        row.appendChild(
            info
        );

        row.appendChild(
            actions
        );


        friendsList.appendChild(
            row
        );
    });
}


/*
    LOAD FRIEND REQUESTS
*/

async function loadFriendRequests() {

    try {

        const response = await fetch(
            `${API_URL}/friends/requests`,
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
                "Could not load requests:",
                data
            );

            return;
        }


        const requests =
            Array.isArray(data)
                ? data
                : data.requests || [];


        renderFriendRequests(
            requests
        );


    } catch (error) {

        console.error(
            "Could not load requests:",
            error
        );
    }
}


/*
    RENDER FRIEND REQUESTS
*/

function renderFriendRequests(
    requests
) {

    friendRequests.innerHTML = "";


    const count =
        requests.length;


    setCount(
        requestCount,
        count
    );


    setCount(
        friendRequestCount,
        count
    );


    if (count === 0) {

        friendRequests.innerHTML = `
            <div class="empty_message">
                You have no new friend requests.
            </div>
        `;

        return;
    }


    requests.forEach(user => {

        const row =
            document.createElement("div");

        row.className =
            "person_row";


        const picture =
            createPicture(user);


        const info =
            createPersonInfo(user);


        const actions =
            document.createElement("div");

        actions.className =
            "person_actions";


        actions.appendChild(
            createViewProfileLink(
                user.user_id
            )
        );


        /*
            ACCEPT
        */

        const acceptButton =
            document.createElement(
                "button"
            );

        acceptButton.className =
            "accept_button";

        acceptButton.textContent =
            "Accept";


        acceptButton.addEventListener(
            "click",
            () => {

                acceptFriend(
                    user.user_id,
                    acceptButton
                );
            }
        );


        /*
            REJECT
        */

        const rejectButton =
            document.createElement(
                "button"
            );

        rejectButton.className =
            "reject_button";

        rejectButton.textContent =
            "Reject";


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


        row.appendChild(
            picture
        );

        row.appendChild(
            info
        );

        row.appendChild(
            actions
        );


        friendRequests.appendChild(
            row
        );
    });
}


/*
    ACCEPT FRIEND
*/

async function acceptFriend(
    userId,
    button,
    refreshAfterChange = refreshFriendPage
) {

    button.disabled = true;


    try {

        const response = await fetch(
            `${API_URL}/friends/${userId}/accept`,
            {
                method: "POST",
                credentials: "include"
            }
        );


        const data =
            await response.json();


        if (!response.ok) {

            console.error(
                "Could not accept request:",
                data
            );

            button.disabled = false;

            return;
        }


        /*
            Refresh all three sections because:

            request disappears
            friend appears
            suggestions may change
        */

        await refreshAfterChange();


    } catch (error) {

        console.error(
            "Could not accept request:",
            error
        );

        button.disabled = false;
    }
}


/*
    REJECT FRIEND
*/

async function rejectFriend(
    userId,
    button,
    refreshAfterChange = refreshFriendPage
) {

    button.disabled = true;


    try {

        const response = await fetch(
            `${API_URL}/friends/${userId}/reject`,
            {
                method: "POST",
                credentials: "include"
            }
        );


        const data =
            await response.json();


        if (!response.ok) {

            console.error(
                "Could not reject request:",
                data
            );

            button.disabled = false;

            return;
        }


        await refreshAfterChange();


    } catch (error) {

        console.error(
            "Could not reject request:",
            error
        );

        button.disabled = false;
    }
}


/*
    LOAD SUGGESTIONS
*/

async function loadSuggestions() {

    try {

        const response = await fetch(
            `${API_URL}/friends/suggestions`,
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
                "Could not load suggestions:",
                data
            );

            return;
        }


        const suggestions =
            Array.isArray(data)
                ? data
                : data.suggestions || [];


        renderSuggestions(
            suggestions
        );


    } catch (error) {

        console.error(
            "Could not load suggestions:",
            error
        );
    }
}


/*
    RENDER SAME UNIVERSITY SUGGESTIONS
*/

function renderSuggestions(
    suggestions
) {

    friendSuggestions.innerHTML = "";


    const count =
        suggestions.length;


    setCount(
        suggestionCount,
        count
    );


    setCount(
        suggestionsSectionCount,
        count,
        count === 1
            ? " suggestion"
            : " suggestions"
    );


    if (count === 0) {

        friendSuggestions.innerHTML = `
            <div class="empty_message">
                No suggestions available.
            </div>
        `;

        return;
    }


    suggestions.forEach(user => {

        /*
            Backend should already exclude self.

            This is just extra frontend safety.
        */

        if (
            currentUser &&
            user.user_id ===
                currentUser.user_id
        ) {
            return;
        }


        const row =
            document.createElement("div");

        row.className =
            "person_row";


        const picture =
            createPicture(user);


        const info =
            createPersonInfo(
                user,
                true
            );


        const actions =
            document.createElement("div");

        actions.className =
            "person_actions";


        actions.appendChild(
            createViewProfileLink(
                user.user_id
            )
        );


        addFriendshipActions(
            actions,
            user,
            refreshFriendPage
        );


        row.appendChild(
            picture
        );

        row.appendChild(
            info
        );

        row.appendChild(
            actions
        );


        friendSuggestions.appendChild(
            row
        );
    });
}


/*
    SEND FRIEND REQUEST
*/

async function sendFriendRequest(
    userId,
    button,
    refreshAfterChange = loadSuggestions
) {

    button.disabled = true;


    try {

        const response = await fetch(
            `${API_URL}/friends/${userId}`,
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

            button.disabled = false;

            return;
        }


        button.textContent =
            "Requested";


        /*
            Reload social data so this person
            stays visible as requested/pending.
        */

        await refreshAfterChange();


    } catch (error) {

        console.error(
            "Could not send friend request:",
            error
        );

        button.disabled = false;
    }
}


/*
    QUICK SEARCH
*/

function runQuickSearch() {

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
    REFRESH SOCIAL DATA
*/

async function refreshFriendPage() {

    await Promise.all([
        loadFriends(),
        loadFriendRequests(),
        loadSuggestions(),
    ]);
}


/*
    EVENTS
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
        runQuickSearch
    );
}


if (quickSearch) {

    quickSearch.addEventListener(
        "keydown",
        event => {

            if (event.key === "Enter") {

                event.preventDefault();

                runQuickSearch();
            }
        }
    );
}


/*
    START PAGE
*/

async function startPage() {

    const authenticated =
        await loadCurrentUser();


    if (!authenticated) {
        return;
    }


    await refreshFriendPage();
}


startPage();

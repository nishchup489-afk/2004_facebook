const API_URL = "http://127.0.0.1:8000";

const DEFAULT_PROFILE_PICTURE =
    "/frontend/assets/default-profile.png";


/*
    ELEMENTS
*/

const searchForm =
    document.getElementById("searchForm");

const searchInput =
    document.getElementById("searchInput");

const schoolFilter =
    document.getElementById("schoolFilter");

const statusFilter =
    document.getElementById("statusFilter");

const searchResults =
    document.getElementById("searchResults");

const searchInfo =
    document.getElementById("searchInfo");

const resultCount =
    document.getElementById("resultCount");


const quickSearch =
    document.getElementById("quickSearch");

const quickSearchButton =
    document.getElementById(
        "quickSearchButton"
    );


const logoutLink =
    document.getElementById("logoutLink");

const homeLink =
    document.getElementById("homeLink");

const profileLink =
    document.getElementById("profileLink");

const sideProfileLink =
    document.getElementById(
        "sideProfileLink"
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


/*
    LOAD CURRENT LOGGED-IN USER

    Used for:
    - My Profile
    - Home
    - knowing if search result is me
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
    URL PARAMETERS

    search.html?q=alex&school=1&status=student
*/

function loadSearchFromUrl() {

    const params =
        new URLSearchParams(
            window.location.search
        );


    const query =
        params.get("q") || "";

    const school =
        params.get("school") || "";

    const status =
        params.get("status") || "";


    searchInput.value = query;

    schoolFilter.value = school;

    statusFilter.value = status;


    if (query) {

        performSearch(
            query,
            school,
            status
        );
    }
}


/*
    UPDATE BROWSER URL

    Search stays shareable / refreshable.
*/

function updateSearchUrl(
    query,
    school,
    status
) {

    const params =
        new URLSearchParams();


    if (query) {

        params.set(
            "q",
            query
        );
    }


    if (school) {

        params.set(
            "school",
            school
        );
    }


    if (status) {

        params.set(
            "status",
            status
        );
    }


    const url =
        `/frontend/search.html?${params.toString()}`;


    window.history.pushState(
        {},
        "",
        url
    );
}


/*
    SEARCH BACKEND
*/

async function performSearch(
    query,
    school = "",
    status = ""
) {

    query = query.trim();


    if (!query) {

        searchInfo.textContent =
            "Enter a name to search Thefacebook directory.";

        searchResults.innerHTML = `
            <div class="empty_results">
                Enter a name to search.
            </div>
        `;

        resultCount.textContent =
            "0 results";

        return;
    }


    searchInfo.textContent =
        `Searching for "${query}"...`;


    /*
        Build:

        /search?q=alex&school=1&status=student
    */

    const params =
        new URLSearchParams();

    params.set(
        "q",
        query
    );


    if (school) {

        params.set(
            "school",
            school
        );
    }


    if (status) {

        params.set(
            "status",
            status
        );
    }


    try {

        const response = await fetch(
            `${API_URL}/search?${params.toString()}`,
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
                "Search failed:",
                data
            );

            searchInfo.textContent =
                "Search could not be completed.";

            return;
        }


        /*
            Backend can return either:

            [
                {...},
                {...}
            ]

            OR

            {
                "results": [...]
            }
        */

        const results =
            Array.isArray(data)
                ? data
                : data.results || [];


        renderResults(
            results,
            query
        );


    } catch (error) {

        console.error(
            "Could not connect to server:",
            error
        );


        searchInfo.textContent =
            "Could not connect to the server.";
    }
}


/*
    RENDER RESULTS
*/

function renderResults(
    users,
    query
) {

    searchResults.innerHTML = "";


    const count =
        users.length;


    resultCount.textContent =
        `${count} ${
            count === 1
                ? "result"
                : "results"
        }`;


    searchInfo.textContent =
        `Results for "${query}"`;


    if (count === 0) {

        searchResults.innerHTML = `
            <div class="empty_results">
                No people were found.
            </div>
        `;

        return;
    }


    users.forEach(user => {

        const result =
            createPersonResult(user);


        searchResults.appendChild(
            result
        );
    });
}


/*
    CREATE ONE PERSON RESULT
*/

function createPersonResult(user) {

    const container =
        document.createElement("div");

    container.className =
        "person_result";


    /*
        PICTURE
    */

    const pictureContainer =
        document.createElement("div");

    pictureContainer.className =
        "person_picture";


    const picture =
        document.createElement("img");


    picture.src =
        user.profile_pic ||
        DEFAULT_PROFILE_PICTURE;


    picture.alt =
        `${fullName(user)} profile picture`;


    pictureContainer.appendChild(
        picture
    );


    /*
        INFORMATION
    */

    const info =
        document.createElement("div");

    info.className =
        "person_info";


    const name =
        document.createElement("div");

    name.className =
        "person_name";


    const nameLink =
        document.createElement("a");

    nameLink.href =
        profileUrl(user.user_id);

    nameLink.textContent =
        fullName(user) || "Unknown User";


    name.appendChild(
        nameLink
    );


    const details =
        document.createElement("div");

    details.className =
        "person_details";


    details.innerHTML = `
        <div>
            <span class="label">
                School:
            </span>

            ${displayValue(
                user.university_name
            )}
        </div>

        <div>
            <span class="label">
                Status:
            </span>

            ${displayValue(
                user.status
            )}
        </div>
    `;


    info.appendChild(name);
    info.appendChild(details);


    /*
        ACTIONS
    */

    const actions =
        document.createElement("div");

    actions.className =
        "person_actions";


    const viewProfile =
        document.createElement("a");

    viewProfile.href =
        profileUrl(user.user_id);

    viewProfile.textContent =
        "View Profile";


    actions.appendChild(
        viewProfile
    );


    /*
        Don't show Add Friend
        on yourself.
    */

    if (
        currentUser &&
        currentUser.user_id
            !== user.user_id
    ) {

        const friendButton =
            document.createElement(
                "button"
            );

        friendButton.textContent =
            "Add as Friend";


        friendButton.addEventListener(
            "click",
            () => {

                addFriend(
                    user.user_id,
                    friendButton
                );
            }
        );


        actions.appendChild(
            friendButton
        );
    }


    container.appendChild(
        pictureContainer
    );

    container.appendChild(
        info
    );

    container.appendChild(
        actions
    );


    return container;
}


/*
    ADD FRIEND

    This assumes your future endpoint:

    POST /friends/{user_id}
*/

async function addFriend(
    targetUserId,
    button
) {

    button.disabled = true;


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

            button.disabled = false;

            return;
        }


        button.textContent =
            "Request Sent";


    } catch (error) {

        console.error(
            "Could not send friend request:",
            error
        );


        button.disabled = false;
    }
}


/*
    MAIN SEARCH FORM
*/

function submitSearch(event) {

    event.preventDefault();


    const query =
        searchInput.value.trim();

    const school =
        schoolFilter.value;

    const status =
        statusFilter.value;


    if (!query) {
        return;
    }


    updateSearchUrl(
        query,
        school,
        status
    );


    performSearch(
        query,
        school,
        status
    );
}


/*
    QUICK SEARCH
*/

function runQuickSearch() {

    const query =
        quickSearch.value.trim();


    if (!query) {
        return;
    }


    searchInput.value =
        query;


    updateSearchUrl(
        query,
        "",
        ""
    );


    performSearch(
        query
    );
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
    EVENTS
*/

if (searchForm) {

    searchForm.addEventListener(
        "submit",
        submitSearch
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


if (logoutLink) {

    logoutLink.addEventListener(
        "click",
        logOut
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


    loadSearchFromUrl();
}


startPage();
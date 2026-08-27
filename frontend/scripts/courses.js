const DEFAULT_PROFILE_PICTURE =
    "/frontend/assets/default-profile.png";


const logoutLink =
    document.getElementById("logoutLink");

const profileLink =
    document.getElementById("profileLink");

const sideProfileLink =
    document.getElementById("sideProfileLink");

const quickSearch =
    document.getElementById("quickSearch");

const quickSearchButton =
    document.getElementById("quickSearchButton");

const myCourses =
    document.getElementById("myCourses");

const courseResults =
    document.getElementById("courseResults");

const classmatesList =
    document.getElementById("classmatesList");

const courseSearchForm =
    document.getElementById("courseSearchForm");

const courseSearch =
    document.getElementById("courseSearch");

const semesterFilter =
    document.getElementById("semesterFilter");

const yearFilter =
    document.getElementById("yearFilter");

const clearCourseSearch =
    document.getElementById("clearCourseSearch");


let currentUser = null;
let selectedCourseId = null;


function setText(
    id,
    value
) {

    const element =
        document.getElementById(id);

    if (!element) {
        return;
    }

    element.textContent =
        value ?? "-";
}


function profileUrl(
    userId
) {

    return (
        `/frontend/profile.html` +
        `?user_id=${userId}`
    );
}


function fullName(
    user
) {

    return [
        user.first_name,
        user.last_name
    ]
        .filter(Boolean)
        .join(" ");
}


function displayValue(
    value
) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "-";
    }

    return value;
}


function courseTitle(
    course
) {

    return (
        `${course.course_code}: ` +
        course.course_name
    );
}


function courseMeta(
    course
) {

    const count =
        course.enrollment_count || 0;

    const people =
        count === 1
            ? "1 person"
            : `${count} people`;


    return (
        `${course.semester} ${course.academic_year}` +
        `, ${people}`
    );
}


function createStatusLabel(
    text,
    extraClass = ""
) {

    const label =
        document.createElement("span");

    label.className =
        `status_label ${extraClass}`.trim();

    label.textContent =
        text;

    return label;
}


async function getJson(
    path
) {

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


async function loadCurrentUser() {

    const data =
        await getJson("/me");

    if (!data) {
        return false;
    }

    currentUser = data;


    const url =
        profileUrl(data.user_id);

    [
        profileLink,
        sideProfileLink
    ].forEach(link => {

        if (link) {
            link.href = url;
        }
    });


    setText(
        "courseSchool",
        data.university_name
    );


    return true;
}


function renderCourses(
    container,
    courses,
    emptyMessage
) {

    container.innerHTML = "";


    if (courses.length === 0) {

        container.innerHTML = `
            <div class="empty_message">
                ${emptyMessage}
            </div>
        `;

        return;
    }


    courses.forEach(course => {

        container.appendChild(
            createCourseRow(course)
        );
    });
}


function createCourseRow(
    course
) {

    const row =
        document.createElement("div");

    row.className =
        "course_row";

    if (selectedCourseId === course.course_id) {
        row.classList.add("selected");
    }


    const info =
        document.createElement("div");

    info.className =
        "course_info";


    const title =
        document.createElement("button");

    title.className =
        "course_title";

    title.type =
        "button";

    title.textContent =
        courseTitle(course);

    title.addEventListener(
        "click",
        () => {
            selectedCourseId =
                course.course_id;

            loadClassmates(
                course.course_id
            );
        }
    );


    const meta =
        document.createElement("div");

    meta.className =
        "course_meta";

    meta.textContent =
        courseMeta(course);


    info.appendChild(title);
    info.appendChild(meta);


    const actions =
        document.createElement("div");

    actions.className =
        "course_actions";


    const viewButton =
        document.createElement("button");

    viewButton.type =
        "button";

    viewButton.textContent =
        "Classmates";

    viewButton.addEventListener(
        "click",
        () => {
            selectedCourseId =
                course.course_id;

            loadClassmates(
                course.course_id
            );
        }
    );

    actions.appendChild(
        viewButton
    );


    if (course.is_enrolled) {

        actions.appendChild(
            createStatusLabel("Added")
        );

        const dropButton =
            document.createElement("button");

        dropButton.type =
            "button";

        dropButton.textContent =
            "Drop";

        dropButton.addEventListener(
            "click",
            () => {
                dropCourse(
                    course.course_id,
                    dropButton
                );
            }
        );

        actions.appendChild(
            dropButton
        );

    } else {

        const addButton =
            document.createElement("button");

        addButton.type =
            "button";

        addButton.textContent =
            "Add Course";

        addButton.addEventListener(
            "click",
            () => {
                enrollCourse(
                    course.course_id,
                    addButton
                );
            }
        );

        actions.appendChild(
            addButton
        );
    }


    row.appendChild(info);
    row.appendChild(actions);


    return row;
}


function renderClassmates(
    course,
    students
) {

    setText(
        "classmatesTitle",
        `Classmates in ${course.course_code}`
    );

    setText(
        "classmatesCount",
        students.length === 1
            ? "1 person"
            : `${students.length} people`
    );


    classmatesList.innerHTML = "";


    if (students.length === 0) {

        classmatesList.innerHTML = `
            <div class="empty_message">
                Nobody has added this course yet.
            </div>
        `;

        return;
    }


    students.forEach(student => {

        classmatesList.appendChild(
            createClassmateRow(student)
        );
    });
}


function createClassmateRow(
    user
) {

    const row =
        document.createElement("div");

    row.className =
        "person_row";


    const picture =
        document.createElement("img");

    picture.src =
        user.profile_pic ||
        DEFAULT_PROFILE_PICTURE;

    picture.alt =
        `${fullName(user)} profile picture`;


    const info =
        document.createElement("div");

    info.className =
        "person_info";


    const name =
        document.createElement("a");

    name.href =
        profileUrl(user.user_id);

    name.textContent =
        fullName(user) || "Unknown User";


    const meta =
        document.createElement("div");

    meta.className =
        "person_meta";

    meta.innerHTML = `
        ${displayValue(user.status)}
        <br>
        Looking for ${displayValue(user.looking_for)}
        <br>
        ${displayValue(user.relationship_status)}
    `;


    info.appendChild(name);
    info.appendChild(meta);


    const actions =
        document.createElement("div");

    actions.className =
        "person_actions";


    actions.appendChild(
        createProfileLink(user.user_id)
    );

    addFriendshipAction(
        actions,
        user
    );


    row.appendChild(picture);
    row.appendChild(info);
    row.appendChild(actions);


    return row;
}


function createProfileLink(
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


function addFriendshipAction(
    actions,
    user
) {

    const friendshipStatus =
        user.friendship_status || "none";


    if (
        friendshipStatus === "self" ||
        (
            currentUser &&
            currentUser.user_id === user.user_id
        )
    ) {

        actions.appendChild(
            createStatusLabel("This is You")
        );

        return;
    }


    if (friendshipStatus === "accepted") {

        actions.appendChild(
            createStatusLabel("Friends")
        );

        return;
    }


    if (friendshipStatus === "pending_sent") {

        actions.appendChild(
            createStatusLabel(
                "Requested",
                "pending_label"
            )
        );

        return;
    }


    if (friendshipStatus === "pending_received") {

        actions.appendChild(
            createStatusLabel(
                "Pending",
                "pending_label"
            )
        );

        const respondLink =
            document.createElement("a");

        respondLink.href =
            "/frontend/friends.html";

        respondLink.textContent =
            "Respond";

        actions.appendChild(
            respondLink
        );

        return;
    }


    const addButton =
        document.createElement("button");

    addButton.type =
        "button";

    addButton.textContent =
        "Add Friend";

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


async function refreshCourses() {

    const params =
        new URLSearchParams();

    const query =
        courseSearch.value.trim();

    const semester =
        semesterFilter.value;

    const year =
        yearFilter.value;


    if (query) {
        params.set("q", query);
    }

    if (semester) {
        params.set("semester", semester);
    }

    if (year) {
        params.set("academic_year", year);
    }


    const path =
        params.toString()
            ? `/courses?${params.toString()}`
            : "/courses";


    const [
        myCoursesData,
        catalogData
    ] = await Promise.all([
        getJson("/courses/mine"),
        getJson(path),
    ]);


    const mine =
        myCoursesData?.courses || [];

    const catalog =
        catalogData?.courses || [];


    setText(
        "myCourseCount",
        mine.length
    );

    setText(
        "resultCourseCount",
        catalog.length
    );

    setText(
        "catalogCount",
        catalog.length === 1
            ? "1 course"
            : `${catalog.length} courses`
    );


    renderCourses(
        myCourses,
        mine.slice(0, 5),
        "You have not added any courses."
    );

    renderCourses(
        courseResults,
        catalog,
        "No courses found."
    );


    if (selectedCourseId) {
        await loadClassmates(
            selectedCourseId
        );
    }
}


async function loadClassmates(
    courseId
) {

    selectedCourseId =
        courseId;

    const data =
        await getJson(
            `/courses/${courseId}/students`
        );

    if (!data) {
        return;
    }

    renderClassmates(
        data.course,
        data.students || []
    );
}


async function enrollCourse(
    courseId,
    button
) {

    button.disabled = true;
    button.textContent = "...";


    try {

        const response = await fetch(
            `${API_URL}/courses/${courseId}/enroll`,
            {
                method: "POST",
                credentials: "include"
            }
        );


        if (!response.ok) {
            button.disabled = false;
            button.textContent = "Add Course";
            return;
        }


        await refreshCourses();


    } catch (error) {

        console.error(
            "Could not add course:",
            error
        );

        button.disabled = false;
        button.textContent = "Add Course";
    }
}


async function dropCourse(
    courseId,
    button
) {

    button.disabled = true;
    button.textContent = "...";


    try {

        const response = await fetch(
            `${API_URL}/courses/${courseId}/enroll`,
            {
                method: "DELETE",
                credentials: "include"
            }
        );


        if (!response.ok) {
            button.disabled = false;
            button.textContent = "Drop";
            return;
        }


        await refreshCourses();


    } catch (error) {

        console.error(
            "Could not drop course:",
            error
        );

        button.disabled = false;
        button.textContent = "Drop";
    }
}


async function sendFriendRequest(
    userId,
    button
) {

    button.disabled = true;
    button.textContent = "...";


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

            if (
                data.detail ===
                "Friend request already sent."
            ) {
                button.replaceWith(
                    createStatusLabel(
                        "Requested",
                        "pending_label"
                    )
                );

                return;
            }

            if (
                data.detail ===
                "This user already sent you a friend request."
            ) {
                button.replaceWith(
                    createStatusLabel(
                        "Pending",
                        "pending_label"
                    )
                );

                return;
            }

            if (
                data.detail ===
                "You are already friends."
            ) {
                button.replaceWith(
                    createStatusLabel("Friends")
                );

                return;
            }

            button.disabled = false;
            button.textContent = "Add Friend";
            return;
        }


        button.replaceWith(
            createStatusLabel(
                "Requested",
                "pending_label"
            )
        );


    } catch (error) {

        console.error(
            "Could not send friend request:",
            error
        );

        button.disabled = false;
        button.textContent = "Add Friend";
    }
}


function submitCourseSearch(
    event
) {

    event.preventDefault();

    refreshCourses();
}


function clearFilters() {

    courseSearch.value = "";
    semesterFilter.value = "";
    yearFilter.value = "2004";

    refreshCourses();
}


function runQuickSearch() {

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


if (courseSearchForm) {
    courseSearchForm.addEventListener(
        "submit",
        submitCourseSearch
    );
}


if (clearCourseSearch) {
    clearCourseSearch.addEventListener(
        "click",
        clearFilters
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


async function startPage() {

    await ensureFrontendConfig();

    const authenticated =
        await loadCurrentUser();

    if (!authenticated) {
        return;
    }

    await refreshCourses();
}


startPage();

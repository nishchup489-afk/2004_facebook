import importlib
import sys
import types


def install_fake_settings(monkeypatch):
    fake_settings = types.ModuleType(
        "app.config.settings"
    )
    fake_settings.pool = None

    monkeypatch.setitem(
        sys.modules,
        "app.config.settings",
        fake_settings,
    )


def clear_course_imports():
    for module_name in [
        "app.service.courses",
        "app.service.friends",
    ]:
        sys.modules.pop(
            module_name,
            None,
        )


def import_courses_service(monkeypatch):
    install_fake_settings(monkeypatch)
    clear_course_imports()

    return importlib.import_module(
        "app.service.courses"
    )


class FakeCursor:

    def __init__(
        self,
        fetchone_results=None,
        fetchall_results=None,
    ):
        self.fetchone_results = list(
            fetchone_results or []
        )
        self.fetchall_results = list(
            fetchall_results or []
        )
        self.executed = []


    def execute(
        self,
        query,
        params,
    ):
        self.executed.append(
            (
                " ".join(query.split()),
                params,
            )
        )


    def fetchone(self):
        return self.fetchone_results.pop(0)


    def fetchall(self):
        return self.fetchall_results.pop(0)


    def __enter__(self):
        return self


    def __exit__(
        self,
        exc_type,
        exc,
        traceback,
    ):
        return False


class FakeConnection:

    def __init__(
        self,
        cursor,
    ):
        self.cursor_instance = cursor


    def cursor(self):
        return self.cursor_instance


    def __enter__(self):
        return self


    def __exit__(
        self,
        exc_type,
        exc,
        traceback,
    ):
        return False


class FakePool:

    def __init__(
        self,
        cursor,
    ):
        self.cursor_instance = cursor


    def connection(self):
        return FakeConnection(
            self.cursor_instance
        )


def course_row(
    course_id=1,
    is_enrolled=False,
):
    return (
        course_id,
        "CS50",
        "Introduction to Computer Science",
        "Harvard University",
        2004,
        "fall",
        12,
        is_enrolled,
    )


def course_access_row(
    course_id=1,
    is_enrolled=False,
    student_id=22,
):
    return (
        *course_row(
            course_id=course_id,
            is_enrolled=is_enrolled,
        ),
        student_id,
    )


def student_row(
    user_id,
    requested_by=None,
    friendship_status=None,
):
    return (
        user_id,
        "Dustin",
        "Moskovitz",
        None,
        "Harvard University",
        "Student",
        "dustin",
        "Networking",
        "Single",
        requested_by,
        friendship_status,
    )


def test_search_courses_returns_school_catalog(monkeypatch):
    courses_service = import_courses_service(
        monkeypatch
    )

    cursor = FakeCursor(
        fetchall_results=[
            [
                course_row(
                    is_enrolled=True
                )
            ]
        ]
    )

    monkeypatch.setattr(
        courses_service,
        "pool",
        FakePool(cursor),
    )

    data = courses_service.search_courses(
        current_user_id=7,
        query="CS",
        semester="fall",
        academic_year=2004,
    )

    assert data["count"] == 1
    assert data["courses"][0]["course_code"] == "CS50"
    assert data["courses"][0]["is_enrolled"] is True

    query, params = cursor.executed[0]

    assert "c.university_id = me.university_id" in query
    assert "c.course_code ILIKE %s" in query
    assert params == [
        7,
        "CS%",
        "%CS%",
        "fall",
        2004,
    ]


def test_enroll_in_course_inserts_current_student(monkeypatch):
    courses_service = import_courses_service(
        monkeypatch
    )

    cursor = FakeCursor(
        fetchone_results=[
            course_access_row(
                course_id=9,
                student_id=22,
            )
        ]
    )

    monkeypatch.setattr(
        courses_service,
        "pool",
        FakePool(cursor),
    )

    result = courses_service.enroll_in_course(
        current_user_id=7,
        course_id=9,
    )

    assert result["status"] == "enrolled"

    insert_query, insert_params = cursor.executed[1]

    assert "INSERT INTO enrollments" in insert_query
    assert insert_params == (
        22,
        9,
    )


def test_course_students_return_friendship_state(monkeypatch):
    courses_service = import_courses_service(
        monkeypatch
    )

    cursor = FakeCursor(
        fetchone_results=[
            course_access_row(
                course_id=3,
                is_enrolled=True,
            )
        ],
        fetchall_results=[
            [
                student_row(
                    user_id=7,
                ),
                student_row(
                    user_id=8,
                    requested_by=7,
                    friendship_status="pending",
                ),
            ]
        ],
    )

    monkeypatch.setattr(
        courses_service,
        "pool",
        FakePool(cursor),
    )

    data = courses_service.get_course_students(
        current_user_id=7,
        course_id=3,
    )

    assert data["course"]["course_id"] == 3
    assert data["students"][0]["friendship_status"] == "self"
    assert data["students"][1]["friendship_status"] == "pending_sent"
    assert data["students"][1]["looking_for"] == "Networking"

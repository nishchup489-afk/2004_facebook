import hashlib
import importlib
import sys
import types
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import pytest # type: ignore
from argon2 import PasswordHasher
from fastapi import FastAPI
from fastapi.testclient import TestClient


BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


fake_settings = types.ModuleType("app.config.settings")
fake_settings.pool = None
sys.modules["app.config.settings"] = fake_settings


auth_service = importlib.import_module("app.service.auth")
auth_router = importlib.import_module("app.router.auth")

from app.schema import (  # noqa: E402
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)


REGISTRATION_CODE = "ABCD-EFGH-JKLM-NPQR"
RAW_PASSWORD = "password123"
RAW_SESSION_TOKEN = "raw-session-token"
DEFAULT_EMAIL = "alex.carter@harvard.edu"


def registration_code_hash(code: str) -> str:
    normalized = code.replace("-", "").strip().upper()

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def session_token_hash(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


class FakeAuthDB:
    def __init__(self):
        self.students_by_email = {}
        self.users_by_email = {}
        self.sessions = []
        self.next_student_id = 1
        self.next_user_id = 1
        self.fail_on_session_insert = False

        self.add_student()

    def add_student(
        self,
        email=DEFAULT_EMAIL,
        first_name="Alex",
        last_name="Carter",
        code=REGISTRATION_CODE,
        claimed_at=None,
        is_active=True,
    ):
        student = {
            "id": self.next_student_id,
            "first_name": first_name,
            "last_name": last_name,
            "university_email": email,
            "registration_code_hash": registration_code_hash(code),
            "claimed_at": claimed_at,
            "is_active": is_active,
        }

        self.next_student_id += 1
        self.students_by_email[email.lower()] = student

        return student

    def add_user(
        self,
        student=None,
        email=DEFAULT_EMAIL,
        password=RAW_PASSWORD,
        is_active=True,
    ):
        if student is None:
            student = self.students_by_email[email.lower()]

        password_hash = auth_service._generate_password_hash(
            password
        )

        user = {
            "id": self.next_user_id,
            "student_id": student["id"],
            "first_name": student["first_name"],
            "last_name": student["last_name"],
            "university_email": student["university_email"],
            "password_hash": password_hash,
            "is_active": is_active,
        }

        self.next_user_id += 1
        self.users_by_email[user["university_email"].lower()] = user

        return user

    def add_session(self, user_id: int, raw_token=RAW_SESSION_TOKEN):
        session = {
            "user_id": user_id,
            "token_hash": session_token_hash(raw_token),
            "expires_at": datetime.now(timezone.utc),
        }

        self.sessions.append(session)

        return session

    def find_student_by_email(self, email: str):
        return self.students_by_email.get(email.lower())

    def find_user_by_email(self, email: str):
        return self.users_by_email.get(email.lower())

    def find_user_by_student_id(self, student_id: int):
        for user in self.users_by_email.values():
            if user["student_id"] == student_id:
                return user

        return None

    def snapshot(self):
        return {
            "students_by_email": deepcopy(self.students_by_email),
            "users_by_email": deepcopy(self.users_by_email),
            "sessions": deepcopy(self.sessions),
            "next_student_id": self.next_student_id,
            "next_user_id": self.next_user_id,
        }

    def restore(self, snapshot):
        self.students_by_email = snapshot["students_by_email"]
        self.users_by_email = snapshot["users_by_email"]
        self.sessions = snapshot["sessions"]
        self.next_student_id = snapshot["next_student_id"]
        self.next_user_id = snapshot["next_user_id"]


class FakePool:
    def __init__(self, db: FakeAuthDB):
        self.db = db

    def connection(self):
        return FakeConnection(self.db)


class FakeConnection:
    def __init__(self, db: FakeAuthDB):
        self.db = db
        self._snapshot = None

    def __enter__(self):
        self._snapshot = self.db.snapshot()

        return self

    def __exit__(self, exc_type, exc, traceback):
        if exc_type is not None:
            self.db.restore(self._snapshot)

        return False

    def cursor(self):
        return FakeCursor(self.db)


class FakeCursor:
    def __init__(self, db: FakeAuthDB):
        self.db = db
        self._result = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def execute(self, query, params=None):
        params = params or ()
        sql = " ".join(query.lower().split())

        if (
            "from students" in sql
            and "where lower(university_email)" in sql
        ):
            self._select_student_by_email(params[0])

        elif (
            "from users" in sql
            and "where student_id" in sql
        ):
            self._select_user_by_student_id(params[0])

        elif "insert into users" in sql:
            self._insert_user(params)

        elif "update students" in sql:
            self._claim_student(params[0])

        elif "insert into sessions" in sql:
            self._insert_session(params)

        elif (
            "from users" in sql
            and "where lower(university_email)" in sql
        ):
            self._select_user_by_email(params[0])

        elif "delete from sessions" in sql:
            self._delete_session(params[0])

        else:
            raise AssertionError(
                f"Unhandled SQL in fake cursor: {sql}"
            )

    def fetchone(self):
        return self._result

    def _select_student_by_email(self, email):
        student = self.db.find_student_by_email(email)

        if student is None:
            self._result = None
            return

        self._result = (
            student["id"],
            student["first_name"],
            student["last_name"],
            student["university_email"],
            student["registration_code_hash"],
            student["claimed_at"],
            student["is_active"],
        )

    def _select_user_by_student_id(self, student_id):
        user = self.db.find_user_by_student_id(student_id)

        if user is None:
            self._result = None
            return

        self._result = (user["id"],)

    def _insert_user(self, params):
        (
            student_id,
            first_name,
            last_name,
            university_email,
            password_hash,
        ) = params

        user = {
            "id": self.db.next_user_id,
            "student_id": student_id,
            "first_name": first_name,
            "last_name": last_name,
            "university_email": university_email,
            "password_hash": password_hash,
            "is_active": True,
        }

        self.db.next_user_id += 1
        self.db.users_by_email[university_email.lower()] = user
        self._result = (user["id"],)

    def _claim_student(self, student_id):
        for student in self.db.students_by_email.values():
            if student["id"] == student_id:
                student["claimed_at"] = datetime.now(timezone.utc)
                self._result = None
                return

        raise AssertionError(
            f"Student id {student_id} does not exist"
        )

    def _insert_session(self, params):
        if self.db.fail_on_session_insert:
            raise RuntimeError("session insert failed")

        user_id, token_hash, expires_at = params

        self.db.sessions.append(
            {
                "user_id": user_id,
                "token_hash": token_hash,
                "expires_at": expires_at,
            }
        )

        self._result = None

    def _select_user_by_email(self, email):
        user = self.db.find_user_by_email(email)

        if user is None:
            self._result = None
            return

        self._result = (
            user["id"],
            user["first_name"],
            user["last_name"],
            user["university_email"],
            user["password_hash"],
            user["is_active"],
        )

    def _delete_session(self, token_hash):
        self.db.sessions = [
            session
            for session in self.db.sessions
            if session["token_hash"] != token_hash
        ]

        self._result = None


@pytest.fixture(autouse=True)
def fast_password_hasher(monkeypatch):
    monkeypatch.setattr(
        auth_service,
        "password_hasher",
        PasswordHasher(
            time_cost=1,
            memory_cost=8,
            parallelism=1,
            hash_len=16,
            salt_len=16,
        ),
    )


@pytest.fixture
def fake_db(monkeypatch):
    db = FakeAuthDB()

    monkeypatch.setattr(
        auth_service,
        "pool",
        FakePool(db),
    )

    return db


def make_register_request(
    email=DEFAULT_EMAIL,
    password=RAW_PASSWORD,
    first_name="Alex",
    last_name="Carter",
    registration_code=REGISTRATION_CODE,
):
    return RegisterRequest(
        university_email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        registration_code=registration_code,
    )


def make_login_request(
    email=DEFAULT_EMAIL,
    password=RAW_PASSWORD,
):
    return LoginRequest(
        university_email=email,
        password=password,
    )


def force_session_token(
    monkeypatch,
    token=RAW_SESSION_TOKEN,
):
    monkeypatch.setattr(
        auth_service,
        "_generate_session_token",
        lambda: token,
    )

    return token


def test_registration_creates_user(fake_db, monkeypatch):
    force_session_token(monkeypatch)

    result, _ = auth_service.register_user(
        make_register_request()
    )

    user = fake_db.find_user_by_email(DEFAULT_EMAIL)

    assert result.user_id == user["id"]
    assert user["student_id"] == 1
    assert user["first_name"] == "Alex"
    assert user["last_name"] == "Carter"
    assert user["university_email"] == DEFAULT_EMAIL


def test_registration_marks_student_claimed(fake_db, monkeypatch):
    force_session_token(monkeypatch)

    student = fake_db.find_student_by_email(DEFAULT_EMAIL)

    assert student["claimed_at"] is None

    auth_service.register_user(
        make_register_request()
    )

    assert student["claimed_at"] is not None


def test_registration_hashes_password(fake_db, monkeypatch):
    force_session_token(monkeypatch)

    auth_service.register_user(
        make_register_request()
    )

    user = fake_db.find_user_by_email(DEFAULT_EMAIL)

    assert user["password_hash"] != RAW_PASSWORD
    assert auth_service.password_hasher.verify(
        user["password_hash"],
        RAW_PASSWORD,
    )


def test_registration_creates_session(fake_db, monkeypatch):
    raw_token = force_session_token(monkeypatch)

    result, session_token = auth_service.register_user(
        make_register_request()
    )

    session = fake_db.sessions[0]

    assert session_token == raw_token
    assert len(fake_db.sessions) == 1
    assert session["user_id"] == result.user_id
    assert session["token_hash"] == session_token_hash(raw_token)
    assert session["token_hash"] != raw_token


def test_wrong_registration_code_fails(fake_db, monkeypatch):
    force_session_token(monkeypatch)

    with pytest.raises(ValueError):
        auth_service.register_user(
            make_register_request(
                registration_code="ZZZZ-ZZZZ-ZZZZ-ZZZZ"
            )
        )

    student = fake_db.find_student_by_email(DEFAULT_EMAIL)

    assert fake_db.users_by_email == {}
    assert student["claimed_at"] is None
    assert fake_db.sessions == []


def test_nonexistent_student_fails(fake_db, monkeypatch):
    force_session_token(monkeypatch)

    with pytest.raises(ValueError):
        auth_service.register_user(
            make_register_request(
                email="missing.student@harvard.edu"
            )
        )

    assert fake_db.users_by_email == {}
    assert fake_db.sessions == []


def test_claimed_student_cannot_register_again(
    fake_db,
    monkeypatch,
):
    force_session_token(monkeypatch)

    student = fake_db.find_student_by_email(DEFAULT_EMAIL)
    student["claimed_at"] = datetime.now(timezone.utc)

    with pytest.raises(ValueError):
        auth_service.register_user(
            make_register_request()
        )

    assert fake_db.users_by_email == {}
    assert fake_db.sessions == []


def test_inactive_student_cannot_register(fake_db, monkeypatch):
    force_session_token(monkeypatch)

    student = fake_db.find_student_by_email(DEFAULT_EMAIL)
    student["is_active"] = False

    with pytest.raises(ValueError):
        auth_service.register_user(
            make_register_request()
        )

    assert fake_db.users_by_email == {}
    assert student["claimed_at"] is None
    assert fake_db.sessions == []


def test_valid_login_creates_session(fake_db, monkeypatch):
    raw_token = force_session_token(monkeypatch)
    user = fake_db.add_user()

    result, session_token = auth_service.login_user(
        make_login_request()
    )

    assert result.user_id == user["id"]
    assert session_token == raw_token
    assert fake_db.sessions[0]["user_id"] == user["id"]
    assert fake_db.sessions[0]["token_hash"] == session_token_hash(
        raw_token
    )


def test_wrong_password_fails(fake_db, monkeypatch):
    force_session_token(monkeypatch)
    fake_db.add_user(password="correct-password")

    with pytest.raises(ValueError):
        auth_service.login_user(
            make_login_request(password="wrong-password")
        )

    assert fake_db.sessions == []


def test_nonexistent_email_fails(fake_db, monkeypatch):
    force_session_token(monkeypatch)

    with pytest.raises(ValueError):
        auth_service.login_user(
            make_login_request(email="missing.student@harvard.edu")
        )

    assert fake_db.sessions == []


def test_inactive_user_cannot_login(fake_db, monkeypatch):
    force_session_token(monkeypatch)
    fake_db.add_user(is_active=False)

    with pytest.raises(ValueError):
        auth_service.login_user(
            make_login_request()
        )

    assert fake_db.sessions == []


def test_logout_deletes_current_session(fake_db):
    user = fake_db.add_user()
    fake_db.add_session(
        user["id"],
        raw_token=RAW_SESSION_TOKEN,
    )

    auth_service.logout_user(RAW_SESSION_TOKEN)

    assert fake_db.sessions == []


def test_logout_without_session_is_safe(monkeypatch):
    monkeypatch.setattr(
        auth_router,
        "logout_user",
        lambda raw_session_token: pytest.fail(
            "logout_user should not be called without a cookie"
        ),
    )

    client = make_api_client(monkeypatch)

    response = client.post("/logout")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Logged out successfully"
    }


def test_register_sets_httponly_session_cookie(monkeypatch):
    def fake_register_user(credentials):
        return (
            RegisterResponse(
                user_id=1,
                first_name=credentials.first_name,
                last_name=credentials.last_name,
                university_email=credentials.university_email,
                message="Registration successful",
            ),
            "register-cookie-token",
        )

    monkeypatch.setattr(
        auth_router,
        "register_user",
        fake_register_user,
    )

    client = make_api_client(monkeypatch)

    response = client.post(
        "/register",
        json={
            "university_email": DEFAULT_EMAIL,
            "password": RAW_PASSWORD,
            "first_name": "Alex",
            "last_name": "Carter",
            "registration_code": REGISTRATION_CODE,
        },
    )

    set_cookie = response.headers["set-cookie"]

    assert response.status_code == 201
    assert "thefacebook_session=register-cookie-token" in set_cookie
    assert "httponly" in set_cookie.lower()
    assert "samesite=lax" in set_cookie.lower()


def test_login_sets_httponly_session_cookie(monkeypatch):
    def fake_login_user(credentials):
        return (
            LoginResponse(
                user_id=1,
                first_name="Alex",
                last_name="Carter",
                university_email=credentials.university_email,
                message="Login successful",
            ),
            "login-cookie-token",
        )

    monkeypatch.setattr(
        auth_router,
        "login_user",
        fake_login_user,
    )

    client = make_api_client(monkeypatch)

    response = client.post(
        "/login",
        json={
            "university_email": DEFAULT_EMAIL,
            "password": RAW_PASSWORD,
        },
    )

    set_cookie = response.headers["set-cookie"]

    assert response.status_code == 200
    assert "thefacebook_session=login-cookie-token" in set_cookie
    assert "httponly" in set_cookie.lower()
    assert "samesite=lax" in set_cookie.lower()


def test_logout_deletes_session_cookie(monkeypatch):
    deleted_tokens = []

    monkeypatch.setattr(
        auth_router,
        "logout_user",
        deleted_tokens.append,
    )

    client = make_api_client(monkeypatch)
    client.cookies.set(
        "thefacebook_session",
        RAW_SESSION_TOKEN,
    )

    response = client.post("/logout")

    set_cookie = response.headers["set-cookie"]

    assert response.status_code == 200
    assert deleted_tokens == [RAW_SESSION_TOKEN]
    assert "thefacebook_session=" in set_cookie
    assert "max-age=0" in set_cookie.lower()


def test_failed_registration_does_not_leave_partial_state(
    fake_db,
    monkeypatch,
):
    force_session_token(monkeypatch)
    fake_db.fail_on_session_insert = True

    with pytest.raises(RuntimeError):
        auth_service.register_user(
            make_register_request()
        )

    student = fake_db.find_student_by_email(DEFAULT_EMAIL)

    assert fake_db.users_by_email == {}
    assert student["claimed_at"] is None
    assert fake_db.sessions == []


def make_api_client(monkeypatch):
    monkeypatch.setattr(
        auth_router,
        "COOKIE_NAME",
        "thefacebook_session",
    )

    monkeypatch.setattr(
        auth_router,
        "COOKIE_MAX_AGE",
        604800,
    )

    app = FastAPI()
    app.include_router(auth_router.router)

    return TestClient(app)

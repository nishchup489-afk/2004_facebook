import importlib
import sys
import types
from datetime import date, datetime
from pathlib import Path

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def install_fake_config_modules(monkeypatch):
    fake_settings = types.ModuleType(
        "app.config.settings"
    )
    fake_settings.pool = None

    fake_media = types.ModuleType(
        "app.config.media"
    )

    fake_cloudinary = types.ModuleType(
        "cloudinary"
    )

    fake_cloudinary_uploader = types.ModuleType(
        "cloudinary.uploader"
    )

    fake_cloudinary.uploader = fake_cloudinary_uploader

    monkeypatch.setitem(
        sys.modules,
        "app.config.settings",
        fake_settings,
    )

    monkeypatch.setitem(
        sys.modules,
        "app.config.media",
        fake_media,
    )

    monkeypatch.setitem(
        sys.modules,
        "cloudinary",
        fake_cloudinary,
    )

    monkeypatch.setitem(
        sys.modules,
        "cloudinary.uploader",
        fake_cloudinary_uploader,
    )


def clear_profile_imports():
    for module_name in [
        "app.main",
        "app.router",
        "app.router.friends",
        "app.router.profile",
        "app.service.friends",
        "app.service.profile",
        "app.service.get_user_id",
    ]:
        sys.modules.pop(
            module_name,
            None,
        )


class FakeCursor:

    def __init__(
        self,
        result,
    ):
        self.result = result
        self.query = None
        self.params = None


    def execute(
        self,
        query,
        params,
    ):
        self.query = query
        self.params = params


    def fetchone(self):
        return self.result


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
        result,
    ):
        self.cursor_instance = FakeCursor(
            result
        )


    def connection(self):
        return FakeConnection(
            self.cursor_instance
        )


def profile_view_row(
    user_id=7,
    requested_by=None,
    friendship_status=None,
):
    return (
        user_id,
        "Mark",
        "Zuckerberg",
        "mzuckerberg@harvard.edu",
        datetime(2004, 2, 4, 9, 30),
        "Harvard University",
        "https://res.cloudinary.com/demo/profile.jpg",
        "zuck",
        "Male",
        "Student",
        "Kirkland House",
        date(1984, 5, 14),
        "Dobbs Ferry, NY",
        "Phillips Exeter Academy",
        "555-0104",
        ["https://thefacebook.com"],
        "Friends",
        "Women",
        "Single",
        "Liberal",
        ["Programming", "Startups"],
        ["Daft Punk"],
        ["The Matrix"],
        "I built a small campus directory.",
        datetime(2004, 2, 5, 10, 45),
        requested_by,
        friendship_status,
    )


def test_profile_creation_route_imports(monkeypatch):
    install_fake_config_modules(monkeypatch)
    clear_profile_imports()

    from app.router.profile import save_profile_route

    assert callable(save_profile_route)


def test_profile_route_is_registered_on_app(monkeypatch):
    install_fake_config_modules(monkeypatch)
    clear_profile_imports()

    main = importlib.import_module("app.main")

    route_paths = set(
        main.app.openapi()["paths"]
    )

    assert "/profile" in route_paths


def test_get_profile_route_is_registered_on_app(monkeypatch):
    install_fake_config_modules(monkeypatch)
    clear_profile_imports()

    main = importlib.import_module("app.main")

    paths = main.app.openapi()["paths"]

    assert "/profile/{user_id}" in paths
    assert "get" in paths["/profile/{user_id}"]


def test_get_profile_returns_profile_view_response(monkeypatch):
    install_fake_config_modules(monkeypatch)
    clear_profile_imports()

    profile_service = importlib.import_module(
        "app.service.profile"
    )

    fake_pool = FakePool(
        profile_view_row(user_id=7)
    )

    monkeypatch.setattr(
        profile_service,
        "pool",
        fake_pool,
    )

    profile = profile_service.get_profile(
        current_user_id=7,
        target_user_id=7,
    )

    assert profile.user_id == 7
    assert profile.is_self is True
    assert profile.first_name == "Mark"
    assert profile.last_name == "Zuckerberg"
    assert profile.university_email == "mzuckerberg@harvard.edu"
    assert profile.university_name == "Harvard University"
    assert profile.username == "zuck"
    assert profile.websites == ["https://thefacebook.com"]
    assert profile.interests == ["Programming", "Startups"]
    assert profile.favorite_music == ["Daft Punk"]
    assert profile.favorite_movies == ["The Matrix"]
    assert profile.bio == "I built a small campus directory."
    assert profile.friendship_status == "self"
    assert fake_pool.cursor_instance.params == (7, 7, 7)


def test_get_profile_marks_other_user_as_not_self(monkeypatch):
    install_fake_config_modules(monkeypatch)
    clear_profile_imports()

    profile_service = importlib.import_module(
        "app.service.profile"
    )

    monkeypatch.setattr(
        profile_service,
        "pool",
        FakePool(profile_view_row(user_id=8)),
    )

    profile = profile_service.get_profile(
        current_user_id=7,
        target_user_id=8,
    )

    assert profile.user_id == 8
    assert profile.is_self is False
    assert profile.friendship_status == "none"


def test_get_profile_marks_sent_friend_request_pending(monkeypatch):
    install_fake_config_modules(monkeypatch)
    clear_profile_imports()

    profile_service = importlib.import_module(
        "app.service.profile"
    )

    monkeypatch.setattr(
        profile_service,
        "pool",
        FakePool(
            profile_view_row(
                user_id=8,
                requested_by=7,
                friendship_status="pending",
            )
        ),
    )

    profile = profile_service.get_profile(
        current_user_id=7,
        target_user_id=8,
    )

    assert profile.friendship_status == "pending_sent"


def test_get_profile_marks_received_friend_request_pending(monkeypatch):
    install_fake_config_modules(monkeypatch)
    clear_profile_imports()

    profile_service = importlib.import_module(
        "app.service.profile"
    )

    monkeypatch.setattr(
        profile_service,
        "pool",
        FakePool(
            profile_view_row(
                user_id=8,
                requested_by=8,
                friendship_status="pending",
            )
        ),
    )

    profile = profile_service.get_profile(
        current_user_id=7,
        target_user_id=8,
    )

    assert profile.friendship_status == "pending_received"


def test_get_profile_missing_row_fails(monkeypatch):
    install_fake_config_modules(monkeypatch)
    clear_profile_imports()

    profile_service = importlib.import_module(
        "app.service.profile"
    )

    monkeypatch.setattr(
        profile_service,
        "pool",
        FakePool(None),
    )

    with pytest.raises(
        LookupError,
        match="Profile not found.",
    ):
        profile_service.get_profile(
            current_user_id=7,
            target_user_id=999,
        )

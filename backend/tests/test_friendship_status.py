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


def clear_friend_imports():
    for module_name in [
        "app.service.friends",
    ]:
        sys.modules.pop(
            module_name,
            None,
        )


def import_friends_service(monkeypatch):
    install_fake_settings(monkeypatch)
    clear_friend_imports()

    return importlib.import_module(
        "app.service.friends"
    )


class FakeCursor:

    def __init__(
        self,
        rows,
    ):
        self.rows = rows
        self.query = None
        self.params = None


    def execute(
        self,
        query,
        params,
    ):
        self.query = query
        self.params = params


    def fetchall(self):
        return self.rows


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
        rows,
    ):
        self.cursor_instance = FakeCursor(
            rows
        )


    def connection(self):
        return FakeConnection(
            self.cursor_instance
        )


def suggestion_row(
    user_id,
    requested_by=None,
    friendship_status=None,
    looking_for="Networking",
    relationship_status="Single",
    current_looking_for="Networking",
    mutual_friend_count=0,
):
    return (
        user_id,
        "Chris",
        "Hughes",
        None,
        "Harvard University",
        "Student",
        "chughes",
        mutual_friend_count,
        looking_for,
        relationship_status,
        requested_by,
        friendship_status,
        current_looking_for,
    )


def test_friendship_status_for_view_uses_request_direction(monkeypatch):
    friends_service = import_friends_service(
        monkeypatch
    )

    assert (
        friends_service.friendship_status_for_view(
            current_user_id=7,
            requested_by=None,
            friendship_status=None,
        )
        == "none"
    )

    assert (
        friends_service.friendship_status_for_view(
            current_user_id=7,
            requested_by=7,
            friendship_status="pending",
        )
        == "pending_sent"
    )

    assert (
        friends_service.friendship_status_for_view(
            current_user_id=7,
            requested_by=8,
            friendship_status="pending",
        )
        == "pending_received"
    )

    assert (
        friends_service.friendship_status_for_view(
            current_user_id=7,
            requested_by=8,
            friendship_status="accepted",
        )
        == "accepted"
    )


def test_friend_suggestions_keep_pending_requests_visible(monkeypatch):
    friends_service = import_friends_service(
        monkeypatch
    )

    fake_pool = FakePool(
        [
            suggestion_row(
                user_id=8,
                requested_by=7,
                friendship_status="pending",
            ),
            suggestion_row(
                user_id=9,
            ),
        ]
    )

    monkeypatch.setattr(
        friends_service,
        "pool",
        fake_pool,
    )

    data = friends_service.get_friend_suggestions(
        current_user_id=7
    )

    pending_user = data["suggestions"][0]
    matching_user = data["suggestions"][1]

    assert data["count"] == 2
    assert pending_user["friendship_status"] == "pending_sent"
    assert pending_user["suggestion_reason"] == "Request pending"
    assert matching_user["friendship_status"] == "none"
    assert matching_user["suggestion_reason"] == (
        "Also looking for Networking"
    )

    normalized_query = " ".join(
        fake_pool.cursor_instance.query.split()
    )

    assert (
        "candidate_friendship.status <> 'accepted'"
        in normalized_query
    )
    assert len(fake_pool.cursor_instance.params) == 10

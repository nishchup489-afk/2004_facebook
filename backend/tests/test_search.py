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


def clear_search_imports():
    for module_name in [
        "app.service.search",
        "app.service.friends",
    ]:
        sys.modules.pop(
            module_name,
            None,
        )


def import_search_service(monkeypatch):
    install_fake_settings(monkeypatch)
    clear_search_imports()

    return importlib.import_module(
        "app.service.search"
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
        self.query = " ".join(
            query.split()
        )
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


def search_row(
    requested_by=7,
    friendship_status="pending",
):
    return (
        8,
        "Alex",
        "Carter",
        None,
        1,
        "Harvard University",
        "Student",
        "alex",
        "Networking",
        "Single",
        requested_by,
        friendship_status,
    )


def test_search_users_filters_profile_fields_and_friendship_state(monkeypatch):
    search_service = import_search_service(
        monkeypatch
    )

    fake_pool = FakePool(
        [
            search_row()
        ]
    )

    monkeypatch.setattr(
        search_service,
        "pool",
        fake_pool,
    )

    results = search_service.search_users(
        query="Alex",
        current_user_id=7,
        university_id=1,
        profile_status="Student",
        looking_for="Networking",
        relationship_status="Single",
    )

    assert results[0]["friendship_status"] == "pending_sent"
    assert results[0]["looking_for"] == "Networking"
    assert results[0]["relationship_status"] == "Single"

    cursor = fake_pool.cursor_instance

    assert "LOWER(p.looking_for)" in cursor.query
    assert "LOWER(p.relationship_status)" in cursor.query
    assert "LEFT JOIN friendships AS f" in cursor.query
    assert cursor.params == [
        7,
        7,
        "Alex%",
        "Alex%",
        1,
        "Student",
        "Networking",
        "Single",
        "Alex",
        50,
    ]


def test_search_users_empty_query_does_not_hit_database(monkeypatch):
    search_service = import_search_service(
        monkeypatch
    )

    assert search_service.search_users(
        query="   ",
        current_user_id=7,
    ) == []

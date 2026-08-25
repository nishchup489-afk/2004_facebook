import importlib
import sys
import types
from pathlib import Path


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
        "app.router.profile",
        "app.service.profile",
        "app.service.get_user_id",
    ]:
        sys.modules.pop(
            module_name,
            None,
        )


def test_profile_creation_route_imports(monkeypatch):
    install_fake_config_modules(monkeypatch)
    clear_profile_imports()

    from app.router.profile import create_profile_route

    assert callable(create_profile_route)


def test_profile_route_is_registered_on_app(monkeypatch):
    install_fake_config_modules(monkeypatch)
    clear_profile_imports()

    main = importlib.import_module("app.main")

    route_paths = set(
        main.app.openapi()["paths"]
    )

    assert "/profile" in route_paths

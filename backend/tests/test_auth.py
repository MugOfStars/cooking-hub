import pytest
from fastapi import Depends, FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.auth import PUBLIC_API_PATHS, require_auth, setup_auth
from app.config import Settings, settings
from app.main import app as real_app
from tests.conftest import TEST_PASSWORD


@pytest.fixture
def client():
    """An app with auth and one protected route. The cookie is Secure, so the client
    must use https, or it won't send the cookie back."""
    app = FastAPI()
    setup_auth(app)

    @app.get("/api/secret", dependencies=[Depends(require_auth)])
    def secret():
        return {"secret": True}

    return TestClient(app, base_url="https://testserver")


def log_in(client):
    return client.post("/api/auth/login", json={"password": TEST_PASSWORD})


def test_protected_route_rejects_anonymous(client):
    assert client.get("/api/secret").status_code == 401


def test_login_sets_hardened_session_cookie(client):
    response = log_in(client)

    assert response.status_code == 204
    cookie = response.headers["set-cookie"].lower()
    assert cookie.startswith("session=")
    for flag in ("httponly", "secure", "samesite=lax", "max-age=31536000"):
        assert flag in cookie
    assert client.get("/api/secret").json() == {"secret": True}
    assert client.get("/api/auth/me").json() == {"authenticated": True, "auth_enabled": True}


def test_wrong_password_rejected_without_cookie(client):
    response = client.post("/api/auth/login", json={"password": "wrong"})

    assert response.status_code == 401
    assert "set-cookie" not in response.headers
    assert client.get("/api/auth/me").json() == {"authenticated": False, "auth_enabled": True}


def test_logout_ends_session(client):
    log_in(client)

    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/secret").status_code == 401


def test_tampered_cookie_rejected(client):
    log_in(client)
    payload, _, signature = client.cookies["session"].rpartition(".")
    client.cookies.set("session", payload + "." + signature[::-1])

    assert client.get("/api/secret").status_code == 401


def test_auth_disabled_opens_protected_routes(client, monkeypatch):
    monkeypatch.setattr(settings, "auth_enabled", False)

    assert client.get("/api/secret").json() == {"secret": True}
    assert client.get("/api/auth/me").json() == {"authenticated": True, "auth_enabled": False}


@pytest.mark.parametrize(
    "overrides",
    [
        {"auth_password_hash": None},
        {"auth_password_hash": "plain-text-not-a-hash"},
        {"session_secret": None},
        {"session_secret": "too-short"},
    ],
)
def test_settings_fail_closed_when_auth_misconfigured(overrides):
    with pytest.raises(ValidationError):
        Settings(database_url="postgresql://u:p@h/db", auth_enabled=True, **overrides)


def test_settings_errors_do_not_echo_secrets():
    """Deploy logs are public, so a misconfiguration must not print secret values."""
    with pytest.raises(ValidationError) as excinfo:
        Settings(
            database_url="postgresql://u:db-password-SENTINEL@h/db",
            auth_enabled=True,
            auth_password_hash="not-a-hash-SENTINEL",
            session_secret="session-secret-SENTINEL-long-enough-to-pass",
        )
    assert "SENTINEL" not in str(excinfo.value)


def test_settings_allow_missing_secrets_when_auth_disabled():
    Settings(
        database_url="postgresql://u:p@h/db",
        auth_enabled=False,
        auth_password_hash=None,
        session_secret=None,
    )


def test_every_non_public_api_route_requires_auth():
    """Deny by default: a new route that forgets require_auth fails here, not in prod."""
    for route in real_app.routes:
        if not isinstance(route, APIRoute) or not route.path.startswith("/api"):
            continue
        if route.path in PUBLIC_API_PATHS:
            continue
        deps = {d.call for d in route.dependant.dependencies}
        assert require_auth in deps, f"{route.path} is missing require_auth"

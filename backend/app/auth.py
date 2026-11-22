from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import APIRouter, FastAPI, HTTPException, Request, status
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings

SESSION_MAX_AGE = 365 * 24 * 60 * 60  # one year, renewed on each request while logged in

# Reachable without logging in. tests/test_auth.py fails if any other /api route
# lacks the require_auth dependency.
PUBLIC_API_PATHS = {
    "/api/live",
    "/api/health",
    "/api/auth/login",
    "/api/auth/logout",
    "/api/auth/me",
}

_hasher = PasswordHasher()
router = APIRouter(prefix="/api/auth")


def setup_auth(app: FastAPI) -> None:
    """Add the signed session cookie and the login/logout routes to an app."""
    app.add_middleware(
        SessionMiddleware,
        # With auth off the session is never read, so no secret needs configuring.
        secret_key=settings.session_secret or "unused-because-auth-is-disabled",
        session_cookie="session",
        max_age=SESSION_MAX_AGE,
        same_site="lax",  # not sent on cross-site POSTs: this is the CSRF protection
        https_only=settings.cookie_secure,
    )
    app.include_router(router)


def require_auth(request: Request) -> None:
    """Dependency for every protected route: 401 unless the session cookie is valid."""
    if settings.auth_enabled and not request.session.get("authenticated"):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not logged in")


class LoginRequest(BaseModel):
    password: str


class AuthStatus(BaseModel):
    authenticated: bool
    auth_enabled: bool


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
def login(body: LoginRequest, request: Request) -> None:
    if not settings.auth_enabled:
        return
    try:
        _hasher.verify(settings.auth_password_hash, body.password)
    except VerifyMismatchError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong password") from None
    request.session["authenticated"] = True


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request) -> None:
    request.session.clear()  # the middleware then expires the cookie


@router.get("/me")
def me(request: Request) -> AuthStatus:
    """Lets the frontend decide whether to show the login screen."""
    return AuthStatus(
        authenticated=not settings.auth_enabled or bool(request.session.get("authenticated")),
        auth_enabled=settings.auth_enabled,
    )

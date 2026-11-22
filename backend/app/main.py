from typing import Annotated

from fastapi import Depends, FastAPI, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import get_db
from app.frontend import FRONTEND_DIST, mount_frontend

app = FastAPI(title="Cooking Hub API")


@app.get("/api/live")
def live() -> dict[str, str]:
    """Liveness: is the process up? Deliberately doesn't touch the database, so the
    host's frequent health checks don't keep a scale-to-zero database awake 24/7."""
    return {"status": "ok"}


@app.get("/api/health")
def health(response: Response, db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    """Report whether the API is up and can reach the database.

    Returns 503 (not 500) when the database is unreachable: the API itself is fine,
    but it can't serve requests, which is what load balancers and monitors look for.
    """
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "degraded", "database": "unreachable"}
    return {"status": "ok", "database": "ok"}


# Keep this last (see mount_frontend). In local development there's usually no build,
# and the Vite dev server serves the frontend instead, so this is skipped.
if FRONTEND_DIST.is_dir():
    mount_frontend(app, FRONTEND_DIST)

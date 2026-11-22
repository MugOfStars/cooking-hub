from typing import Annotated

from fastapi import Depends, FastAPI, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import get_db

app = FastAPI(title="Cooking Hub API")


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

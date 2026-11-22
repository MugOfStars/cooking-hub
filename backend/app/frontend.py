from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# In the repo and in the Docker image, the built frontend sits at <root>/frontend/dist.
FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"


def mount_frontend(app: FastAPI, dist: Path) -> None:
    """Serve the built React app from the same origin as the API.

    Must be called after all API routes are registered: the catch-all route below
    matches every path, so anything added after it would never be reached.
    """
    dist = dist.resolve()
    index = dist / "index.html"

    # Vite puts hashed JS/CSS bundles in assets/; serve them directly.
    app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str) -> FileResponse:
        # An unknown /api/... URL is a client bug. Return a real 404, not the HTML page.
        if path == "api" or path.startswith("api/"):
            raise HTTPException(status_code=404)
        # Top-level files from public/ (e.g. favicon.svg). The is_relative_to check
        # blocks path traversal (e.g. "../backend/...") from escaping dist/.
        file = (dist / path).resolve()
        if path and file.is_file() and file.is_relative_to(dist):
            return FileResponse(file)
        # Everything else is a client-side route (e.g. /recipes/42). React handles it.
        return FileResponse(index)

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.frontend import mount_frontend


@pytest.fixture
def client(tmp_path):
    """An app serving a fake frontend build, with one API route and a file outside dist."""
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<html>index</html>")
    (dist / "favicon.svg").write_text("<svg/>")
    (dist / "assets" / "app-abc123.js").write_text("console.log('app')")
    (tmp_path / "secret.txt").write_text("do not serve")

    app = FastAPI()

    @app.get("/api/ping")
    def ping():
        return {"pong": True}

    mount_frontend(app, dist)
    return TestClient(app)


def test_root_serves_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == "<html>index</html>"


def test_client_side_route_serves_index(client):
    response = client.get("/recipes/42")
    assert response.status_code == 200
    assert response.text == "<html>index</html>"


def test_serves_built_assets_and_public_files(client):
    assert client.get("/assets/app-abc123.js").text == "console.log('app')"
    assert client.get("/favicon.svg").text == "<svg/>"


def test_api_routes_take_priority(client):
    assert client.get("/api/ping").json() == {"pong": True}


def test_unknown_api_route_is_json_404_not_index(client):
    response = client.get("/api/nope")
    assert response.status_code == 404
    assert response.headers["content-type"] == "application/json"


def test_path_traversal_does_not_escape_dist(client):
    # %2e%2e is an encoded "..", so the HTTP client doesn't normalize it away first.
    response = client.get("/%2e%2e/secret.txt")
    assert "do not serve" not in response.text

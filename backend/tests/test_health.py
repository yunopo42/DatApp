from fastapi.testclient import TestClient

from app.main import app


def test_liveness_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_liveness_allows_configured_frontend_origin() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/health/live",
            headers={"Origin": "http://localhost:5173"},
        )

    assert response.headers["access-control-allow-origin"] == ("http://localhost:5173")

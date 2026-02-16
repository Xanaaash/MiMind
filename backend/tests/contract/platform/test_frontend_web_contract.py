from fastapi.testclient import TestClient

from web_app import app


def test_frontend_root_contract() -> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "id=\"registerForm\"" in response.text
    assert "id=\"coachForm\"" in response.text

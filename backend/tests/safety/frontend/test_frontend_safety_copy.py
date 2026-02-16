from fastapi.testclient import TestClient

from web_app import app


def test_frontend_safety_copy_visible() -> None:
    client = TestClient(app)

    response = client.get("/")
    script = client.get("/app.js")

    assert response.status_code == 200
    assert "非医疗" in response.text
    assert "危机热线" in response.text
    assert script.status_code == 200
    assert "988" in script.text


def test_frontend_avoids_diagnostic_claim_copy() -> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "你患有" not in response.text
    assert "处方药" not in response.text

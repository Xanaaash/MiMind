from fastapi.testclient import TestClient

from web_app import app


def test_frontend_root_serves_html() -> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "MiMind" in response.text


def test_frontend_contains_constitution_boundary_copy() -> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "非医疗" in response.text
    assert "不提供临床诊断" in response.text

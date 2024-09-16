from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healtz():
    response = client.get("/healtz")
    print(response.json())
    assert 200 == response.status_code
    assert {"status": "success", "message": "OK!"} == response.json()


# put devicezip invalid instance return 401

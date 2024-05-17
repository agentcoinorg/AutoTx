from fastapi.testclient import TestClient
from autotx import server
from autotx.server import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_create_task():
    server.setup_server(verbose=True, logs=None, max_rounds=None, cache=None)
    response = client.post("/api/v1/tasks", json={
        "prompt": "Send 1 ETH to vitalik.eth",
    })
    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert data["messages"] == []
    assert data["transactions"] == []
    assert data["running"] is True

    response = client.get(f"/api/v1/tasks/{data['id']}")
    data = response.json()

    assert data["running"] is False
    assert len(data["transactions"]) > 0

def test_get_tasks():
    response = client.get("/api/v1/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "id" in data[0]

def test_get_task():
    response = client.get("/api/v1/tasks")
    task_id = response.json()[0]["id"]
    
    response = client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert len(data["messages"]) > 0
    assert data["running"] is False

def test_get_task_transactions():
    response = client.get("/api/v1/tasks")
    task_id = response.json()[0]["id"]

    response = client.get(f"/api/v1/tasks/{task_id}/transactions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

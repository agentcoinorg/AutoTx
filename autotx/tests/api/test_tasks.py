import uuid
from fastapi.testclient import TestClient
import pytest
from autotx import db, server
from autotx.server import app
from fastapi.testclient import TestClient

from autotx.utils.ethereum.cached_safe_address import get_cached_safe_address

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup():
    db.clear_db()
    db.create_app("test", "1234")

def test_create_task_auth():
    smart_wallet_address = get_cached_safe_address()

    response = client.post("/api/v1/tasks", json={
        "prompt": "Send 1 ETH to vitalik.eth",
        "address": smart_wallet_address,
        "chain_id": 1,
        "user_id": "123"
    })
    assert response.status_code == 401

def test_get_tasks_auth():
    response = client.get("/api/v1/tasks")
    assert response.status_code == 401

def test_get_task_auth():
    response = client.get("/api/v1/tasks/123")
    assert response.status_code == 401

def test_get_task_transactions_auth():
    response = client.get("/api/v1/tasks/123/transactions")
    assert response.status_code == 401

def test_create_task():
    server.setup_server(verbose=True, logs=None, max_rounds=None, cache=False, is_dev=True, check_valid_safe=False)
    
    smart_wallet_address = get_cached_safe_address()
    user_id = uuid.uuid4().hex
   
    response = client.post("/api/v1/connect", json={
        "user_id": user_id,
    }, headers={
        "Authorization": f"Bearer 1234"
    })
    assert response.status_code == 200

    response = client.post("/api/v1/tasks", json={
        "prompt": "Send 1 ETH to vitalik.eth",
        "address": smart_wallet_address,
        "chain_id": 1,
        "user_id": user_id
    }, headers={
        "Authorization": f"Bearer 1234"
    })
    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert data["messages"] == []
    assert data["transactions"] == []
    assert data["running"] is True

    response = client.get(f"/api/v1/tasks/{data['id']}", headers={
        "Authorization": f"Bearer 1234"
    })
    data = response.json()

    assert data["running"] is False
    assert len(data["transactions"]) > 0

def test_get_tasks():
    response = client.get("/api/v1/tasks", headers={
        "Authorization": f"Bearer 1234"
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "id" in data[0]

def test_get_task():
    response = client.get("/api/v1/tasks", headers={
        "Authorization": f"Bearer 1234"
    })
    task_id = response.json()[0]["id"]
    
    response = client.get(f"/api/v1/tasks/{task_id}", headers={
        "Authorization": f"Bearer 1234"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert len(data["messages"]) > 0
    assert data["running"] is False

def test_get_task_transactions():
    response = client.get("/api/v1/tasks", headers={
        "Authorization": f"Bearer 1234"
    })
    task_id = response.json()[0]["id"]

    response = client.get(f"/api/v1/tasks/{task_id}/transactions", headers={
        "Authorization": f"Bearer 1234"
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

import uuid
from fastapi.testclient import TestClient
from autotx import db, server
from autotx.server import app
from fastapi.testclient import TestClient

from autotx.utils.ethereum.cached_safe_address import get_cached_safe_address

client = TestClient(app)

def test_send_transactions_auth():
    
    user_id = uuid.uuid4().hex

    response = client.post("/api/v1/tasks/123/transactions", json={
        "user_id": user_id,
        "address": "0x123",
        "chain_id": 1,
    })
    assert response.status_code == 401

def test_send_transactions():
    db.clear_db()
    db.create_app("test", "1234")
    server.setup_server(verbose=True, logs=None, max_rounds=None, cache=False, is_dev=True, check_valid_safe=False)

    user_id = uuid.uuid4().hex
    smart_wallet_address = get_cached_safe_address()
   
    response = client.post("/api/v1/connect", json={
        "user_id": user_id,
    }, headers={
        "Authorization": f"Bearer 1234"
    })
    assert response.status_code == 200
    data = response.json()

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

    task_id = data["id"]

    response = client.post(f"/api/v1/tasks/{task_id}/transactions", json={
        "user_id": user_id,
        "address": smart_wallet_address,
        "chain_id": 1,
    }, headers={
        "Authorization": f"Bearer 1234"
    })
    assert response.status_code == 200

    app = db.get_app_by_api_key("1234")

    batches = db.get_submitted_batches(app.id, task_id)

    assert len(batches) == 1
    assert batches[0].app_id == app.id
    assert batches[0].address == smart_wallet_address
    assert batches[0].chain_id == 1
    assert batches[0].task_id == task_id
    assert batches[0].created_at is not None

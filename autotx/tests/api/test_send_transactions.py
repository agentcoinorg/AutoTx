import uuid
from fastapi.testclient import TestClient
from autotx import db, server
from autotx.server import app
from fastapi.testclient import TestClient

from autotx.utils.ethereum.cached_safe_address import get_cached_safe_address

client = TestClient(app)

def test_get_intents_auth():
    response = client.get("/api/v1/tasks/123/intents")
    assert response.status_code == 401

def test_get_transactions_auth():
    
    user_id = uuid.uuid4().hex

    response = client.get("/api/v1/tasks/123/transactions", params={
        "user_id": user_id,
        "address": "0x123",
        "chain_id": 1,
    })
    assert response.status_code == 401

def test_prepare_transactions_auth():
    
    user_id = uuid.uuid4().hex

    response = client.post("/api/v1/tasks/123/transactions/prepare", params={
        "user_id": user_id,
        "address": "0x123",
        "chain_id": 1,
    })
    assert response.status_code == 401

def test_send_transactions_auth():
    
    user_id = uuid.uuid4().hex

    response = client.post("/api/v1/tasks/123/transactions", params={
        "user_id": user_id,
        "address": "0x123",
        "chain_id": 1,
        "batch_id": "123"
    })
    assert response.status_code == 401


def test_get_transactions():
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

    response = client.get(f"/api/v1/tasks/{task_id}/intents", headers={
        "Authorization": f"Bearer 1234"
    })
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1

    response = client.get(f"/api/v1/tasks/{task_id}/transactions", params={
        "user_id": user_id,
        "address": smart_wallet_address,
        "chain_id": 1,
    }, headers={
        "Authorization": f"Bearer 1234"
    })
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1

    response = client.get(f"/api/v1/tasks/{task_id}/transactions", params={
        "user_id": user_id,
        "address": smart_wallet_address,
        "chain_id": 2,
    }, headers={
        "Authorization": f"Bearer 1234"
    })
    assert response.status_code == 400

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

    response = client.post(f"/api/v1/tasks/{task_id}/transactions/prepare", params={
        "user_id": user_id,
        "address": smart_wallet_address,
        "chain_id": 2,
    }, headers={
        "Authorization": f"Bearer 1234"
    })
    assert response.status_code == 400

    response = client.post(f"/api/v1/tasks/{task_id}/transactions/prepare", params={
        "user_id": user_id,
        "address": smart_wallet_address,
        "chain_id": 1,
    }, headers={
        "Authorization": f"Bearer 1234"
    })
    assert response.status_code == 200
    batch1 = response.json()

    response = client.post(f"/api/v1/tasks/{task_id}/transactions/prepare", params={
        "user_id": user_id,
        "address": smart_wallet_address,
        "chain_id": 1,
    }, headers={
        "Authorization": f"Bearer 1234"
    })
    assert response.status_code == 200
    batch2 = response.json()

    app = db.get_app_by_api_key("1234")

    batches = db.get_submitted_batches(app.id, task_id)
    assert len(batches) == 2
    
    assert batches[0].app_id == app.id
    assert batches[0].address == smart_wallet_address
    assert batches[0].chain_id == 1
    assert batches[0].task_id == task_id
    assert batches[0].created_at is not None
    assert batches[0].submitted_on is None

    assert batches[1].app_id == app.id
    assert batches[1].address == smart_wallet_address
    assert batches[1].chain_id == 1
    assert batches[1].task_id == task_id
    assert batches[1].created_at is not None
    assert batches[1].submitted_on is None

    assert batch1["batch_id"] == batches[0].id
    assert len(batch1["transactions"]) == 1

    assert batch2["batch_id"] == batches[1].id
    assert len(batch2["transactions"]) == 1

    response = client.post(f"/api/v1/tasks/{task_id}/transactions", params={
        "user_id": user_id,
        "address": smart_wallet_address,
        "chain_id": 2,
        "batch_id": batch1["batch_id"]
    }, headers={
        "Authorization": f"Bearer 1234"
    })
    assert response.status_code == 400

    response = client.post(f"/api/v1/tasks/{task_id}/transactions", params={
        "user_id": user_id,
        "address": smart_wallet_address,
        "chain_id": 1,
        "batch_id": batch1["batch_id"]
    }, headers={
        "Authorization": f"Bearer 1234"
    })
    assert response.status_code == 200

    batches = db.get_submitted_batches(app.id, task_id)
    batches = sorted(batches, key=lambda x: x.created_at)
    assert len(batches) == 2
    assert batches[0].submitted_on is not None
    assert batches[1].submitted_on is None

    response = client.post(f"/api/v1/tasks/{task_id}/transactions", params={
        "user_id": user_id,
        "address": smart_wallet_address,
        "chain_id": 1,
        "batch_id": batch2["batch_id"]
    }, headers={
        "Authorization": f"Bearer 1234"
    })
    assert response.status_code == 200

    batches = db.get_submitted_batches(app.id, task_id)
    assert len(batches) == 2
    assert batches[0].submitted_on is not None
    assert batches[1].submitted_on is not None

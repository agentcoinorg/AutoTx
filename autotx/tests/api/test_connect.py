import uuid
from fastapi.testclient import TestClient
import pytest
from web3 import Web3
from autotx import db, server
from autotx.server import app
from fastapi.testclient import TestClient

client = TestClient(app)

@pytest.fixture
def setup():
    db.clear_db()
    db.create_app("test", "1234")
    server.setup_server(verbose=True, logs=None, max_rounds=None, cache=False, is_dev=False, check_valid_safe=False)

def test_connect_auth(setup):
    
    user_id = uuid.uuid4().hex

    response = client.post("/api/v1/connect", json={
        "user_id": user_id,
    })
    assert response.status_code == 401

def test_connect(setup):
    user_id = uuid.uuid4().hex
   
    response = client.post("/api/v1/connect", json={
        "user_id": user_id,
    }, headers={
        "Authorization": f"Bearer 1234"
    })
    assert response.status_code == 200
    data = response.json()

    assert "user_id" in data
    assert "agent_address" in data
    assert "created_at" in data

    assert data["user_id"] == user_id
    assert Web3.is_address(data["agent_address"])

    response2 = client.post("/api/v1/connect", json={
        "user_id": user_id,
    }, headers={
        "Authorization": f"Bearer 1234"
    })
    assert response2.status_code == 200
    data2 = response2.json()

    assert "user_id" in data2
    assert "agent_address" in data2
    assert "created_at" in data2

    assert data2["user_id"] == user_id
    assert Web3.is_address(data2["agent_address"])
    assert data2["agent_address"] == data["agent_address"]


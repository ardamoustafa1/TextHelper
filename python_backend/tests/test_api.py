import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test the /health endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert "transformer_loaded" in data
    assert "elasticsearch_available" in data

def test_process_text_simple():
    """Test basic text processing."""
    payload = {
        "text": "merhaba",
        "context": "",
        "max_suggestions": 5
    }
    response = client.post("/api/v1/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert isinstance(data["suggestions"], list)
    assert len(data["suggestions"]) > 0

def test_process_text_empty():
    """Test processing empty text."""
    payload = {
        "text": "",
        "context": ""
    }
    response = client.post("/api/v1/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["suggestions"]) == 0

def test_learn_endpoint():
    """Test the learning endpoint."""
    payload = {
        "text": "yeni öğrenilecek veri"
    }
    response = client.post("/api/v1/learn", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_websocket_connection():
    """Test WebSocket connection."""
    with client.websocket_connect("/api/v1/ws") as websocket:
        data = {"text": "merhaba"}
        websocket.send_json(data)
        response = websocket.receive_json()
        assert "suggestions" in response
        assert isinstance(response["suggestions"], list)

# ---------------------------------------------------------
# Test Cases for IVR Backend (Milestone 4)
# This file contains unit and integration tests for
# validating API endpoints and IVR flow functionality.
# ---------------------------------------------------------
from fastapi.testclient import TestClient
from backend_ivr import app

# Create test client for FastAPI app
client = TestClient(app)

# Test if root endpoint is working
def test_root():
    response = client.get("/")
    assert response.status_code == 200

# Test if call session starts successfully
def test_start_call():
    response = client.post("/start-call", json={
        "caller_name": "TestUser"
    })
    assert response.status_code == 200

# Test menu option 1 (Lab Report Status flow)
def test_handle_menu_option_1():
    # Start a call session first
    start = client.post("/start-call", json={
        "caller_name": "TestUser"
    })

    session_id = start.json().get("session_id")

    # Send menu input
    response = client.post("/handle-menu", json={
        "session_id": session_id,
        "user_input": "1"
    })

    assert response.status_code == 200

# Test conversational flow (Milestone 3 integration)
def test_converse_flow():
    start = client.post("/start-call", json={
        "caller_name": "TestUser"
    })

    session_id = start.json().get("session_id")

    response = client.post("/converse", params={
        "session_id": session_id,
        "user_text": "check lab report"
    })

    assert response.status_code == 200


# Test handling of invalid session/input
def test_invalid_input():
    response = client.post("/converse", params={
        "session_id": "invalid",
        "user_text": "random text"
    })

    assert response.status_code == 200

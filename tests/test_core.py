import pytest
import threading
import zmq
import json
import time
from jupdb import JuPDb

@pytest.fixture
def debugger():
    return JuPDb(port=5556)  # Use different port for testing

def test_debugger_initialization(debugger):
    assert debugger.port == 5556
    assert debugger.running is False
    assert debugger.debug_frame is None

def test_set_trace_captures_frame(debugger):
    def test_frame():
        with pytest.raises(RuntimeError):
            debugger.set_trace()

    t = threading.Thread(target=test_frame)
    t.start()
    time.sleep(0.1)

    assert debugger.debug_frame is not None
    assert debugger.running is True

    debugger.running = False
    t.join()

def test_zmq_communication(debugger):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5556")

    def run_debugger():
        debugger.set_trace()

    t = threading.Thread(target=run_debugger)
    t.start()
    time.sleep(0.2)

    # Test eval command
    socket.send_string(json.dumps({"command": "eval", "code": "10+20"}))
    response = json.loads(socket.recv_string())
    assert response["result"] == "30"

    # Test continue command
    socket.send_string(json.dumps({"command": "continue"}))
    response = json.loads(socket.recv_string())
    assert response["status"] == "resuming"

    t.join()
    context.term()

def test_variable_synchronization(debugger):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5556")

    test_vars = {"x": 10}

    def test_frame():
        debugger.set_trace()
        # After debugger continues
        assert test_vars["x"] == 42

    t = threading.Thread(target=test_frame, kwargs=test_vars)
    t.start()
    time.sleep(0.2)

    # Modify variable
    socket.send_string(json.dumps({
        "command": "eval",
        "code": "x = 42"
    }))
    response = json.loads(socket.recv_string())
    assert response["result"] == "executed"

    # Continue execution
    socket.send_string(json.dumps({"command": "continue"}))
    t.join()
    context.term()
    

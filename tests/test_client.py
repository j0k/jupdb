import pytest
import threading
import time
from jupdb import JuPDb
from jupdb.client import debug_eval, debug_continue

@pytest.fixture
def debug_server(zmq_context):
    port = 5557
    server = JuPDb(port=port)
    server_thread = threading.Thread(target=server.set_trace)
    server_thread.start()

    # Wait for server to start
    start_time = time.time()
    while True:
        try:
            socket = zmq_context.socket(zmq.REQ)
            socket.connect(f"tcp://localhost:{port}")
            socket.send_string('{"command": "ping"}')
            socket.close()
            break
        except zmq.ZMQError:
            if time.time() - start_time > 5:
                raise TimeoutError("Debug server failed to start")
            time.sleep(0.1)

    yield port

    # Cleanup
    debug_continue(port=port)
    server_thread.join(timeout=2)
    if server_thread.is_alive():
        server.running = False

def test_client_connection(debug_server):
    port = debug_server
    response = debug_eval("10+20", port=port)
    assert response["result"] == "30", f"Unexpected response: {response}"

    response = debug_continue(port=port)
    assert response["status"] == "resuming"

def test_variable_manipulation(debug_server):
    port = debug_server
    debug_eval("x = 42", port=port)
    response = debug_eval("x", port=port)
    assert response["result"] == "42", "Variable not updated"
    debug_continue(port=port)

def test_error_handling(debug_server):
    port = debug_server
    # Test syntax error
    response = debug_eval("invalid syntax", port=port)
    assert "error" in response, "Should return error for invalid code"

    # Test runtime error
    response = debug_eval("1/0", port=port)
    assert "error" in response, "Should return error for division by zero"

    debug_continue(port=port)

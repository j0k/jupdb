import zmq
from json import loads, dumps

class JuPDbClient:
    def __init__(self, port=5555):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://localhost:{port}")

    def eval(self, code):
        self.socket.send_string(dumps({"command": "eval", "code": code}))
        return loads(self.socket.recv_string())

    def cont(self):
        self.socket.send_string(dumps({"command": "continue"}))
        return loads(self.socket.recv_string())

# Shortcut functions
def debug_eval(code, port=5555):
    return JuPDbClient(port).eval(code)

def debug_continue(port=5555):
    return JuPDbClient(port).cont()

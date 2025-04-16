import sys
import inspect
import zmq
from threading import Thread, Event
from json import dumps, loads

class JuPDb:
    def __init__(self, port=5555):
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{self.port}")
        self.debug_frame = None
        self.running = False
        self.event = Event()

    def set_trace(self):
        self.debug_frame = inspect.currentframe().f_back
        self.running = True
        Thread(target=self.debug_loop).start()
        self.event.wait()

    def debug_loop(self):
        try:
            while self.running:
                msg = loads(self.socket.recv_string())

                if msg["command"] == "eval":
                    response = self._handle_eval(msg["code"])
                elif msg["command"] == "continue":
                    self.running = False
                    response = {"status": "resuming"}
                    self.event.set()
                else:
                    response = {"error": "Unknown command"}

                self.socket.send_string(dumps(response))
        finally:
            self.socket.close()
            self.context.term()

    def _handle_eval(self, code):
        try:
            result = eval(code, self.debug_frame.f_globals, self.debug_frame.f_locals)
            return {"result": str(result)}
        except SyntaxError:
            try:
                exec(code, self.debug_frame.f_globals, self.debug_frame.f_locals)
                self._sync_locals()
                return {"result": "executed"}
            except Exception as e:
                return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    def _sync_locals(self):
        try:
            import ctypes
            ctypes.pythonapi.PyFrame_LocalsToFast(
                ctypes.py_object(self.debug_frame),
                ctypes.c_int(1))
        except:
            pass

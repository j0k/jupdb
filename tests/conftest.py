import pytest
import zmq

@pytest.fixture(scope="session")
def zmq_context():
    context = zmq.Context()
    yield context
    context.term()

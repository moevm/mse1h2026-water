from fastapi.testclient import TestClient
from back.routers import methods

client = TestClient(methods.app)

def build_eutrophication_stub(response):
    called = {"count": 0, "args": None, "kwargs": None}

    def stub(*args, **kwargs):
        called["count"] += 1
        called["args"] = args
        called["kwargs"] = kwargs
        return response

    return called, stub
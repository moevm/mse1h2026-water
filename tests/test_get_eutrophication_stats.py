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

def test_get_eutrophication_stats_returns_payload(monkeypatch):
    expected = {
        "coordinates": {"lon": 30.27, "lat": 59.96},
        "ndci_mean": 0.05,
        "total_water_area_m2": 1000.0,
        "polluted_area_m2": 100.0,
        "polluted_percentage": 10.0,
        "date_analyzed": "S2A_MSIL2A_20250715",
        "calculated_at": "2025-07-20T12:00:00",
    }

    called, stub = build_eutrophication_stub(expected)
    monkeypatch.setattr(methods, "initialize_ee", lambda: None)
    monkeypatch.setattr(
        methods.calculate_ndci, "get_eutrophication_stats", stub
    )

    response = client.get(
        "/methods/get_eutrophication_stats",
        params={
            "lat": 59.96,
            "lon": 30.27,
            "buffer_km": 4.0,
            "start_date": "2025-07-01",
            "end_date": "2025-09-01",
            "ndci_threshold": 0.12,
        },
    )

    assert response.status_code == 200
    assert response.json() == expected
    assert called["args"] == (30.27, 59.96, 4.0, "2025-07-01", "2025-09-01", 0.12)
    assert called["count"] == 1


def test_get_eutrophication_stats_default_params(monkeypatch):
    called, stub = build_eutrophication_stub({"ok": True})
    monkeypatch.setattr(methods, "initialize_ee", lambda: None)
    monkeypatch.setattr(
        methods.calculate_ndci, "get_eutrophication_stats", stub
    )

    response = client.get("/methods/get_eutrophication_stats")

    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert called["args"] == (
        30.314997,
        59.938784,
        6.0,
        "2025-06-01",
        "2025-08-31",
        0.1,
    )

def test_get_eutrophication_stats_invalid_latitude(monkeypatch):
    called, stub = build_eutrophication_stub(None)
    monkeypatch.setattr(methods, "initialize_ee", lambda: None)
    monkeypatch.setattr(
        methods.calculate_ndci, "get_eutrophication_stats", stub
    )

    response = client.get(
        "/methods/get_eutrophication_stats",
        params={"lat": 100, "lon": 30.27},
    )

    assert response.status_code == 422
    assert called["count"] == 0


def test_get_eutrophication_stats_invalid_longitude(monkeypatch):
    called, stub = build_eutrophication_stub(None)
    monkeypatch.setattr(methods, "initialize_ee", lambda: None)
    monkeypatch.setattr(
        methods.calculate_ndci, "get_eutrophication_stats", stub
    )

    response = client.get(
        "/methods/get_eutrophication_stats",
        params={"lat": 59.96, "lon": 200},
    )

    assert response.status_code == 422
    assert called["count"] == 0


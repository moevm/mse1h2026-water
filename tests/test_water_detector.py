from fastapi.testclient import TestClient

from back.routers import methods


client = TestClient(methods.app)


def build_water_type_stub(response):
    called = {"count": 0, "args": None}

    def stub_get_water_type_from_open_data(lat, lon, radius):
        called["count"] += 1
        called["args"] = (lat, lon, radius)
        return response

    return called, stub_get_water_type_from_open_data


def test_water_detector_payload_from_service(monkeypatch):
    expected_payload = {
        "coordinates": {"lat": 59.96, "lon": 30.27},
        "source": "OpenStreetMap",
        "water_type": "river",
        "water_name": "Malaya Nevka",
        "raw_tags": {"waterway": "river", "name": "Malaya Nevka"},
    }

    called, stub_get_water_type_from_open_data = build_water_type_stub(expected_payload)

    monkeypatch.setattr(
        methods.water_detector,
        "get_water_type_from_open_data",
        stub_get_water_type_from_open_data,
    )

    response = client.get(
        "/methods/water_detector",
        params={"lat": 59.96, "lon": 30.27, "radius": 80},
    )

    assert response.status_code == 200
    assert response.json() == expected_payload
    assert called["args"] == (59.96, 30.27, 80)


def test_water_detector_default_params(monkeypatch):
    called, stub_get_water_type_from_open_data = build_water_type_stub({"ok": True})

    monkeypatch.setattr(
        methods.water_detector,
        "get_water_type_from_open_data",
        stub_get_water_type_from_open_data,
    )

    response = client.get("/methods/water_detector")

    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert called["args"] == (59.938784, 30.314997, 50)


def test_water_detector_invalid_latitude(monkeypatch):
    called, stub_get_water_type_from_open_data = build_water_type_stub({"ok": True})

    monkeypatch.setattr(
        methods.water_detector,
        "get_water_type_from_open_data",
        stub_get_water_type_from_open_data,
    )

    response = client.get("/methods/water_detector", params={"lat": 100, "lon": 30.27})

    assert response.status_code == 422
    assert called["count"] == 0


def test_water_detector_non_integer_radius(monkeypatch):
    called, stub_get_water_type_from_open_data = build_water_type_stub({"ok": True})

    monkeypatch.setattr(
        methods.water_detector,
        "get_water_type_from_open_data",
        stub_get_water_type_from_open_data,
    )

    response = client.get(
        "/methods/water_detector",
        params={"lat": 59.96, "lon": 30.27, "radius": "abc"},
    )

    assert response.status_code == 422
    assert called["count"] == 0

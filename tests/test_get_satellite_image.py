from fastapi.testclient import TestClient
from back.routers import methods

client = TestClient(methods.app)


def build_satellite_stub(response):
    called = {"count": 0, "args": None}

    def stub(lon, lat, buffer_km, start_date, end_date):
        called["count"] += 1
        called["args"] = (lon, lat, buffer_km, start_date, end_date)
        return None, None, "fake-url", response

    return called, stub


def test_get_satellite_image_returns_metadata(monkeypatch):
    expected_metadata = {
        "image_id": "IMG_1",
        "satellite": "Sentinel-2",
        "collection": "COPERNICUS/S2_SR_HARMONIZED",
        "acquisition_date": "2025-08-01",
        "cloud_percentage": 10,
        "coordinates_center": {"longitude": 30.27, "latitude": 59.96},
        "buffer_km": 6.0,
        "date_range": {"start": "2025-06-01", "end": "2025-08-31"},
        "thumbnail_url": "http://test",
        "bands_used": ["B4", "B3", "B2", "B8", "B11"],
        "created_at": "2025-01-01T00:00:00",
    }

    called, stub = build_satellite_stub(expected_metadata)

    monkeypatch.setattr(methods, "initialize_ee", lambda: None)
    monkeypatch.setattr(
        methods.download_images,
        "get_satellite_image",
        stub
    )

    response = client.get(
        "/methods/get_satellite_image",
        params={"lat": 59.96, "lon": 30.27},
    )

    assert response.status_code == 200
    assert response.json() == expected_metadata
    assert called["args"] == (30.27, 59.96, 6.0, "2025-06-01", "2025-08-31")
    assert called["count"] == 1

def test_get_satellite_image_defaults(monkeypatch):
    called, stub = build_satellite_stub({"ok": True})

    monkeypatch.setattr(methods, "initialize_ee", lambda: None)
    monkeypatch.setattr(methods.download_images, "get_satellite_image", stub)

    response = client.get("/methods/get_satellite_image")

    assert response.status_code == 200
    assert response.json() == {"ok": True}

    assert called["args"] == (
        30.314997,
        59.938784,
        6.0,
        "2025-06-01",
        "2025-08-31",
    )

def test_get_satellite_image_invalid_lat(monkeypatch):
    called, stub = build_satellite_stub({"ok": True})

    monkeypatch.setattr(methods, "initialize_ee", lambda: None)
    monkeypatch.setattr(methods.download_images, "get_satellite_image", stub)

    response = client.get(
        "/methods/get_satellite_image",
        params={"lat": 100, "lon": 30},
    )

    assert response.status_code == 422
    assert called["count"] == 0

def test_get_satellite_image_invalid_lon(monkeypatch):
    called, stub = build_satellite_stub({"ok": True})

    monkeypatch.setattr(methods, "initialize_ee", lambda: None)
    monkeypatch.setattr(methods.download_images, "get_satellite_image", stub)

    response = client.get(
        "/methods/get_satellite_image",
        params={"lat": 50, "lon": 200},
    )

    assert response.status_code == 422
    assert called["count"] == 0


def test_get_satellite_image_calls_initialize_ee(monkeypatch):
    ee_calls = {"n": 0}

    def track_ee():
        ee_calls["n"] += 1

    called, stub = build_satellite_stub({"ok": True})

    monkeypatch.setattr(methods, "initialize_ee", track_ee)
    monkeypatch.setattr(methods.download_images, "get_satellite_image", stub)

    response = client.get("/methods/get_satellite_image")

    assert response.status_code == 200
    assert ee_calls["n"] == 1
    assert called["count"] == 1
from fastapi.testclient import TestClient
from back import app  

client = TestClient(app.app)


def build_stub(response):
    called = {"count": 0, "args": None, "kwargs": None}

    def stub(*args, **kwargs):
        called["count"] += 1
        called["args"] = args
        called["kwargs"] = kwargs
        return response

    return called, stub


def build_async_stub(response):
    called = {"count": 0, "args": None, "kwargs": None}

    async def stub(*args, **kwargs):
        called["count"] += 1
        called["args"] = args
        called["kwargs"] = kwargs
        return response

    return called, stub


def test_get_water_info_success(monkeypatch, tmp_path):
    fake_image = object()
    fake_region = object()
    fake_url = "http://image.url/thumb.png"

    geojson_path = tmp_path / "test.geojson"
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"id": 1, "type": "озеро", "area_pixels": 5000},
                "geometry": {"type": "Polygon", "coordinates": [[]]},
            },
            {
                "type": "Feature",
                "properties": {"id": 2, "type": "река", "area_pixels": 1500},
                "geometry": {"type": "Polygon", "coordinates": [[]]},
            },
        ],
    }

    classifier_result = {
        "image_path": "img/classified/test.png",
        "geojson_path": str(geojson_path),
        "geojson_data": geojson_data,
    }

    eutro_result = {"ndci_mean": 0.35, "polluted_percentage": 22.5}

    ee_called = {"n": 0}

    def track_ee():
        ee_called["n"] += 1

    download_called, download_stub = build_stub(
        (fake_image, fake_region, fake_url, {})
    )

    classify_called, classify_stub = build_async_stub(classifier_result)

    eutro_called, eutro_stub = build_stub(eutro_result)

    monkeypatch.setattr(app.methods, "initialize_ee", track_ee)
    monkeypatch.setattr(
        app.methods.download_images,
        "get_satellite_image",
        download_stub,
    )
    monkeypatch.setattr(
        app.integrated_water_classifiers,
        "cv_integrated_water_classifier",
        classify_stub,
    )
    monkeypatch.setattr(
        app.calculate_ndci,
        "get_eutrophication_stats",
        eutro_stub,
    )

    response = client.get(
        "/water-info",
        params={
            "lat": 59.93,
            "lon": 30.31,
            "buffer_km": 5.0,
            "start_date": "2025-06-01",
            "end_date": "2025-08-31",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "image_path" in data
    assert "geojson_path" in data
    assert "eutrophication_stats" in data
    assert "risk_interpretation" in data

    assert data["image_path"].startswith("http")
    assert data["geojson_path"].startswith("http")

    risk = data["risk_interpretation"]
    assert risk["dominant_type"] == "озеро"
    assert risk["primary"]["water_type"] == "озеро"
    assert set(risk["by_type"].keys()) == {"озеро", "река"}

    assert ee_called["n"] == 1
    assert download_called["count"] == 1
    assert classify_called["count"] == 1
    assert eutro_called["count"] == 1


def test_get_water_info_default_params(monkeypatch, tmp_path):
    fake_image = object()
    fake_region = object()
    fake_url = "http://image.url/thumb.png"

    geojson_path = tmp_path / "test.geojson"
    classifier_result = {
        "image_path": "img/classified/test.png",
        "geojson_path": str(geojson_path),
        "geojson_data": {"type": "FeatureCollection", "features": []},
    }

    eutro_result = {"ndci_mean": 0.0, "polluted_percentage": 0.0}

    download_called, download_stub = build_stub(
        (fake_image, fake_region, fake_url, {})
    )
    classify_called, classify_stub = build_async_stub(classifier_result)
    eutro_called, eutro_stub = build_stub(eutro_result)

    monkeypatch.setattr(app.methods, "initialize_ee", lambda: None)
    monkeypatch.setattr(
        app.methods.download_images,
        "get_satellite_image",
        download_stub,
    )
    monkeypatch.setattr(
        app.integrated_water_classifiers,
        "cv_integrated_water_classifier",
        classify_stub,
    )
    monkeypatch.setattr(
        app.calculate_ndci,
        "get_eutrophication_stats",
        eutro_stub,
    )

    response = client.get("/water-info")

    assert response.status_code == 200

    assert download_called["args"] == (
        30.314997,
        59.938784,
        6.0,
        "2025-06-01",
        "2025-08-31",
    )

    assert eutro_called["args"] == (
        30.314997,
        59.938784,
        6.0,
        "2025-06-01",
        "2025-08-31",
    )

    assert classify_called["count"] == 1

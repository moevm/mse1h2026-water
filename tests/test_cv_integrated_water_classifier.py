from fastapi.testclient import TestClient
from back.routers import methods

client = TestClient(methods.app)


def build_cv_stub(response):
    called = {"count": 0, "args": None, "kwargs": None}

    async def stub(*args, **kwargs):
        called["count"] += 1
        called["args"] = args
        called["kwargs"] = kwargs
        return response

    return called, stub


def build_download_stub():
    called = {"count": 0, "args": None}

    def stub(lon, lat, buffer_km, start_date, end_date, tif_file=None):
        called["count"] += 1
        called["args"] = (lon, lat, buffer_km, start_date, end_date)

        return "fake-image", "fake-region", "fake-url", {}

    return called, stub


def test_cv_classifier_success(monkeypatch):
    expected = {
        "image_path": "img/test.png",
        "geojson_path": "geojson/test.geojson"
    }

    cv_called, cv_stub = build_cv_stub(expected)
    dl_called, dl_stub = build_download_stub()

    monkeypatch.setattr(methods, "initialize_ee", lambda: None)
    monkeypatch.setattr(methods.download_images, "get_satellite_image", dl_stub)
    monkeypatch.setattr(
        methods.integrated_water_classifiers,
        "cv_integrated_water_classifier",
        cv_stub
    )

    payload = {
        "image_id": "id",
        "satellite": "Sentinel-2",
        "collection": "COPERNICUS",
        "acquisition_date": "2025",
        "cloud_percentage": 10,
        "coordinates_center": {"longitude": 30.27, "latitude": 59.96},
        "buffer_km": 6.0,
        "date_range": {"start": "2025-06-01", "end": "2025-08-31"},
        "thumbnail_url": "http://test",
        "bands_used": [],
        "created_at": "2025"
    }

    response = client.post("/methods/cv_integrated_water_classifier", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["image_path"].startswith("http://testserver/")
    assert data["geojson_path"].startswith("http://testserver/")

    assert cv_called["count"] == 1
    assert dl_called["count"] == 1


def test_cv_classifier_calls_download_correct(monkeypatch):
    cv_called, cv_stub = build_cv_stub({"results": [], "image_path": "a", "geojson_path": "b"})
    dl_called, dl_stub = build_download_stub()

    monkeypatch.setattr(methods, "initialize_ee", lambda: None)
    monkeypatch.setattr(methods.download_images, "get_satellite_image", dl_stub)
    monkeypatch.setattr(
        methods.integrated_water_classifiers,
        "cv_integrated_water_classifier",
        cv_stub
    )

    payload = {
        "image_id": "id",
        "satellite": "Sentinel-2",
        "collection": "COPERNICUS",
        "acquisition_date": "2025",
        "cloud_percentage": 10,
        "coordinates_center": {"longitude": 10, "latitude": 20},
        "buffer_km": 5,
        "date_range": {"start": "A", "end": "B"},
        "thumbnail_url": "url",
        "bands_used": [],
        "created_at": "2025"
    }

    client.post("/methods/cv_integrated_water_classifier", json=payload)

    assert dl_called["args"] == (10, 20, 5, "A", "B")


def test_cv_classifier_invalid_payload():
    response = client.post("/methods/cv_integrated_water_classifier", json={})

    assert response.status_code == 422

def test_cv_classifier_passes_download_result_to_classifier(monkeypatch):
    cv_called, cv_stub = build_cv_stub({"results": [], "annotated_url": "a",
                                        "geojson_path": "b", "image_path": "img/test.png"})

    def dl_stub(lon, lat, buffer_km, start_date, end_date, tif_file=None):
        return "image-from-download", "region-from-download", "url-from-download", {}

    monkeypatch.setattr(methods, "initialize_ee", lambda: None)
    monkeypatch.setattr(methods.download_images, "get_satellite_image", dl_stub)
    monkeypatch.setattr(
        methods.integrated_water_classifiers,
        "cv_integrated_water_classifier",
        cv_stub
    )

    payload = {
        "image_id": "id",
        "satellite": "Sentinel-2",
        "collection": "COPERNICUS",
        "acquisition_date": "2025",
        "cloud_percentage": 10,
        "coordinates_center": {"longitude": 30.27, "latitude": 59.96},
        "buffer_km": 6.0,
        "date_range": {"start": "2025-06-01", "end": "2025-08-31"},
        "thumbnail_url": "http://test",
        "bands_used": [],
        "created_at": "2025"
    }

    response = client.post("/methods/cv_integrated_water_classifier", json=payload)

    assert response.status_code == 200
    assert cv_called["count"] == 1
    assert cv_called["args"] == (
        "image-from-download",
        "region-from-download",
        "url-from-download",
        {}
    )

def test_cv_classifier_does_not_call_classifier_when_download_fails(monkeypatch):
    cv_called, cv_stub = build_cv_stub({"results": [], "annotated_url": "a", "geojson_path": "b"})

    def dl_stub(lon, lat, buffer_km, start_date, end_date, tif_file=None):
        raise RuntimeError("download failed")

    monkeypatch.setattr(methods, "initialize_ee", lambda: None)
    monkeypatch.setattr(methods.download_images, "get_satellite_image", dl_stub)
    monkeypatch.setattr(
        methods.integrated_water_classifiers,
        "cv_integrated_water_classifier",
        cv_stub
    )

    payload = {
        "image_id": "id",
        "satellite": "Sentinel-2",
        "collection": "COPERNICUS",
        "acquisition_date": "2025",
        "cloud_percentage": 10,
        "coordinates_center": {"longitude": 30.27, "latitude": 59.96},
        "buffer_km": 6.0,
        "date_range": {"start": "2025-06-01", "end": "2025-08-31"},
        "thumbnail_url": "http://test",
        "bands_used": [],
        "created_at": "2025"
    }

    try:
        client.post("/methods/cv_integrated_water_classifier", json=payload)
    except RuntimeError:
        pass

    assert cv_called["count"] == 0

def test_cv_classifier_download_called_before_classifier(monkeypatch):
    order = []

    def dl_stub(lon, lat, buffer_km, start_date, end_date, tif_file=None):
        order.append("download")
        return "image", "region", "url", {"smth":"data"}

    async def cv_stub(image, region, url, metadata):
        order.append("classifier")
        return {"results": [], "annotated_url": "a", "geojson_path": "b","image_path":"img/test.png"}

    monkeypatch.setattr(methods, "initialize_ee", lambda: None)
    monkeypatch.setattr(methods.download_images, "get_satellite_image", dl_stub)
    monkeypatch.setattr(
        methods.integrated_water_classifiers,
        "cv_integrated_water_classifier",
        cv_stub
    )

    payload = {
        "image_id": "id",
        "satellite": "Sentinel-2",
        "collection": "COPERNICUS",
        "acquisition_date": "2025",
        "cloud_percentage": 10,
        "coordinates_center": {"longitude": 30.27, "latitude": 59.96},
        "buffer_km": 6.0,
        "date_range": {"start": "2025-06-01", "end": "2025-08-31"},
        "thumbnail_url": "http://test",
        "bands_used": [],
        "created_at": "2025"
    }

    response = client.post("/methods/cv_integrated_water_classifier", json=payload)

    assert response.status_code == 200
    assert order == ["download", "classifier"]

def test_cv_classifier_calls_initialize_ee(monkeypatch):
    ee_calls = {"n": 0}

    def track():
        ee_calls["n"] += 1

    cv_called, cv_stub = build_cv_stub({"results": [], "image_path": "a", "geojson_path": "b"})
    dl_called, dl_stub = build_download_stub()

    monkeypatch.setattr(methods, "initialize_ee", track)
    monkeypatch.setattr(methods.download_images, "get_satellite_image", dl_stub)
    monkeypatch.setattr(
        methods.integrated_water_classifiers,
        "cv_integrated_water_classifier",
        cv_stub
    )

    payload = {
        "image_id": "id",
        "satellite": "Sentinel-2",
        "collection": "COPERNICUS",
        "acquisition_date": "2025",
        "cloud_percentage": 10,
        "coordinates_center": {"longitude": 1, "latitude": 2},
        "buffer_km": 6,
        "date_range": {"start": "s", "end": "e"},
        "thumbnail_url": "url",
        "bands_used": [],
        "created_at": "2025"
    }

    response = client.post("/methods/cv_integrated_water_classifier", json=payload)

    assert response.status_code == 200
    assert ee_calls["n"] == 1
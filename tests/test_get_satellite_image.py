from back.model.download_images import build_metadata
from back.model.download_images import select_image
from back.model.download_images import build_thumbnail
import json
from back.model.download_images import save_metadata
import back.model.download_images as m
from fakes import FakeCollection, FakeGeometry, FakeImage
    
def test_build_region(monkeypatch):
    def fake_point(coords):
        return FakeGeometry(coords)

    monkeypatch.setattr(m.ee.Geometry, "Point", fake_point)

    region = m.build_region(30.0, 60.0, 5)

    assert isinstance(region, FakeGeometry)

def test_build_metadata():
    image = FakeImage()

    result = build_metadata(
        image.getInfo(),
        lon=30.0,
        lat=60.0,
        buffer_km=5,
        start_date="2025-01-01",
        end_date="2025-02-01",
        url="http://test"
    )

    assert result["image_id"] == "TEST_IMAGE_123"
    assert result["cloud_percentage"] == 10

def test_select_image_ok():
    collection = FakeCollection()
    image = select_image(collection)

    assert image is not None

def test_select_image_none():
    class EmptyImage:
        def getInfo(self):
            return None

    class EmptyCollection:
        def first(self):
            return EmptyImage()

    assert select_image(EmptyCollection()) is None

def test_build_thumbnail():
    image = FakeImage()
    region = "region"

    rgb, url = build_thumbnail(image, region)

    assert url == "http://fake-url/image.png"
    assert rgb is image

def test_save_metadata(tmp_path):
    file = tmp_path / "meta.json"

    data = {"a": 1}

    save_metadata(data, str(file))

    assert file.exists()

    with open(file) as f:
        loaded = json.load(f)

    assert loaded == data

def test_open_in_browser(monkeypatch):
    called = {}

    def fake_open(url):
        called["url"] = url

    monkeypatch.setattr(m.webbrowser, "open", fake_open)

    m.open_in_browser("http://test")

    assert called["url"] == "http://test"

def test_get_satellite_image(monkeypatch):
    monkeypatch.setattr(m, "build_collection", lambda *args, **kwargs: FakeCollection())
    monkeypatch.setattr(m, "open_in_browser", lambda url: None)
    monkeypatch.setattr(m, "save_metadata", lambda *args, **kwargs: None)
    monkeypatch.setattr(m, "build_region", lambda lon, lat, buffer_km: "fake-region")

    rgb, region, url, metadata = m.get_satellite_image(
        lon=30,
        lat=60,
        buffer_km=5,
        json_filename="test.json",
        open_browser=True
    )

    assert url == "http://fake-url/image.png"
    assert metadata["satellite"] == "Sentinel-2"
    assert rgb is not None
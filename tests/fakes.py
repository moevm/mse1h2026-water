class FakeImage:
    def __init__(self, info=None):
        self._info = info or {
            "id": "TEST_IMAGE_123",
            "properties": {
                "DATATAKE_IDENTIFIER": "2025-08-01",
                "CLOUDY_PIXEL_PERCENTAGE": 10,
            }
        }

    def getInfo(self):
        return self._info

    def select(self, bands):
        return self

    def getThumbURL(self, params):
        return "http://fake-url/image.png"

class FakeCollection:
    def __init__(self, image=None):
        self.image = image or FakeImage()

    def first(self):
        return self.image

class FakeGeometry:
    def __init__(self, coords):
        self.coords = coords

    def buffer(self, x):
        return self

    def bounds(self):
        return self
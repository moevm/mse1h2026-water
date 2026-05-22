from fastapi.testclient import TestClient
from back import app  

client = TestClient(app.app)

def test_large_region_image_error():
    response = client.get(
        "/water-info",
        params={
            "lat": 59.9386,
            "lon": 30.3141,
            "buffer_km": 10
        }
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "Слишком большой радиус запроса"

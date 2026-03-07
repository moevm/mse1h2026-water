import ee
import json
from datetime import datetime
from typing import Tuple, Optional

ee.Authenticate()
ee.Initialize(project='mseml-488016')

def get_satellite_image(
        lon: float,                 
        lat: float, 
        buffer_km: float = 5.0, 
        start_date: str = '2023-06-01',
        end_date: str = '2023-08-31',
        json_filename: str = 'image_info.json'
) -> Tuple[Optional[ee.Image], Optional[ee.Geometry], Optional[str]]:
    """
    Получение спутникового снимка
    """

    point = ee.Geometry.Point([lon, lat])
    region = point.buffer(buffer_km * 1000).bounds()

    collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterDate(start_date, end_date) \
        .filterBounds(region) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))

    image = collection.first()

    if image.getInfo() is None:
        print("Нет изображений за указанный период")
        return None, None, None

    rgb_image = image.select(['B4', 'B3', 'B2', 'B8'])
    
    url = rgb_image.getThumbURL({
        'region': region,
        'dimensions': 1024,
        'format': 'png',
        'min': 0,
        'max': 3000,
        'gamma': 1.4
    })

    info = image.getInfo()
    properties = info.get('properties', {})

    image_metadata = {
        "image_id": info.get('id'),
        "satellite": "Sentinel-2",
        "collection": "COPERNICUS/S2_SR_HARMONIZED",
        "acquisition_date": properties.get('DATATAKE_IDENTIFIER'),
        "cloud_percentage": properties.get('CLOUDY_PIXEL_PERCENTAGE'),
        "coordinates_center": {
            "longitude": lon,
            "latitude": lat
        },
        "buffer_km": buffer_km,
        "date_range": {
            "start": start_date,
            "end": end_date
        },
        "thumbnail_url": url,
        "bands_used": ["B4", "B3", "B2"],
        "created_at": datetime.now().isoformat()
    }

    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(image_metadata, f, ensure_ascii=False, indent=4)
        
    print(f"URL изображения: {url}")

    return rgb_image, region, url

if __name__ == "__main__":
    lon, lat = 30.3141, 59.9386
    buffer_km = 10
    start_date, end_date = '2023-06-01', '2023-08-31'
    image, region, url = get_satellite_image(
        lon=lon, lat=lat, buffer_km=buffer_km, start_date=start_date, end_date=end_date
    )
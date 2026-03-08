import ee
from typing import Optional, Dict, Any

ee.Authenticate()
ee.Initialize(project='mseml-488016')

def get_eutrophication_stats(
    lon: float, 
    lat: float, 
    buffer_km: float = 5.0, 
    start_date: str = '2023-07-01', 
    end_date: str = '2023-08-31'
) -> Optional[Dict[str, Any]]:
    
    point = ee.Geometry.Point([lon, lat])
    region = point.buffer(buffer_km * 1000).bounds()

    collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterDate(start_date, end_date) \
        .filterBounds(region) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))

    if collection.size().getInfo() == 0:
        return None

    image = collection.first()

    ndwi = image.normalizedDifference(['B3', 'B8'])
    water_mask = ndwi.gt(0)

    return {"status": "Water mask created"}

if __name__ == "__main__":
    print(get_eutrophication_stats(lon=30.3141, lat=59.9386))
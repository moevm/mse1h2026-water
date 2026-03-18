import ee
import json
from datetime import datetime
from typing import Optional, Dict, Any

def get_eutrophication_stats(
    lon: float, 
    lat: float, 
    buffer_km: float = 6.0, 
    start_date: str = '2025-06-01', 
    end_date: str = '2025-08-31',
    ndci_threshold: float = 0.1,
    json_filename: Optional[str] = None
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

    ndci = image.normalizedDifference(['B5', 'B4'])
    polluted_mask = ndci.gt(ndci_threshold).And(water_mask)

    pixel_area = ee.Image.pixelArea()
    water_area_img = water_mask.multiply(pixel_area)
    polluted_area_img = polluted_mask.multiply(pixel_area)

    stats = water_area_img.addBands(polluted_area_img).reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=region,
        scale=10, 
        maxPixels=1e9
    ).getInfo()

    total_water_sqm = stats.get('nd')
    polluted_water_sqm = stats.get('nd_1')

    if not total_water_sqm or total_water_sqm == 0:
        print("В заданном радиусе не найдено водоемов.")
        return None
    
    polluted_percentage = (polluted_water_sqm/total_water_sqm)*100

    ndci_mean_stats = ndci.updateMask(water_mask).reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=region,
        scale=10, 
        maxPixels=1e9
    ).getInfo()
    
    ndci_mean_value = ndci_mean_stats.get('nd')

    result_data = {
        "coordinates": {"lon": lon, "lat": lat},
        "ndci_mean": round(ndci_mean_value, 4) if ndci_mean_value else None,
        "total_water_area_m2": round(total_water_sqm, 2),
        "polluted_area_m2": round(polluted_water_sqm, 2),
        "polluted_percentage": round(polluted_percentage, 2),
        "date_analyzed": image.get('DATATAKE_IDENTIFIER').getInfo(),
        "calculated_at": datetime.now().isoformat()
    }

    if json_filename:
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=4)

    return result_data

if __name__ == "__main__":
    ee.Authenticate()
    ee.Initialize(project='mseml-488016')

    lon, lat = 30.4677, 59.9226
    buffer_km = 0.5
    start_date = '2025-07-15'
    end_date = '2025-09-10'
    ndci_threshold = 0.1

    result = get_eutrophication_stats(
        lon=lon, lat=lat, buffer_km=buffer_km, 
        start_date=start_date, end_date=end_date, 
        ndci_threshold=ndci_threshold,
        json_filename='eutrophication_stats.json'
    )

    if result:
        print(f"Средний индекс хлорофилла (NDCI): {result['ndci_mean']}")
        print(f"Доля эвтрофикации: {result['polluted_percentage']}%")
        print(f"Общая площадь воды: {result['total_water_area_m2']} кв.м.")
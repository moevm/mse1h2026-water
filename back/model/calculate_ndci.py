import ee
import json
from datetime import datetime
from typing import Optional, Dict, Any
from model.water_utils import get_water_mask_gee

try:
    from ee_auth import initialize_ee
except ModuleNotFoundError:
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from ee_auth import initialize_ee

def _study_region_bounds(lon: float, lat: float, buffer_km: float) -> ee.Geometry:
    point = ee.Geometry.Point([lon, lat])
    return point.buffer(buffer_km * 1000).bounds()

def _s2_harmonized_collection(
    region: ee.Geometry, start_date: str, end_date: str
) -> ee.ImageCollection:
    return (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterDate(start_date, end_date)
        .filterBounds(region)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
    )

def _ndci_image(s2_image: ee.Image) -> ee.Image:
    return s2_image.normalizedDifference(["B5", "B4"])

def _polluted_water_mask(
    ndci: ee.Image, water_mask: ee.Image, ndci_threshold: float
) -> ee.Image:
    return ndci.gt(ndci_threshold).And(water_mask)

def _sum_water_and_polluted_areas_m2(
    water_mask: ee.Image, polluted_mask: ee.Image, region: ee.Geometry
) -> Dict[str, Any]:
    pixel_area = ee.Image.pixelArea()
    water_area_img = water_mask.multiply(pixel_area)
    polluted_area_img = polluted_mask.multiply(pixel_area)
    return (
        water_area_img.addBands(polluted_area_img)
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=region,
            scale=10,
            maxPixels=1e9,
        )
        .getInfo()
    )

def _mean_ndci_over_water(
    ndci: ee.Image, water_mask: ee.Image, region: ee.Geometry
) -> Optional[float]:
    stats = (
        ndci.updateMask(water_mask)
        .reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=region,
            scale=10,
            maxPixels=1e9,
        )
        .getInfo()
    )
    return stats.get("nd")

def _assemble_result_payload(
    lon: float,
    lat: float,
    ndci_mean_value: Optional[float],
    total_water_sqm: float,
    polluted_water_sqm: float,
    polluted_percentage: float,
    date_analyzed: str,
) -> Dict[str, Any]:
    return {
        "coordinates": {"lon": lon, "lat": lat},
        "ndci_mean": round(ndci_mean_value, 4) if ndci_mean_value else None,
        "total_water_area_m2": round(total_water_sqm, 2),
        "polluted_area_m2": round(polluted_water_sqm, 2),
        "polluted_percentage": round(polluted_percentage, 2),
        "date_analyzed": date_analyzed,
        "calculated_at": datetime.now().isoformat(),
    }

def _write_result_json(payload: Dict[str, Any], json_filename: str) -> None:
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)

def get_eutrophication_stats(
    lon: float, 
    lat: float, 
    buffer_km: float = 6.0, 
    start_date: str = '2025-06-01', 
    end_date: str = '2025-08-31',
    ndci_threshold: float = 0.1,
    json_filename: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    region = _study_region_bounds(lon, lat, buffer_km)
    collection = _s2_harmonized_collection(region, start_date, end_date)

    if collection.size().getInfo() == 0:
        return None

    image = collection.first()
    water_mask = get_water_mask_gee(image)
    ndci = _ndci_image(image)
    polluted_mask = _polluted_water_mask(ndci, water_mask, ndci_threshold)

    area_stats = _sum_water_and_polluted_areas_m2(water_mask, polluted_mask, region)
    total_water_sqm = area_stats.get("nd")
    polluted_water_sqm = area_stats.get("nd_1")

    if not total_water_sqm or total_water_sqm == 0:
        print("В заданном радиусе не найдено водоемов.")
        return None
    
    polluted_percentage = (polluted_water_sqm / total_water_sqm) * 100
    ndci_mean_value = _mean_ndci_over_water(ndci, water_mask, region)
    date_analyzed = image.get("DATATAKE_IDENTIFIER").getInfo()

    result_data = _assemble_result_payload(
        lon,
        lat,
        ndci_mean_value,
        total_water_sqm,
        polluted_water_sqm,
        polluted_percentage,
        date_analyzed,
    )

    if json_filename:
        _write_result_json(result_data, json_filename)

    return result_data

if __name__ == "__main__":
    initialize_ee()

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

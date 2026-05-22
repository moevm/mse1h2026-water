import ee
import json
import webbrowser
import requests
import uuid
from datetime import datetime
from typing import Tuple, Optional, Dict, Any

from streamlit import image

try:
    from ee_auth import initialize_ee
except ModuleNotFoundError:
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from ee_auth import initialize_ee


def build_region(lon: float, lat: float, buffer_km: float) -> ee.Geometry:
    point = ee.Geometry.Point([lon, lat])
    return point.buffer(buffer_km * 1000).bounds()

def build_collection(
    region: ee.Geometry,
    start_date: str,
    end_date: str,
    min_coverage: float = 0.9,
):

    region_area = region.area(maxError=1)


    def add_coverage(image):
        intersection = image.geometry().intersection(
            region,
            ee.ErrorMargin(1)
        )

        coverage_area = intersection.area(maxError=1)

        coverage = coverage_area.divide(region_area)

        return image.set("coverage", coverage)


    return (
        ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        .filterDate(start_date, end_date)
        .filterBounds(region)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
        .map(add_coverage)
        .filter(ee.Filter.gte("coverage", min_coverage))
    )

def select_image(collection):
    image = collection.first()
    if image.getInfo() is None:
        return None
    return image

def build_thumbnail(image, region):
    rgb = image.select(['B4', 'B3', 'B2', 'B8', 'B11'])
    url = rgb.getThumbURL({
        'region': region,
        'scale': 30,
        'format': 'png',
        'min': 0,
        'max': 3000,
        'crs': 'EPSG:3857'
    })
    return rgb, url

def build_metadata(image_info, lon, lat, buffer_km, start_date, end_date, url, tif_file):
    props = image_info.get('properties', {}) if image_info else {}
    
    return {
        "image_id": image_info.get('id') if image_info else None,
        "satellite": "Sentinel-2",
        "collection": "COPERNICUS/S2_SR_HARMONIZED",
        "acquisition_date": props.get('DATATAKE_IDENTIFIER'),
        "cloud_percentage": props.get('CLOUDY_PIXEL_PERCENTAGE'),
        "coordinates_center": {"longitude": lon, "latitude": lat},
        "buffer_km": buffer_km,
        "date_range": {"start": start_date, "end": end_date},
        "thumbnail_url": url,
        "bands_used": ['B4', 'B3', 'B2', 'B8', 'B11'],
        "tif_file": tif_file,
        "created_at": datetime.now().isoformat(),
    }

def save_metadata(metadata, filename: str):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

def open_in_browser(url: str):
    webbrowser.open(url)

def create_tif_file(image, region):
    ee_tif_url = image.getDownloadURL({
        "region": region,
        "scale": 30,
        "format": "GEO_TIFF",
        "crs": "EPSG:3857",
    })
    
    r = requests.get(ee_tif_url)
    tif_file = f"geotif/{uuid.uuid4()}.tif"
    with open(tif_file, "xb") as f:
        f.write(r.content)
    
    return tif_file

def get_satellite_image(
    lon: float,
    lat: float,
    buffer_km: float = 6.0,
    start_date: str = '2025-06-01',
    end_date: str = '2025-08-31',
    json_filename: str | None = None,
    open_browser: bool = False,
    tif_file: str | None = None
):
    region = build_region(lon, lat, buffer_km)
    collection = build_collection(region, start_date, end_date)

    image = select_image(collection)
    if image is None:
        print("Нет изображений за указанный период")
        return None, None, None, None

    rgb, url = build_thumbnail(image, region)

    if not tif_file:
        tif_file = create_tif_file(image, region)
    
    info = image.getInfo()
    metadata = build_metadata(
        info, lon, lat, buffer_km, start_date, end_date, url, tif_file
    )

    if json_filename:
        save_metadata(metadata, json_filename)

    if open_browser:
        open_in_browser(url)

    return rgb, region, url, metadata

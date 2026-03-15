from model import download_images
from model import integrated_water_classifiers
from model import water_detector
import calculate_ndci

from typing import Any, Dict
from pydantic import BaseModel
from fastapi import FastAPI, APIRouter, Query, Request

import uvicorn
import os
import ee


file = os.path.basename(__file__)
filename = os.path.splitext(file)[0]

app = FastAPI()
router = APIRouter(prefix=f"/{filename}")

_ee_initialized = False


class SatelliteImageMetadata(BaseModel):
    image_id: str
    satellite: str
    collection: str
    acquisition_date: str
    cloud_percentage: float
    coordinates_center: Dict[str, float]
    buffer_km: float
    date_range: Dict[str, str]
    thumbnail_url: str = None
    bands_used: list = None
    created_at: str = None


def initialize_ee():
    global _ee_initialized
    if not _ee_initialized:
        ee.Authenticate()
        ee.Initialize(project='mseml-488016')
        _ee_initialized = True


@router.get("/get_satellite_image")
async def get_satellite_image(
    lat: float = Query(default=59.938784, ge=0, le=90),
    lon: float = Query(default=30.314997, ge=0, le=180),
    buffer_km: float = Query(default=0.25), 
    start_date: str = Query(default='2025-06-01'),
    end_date: str = Query(default='2025-08-31'),
):
    
    initialize_ee()
    return download_images.get_satellite_image(lon, lat, buffer_km, start_date, end_date)[3]


@router.post("/cv_integrated_water_classifier",
            summary='Классификации водоемов через OpenCV')
async def cv_integrated_water_classifier(
    request: Request,
    image_metadata_json: SatelliteImageMetadata,
):

    initialize_ee()
    
    image_metadata = image_metadata_json.model_dump()
    
    image, region, url, _ = download_images.get_satellite_image(
        lon=image_metadata["coordinates_center"]["longitude"],
        lat=image_metadata["coordinates_center"]["latitude"],
        buffer_km=image_metadata["buffer_km"],
        start_date=image_metadata["date_range"]["start"],
        end_date=image_metadata["date_range"]["end"]
    )
    
    result = await integrated_water_classifiers.cv_integrated_water_classifier(image, region, url)
    result["annotated_url"] = f"{request.base_url}{result["annotated_url"]}"
    return result


@router.get("/water_detector")
async def water_detector_endpoint(
    lat: float = Query(default=59.938784, ge=0, le=90),
    lon: float = Query(default=30.314997, ge=0, le=180),
    radius: int = Query(default=50), 
):
    
    return water_detector.get_water_type_from_open_data(lat, lon, radius)


@router.get("/get_eutrophication_stats")
async def get_eutrophication_stats(
    lat: float = Query(default=59.938784, ge=0, le=90),
    lon: float = Query(default=30.314997, ge=0, le=180),
    buffer_km: float = 5.0, 
    start_date: str = '2023-07-01', 
    end_date: str = '2023-08-31',
    ndci_threshold: float = 0.1,
):
    
    initialize_ee()
    
    return calculate_ndci.get_eutrophication_stats(
        lon, 
        lat, 
        buffer_km, 
        start_date, 
        end_date,
        ndci_threshold,
    )


app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(f"{filename}:app", reload=True)

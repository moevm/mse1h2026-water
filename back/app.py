from routers import methods
from model import integrated_water_classifiers, calculate_ndci

from fastapi import FastAPI, APIRouter, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware 

import uvicorn
import os

file = os.path.basename(__file__)
filename = os.path.splitext(file)[0]

app = FastAPI()
router = APIRouter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@router.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs", status_code=302)


@app.get("/water-info")
async def get_water_info(
    request: Request,
    lat: float = Query(default=59.938784, ge=-90, le=90),
    lon: float = Query(default=30.314997, ge=-180, le=180),
    buffer_km: float = Query(default=6.0), 
    start_date: str = Query(default='2025-06-01'),
    end_date: str = Query(default='2025-08-31'),
):
    
    methods.initialize_ee()
    
    image, region, url, metadata = methods.download_images.get_satellite_image(
        lon, lat, buffer_km, start_date, end_date
    )
    
    result = await integrated_water_classifiers.cv_integrated_water_classifier(image, region, url, metadata)
    result["image_path"] = f"{request.base_url}{result['image_path']}"
    result["geojson_path"] = f"{request.base_url}{result['geojson_path']}"
    result["eutrophication_stats"] = calculate_ndci.get_eutrophication_stats(lon, lat, buffer_km, start_date, end_date)
    return result


app.include_router(router)
app.include_router(methods.router)
os.makedirs("img", exist_ok=True)
os.makedirs("geojson", exist_ok=True)
os.makedirs("geotif", exist_ok=True)
app.mount("/img", StaticFiles(directory="img"), name="Классифицированные изображения")
app.mount("/geojson", StaticFiles(directory="geojson"), name="GeoJSON файлы")
app.mount("/geotif", StaticFiles(directory="geotif"), name="GEO_TIFF файлы")

if __name__ == "__main__":
    # Если нужно резко прерывать, то можно добавить timeout_graceful_shutdown=1
    uvicorn.run(f"{filename}:app", reload=True)

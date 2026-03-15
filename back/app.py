from routers import methods

from fastapi import FastAPI, APIRouter, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

import uvicorn
import os

file = os.path.basename(__file__)
filename = os.path.splitext(file)[0]

app = FastAPI()
router = APIRouter()


@router.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs", status_code=303)


@app.get("/water-info")
async def get_water_info(
    request: Request,
    lat: float = Query(default=59.938784, ge=0, le=90),
    lon: float = Query(default=30.314997, ge=0, le=180),
    buffer_km: float = Query(default=0.25), 
    start_date: str = Query(default='2025-06-01'),
    end_date: str = Query(default='2025-08-31'),
):
    
    methods.initialize_ee()
    
    image, region, url, _ = methods.download_images.get_satellite_image(
        lon, lat, buffer_km, start_date, end_date
    )
    
    result = await methods.integrated_water_classifiers.cv_integrated_water_classifier(image, region, url)
    result["annotated_url"] = f"{request.base_url}{result["annotated_url"]}"
    return result


app.include_router(router)
app.include_router(methods.router)
os.makedirs("img/classified", exist_ok=True)
app.mount("/img/classified", StaticFiles(directory="img/classified"), name="Классифицированные изображения")


if __name__ == "__main__":
    # Если нужно резко прерывать, то можно добавить timeout_graceful_shutdown=1
    uvicorn.run(f"{filename}:app", reload=True)

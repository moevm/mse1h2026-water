from model import API

from fastapi import FastAPI, APIRouter, Query

import uvicorn
import os
import ee


file = os.path.basename(__file__)
filename = os.path.splitext(file)[0]

app = FastAPI()
router = APIRouter(prefix=f"/{filename}")


@router.get("/get_satellite_image")
async def get_satellite_image(
    lat: float = Query(default=59.938784, ge=0, le=90),
    lon: float = Query(default=30.314997, ge=0, le=180),
    buffer_km: float = Query(default=5.0), 
    start_date: str = Query(default='2025-06-01'),
    end_date: str = Query(default='2025-08-31'),
):
    ee.Authenticate()
    ee.Initialize(project='mseml-488016')
    return API.get_satellite_image(lon, lat, buffer_km, start_date, end_date)[3]


app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(f"{filename}:app", reload=True)

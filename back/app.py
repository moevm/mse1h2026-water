from routers import methods

from fastapi import FastAPI, APIRouter, Query
from fastapi.responses import RedirectResponse

import uvicorn
import os

file = os.path.basename(__file__)
filename = os.path.splitext(file)[0]

app = FastAPI()
router = APIRouter()

WATER_TYPES = "болото/река/озеро/пруд"
ECOLOGICAL_STATUSES = "чистый/эвтрофикация"


@router.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs", status_code=303)


@app.get("/water-info")
async def get_water_info(
    lat: float = Query(..., ge=0, le=90),
    lon: float = Query(..., ge=0, le=180)
):
    return {
        "coordinates": {"lat": lat, "lon": lon},
        "water_type": WATER_TYPES,
        "ecological_status": ECOLOGICAL_STATUSES
    }


app.include_router(router)
app.include_router(methods.router)


if __name__ == "__main__":
    uvicorn.run(f"{filename}:app", reload=True)

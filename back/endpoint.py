from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware 
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WATER_TYPES = "болото/река/озеро/пруд"
ECOLOGICAL_STATUSES = "чистый/эвтрофикация"

@app.get("/")
async def root():
    return {}

@app.get("/water-info")

async def get_water_info(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180)
):
    return {
        "coordinates": {"lat": lat, "lon": lon},
        "water_type": WATER_TYPES,
        "ecological_status": ECOLOGICAL_STATUSES
    }
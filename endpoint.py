from fastapi import FastAPI, Query

app = FastAPI()
WATER_TYPES = "болото/река/озеро/пруд"
ECOLOGICAL_STATUSES = "чистый/эвтрофикация"

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
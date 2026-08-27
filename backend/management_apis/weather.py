"""
Weather API router — exposes endpoints to retrieve current weather
conditions and 7-day forecast with crop weather-risk assessment.
"""

from fastapi import APIRouter, HTTPException, Query

from backend.service_apis.weather_service import get_weather_data

router = APIRouter(
    prefix="/weather",
    tags=["Weather"],
)


@router.get("/")
def get_weather(
    lat: float = Query(..., description="Latitude of the farm location", ge=-90, le=90),
    lon: float = Query(..., description="Longitude of the farm location", ge=-180, le=180),
):
    """
    Retrieve current weather conditions and 7-day forecast for a farm location.

    Returns (via Open-Meteo):
    - Current temperature, humidity, precipitation, wind, pressure
    - 7-day daily forecast (max/min temp, rain sum, wind, sunrise/sunset)
    - WMO weather condition descriptions
    - Weather risk level for crop distress model (Low / Medium / High)
    """
    try:
        return get_weather_data(lat=lat, lon=lon)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")

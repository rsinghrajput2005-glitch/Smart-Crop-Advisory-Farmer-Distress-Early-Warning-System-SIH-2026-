"""
Soil API router — exposes endpoints to retrieve SoilGrids data for a farm location.
"""

from fastapi import APIRouter, HTTPException, Query

from backend.service_apis.soil_service import get_soil_data

router = APIRouter(
    prefix="/soil",
    tags=["Soil"],
)


@router.get("/")
def get_soil(
    lat: float = Query(..., description="Latitude of the farm location", ge=-90, le=90),
    lon: float = Query(..., description="Longitude of the farm location", ge=-180, le=180),
):
    """
    Retrieve soil properties for a given farm latitude/longitude.

    Fetches the following from SoilGrids ISRIC (0–30 cm depth):
    - Soil pH
    - Organic Carbon Density
    - Clay content (%)
    - Sand content (%)
    - Nitrogen (g/kg)

    Also returns agronomic interpretation hints for each property.
    """
    try:
        return get_soil_data(lat=lat, lon=lon)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")

"""
NDVI API router — exposes endpoints to retrieve Sentinel-2 NDVI
scene data and crop condition assessment for a farm location.
"""

from fastapi import APIRouter, HTTPException, Query

from backend.service_apis.ndvi_service import get_ndvi_data, get_ndvi_with_value

router = APIRouter(
    prefix="/ndvi",
    tags=["NDVI / Satellite"],
)


@router.get("/")
def get_ndvi(
    lat: float = Query(..., description="Latitude of the farm location", ge=-90, le=90),
    lon: float = Query(..., description="Longitude of the farm location", ge=-180, le=180),
):
    """
    Retrieve the latest Sentinel-2 scene metadata for a farm location.

    Returns:
    - Scene ID, acquisition date, cloud cover
    - Asset URLs for B04 (Red) and B08 (NIR) bands — use these to compute NDVI
    - Thumbnail / visual preview URL
    - NDVI formula and value interpretation reference
    - Advisory notes on computing NDVI from the asset links

    Note: Full pixel-level NDVI computation requires rasterio/GDAL on the asset COGs.
    """
    try:
        return get_ndvi_data(lat=lat, lon=lon)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")


@router.get("/analyse")
def analyse_ndvi(
    lat: float = Query(..., description="Latitude of the farm location", ge=-90, le=90),
    lon: float = Query(..., description="Longitude of the farm location", ge=-180, le=180),
    ndvi_value: float = Query(
        ...,
        description="Pre-computed NDVI value (−1.0 to 1.0) for this farm",
        ge=-1.0,
        le=1.0,
    ),
):
    """
    Analyse a pre-computed NDVI value for a farm location.

    Combines the NDVI value with Sentinel-2 scene metadata and returns:
    - Crop condition label (Bare Soil / Moderate / Healthy / Dense Vegetation)
    - Urgency level (Low / Medium / High)
    - Actionable advisory for the farmer
    - Scene metadata for reference

    Use this endpoint when NDVI has already been computed from satellite bands.
    """
    try:
        return get_ndvi_with_value(lat=lat, lon=lon, ndvi_value=ndvi_value)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")

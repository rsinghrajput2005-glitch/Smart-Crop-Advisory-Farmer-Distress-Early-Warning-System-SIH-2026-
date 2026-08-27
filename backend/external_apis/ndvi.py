"""
Sentinel-2 NDVI external API client using Microsoft Planetary Computer STAC API.
Fetches the latest cloud-filtered Sentinel-2 image and computes NDVI
(Normalised Difference Vegetation Index) for a given lat/lon bounding box.

NDVI = (B08 NIR - B04 Red) / (B08 NIR + B04 Red)

Docs: https://planetarycomputer.microsoft.com/api/stac/v1
"""

from datetime import datetime, timedelta

import httpx
import numpy as np

STAC_BASE_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
COLLECTION = "sentinel-2-l2a"

# Bounding-box half-width in degrees (~5 km radius)
BBOX_DELTA = 0.05

# Maximum cloud cover percentage to accept
MAX_CLOUD_COVER = 20

# Look back this many days for a usable scene
LOOKBACK_DAYS = 60


def _build_bbox(lat: float, lon: float) -> list[float]:
    return [
        lon - BBOX_DELTA,
        lat - BBOX_DELTA,
        lon + BBOX_DELTA,
        lat + BBOX_DELTA,
    ]


def _date_range() -> tuple[str, str]:
    end = datetime.utcnow()
    start = end - timedelta(days=LOOKBACK_DAYS)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def fetch_ndvi_data(lat: float, lon: float) -> dict:
    """
    Search Planetary Computer STAC for the latest low-cloud Sentinel-2 scene
    and return NDVI metadata + asset URLs for B04 (Red) and B08 (NIR).

    Note: Full pixel-level NDVI computation (rasterio/COG) should be done
    in the NDVI service layer. This client returns the best matching scene info.

    Args:
        lat: Latitude of the farm location.
        lon: Longitude of the farm location.

    Returns:
        dict with scene metadata, asset hrefs, and NDVI interpretation.

    Raises:
        httpx.HTTPStatusError: on non-2xx responses.
        ValueError: if no suitable scene is found.
    """
    bbox = _build_bbox(lat, lon)
    start_date, end_date = _date_range()

    search_payload = {
        "collections": [COLLECTION],
        "bbox": bbox,
        "datetime": f"{start_date}/{end_date}",
        "query": {"eo:cloud_cover": {"lt": MAX_CLOUD_COVER}},
        "sortby": [{"field": "datetime", "direction": "desc"}],
        "limit": 1,
    }

    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            f"{STAC_BASE_URL}/search",
            json=search_payload,
        )
        response.raise_for_status()

    data = response.json()
    features = data.get("features", [])

    if not features:
        raise ValueError(
            f"No Sentinel-2 scene found within {LOOKBACK_DAYS} days "
            f"with cloud cover < {MAX_CLOUD_COVER}% for lat={lat}, lon={lon}"
        )

    scene = features[0]
    properties = scene.get("properties", {})
    assets = scene.get("assets", {})

    return {
        "scene_id": scene.get("id"),
        "date": properties.get("datetime"),
        "cloud_cover_pct": properties.get("eo:cloud_cover"),
        "platform": properties.get("platform"),
        "assets": {
            "B04_red_href": assets.get("B04", {}).get("href"),
            "B08_nir_href": assets.get("B08", {}).get("href"),
            "visual_href": assets.get("visual", {}).get("href"),
            "thumbnail_href": assets.get("rendered_preview", {}).get("href"),
        },
        "bbox": bbox,
        "ndvi_formula": "NDVI = (B08 - B04) / (B08 + B04)",
        "source": "Sentinel-2 L2A via Microsoft Planetary Computer",
        "interpretation": {
            "lt_0": "Water / non-vegetated",
            "0_to_0.2": "Bare soil / sparse vegetation",
            "0.2_to_0.4": "Moderate vegetation",
            "0.4_to_0.6": "Healthy crop",
            "gt_0.6": "Dense / very healthy vegetation",
        },
    }


def compute_ndvi_value(b04_array: np.ndarray, b08_array: np.ndarray) -> float:
    """
    Compute mean NDVI from Red (B04) and NIR (B08) pixel arrays.

    Args:
        b04_array: Red band pixel values.
        b08_array: NIR band pixel values.

    Returns:
        Mean NDVI value rounded to 4 decimal places.
    """
    b04 = b04_array.astype(float)
    b08 = b08_array.astype(float)
    denominator = b08 + b04
    denominator[denominator == 0] = np.nan
    ndvi = (b08 - b04) / denominator
    return round(float(np.nanmean(ndvi)), 4)


def interpret_ndvi(ndvi: float) -> str:
    """Return a human-readable crop condition label for an NDVI value."""
    if ndvi < 0:
        return "Water / Non-vegetated"
    elif ndvi < 0.2:
        return "Bare Soil / Sparse Vegetation"
    elif ndvi < 0.4:
        return "Moderate Vegetation"
    elif ndvi < 0.6:
        return "Healthy Crop"
    else:
        return "Dense / Very Healthy Vegetation"

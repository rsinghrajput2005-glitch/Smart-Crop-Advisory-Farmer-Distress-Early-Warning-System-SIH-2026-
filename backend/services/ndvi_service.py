"""
services/ndvi_service.py

Returns a MOCKED NDVI value for a given farm location.

TODO: Replace mock with real Sentinel-2 NDVI computation. Future integration plan:
        1. Query Microsoft Planetary Computer STAC API for the latest
           low-cloud Sentinel-2 L2A scene:
           POST https://planetarycomputer.microsoft.com/api/stac/v1/search
           with filters: collection=sentinel-2-l2a, cloud_cover < 20%,
                         bbox around (lat, lon), sorted by date desc.
        2. Retrieve the B04 (Red) and B08 (NIR) Cloud-Optimised GeoTIFF assets.
        3. Read pixel values over the farm boundary using rasterio + shapely.
        4. Compute: NDVI = (B08 - B04) / (B08 + B04)
        5. Return the mean NDVI over the farm polygon.
        Additional libraries needed: rasterio, shapely, pyproj, numpy
"""

from __future__ import annotations

import random


def get_ndvi(lat: float, lon: float) -> dict:
    """
    Return NDVI data for a farm location.

    Currently returns a MOCKED NDVI value (random float in the realistic
    0.3–0.8 range) for development and demo purposes.

    Args:
        lat: Farm latitude  (-90 to 90).
        lon: Farm longitude (-180 to 180).

    Returns:
        dict with:
            ndvi_value   – float (0.3–0.8 mock range)
            condition    – human-readable crop condition label
            advisory     – actionable recommendation for the farmer
            is_mock      – True (remove after real Sentinel-2 integration)
            note         – disclaimer

    # TODO: Replace the mock value with real Sentinel-2 computation (see module docstring).
    """
    # MOCK: random NDVI in 0.3–0.8 to simulate typical in-season crop values
    ndvi_value = round(random.uniform(0.3, 0.8), 4)  # TODO: replace with real computation

    condition = _interpret_ndvi(ndvi_value)
    advisory  = _advisory(ndvi_value, condition)

    return {
        "lat":        lat,
        "lon":        lon,
        "ndvi_value": ndvi_value,
        "condition":  condition,
        "advisory":   advisory,
        "is_mock":    True,   # TODO: set to False once Sentinel-2 is integrated
        "note": (
            "⚠ Mock NDVI value — for development/demo purposes only. "
            "See TODO in ndvi_service.py for real Sentinel-2 integration steps."
        ),
    }


def _interpret_ndvi(ndvi: float) -> str:
    """Map an NDVI value to a crop condition label."""
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


def _advisory(ndvi: float, condition: str) -> dict:
    """Return urgency-rated advisory based on NDVI value."""
    table = {
        "Water / Non-vegetated": (
            "Check for waterlogging or crop failure. Immediate field inspection needed.",
            "High",
        ),
        "Bare Soil / Sparse Vegetation": (
            "Poor crop establishment detected. Check germination and consider gap-filling.",
            "High",
        ),
        "Moderate Vegetation": (
            "Crop is developing but below optimum. Monitor soil moisture and apply fertiliser if needed.",
            "Medium",
        ),
        "Healthy Crop": (
            "Crop appears healthy. Continue regular monitoring.",
            "Low",
        ),
        "Dense / Very Healthy Vegetation": (
            "Excellent crop condition. Monitor for lodging risk in dense canopies.",
            "Low",
        ),
    }
    action, urgency = table.get(condition, ("No advisory available.", "Unknown"))
    return {
        "urgency": urgency,
        "action":  action,
    }

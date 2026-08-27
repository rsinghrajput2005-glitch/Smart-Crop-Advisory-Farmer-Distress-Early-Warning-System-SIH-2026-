"""
NDVI service — orchestrates Sentinel-2 NDVI scene fetching and interpretation.
Sits between the API router and the external_apis.ndvi client.
"""

from backend.external_apis.ndvi import fetch_ndvi_data, interpret_ndvi


def get_ndvi_data(lat: float, lon: float) -> dict:
    """
    Retrieve the latest Sentinel-2 NDVI scene metadata and crop condition assessment.

    Args:
        lat: Latitude of the farm.
        lon: Longitude of the farm.

    Returns:
        dict with scene info, NDVI assets, and crop condition label.

    Raises:
        ValueError: if coordinates are invalid or no scene found.
        RuntimeError: if Planetary Computer API is unreachable.
    """
    if not (-90 <= lat <= 90):
        raise ValueError(f"Invalid latitude: {lat}.")
    if not (-180 <= lon <= 180):
        raise ValueError(f"Invalid longitude: {lon}.")

    try:
        ndvi_data = fetch_ndvi_data(lat=lat, lon=lon)
    except ValueError as exc:
        raise ValueError(str(exc)) from exc
    except Exception as exc:
        raise RuntimeError(
            f"Failed to fetch NDVI data from Planetary Computer: {exc}"
        ) from exc

    # Attach advisory notes
    ndvi_data["advisory"] = _ndvi_advisory(ndvi_data)
    return ndvi_data


def get_ndvi_with_value(lat: float, lon: float, ndvi_value: float) -> dict:
    """
    Combine a pre-computed NDVI value with scene metadata and produce
    full interpretation + advisory for the ML distress model.

    Args:
        lat: Latitude of the farm.
        lon: Longitude of the farm.
        ndvi_value: Computed NDVI value (from rasterio band calculation).

    Returns:
        dict with ndvi_value, condition label, scene metadata, advisory.
    """
    scene_data = get_ndvi_data(lat, lon)
    condition = interpret_ndvi(ndvi_value)

    scene_data["ndvi_value"] = ndvi_value
    scene_data["crop_condition"] = condition
    scene_data["advisory"] = _ndvi_advisory_from_value(ndvi_value)

    return scene_data


def _ndvi_advisory(ndvi_data: dict) -> dict:
    """Generate advisory notes from scene metadata (without pixel NDVI value)."""
    cloud_cover = ndvi_data.get("cloud_cover_pct", 0)
    scene_date = ndvi_data.get("date", "Unknown")

    notes = []
    if cloud_cover and cloud_cover > 10:
        notes.append(
            f"Scene has {cloud_cover:.1f}% cloud cover — NDVI values may be partially masked."
        )
    notes.append(
        f"Latest available Sentinel-2 scene: {scene_date}. "
        "Use B04 (Red) and B08 (NIR) asset links to compute pixel-level NDVI."
    )

    return {
        "notes": notes,
        "recommendation": (
            "Compute NDVI using the provided B04/B08 asset URLs with rasterio or GDAL. "
            "Apply cloud mask before computing mean NDVI for the farm area."
        ),
    }


def _ndvi_advisory_from_value(ndvi: float) -> dict:
    """Generate crop-specific advisory based on NDVI value."""
    condition = interpret_ndvi(ndvi)

    advisories = {
        "Water / Non-vegetated": {
            "action": "Verify crop establishment — possible waterlogging or bare field.",
            "urgency": "High",
        },
        "Bare Soil / Sparse Vegetation": {
            "action": "Check germination and emergence. Consider gap-filling or re-sowing.",
            "urgency": "High",
        },
        "Moderate Vegetation": {
            "action": "Monitor crop closely. Assess soil moisture and apply fertiliser if needed.",
            "urgency": "Medium",
        },
        "Healthy Crop": {
            "action": "Crop appears healthy. Continue regular monitoring.",
            "urgency": "Low",
        },
        "Dense / Very Healthy Vegetation": {
            "action": "Excellent crop condition. Monitor for lodging risk in high-density canopies.",
            "urgency": "Low",
        },
    }

    advisory = advisories.get(condition, {"action": "No advisory available.", "urgency": "Unknown"})
    advisory["condition"] = condition
    advisory["ndvi_value"] = ndvi
    return advisory

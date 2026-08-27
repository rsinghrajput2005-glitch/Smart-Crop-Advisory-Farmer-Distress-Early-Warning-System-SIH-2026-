"""
Soil service — orchestrates SoilGrids data fetching and caching.
This layer sits between the API router and the external_apis.soil client.
"""

from backend.external_apis.soil import fetch_soil_data


def get_soil_data(lat: float, lon: float) -> dict:
    """
    Retrieve and return soil properties for the given coordinates.

    Args:
        lat: Latitude of the farm.
        lon: Longitude of the farm.

    Returns:
        Soil data dict with ph, organic_carbon, clay, sand, nitrogen.

    Raises:
        ValueError: if coordinates are out of valid range.
        RuntimeError: if SoilGrids API is unreachable.
    """
    if not (-90 <= lat <= 90):
        raise ValueError(f"Invalid latitude: {lat}. Must be between -90 and 90.")
    if not (-180 <= lon <= 180):
        raise ValueError(f"Invalid longitude: {lon}. Must be between -180 and 180.")

    try:
        soil = fetch_soil_data(lat=lat, lon=lon)
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch soil data from SoilGrids: {exc}") from exc

    # Enrich with interpretation hints
    soil["interpretation"] = _interpret_soil(soil)
    return soil


def _interpret_soil(soil: dict) -> dict:
    """Return basic agronomic interpretations for soil values."""
    interpretation = {}

    ph = soil.get("ph")
    if ph is not None:
        if ph < 5.5:
            interpretation["ph"] = "Strongly acidic — lime amendment recommended"
        elif ph < 6.5:
            interpretation["ph"] = "Slightly acidic — suitable for most crops"
        elif ph < 7.5:
            interpretation["ph"] = "Neutral — optimal for most crops"
        elif ph < 8.5:
            interpretation["ph"] = "Slightly alkaline — monitor micronutrient availability"
        else:
            interpretation["ph"] = "Strongly alkaline — gypsum or sulfur treatment may help"

    oc = soil.get("organic_carbon")
    if oc is not None:
        if oc < 5:
            interpretation["organic_carbon"] = "Very low — organic matter addition needed"
        elif oc < 10:
            interpretation["organic_carbon"] = "Low — compost application beneficial"
        elif oc < 20:
            interpretation["organic_carbon"] = "Medium — adequate for most crops"
        else:
            interpretation["organic_carbon"] = "High — good soil health"

    clay = soil.get("clay")
    if clay is not None:
        if clay < 15:
            interpretation["texture"] = "Sandy — low water retention, frequent irrigation needed"
        elif clay < 35:
            interpretation["texture"] = "Loamy — good balance of drainage and retention"
        else:
            interpretation["texture"] = "Clayey — risk of waterlogging, drainage important"

    return interpretation

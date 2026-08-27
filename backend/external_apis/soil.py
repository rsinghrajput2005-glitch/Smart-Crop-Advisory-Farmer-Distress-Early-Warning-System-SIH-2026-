"""
SoilGrids / ISRIC WCS external API client.
Fetches soil properties (pH, Organic Carbon, Clay, Sand, Nitrogen)
for a given latitude/longitude using the SoilGrids REST API v2.
Docs: https://rest.isric.org/soilgrids/v2.0/docs
"""

import httpx

SOILGRIDS_BASE_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"

# Properties to fetch from SoilGrids
SOIL_PROPERTIES = ["phh2o", "ocd", "clay", "sand", "nitrogen"]

# Depth interval to query (0-30 cm topsoil)
DEPTH = "0-30cm"

# Statistic value to use
VALUE = "mean"


def fetch_soil_data(lat: float, lon: float) -> dict:
    """
    Fetch soil properties from SoilGrids REST API v2.

    Args:
        lat: Latitude of the farm location.
        lon: Longitude of the farm location.

    Returns:
        dict with keys: ph, organic_carbon, clay, sand, nitrogen
        All values are in their standard units (pH: 1/10 pH unit * 10,
        ocd: dg/kg, clay/sand: g/kg, nitrogen: cg/kg).

    Raises:
        httpx.HTTPStatusError: on non-2xx responses.
        ValueError: if expected data is missing from response.
    """
    params = {
        "lon": lon,
        "lat": lat,
        "property": SOIL_PROPERTIES,
        "depth": DEPTH,
        "value": VALUE,
    }

    with httpx.Client(timeout=30.0) as client:
        response = client.get(SOILGRIDS_BASE_URL, params=params)
        response.raise_for_status()

    data = response.json()
    layers = {
        layer["name"]: layer["depths"][0]["values"][VALUE]
        for layer in data.get("properties", {}).get("layers", [])
        if layer.get("depths")
    }

    return {
        # pH: raw value is pH * 10, so divide by 10
        "ph": round(layers.get("phh2o", 0) / 10, 2) if layers.get("phh2o") else None,
        # Organic Carbon Density: dg/kg → g/kg
        "organic_carbon": round(layers.get("ocd", 0) / 10, 2) if layers.get("ocd") else None,
        # Clay content: g/kg → %
        "clay": round(layers.get("clay", 0) / 10, 2) if layers.get("clay") else None,
        # Sand content: g/kg → %
        "sand": round(layers.get("sand", 0) / 10, 2) if layers.get("sand") else None,
        # Nitrogen: cg/kg → g/kg
        "nitrogen": round(layers.get("nitrogen", 0) / 100, 3) if layers.get("nitrogen") else None,
        "source": "SoilGrids ISRIC v2",
        "depth": DEPTH,
    }

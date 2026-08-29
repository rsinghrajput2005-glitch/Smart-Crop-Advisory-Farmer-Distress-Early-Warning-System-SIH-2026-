"""
SoilGrids external API client — now via OpenEPI's Soil API.

rest.isric.org's REST endpoint has been intermittently paused/unstable
(ISRIC's own docs note the outage with no ETA). OpenEPI serves the same
underlying SoilGrids data through a more reliable public wrapper, so we
call that instead. Function name, signature, and return shape are
unchanged so callers (backend.service_apis.soil_service) need no changes.

Docs: https://developer-test.openepi.io/data-catalog/soil
"""

import httpx

SOILGRIDS_BASE_URL = "https://api.openepi.io/soil/property"

# Properties to fetch
SOIL_PROPERTIES = ["phh2o", "ocd", "clay", "sand"]

# Depth interval to query (0-30 cm topsoil)
DEPTH = "0-30cm"

# Statistic value to use
VALUE = "mean"


def fetch_soil_data(lat: float, lon: float) -> dict:
    """
    Fetch soil properties from OpenEPI's Soil API (SoilGrids-backed).

    Args:
        lat: Latitude of the farm location.
        lon: Longitude of the farm location.

    Returns:
        dict with keys: ph, organic_carbon, clay, sand, source, depth.

    Raises:
        httpx.HTTPStatusError: on non-2xx responses.
        RuntimeError: if expected data is missing from response.
    """
    params = {
        "lat": lat,
        "lon": lon,
        "properties": SOIL_PROPERTIES,
        "depths": DEPTH,
        "values": VALUE,
    }

    with httpx.Client(timeout=30.0) as client:
        response = client.get(SOILGRIDS_BASE_URL, params=params)
        response.raise_for_status()

    data = response.json()

    layers = {}
    for layer in data.get("properties", {}).get("layers", []):
        depths = layer.get("depths", [])
        if not depths:
            continue
        # Match the requested depth explicitly rather than assuming
        # index 0 corresponds to what we asked for.
        match = next((d for d in depths if d.get("label") == DEPTH), depths[0])
        layers[layer["name"]] = match.get("values", {}).get(VALUE)

    if not layers:
        raise RuntimeError(
            "OpenEPI Soil API returned no soil data for this location."
        )

    return {
        # pH: raw value is pH * 10, so divide by 10
        "ph": round(layers["phh2o"] / 10, 2) if layers.get("phh2o") is not None else None,
        # Organic Carbon Density → real units, divide by 10
        "organic_carbon": round(layers["ocd"] / 10, 2) if layers.get("ocd") is not None else None,
        # Clay content: g/kg → %
        "clay": round(layers["clay"] / 10, 2) if layers.get("clay") is not None else None,
        # Sand content: g/kg → %
        "sand": round(layers["sand"] / 10, 2) if layers.get("sand") is not None else None,
        "source": "OpenEPI Soil API (SoilGrids/ISRIC data)",
        "depth": DEPTH,
    }
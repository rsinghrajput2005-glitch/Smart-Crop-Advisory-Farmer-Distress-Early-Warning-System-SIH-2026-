"""
services/soil_service.py

Fetches soil properties from the free SoilGrids REST API v2 (ISRIC).
No API key required.

Endpoint: https://rest.isric.org/soilgrids/v2.0/properties/query
Docs:     https://rest.isric.org/soilgrids/v2.0/docs
"""

from __future__ import annotations

import requests

SOILGRIDS_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"

# Properties to request (SoilGrids internal names)
SOIL_PROPERTIES = ["phh2o", "ocd", "clay", "sand"]

# Topsoil depth layer (0–30 cm)
DEPTH = "0-30cm"

# Statistical summary to use
VALUE = "mean"


def get_soil_data(lat: float, lon: float) -> dict:
    """
    Fetch soil properties for a farm location from SoilGrids REST API v2.

    Args:
        lat: Farm latitude  (-90 to 90).
        lon: Farm longitude (-180 to 180).

    Returns:
        dict with keys:
            ph              – Soil pH (0–14)
            organic_carbon  – Organic carbon density (g/kg)
            clay            – Clay content (%)
            sand            – Sand content (%)
            depth           – Depth queried
            source          – Data source label

    Raises:
        ValueError:  If coordinates are out of range.
        RuntimeError: If the SoilGrids API call fails.
    """
    if not (-90 <= lat <= 90):
        raise ValueError(f"Latitude {lat} is out of range (-90 to 90).")
    if not (-180 <= lon <= 180):
        raise ValueError(f"Longitude {lon} is out of range (-180 to 180).")

    params = {
        "lon": lon,
        "lat": lat,
        "property": SOIL_PROPERTIES,
        "depth": DEPTH,
        "value": VALUE,
    }

    try:
        response = requests.get(SOILGRIDS_URL, params=params, timeout=30)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise RuntimeError("SoilGrids API timed out. Try again shortly.")
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"SoilGrids API error: {exc}") from exc

    layers = {
        layer["name"]: layer["depths"][0]["values"].get(VALUE)
        for layer in response.json().get("properties", {}).get("layers", [])
        if layer.get("depths")
    }

    # ── Unit conversions ────────────────────────────────────────────────────
    # SoilGrids returns raw integer-scaled values:
    #   phh2o   → pH × 10       (divide by 10 to get real pH)
    #   ocd     → dg/kg         (divide by 10 to get g/kg)
    #   clay    → g/kg          (divide by 10 to get %)
    #   sand    → g/kg          (divide by 10 to get %)

    return {
        "ph": _divide(layers.get("phh2o"), 10),
        "organic_carbon": _divide(layers.get("ocd"), 10),
        "clay": _divide(layers.get("clay"), 10),
        "sand": _divide(layers.get("sand"), 10),
        "depth": DEPTH,
        "source": "SoilGrids ISRIC REST API v2",
    }


def _divide(value, divisor: float):
    """Safely divide a value; return None if value is None or zero-division."""
    try:
        return round(float(value) / divisor, 2)
    except (TypeError, ZeroDivisionError):
        return None

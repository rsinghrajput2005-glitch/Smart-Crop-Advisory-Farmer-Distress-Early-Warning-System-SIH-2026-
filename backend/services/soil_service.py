"""
Soil data service.

Tries OpenEPI's Soil API (api.openepi.io) first, which serves SoilGrids
data. If that call fails for any reason (timeout, connection error, or
a non-2xx/5xx response like the intermittent Cloudflare 530s we've seen),
falls back to static regional topsoil estimates so callers always get a
usable result instead of a 500.

The fallback values are coarse (typical Indian topsoil ranges by region)
and are NOT a substitute for real soil testing — they exist purely so the
app degrades gracefully instead of failing outright when the upstream API
has a bad day.
"""

from __future__ import annotations

import logging

import requests

logger = logging.getLogger(__name__)

OPENEPI_SOIL_URL = "https://api.openepi.io/soil/property"

# Properties to request (SoilGrids property codes)
SOIL_PROPERTIES = ["phh2o", "ocd", "clay", "sand"]

# Topsoil depth layer (0–30 cm)
DEPTH = "0-30cm"

# Statistical summary to use
VALUE = "mean"

# ── Static fallback ──────────────────────────────────────────────────────
# Coarse regional topsoil defaults, used only when the live API is
# unreachable. Keyed by a rough lat/lon bounding box so different parts of
# India get at least a plausible regional estimate rather than one generic
# number nationwide. Extend this table as needed for your target states.
_REGIONAL_FALLBACKS = [
    # (lat_min, lat_max, lon_min, lon_max, values, label)
    (17.0, 22.5, 81.0, 87.5,
     {"ph": 6.2, "organic_carbon": 9.5, "clay": 28.0, "sand": 42.0},
     "Odisha/Jharkhand/Chhattisgarh region default"),
    (21.0, 30.5, 74.0, 89.0,
     {"ph": 7.0, "organic_carbon": 7.0, "clay": 22.0, "sand": 48.0},
     "Indo-Gangetic plain default"),
]

# Used if no regional box matches at all.
_NATIONAL_FALLBACK = {"ph": 6.8, "organic_carbon": 8.0, "clay": 25.0, "sand": 45.0}


def _get_fallback_soil_data(lat: float, lon: float) -> dict:
    """Return coarse static soil estimates when the live API is unavailable."""
    for lat_min, lat_max, lon_min, lon_max, values, label in _REGIONAL_FALLBACKS:
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return {
                **values,
                "depth": DEPTH,
                "source": f"Static fallback estimate ({label}) — live API unavailable",
                "is_fallback": True,
            }
    return {
        **_NATIONAL_FALLBACK,
        "depth": DEPTH,
        "source": "Static fallback estimate (national default) — live API unavailable",
        "is_fallback": True,
    }


def _divide(value, divisor: float):
    """Safely divide a value; return None if value is None or zero-division."""
    try:
        return round(float(value) / divisor, 2)
    except (TypeError, ZeroDivisionError):
        return None


def _fetch_live_soil_data(lat: float, lon: float) -> dict:
    """Fetch soil properties from OpenEPI's Soil API. Raises on any failure."""
    params = {
        "lat": lat,
        "lon": lon,
        "depths": DEPTH,
        "properties": SOIL_PROPERTIES,
        "values": VALUE,
    }

    response = requests.get(OPENEPI_SOIL_URL, params=params, timeout=15)
    response.raise_for_status()

    body = response.json()
    layers_raw = body.get("properties", {}).get("layers", [])

    layers = {}
    for layer in layers_raw:
        name = layer.get("name")
        depths = layer.get("depths", [])
        if not depths:
            continue
        match = next((d for d in depths if d.get("label") == DEPTH), depths[0])
        layers[name] = match.get("values", {}).get(VALUE)

    if not layers:
        raise RuntimeError("OpenEPI Soil API returned no usable soil property data.")

    return {
        "ph": _divide(layers.get("phh2o"), 10),
        "organic_carbon": _divide(layers.get("ocd"), 10),
        "clay": _divide(layers.get("clay"), 10),
        "sand": _divide(layers.get("sand"), 10),
        "depth": DEPTH,
        "source": "OpenEPI Soil API (SoilGrids/ISRIC data)",
        "is_fallback": False,
    }


def get_soil_data(lat: float, lon: float) -> dict:
    """
    Fetch soil properties for a farm location.

    Tries the live OpenEPI Soil API first. If that fails for any reason,
    falls back to static regional topsoil estimates so this function never
    raises for a transient upstream outage — callers always get a dict back.

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
            is_fallback     – True if static fallback values were used
    Raises:
        ValueError: If coordinates are out of range. This is the only
            error still raised — bad input is a caller bug, not a
            transient failure, so it should not be silently papered over.
    """
    if not (-90 <= lat <= 90):
        raise ValueError(f"Latitude {lat} is out of range (-90 to 90).")
    if not (-180 <= lon <= 180):
        raise ValueError(f"Longitude {lon} is out of range (-180 to 180).")

    try:
        return _fetch_live_soil_data(lat, lon)
    except Exception as exc:
        logger.warning(
            "Live soil API failed for (%s, %s): %s — using static fallback.",
            lat, lon, exc,
        )
        return _get_fallback_soil_data(lat, lon)
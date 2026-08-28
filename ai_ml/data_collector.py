from ai_ml.apis.weather_api import get_weather
from ai_ml.apis.soil_api import get_soil_data
from ai_ml.apis.mandi_service import get_mandi_summary
from ai_ml.data_formater import format_soil, format_market


def _safe_float(value):
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_weather_data(raw_weather):
    """Normalize weather payloads so the rest of the pipeline does not depend on raw API keys."""
    if not raw_weather:
        return {
            "available": False,
            "temperature_c": None,
            "humidity_percent": None,
            "precipitation_mm": None,
            "soil_moisture_m3_m3": None,
            "heavy_rain": False,
        }

    current = raw_weather.get("current", {}) or {}
    hourly = raw_weather.get("hourly", {}) or {}
    soil_values = hourly.get("soil_moisture_0_to_1cm", []) or []
    valid_values = [value for value in soil_values if value is not None]
    precipitation = _safe_float(current.get("precipitation"))

    return {
        "available": True,
        "temperature_c": _safe_float(current.get("temperature_2m")),
        "humidity_percent": _safe_float(current.get("relative_humidity_2m")),
        "precipitation_mm": precipitation,
        "soil_moisture_m3_m3": _safe_float(valid_values[0]) if valid_values else None,
        "heavy_rain": bool(precipitation is not None and precipitation >= 50),
    }


def normalize_soil_data(raw_soil_data):
    """Return a compact soil structure without exposing the full SoilGrids payload."""
    if not raw_soil_data:
        return {
            "available": False,
            "ph": None,
            "nitrogen": None,
            "clay_percent": None,
            "sand_percent": None,
            "silt_percent": None,
            "organic_carbon": None,
        }

    return format_soil({"data": raw_soil_data})


def normalize_mandi_data(raw_mandi):
    """Normalize mandi summary payloads into a compact market structure."""
    if not raw_mandi:
        return {"found": False, "commodity": None, "latest_date": None, "markets": []}

    markets = []
    for market in raw_mandi.get("markets", []) or []:
        markets.append(
            {
                "market": market.get("market"),
                "commodity": market.get("commodity"),
                "modal_price": _safe_float(market.get("modal_price")),
                "min_price": _safe_float(market.get("min_price")),
                "max_price": _safe_float(market.get("max_price")),
                "previous_modal_price": _safe_float(market.get("previous_modal_price")),
                "price_change_percent": _safe_float(market.get("price_change_percent")),
                "date": market.get("date"),
            }
        )

    return {
        "found": bool(raw_mandi.get("found", bool(markets))),
        "commodity": raw_mandi.get("commodity"),
        "latest_date": raw_mandi.get("latest_date"),
        "markets": markets,
    }


def collect_all_data(latitude, longitude, state, district, crop):
    """Collect weather, soil and mandi data and normalize them for the rest of the pipeline."""
    weather_data = {
        "available": False,
        "temperature_c": None,
        "humidity_percent": None,
        "precipitation_mm": None,
        "soil_moisture_m3_m3": None,
        "heavy_rain": False,
    }
    soil_data = {
        "available": False,
        "ph": None,
        "nitrogen": None,
        "clay_percent": None,
        "sand_percent": None,
        "silt_percent": None,
        "organic_carbon": None,
    }
    mandi_data = {"found": False, "commodity": crop, "latest_date": None, "markets": []}

    try:
        weather_raw = get_weather(latitude=latitude, longitude=longitude)
        weather_data = normalize_weather_data(weather_raw)
    except Exception as exc:
        print(f"Weather API error: {exc}")

    try:
        soil_raw = get_soil_data(latitude=latitude, longitude=longitude)
        soil_data = normalize_soil_data(soil_raw)
    except Exception as exc:
        print(f"Soil API error: {exc}")

    try:
        mandi_data = normalize_mandi_data(
            get_mandi_summary(state=state, district=district, commodity=crop)
        )
    except Exception as exc:
        print(f"Mandi error: {exc}")

    return {
        "weather": weather_data,
        "soil": soil_data,
        "mandi": mandi_data,
    }
def _safe_float(value):
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def format_weather(weather):
    """Convert weather data into a clean backend-friendly structure."""
    if not weather:
        return {
            "available": False,
            "temperature_c": None,
            "humidity_percent": None,
            "precipitation_mm": None,
            "soil_moisture_m3_m3": None,
            "heavy_rain": False,
        }

    precipitation = weather.get("precipitation")
    if precipitation is None:
        precipitation = weather.get("precipitation_mm")

    soil_moisture = weather.get("soil_moisture")
    if soil_moisture is None:
        soil_moisture = weather.get("soil_moisture_m3_m3")

    return {
        "available": True,
        "temperature_c": _safe_float(weather.get("temperature_c", weather.get("temperature"))),
        "humidity_percent": _safe_float(weather.get("humidity_percent", weather.get("humidity"))),
        "precipitation_mm": _safe_float(precipitation),
        "soil_moisture_m3_m3": _safe_float(soil_moisture),
        "heavy_rain": bool(weather.get("heavy_rain", False)),
    }


def extract_soil_layer(soil_data, layer_name):
    """Extract the 0-5 cm mean value for a SoilGrids property."""
    if not soil_data:
        return None

    properties = soil_data.get("properties", {})
    for layer in properties.get("layers", []) or []:
        if layer.get("name") != layer_name:
            continue

        for depth in layer.get("depths", []) or []:
            if depth.get("label") in {"0-5cm", "0-15cm", "0-30cm"}:
                values = depth.get("values", {}) or {}
                value = values.get("mean")
                if value is not None:
                    return value

        for depth in layer.get("depths", []) or []:
            values = depth.get("values", {}) or {}
            if values.get("mean") is not None:
                return values.get("mean")

    return None


def format_soil(soil):
    """Convert SoilGrids raw response into a compact structure."""
    if not soil:
        return {
            "available": False,
            "ph": None,
            "nitrogen": None,
            "clay_percent": None,
            "sand_percent": None,
            "silt_percent": None,
            "organic_carbon": None,
        }

    if set({"available", "ph", "nitrogen", "clay_percent", "sand_percent", "silt_percent", "organic_carbon"}).issubset(soil.keys()):
        return {
            "available": bool(soil.get("available", False)),
            "ph": soil.get("ph"),
            "nitrogen": soil.get("nitrogen"),
            "clay_percent": soil.get("clay_percent"),
            "sand_percent": soil.get("sand_percent"),
            "silt_percent": soil.get("silt_percent"),
            "organic_carbon": soil.get("organic_carbon"),
        }

    raw_data = soil.get("data") or soil.get("raw_data")
    if not raw_data:
        return {
            "available": False,
            "ph": None,
            "nitrogen": None,
            "clay_percent": None,
            "sand_percent": None,
            "silt_percent": None,
            "organic_carbon": None,
        }

    soil_data = {
        "available": True,
        "ph": extract_soil_layer(raw_data, "phh2o"),
        "nitrogen": extract_soil_layer(raw_data, "nitrogen"),
        "clay_percent": extract_soil_layer(raw_data, "clay"),
        "sand_percent": extract_soil_layer(raw_data, "sand"),
        "silt_percent": extract_soil_layer(raw_data, "silt"),
        "organic_carbon": extract_soil_layer(raw_data, "soc"),
    }
    return soil_data


def format_market(mandi):
    """Convert mandi data into a compact backend-friendly structure."""
    if set({"found", "commodity", "latest_date", "markets"}).issubset(mandi.keys()):
        markets = []
        for market in mandi.get("markets", []) or []:
            markets.append(
                {
                    "name": market.get("name") or market.get("market"),
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
            "found": bool(mandi.get("found", bool(markets))),
            "commodity": mandi.get("commodity"),
            "latest_date": mandi.get("latest_date"),
            "markets": markets,
        }

    markets = []
    for market in mandi.get("markets", []) or []:
        markets.append(
            {
                "name": market.get("market"),
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
        "found": bool(mandi.get("found", bool(markets))),
        "commodity": mandi.get("commodity"),
        "latest_date": mandi.get("latest_date"),
        "markets": markets,
    }


def format_all_data(farmer_data, collected_data):
    """Create the final standardized response for the backend."""
    weather = format_weather(collected_data.get("weather", {}))
    soil = format_soil(collected_data.get("soil", {}))
    market = format_market(collected_data.get("mandi", {}))

    return {
        "location": {
            "latitude": farmer_data.get("latitude"),
            "longitude": farmer_data.get("longitude"),
            "state": farmer_data.get("state"),
            "district": farmer_data.get("district"),
        },
        "crop": {
            "name": farmer_data.get("crop"),
            "stage": farmer_data.get("crop_stage"),
        },
        "weather": weather,
        "soil": soil,
        "market": market,
    }
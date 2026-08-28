import json
from pathlib import Path


def load_crop_rules():
    rules_path = Path(__file__).with_name("crop_rules.json")
    if not rules_path.exists():
        return {}

    with rules_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def prepare_advisory_data(farmer, features, distress, weather=None, soil=None, market=None):
    crop_name = str(farmer.get("crop") or "").strip()
    crop_stage = str(farmer.get("crop_stage") or "").strip()
    crop_rules = load_crop_rules()
    crop_rule = crop_rules.get(crop_name.lower(), {}) if crop_name else {}

    crop_context = {
        "name": crop_name,
        "stage": crop_stage,
        "rules": crop_rule,
        "stage_guidance": crop_rule.get("stages", {}).get(crop_stage.lower(), {}) if isinstance(crop_rule.get("stages"), dict) else {},
    }

    weather_payload = weather or {
        "temperature_c": features.get("temperature"),
        "humidity_percent": features.get("humidity"),
        "precipitation_mm": features.get("precipitation"),
        "soil_moisture_m3_m3": features.get("soil_moisture"),
        "rainfall_deviation_percent": features.get("rainfall_deviation"),
        "heavy_rain": features.get("heavy_rain"),
    }

    market_payload = market or {
        "current_price": features.get("current_market_price"),
        "previous_price": features.get("previous_market_price"),
        "price_change_percent": features.get("market_price_change"),
    }

    return {
        "farmer": {
            "crop": crop_name,
            "crop_stage": crop_stage,
        },
        "weather": weather_payload,
        "soil": soil or {"available": False, "ph": None, "nitrogen": None, "clay_percent": None, "sand_percent": None, "silt_percent": None, "organic_carbon": None},
        "market": market_payload,
        "risk": {
            "score": distress.get("score"),
            "level": distress.get("risk_level"),
            "reasons": distress.get("reasons", []),
        },
        "rainfall": {
            "deviation_percent": features.get("rainfall_deviation"),
            "heavy_rain": features.get("heavy_rain"),
        },
        "crop_context": crop_context,
    }
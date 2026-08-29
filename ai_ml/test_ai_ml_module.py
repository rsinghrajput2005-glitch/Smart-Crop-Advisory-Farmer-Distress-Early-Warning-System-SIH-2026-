import types

import pytest

from ai_ml.data_formater import format_soil, format_weather, format_market
from ai_ml.feature_engineering import build_features
from ai_ml.distress.scoring import calculate_distress_score
from ai_ml.advisory.llm_advisory import generate_farmer_advisory
from ai_ml.run_pipeline import run_pipeline


def test_format_weather_standardizes_output():
    weather = {
        "temperature": 29.4,
        "humidity": 74,
        "precipitation": 0.0,
        "soil_moisture": 0.41,
        "heavy_rain": False,
    }

    result = format_weather(weather)

    assert result["temperature_c"] == 29.4
    assert result["humidity_percent"] == 74
    assert result["precipitation_mm"] == 0.0
    assert result["soil_moisture_m3_m3"] == 0.41
    assert result["heavy_rain"] is False


def test_format_soil_uses_none_for_missing_values():
    soil_raw = {
        "properties": {
            "layers": [
                {
                    "name": "phh2o",
                    "depths": [{"label": "0-5cm", "values": {"mean": 6.7}}],
                },
                {
                    "name": "nitrogen",
                    "depths": [{"label": "0-5cm", "values": {"mean": None}}],
                },
            ]
        }
    }

    result = format_soil({"data": soil_raw})

    assert result["available"] is True
    assert result["ph"] == 6.7
    assert result["nitrogen"] is None
    assert result["clay_percent"] is None


def test_format_market_keeps_market_summary_clean():
    market = {
        "found": True,
        "commodity": "Wheat",
        "latest_date": "2024-02-06",
        "markets": [
            {
                "market": "Nashik",
                "commodity": "Wheat",
                "modal_price": 2831.0,
                "min_price": 2700.0,
                "max_price": 2900.0,
                "price_change_percent": -1.05,
                "date": "2024-02-06",
            }
        ],
    }

    result = format_market(market)

    assert result["found"] is True
    assert result["commodity"] == "Wheat"
    assert result["markets"][0]["name"] == "Nashik"
    assert result["markets"][0]["modal_price"] == 2831.0


def test_build_features_handles_missing_baseline_and_market():
    data = {
        "weather": {
            "temperature": 32,
            "humidity": 70,
            "precipitation": 12,
            "soil_moisture": 0.18,
        },
        "mandi": {
            "markets": [
                {
                    "modal_price": 2800,
                    "previous_modal_price": 2850,
                    "price_change_percent": -1.75,
                }
            ]
        },
    }

    features = build_features(data, normal_rainfall=None)

    assert features["temperature"] == 32
    assert features["rainfall_deviation"] is None
    assert features["soil_moisture"] == 0.18
    assert features["market_price_change"] == -1.75
    assert features["current_market_price"] == 2800


def test_distress_score_returns_risk_and_reasons():
    features = {
        "rainfall_deviation": -35,
        "soil_moisture": 0.18,
        "temperature": 40,
        "heavy_rain": False,
        "market_price_change": -12,
    }

    result = calculate_distress_score(features)

    assert 0 <= result["score"] <= 100
    assert result["risk_level"] in {"LOW", "MEDIUM", "HIGH"}
    assert len(result["reasons"]) >= 1


def test_generate_farmer_advisory_falls_back_without_key(monkeypatch):
    import ai_ml.advisory.llm_advisory as llm_module

    monkeypatch.setattr(llm_module, "client", None, raising=False)

    result = generate_farmer_advisory(
        {
            "farmer": {"crop": "Wheat", "crop_stage": "flowering"},
            "weather": {"temperature": 29, "humidity": 70, "precipitation": 0},
            "soil": {"available": False, "ph": None},
            "market": {"current_price": 2800, "price_change": -1.5},
            "risk": {"score": 20, "level": "LOW", "reasons": []},
        },
        language="English",
    )

    assert "SITUATION:" in result
    assert "RECOMMENDED ACTIONS:" in result
    assert "MARKET:" in result


def test_pipeline_returns_standardized_response(monkeypatch):
    import ai_ml.data_collector as data_collector_module

    sample = {
        "weather": {
            "temperature": 28.5,
            "humidity": 75,
            "precipitation": 0.0,
            "soil_moisture": 0.42,
            "heavy_rain": False,
        },
        "soil": {
            "available": True,
            "ph": 6.4,
            "nitrogen": None,
            "clay_percent": 26,
            "sand_percent": 43,
            "silt_percent": 31,
            "organic_carbon": 0.8,
        },
        "mandi": {
            "found": True,
            "commodity": "Wheat",
            "latest_date": "2024-02-06",
            "markets": [
                {
                    "market": "Nashik",
                    "commodity": "Wheat",
                    "modal_price": 2831.0,
                    "min_price": 2700.0,
                    "max_price": 2900.0,
                    "price_change_percent": -1.05,
                    "date": "2024-02-06",
                }
            ],
        },
    }

    monkeypatch.setattr(data_collector_module, "collect_all_data", lambda **kwargs: sample)

    result = run_pipeline(
        latitude=20.0059,
        longitude=73.7910,
        state="Maharashtra",
        district="nashik",
        crop="Wheat",
        crop_stage="flowering",
        language="English",
        normal_rainfall=None,
    )

    assert result["location"]["state"] == "Maharashtra"
    assert result["crop"]["name"] == "Wheat"
    assert result["weather"]["temperature_c"] == 28.5
    assert result["soil"]["available"] is True
    assert result["market"]["found"] is True
    assert result["distress"]["risk_level"] in {"LOW", "MEDIUM", "HIGH"}
    assert "text" in result["advisory"]

import ai_ml.data_collector as data_collector_module
from ai_ml.data_formater import format_all_data
from ai_ml.feature_engineering import build_features
from ai_ml.distress.scoring import calculate_distress_score
from ai_ml.advisory.advisory_engine import prepare_advisory_data
from ai_ml.advisory.llm_advisory import generate_farmer_advisory
from ai_ml.speech.text_to_speech import text_to_speech


def _normalize_farmer_input(farmer_input=None, **kwargs):
    if farmer_input is not None:
        farmer_input = dict(farmer_input)
        return {
            "latitude": farmer_input.get("latitude", kwargs.get("latitude")),
            "longitude": farmer_input.get("longitude", kwargs.get("longitude")),
            "state": farmer_input.get("state", kwargs.get("state")),
            "district": farmer_input.get("district", kwargs.get("district")),
            "crop": farmer_input.get("crop", kwargs.get("crop")),
            "crop_stage": farmer_input.get("crop_stage", kwargs.get("crop_stage")),
        }

    return {
        "latitude": kwargs.get("latitude"),
        "longitude": kwargs.get("longitude"),
        "state": kwargs.get("state"),
        "district": kwargs.get("district"),
        "crop": kwargs.get("crop"),
        "crop_stage": kwargs.get("crop_stage"),
    }


def run_pipeline(
    latitude=None,
    longitude=None,
    state=None,
    district=None,
    crop=None,
    crop_stage=None,
    language="English",
    normal_rainfall=None,
    farmer_input=None,
    generate_audio=False,
    audio_output_dir=None,
):
    """Run the complete AI/ML pipeline and return a backend-friendly dictionary."""
    farmer_data = _normalize_farmer_input(
        farmer_input=farmer_input,
        latitude=latitude,
        longitude=longitude,
        state=state,
        district=district,
        crop=crop,
        crop_stage=crop_stage,
    )

    if farmer_data.get("latitude") is None or farmer_data.get("longitude") is None:
        raise ValueError("latitude and longitude are required.")
    if not farmer_data.get("crop"):
        raise ValueError("crop is required.")

    collected_data = data_collector_module.collect_all_data(
        latitude=farmer_data["latitude"],
        longitude=farmer_data["longitude"],
        state=farmer_data.get("state"),
        district=farmer_data.get("district"),
        crop=farmer_data["crop"],
    )

    formatted_data = format_all_data(farmer_data, collected_data)
    features = build_features(formatted_data, normal_rainfall=normal_rainfall)
    distress = calculate_distress_score(features)

    advisory_data = prepare_advisory_data(
        farmer={
            "crop": farmer_data.get("crop"),
            "crop_stage": farmer_data.get("crop_stage"),
        },
        features=features,
        distress=distress,
        weather=formatted_data.get("weather"),
        soil=formatted_data.get("soil"),
        market=formatted_data.get("market"),
    )

    advisory_text = generate_farmer_advisory(advisory_data, language=language)

    result = {
        "location": formatted_data["location"],
        "crop": formatted_data["crop"],
        "weather": formatted_data["weather"],
        "soil": formatted_data["soil"],
        "market": formatted_data["market"],
        "features": features,
        "distress": distress,
        "advisory": {
            "text": advisory_text,
            "language": language,
        },
    }

    if generate_audio:
        try:
            audio_path = text_to_speech(advisory_text, language=language, output_path=audio_output_dir)
            result["advisory"]["audio"] = {"path": audio_path, "format": "wav"}
        except Exception as exc:
            result["advisory"]["audio"] = {"status": "not_generated", "error": str(exc)}

    return result


def main():
    example = run_pipeline(
        latitude=20.0059,
        longitude=73.7910,
        state="Maharashtra",
        district="nashik",
        crop="Wheat",
        crop_stage="flowering",
        language="English",
    )

    import json
    print(json.dumps(example, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
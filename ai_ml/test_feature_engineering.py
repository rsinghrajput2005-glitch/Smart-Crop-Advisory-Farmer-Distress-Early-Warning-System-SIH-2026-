from ai_ml.data_collector import (
    collect_all_data
)

from ai_ml.feature_engineering import (
    build_features
)


def main():

    # --------------------------------
    # Farmer information
    # --------------------------------

    latitude = 20.0059
    longitude = 73.7910

    state = "Maharashtra"
    district = "nashik"
    crop = "Wheat"

    # --------------------------------
    # Collect REAL data
    # --------------------------------

    collected_data = collect_all_data(

        latitude=latitude,

        longitude=longitude,

        state=state,

        district=district,

        crop=crop
    )

    print(
        "\n========== RAW DATA ==========\n"
    )

    print(
        collected_data
    )

    # --------------------------------
    # Feature engineering
    # --------------------------------

    features = build_features(
        collected_data
    )

    print(
        "\n========== FEATURES ==========\n"
    )

    for key, value in features.items():

        print(
            f"{key}: {value}"
        )

    print(
        "\n==============================\n"
    )


if __name__ == "__main__":

    main()
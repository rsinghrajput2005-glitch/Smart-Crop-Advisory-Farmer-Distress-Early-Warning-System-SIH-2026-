from ai_ml.data_collector import (
    collect_all_data
)

from ai_ml.data_formater import (
    format_all_data
)


def main():

    farmer_data = {

        "latitude": 20.0059,

        "longitude": 73.791,

        "state": "Maharashtra",

        "district": "nashik",

        "crop": "Wheat",

        "crop_stage": "flowering"
    }


    print(
        "\nCollecting data..."
    )


    collected_data = collect_all_data(

        latitude=farmer_data[
            "latitude"
        ],

        longitude=farmer_data[
            "longitude"
        ],

        state=farmer_data[
            "state"
        ],

        district=farmer_data[
            "district"
        ],

        crop=farmer_data[
            "crop"
        ]
    )


    final_data = format_all_data(

        farmer_data,

        collected_data
    )


    print(
        "\n========== CLEAN DATA ==========\n"
    )


    import json

    print(
        json.dumps(
            final_data,
            indent=2,
            ensure_ascii=False
        )
    )


    print(
        "\n================================\n"
    )


if __name__ == "__main__":

    main()
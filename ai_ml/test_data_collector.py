from ai_ml.data_collector import (
    collect_all_data
)


def main():

    # Example:
    # Nashik coordinates
    # Replace with farmer's actual location later.

    result = collect_all_data(

        latitude=20.0059,

        longitude=73.7910,

        state="Maharashtra",

        district="nashik",

        crop="Wheat"
    )

    print(
        "\n\n========== FINAL DATA ==========\n"
    )

    print(
        result
    )

    print(
        "\n================================\n"
    )


if __name__ == "__main__":

    main()
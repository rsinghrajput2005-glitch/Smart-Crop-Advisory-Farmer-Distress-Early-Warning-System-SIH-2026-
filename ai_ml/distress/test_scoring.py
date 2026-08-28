from ai_ml.distress.scoring import (
    calculate_distress_score
)


def main():

    features = {

        "temperature": 38,

        "rainfall_deviation": -35,

        "soil_moisture": 0.18,

        "heavy_rain": False,

        "market_price_change": -15
    }

    result = calculate_distress_score(
        features
    )

    print(
        "\n========== DISTRESS RESULT ==========\n"
    )

    print(
        "Score:",
        result["score"]
    )

    print(
        "Risk Level:",
        result["risk_level"]
    )

    print(
        "\nReasons:"
    )

    for reason in result["reasons"]:

        print(
            "-",
            reason
        )

    print(
        "\n======================================\n"
    )


if __name__ == "__main__":

    main()
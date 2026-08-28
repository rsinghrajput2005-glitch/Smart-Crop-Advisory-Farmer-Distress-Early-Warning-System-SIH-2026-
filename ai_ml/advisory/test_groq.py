from ai_ml.advisory.llm_advisory import (
    generate_advisory
)


def main():

    context = {

        "crop": "paddy",

        "crop_stage": "flowering",

        "rainfall_deviation": -35,

        "temperature": 32,

        "soil_moisture": 20,

        "heavy_rain": False,

        "market_price_change": -5,

        "detected_conditions": [
            "rainfall_deficit",
            "low_soil_moisture"
        ]
    }

    farmer_question = (
        "My paddy crop is not getting "
        "enough rainfall. What should I do?"
    )

    result = generate_advisory(
        context,
        farmer_question
    )

    print("\n========== GROQ ADVISORY ==========\n")

    print(result)

    print("\n====================================")


if __name__ == "__main__":
    main()
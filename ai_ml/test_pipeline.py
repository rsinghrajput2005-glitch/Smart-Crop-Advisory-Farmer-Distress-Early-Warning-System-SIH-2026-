import json

from ai_ml.run_pipeline import run_pipeline


def main():

    result = run_pipeline(
        latitude=20.0059,
        longitude=73.7910,
        state="Maharashtra",
        district="nashik",
        crop="Wheat",
        crop_stage="flowering",
        language="English"
    )

    print("\n========== FINAL RESULT ==========\n")

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )

    print(
        "\n==================================\n"
    )


if __name__ == "__main__":
    main()
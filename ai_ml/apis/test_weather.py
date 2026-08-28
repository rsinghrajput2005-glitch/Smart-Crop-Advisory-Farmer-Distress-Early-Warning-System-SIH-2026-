from ai_ml.apis.weather_api import get_weather


def main():

    # Example coordinates
    # Replace with actual farmer location later.

    latitude = 19.8135
    longitude = 85.8312

    data = get_weather(
        latitude,
        longitude
    )

    print("\n========== WEATHER ==========\n")

    print(
        "Current:",
        data.get("current")
    )

    print("\nDaily:")
    print(
        data.get("daily")
    )

    print("\n=============================")


if __name__ == "__main__":
    main()
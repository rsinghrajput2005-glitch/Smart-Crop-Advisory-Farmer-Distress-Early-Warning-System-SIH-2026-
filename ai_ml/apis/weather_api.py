import requests


OPEN_METEO_URL = (
    "https://api.open-meteo.com/v1/forecast"
)


def get_weather(latitude, longitude):

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "current": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation"
        ]),

        "hourly": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "soil_moisture_0_to_1cm"
        ]),

        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum"
        ]),

        "forecast_days": 7,

        "timezone": "auto"
    }

    response = requests.get(
        OPEN_METEO_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()
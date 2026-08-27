"""
Weather external API client using Open-Meteo (free, no API key required).
Fetches current weather conditions and a 7-day forecast for a lat/lon.
Docs: https://open-meteo.com/en/docs
"""

import httpx

OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"

CURRENT_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "weather_code",
    "wind_speed_10m",
    "wind_direction_10m",
    "apparent_temperature",
    "surface_pressure",
]

DAILY_VARIABLES = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "rain_sum",
    "weather_code",
    "wind_speed_10m_max",
    "sunrise",
    "sunset",
]


def fetch_weather_data(lat: float, lon: float) -> dict:
    """
    Fetch current weather and 7-day daily forecast from Open-Meteo.

    Args:
        lat: Latitude of the farm location.
        lon: Longitude of the farm location.

    Returns:
        dict with 'current' (live conditions) and 'forecast' (7-day daily list).

    Raises:
        httpx.HTTPStatusError: on non-2xx responses.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ",".join(CURRENT_VARIABLES),
        "daily": ",".join(DAILY_VARIABLES),
        "timezone": "Asia/Kolkata",
        "forecast_days": 7,
    }

    with httpx.Client(timeout=20.0) as client:
        response = client.get(OPEN_METEO_BASE_URL, params=params)
        response.raise_for_status()

    data = response.json()

    current = data.get("current", {})
    daily = data.get("daily", {})

    forecast_days = len(daily.get("time", []))
    forecast = [
        {
            "date": daily["time"][i],
            "temp_max": daily["temperature_2m_max"][i],
            "temp_min": daily["temperature_2m_min"][i],
            "precipitation_sum_mm": daily["precipitation_sum"][i],
            "rain_sum_mm": daily["rain_sum"][i],
            "weather_code": daily["weather_code"][i],
            "wind_speed_max_kmh": daily["wind_speed_10m_max"][i],
            "sunrise": daily["sunrise"][i],
            "sunset": daily["sunset"][i],
        }
        for i in range(forecast_days)
    ]

    return {
        "current": {
            "temperature_c": current.get("temperature_2m"),
            "feels_like_c": current.get("apparent_temperature"),
            "humidity_pct": current.get("relative_humidity_2m"),
            "precipitation_mm": current.get("precipitation"),
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "wind_direction_deg": current.get("wind_direction_10m"),
            "pressure_hpa": current.get("surface_pressure"),
            "weather_code": current.get("weather_code"),
            "time": current.get("time"),
        },
        "forecast": forecast,
        "source": "Open-Meteo",
        "units": {
            "temperature": "°C",
            "precipitation": "mm",
            "wind_speed": "km/h",
            "pressure": "hPa",
        },
    }

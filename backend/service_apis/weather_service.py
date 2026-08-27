"""
Weather service — orchestrates Open-Meteo data fetching and risk assessment.
Sits between the API router and the external_apis.weather client.
"""

from backend.external_apis.weather import fetch_weather_data

# WMO Weather Interpretation Codes (subset)
WMO_CODE_MAP = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with heavy hail",
}


def get_weather_data(lat: float, lon: float) -> dict:
    """
    Retrieve current weather and 7-day forecast with risk assessment.

    Args:
        lat: Latitude of the farm.
        lon: Longitude of the farm.

    Returns:
        Weather dict with current conditions, 7-day forecast, and weather risk level.

    Raises:
        ValueError: if coordinates are invalid.
        RuntimeError: if Open-Meteo is unreachable.
    """
    if not (-90 <= lat <= 90):
        raise ValueError(f"Invalid latitude: {lat}.")
    if not (-180 <= lon <= 180):
        raise ValueError(f"Invalid longitude: {lon}.")

    try:
        weather = fetch_weather_data(lat=lat, lon=lon)
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch weather data: {exc}") from exc

    # Decode WMO weather code to description
    current_code = weather["current"].get("weather_code")
    weather["current"]["condition"] = WMO_CODE_MAP.get(current_code, "Unknown")

    for day in weather["forecast"]:
        day["condition"] = WMO_CODE_MAP.get(day.get("weather_code"), "Unknown")

    # Assess weather risk for crop advisory
    weather["weather_risk"] = _assess_weather_risk(weather)

    return weather


def _assess_weather_risk(weather: dict) -> dict:
    """
    Assess weather-related risk level for crop distress model.

    Returns:
        dict with risk_level (Low/Medium/High) and risk_factors list.
    """
    risk_factors = []
    risk_score = 0

    current = weather.get("current", {})
    forecast = weather.get("forecast", [])

    temp = current.get("temperature_c")
    if temp is not None:
        if temp > 42:
            risk_factors.append("Extreme heat stress (>42°C)")
            risk_score += 3
        elif temp > 38:
            risk_factors.append("High temperature stress (>38°C)")
            risk_score += 2
        elif temp < 5:
            risk_factors.append("Cold stress risk (<5°C)")
            risk_score += 2

    humidity = current.get("humidity_pct")
    if humidity is not None:
        if humidity > 90:
            risk_factors.append("Very high humidity — fungal disease risk")
            risk_score += 2
        elif humidity < 20:
            risk_factors.append("Very low humidity — drought stress risk")
            risk_score += 1

    total_forecast_rain = sum(
        d.get("precipitation_sum_mm", 0) or 0 for d in forecast
    )
    if total_forecast_rain > 150:
        risk_factors.append(f"Heavy rainfall forecast: {total_forecast_rain:.1f} mm over 7 days")
        risk_score += 3
    elif total_forecast_rain < 5:
        risk_factors.append("Very low rainfall forecast — irrigation needed")
        risk_score += 1

    high_wind_days = sum(
        1 for d in forecast if (d.get("wind_speed_max_kmh") or 0) > 60
    )
    if high_wind_days > 0:
        risk_factors.append(f"High wind days in forecast: {high_wind_days}")
        risk_score += high_wind_days

    if risk_score >= 6:
        risk_level = "High"
    elif risk_score >= 3:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "risk_factors": risk_factors,
    }

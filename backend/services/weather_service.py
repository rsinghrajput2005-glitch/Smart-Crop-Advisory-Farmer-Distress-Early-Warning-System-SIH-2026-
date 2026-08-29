"""
Weather service — orchestrates Open-Meteo data fetching and risk assessment.
Sits between the API router and the external_apis.weather client.

If Open-Meteo is unreachable or errors out, falls back to seeded mock data
so callers always get a usable response instead of a 500/503 — same
resilience pattern used in soil_service.py.
"""

import logging
import random
from datetime import datetime, timedelta

from backend.external_apis.weather import fetch_weather_data

logger = logging.getLogger(__name__)

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

    Tries the live Open-Meteo API first. If that fails for any reason
    (network error, timeout, non-2xx response), falls back to seeded
    mock data so this function never raises for a transient upstream
    outage — callers always get a usable dict back.

    Args:
        lat: Latitude of the farm.
        lon: Longitude of the farm.

    Returns:
        Weather dict with current conditions, 7-day forecast, and weather risk level.

    Raises:
        ValueError: if coordinates are invalid. This is the only error
            still raised — bad input is a caller bug, not a transient
            failure, so it should not be silently papered over.
    """
    if not (-90 <= lat <= 90):
        raise ValueError(f"Invalid latitude: {lat}.")
    if not (-180 <= lon <= 180):
        raise ValueError(f"Invalid longitude: {lon}.")

    try:
        weather = fetch_weather_data(lat=lat, lon=lon)
    except Exception as exc:
        logger.warning(
            "Live weather API failed for (%s, %s): %s — using fallback mock data.",
            lat, lon, exc,
        )
        return _mock_weather(lat, lon)

    # Decode WMO weather code to description
    current_code = weather["current"].get("weather_code")
    weather["current"]["condition"] = WMO_CODE_MAP.get(current_code, "Unknown")

    for day in weather["forecast"]:
        day["condition"] = WMO_CODE_MAP.get(day.get("weather_code"), "Unknown")

    # Assess weather risk for crop advisory
    weather["weather_risk"] = _assess_weather_risk(weather)
    weather["is_fallback"] = False

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


# ── Fallback mock weather (used only when Open-Meteo is unreachable) ────────

def _mock_weather(lat: float, lon: float) -> dict:
    """
    Return seeded, location-stable mock weather data shaped exactly like the
    live Open-Meteo response, so callers (advisory/risk endpoints, frontend)
    don't need any special-casing when the live API is down.
    """
    # Seed on coordinates so the same farm location gets consistent demo
    # numbers across repeated calls, instead of random values each time.
    rng = random.Random(int(abs(lat * 1000 + lon * 100)) % 999999)

    temp = round(rng.uniform(22.0, 36.0), 1)
    humidity = rng.randint(45, 85)
    pressure = 1008 + rng.randint(-6, 6)
    wind = round(rng.uniform(6.0, 22.0), 1)
    current_code = rng.choice([0, 1, 2, 3, 61, 80])

    current = {
        "temperature_c": temp,
        "feels_like_c": round(temp + rng.uniform(0.5, 2.5), 1),
        "humidity_pct": humidity,
        "precipitation_mm": round(rng.uniform(0.0, 3.0), 2),
        "wind_speed_kmh": wind,
        "wind_direction_deg": rng.randint(0, 360),
        "pressure_hpa": pressure,
        "weather_code": current_code,
        "condition": WMO_CODE_MAP.get(current_code, "Unknown"),
        "time": datetime.utcnow().isoformat(),
    }

    forecast = []
    for i in range(7):
        day_date = datetime.utcnow() + timedelta(days=i + 1)
        day_code = rng.choice([0, 1, 2, 3, 61, 63, 80])
        t_max = round(temp + rng.uniform(1, 4), 1)
        t_min = round(temp - rng.uniform(3, 7), 1)
        precip = round(rng.uniform(0.0, 12.0), 1)
        forecast.append({
            "date": day_date.strftime("%Y-%m-%d"),
            "temp_max": t_max,
            "temp_min": t_min,
            "precipitation_sum_mm": precip,
            "rain_sum_mm": precip,
            "weather_code": day_code,
            "condition": WMO_CODE_MAP.get(day_code, "Unknown"),
            "wind_speed_max_kmh": round(rng.uniform(10.0, 35.0), 1),
            "sunrise": None,
            "sunset": None,
        })

    weather = {
        "current": current,
        "forecast": forecast,
        "source": "Fallback estimate — live weather API unavailable",
        "units": {
            "temperature": "°C",
            "rainfall": "mm",
            "wind_speed": "km/h",
            "pressure": "hPa",
        },
        "is_fallback": True,
    }
    weather["weather_risk"] = _assess_weather_risk(weather)
    return weather
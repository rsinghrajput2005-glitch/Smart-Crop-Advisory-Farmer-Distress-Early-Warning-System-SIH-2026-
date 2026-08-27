"""
services/weather_service.py

Fetches current weather and 5-day/3-hour forecast from OpenWeatherMap.
Requires OPENWEATHER_API_KEY set in the .env file.

Free plan docs: https://openweathermap.org/api/one-call-3
Current weather: https://api.openweathermap.org/data/2.5/weather
5-day forecast:  https://api.openweathermap.org/data/2.5/forecast

Falls back to realistic mock data when no API key is provided (demo mode).
"""

from __future__ import annotations

import os
import random
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

CURRENT_URL  = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

# WMO-style condition map (OpenWeatherMap weather ID ranges)
_CONDITION_MAP = {
    (200, 299): "Thunderstorm",
    (300, 399): "Drizzle",
    (500, 531): "Rain",
    (600, 622): "Snow",
    (700, 781): "Haze / Fog",
    (800, 800): "Clear Sky",
    (801, 804): "Cloudy",
}

def _weather_id_to_condition(code: int) -> str:
    for (lo, hi), label in _CONDITION_MAP.items():
        if lo <= code <= hi:
            return label
    return "Unknown"


def get_weather_data(lat: float, lon: float) -> dict:
    """
    Fetch current weather conditions and 5-day forecast for a farm location.

    Uses OpenWeatherMap free API tier (requires OPENWEATHER_API_KEY in .env).
    Falls back to realistic mock data when key is absent (demo mode).

    Args:
        lat: Farm latitude  (-90 to 90).
        lon: Farm longitude (-180 to 180).

    Returns:
        dict with keys:
            current      – dict: temperature_c, humidity_pct, rainfall_mm,
                                  condition, wind_speed_kmh, pressure_hpa
            forecast     – list of daily summaries
            weather_risk – dict: risk_level, risk_score, risk_factors
            source       – data source label
            units        – unit labels
    """
    if not (-90 <= lat <= 90):
        raise ValueError(f"Latitude {lat} is out of range (-90 to 90).")
    if not (-180 <= lon <= 180):
        raise ValueError(f"Longitude {lon} is out of range (-180 to 180).")

    # ── No API key → return mock data for demo ──────────────────────────────
    if not OPENWEATHER_API_KEY:
        return _mock_weather(lat, lon)

    common_params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
    }

    # ── Current weather ──────────────────────────────────────────────────────
    try:
        current_resp = requests.get(CURRENT_URL, params=common_params, timeout=15)
        current_resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        # Fallback to mock on any network error
        return _mock_weather(lat, lon)

    cw = current_resp.json()
    weather_id = cw["weather"][0]["id"]
    current = {
        "temperature_c":     cw["main"]["temp"],
        "feels_like_c":      cw["main"]["feels_like"],
        "humidity_pct":      cw["main"]["humidity"],
        "pressure_hpa":      cw["main"]["pressure"],
        "rainfall_mm":       cw.get("rain", {}).get("1h", 0.0),
        "wind_speed_kmh":    round(cw["wind"]["speed"] * 3.6, 2),
        "wind_direction_deg": cw["wind"].get("deg"),
        "description":       cw["weather"][0]["description"].title(),
        "condition":         _weather_id_to_condition(weather_id),
        "icon":              cw["weather"][0]["icon"],
        "city":              cw.get("name"),
        "time":              cw.get("dt"),
    }

    # ── 5-day / 3-hour forecast → collapse to daily summaries ───────────────
    try:
        forecast_resp = requests.get(
            FORECAST_URL, params={**common_params, "cnt": 40}, timeout=15
        )
        forecast_resp.raise_for_status()
    except requests.exceptions.RequestException:
        forecast = []
    else:
        forecast = _parse_forecast(forecast_resp.json().get("list", []))

    weather_risk = _compute_weather_risk(current, forecast)

    return {
        "current":      current,
        "forecast":     forecast,
        "weather_risk": weather_risk,
        "source":       "OpenWeatherMap API",
        "units": {
            "temperature":  "°C",
            "rainfall":     "mm",
            "wind_speed":   "km/h",
            "pressure":     "hPa",
        },
    }


def _parse_forecast(items: list) -> list[dict]:
    """Collapse 3-hourly forecast entries into one summary per calendar date."""
    from collections import defaultdict

    daily: dict[str, dict] = defaultdict(lambda: {
        "temps": [], "rainfall_mm": 0.0, "descriptions": [], "codes": []
    })

    for item in items:
        date = item["dt_txt"][:10]
        daily[date]["temps"].append(item["main"]["temp"])
        daily[date]["rainfall_mm"] += item.get("rain", {}).get("3h", 0.0)
        daily[date]["descriptions"].append(item["weather"][0]["description"].title())
        daily[date]["codes"].append(item["weather"][0]["id"])

    result = []
    for date, data in sorted(daily.items())[:5]:
        temps = data["temps"]
        dominant_code = max(set(data["codes"]), key=data["codes"].count)
        result.append({
            "date":          date,
            "temp_max_c":    round(max(temps), 1),
            "temp_min_c":    round(min(temps), 1),
            "rainfall_mm":   round(data["rainfall_mm"], 2),
            "description":   max(set(data["descriptions"]), key=data["descriptions"].count),
            "condition":     _weather_id_to_condition(dominant_code),
        })
    return result


def _compute_weather_risk(current: dict, forecast: list) -> dict:
    """
    Compute an agricultural weather risk assessment.

    Risk factors considered:
      - High temperature (>38°C) or Low temperature (<10°C)
      - High humidity (>85%)
      - High wind speed (>50 km/h)
      - Heavy rainfall in forecast (>20 mm/day)
      - Thunderstorm / cyclone condition

    Returns:
        dict with risk_level (Low/Medium/High), risk_score (0–100),
        and risk_factors (list of strings).
    """
    factors = []
    score = 0

    temp = current.get("temperature_c", 25.0)
    humidity = current.get("humidity_pct", 60.0)
    wind = current.get("wind_speed_kmh", 10.0)
    condition = current.get("condition", "")
    rain = current.get("rainfall_mm", 0.0)

    if temp >= 40:
        factors.append("Extreme heat (≥40°C) — heat stress risk for crops")
        score += 30
    elif temp >= 38:
        factors.append("High temperature (≥38°C) — monitor irrigation")
        score += 15
    elif temp <= 5:
        factors.append("Near-freezing temperature — frost risk")
        score += 30
    elif temp <= 10:
        factors.append("Low temperature (≤10°C) — cold stress possible")
        score += 15

    if humidity >= 90:
        factors.append("Very high humidity (≥90%) — disease/fungal risk")
        score += 20
    elif humidity >= 80:
        factors.append("High humidity (≥80%) — monitor for blight")
        score += 10

    if wind >= 60:
        factors.append("Very high wind speed (≥60 km/h) — lodging risk")
        score += 25
    elif wind >= 40:
        factors.append("High wind speed (≥40 km/h) — monitor crops")
        score += 12

    if "Thunderstorm" in condition:
        factors.append("Active thunderstorm — avoid field operations")
        score += 25

    # Check forecast for heavy rain days
    heavy_rain_days = [
        d["date"] for d in forecast if d.get("rainfall_mm", 0) > 20
    ]
    if len(heavy_rain_days) >= 3:
        factors.append(f"Heavy rainfall forecast for {len(heavy_rain_days)} days — waterlogging risk")
        score += 20
    elif heavy_rain_days:
        factors.append(f"Heavy rainfall forecast on {', '.join(heavy_rain_days)}")
        score += 10

    # Erratic rainfall: check if some days have 0mm and others >15mm
    rain_amounts = [d.get("rainfall_mm", 0) for d in forecast]
    if rain_amounts:
        if max(rain_amounts) > 15 and min(rain_amounts) == 0 and len(rain_amounts) >= 3:
            factors.append("Erratic rainfall pattern — uneven crop water availability")
            score += 10

    score = min(score, 100)

    if score >= 50:
        risk_level = "High"
    elif score >= 25:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    if not factors:
        factors.append("No significant weather risks detected")

    return {
        "risk_level":   risk_level,
        "risk_score":   score,
        "risk_factors": factors,
    }


# ── Mock weather (demo / no-API-key mode) ────────────────────────────────────

def _mock_weather(lat: float, lon: float) -> dict:
    """Return realistic mock weather data for demo purposes."""
    random.seed(int(abs(lat * 1000 + lon * 100)) % 9999)

    temp = round(random.uniform(24.0, 36.0), 1)
    humidity = random.randint(55, 85)
    wind = round(random.uniform(8.0, 28.0), 1)

    current = {
        "temperature_c":     temp,
        "feels_like_c":      round(temp + random.uniform(1.0, 3.0), 1),
        "humidity_pct":      humidity,
        "pressure_hpa":      1010 + random.randint(-5, 5),
        "rainfall_mm":       round(random.uniform(0.0, 4.0), 2),
        "wind_speed_kmh":    wind,
        "wind_direction_deg": random.randint(0, 360),
        "description":       random.choice(["Partly Cloudy", "Clear Sky", "Light Rain", "Overcast"]),
        "condition":         random.choice(["Cloudy", "Clear Sky", "Rain"]),
        "icon":              "02d",
        "city":              "Demo Location",
        "time":              int(datetime.utcnow().timestamp()),
    }

    forecast = []
    base_rain_pattern = [0.0, 2.5, 18.0, 5.0, 0.0]
    for i in range(5):
        day = datetime.utcnow() + timedelta(days=i + 1)
        forecast.append({
            "date":        day.strftime("%Y-%m-%d"),
            "temp_max_c":  round(temp + random.uniform(1, 4), 1),
            "temp_min_c":  round(temp - random.uniform(3, 7), 1),
            "rainfall_mm": base_rain_pattern[i] + random.uniform(-1, 2),
            "description": random.choice(["Partly Cloudy", "Light Rain", "Clear"]),
            "condition":   random.choice(["Cloudy", "Rain", "Clear Sky"]),
        })

    weather_risk = _compute_weather_risk(current, forecast)

    return {
        "current":      current,
        "forecast":     forecast,
        "weather_risk": weather_risk,
        "source":       "Mock Data (Demo Mode — add OPENWEATHER_API_KEY for live data)",
        "units": {
            "temperature":  "°C",
            "rainfall":     "mm",
            "wind_speed":   "km/h",
            "pressure":     "hPa",
        },
    }

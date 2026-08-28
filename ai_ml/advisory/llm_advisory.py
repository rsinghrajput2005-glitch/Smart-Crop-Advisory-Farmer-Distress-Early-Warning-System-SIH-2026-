import os
from pathlib import Path

from dotenv import load_dotenv

try:
    from groq import Groq
except ImportError:  # pragma: no cover
    Groq = None


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if Groq and api_key else None
MODEL_NAME = "llama-3.3-70b-versatile"


def _fallback_advisory(advisory_data, language="English"):
    crop = advisory_data.get("farmer", {}).get("crop") or "crop"
    stage = advisory_data.get("farmer", {}).get("crop_stage") or "current stage"
    weather = advisory_data.get("weather", {})
    soil = advisory_data.get("soil", {})
    market = advisory_data.get("market", {})
    risk = advisory_data.get("risk", {})
    risk_level = risk.get("level") or "LOW"
    reasons = risk.get("reasons") or []

    situation = (
        f"For {crop} at the {stage} stage, the current data indicates a {risk_level.lower()} distress signal "
        f"from the available information. Weather shows {weather.get('temperature_c')}°C, "
        f"humidity {weather.get('humidity_percent')}%, and precipitation {weather.get('precipitation_mm')} mm. "
        f"Soil data is {'available' if soil.get('available') else 'not available'}; missing soil values were not assumed."
    )

    if reasons:
        reason_text = "; ".join(reasons)
    else:
        reason_text = "No major alert was detected from the current available data."

    market_text = (
        f"The current mandi price is {market.get('current_price')} and the price change is {market.get('price_change_percent')}%. "
        f"The absolute price change should be interpreted alongside the percent change."
    )

    return f"""SITUATION:
{ situation }

RECOMMENDED ACTIONS:
- Review field conditions and keep a close watch on crop stress signs during the {stage} stage.
- Use local agronomic practices and check the current soil and weather status before making any changes.
- Focus on field observation and timely action rather than guessing from missing values.

WHAT TO MONITOR:
- Soil moisture, rainfall pattern, and temperature trends.
- New stress symptoms in the crop canopy or root zone.
- Market movement and price changes before selling.

MARKET:
{market_text}

RISK:
Risk level: {risk_level}. Detected reasons: {reason_text}.

Note: This advisory is based on the information currently available. Missing values were not invented.
"""


def generate_farmer_advisory(advisory_data, language="English"):
    if client is None:
        return _fallback_advisory(advisory_data, language=language)

    crop = advisory_data.get("farmer", {}).get("crop") or "crop"
    stage = advisory_data.get("farmer", {}).get("crop_stage") or "current stage"
    weather = advisory_data.get("weather", {})
    soil = advisory_data.get("soil", {})
    market = advisory_data.get("market", {})
    risk = advisory_data.get("risk", {})
    rainfall = advisory_data.get("rainfall", {})

    prompt = f"""
You are an agricultural advisory assistant for Indian farmers.
Use only the information provided below. Do not invent missing values.

Crop: {crop}
Crop stage: {stage}
Language: {language}

Weather:
{weather}

Soil:
{soil}

Market:
{market}

Rainfall:
{rainfall}

Distress analysis:
{risk}

Important rules:
1. Never invent missing values or assume null soil values.
2. Do not create arbitrary numerical thresholds.
3. Do not recommend pesticides, fertilizers or irrigation quantities without sufficient evidence.
4. Do not say the crop is healthy only because the risk is LOW.
5. LOW means no major distress indicator was detected from the available data.
6. Market advice must clearly distinguish percentage price change from the absolute price value.
7. Use simple language suitable for farmers.
8. Keep the answer concise and actionable.
9. Consider crop stage and crop type.

Format the response exactly as follows:

SITUATION:
...

RECOMMENDED ACTIONS:
- ...
- ...
- ...

WHAT TO MONITOR:
- ...
- ...

MARKET:
...

RISK:
...
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You provide safe and practical agricultural guidance for farmers. Keep it simple, conservative, and evidence-based.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=700,
        )
        content = response.choices[0].message.content
        if not content:
            return _fallback_advisory(advisory_data, language=language)
        return content.strip()
    except Exception:
        return _fallback_advisory(advisory_data, language=language)
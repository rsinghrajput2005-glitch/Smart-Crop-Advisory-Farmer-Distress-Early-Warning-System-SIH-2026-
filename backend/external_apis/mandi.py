"""
Mandi (Agricultural Market) external API client.
Uses the Government of India data.gov.in API — AGMARKNET daily arrivals & prices.
API resource: Agmarknet Price & Arrival Data (OGD Platform India)

API Docs: https://data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi
Requires a free API key from https://data.gov.in — set DATAGOV_API_KEY in .env

Falls back to realistic mock data when DATAGOV_API_KEY is absent (demo mode).
"""

import os
import random
from datetime import date, datetime, timedelta

import httpx
from dotenv import load_dotenv

load_dotenv()

DATAGOV_API_KEY = os.getenv("DATAGOV_API_KEY", "")

# AGMARKNET resource ID on data.gov.in
AGMARKNET_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
DATAGOV_BASE_URL = "https://api.data.gov.in/resource"

DEFAULT_LIMIT = 50

# ── Mock price data ────────────────────────────────────────────────────────────
_CROP_BASE_PRICES: dict[str, int] = {
    "rice": 2000, "wheat": 2100, "maize": 1800, "tomato": 900,
    "onion": 800, "potato": 700, "soybean": 4200, "cotton": 6200,
    "sugarcane": 350, "mustard": 5200,
}

_MOCK_MANDIS = [
    ("Bhubaneswar Mandi", "Odisha", "Khordha"),
    ("Cuttack Agricultural Market", "Odisha", "Cuttack"),
    ("Puri Mandi", "Odisha", "Puri"),
    ("Sambalpur Market Yard", "Odisha", "Sambalpur"),
    ("Berhampur APMC", "Odisha", "Ganjam"),
    ("Rourkela Mandi", "Odisha", "Sundargarh"),
]

_VARIETIES = {
    "rice": ["Swarna", "Lalat", "Pooja"],
    "wheat": ["Sharbati", "HD-2967", "GW-496"],
    "tomato": ["Hybrid", "Deshi", "Cherry"],
    "onion": ["Red Medium", "White", "Nasik Red"],
    "potato": ["Jyoti", "Kufri Sindhuri", "Ladyfinger"],
    "maize": ["Yellow Hybrid", "White Local", "QPM"],
    "soybean": ["JS 335", "JS 9305", "NRC 37"],
    "mustard": ["Varuna", "Pusa Bold", "RH 30"],
}
_DEFAULT_VARIETY = ["Local", "Deshi", "Mixed"]


def _generate_mock_data(commodity: str, state: str | None, days_back: int) -> dict:
    """Generate realistic mock mandi price records."""
    random.seed(abs(hash(str(commodity) + str(state))) % 9999)
    crop_key = (commodity or "").lower()
    base = _CROP_BASE_PRICES.get(crop_key, 2000)
    varieties = _VARIETIES.get(crop_key, _DEFAULT_VARIETY)
    trend_factor = random.choice([-0.09, -0.04, 0.02, 0.06])

    records = []
    for day_offset in range(min(days_back, 7)):
        day_date = (date.today() - timedelta(days=day_offset)).strftime("%d/%m/%Y")
        day_adj = trend_factor * (days_back - day_offset - 1) / max(days_back - 1, 1)
        for i, (mandi_name, mandi_state, district) in enumerate(_MOCK_MANDIS[:4]):
            modal = round(base * (1 + random.uniform(-0.10, 0.10) + day_adj))
            records.append({
                "state": state or mandi_state,
                "district": district,
                "market": mandi_name,
                "commodity": commodity,
                "variety": varieties[i % len(varieties)],
                "arrival_date": day_date,
                "min_price": round(modal * random.uniform(0.88, 0.96)),
                "max_price": round(modal * random.uniform(1.04, 1.14)),
                "modal_price": modal,
            })

    modal_prices = [r["modal_price"] for r in records]
    summary = {
        "avg_modal_price": round(sum(modal_prices) / len(modal_prices), 2) if modal_prices else None,
        "min_modal_price": min(modal_prices) if modal_prices else None,
        "max_modal_price": max(modal_prices) if modal_prices else None,
        "num_markets": len(_MOCK_MANDIS[:4]),
        "currency": "INR / Quintal",
    }

    return {
        "commodity": commodity,
        "state_filter": state,
        "market_filter": None,
        "records": records,
        "summary": summary,
        "source": "Mock Data (Demo Mode — add DATAGOV_API_KEY for live AGMARKNET data)",
    }


def fetch_mandi_prices(
    commodity: str,
    state: str | None = None,
    market: str | None = None,
    days_back: int = 7,
) -> dict:
    """
    Fetch recent mandi (market) price data for a commodity from AGMARKNET.
    Falls back to mock data when DATAGOV_API_KEY is not set.

    Args:
        commodity: Crop/commodity name (e.g. "Rice", "Wheat", "Tomato").
        state: Optional state filter (e.g. "Odisha", "Maharashtra").
        market: Optional specific market/mandi name.
        days_back: Number of past days to include in results.

    Returns:
        dict with 'records' list (price entries) and 'summary' statistics.
    """
    if not DATAGOV_API_KEY:
        return _generate_mock_data(commodity, state, days_back)

    cutoff_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%d/%m/%Y")

    params = {
        "api-key": DATAGOV_API_KEY,
        "format": "json",
        "limit": DEFAULT_LIMIT,
        "filters[Commodity]": commodity,
    }

    if state:
        params["filters[State]"] = state
    if market:
        params["filters[Market]"] = market

    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.get(
                f"{DATAGOV_BASE_URL}/{AGMARKNET_RESOURCE_ID}",
                params=params,
            )
            response.raise_for_status()
    except Exception:
        # Fallback to mock on any error
        return _generate_mock_data(commodity, state, days_back)

    data = response.json()
    records_raw = data.get("records", [])

    records = [
        {
            "state": r.get("State"),
            "district": r.get("District"),
            "market": r.get("Market"),
            "commodity": r.get("Commodity"),
            "variety": r.get("Variety"),
            "arrival_date": r.get("Arrival_Date"),
            "min_price": _safe_float(r.get("Min_x0020_Price")),
            "max_price": _safe_float(r.get("Max_x0020_Price")),
            "modal_price": _safe_float(r.get("Modal_x0020_Price")),
        }
        for r in records_raw
    ]

    if not records:
        return _generate_mock_data(commodity, state, days_back)

    modal_prices = [r["modal_price"] for r in records if r["modal_price"] is not None]
    summary = {
        "avg_modal_price": round(sum(modal_prices) / len(modal_prices), 2) if modal_prices else None,
        "min_modal_price": min(modal_prices) if modal_prices else None,
        "max_modal_price": max(modal_prices) if modal_prices else None,
        "num_markets": len(records),
        "currency": "INR / Quintal",
    }

    return {
        "commodity": commodity,
        "state_filter": state,
        "market_filter": market,
        "records": records,
        "summary": summary,
        "source": "AGMARKNET via data.gov.in",
    }


def _safe_float(value) -> float | None:
    """Safely convert a value to float, returning None on failure."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

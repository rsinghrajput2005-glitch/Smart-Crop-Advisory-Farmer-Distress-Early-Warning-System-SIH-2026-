"""
services/mandi_service.py

Returns realistic MOCK mandi (agricultural market) price data with
summary statistics and price trend analysis.

TODO: Replace mock data with live AGMARKNET / data.gov.in API integration.
      Steps to swap in the real API:
        1. Register at https://data.gov.in and obtain a free API key.
        2. Add DATAGOV_API_KEY to your .env file.
        3. Replace the _mock_prices() call below with a real HTTP request to:
           https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070
           with params: api-key, format=json, filters[Commodity]=<crop>,
                        filters[State]=<state>, limit=50
        4. Map the response fields:
               State, District, Market, Commodity, Variety,
               Arrival_Date, Min_x0020_Price, Max_x0020_Price, Modal_x0020_Price
"""

from __future__ import annotations

import random
from datetime import date, timedelta


def get_mandi_prices(crop: str, location: str, days_back: int = 7) -> dict:
    """
    Return mandi price data for a crop and location, including summary
    statistics and price trend analysis.

    Currently returns MOCK data with realistic price ranges for common
    Indian crops. Structure matches the live AGMARKNET API response.

    Args:
        crop:      Crop/commodity name (e.g. "Rice", "Wheat", "Tomato").
        location:  State or district name (e.g. "Odisha", "Punjab").
        days_back: Number of days of historical records to generate.

    Returns:
        dict with:
            commodity    – Queried crop name
            state_filter – Queried location
            records      – list of mandi price dicts
            summary      – avg/min/max modal price, num_markets, currency
            price_trend  – trend direction, change_pct, distress_signal
            source       – data source label
    """
    records = _mock_prices(crop=crop, location=location, days_back=days_back)

    summary = _compute_summary(records)
    price_trend = _compute_price_trend(records)

    return {
        "commodity":    crop,
        "state_filter": location,
        "market_filter": None,
        "records":      records,
        "summary":      summary,
        "price_trend":  price_trend,
        "is_mock":      True,
        "source": (
            "Mock Data (Demo Mode) — See mandi_service.py TODO to integrate "
            "live AGMARKNET / data.gov.in API."
        ),
    }


# ── Computation helpers ───────────────────────────────────────────────────────

def _compute_summary(records: list[dict]) -> dict:
    """Compute summary statistics across all mandi records."""
    if not records:
        return {
            "avg_modal_price": None,
            "min_modal_price": None,
            "max_modal_price": None,
            "num_markets": 0,
            "currency": "INR / Quintal",
        }

    modal_prices = [r["modal_price"] for r in records if r.get("modal_price")]
    markets = set(r["mandi_name"] for r in records if r.get("mandi_name"))

    return {
        "avg_modal_price": round(sum(modal_prices) / len(modal_prices), 2) if modal_prices else None,
        "min_modal_price": min(modal_prices) if modal_prices else None,
        "max_modal_price": max(modal_prices) if modal_prices else None,
        "num_markets": len(markets),
        "currency": "INR / Quintal",
    }


def _compute_price_trend(records: list[dict]) -> dict:
    """
    Compute price trend by comparing the oldest vs newest modal prices
    across records sorted by arrival_date.
    """
    if not records or len(records) < 2:
        return {
            "trend": "Stable",
            "change_pct": 0.0,
            "oldest_modal_price": None,
            "newest_modal_price": None,
            "distress_signal": False,
            "note": "Insufficient data to compute trend.",
        }

    sorted_records = sorted(records, key=lambda r: r.get("arrival_date", ""))
    oldest_price = sorted_records[0].get("modal_price")
    newest_price = sorted_records[-1].get("modal_price")

    if not oldest_price or not newest_price or oldest_price == 0:
        return {
            "trend": "Stable",
            "change_pct": 0.0,
            "oldest_modal_price": oldest_price,
            "newest_modal_price": newest_price,
            "distress_signal": False,
            "note": "Could not compute trend — missing price data.",
        }

    change_pct = round(((newest_price - oldest_price) / oldest_price) * 100, 2)

    if change_pct <= -10:
        trend = "Sharply Falling"
    elif change_pct <= -5:
        trend = "Falling"
    elif change_pct >= 10:
        trend = "Sharply Rising"
    elif change_pct >= 5:
        trend = "Rising"
    else:
        trend = "Stable"

    distress_signal = change_pct <= -5

    note = (
        f"Price {'dropped' if change_pct < 0 else 'rose'} by "
        f"{abs(change_pct):.1f}% over the past week."
    )
    if distress_signal:
        note += " ⚠ Distress signal: price drop may indicate oversupply or demand shock."

    return {
        "trend":               trend,
        "change_pct":          change_pct,
        "oldest_modal_price":  oldest_price,
        "newest_modal_price":  newest_price,
        "distress_signal":     distress_signal,
        "note":                note,
    }


# ── Mock data generator ───────────────────────────────────────────────────────

# Realistic base modal prices in INR per Quintal (100 kg) for common crops
_CROP_BASE_PRICES: dict[str, int] = {
    "rice":      2000,
    "wheat":     2100,
    "maize":     1800,
    "tomato":     900,
    "onion":      800,
    "potato":     700,
    "soybean":   4200,
    "cotton":    6200,
    "sugarcane":  350,
    "mustard":   5200,
}

_DEFAULT_BASE_PRICE = 2000

_MOCK_MANDIS = [
    "Bhubaneswar Mandi",
    "Cuttack Agricultural Market",
    "Puri Mandi",
    "Sambalpur Market Yard",
    "Berhampur APMC",
    "Rourkela Mandi",
]

_VARIETIES = {
    "rice":    ["Swarna", "Lalat", "Pooja"],
    "wheat":   ["Sharbati", "HD-2967", "GW-496"],
    "tomato":  ["Hybrid", "Deshi", "Cherry"],
    "onion":   ["Red Medium", "White", "Nasik Red"],
    "potato":  ["Jyoti", "Kufri Sindhuri", "Ladyfinger"],
    "maize":   ["Yellow Hybrid", "White Local", "QPM"],
    "soybean": ["JS 335", "JS 9305", "NRC 37"],
    "mustard": ["Varuna", "Pusa Bold", "RH 30"],
}
_DEFAULT_VARIETY = ["Local", "Deshi", "Mixed"]


def _mock_prices(crop: str, location: str, days_back: int = 7) -> list[dict]:
    """Generate a list of realistic mock mandi price records over multiple days."""
    random.seed(abs(hash(crop + location)) % 9999)

    crop_key = crop.lower()
    base = _CROP_BASE_PRICES.get(crop_key, _DEFAULT_BASE_PRICE)
    varieties = _VARIETIES.get(crop_key, _DEFAULT_VARIETY)

    records = []
    # Simulate a slight downward trend to sometimes trigger distress signal
    trend_factor = random.choice([-0.08, -0.03, 0.02, 0.05])

    for day_offset in range(min(days_back, 7)):
        day_date = (date.today() - timedelta(days=day_offset)).isoformat()
        # Apply trend: older entries have prices before the trend
        day_adjustment = trend_factor * (days_back - day_offset - 1) / max(days_back - 1, 1)

        for i, mandi in enumerate(_MOCK_MANDIS[:4]):
            variation = random.uniform(-0.10, 0.10)
            modal = round(base * (1 + variation + day_adjustment))
            min_p = round(modal * random.uniform(0.88, 0.96))
            max_p = round(modal * random.uniform(1.04, 1.14))

            records.append({
                "mandi_name":   mandi,
                "state":        location,
                "district":     location,
                "market":       mandi,
                "location":     location,
                "crop":         crop,
                "commodity":    crop,
                "variety":      varieties[i % len(varieties)],
                "min_price":    min_p,
                "max_price":    max_p,
                "modal_price":  modal,
                "currency":     "INR / Quintal",
                "arrival_date": day_date,
            })

    return records

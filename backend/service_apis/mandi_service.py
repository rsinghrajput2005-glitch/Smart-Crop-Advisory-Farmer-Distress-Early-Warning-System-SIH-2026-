"""
Mandi service — orchestrates AGMARKNET price fetching and price-trend analysis.
Sits between the API router and the external_apis.mandi client.
"""

from backend.external_apis.mandi import fetch_mandi_prices


def get_mandi_prices(
    commodity: str,
    state: str | None = None,
    market: str | None = None,
    days_back: int = 7,
) -> dict:
    """
    Retrieve recent mandi prices for a commodity and compute price trend.

    Args:
        commodity: Crop/commodity name (e.g. "Rice", "Wheat", "Tomato").
        state: Optional state to filter results.
        market: Optional specific market/mandi name.
        days_back: Number of past days to include.

    Returns:
        dict with records, summary statistics, and price trend assessment.

    Raises:
        ValueError: if commodity name is empty.
        RuntimeError: if AGMARKNET API is unreachable.
    """
    commodity = commodity.strip()
    if not commodity:
        raise ValueError("Commodity name must not be empty.")

    try:
        mandi_data = fetch_mandi_prices(
            commodity=commodity,
            state=state,
            market=market,
            days_back=days_back,
        )
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch mandi data: {exc}") from exc

    mandi_data["price_trend"] = _assess_price_trend(mandi_data)
    return mandi_data


def _assess_price_trend(mandi_data: dict) -> dict:
    """
    Assess the price trend from mandi records.
    Sorts records by date and computes percentage change from oldest to newest.

    Returns:
        dict with trend direction, change_pct, and distress_signal.
    """
    records = mandi_data.get("records", [])

    dated_records = [
        r for r in records
        if r.get("arrival_date") and r.get("modal_price") is not None
    ]

    if len(dated_records) < 2:
        return {
            "trend": "Insufficient data",
            "change_pct": None,
            "distress_signal": False,
            "note": "Need at least 2 records with dates for trend analysis.",
        }

    dated_records.sort(key=lambda r: r["arrival_date"])
    oldest_price = dated_records[0]["modal_price"]
    newest_price = dated_records[-1]["modal_price"]

    if oldest_price and oldest_price != 0:
        change_pct = round(((newest_price - oldest_price) / oldest_price) * 100, 2)
    else:
        change_pct = 0.0

    if change_pct <= -15:
        trend = "Sharply Falling"
        distress_signal = True
    elif change_pct <= -5:
        trend = "Falling"
        distress_signal = True
    elif change_pct < 5:
        trend = "Stable"
        distress_signal = False
    elif change_pct < 15:
        trend = "Rising"
        distress_signal = False
    else:
        trend = "Sharply Rising"
        distress_signal = False

    return {
        "trend": trend,
        "change_pct": change_pct,
        "oldest_modal_price": oldest_price,
        "newest_modal_price": newest_price,
        "distress_signal": distress_signal,
        "note": (
            "Price distress signal triggered — farmers may be selling below cost."
            if distress_signal
            else "Price trend is stable or rising — no price distress detected."
        ),
    }

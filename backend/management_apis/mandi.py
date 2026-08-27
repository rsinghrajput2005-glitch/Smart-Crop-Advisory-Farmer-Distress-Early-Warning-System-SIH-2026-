"""
Mandi API router — exposes endpoints to retrieve AGMARKNET commodity prices
and price-trend analysis for farmer distress risk detection.
"""

from fastapi import APIRouter, HTTPException, Query

from backend.service_apis.mandi_service import get_mandi_prices

router = APIRouter(
    prefix="/mandi",
    tags=["Mandi / Market Prices"],
)


@router.get("/prices")
def get_prices(
    commodity: str = Query(..., description="Crop/commodity name (e.g. Rice, Wheat, Tomato)"),
    state: str | None = Query(None, description="State to filter markets (e.g. Odisha)"),
    market: str | None = Query(None, description="Specific market/mandi name (optional)"),
    days_back: int = Query(7, description="Number of past days to fetch prices for", ge=1, le=30),
):
    """
    Retrieve recent mandi prices for a commodity from AGMARKNET (data.gov.in).

    Returns:
    - Price records: state, district, market, variety, min/max/modal price, date
    - Summary: average, min, max modal price across all matching markets
    - Price trend: Falling / Stable / Rising with percentage change
    - Distress signal: True if prices have dropped ≥ 5% (used in distress model)

    Requires `DATAGOV_API_KEY` in your `.env` file.
    Get a free key at: https://data.gov.in
    """
    try:
        return get_mandi_prices(
            commodity=commodity,
            state=state,
            market=market,
            days_back=days_back,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")

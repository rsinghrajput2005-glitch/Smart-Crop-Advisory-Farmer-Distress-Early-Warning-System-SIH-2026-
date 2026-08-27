"""
schemas.py — Pydantic request and response models.

All FastAPI endpoints use these schemas for input validation
and structured JSON output. Organised by service domain.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ══════════════════════════════════════════════════════════════
# Shared / Common
# ══════════════════════════════════════════════════════════════

class LocationQuery(BaseModel):
    """Latitude/longitude coordinates for a farm location."""
    lat: float = Field(..., ge=-90, le=90, description="Latitude of the farm")
    lon: float = Field(..., ge=-180, le=180, description="Longitude of the farm")


class APIResponse(BaseModel):
    """Generic success/error wrapper."""
    success: bool
    message: str
    data: Optional[dict] = None


# ══════════════════════════════════════════════════════════════
# Soil
# ══════════════════════════════════════════════════════════════

class SoilInterpretation(BaseModel):
    ph: Optional[str] = None
    organic_carbon: Optional[str] = None
    texture: Optional[str] = None


class SoilResponse(BaseModel):
    ph: Optional[float] = Field(None, description="Soil pH (0–14)")
    organic_carbon: Optional[float] = Field(None, description="Organic carbon density (g/kg)")
    clay: Optional[float] = Field(None, description="Clay content (%)")
    sand: Optional[float] = Field(None, description="Sand content (%)")
    nitrogen: Optional[float] = Field(None, description="Nitrogen content (g/kg)")
    source: str
    depth: str
    interpretation: Optional[SoilInterpretation] = None


# ══════════════════════════════════════════════════════════════
# Weather
# ══════════════════════════════════════════════════════════════

class CurrentWeather(BaseModel):
    temperature_c: Optional[float]
    feels_like_c: Optional[float]
    humidity_pct: Optional[float]
    precipitation_mm: Optional[float]
    wind_speed_kmh: Optional[float]
    wind_direction_deg: Optional[float]
    pressure_hpa: Optional[float]
    weather_code: Optional[int]
    condition: Optional[str]
    time: Optional[str]


class ForecastDay(BaseModel):
    date: str
    temp_max: Optional[float]
    temp_min: Optional[float]
    precipitation_sum_mm: Optional[float]
    rain_sum_mm: Optional[float]
    weather_code: Optional[int]
    condition: Optional[str]
    wind_speed_max_kmh: Optional[float]
    sunrise: Optional[str]
    sunset: Optional[str]


class WeatherRisk(BaseModel):
    risk_level: str = Field(..., description="Low / Medium / High")
    risk_score: int
    risk_factors: list[str]


class WeatherResponse(BaseModel):
    current: CurrentWeather
    forecast: list[ForecastDay]
    weather_risk: WeatherRisk
    source: str
    units: dict


# ══════════════════════════════════════════════════════════════
# NDVI / Satellite
# ══════════════════════════════════════════════════════════════

class NDVIAssets(BaseModel):
    B04_red_href: Optional[str]
    B08_nir_href: Optional[str]
    visual_href: Optional[str]
    thumbnail_href: Optional[str]


class NDVIAdvisory(BaseModel):
    condition: Optional[str] = None
    ndvi_value: Optional[float] = None
    urgency: Optional[str] = None
    action: Optional[str] = None
    notes: Optional[list[str]] = None
    recommendation: Optional[str] = None


class NDVIResponse(BaseModel):
    scene_id: Optional[str]
    date: Optional[str]
    cloud_cover_pct: Optional[float]
    platform: Optional[str]
    assets: NDVIAssets
    bbox: list[float]
    ndvi_formula: str
    source: str
    interpretation: dict
    advisory: NDVIAdvisory
    ndvi_value: Optional[float] = None
    crop_condition: Optional[str] = None


# ══════════════════════════════════════════════════════════════
# Mandi / Market Prices
# ══════════════════════════════════════════════════════════════

class MandiRecord(BaseModel):
    state: Optional[str]
    district: Optional[str]
    market: Optional[str]
    commodity: Optional[str]
    variety: Optional[str]
    arrival_date: Optional[str]
    min_price: Optional[float] = Field(None, description="Min price (INR/Quintal)")
    max_price: Optional[float] = Field(None, description="Max price (INR/Quintal)")
    modal_price: Optional[float] = Field(None, description="Modal price (INR/Quintal)")


class MandiSummary(BaseModel):
    avg_modal_price: Optional[float]
    min_modal_price: Optional[float]
    max_modal_price: Optional[float]
    num_markets: int
    currency: str


class PriceTrend(BaseModel):
    trend: str = Field(..., description="Sharply Falling / Falling / Stable / Rising / Sharply Rising")
    change_pct: Optional[float]
    oldest_modal_price: Optional[float]
    newest_modal_price: Optional[float]
    distress_signal: bool = Field(..., description="True if price drop ≥ 5%")
    note: str


class MandiResponse(BaseModel):
    commodity: str
    state_filter: Optional[str]
    market_filter: Optional[str]
    records: list[MandiRecord]
    summary: Optional[MandiSummary]
    price_trend: Optional[PriceTrend]
    source: str


# ══════════════════════════════════════════════════════════════
# Crop Advisory (ML output)
# ══════════════════════════════════════════════════════════════

class CropAdvisoryRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    crop: str = Field(..., description="Crop name, e.g. Rice, Wheat")
    growth_stage: str = Field(
        ...,
        description="Growth stage, e.g. Germination, Tillering, Flowering, Harvesting",
    )


class CropAdvisoryResponse(BaseModel):
    crop: str
    growth_stage: str
    advisory: str
    soil_summary: Optional[dict] = None
    weather_summary: Optional[dict] = None
    ndvi_condition: Optional[str] = None


# ══════════════════════════════════════════════════════════════
# Distress Risk (ML output)
# ══════════════════════════════════════════════════════════════

class DistressRiskRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    crop: str
    growth_stage: str
    ndvi_value: Optional[float] = Field(None, ge=-1.0, le=1.0)
    mandi_commodity: Optional[str] = None


class DistressRiskResponse(BaseModel):
    risk_level: str = Field(..., description="Low / Medium / High")
    risk_score: float
    risk_factors: list[str]
    crop: str
    growth_stage: str
    officer_alert: bool = Field(
        ..., description="True if risk is High — triggers officer dashboard alert"
    )

# ══════════════════════════════════════════════════════════════
# Chatbot
# ══════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    message: str = Field(..., description="The farmer's voice/text query")

class ChatResponse(BaseModel):
    response: str = Field(..., description="The LLM-generated reply")

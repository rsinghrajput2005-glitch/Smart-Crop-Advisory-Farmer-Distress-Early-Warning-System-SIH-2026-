from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import traceback

from backend.schemas import (
    CropAdvisoryRequest, CropAdvisoryResponse,
    DistressRiskRequest, DistressRiskResponse,
    ChatRequest, ChatResponse
)
from backend.services.soil_service import get_soil_data
from backend.services.weather_service import get_weather_data
from backend.services.ndvi_service import get_ndvi
from backend.services.mandi_service import get_mandi_prices
from backend.inference import get_crop_advisory, get_distress_risk
from backend.services.advisory_ai import generate_farmer_advisory
from backend.services.advisory_data import prepare_advisory_data

from backend.management_apis.auth import router as auth_router
from backend.management_apis.farms import router as farm_router
from backend.management_apis.soil import router as soil_router
from backend.management_apis.weather import router as weather_router
from backend.management_apis.ndvi import router as ndvi_router
from backend.management_apis.mandi import router as mandi_router
from backend.management_apis.chat import router as chat_router
from backend.management_apis.tts import router as tts_router

app = FastAPI(
    title="Smart Crop Advisory & Farmer Distress Early-Warning System",
    description=(
        "A multilingual, low-bandwidth AI platform combining soil, weather, "
        "Sentinel-2 NDVI, and mandi-price data to provide crop-stage-specific "
        "advisory and early farmer-distress risk detection."
    ),
    version="1.0.0",
    contact={
        "name": "SIH 2026 Team",
    },
)

# CORS — update origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth & farm management
app.include_router(auth_router)
app.include_router(farm_router)

# Data services
app.include_router(soil_router)
app.include_router(weather_router)
app.include_router(ndvi_router)
app.include_router(mandi_router)
app.include_router(chat_router)
app.include_router(tts_router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

# ── ML Inference Endpoints ────────────────────────────────────────────────────
@app.post("/advisory", response_model=CropAdvisoryResponse, tags=["ML Inference"])
def advisory_endpoint(req: CropAdvisoryRequest):
    try:
        soil = get_soil_data(req.lat, req.lon)
        weather = get_weather_data(req.lat, req.lon)
        ndvi_data = get_ndvi(req.lat, req.lon)

        soil_ph = soil.get("ph", 7.0)
        organic_carbon = soil.get("organic_carbon", 10.0)
        clay = soil.get("clay", 20.0)
        sand = soil.get("sand", 40.0)

        forecast = weather.get("forecast", [])
        rainfall_mm = sum([d.get("rainfall_mm", 0.0) for d in forecast])
        temperature_c = weather.get("current", {}).get("temperature_c", 25.0)
        humidity_pct = weather.get("current", {}).get("humidity_pct", 60.0)

        ndvi_val = ndvi_data.get("ndvi_value", 0.5)
        crop_condition = ndvi_data.get("condition", "Unknown")
        weather_risk_level = weather.get("weather_risk", {}).get("risk_level", "Medium")

        # Mandi / market data, reused for both distress scoring and advisory context
        mandi = get_mandi_prices(req.crop, location="Unknown")
        mandi_modal_price = 2000.0
        if mandi.get("summary") and mandi["summary"].get("avg_modal_price"):
            mandi_modal_price = mandi["summary"]["avg_modal_price"]
        price_trend_pct = mandi.get("price_trend", {}).get("change_pct", 0.0)
        price_distress_flag = 1 if mandi.get("price_trend", {}).get("distress_signal") else 0

        # Run the same distress-risk logic used by /risk, so /advisory has real risk context
        risk_level, risk_score, risk_reasons = get_distress_risk(
            req.crop, "Unknown Location", ndvi_val, crop_condition,
            weather_risk_level, rainfall_mm, temperature_c, mandi_modal_price,
            price_trend_pct, price_distress_flag
        )

        farmer = {"crop": req.crop, "crop_stage": req.growth_stage}
        features = {
            "temperature": temperature_c,
            "humidity": humidity_pct,
            "precipitation": weather.get("current", {}).get("precipitation_mm"),
            "soil_moisture": None,
            "rainfall_deviation": None,
            "heavy_rain": rainfall_mm > 200,
            "current_market_price": mandi_modal_price,
            "previous_price": None,
            "market_price_change": price_trend_pct,
        }
        distress = {
            "score": risk_score,
            "risk_level": risk_level,
            "reasons": risk_reasons,
        }
        soil_payload = {
            "available": True,
            "ph": soil_ph,
            "nitrogen": soil.get("nitrogen"),
            "clay_percent": clay,
            "sand_percent": sand,
            "silt_percent": soil.get("silt"),
            "organic_carbon": organic_carbon,
        }

        advisory_data = prepare_advisory_data(
            farmer=farmer,
            features=features,
            distress=distress,
            soil=soil_payload,
        )

        advisory_text = generate_farmer_advisory(advisory_data, language=req.language)

        return CropAdvisoryResponse(
            crop=req.crop,
            growth_stage=req.growth_stage,
            advisory=advisory_text,
            soil_summary={"ph": soil_ph, "organic_carbon": organic_carbon},
            weather_summary={"temperature_c": temperature_c, "rainfall_mm": rainfall_mm},
            ndvi_condition=crop_condition,
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/risk", response_model=DistressRiskResponse, tags=["ML Inference"])
def risk_endpoint(req: DistressRiskRequest):
    try:
        weather = get_weather_data(req.lat, req.lon)
        ndvi_data = get_ndvi(req.lat, req.lon)
        
        commodity = req.mandi_commodity or req.crop
        mandi = get_mandi_prices(commodity, location="Unknown")
        
        ndvi_val = req.ndvi_value if req.ndvi_value is not None else ndvi_data.get("ndvi_value", 0.5)
        crop_condition = ndvi_data.get("condition", "Unknown")
        weather_risk = weather.get("weather_risk", {}).get("risk_level", "Medium")
        rainfall_mm = sum([d.get("rainfall_mm", 0.0) for d in weather.get("forecast", [])])
        temperature_c = weather.get("current", {}).get("temperature_c", 25.0)
        
        mandi_modal_price = 2000.0
        if mandi.get("summary") and mandi["summary"].get("avg_modal_price"):
            mandi_modal_price = mandi["summary"]["avg_modal_price"]
            
        price_trend_pct = mandi.get("price_trend", {}).get("change_pct", 0.0)
        price_distress_flag = 1 if mandi.get("price_trend", {}).get("distress_signal") else 0
        
        risk_level, risk_score, factors = get_distress_risk(
            req.crop, "Unknown Location", ndvi_val, crop_condition,
            weather_risk, rainfall_mm, temperature_c, mandi_modal_price,
            price_trend_pct, price_distress_flag
        )
        
        return DistressRiskResponse(
            risk_level=risk_level,
            risk_score=risk_score,
            risk_factors=factors,
            crop=req.crop,
            growth_stage=req.growth_stage,
            officer_alert=(risk_level == "High")
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
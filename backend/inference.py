"""
backend/inference.py
Logic for loading trained ML models and running inference.
Falls back to rule-based advisory when models are not yet trained.
"""

import os
import pickle
import numpy as np

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

# ── Load Crop Advisory Model ──────────────────────────────────────────
CROP_ADVISORY_PATH = os.path.join(MODELS_DIR, "crop_advisory_model.pkl")
try:
    with open(CROP_ADVISORY_PATH, "rb") as f:
        crop_data = pickle.load(f)
        
    crop_advisory_model = crop_data["model"]
    crop_advisory_le_label = crop_data["label_encoder"]
    crop_advisory_encoders = crop_data.get("encoders", {})
    print("Crop Advisory model loaded.")
except Exception as e:
    print(f"Crop Advisory model not loaded ({e}) - using rule-based fallback.")
    crop_advisory_model = None

# ── Load Distress Risk Model ──────────────────────────────────────────
DISTRESS_RISK_PATH = os.path.join(MODELS_DIR, "distress_risk_model.pkl")
try:
    with open(DISTRESS_RISK_PATH, "rb") as f:
        risk_data = pickle.load(f)
        
    distress_risk_model = risk_data["model"]
    distress_risk_le_label = risk_data["label_encoder"]
    distress_risk_encoders = risk_data.get("encoders", {})
    print("Distress Risk model loaded.")
except Exception as e:
    print(f"Distress Risk model not loaded ({e}) - using rule-based fallback.")
    distress_risk_model = None

# ── Rule-based advisory lookup ────────────────────────────────────────

_ADVISORY_RULES = {
    ("rice",    "germination"):  "Maintain 2-3 cm standing water. Ensure uniform seed distribution. Apply DAP @ 50 kg/ha as basal dose.",
    ("rice",    "tillering"):    "Apply N fertilizer (urea) as split dose. Control early shoot borer with recommended insecticide if infestation >5%.",
    ("rice",    "vegetative"):   "Monitor for leaf folder and blast disease. Maintain proper water level. Apply micronutrients if deficiency observed.",
    ("rice",    "flowering"):    "Avoid water stress — keep 3-5 cm water level. Avoid pesticide sprays during flowering to protect pollinators.",
    ("rice",    "grain_filling"):"Ensure adequate irrigation. Apply potash if not done earlier. Monitor for BPH and neck blast disease.",
    ("rice",    "harvesting"):   "Drain field 10-15 days before harvest. Harvest at 80-85% grain maturity. Sun-dry to 14% moisture before storage.",
    ("wheat",   "germination"):  "Ensure proper seedbed preparation. Sow at 100-125 kg/ha seed rate. Apply basal fertilizer (N:P:K = 120:60:40 kg/ha).",
    ("wheat",   "tillering"):    "Apply first irrigation at CRI stage (21 days). Top-dress 50% of nitrogen. Control Phalaris minor weed if present.",
    ("wheat",   "vegetative"):   "Apply second irrigation at tillering. Monitor for yellow rust — spray Propiconazole if observed.",
    ("wheat",   "flowering"):    "Apply third irrigation at flowering. Avoid water stress. Monitor for aphids and treat if threshold crossed.",
    ("wheat",   "grain_filling"):"Apply fourth irrigation at grain filling stage. Monitor for Karnal bunt in humid conditions.",
    ("wheat",   "harvesting"):   "Harvest at golden-yellow color of grains. Avoid delayed harvest to prevent shattering losses.",
    ("maize",   "germination"):  "Apply basal fertilizer (N:P:K). Ensure soil moisture for uniform germination. Target plant population 65,000/ha.",
    ("maize",   "vegetative"):   "Apply top-dress N at knee-high stage. Control fall armyworm if observed — use recommended pesticide in whorl.",
    ("maize",   "flowering"):    "Apply potash and micronutrients. Ensure irrigation during silk emergence for better pollination.",
    ("maize",   "grain_filling"):"Maintain soil moisture. Monitor for ear rot diseases. Reduce irrigation 2-3 weeks before harvest.",
    ("maize",   "harvesting"):   "Harvest when husks turn brown and grains are hard. Dry to <13% moisture before storage.",
    ("tomato",  "germination"):  "Transplant 25-30 day old seedlings. Apply starter fertilizer. Maintain 60-70% soil moisture.",
    ("tomato",  "vegetative"):   "Apply N-P-K @ 200:200:200 kg/ha split doses. Train plants and remove suckers weekly.",
    ("tomato",  "flowering"):    "Apply micronutrients (boron). Monitor for fruit borer — use pheromone traps. Avoid excess N.",
    ("tomato",  "grain_filling"):"Maintain consistent irrigation to prevent blossom end rot. Spray calcium if deficiency seen.",
    ("tomato",  "harvesting"):   "Harvest at breaker stage for distant markets, at red-ripe for local sale.",
    ("soybean", "germination"):  "Treat seed with Rhizobium culture. Ensure good seedbed moisture. Avoid waterlogging.",
    ("soybean", "vegetative"):   "Apply N:P:K @ 20:80:40 kg/ha. Weed control at 30-35 DAS with recommended herbicide.",
    ("soybean", "flowering"):    "Spray micronutrients at flowering. Avoid waterlogging. Monitor for semilooper and girdle beetle.",
    ("soybean", "grain_filling"):"Ensure adequate moisture at pod fill. Monitor for pod borer with pheromone traps.",
    ("soybean", "harvesting"):   "Harvest at 90% pod maturity (yellowing). Dry to <12% moisture. Avoid field losses.",
    ("mustard", "germination"):  "Sow at 5 kg/ha seed rate. Apply basal dose of P & K. Ensure field drainage.",
    ("mustard", "vegetative"):   "Apply N fertilizer. Thin seedlings to proper spacing. Control Lipaphis erysimi aphid.",
    ("mustard", "flowering"):    "Spray Boron @ 0.2% at flowering. Avoid irrigation at flowering time. Protect pollinators.",
    ("mustard", "grain_filling"):"Monitor for Sclerotinia rot in humid conditions. Reduce irrigation. Apply potash if needed.",
    ("mustard", "harvesting"):   "Harvest when 75% pods turn yellow. Avoid over-ripening to prevent shattering losses.",
    ("onion",   "germination"):  "Transplant 6-8 week old seedlings. Apply basal NPK. Ensure good drainage to prevent damping-off.",
    ("onion",   "vegetative"):   "Irrigate every 8-10 days. Apply N top-dress. Control thrips with recommended insecticide.",
    ("onion",   "harvesting"):   "Stop irrigation 10 days before harvest when tops fall. Cure bulbs in field for 3-5 days before storage.",
}

_DEFAULT_ADVISORY = (
    "Monitor your crop regularly for pests and diseases. "
    "Maintain adequate soil moisture and apply fertilizers as per soil test recommendations. "
    "Contact your local agricultural extension officer for site-specific advice."
)


def _rule_based_advisory(crop: str, growth_stage: str,
                          soil_ph: float = 7.0, ndvi: float = 0.5,
                          rainfall_mm: float = 50.0, temperature_c: float = 28.0) -> str:
    """Generate rule-based crop advisory with environmental context."""
    key = (crop.lower(), growth_stage.lower())
    base_advisory = _ADVISORY_RULES.get(key, _DEFAULT_ADVISORY)

    # Append context-specific tips
    addons = []
    if soil_ph < 5.5:
        addons.append("Soil pH is low — apply lime to correct acidity before next sowing.")
    elif soil_ph > 8.0:
        addons.append("Soil pH is alkaline — apply gypsum and organic matter to reduce pH.")

    if ndvi < 0.25:
        addons.append("Low NDVI detected — possible poor crop stand or nutrient deficiency. Field inspection recommended.")
    elif ndvi > 0.75:
        addons.append("Excellent crop canopy detected — maintain current management practices.")

    if rainfall_mm > 200:
        addons.append("Heavy recent rainfall — check for waterlogging and drainage issues.")
    elif rainfall_mm < 10:
        addons.append("Low rainfall — ensure irrigation schedule is maintained.")

    if temperature_c > 38:
        addons.append("High heat stress — increase irrigation frequency and consider mulching.")
    elif temperature_c < 10:
        addons.append("Low temperature — protect crop from cold with light irrigation if frost risk is present.")

    if addons:
        return base_advisory + " | " + " ".join(addons)
    return base_advisory


def get_crop_advisory(
    crop: str, growth_stage: str, soil_ph: float, organic_carbon: float, 
    clay: float, sand: float, rainfall_mm: float, temperature_c: float, 
    humidity_pct: float, ndvi: float
) -> str:
    """Run inference for Crop Advisory. Falls back to rule-based if model not loaded."""
    if not crop_advisory_model:
        return _rule_based_advisory(crop, growth_stage, soil_ph, ndvi, rainfall_mm, temperature_c)

    # Encode categorical inputs
    le_crop = crop_advisory_encoders.get("crop")
    try:
        crop_enc = le_crop.transform([crop])[0] if le_crop else 0
    except ValueError:
        crop_enc = 0

    le_stage = crop_advisory_encoders.get("growth_stage")
    try:
        stage_enc = le_stage.transform([growth_stage])[0] if le_stage else 0
    except ValueError:
        stage_enc = 0

    X = np.array([[
        crop_enc, stage_enc, soil_ph, organic_carbon, clay, sand, 
        rainfall_mm, temperature_c, humidity_pct, ndvi
    ]])
    
    try:
        pred_idx = crop_advisory_model.predict(X)[0]
        result = crop_advisory_le_label.inverse_transform([pred_idx])[0]
        # Append rule-based addons for context
        key = (crop.lower(), growth_stage.lower())
        addons = _rule_based_advisory(crop, growth_stage, soil_ph, ndvi, rainfall_mm, temperature_c)
        return f"{result} | {addons}"
    except Exception:
        return _rule_based_advisory(crop, growth_stage, soil_ph, ndvi, rainfall_mm, temperature_c)


def get_distress_risk(
    crop: str, location: str, ndvi_value: float, crop_condition: str,
    weather_risk: str, rainfall_mm: float, temperature_c: float,
    mandi_modal_price: float, price_trend_pct: float, price_distress_flag: int
) -> tuple[str, float, list[str]]:
    """Run inference for Distress Risk. Returns (risk_level, risk_score, major_factors).
    Falls back to rule-based scoring if model not loaded."""
    
    if not distress_risk_model:
        return _rule_based_distress_risk(
            crop, ndvi_value, crop_condition, weather_risk,
            rainfall_mm, temperature_c, mandi_modal_price,
            price_trend_pct, price_distress_flag
        )

    # Encode categorical inputs
    def safe_encode(encoder_name, val):
        le = distress_risk_encoders.get(encoder_name)
        if not le: return 0
        try:
            return le.transform([val])[0]
        except ValueError:
            return 0

    crop_enc = safe_encode("crop", crop)
    loc_enc = safe_encode("location", location)
    cond_enc = safe_encode("crop_condition", crop_condition)
    weather_enc = safe_encode("weather_risk", weather_risk)

    X = np.array([[
        crop_enc, loc_enc, ndvi_value, cond_enc, weather_enc, 
        rainfall_mm, temperature_c, mandi_modal_price, price_trend_pct, price_distress_flag
    ]])
    
    try:
        pred_idx = distress_risk_model.predict(X)[0]
        risk_level = distress_risk_le_label.inverse_transform([pred_idx])[0]
        probs = distress_risk_model.predict_proba(X)[0]
        risk_score = float(max(probs) * 10)
        factors = _get_risk_factors(price_distress_flag, weather_risk, ndvi_value,
                                    rainfall_mm, price_trend_pct, temperature_c)
        return risk_level, round(risk_score, 1), factors
    except Exception:
        return _rule_based_distress_risk(
            crop, ndvi_value, crop_condition, weather_risk,
            rainfall_mm, temperature_c, mandi_modal_price,
            price_trend_pct, price_distress_flag
        )


def _get_risk_factors(price_distress_flag, weather_risk, ndvi_value,
                      rainfall_mm, price_trend_pct, temperature_c) -> list[str]:
    """Build list of human-readable risk factors."""
    factors = []
    if price_distress_flag == 1 or price_trend_pct <= -5:
        factors.append(f"Price distress: {abs(price_trend_pct):.1f}% price drop in market")
    if weather_risk == "High":
        factors.append("High weather risk — adverse conditions for crop")
    if ndvi_value < 0.25:
        factors.append("Low NDVI — poor crop health detected by satellite")
    if rainfall_mm > 200:
        factors.append("Excess rainfall — waterlogging risk")
    elif rainfall_mm < 5:
        factors.append("Drought risk — insufficient rainfall")
    if temperature_c > 38:
        factors.append("Heat stress — high temperature impacting crop yield")
    if not factors:
        factors.append("Multiple moderate risk indicators detected")
    return factors


def _rule_based_distress_risk(
    crop: str, ndvi_value: float, crop_condition: str, weather_risk: str,
    rainfall_mm: float, temperature_c: float, mandi_modal_price: float,
    price_trend_pct: float, price_distress_flag: int
) -> tuple[str, float, list[str]]:
    """Rule-based distress risk scoring when ML model is not available."""
    score = 0.0
    factors = []

    # NDVI component (max 25 pts)
    if ndvi_value < 0.2:
        score += 25
        factors.append("Critical crop health — very low NDVI detected")
    elif ndvi_value < 0.4:
        score += 15
        factors.append("Below-average crop health — monitor closely")
    elif ndvi_value < 0.5:
        score += 5

    # Weather risk component (max 25 pts)
    if weather_risk == "High":
        score += 25
        factors.append("High weather risk — adverse conditions for crop")
    elif weather_risk == "Medium":
        score += 12

    # Price distress component (max 25 pts)
    if price_distress_flag == 1 or price_trend_pct <= -10:
        score += 25
        factors.append(f"Severe price distress: {abs(price_trend_pct):.1f}% drop in mandi prices")
    elif price_trend_pct <= -5:
        score += 15
        factors.append(f"Price falling: {abs(price_trend_pct):.1f}% drop in mandi prices")

    # Rainfall extremes (max 15 pts)
    if rainfall_mm > 250:
        score += 15
        factors.append("Extreme rainfall — flood/waterlogging distress risk")
    elif rainfall_mm < 5:
        score += 15
        factors.append("Drought risk — critically low rainfall")
    elif rainfall_mm > 150:
        score += 7

    # Temperature extremes (max 10 pts)
    if temperature_c > 40 or temperature_c < 5:
        score += 10
        factors.append(f"Temperature extreme: {temperature_c}°C — crop stress likely")
    elif temperature_c > 37:
        score += 5

    score = min(score, 100.0)

    if score >= 55:
        risk_level = "High"
    elif score >= 30:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    if not factors:
        factors.append("No major individual risk factors — low baseline risk")

    return risk_level, round(score / 10, 1), factors

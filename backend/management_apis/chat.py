"""
management_apis/chat.py

Farmer advisory chatbot endpoint.
Uses Groq (llama-3.1-8b-instant) for richer, context-aware responses when
GROQ_API_KEY is set in .env. Falls back to the rule-based knowledge base below
if the key is missing or the LLM call fails for any reason.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel, Field

import logging

try:
    from groq import Groq
except ImportError:  # pragma: no cover
    Groq = None

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

_api_key = os.getenv("GROQ_API_KEY")
_client = Groq(api_key=_api_key) if Groq and _api_key else None
_MODEL_NAME = "openai/gpt-oss-120b"

router = APIRouter(
    prefix="/chat",
    tags=["Advisory Chatbot"],
)


class ChatRequest(BaseModel):
    message: str = Field(..., description="The farmer's query (text or voice-transcribed)")
    language: str = Field("en", description="Language code: en, hi, te, ta, bn, mr, or")
    crop: str | None = Field(None, description="Farmer's current crop (optional context)")
    growth_stage: str | None = Field(None, description="Current growth stage (optional context)")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Advisory reply")
    category: str = Field(..., description="Query category detected")
    source: str = Field(..., description="Response source: rule-based or llm")


# ── Knowledge base ─────────────────────────────────────────────────────────────

_PEST_RESPONSES = {
    "armyworm":    "Fall Armyworm: Apply Emamectin benzoate 5% SG @ 0.4 g/litre or Chlorantraniliprole in the whorl at first sign of infestation. Pheromone traps help in early detection.",
    "borer":       "Stem/Shoot Borer: Remove and destroy dead hearts early. Apply Cartap Hydrochloride or Chlorpyrifos @ 2 ml/litre. Use pheromone traps for monitoring.",
    "aphid":       "Aphids: Spray Imidacloprid 17.8 SL @ 0.5 ml/litre or Dimethoate 30 EC @ 2 ml/litre. Encourage natural predators like ladybird beetles.",
    "blast":       "Rice Blast: Spray Tricyclazole 75 WP @ 0.6 g/litre or Propiconazole 25 EC @ 1 ml/litre at first sign of infection. Remove infected debris.",
    "blight":      "Blight: Apply Copper Oxychloride 50 WP @ 3 g/litre or Mancozeb 75 WP @ 2.5 g/litre. Improve drainage. Avoid overhead irrigation.",
    "rust":        "Rust disease: Apply Propiconazole 25 EC @ 1 ml/litre or Tebuconazole @ 1 ml/litre. Remove infected leaves and avoid overhead irrigation.",
    "thrips":      "Thrips: Spray Spinosad 45 SC @ 0.3 ml/litre or Fipronil 5 SC @ 1.5 ml/litre. Avoid over-irrigation and dense planting.",
    "weevil":      "Weevil infestation: Clean storage thoroughly. Use Aluminium Phosphide for fumigation. Sun-dry grain to <12% moisture before storage.",
    "locust":      "Locust: Contact your District Agriculture Officer immediately. Use Malathion 50 EC aerial spray at recommended dosage. Monitor DSS alerts.",
    "mite":        "Spider Mites: Spray Dicofol 18.5 EC @ 2.5 ml/litre or Abamectin. Maintain field moisture — mites thrive in dry conditions.",
}

_FERTILIZER_RESPONSES = {
    "urea":        "Urea (46% N): Apply as split doses — basal + top-dress. Avoid applying before heavy rain. Recommended rate varies by crop: Rice 120 kg/ha, Wheat 120 kg/ha.",
    "dap":         "DAP (Di-Ammonium Phosphate, 18-46-0): Apply as basal dose before sowing. Standard rate: 50-100 kg/ha. Store in dry conditions.",
    "potash":      "Muriate of Potash (MOP, 0-0-60): Apply at sowing or tillering stage. Rate: 40-60 kg/ha. Essential for grain quality and disease resistance.",
    "npk":         "NPK balanced fertilizer: Apply as per soil test report. General recommendation — Rice: 120:60:40, Wheat: 120:60:40, Maize: 150:75:60 kg/ha of N:P:K.",
    "micronutrient": "Micronutrients: Zinc Sulphate @ 25 kg/ha for zinc deficiency (common in rice). Boron (Borax @ 10 kg/ha) for mustard and tomato flowering stage.",
    "organic":     "Organic Manure: Apply FYM (Farm Yard Manure) @ 10-15 tonnes/ha or Vermicompost @ 2-3 tonnes/ha. Improves soil structure and long-term fertility.",
}

_SCHEME_RESPONSES = {
    "pm kisan":    "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi): ₹6,000/year in 3 instalments to eligible farmers. Register at pmkisan.gov.in or nearest CSC. Requires Aadhaar + land record.",
    "fasal bima":  "PM Fasal Bima Yojana: Crop insurance scheme covering yield loss due to drought, flood, hail, pest. Enroll before crop season through your bank or CSC. Premium: 2% for Kharif, 1.5% for Rabi.",
    "kcc":         "Kisan Credit Card (KCC): Short-term crop loan @ 4-7% interest. Apply at nearest bank with land documents. Provides revolving credit for seeds, fertilizers, pesticides.",
    "soil health": "Soil Health Card: Free soil testing every 2 years. Visit nearest Krishi Vigyan Kendra or district agriculture office. Recommendations provided for fertilizer use.",
    "enam":        "e-NAM (National Agriculture Market): Online mandi platform for better prices. Register at enam.gov.in. Sell produce digitally across mandis without middlemen.",
    "kisan call":  "Kisan Call Center: Toll-free helpline 1800-180-1551 (available 6 AM - 10 PM). Get free agricultural advice in your regional language.",
}

_WEATHER_RESPONSES = {
    "drought":     "Drought Management: Prioritize irrigation for critical growth stages (flowering, grain filling). Use mulching to conserve soil moisture. Consider growing drought-tolerant varieties like Drought Tolerant Rice. Contact local agriculture office for contingency crop plan.",
    "flood":       "Flood Management: Drain excess water immediately. After flood recession, apply potassium nitrate spray to revive crops. Remove lodged plants. Re-sow if >50% crop is damaged. Claim insurance under PMFBY.",
    "frost":       "Frost Protection: Light evening irrigation before frost protects root zone. Use smoke/burning crop residues in extreme cases. Cover seedlings with polythene. Apply potassium spray to strengthen cell walls.",
    "heat":        "Heat Stress Management: Increase irrigation frequency — twice daily for vegetables. Apply anti-transpirants (Kaolin @ 5%). Shade nets for nurseries. Harvest cereal crops early if grains are filling.",
    "rain":        "Rainfall Advisory: Monitor forecast closely. Ensure proper drainage. Avoid fertilizer application before heavy rain. In excess rain, apply fungicides preventively for blight and blast diseases.",
    "humidity":    "High Humidity Advisory: High humidity increases risk of fungal diseases (blight, rust, blast). Apply preventive fungicides. Improve air circulation by thinning plant canopy.",
}

_SOIL_RESPONSES = {
    "ph":          "Soil pH Management: pH < 5.5 — apply agricultural lime (CaCO3) @ 2-3 tonnes/ha. pH > 7.5 — apply gypsum or sulphur powder. Always do soil testing for precise recommendations.",
    "sandy":       "Sandy Soil Management: Sandy soils drain fast and hold less nutrients. Add organic matter (FYM, compost). Increase irrigation frequency. Use slow-release fertilizers.",
    "clay":        "Clay Soil Management: Clay soils drain poorly. Add gypsum and organic matter. Avoid tillage when wet. Raised beds for vegetable crops improve drainage.",
    "organic carbon": "Low Organic Carbon: Add FYM @ 10-15 t/ha, crop residue incorporation, green manuring (Dhaincha or Sunhemp). Organic carbon above 0.75% is ideal.",
    "nitrogen":    "Nitrogen deficiency: Yellowing of lower leaves (chlorosis). Apply urea or ammonium sulphate. Use split applications. Intercrop with legumes to fix atmospheric nitrogen.",
}

_GENERAL_RESPONSES = {
    "hello":       "🌱 Namaste! I am your Smart Crop Advisory assistant. Ask me about crop management, pests, fertilizers, government schemes, weather, or market prices. How can I help you today?",
    "help":        "I can answer questions about:\n• Crop advisory (fertilizers, irrigation, growth stages)\n• Pest & disease management\n• Weather impact on crops\n• Government schemes (PM-KISAN, Fasal Bima, KCC)\n• Soil health management\n• Mandi prices and market information",
    "mandi":       "For mandi price information, use the Market Prices section of this dashboard. It shows current modal prices, price trends, and distress alerts for your crop across multiple mandis.",
    "loan":        "Agricultural Loan Options: Kisan Credit Card (KCC) offers revolving credit at 4% interest. PM MUDRA Yojana for allied activities. NABARD provides long-term investment loans. Contact your nearest nationalized bank.",
    "storage":     "Grain Storage: Dry grain to <12% moisture (14% for paddy). Use clean, dry PUSA bins or hermetic bags. Fumigate with Aluminium Phosphide (2 tablets per tonne). Inspect monthly for pest damage.",
    "irrigation":  "Irrigation Scheduling: Use soil moisture feel method or tensiometer. Critical stages: germination, tillering (rice), flowering (all crops), grain filling. Drip/sprinkler saves 40-50% water.",
    "market":      "Market Information: Check the Mandi Prices section for real-time market data. For better prices, use e-NAM platform (enam.gov.in) or FPO (Farmer Producer Organizations) for collective selling.",
}


def _detect_category(message: str) -> str:
    """Detect the category of the farmer's query."""
    msg = message.lower()
    if any(k in msg for k in ["pest", "insect", "borer", "armyworm", "aphid", "thrips", "mite", "locust", "worm", "bug"]):
        return "pest"
    if any(k in msg for k in ["disease", "blast", "blight", "rust", "fungus", "rot", "wilt"]):
        return "disease"
    if any(k in msg for k in ["fertilizer", "urea", "dap", "npk", "potash", "nitrogen", "phosphorus", "micronutrient", "manure", "compost"]):
        return "fertilizer"
    if any(k in msg for k in ["scheme", "pm kisan", "fasal bima", "kcc", "insurance", "subsidy", "enam", "loan", "kisan call"]):
        return "scheme"
    if any(k in msg for k in ["weather", "rain", "drought", "flood", "frost", "heat", "humidity", "temperature"]):
        return "weather"
    if any(k in msg for k in ["soil", "ph", "sandy", "clay", "organic carbon", "nitrogen deficiency"]):
        return "soil"
    if any(k in msg for k in ["price", "mandi", "market", "sell", "rate"]):
        return "market"
    if any(k in msg for k in ["hello", "hi", "namaste", "help", "what can"]):
        return "general"
    return "general"


def _find_best_response(message: str, category: str, crop: str | None, growth_stage: str | None) -> str:
    """Find the best matching rule-based response."""
    msg = message.lower()

    if category == "pest" or category == "disease":
        for keyword, response in _PEST_RESPONSES.items():
            if keyword in msg:
                return response
        if crop:
            return (
                f"For pest/disease management in {crop}: Scout your field every 3-4 days. "
                "Use Economic Threshold Levels (ETL) before applying pesticides. "
                "Prefer bio-pesticides (Neem oil 3%, Bt) for early-stage control. "
                "Contact your local Krishi Vigyan Kendra for specific identification and treatment."
            )
        return "Monitor your field regularly. Use ETL-based integrated pest management (IPM). Contact KVK (Krishi Vigyan Kendra) for local pest identification and recommended treatments."

    if category == "fertilizer":
        for keyword, response in _FERTILIZER_RESPONSES.items():
            if keyword in msg:
                return response
        return "Apply fertilizers based on soil test recommendations (Soil Health Card). Follow N:P:K ratio recommended for your crop. Use split nitrogen applications for better uptake. Avoid over-fertilization."

    if category == "scheme":
        for keyword, response in _SCHEME_RESPONSES.items():
            if keyword in msg:
                return response
        return "Key Government Schemes: PM-KISAN (₹6,000/yr), PM Fasal Bima (crop insurance), Kisan Credit Card, e-NAM (digital mandi), Soil Health Card. Call 1800-180-1551 (Kisan Call Center) for more details."

    if category == "weather":
        for keyword, response in _WEATHER_RESPONSES.items():
            if keyword in msg:
                return response
        return "For weather-related decisions: check 5-day forecast in the Weather section of this dashboard. Critical: avoid spraying pesticides/fertilizers on windy or rainy days."

    if category == "soil":
        for keyword, response in _SOIL_RESPONSES.items():
            if keyword in msg:
                return response
        return "Get your Soil Health Card from the district agriculture office. It provides crop-specific fertilizer recommendations. Key parameters: pH (6-7.5 ideal), organic carbon (>0.75%), available N, P, K."

    if category == "market":
        return _GENERAL_RESPONSES["mandi"]

    for keyword, response in _GENERAL_RESPONSES.items():
        if keyword in msg:
            return response

    if crop and growth_stage:
        return (
            f"For {crop} at {growth_stage} stage: maintain regular field monitoring, "
            "apply inputs as per schedule, and consult the Crop Advisory section for AI-powered recommendations tailored to your field data. "
            "For specific queries, mention keywords like 'pest', 'fertilizer', 'scheme', or 'weather'."
        )

    return (
        "I can help with: crop advisory, pest & disease management, fertilizer recommendations, "
        "government schemes, weather impact, soil health, and market prices. "
        "Please ask a specific question or try: 'Help with rice blast disease' or 'PM-KISAN scheme details'."
    )


def _rule_based_reply(message: str, crop: str | None, growth_stage: str | None) -> tuple[str, str]:
    """Returns (response_text, category)."""
    category = _detect_category(message)
    response_text = _find_best_response(message, category, crop, growth_stage)
    return response_text, category


def _llm_reply(message: str, crop: str | None, growth_stage: str | None, language: str) -> str | None:
    """Try a Groq-generated reply. Returns None on any failure so the caller can fall back."""
    if _client is None:
        if Groq is None:
            logger.warning("Groq reply skipped: 'groq' package is not installed.")
        elif not _api_key:
            logger.warning("Groq reply skipped: GROQ_API_KEY is not set in .env.")
        return None

    context_lines = []
    if crop:
        context_lines.append(f"Farmer's current crop: {crop}")
    if growth_stage:
        context_lines.append(f"Current growth stage: {growth_stage}")
    context = "\n".join(context_lines) if context_lines else "No crop/stage context provided."

    prompt = f"""
You are an agricultural advisory chatbot for Indian farmers.

{context}

Farmer's question: {message}

Rules:
1. Only give advice that is safe, practical, and widely accepted agronomic practice for Indian farming conditions.
2. If the question is about pesticides or fertilizers, mention active ingredient, dose, and any key precaution.
3. Keep the answer short — 3-6 sentences, no headers, plain conversational text.
4. If you don't have enough information to answer safely, say so and suggest contacting the local Krishi Vigyan Kendra (KVK) or agriculture extension officer.
5. Do not invent scheme names, prices, or figures you are not confident about.
6. Respond in {language if language and language.lower() != "en" else "English"}.
"""

    try:
        response = _client.chat.completions.create(
            model=_MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a concise, safe, and practical agricultural advisory assistant for farmers.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=400,
        )
        content = response.choices[0].message.content
        return content.strip() if content else None
    except Exception as exc:
        logger.warning("Groq chat completion failed: %s", exc)
        return None


@router.post("/", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    """
    Farmer advisory chatbot.

    Tries a Groq LLM response first (if GROQ_API_KEY is configured) for a
    richer, context-aware reply. Falls back to the rule-based knowledge base
    if Groq is unavailable, unconfigured, or the call fails for any reason.
    """
    message = req.message.strip()
    if not message:
        return ChatResponse(
            response="Please enter a question. For example: 'How to treat rice blast disease?'",
            category="general",
            source="rule-based",
        )

    llm_response = _llm_reply(message, req.crop, req.growth_stage, req.language)
    if llm_response:
        category = _detect_category(message)
        return ChatResponse(response=llm_response, category=category, source="llm")

    response_text, category = _rule_based_reply(message, req.crop, req.growth_stage)
    return ChatResponse(response=response_text, category=category, source="rule-based")
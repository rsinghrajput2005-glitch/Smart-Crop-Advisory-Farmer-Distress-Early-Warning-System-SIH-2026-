# -*- coding: utf-8 -*-
"""
train_distress_risk.py
======================
Generates synthetic training data and trains a Farmer Distress Risk model.

** PROTOTYPE — SYNTHETIC DATA ONLY **
This script uses programmatically generated data to produce a working
prototype model for SIH 2026 demo purposes. Labels are derived from
multi-factor risk logic, not real distress survey data.

TODO (post-hackathon):
    - Collect real farmer distress data from Krishi Vibhag / state Agri Dept.
    - Incorporate historical loan default / crop insurance claim records.
    - Validate against known distress events (district-level crop loss data).

Features used:
    crop, location, ndvi_value, crop_condition,
    weather_risk, rainfall_mm, temperature_c,
    mandi_modal_price, price_trend_pct, price_distress_flag

Target:
    "Low"    – No immediate risk; routine monitoring
    "Medium" – Elevated risk; advisory intervention recommended
    "High"   – Severe risk; officer alert triggered

Model: XGBoost Classifier
Output: backend/models/distress_risk_model.pkl
        backend/models/distress_risk_label_encoder.pkl
"""

import os
import random
import pickle
import warnings

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

warnings.filterwarnings("ignore")

# ── Reproducibility ───────────────────────────────────────────────────────────
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# ── Output paths ─────────────────────────────────────────────────────────────
MODELS_DIR  = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

MODEL_PATH   = os.path.join(MODELS_DIR, "distress_risk_model.pkl")
ENCODER_PATH = os.path.join(MODELS_DIR, "distress_risk_label_encoder.pkl")

# ── Constants ─────────────────────────────────────────────────────────────────
N_SAMPLES = 10_000

CROPS = ["rice", "wheat", "maize", "tomato", "onion", "soybean", "mustard"]

# Indian state / district names (used as location labels)
LOCATIONS = [
    "Odisha", "Punjab", "Maharashtra", "Uttar Pradesh",
    "Madhya Pradesh", "Andhra Pradesh", "Karnataka", "Bihar",
]

# Crop condition labels (from NDVI interpretation)
CROP_CONDITIONS = [
    "Water / Non-vegetated",
    "Bare Soil / Sparse Vegetation",
    "Moderate Vegetation",
    "Healthy Crop",
    "Dense / Very Healthy Vegetation",
]

# Weather risk levels (from weather service)
WEATHER_RISKS = ["Low", "Medium", "High"]

# Price trend categories (from mandi service)
PRICE_TRENDS = [
    "Sharply Falling", "Falling", "Stable", "Rising", "Sharply Rising"
]

RISK_LABELS = ["Low", "Medium", "High"]

# Realistic base modal prices per crop (INR / Quintal)
CROP_BASE_PRICES = {
    "rice": 2000, "wheat": 2100, "maize": 1800,
    "tomato": 900, "onion": 800, "soybean": 4200, "mustard": 5200,
}


# ══════════════════════════════════════════════════════════════════════════════
# 1. SYNTHETIC DATA GENERATION
# ══════════════════════════════════════════════════════════════════════════════

def generate_row() -> dict:
    """
    Generate one synthetic distress-risk observation with a rule-based label.
    All ranges reflect realistic Indian agricultural conditions.
    """
    crop     = random.choice(CROPS)
    location = random.choice(LOCATIONS)

    # ── NDVI & crop condition ─────────────────────────────────────────────────
    ndvi_value     = round(random.uniform(0.0, 0.90), 4)
    crop_condition = _ndvi_to_condition(ndvi_value)

    # ── Weather ───────────────────────────────────────────────────────────────
    weather_risk   = random.choice(WEATHER_RISKS)
    rainfall_mm    = round(random.uniform(0.0, 250.0), 1)
    temperature_c  = round(random.uniform(8.0, 46.0), 1)

    # ── Market / Mandi ────────────────────────────────────────────────────────
    base_price = CROP_BASE_PRICES.get(crop, 2000)
    mandi_modal_price = round(base_price * random.uniform(0.55, 1.45))
    price_trend_pct   = round(random.uniform(-25.0, 25.0), 2)
    price_distress    = 1 if price_trend_pct <= -5 else 0

    # ── Rule-based risk label ─────────────────────────────────────────────────
    risk = _risk_rule(
        ndvi_value=ndvi_value,
        crop_condition=crop_condition,
        weather_risk=weather_risk,
        rainfall_mm=rainfall_mm,
        temperature_c=temperature_c,
        mandi_modal_price=mandi_modal_price,
        base_price=base_price,
        price_trend_pct=price_trend_pct,
        price_distress=price_distress,
    )

    return {
        "crop":               crop,
        "location":           location,
        "ndvi_value":         ndvi_value,
        "crop_condition":     crop_condition,
        "weather_risk":       weather_risk,
        "rainfall_mm":        rainfall_mm,
        "temperature_c":      temperature_c,
        "mandi_modal_price":  mandi_modal_price,
        "price_trend_pct":    price_trend_pct,
        "price_distress_flag": price_distress,
        "risk_level":         risk,
    }


def _ndvi_to_condition(ndvi: float) -> str:
    """Map NDVI value to crop condition label."""
    if ndvi < 0.05:
        return "Water / Non-vegetated"
    elif ndvi < 0.2:
        return "Bare Soil / Sparse Vegetation"
    elif ndvi < 0.4:
        return "Moderate Vegetation"
    elif ndvi < 0.6:
        return "Healthy Crop"
    else:
        return "Dense / Very Healthy Vegetation"


def _risk_rule(
    ndvi_value, crop_condition, weather_risk,
    rainfall_mm, temperature_c,
    mandi_modal_price, base_price,
    price_trend_pct, price_distress,
) -> str:
    """
    Multi-factor distress risk scoring.

    Score accumulation:
        +3 → Critical factor (very high risk contribution)
        +2 → Major factor
        +1 → Minor factor

    Thresholds:
        score >= 7  → High
        score >= 4  → Medium
        score <  4  → Low
    """
    score = 0

    # ── Crop condition / NDVI ─────────────────────────────────────────────────
    if crop_condition in ("Water / Non-vegetated", "Bare Soil / Sparse Vegetation"):
        score += 3
    elif crop_condition == "Moderate Vegetation":
        score += 1

    if ndvi_value < 0.15:
        score += 2  # reinforces bare/failed crop signal

    # ── Weather risk ──────────────────────────────────────────────────────────
    if weather_risk == "High":
        score += 3
    elif weather_risk == "Medium":
        score += 1

    # ── Extreme temperature ───────────────────────────────────────────────────
    if temperature_c > 43:
        score += 2
    elif temperature_c < 6:
        score += 2

    # ── Rainfall extremes ─────────────────────────────────────────────────────
    if rainfall_mm > 200:
        score += 2   # flood risk
    elif rainfall_mm < 5:
        score += 2   # severe drought

    # ── Mandi price distress ──────────────────────────────────────────────────
    if price_distress:
        score += 2
    if price_trend_pct <= -15:
        score += 1   # additional weight for sharp price crash

    # ── Price below 70% of base → forced selling / distress ──────────────────
    if mandi_modal_price < base_price * 0.70:
        score += 2

    # ── Final classification ──────────────────────────────────────────────────
    if score >= 7:
        return "High"
    elif score >= 4:
        return "Medium"
    else:
        return "Low"


# ══════════════════════════════════════════════════════════════════════════════
# 2. BUILD DATASET
# ══════════════════════════════════════════════════════════════════════════════

def build_dataset(n: int) -> pd.DataFrame:
    print(f"Generating {n:,} synthetic distress risk samples...")
    rows = [generate_row() for _ in range(n)]
    df = pd.DataFrame(rows)
    print("Risk label distribution:")
    print(df["risk_level"].value_counts())
    print()
    return df


# ══════════════════════════════════════════════════════════════════════════════
# 3. PREPROCESS
# ══════════════════════════════════════════════════════════════════════════════

def preprocess(df: pd.DataFrame):
    """Label-encode categoricals and return feature matrix X and target y."""
    le_crop      = LabelEncoder()
    le_location  = LabelEncoder()
    le_condition = LabelEncoder()
    le_weather   = LabelEncoder()

    df["crop_enc"]           = le_crop.fit_transform(df["crop"])
    df["location_enc"]       = le_location.fit_transform(df["location"])
    df["crop_condition_enc"] = le_condition.fit_transform(df["crop_condition"])
    df["weather_risk_enc"]   = le_weather.fit_transform(df["weather_risk"])

    feature_cols = [
        "crop_enc", "location_enc",
        "ndvi_value", "crop_condition_enc",
        "weather_risk_enc", "rainfall_mm", "temperature_c",
        "mandi_modal_price", "price_trend_pct", "price_distress_flag",
    ]
    X = df[feature_cols].values
    y = df["risk_level"].values

    encoders = {
        "crop":          le_crop,
        "location":      le_location,
        "crop_condition": le_condition,
        "weather_risk":  le_weather,
    }
    return X, y, feature_cols, encoders


# ══════════════════════════════════════════════════════════════════════════════
# 4. TRAIN MODEL
# ══════════════════════════════════════════════════════════════════════════════

def train(X, y, feature_cols: list):
    """Train XGBoost classifier and return model + label encoder."""
    le_label = LabelEncoder()
    y_enc = le_label.fit_transform(y)  # Low=0, Medium=1, High=2

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=RANDOM_SEED, stratify=y_enc
    )

    # Compute class weights for imbalanced labels
    class_counts = np.bincount(y_train)
    scale_pos = class_counts[0] / class_counts[2] if class_counts[2] > 0 else 1

    print("Training XGBoost Classifier...")
    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.08,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric="mlogloss",
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False,
    )

    # ── Evaluation ────────────────────────────────────────────────────────────
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Test Accuracy: {acc:.4f} ({acc*100:.2f}%)\n")

    print("Classification Report:")
    print(classification_report(
        y_test, y_pred,
        target_names=le_label.classes_,
        zero_division=0,
    ))

    print("Confusion Matrix (rows=actual, cols=predicted):")
    cm = confusion_matrix(y_test, y_pred)
    cm_df = pd.DataFrame(
        cm,
        index=[f"Actual {c}" for c in le_label.classes_],
        columns=[f"Pred {c}" for c in le_label.classes_],
    )
    print(cm_df.to_string())
    print()

    # ── Feature importance ────────────────────────────────────────────────────
    importances = sorted(
        zip(feature_cols, model.feature_importances_),
        key=lambda x: x[1], reverse=True
    )
    print("Feature Importances:")
    for name, imp in importances:
        bar = "#" * int(imp * 50)
        print(f"  {name:<25} {imp:.4f}  {bar}")
    print()

    return model, le_label


# ══════════════════════════════════════════════════════════════════════════════
# 5. SAVE ARTIFACTS
# ══════════════════════════════════════════════════════════════════════════════

def save_artifacts(model, le_label, feature_cols, encoders):
    payload = {
        "model":         model,
        "label_encoder": le_label,          # Low / Medium / High
        "feature_cols":  feature_cols,
        "encoders":      encoders,          # categorical column encoders
        "risk_labels":   list(le_label.classes_),
        "officer_alert_threshold": "High",  # trigger alert when risk == "High"
        "note": (
            "SYNTHETIC PROTOTYPE — trained on rule-based synthetic data. "
            "Replace with real distress survey / crop-loss data before production."
        ),
    }
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(payload, f)
    print(f"✅ Model saved → {MODEL_PATH}")


# ══════════════════════════════════════════════════════════════════════════════
# 6. MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  Farmer Distress Risk Model - Synthetic Training Script")
    print("  ** PROTOTYPE - SYNTHETIC DATA - SIH 2026 **")
    print("=" * 60)
    print()

    df                          = build_dataset(N_SAMPLES)
    X, y, feature_cols, encoders = preprocess(df)
    model, le_label             = train(X, y, feature_cols)
    save_artifacts(model, le_label, feature_cols, encoders)

    print()
    print("Done! High-risk predictions will trigger officer alerts.")

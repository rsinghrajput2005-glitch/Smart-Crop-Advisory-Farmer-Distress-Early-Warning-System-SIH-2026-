# -*- coding: utf-8 -*-
"""
train_crop_advisory.py
======================
Generates synthetic training data and trains a Crop Advisory model.

** PROTOTYPE — SYNTHETIC DATA ONLY **
This script uses programmatically generated data to produce a working
prototype model for SIH 2026 demo purposes. Labels are derived from
agronomic rule-of-thumb logic, not from real field observations.

TODO (post-hackathon):
    - Replace synthetic dataset with real labelled observations
      from agricultural extension officers / Krishi Vigyan Kendras.
    - Validate model performance on held-out real-world crop data.

Features used:
    crop, growth_stage, soil_ph, organic_carbon (g/kg),
    clay (%), sand (%), rainfall_mm, temperature_c,
    humidity_pct, ndvi

Target (advisory label):
    "No Action Needed"
    "Irrigate Now"
    "Apply Nitrogen Fertiliser"
    "Apply Pesticide / Fungicide"
    "Harvest Soon"
    "Crop Stress — Field Inspection Needed"

Model: Random Forest Classifier (scikit-learn)
Output: backend/models/crop_advisory_model.pkl
        backend/models/crop_advisory_label_encoder.pkl
"""

import os
import random
import pickle
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

warnings.filterwarnings("ignore")

# ── Reproducibility ───────────────────────────────────────────────────────────
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# ── Output paths ─────────────────────────────────────────────────────────────
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

MODEL_PATH    = os.path.join(MODELS_DIR, "crop_advisory_model.pkl")
ENCODER_PATH  = os.path.join(MODELS_DIR, "crop_advisory_label_encoder.pkl")

# ── Constants ─────────────────────────────────────────────────────────────────
N_SAMPLES = 8_000

CROPS = ["rice", "wheat", "maize", "tomato", "onion", "soybean", "mustard"]

GROWTH_STAGES = [
    "germination",
    "tillering",
    "vegetative",
    "flowering",
    "grain_filling",
    "harvesting",
]

ADVISORY_LABELS = [
    "No Action Needed",
    "Irrigate Now",
    "Apply Nitrogen Fertiliser",
    "Apply Pesticide / Fungicide",
    "Harvest Soon",
    "Crop Stress — Field Inspection Needed",
]


# ══════════════════════════════════════════════════════════════════════════════
# 1. SYNTHETIC DATA GENERATION
# ══════════════════════════════════════════════════════════════════════════════

def generate_row() -> dict:
    """
    Generate one synthetic crop observation with a rule-based advisory label.
    Ranges are calibrated to realistic agronomic values for Indian crops.
    """
    crop         = random.choice(CROPS)
    growth_stage = random.choice(GROWTH_STAGES)

    # ── Soil properties (SoilGrids-style realistic ranges) ───────────────────
    soil_ph          = round(random.uniform(4.5, 8.5), 2)
    organic_carbon   = round(random.uniform(2.0, 25.0), 2)   # g/kg
    clay             = round(random.uniform(5.0, 55.0), 2)   # %
    sand             = round(random.uniform(10.0, 80.0), 2)  # %

    # ── Weather (India monsoon / Rabi season ranges) ─────────────────────────
    rainfall_mm      = round(random.uniform(0.0, 200.0), 1)
    temperature_c    = round(random.uniform(10.0, 45.0), 1)
    humidity_pct     = round(random.uniform(20.0, 98.0), 1)

    # ── NDVI (0.0–1.0, realistic in-season range 0.2–0.85) ──────────────────
    ndvi             = round(random.uniform(0.05, 0.90), 4)

    # ── Rule-based advisory label ─────────────────────────────────────────────
    advisory = _advisory_rule(
        crop=crop,
        growth_stage=growth_stage,
        soil_ph=soil_ph,
        organic_carbon=organic_carbon,
        clay=clay,
        rainfall_mm=rainfall_mm,
        temperature_c=temperature_c,
        humidity_pct=humidity_pct,
        ndvi=ndvi,
    )

    return {
        "crop":            crop,
        "growth_stage":    growth_stage,
        "soil_ph":         soil_ph,
        "organic_carbon":  organic_carbon,
        "clay":            clay,
        "sand":            sand,
        "rainfall_mm":     rainfall_mm,
        "temperature_c":   temperature_c,
        "humidity_pct":    humidity_pct,
        "ndvi":            ndvi,
        "advisory":        advisory,
    }


def _advisory_rule(
    crop, growth_stage, soil_ph, organic_carbon,
    clay, rainfall_mm, temperature_c, humidity_pct, ndvi
) -> str:
    """
    Deterministic rule-based advisory assignment.
    Mimics agronomic heuristics used by extension officers.
    Rules are applied in priority order (most critical first).
    """
    # ── PRIORITY 1: Extreme stress → Field Inspection ────────────────────────
    if temperature_c > 42 and ndvi < 0.3:
        return "Crop Stress — Field Inspection Needed"
    if ndvi < 0.15 and growth_stage not in ("germination", "harvesting"):
        return "Crop Stress — Field Inspection Needed"
    if soil_ph < 4.8 or soil_ph > 8.2:
        return "Crop Stress — Field Inspection Needed"

    # ── PRIORITY 2: Harvest Soon ──────────────────────────────────────────────
    if growth_stage == "harvesting" and ndvi > 0.35:
        return "Harvest Soon"
    if growth_stage == "grain_filling" and ndvi > 0.6 and rainfall_mm < 10:
        return "Harvest Soon"

    # ── PRIORITY 3: Pest / Fungal risk ───────────────────────────────────────
    if humidity_pct > 85 and temperature_c > 25 and ndvi > 0.4:
        return "Apply Pesticide / Fungicide"
    if humidity_pct > 90 and growth_stage in ("flowering", "grain_filling"):
        return "Apply Pesticide / Fungicide"

    # ── PRIORITY 4: Irrigation needed ────────────────────────────────────────
    drought_crops = ["rice", "maize", "tomato", "onion"]
    if crop in drought_crops and rainfall_mm < 15 and temperature_c > 32:
        return "Irrigate Now"
    if clay < 15 and rainfall_mm < 10:
        # Sandy soil + low rain = poor moisture retention
        return "Irrigate Now"
    if ndvi < 0.3 and rainfall_mm < 20 and growth_stage in ("vegetative", "flowering"):
        return "Irrigate Now"

    # ── PRIORITY 5: Nitrogen deficiency ──────────────────────────────────────
    if organic_carbon < 5 and growth_stage in ("tillering", "vegetative", "flowering"):
        return "Apply Nitrogen Fertiliser"
    if ndvi < 0.35 and organic_carbon < 8 and growth_stage == "vegetative":
        return "Apply Nitrogen Fertiliser"

    # ── DEFAULT: No action ────────────────────────────────────────────────────
    return "No Action Needed"


# ══════════════════════════════════════════════════════════════════════════════
# 2. BUILD DATASET
# ══════════════════════════════════════════════════════════════════════════════

def build_dataset(n: int) -> pd.DataFrame:
    print(f"Generating {n:,} synthetic crop advisory samples...")
    rows = [generate_row() for _ in range(n)]
    df = pd.DataFrame(rows)
    print("Advisory label distribution:")
    print(df["advisory"].value_counts())
    print()
    return df


# ══════════════════════════════════════════════════════════════════════════════
# 3. PREPROCESS
# ══════════════════════════════════════════════════════════════════════════════

def preprocess(df: pd.DataFrame):
    """Encode categorical features and split into X, y."""
    le_crop  = LabelEncoder()
    le_stage = LabelEncoder()

    df["crop_enc"]         = le_crop.fit_transform(df["crop"])
    df["growth_stage_enc"] = le_stage.fit_transform(df["growth_stage"])

    feature_cols = [
        "crop_enc", "growth_stage_enc",
        "soil_ph", "organic_carbon", "clay", "sand",
        "rainfall_mm", "temperature_c", "humidity_pct", "ndvi",
    ]
    X = df[feature_cols].values
    y = df["advisory"].values

    return X, y, le_crop, le_stage


# ══════════════════════════════════════════════════════════════════════════════
# 4. TRAIN MODEL
# ══════════════════════════════════════════════════════════════════════════════

def train(X, y):
    """Train a Random Forest classifier and return model + label encoder."""
    le_label = LabelEncoder()
    y_enc = le_label.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=RANDOM_SEED, stratify=y_enc
    )

    print("Training Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=4,
        class_weight="balanced",   # handles any label imbalance
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

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

    # ── Feature importance ────────────────────────────────────────────────────
    feature_names = [
        "crop", "growth_stage",
        "soil_ph", "organic_carbon", "clay", "sand",
        "rainfall_mm", "temperature_c", "humidity_pct", "ndvi",
    ]
    importances = sorted(
        zip(feature_names, model.feature_importances_),
        key=lambda x: x[1], reverse=True
    )
    print("Feature Importances:")
    for name, imp in importances:
        bar = "#" * int(imp * 40)
        print(f"  {name:<20} {imp:.4f}  {bar}")
    print()

    return model, le_label


# ══════════════════════════════════════════════════════════════════════════════
# 5. SAVE ARTIFACTS
# ══════════════════════════════════════════════════════════════════════════════

def save_artifacts(model, le_label, le_crop, le_stage):
    payload = {
        "model":        model,
        "label_encoder": le_label,
        "encoders": {
            "crop": le_crop,
            "growth_stage": le_stage,
        },
        "feature_cols": [
            "crop_enc", "growth_stage_enc",
            "soil_ph", "organic_carbon", "clay", "sand",
            "rainfall_mm", "temperature_c", "humidity_pct", "ndvi",
        ],
        "advisory_labels": list(le_label.classes_),
        "note": (
            "SYNTHETIC PROTOTYPE — trained on rule-based synthetic data. "
            "Replace with real labelled field data before production use."
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
    print("  Crop Advisory Model - Synthetic Training Script")
    print("  ** PROTOTYPE - SYNTHETIC DATA - SIH 2026 **")
    print("=" * 60)
    print()

    df             = build_dataset(N_SAMPLES)
    X, y, le_crop, le_stage = preprocess(df)
    model, le_label = train(X, y)
    save_artifacts(model, le_label, le_crop, le_stage)

    print()
    print("Done! Run the backend to use this model at /advisory")

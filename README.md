# Smart Crop Advisory & Farmer Distress Early-Warning System

## Overview
A multilingual, low-bandwidth AI platform that combines **soil, weather, Sentinel-2 NDVI, and mandi-price data** to provide crop-stage-specific advisory and early farmer-distress risk detection.

### Farmer Input
The farmer provides only:
- Location
- Crop type
- Crop growth stage

Technical information such as soil properties and NDVI is collected automatically.

## Core Flow

```text
Farmer
  ↓
Location + Crop + Growth Stage
  ↓
Automatic Data Collection
  ├── SoilGrids → pH, Organic Carbon, Clay, Sand
  ├── Weather API → Temperature, Rainfall, Forecast
  ├── Sentinel-2 → NDVI / Crop Condition
  └── AGMARKNET/Govt. Data → Mandi Prices
  ↓
Feature Engineering
  ↓
AI / ML Analysis
  ├── Crop Condition / Advisory
  └── Distress Risk Prediction
  ↓
Low / Medium / High Risk
  ↓
Farmer Advisory + Officer Alert
```

## Data Sources

### Soil
**SoilGrids / ISRIC WCS**
- pH
- Organic Carbon
- Clay
- Sand
- Nitrogen and other available properties

Location is used to retrieve soil information.

### Weather
Weather API:
- Temperature
- Humidity
- Rainfall/precipitation
- Forecast
- Wind and other available parameters

### Satellite
**Sentinel-2**
- B4 = Red
- B8 = NIR

```text
NDVI = (B8 - B4) / (B8 + B4)
```

Cloud filtering should be applied before selecting the latest usable observation.

### Mandi
**AGMARKNET / Government data**
- Commodity
- Variety
- Market/Mandi
- Arrival date
- Minimum price
- Maximum price
- Modal price

Historical prices can be used to calculate price trends.

## Crop Advisory

```text
Crop + Growth Stage
        +
Soil + Weather + NDVI
        ↓
ML / Rule-based Analysis
        ↓
Crop Condition
        ↓
Stage-specific Advisory
```

Example:

```text
Crop: Rice
Stage: Flowering
NDVI: Moderate
Rainfall: Low
Soil: Dry

→ Irrigation advisory based on current conditions
```

## Distress Risk

```text
Crop Condition
+ Weather Risk
+ Mandi Price Trend
+ Other available indicators
        ↓
Distress Risk Model
        ↓
Low / Medium / High
```

A high-risk case can be highlighted on the agriculture-officer dashboard.

## ML Components

### Crop Condition / Advisory Model
Possible features:
- Crop
- Growth stage
- Soil pH
- Organic carbon
- Clay
- Sand
- Rainfall
- Temperature
- Humidity
- NDVI

Possible models:
- Random Forest
- XGBoost

### Distress Risk Model
Possible features:
- NDVI/crop condition
- Weather risk
- Rainfall
- Temperature
- Mandi price
- Historical price trend
- Crop
- Location

Output:
**Low / Medium / High**

## System Architecture

```text
Frontend
   ↓
FastAPI Backend
   ├── Soil Service
   ├── Weather Service
   ├── NDVI/Satellite Service
   └── Mandi Service
   ↓
Feature Engineering
   ↓
ML Models
   ├── Crop Advisory
   └── Distress Risk
   ↓
Database
   ↓
Farmer Dashboard + Officer Dashboard
```

## Main Screens
1. Farmer Home
2. Weather
3. Crop Advisory
4. Mandi Prices
5. Risk Score
6. Officer Dashboard

## Technology Stack
- **Frontend:** React / HTML-CSS-JS
- **Backend:** FastAPI + Python
- **ML:** Pandas, NumPy, Scikit-learn, XGBoost
- **Satellite:** Sentinel-2
- **Soil:** SoilGrids WCS
- **Weather:** Weather API
- **Market:** AGMARKNET / Government data
- **Database:** SQLite for prototype / PostgreSQL for scaling

## 5-Day Hackathon Plan

### Day 1 — Data & APIs
- SoilGrids integration
- Weather API
- Mandi data
- NDVI pipeline
- Data cleaning

### Day 2 — ML
- Prepare training data
- Feature engineering
- Train baseline models
- Save models

### Day 3 — Backend
- FastAPI endpoints
- External API integration
- ML model integration
- End-to-end backend testing

### Day 4 — Frontend & Integration
- Farmer screens
- Officer dashboard
- Connect frontend with backend
- Display advisory, weather, mandi and risk

### Day 5 — Testing & PPT
- End-to-end testing
- Bug fixing
- Demo scenario
- Final PPT
- Pitch and Q&A preparation

## Future Scope
- Sentinel-1 integration for cloudy conditions
- More crop-specific models
- More Indian languages
- Voice-first interaction
- Government-scheme recommendations
- Automated officer alerts
- Expansion from Odisha to other states

## Important
This is a hackathon prototype. Predictions and advisories should be validated against reliable agricultural guidance before real-world deployment. NDVI is an indicator of vegetation condition and should not be treated as a standalone diagnosis.

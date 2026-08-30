# 🌾 Smart Crop Advisory & Farmer Distress Early-Warning System

**Team Pragyan | Smart India Hackathon 2026**

## 📌 Overview

Smart Crop Advisory & Farmer Distress Early-Warning System is an AI-powered agricultural platform that combines **soil, weather, satellite and mandi-price data** to provide personalized, crop-stage-specific advisory and identify potential farmer distress at an early stage.

The farmer only needs to provide **location, crop type and growth stage**. The system automatically collects the required data and generates actionable recommendations.

## 💡 Key Features

- 🌱 Crop-stage-specific advisory
- 🧪 Location-based soil information using SoilGrids
- 🌦️ Current weather and forecast-based analysis
- 🛰️ Sentinel-2 based NDVI and crop-condition monitoring
- 💰 Current and historical mandi price analysis
- ⚠️ Farmer distress-risk score
- 💧 Irrigation advisory
- 🗣️ Multilingual STT/TTS voice support
- 📱 Lightweight interface for low-connectivity areas

## 🔄 System Workflow

**Farmer Input → Data Collection → Data Processing → AI/ML Analysis → Advisory & Risk Detection → Farmer/Officer Dashboard**

The system collects soil data from **SoilGrids**, weather and forecast data from a **Weather API**, crop-condition information from **Sentinel-2**, and market information from **mandi data**. These parameters are processed and combined with crop type and growth stage before being passed to the AI/ML module.

## 🏗️ System Architecture

The system follows a layered architecture where the frontend communicates with the FastAPI backend, which coordinates external agricultural data sources, the database, and AI/ML models.

```text
                         FARMER
                           │
                           ▼
              ┌─────────────────────┐
              │      FRONTEND       │
              │ Web / Mobile UI     │
              │ Map + Dashboard     │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   FASTAPI BACKEND   │
              │ API + Authentication│
              │ Data Integration    │
              └──────────┬──────────┘
                         │
             ┌───────────┼───────────┐
             │           │           │
             ▼           ▼           ▼
        ┌─────────┐ ┌──────────┐ ┌──────────┐
        │External │ │PostgreSQL│ │ AI / ML  │
        │  APIs   │ │ Database │ │  Models  │
        └────┬────┘ └──────────┘ └────┬─────┘
             │                        │
      ┌──────┼─────────┐              │
      ▼      ▼         ▼              │
   SoilGrids Weather  Sentinel-2      │
                     + NDVI           │
             │                        │
             ▼                        ▼
        Mandi Data              Predictions
             │                        │
             └───────────┬────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   ADVISORY ENGINE   │
              │ Crop Advisory       │
              │ Irrigation Advice   │
              │ Distress Risk       │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  FARMER / OFFICER   │
              │ Dashboard + Alerts  │
              │ Text + Voice        │
              └─────────────────────┘
```

## 🤖 AI/ML

The AI/ML module uses parameters such as:

- Crop type
- Growth stage
- Soil properties
- Weather and rainfall
- NDVI
- Mandi price trends

The model generates:

- Crop condition/stress indication
- Crop-stage-specific advisory
- Irrigation recommendation
- Farmer distress-risk score

Possible models include **Random Forest and XGBoost**.

## 🛰️ NDVI

Sentinel-2 imagery is used to monitor crop condition.

NDVI is calculated as:

`NDVI = (NIR - Red) / (NIR + Red)`

For Sentinel-2:

`Red = B4`  
`NIR = B8`

Cloud filtering is applied to select a valid/latest observation. Sentinel-1 can be integrated later for cloudy periods.

## 🗣️ Multilingual Voice Support

The system supports regional-language interaction using **Speech-to-Text (STT)** and **Text-to-Speech (TTS)**.

**Farmer Voice → STT → AI/ML Processing → Advisory → TTS → Regional-Language Voice**

This allows farmers to provide voice input and receive advisory in their preferred language.

## 🛠️ Technology Stack

**Frontend:** HTML, CSS, JavaScript, Leaflet.js, Chart.js

**Backend:** Python, FastAPI, Uvicorn

**Database:** PostgreSQL, SQLAlchemy

**AI/ML:** Scikit-learn, XGBoost, Joblib

**Data Processing:** Pandas, NumPy, SciPy

**Data Sources:** SoilGrids, Open-Meteo, Sentinel-2, AGMARKNET/Mandi Data

**Voice & Language:** Sarvam AI, STT, TTS

## 📊 Expected Outputs

**Crop Condition:** Healthy / Moderate Stress / High Stress

**Distress Risk:** Low / Medium / High

**Advisory:** Irrigation guidance, crop-management recommendations, weather-risk alerts and market-price insights.

## ⚠️ Challenges & Mitigation

- **Cloud cover:** Cloud filtering and latest valid Sentinel-2 observation
- **Missing data:** Validation and fallback data
- **Crop variability:** Crop and growth stage as model inputs
- **Limited labelled data:** Historical data and careful model validation
- **Prediction uncertainty:** Risk/confidence levels and real-world validation
- **Low connectivity:** Lightweight text and voice interface

## 🌍 Impact

**Social:** Regional-language access and early farmer support.

**Economic:** Reduced avoidable crop losses and better market decisions.

**Environmental:** Efficient water usage and sustainable resource management.

## 🔮 Future Scope

- Expansion to more states and crops
- Sentinel-1 integration for cloudy periods
- More Indian regional languages
- Improved distress-risk prediction
- District-level risk monitoring

## 📚 References

- SoilGrids Documentation
- Sentinel-2 Documentation
- Open-Meteo Documentation
- AGMARKNET
- Sarvam AI Documentation
- FastAPI Documentation
- Scikit-learn Documentation
- XGBoost Documentation

## 👥 Team Pragyan

**Smart Crop Advisory & Farmer Distress Early-Warning System**

Built for **Smart India Hackathon 2026**.

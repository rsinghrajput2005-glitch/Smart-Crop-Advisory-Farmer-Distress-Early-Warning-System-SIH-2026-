# models/ — saved ML model files (.pkl, .joblib, .json, etc.)
#
# Place trained model artifacts here, for example:
#   crop_advisory_model.pkl      — Random Forest / XGBoost crop advisory model
#   distress_risk_model.pkl      — Distress risk prediction model
#   label_encoders.pkl           — Fitted sklearn LabelEncoders for categorical features
#   scaler.pkl                   — Fitted StandardScaler / MinMaxScaler
#
# These files are loaded at startup by backend/model_apis/ inference endpoints.
# They are NOT committed to git (add *.pkl to .gitignore).

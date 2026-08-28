def calculate_distress_score(features):
    score = 0
    reasons = []

    rainfall = features.get("rainfall_deviation")
    if rainfall is not None:
        if rainfall <= -40:
            score += 25
            reasons.append("Severe rainfall deficit")
        elif rainfall <= -20:
            score += 15
            reasons.append("Rainfall is below normal")

    soil_moisture = features.get("soil_moisture")
    if soil_moisture is not None and soil_moisture > 1:
        soil_moisture = soil_moisture / 100

    if soil_moisture is not None:
        if soil_moisture < 0.20:
            score += 25
            reasons.append("Very low soil moisture")
        elif soil_moisture < 0.30:
            score += 15
            reasons.append("Low soil moisture")

    temperature = features.get("temperature")
    if temperature is not None:
        if temperature >= 40:
            score += 20
            reasons.append("Very high temperature")
        elif temperature >= 35:
            score += 10
            reasons.append("High temperature")

    if features.get("heavy_rain"):
        score += 15
        reasons.append("Heavy rainfall detected")

    market_change = features.get("market_price_change")
    if market_change is not None:
        if market_change <= -20:
            score += 20
            reasons.append("Severe market price decline")
        elif market_change <= -10:
            score += 15
            reasons.append("Significant market price decline")
        elif market_change <= -5:
            score += 10
            reasons.append("Market price is declining")

    score = min(score, 100)
    if score >= 60:
        risk_level = "HIGH"
    elif score >= 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "score": score,
        "risk_level": risk_level,
        "reasons": reasons,
    }


score_distress = calculate_distress_score
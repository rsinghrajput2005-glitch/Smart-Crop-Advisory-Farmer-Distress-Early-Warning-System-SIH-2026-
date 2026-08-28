def _coalesce(*values):
    for value in values:
        if value is not None:
            return value
    return None


def calculate_rainfall_deviation(actual, normal):
    if actual is None or normal is None or normal == 0:
        return None

    return round(((actual - normal) / normal) * 100, 2)


def detect_heavy_rain(precipitation):
    if precipitation is None:
        return False

    return precipitation >= 50


def build_features(data, normal_rainfall=None):
    weather = data.get("weather", {}) or {}
    market_data = data.get("market") or data.get("mandi") or {}
    markets = market_data.get("markets", []) or []

    temperature = _coalesce(weather.get("temperature"), weather.get("temperature_c"))
    humidity = _coalesce(weather.get("humidity"), weather.get("humidity_percent"))
    precipitation = _coalesce(weather.get("precipitation"), weather.get("precipitation_mm"))
    soil_moisture = _coalesce(weather.get("soil_moisture"), weather.get("soil_moisture_m3_m3"))

    rainfall_deviation = calculate_rainfall_deviation(precipitation, normal_rainfall)
    heavy_rain = bool(weather.get("heavy_rain", False)) or detect_heavy_rain(precipitation)

    current_price = None
    previous_price = None
    price_change = None

    if markets:
        first_market = markets[0]
        current_price = _coalesce(first_market.get("modal_price"), first_market.get("current_price"))
        previous_price = _coalesce(
            first_market.get("previous_modal_price"),
            first_market.get("previous_price"),
        )
        price_change = _coalesce(
            first_market.get("price_change_percent"),
            first_market.get("price_change"),
        )

    if current_price is not None and previous_price is not None and previous_price != 0 and price_change is None:
        price_change = round(((current_price - previous_price) / previous_price) * 100, 2)

    return {
        "temperature": temperature,
        "humidity": humidity,
        "precipitation": precipitation,
        "rainfall_deviation": rainfall_deviation,
        "soil_moisture": soil_moisture,
        "heavy_rain": heavy_rain,
        "market_price_change": price_change,
        "current_market_price": current_price,
        "previous_market_price": previous_price,
    }
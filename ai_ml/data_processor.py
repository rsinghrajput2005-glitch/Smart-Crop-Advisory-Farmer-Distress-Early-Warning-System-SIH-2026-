def calculate_rainfall_deviation(
    actual_rainfall,
    normal_rainfall
):

    if normal_rainfall == 0:
        return None

    return round(
        (
            (actual_rainfall - normal_rainfall)
            / normal_rainfall
        ) * 100,
        2
    )


def calculate_price_change(
    current_price,
    previous_price
):

    if previous_price == 0:
        return None

    return round(
        (
            (current_price - previous_price)
            / previous_price
        ) * 100,
        2
    )
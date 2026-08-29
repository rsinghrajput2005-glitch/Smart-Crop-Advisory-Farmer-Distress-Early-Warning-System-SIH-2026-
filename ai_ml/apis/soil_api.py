import requests


SOILGRIDS_URL = (
    "https://rest.isric.org/"
    "soilgrids/v2.0/properties/query"
)


def get_soil_data(latitude, longitude):

    params = [

        ("lon", longitude),
        ("lat", latitude),

        ("property", "phh2o"), 
        ("property", "nitrogen"),
        ("property", "clay"),
        ("property", "sand"),
        ("property", "silt"),
        ("property", "soc"),

        ("depth", "0-5cm"),
        ("depth", "5-15cm"),
        ("depth", "15-30cm"),

        ("value", "mean")
    ]

    response = requests.get(
        SOILGRIDS_URL,
        params=params,
        timeout=60
    )

    response.raise_for_status()

    return response.json()
from pathlib import Path

import pandas as pd


# mandi_csv.py
# Location:
# ai_ml/apis/mandi_csv.py

AI_ML_DIR = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    AI_ML_DIR
    / "data"
    / "processed"
    / "mandi_price_clean.pkl"
)


def load_mandi_data():

    print(
        "Loading dataset from:"
    )

    print(
        DATASET_PATH
    )

    print(
        "File exists:",
        DATASET_PATH.exists()
    )

    if not DATASET_PATH.exists():

        raise FileNotFoundError(
            f"\nMandi dataset not found:\n"
            f"{DATASET_PATH}\n\n"
            f"Please put mandi_price_clean.pkl "
            f"inside ai_ml/data/processed/"
        )

    df = pd.read_pickle(
        DATASET_PATH
    )

    print(
        "Dataset loaded successfully!"
    )

    print(
        "Rows:",
        len(df)
    )

    return df


def search_mandi_prices(
    state=None,
    district=None,
    commodity=None
):

    df = load_mandi_data()

    if state:

        df = df[
            df["STATE"]
            .astype(str)
            .str.strip()
            .str.lower()
            == state.strip().lower()
        ]

    if district:

        df = df[
            df["District Name"]
            .astype(str)
            .str.strip()
            .str.lower()
            == district.strip().lower()
        ]

    if commodity:

        df = df[
            df["Commodity"]
            .astype(str)
            .str.strip()
            .str.lower()
            == commodity.strip().lower()
        ]

    return df
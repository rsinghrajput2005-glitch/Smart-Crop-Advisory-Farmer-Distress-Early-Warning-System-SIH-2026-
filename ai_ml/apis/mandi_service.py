from ai_ml.apis.mandi_csv import (
    search_mandi_prices
)


def get_mandi_summary(
    state,
    district,
    commodity
):

    df = search_mandi_prices(
        state=state,
        district=district,
        commodity=commodity
    )

    if df.empty:

        return {
            "found": False,
            "message": "No mandi data found.",
            "markets": []
        }

    # Latest available date
    latest_date = df["Price Date"].max()

    latest_data = df[
        df["Price Date"] == latest_date
    ].copy()

    # One record per market
    latest_data = (
        latest_data
        .sort_values(
            "Modal_Price",
            ascending=False
        )
        .drop_duplicates(
            subset=["Market Name"]
        )
    )

    markets = []

    for _, row in latest_data.iterrows():

        price_change = row[
            "Price_Change_Percent"
        ]

        if price_change != price_change:
            price_change = None

        markets.append({

            "market":
                row["Market Name"],

            "commodity":
                row["Commodity"],

            "modal_price":
                float(row["Modal_Price"]),

            "min_price":
                float(row["Min_Price"]),

            "max_price":
                float(row["Max_Price"]),

            "price_change_percent":
                (
                    float(price_change)
                    if price_change is not None
                    else None
                ),

            "date":
                row["Price Date"].strftime(
                    "%Y-%m-%d"
                )
        })

    return {

        "found": True,

        "state": state,

        "district": district,

        "commodity": commodity,

        "latest_date":
            latest_date.strftime(
                "%Y-%m-%d"
            ),

        "markets": markets
    }
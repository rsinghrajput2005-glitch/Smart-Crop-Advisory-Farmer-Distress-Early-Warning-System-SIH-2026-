from ai_ml.apis.mandi_csv import (
    search_mandi_prices
)


def main():

    print(
        "\n========== MANDI TEST ==========\n"
    )

    data = search_mandi_prices(
        state="Maharashtra",
        district="nashik",
        commodity="Wheat"
    )

    print(
        "\nRecords found:",
        len(data)
    )

    if not data.empty:

        print(
            data[
                [
                    "STATE",
                    "District Name",
                    "Market Name",
                    "Commodity",
                    "Modal_Price",
                    "Previous_Modal_Price",
                    "Price_Change_Percent",
                    "Price Date"
                ]
            ]
            .tail(10)
            .to_string(index=False)
        )

    else:

        print(
            "\nNo matching records found."
        )

    print(
        "\n================================\n"
    )


if __name__ == "__main__":
    main()
from ai_ml.apis.mandi_service import (
    get_mandi_summary
)


def main():

    result = get_mandi_summary(

        state="Maharashtra",

        district="nashik",

        commodity="Wheat"
    )

    print(
        "\n========== MANDI SUMMARY ==========\n"
    )

    print(
        "Found:",
        result["found"]
    )

    print(
        "Latest Date:",
        result.get("latest_date")
    )

    print(
        "\nMarkets:"
    )

    for market in result.get(
        "markets",
        []
    )[:10]:

        print(
            f"\n{market['market']}"
        )

        print(
            f"Modal Price: "
            f"₹{market['modal_price']}"
        )

        print(
            f"Min Price: "
            f"₹{market['min_price']}"
        )

        print(
            f"Max Price: "
            f"₹{market['max_price']}"
        )

        print(
            f"Price Change: "
            f"{market['price_change_percent']}%"
        )

        print(
            f"Date: "
            f"{market['date']}"
        )


if __name__ == "__main__":

    main()
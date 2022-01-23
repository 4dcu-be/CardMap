import sys
import pandas as pd
from os import path

if __name__ == "__main__":
    orders = sys.argv[1]
    output_dir = sys.argv[2]

    processed_data = pd.read_csv(orders)

    by_location = (
        processed_data.groupby(["lng", "lat"])
            .agg(
            card_value=pd.NamedAgg("card_value", sum),
            card_count=pd.NamedAgg("card_count", sum),
            shipping=pd.NamedAgg("shipping", sum),
            order_count=pd.NamedAgg("shipping", "count"),
            zip=pd.NamedAgg("zip", "first"),
            city=pd.NamedAgg("city", "first"),
            country=pd.NamedAgg("country", "first"),
        )
            .reset_index()
    )

    by_location.to_csv(path.join(output_dir, "orders_by_location.csv"), index=None)

    by_country = (
        processed_data.groupby(["country"])
            .agg(
            card_value=pd.NamedAgg("card_value", sum),
            card_count=pd.NamedAgg("card_count", sum),
            shipping=pd.NamedAgg("shipping", sum),
            order_count=pd.NamedAgg("shipping", "count"),
        )
            .reset_index()
    )

    by_country.to_csv(path.join(output_dir, "orders_by_country.csv"), index=None)

    totals = pd.DataFrame(
        by_country.drop(columns=["country"]).sum(axis="rows"), columns=["total"]
    )
    totals.to_csv(path.join(output_dir, "orders_summary.csv"))

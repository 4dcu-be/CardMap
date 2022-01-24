import sys
import pandas as pd
from os import path

from operations import groupby_country, summarize, groupby_location

if __name__ == "__main__":
    orders = sys.argv[1]
    output_dir = sys.argv[2]

    # Read input
    processed_data = pd.read_csv(orders)

    # Transform
    by_location = processed_data.pipe(groupby_location)
    by_country = processed_data.pipe(groupby_country)
    totals = processed_data.pipe(summarize)

    # Write output
    by_location.to_csv(path.join(output_dir, "orders_by_location.csv"), index=None)
    by_country.to_csv(path.join(output_dir, "orders_by_country.csv"), index=None)
    totals.to_csv(path.join(output_dir, "orders_summary.csv"))

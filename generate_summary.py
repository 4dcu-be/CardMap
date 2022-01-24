import sys
import pandas as pd
from os import path

from operations import groupby_country, summarize, groupby_location
import click


@click.command()
@click.argument('orders')
@click.argument('output_dir')
def run(orders, output_dir):
    """
    Will read a CSV file with parsed ORDERS and generate some summary statistics by location, country and total. The
    results will be written to different files in OUTPUT_DIR


    :param orders: path to CSV file with parsed orders
    :param output_dir: directory to write summary statistics to
    """
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


if __name__ == "__main__":
    run()



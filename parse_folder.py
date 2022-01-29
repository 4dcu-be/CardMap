import pandas as pd
import os

from operations import add_new_shipments, start_pipeline, add_coordinates
from dotenv import load_dotenv

import click


load_dotenv()  # take environment variables from .env.

COLUMNS = [
    "shipment_id",
    "zip",
    "city",
    "country",
    "card_value",
    "card_count",
    "shipping",
    "order_date",
    "lng",
    "lat",
]


def load_data(file: str) -> pd.DataFrame:
    try:
        output = pd.read_csv(file)
    except Exception as _:
        output = pd.DataFrame(columns=COLUMNS)

    return output


@click.command()
@click.argument("orders")
@click.argument("eml_data")
@click.option("--api_key", default=None, help="Google Geocoding API key")
def run(orders, eml_data, api_key=None):
    """
    Will load previously parsed from ORDERS (or create a new file if these don't exist), and parse all eml files in
    EML_DATA, geocode the results and add these.

    :param orders: Path to an existing CSV file with previously parsed orders
    :param eml_data: Path to directory with EML files to be processed
    :param api_key: A Google API key which can access the Geocoding API
    """
    # Get API key from Google's Geocoding API from environment vars
    if api_key is None:
        api_key = os.environ["API_KEY"]

    # # Get command line args
    # orders = sys.argv[1]
    # eml_data = sys.argv[2]

    # Load orders (or create new df)
    processed_data = load_data(orders)

    # Add new shipments (from eml files) and add coordinates
    processed_data = (
        processed_data.pipe(start_pipeline)
        .pipe(add_new_shipments, eml_data)
        .pipe(add_coordinates, api_key)
    )

    # Write output
    processed_data.to_csv(orders, index=None)


if __name__ == "__main__":
    run()

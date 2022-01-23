import sys

import pandas as pd
import os

from operations import add_new_shipments, start_pipeline, add_coordinates
from dotenv import load_dotenv

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


if __name__ == "__main__":
    api_key = os.environ[
        "API_KEY"
    ]  # Get API key from Google's Geocoding API from environment vars

    orders = sys.argv[1]
    eml_data = sys.argv[2]

    processed_data = load_data(orders)

    processed_data = (
        processed_data.pipe(start_pipeline)
        .pipe(add_new_shipments, eml_data)
        .pipe(add_coordinates, api_key)
    )

    processed_data.to_csv(orders, index=None)



import pandas as pd
import os

from operations import add_new_shipments, start_pipeline, add_coordinates


COLUMNS = ['shipment_id', 'zip', 'city', 'country', 'card_value', 'card_count', 'shipping', 'order_date', 'lng', 'lat']


def load_data(file: str) -> pd.DataFrame:
    try:
        output = pd.read_csv(file)
    except Exception as _:
        output = pd.DataFrame(columns=COLUMNS)

    return output


if __name__ == "__main__":
    api_key = os.environ['API_KEY']  # Get API key from Google's Geocoding API from environment vars

    processed_data = load_data('./data/shipped_orders.csv')

    processed_data = processed_data\
        .pipe(start_pipeline)\
        .pipe(add_new_shipments, './eml_data/')\
        .pipe(add_coordinates, api_key)

    processed_data.to_csv('./data/shipped_orders.csv', index=None)

    by_location = processed_data.groupby(['lng', 'lat']).agg(
        card_value=pd.NamedAgg('card_value', sum),
        card_count=pd.NamedAgg('card_count', sum),
        shipping=pd.NamedAgg('shipping', sum),
        order_count=pd.NamedAgg('shipping', 'count'),
        zip=pd.NamedAgg('zip', 'first'),
        city=pd.NamedAgg('city', 'first'),
        country=pd.NamedAgg('country', 'first')
    ).reset_index()

    by_location.to_csv('./data/orders_by_location.csv', index=None)

    by_country = processed_data.groupby(['country']).agg(
        card_value=pd.NamedAgg('card_value', sum),
        card_count=pd.NamedAgg('card_count', sum),
        shipping=pd.NamedAgg('shipping', sum),
        order_count=pd.NamedAgg('shipping', 'count')
    ).reset_index()

    by_country.to_csv('./data/orders_by_country.csv', index=None)

    totals = pd.DataFrame(by_country.drop(columns=['country']).sum(axis='rows'), columns=['total'])
    totals.to_csv('./data/orders_summary.csv')

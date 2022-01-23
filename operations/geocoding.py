import googlemaps
import numpy as np
import pandas as pd


def prepare_address(row):
    """
    Takes a row from the dataframe and combines zip code, city and country columns in a valid address string for
    Google's Geocoding API

    :param row: row from a dataframe that countains a field zip, city and country
    :return: address compatible with Geocoding API
    """
    return f"{row['zip']} {row['city']}, {row['country']}"


def add_coordinates(df: pd.DataFrame, api_key: str):
    """
    Adds longitude and latitude in the fields lng and lat of a Pandas DataFrame that contains address information
    (zip, city and country).

    :param df: Pandas dataframe containing zip, city and country columns
    :param api_key: API key for Googles Geocoding API
    :return: dataframe with columns lng and lat completed with the geocoding data
    """
    new_df = df.copy()

    gmaps = googlemaps.Client(key=api_key)

    for ix, row in new_df.iterrows():
        if np.isnan(row['lat']):
            geocode_result = gmaps.geocode(prepare_address(row))
            location = geocode_result[0]['geometry']['location']
            new_df.at[ix, 'lat'] = location['lat']
            new_df.at[ix, 'lng'] = location['lng']

    return new_df

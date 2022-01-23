import pandas as pd

from .shipments import add_new_shipments
from .geocoding import add_coordinates


def start_pipeline(df: pd.DataFrame):
    """
    Small function to be used with pandas' .pipe to make sure the original df isn't altered unintentionally

    :param df: input dataframe
    :return: copy of input
    """
    return df.copy()

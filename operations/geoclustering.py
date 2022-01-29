from math import radians

import pandas as pd
from scipy.cluster import hierarchy as shc
from scipy.spatial import distance as ssd
from sklearn.metrics.pairwise import haversine_distances


def cluster_locations(df: pd.DataFrame, height=100) -> pd.DataFrame:
    """
    Calculates distance between all locations, clusters them and groups the clusters

    :param df: input dataframe, should have longitude (lng), latitude (lat), city and country information along with
    card_value, card_count, order_count and shipping
    :param height: where to cut hierarchical clustering, smaller value will generate more clusters
    :return: dataframe with locations clustered
    """
    locations_radians = list(
        df.apply(lambda x: [radians(x.lat), radians(x.lng)], axis="columns")
    )

    distance_matrix = haversine_distances(locations_radians) * 6371
    compressed_distance = ssd.squareform(distance_matrix)

    df["cluster"] = shc.cut_tree(shc.ward(compressed_distance), height=height).flatten()

    output = (
        df.groupby(["cluster", "country"])
        .agg(
            lng=pd.NamedAgg("lng", "mean"),
            lat=pd.NamedAgg("lat", "mean"),
            city=pd.NamedAgg("city", lambda x: ", ".join(x)),
            card_value=pd.NamedAgg("card_value", "sum"),
            card_count=pd.NamedAgg("card_count", "sum"),
            shipping=pd.NamedAgg("shipping", "sum"),
            order_count=pd.NamedAgg("order_count", "sum"),
            country=pd.NamedAgg("country", "first"),
            locations=pd.NamedAgg("city", "size"),
        )
        .sort_values("locations", ascending=False)
    )

    return output

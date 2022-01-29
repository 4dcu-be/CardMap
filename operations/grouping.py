import pandas as pd


def groupby_country(df: pd.DataFrame):
    return (
        df.groupby(["country"])
        .agg(
            card_value=pd.NamedAgg("card_value", sum),
            card_count=pd.NamedAgg("card_count", sum),
            shipping=pd.NamedAgg("shipping", sum),
            order_count=pd.NamedAgg("shipping", "count"),
        )
        .reset_index()
    )


def summarize(df: pd.DataFrame):
    df_by_country = groupby_country(df)

    return pd.DataFrame(
        df_by_country.drop(columns=["country"]).sum(axis="rows"), columns=["total"]
    )


def groupby_location(df: pd.DataFrame):
    return (
        df.groupby(["lng", "lat"])
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

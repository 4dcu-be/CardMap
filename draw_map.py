import altair as alt
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import geopandas as gpd

world_data = pd.read_json("./map_data/world-110m-country-codes.json")

format_cost = lambda x: f"€ {x:.02f}"
format_cards = lambda x: f"{x} card" if x == 1 else f"{x} cards"

projection_params = {
    "scale": 900,
    "rotate": [-10, 0],
    "center": [0, 50],
    "parallels": [35, 65],
    "precision": 0.1,
}

gdf = gpd.read_file(
    "./map_data/countries-50m.json",
    driver="TopoJSON",
).fillna(-1)
gdf["id"] = gdf["id"].astype(int)


def get_country_data(filename):
    country_data = pd.read_csv(filename)
    country_data = pd.merge(
        country_data,
        world_data[["id", "name"]],
        how="left",
        left_on="country",
        right_on="name",
    ).drop(columns="name")

    country_data["card_value_str"] = country_data["card_value"].apply(format_cost)
    country_data["shipping_str"] = country_data["shipping"].apply(format_cost)
    country_data["card_count_str"] = country_data["card_count"].apply(format_cards)
    country_data["title"] = country_data.apply(
        lambda x: f"{x['country']} (1 order)"
        if x["order_count"] == 1
        else f"{x['country']} ({x['order_count']} orders)",
        axis="columns",
    )

    mms = MinMaxScaler(feature_range=(0, 100))
    mms_data = mms.fit_transform(
        country_data[["card_value", "card_count", "shipping", "order_count"]]
    )

    country_data[
        ["card_value_mms", "card_count_mms", "shipping_mms", "order_count_mms"]
    ] = mms_data

    return country_data


def get_location_data(filename):
    location_data = pd.read_csv(filename)
    location_data["card_value_str"] = location_data["card_value"].apply(format_cost)
    location_data["shipping_str"] = location_data["shipping"].apply(format_cost)
    location_data["card_count_str"] = location_data["card_count"].apply(format_cards)
    location_data["title"] = location_data.apply(
        lambda x: f"{x['city']} (1 order)"
        if x["order_count"] == 1
        else f"{x['city']} ({x['order_count']} orders)",
        axis="columns",
    )

    return location_data


def create_map(country_data, location_data):
    long_normalized_df = country_data.melt(
        id_vars=[
            "country",
            "card_value",
            "card_count",
            "shipping",
            "order_count",
            "id",
            "card_value_str",
            "shipping_str",
            "card_count_str",
            "title",
        ],
        value_vars=[
            "card_value_mms",
            "card_count_mms",
            "shipping_mms",
            "order_count_mms",
        ],
        ignore_index=True,
    )

    country_geo_df = (
        pd.merge(
            gdf[["id", "geometry"]],
            long_normalized_df,
            how="right",
            left_on="id",
            right_on="id",
        )
        .replace(
            {
                "card_value_mms": "Card value",
                "card_count_mms": "Card count",
                "shipping_mms": "Shipping cost",
                "order_count_mms": "Orders",
            }
        )
        .sort_values("variable", ascending=False)
    )

    background = (
        alt.Chart(gdf)
        .mark_geoshape(fill="lightgray", stroke="white")
        .project("conicEquidistant", **projection_params)
        .properties(width=700, height=500)
    )

    input_dropdown = alt.binding_select(
        options=["Card count", "Card value", "Orders", "Shipping cost"],
        name="Color countries by : ",
    )
    selection = alt.selection_single(
        fields=["variable"], bind=input_dropdown, init={"variable": "Card value"}
    )

    heatmap = (
        alt.Chart(country_geo_df)
        .mark_geoshape(stroke="white")
        .encode(
            color=alt.Color("value:Q", title=None, legend=None),
            tooltip=[
                alt.Tooltip("title:O", title="Country"),
                alt.Tooltip("card_value_str:O", title="Total value"),
                alt.Tooltip("shipping_str:O", title="Total shipping"),
                alt.Tooltip("card_count_str:O", title="Cards ordered"),
            ],
        )
        .add_selection(selection)
        .transform_filter(selection)
        .project("conicEquidistant", **projection_params)
        .properties(width=800, height=500)
    )

    points = (
        alt.Chart(location_data)
        .mark_circle()
        .project("conicEquidistant", **projection_params)
        .encode(
            longitude="lng:Q",
            latitude="lat:Q",
            size=alt.Size("locations:O", scale=alt.Scale(range=[50, 300]), legend=None),
            tooltip=[
                alt.Tooltip("title", title="City"),
                alt.Tooltip("card_value_str:O", title="Total value"),
                alt.Tooltip("shipping_str:O", title="Total shipping"),
                alt.Tooltip("card_count_str:O", title="Cards ordered"),
            ],
        )
        .add_selection(alt.selection_single())
    )

    numbers = (
        alt.Chart(location_data[location_data.order_count > 1])
        .mark_text(align="center", baseline="middle", color="white", size=6)
        .project("conicEquidistant", **projection_params)
        .encode(
            longitude="lng:Q",
            latitude="lat:Q",
            text="order_count:Q",
            tooltip=[
                alt.Tooltip("title", title="City"),
                alt.Tooltip("card_value_str:O", title="Total value"),
                alt.Tooltip("shipping_str:O", title="Total shipping"),
                alt.Tooltip("card_count_str:O", title="Cards ordered"),
            ],
        )
        .add_selection(
            alt.selection_single()
        )  # https://stackoverflow.com/questions/65755698/altair-tooltips-dont-work-when-using-selection
    )

    return background + heatmap + points + numbers


if __name__ == "__main__":
    country_data = get_country_data("./data/orders_by_country.csv")
    location_data = get_location_data("./data/orders_by_location_cluster.csv")

    altair_map = create_map(country_data, location_data)

    altair_map.save("./docs/index.html")

    output_chart = altair_map.properties(width="container", height=500)
    output_chart.save("mtg_map.json")

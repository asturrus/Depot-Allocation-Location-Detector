import streamlit as st
import leafmap.foliumap as leafmap
from folium.plugins import MarkerCluster
import folium

st.set_page_config(layout="wide")

markdown = """
Cluster Map Visualization of Data Coordinates
"""

st.sidebar.title("About")
st.sidebar.info(markdown)

st.title("Marker Cluster")

m = leafmap.Map(center=[40, -100], zoom=4)
cities = "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_cities.csv"
regions = "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_regions.geojson"
m.add_geojson(regions, layer_name="US Regions")
m.add_points_from_xy(
    cities,
    x="longitude",
    y="latitude",
    color_column="region",
    icon_names=["gear", "map", "leaf", "globe"],
    spin=True,
    add_legend=True,
)

m.to_streamlit(height=700)
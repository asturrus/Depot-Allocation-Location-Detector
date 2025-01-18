import streamlit as st
import leafmap.foliumap as leafmap
from pathlib import Path
import pandas as pd
import geopandas as gpd
# import pymongo
# from sklearn.cluster import KMeans
# import numpy as np

markdown = """
TBD TO WRITE LATER ON
"""

st.set_page_config(layout="wide")

st.sidebar.title("About")
st.sidebar.info(markdown)

st.title("Depot Allocation Location Detector")

st.header("Instructions")

markdown = """
1. Input a media file or media files containing 'latitude' and 'longitude' information
2. The Depot Allocation Location Detector will parse the data files
3. Following the parsing the data will be displayed via various GeoSpatial Maps
4. Option to view parsed data on Cluster map, Heat map, and Priority Chart

"""

st.markdown(markdown)

coordinates = None

with st.form("my_form", clear_on_submit=True):

    uploaded_files = st.file_uploader(
        "Select a CSV, GeoJson, ShapeFile file(s)", accept_multiple_files=True, type=['geojson', 'csv', 'shp']
    )
    for uploaded_file in uploaded_files:
        file_extension = (Path(uploaded_file.name).suffix)

        if file_extension == '.csv' :
            try:
                df = pd.read_csv(uploaded_file)

                # Ensure 'latitude' and 'longitude' columns exist
                if {"latitude", "longitude"}.issubset(df.columns.str.lower()):
                    df.columns = df.columns.str.lower()  # Normalize column names
                    coordinates = df
                else:
                        st.error("The CSV file must contain 'latitude' and 'longitude' columns.")

            except Exception as e:
                st.error(f"Error reading CSV file: {e}")


        # elif file_extension == '.shp' :
        #     data = gpd.read_file(uploaded_file)
        #     data.to_csv('output.csv', index=False)
        #     coordinates = 'output.csv'


        elif file_extension == '.geojson' :
            try:
                gdf = gpd.read_file(uploaded_file)

                if {"latitude", "longitude"}.issubset(gdf.columns.str.lower()):
                    gdf.columns = gdf.columns.str.lower()
                    coordinates = gdf

                else:
                    st.error("The GeoJSON file must contain 'latitude' and 'longitude' columns.")

            except Exception as e:
                st.error(f"Error reading GeoJSON file: {e}")




    # st.write("Filename:", uploaded_file.name)
    # st.write(Path(uploaded_file.name).suffix)

    submitted = st.form_submit_button("Upload")

if not uploaded_files and submitted:
    st.write("Please enter the files desired for processing.")
elif submitted:
    st.write("Files Successfully Uploaded!")



st.divider()

    # conn = st.connection('your_database_name', type='nosql')
    # with conn.session as s:
    #     s.execute('BEGIN;')
    #     for data in bytes_data:
    #         s.execute('INSERT INTO your_db (column1, column2) VALUES (?, ?)', data)
    #     s.execute('COMMIT;')
    # st.write(bytes_data)

st.header("Input Location Coordinates")

m = leafmap.Map(minimap_control=True)
m.add_basemap("OpenTopoMap")

if coordinates is not None and not coordinates.empty:

    m.add_points_from_xy(coordinates, x="longitude", y="latitude", layer_name="Coordinate Points")

m.to_streamlit(height=500)



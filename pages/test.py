import pandas as pd
import geopandas as gpd
import streamlit as st
from pathlib import Path
from sklearn.cluster import KMeans
import leafmap.foliumap as leafmap
from folium.plugins import MarkerCluster
import folium

# Initialize session state
if "all_coordinates" not in st.session_state:
    st.session_state.all_coordinates = None

with st.form("my_form", clear_on_submit=True):
    uploaded_files = st.file_uploader(
        "Select a CSV, GeoJSON, or Shapefile file(s)",
        accept_multiple_files=True,
        type=['geojson', 'csv', 'shp']
    )

    all_coordinates = []  # Temporary storage for the current session

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_extension = Path(uploaded_file.name).suffix.lower()

            # If the file is CSV Type
            if file_extension == '.csv':
                try:
                    df = pd.read_csv(uploaded_file)

                    # Ensure 'latitude' and 'longitude' columns exist
                    if {"latitude", "longitude"}.issubset(df.columns.str.lower()):
                        df.columns = df.columns.str.lower()  # Normalize column names
                        coordinates = df[['latitude', 'longitude']]
                        all_coordinates.append(coordinates)
                        st.success(f"CSV file '{uploaded_file.name}' successfully processed!")
                    else:
                        st.error(f"The CSV file '{uploaded_file.name}' must contain 'latitude' and 'longitude' columns.")

                except Exception as e:
                    st.error(f"Error reading CSV file '{uploaded_file.name}': {e}")

            # If the file is Shapefile Type
            elif file_extension == '.shp':
                try:
                    gdf = gpd.read_file(uploaded_file)

                    # Ensure geometry exists and extract coordinates
                    if gdf.geometry is not None:
                        gdf['longitude'] = gdf.geometry.x
                        gdf['latitude'] = gdf.geometry.y
                        coordinates = gdf[['latitude', 'longitude']]
                        all_coordinates.append(coordinates)
                        st.success(f"Shapefile '{uploaded_file.name}' successfully processed!")
                    else:
                        st.error(f"The Shapefile '{uploaded_file.name}' must contain valid geometry data.")

                except Exception as e:
                    st.error(f"Error reading Shapefile '{uploaded_file.name}': {e}")

            # If the file is GeoJSON Type
            elif file_extension == '.geojson':
                try:
                    gdf = gpd.read_file(uploaded_file)

                    # Ensure geometry exists and extract coordinates
                    if gdf.geometry is not None:
                        gdf['longitude'] = gdf.geometry.x
                        gdf['latitude'] = gdf.geometry.y
                        coordinates = gdf[['latitude', 'longitude']]
                        all_coordinates.append(coordinates)
                        st.success(f"GeoJSON file '{uploaded_file.name}' successfully processed!")
                    else:
                        st.error(f"The GeoJSON file '{uploaded_file.name}' must contain valid geometry data.")

                except Exception as e:
                    st.error(f"Error reading GeoJSON file '{uploaded_file.name}': {e}")

    submitted = st.form_submit_button("Process File(s)")

    if submitted:
        if all_coordinates:
            # Combine all coordinates into a single DataFrame
            st.session_state.all_coordinates = pd.concat(all_coordinates, ignore_index=True)
            st.success("All files successfully uploaded and processed!")
        else:
            st.error("No valid coordinates found in the uploaded files.")

# Clustering and Visualization
if st.session_state.all_coordinates is not None:
    st.write("Combined Coordinates:")
    st.write(st.session_state.all_coordinates.head())

    max_clusters = len(st.session_state.all_coordinates.drop_duplicates())
    num_clusters = st.number_input(
        "Enter the number of clusters for KMeans",
        min_value=1,
        max_value=max_clusters,
        step=1
    )

    if st.button("Perform Clustering"):
        try:
            # Apply KMeans clustering
            kmeans = KMeans(n_clusters=num_clusters, random_state=42)
            st.session_state.all_coordinates['Cluster'] = kmeans.fit_predict(
                st.session_state.all_coordinates[['latitude', 'longitude']]
            )

            # Get cluster centers
            clusters = kmeans.cluster_centers_

            st.write("Cluster Centers:")
            st.write(pd.DataFrame(clusters, columns=['latitude', 'longitude']))

            # Create map and add cluster markers
            m = leafmap.Map(minimap_control=True)
            marker_cluster = MarkerCluster().add_to(m)

            for center in clusters:
                folium.Marker(
                    location=[center[0], center[1]],
                    popup="Cluster Center"
                ).add_to(marker_cluster)

            # Add original points to map
            for _, row in st.session_state.all_coordinates.iterrows():
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=5,
                    color="blue",
                    fill=True,
                    fill_opacity=0.6
                ).add_to(m)

            # Display the map
            m.to_streamlit(height=700)

        except ValueError as e:
            st.error(f"Error during clustering: {e}")

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
if "cluster_map" not in st.session_state:
    st.session_state.cluster_map = None
if "cluster_centers" not in st.session_state:
    st.session_state.cluster_centers = None  # Store cluster centers
if "priority_list" not in st.session_state:
    st.session_state.priority_list = None  # Store priority list (coordinates + clusters)

with st.form("my_form", clear_on_submit=True):
    uploaded_files = st.file_uploader(
        "Select a CSV, GeoJSON, or Shapefile file(s)",
        accept_multiple_files=True,
        type=['geojson', 'csv', 'shp']
    )

    all_coordinates = []  # Temporary storage

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_extension = Path(uploaded_file.name).suffix.lower()

            if file_extension == '.csv':
                try:
                    df = pd.read_csv(uploaded_file)
                    if {"latitude", "longitude"}.issubset(df.columns.str.lower()):
                        df.columns = df.columns.str.lower()
                        coordinates = df[['latitude', 'longitude']]
                        all_coordinates.append(coordinates)
                        st.success(f"CSV '{uploaded_file.name}' processed!")
                    else:
                        st.error(f"CSV '{uploaded_file.name}' must contain 'latitude' and 'longitude'.")
                except Exception as e:
                    st.error(f"Error reading CSV '{uploaded_file.name}': {e}")

            elif file_extension in ['.shp', '.geojson']:
                try:
                    gdf = gpd.read_file(uploaded_file)
                    if gdf.geometry is not None:
                        gdf["latitude"] = gdf.geometry.centroid.y
                        gdf["longitude"] = gdf.geometry.centroid.x
                        coordinates = gdf[['latitude', 'longitude']]
                        all_coordinates.append(coordinates)
                        st.success(f"{file_extension.upper()} '{uploaded_file.name}' processed!")
                    else:
                        st.error(f"{file_extension.upper()} '{uploaded_file.name}' must contain valid geometry data.")
                except Exception as e:
                    st.error(f"Error reading {file_extension.upper()} '{uploaded_file.name}': {e}")

    submitted = st.form_submit_button("Upload and Cluster")

    if submitted:
        if all_coordinates:
            st.session_state.all_coordinates = pd.concat(all_coordinates, ignore_index=True)
            st.success("All files successfully uploaded and processed!")
        else:
            st.error("No valid coordinates found.")

# Clustering
if st.session_state.all_coordinates is not None:
    st.divider()
    st.write("Data Uploaded Successfully!")

    max_clusters = len(st.session_state.all_coordinates.drop_duplicates())
    num_clusters = st.number_input(
        "Enter the number of clusters",
        min_value=1,
        max_value=max_clusters,
        step=1
    )

    if st.button("Perform Clustering"):
        try:
            kmeans = KMeans(n_clusters=num_clusters, random_state=42)
            st.session_state.all_coordinates['Cluster'] = kmeans.fit_predict(
                st.session_state.all_coordinates[['latitude', 'longitude']]
            )

            cluster_centers = kmeans.cluster_centers_
            st.session_state.cluster_centers = pd.DataFrame(cluster_centers, columns=['latitude', 'longitude'])

            # Create Priority List (Combined Coordinates + Cluster Centers)
            priority_list = st.session_state.all_coordinates.copy()
            priority_list['Priority'] = priority_list['Cluster'].rank(method="first")
            st.session_state.priority_list = priority_list

            # Create cluster map
            m = leafmap.Map(minimap_control=True)
            marker_cluster = MarkerCluster().add_to(m)

            for center in cluster_centers:
                folium.Marker(location=[center[0], center[1]], popup="Cluster Center").add_to(marker_cluster)

            for _, row in st.session_state.all_coordinates.iterrows():
                folium.CircleMarker(location=[row['latitude'], row['longitude']], radius=5, color="blue",
                                    fill=True, fill_opacity=0.6).add_to(m)

            st.session_state.cluster_map = m

            st.success("Clustering complete!")

            # Navigation Buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("View Cluster Map"):
                    st.switch_page("pages/clustermap.py")

            with col2:
                if st.button("View Priority List"):
                    st.switch_page("pages/priority_list.py")

        except ValueError as e:
            st.error(f"Error during clustering: {e}")


st.header("Ex")

example_m = leafmap.Map(minimap_control=True)
example_m.add_basemap("OpenTopoMap")

example_m.to_streamlit(height=700)


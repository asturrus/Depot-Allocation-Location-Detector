import pandas as pd
import geopandas as gpd
import streamlit as st
from pathlib import Path
from sklearn.cluster import KMeans
import leafmap.foliumap as leafmap
from folium.plugins import MarkerCluster
import folium
from db_config import collection  # MongoDB Connection

# Set page configuration (must be at the top of the file)
# st.set_page_config(layout="wide")

# Sidebar and Header Content
st.sidebar.title("About")
st.sidebar.info("TBD TO WRITE LATER ON")

st.title("Depot Allocation Location Detector")

st.header("Instructions")
st.markdown("""
1. Input a media file or media files containing 'latitude' and 'longitude' information
2. The Depot Allocation Location Detector will parse the data files
3. Following the parsing, the data will be displayed via various GeoSpatial Maps
4. Option to view parsed data on Cluster map, Heat map, and Priority Chart
""")

# result = collection.delete_many({})
# st.write(f"{result.deleted_count} documents deleted.")


# ---- Initialize session state ----
if "all_coordinates" not in st.session_state:
    st.session_state.all_coordinates = None
if "cluster_map" not in st.session_state:
    st.session_state.cluster_map = None
if "cluster_centers" not in st.session_state:
    st.session_state.cluster_centers = None  # Store cluster centers
if "priority_list" not in st.session_state:
    st.session_state.priority_list = None  # Store priority list (coordinates + clusters)

# ---- Upload Files ----
with st.form("upload_form", clear_on_submit=True):
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

# ---- Clustering ----
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

    # if st.button("Perform Clustering"):
    #     try:
    #         kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    #         st.session_state.all_coordinates['Cluster'] = kmeans.fit_predict(
    #             st.session_state.all_coordinates[['latitude', 'longitude']]
    #         )

    #         cluster_centers = kmeans.cluster_centers_
    #         st.session_state.cluster_centers = pd.DataFrame(cluster_centers, columns=['latitude', 'longitude'])

    #         # Create Priority List (Combined Coordinates + Cluster Centers)
    #         priority_list = st.session_state.all_coordinates.copy()
    #         priority_list['Priority'] = priority_list['Cluster'].rank(method="first")
    #         st.session_state.priority_list = priority_list

    #         # Save clustered data to MongoDB
    #         cluster_data = st.session_state.all_coordinates.to_dict(orient="records")
    #         collection.insert_many(cluster_data)  # Save clustered data
    #         st.success("Clustering complete and data saved to MongoDB!")

    #         # Create cluster map
    #         m = leafmap.Map(minimap_control=True)
    #         marker_cluster = MarkerCluster().add_to(m)

    #         for center in cluster_centers:
    #             folium.Marker(location=[center[0], center[1]], popup="Cluster Center").add_to(marker_cluster)

    #         for _, row in st.session_state.all_coordinates.iterrows():
    #             folium.CircleMarker(location=[row['latitude'], row['longitude']], radius=5, color="blue",
    #                                 fill=True, fill_opacity=0.6).add_to(m)

    #         st.session_state.cluster_map = m

    #     except ValueError as e:
    #         st.error(f"Error during clustering: {e}")

    if st.button("Perform Clustering"):
        try:
            kmeans = KMeans(n_clusters=num_clusters, random_state=42)
            st.session_state.all_coordinates['Cluster'] = kmeans.fit_predict(
                st.session_state.all_coordinates[['latitude', 'longitude']]
            )

            cluster_centers = kmeans.cluster_centers_
            st.session_state.cluster_centers = pd.DataFrame(cluster_centers, columns=['latitude', 'longitude'])

            # ---- Create Priority List ----
            priority_list = st.session_state.all_coordinates.copy()
            priority_list['Priority'] = priority_list['Cluster'].rank(method="first")
            st.session_state.priority_list = priority_list

            # ---- Create cluster map ----
            m = leafmap.Map(minimap_control=True)
            marker_cluster = MarkerCluster().add_to(m)

            for center in cluster_centers:
                folium.Marker(location=[center[0], center[1]], popup="Cluster Center").add_to(marker_cluster)

            for _, row in st.session_state.all_coordinates.iterrows():
                folium.CircleMarker(location=[row['latitude'], row['longitude']], radius=5, color="blue",
                                    fill=True, fill_opacity=0.6).add_to(m)

            st.session_state.cluster_map = m


            # ---- Group by cluster and prepare for MongoDB ----
            grouped_data = []

            for cluster_num in range(num_clusters):
                cluster_coords = st.session_state.all_coordinates[
                    st.session_state.all_coordinates['Cluster'] == cluster_num
                ][['latitude', 'longitude']].to_dict(orient='records')

                cluster_entry = {
                    "cluster": int(cluster_num),
                    "center": {
                        "latitude": float(cluster_centers[cluster_num][0]),
                        "longitude": float(cluster_centers[cluster_num][1])
                    },
                    "cities": cluster_coords
                }

                grouped_data.append(cluster_entry)

            # ---- Save grouped data to MongoDB ----
            collection.insert_many(grouped_data)

            st.success("Clustering complete and saved to database!")

        except ValueError as e:
            st.error(f"Error during clustering: {e}")


# ---- View Saved Data ----
# if st.button("View Saved Clusters"):
#     st.subheader("Saved Clustered Data from Database")
#     saved_data = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB _id
#     if saved_data:
#         df_saved = pd.DataFrame(saved_data)
#         st.dataframe(df_saved)
#     else:
#         st.warning("No clustered data found in database.")

if st.button("View Saved Clusters"):
    st.subheader("📍 Saved Clustered Data from Database")
    saved_data = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB _id

    if saved_data:
        for idx, doc in enumerate(saved_data):
            cluster = doc["center"]
            cities = doc["cities"]

            st.markdown(f"## 🏠 Cluster {idx+1}")
            st.write(f"**Cluster Center:** Latitude: `{cluster['latitude']}`, Longitude: `{cluster['longitude']}`")

            if cities:
                df_cities = pd.DataFrame(cities)
                st.markdown("### 🏙 Cities Assigned to This Cluster:")
                st.dataframe(df_cities)
            else:
                st.warning("No cities assigned to this cluster.")

    else:
        st.warning("No clustered data found in the database.")


# ---- Navigation for Cluster Map & Priority List ----
st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("View Cluster Map"):
        st.switch_page("pages/Clustermap.py")
with col2:
    if st.button("View Priority List"):
        st.switch_page("pages/Priority List.py")


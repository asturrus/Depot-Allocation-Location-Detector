import streamlit as st
import leafmap.foliumap as leafmap
# import pymongo
# from sklearn.cluster import KMeans
# import numpy as np

# @st.cache_resource
# def init_connection():
#     return pymongo.MongoClient(**st.secrets["mongo"])

# client = init_connection()

# @st.cache_data(ttl=600)
# def get_data():
#     db = client.mydb
#     items = db.mycollection.find()
#     items = list(items)  # make hashable for st.cache_data
#     return items

# items = get_data()

# for item in items:
#     st.write(f"{item['name']} has a :{item['pet']}:")










markdown = """
TBD TO WRITE LATER ON
"""

st.set_page_config(layout="wide")

st.sidebar.title("About")
st.sidebar.info(markdown)

st.title("Depot Allocation Location Detector")

st.header("Instructions")

markdown = """
1. Input a media file or media files
2. The Depot Allocation Location Detector will parse the data files
3. Following the parsing the data will be displayed via various GeoSpatial Maps
4. Option to view parsed data on Cluster map, Heat map, and Priority Chart

"""

st.markdown(markdown)

uploaded_files = st.file_uploader(
    "Select a CSV, GeoJson, ShapeFile file(s)", accept_multiple_files=True
)
for uploaded_file in uploaded_files:
    bytes_data = uploaded_file.read()
    st.write("filename:", uploaded_file.name)

    # conn = st.connection('your_database_name', type='sql')
    # with conn.session as s:
    #     s.execute('BEGIN;')
    #     for data in bytes_data:
    #         s.execute('INSERT INTO your_db (column1, column2) VALUES (?, ?)', data)
    #     s.execute('COMMIT;')
    # st.write(bytes_data)

m = leafmap.Map(minimap_control=True)
m.add_basemap("OpenTopoMap")
m.to_streamlit(height=500)



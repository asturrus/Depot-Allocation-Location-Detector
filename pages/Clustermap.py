import streamlit as st

st.set_page_config(layout="wide")

markdown = """
Cluster Map Visualization of Data Coordinates
"""

st.sidebar.title("About")
st.sidebar.info(markdown)

st.title("Marker Cluster")


if "cluster_map" in st.session_state and st.session_state.cluster_map:

    if st.button("Back to Home Page"):
        st.switch_page("Home.py")

    st.session_state.cluster_map.to_streamlit(height=700)

else:
    st.error("No cluster map available. Please upload and process data on the main page first.")
    if st.button("Go to Home page to process data"):
        st.switch_page("Home.py")

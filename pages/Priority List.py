import streamlit as st
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")

markdown = """
Prioritization List of Emergency Operational Centers
"""

st.sidebar.title("About")
st.sidebar.info(markdown)

st.title("Priority List")

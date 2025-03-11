import streamlit as st

st.set_page_config(layout="wide")

markdown = """
Prioritization List of Emergency Operational Centers
"""

st.sidebar.title("About")
st.sidebar.info(markdown)

st.title("Priority List")

if "priority_list" in st.session_state and st.session_state.priority_list is not None:

    if st.button("Back to Home"):
        st.switch_page("Home.py")

    st.write("### Clustered Coordinates with Priority Ranking:")
    st.dataframe(st.session_state.priority_list)

    st.write("### Cluster Centers:")
    st.dataframe(st.session_state.cluster_centers)

else:
    st.error("No priority list available. Please process data on the main page first.")
    if st.button("Go to Home page to process data"):
        st.switch_page("Home.py")

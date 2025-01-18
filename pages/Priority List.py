import streamlit as st
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")

markdown = """
Prioritization List of Emergency Operational Centers
"""

st.sidebar.title("About")
st.sidebar.info(markdown)

st.title("Priority List")

# Sample data
items = [
    {"center": "Task 1", "priority": 3},
    {"center": "Task 2", "priority": 1},
    {"center": "Task 3", "priority": 2}
]

# Sort the items by priority
sorted_items = sorted(items, key=lambda x: x['priority'])

# Prepare the Markdown list
markdown_list = ""
for item in sorted_items:
    markdown_list += f"- {item['center']} (Priority: {item['priority']})\n"

# Display the list in Streamlit
st.markdown(markdown_list)
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import streamlit as st

# MongoDB Atlas Connection
MONGO_URI = "mongodb+srv://adminuser03:76d0oYg6NKOWB28k@depot-location-allocati.ebih9.mongodb.net/?retryWrites=true&w=majority&appName=Depot-Location-Allocation"

# Create MongoDB client with Server API version
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))

# Connect to the database
db = client["Emergency-Centers"]
collection = db["Emergency_Operation_Centers"]

# Test connection (Optional: Display connection status in Admin page)
try:
    client.admin.command("ping")
    st.success("✅ Connected to MongoDB Atlas")
except Exception as e:
    st.error(f"❌ Connection failed: {e}")

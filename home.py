from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
uri = "mongodb+srv://adminuser03:76d0oYg6NKOWB28k@depot-location-allocati.ebih9.mongodb.net/?retryWrites=true&w=majority&appName=Depot-Location-Allocation"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


        # conn = st.connection('your_database_name', type='nosql')
    # with conn.session as s:
    #     s.execute('BEGIN;')
    #     for data in bytes_data:
    #         s.execute('INSERT INTO your_db (column1, column2) VALUES (?, ?)', data)
    #     s.execute('COMMIT;')
    # st.write(bytes_data)
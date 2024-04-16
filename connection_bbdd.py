from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def establecer_conexion():
    uri = "mongodb+srv://mimika:1.Cambiame@databasecluster.ldcnr5i.mongodb.net/?retryWrites=true&w=majority&appName=DatabaseCluster"

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Ping to your deployment. You successfully connected to MongoDB!")
        
        # Obtain a list of available databases
        database_names = client.list_database_names()

        # Print the available databases
        print("Available databases:")
        for db_name in database_names:
            print(f"- {db_name}")
            
    except Exception as e:
        print(e)

# Call the function to establish connection
establecer_conexion()

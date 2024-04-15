
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://mimika:1.Cambiame@databasecluster.ldcnr5i.mongodb.net/?retryWrites=true&w=majority&appName=DatabaseCluster"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    
    # Obtener una lista de las bases de datos disponibles
    database_names = client.list_database_names()

    # Imprimir las bases de datos
    print("Bases de datos disponibles:")
    for db_name in database_names:
        print(f"- {db_name}")
        
except Exception as e:
    print(e)
# Importa las clases necesarias
from flask import Flask
from pymongo import MongoClient

# Crea la aplicación Flask
app = Flask(__name__)

# Configuración de la conexión a MongoDB
MONGO_URI = "mongodb+srv://mimikaAckerman:comoqueso2134@atlascluster.lscuccj.mongodb.net/?retryWrites=true&w=majority&appName=AtlasCluster"

# Conexión a la base de datos
try:
    client = MongoClient(MONGO_URI)
    db = client.UB_cvs  # Cambia 'test' al nombre de tu base de datos
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# Rutas y otras configuraciones de la aplicación Flask...

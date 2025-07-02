from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def establecer_conexion():
    try:
        uri = "mongodb+srv://tekiotechnology:Developer00@cluster0.mczls2q.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        client = MongoClient(uri, server_api=ServerApi('1'))

        # Verifica conexión
        client.admin.command('ping')
        print("✅ Conectado a MongoDB Atlas correctamente.")

        # Devuelve la base de datos
        return client["ub_cv"]  # ← esto es lo más importante

    except Exception as e:
        print(f"❌ Error de conexión a MongoDB: {e}")
        return None

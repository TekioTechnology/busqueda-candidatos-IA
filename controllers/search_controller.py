from flask import Blueprint, request, jsonify
from config.connection_bbdd import establecer_conexion
from utils.embedding import generar_embedding
import numpy as np
from bson import ObjectId

search_bp = Blueprint("search_bp", __name__)

def calcular_similitud(embedding1, embedding2):
    a = np.array(embedding1)
    b = np.array(embedding2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))) * 100  # porcentaje

@search_bp.route("/", methods=["POST"])
def buscar_candidatos():
    try:
        db = establecer_conexion()
        if db is None:
            return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

        datos = request.get_json()
        consulta = datos.get("consulta")
        umbral = float(datos.get("umbral", 5.0))

        if not consulta:
            return jsonify({"error": "Consulta requerida"}), 400

        embedding_consulta = generar_embedding(consulta)
        if embedding_consulta is None:
            return jsonify({"error": "No se pudo generar embedding"}), 500

        resultados = []

        # 🔁 Paso nuevo: buscar IDs de candidatos que ya fueron marcados como fallo para esta consulta
        fallos_previos = db["learn"].find({
            "consulta": consulta,
            "umbral": umbral,
            "estado": "fallo",
            "id_mejor_candidato": {"$ne": None}
        })
        ids_a_ignorar = set(f["id_mejor_candidato"] if isinstance(f["id_mejor_candidato"], ObjectId) else ObjectId(f["id_mejor_candidato"]) for f in fallos_previos)


        # 🔍 Buscar candidatos ignorando los ya fallidos
        for doc in db["db.upload_cv"].find({"embedding": {"$exists": True}}):
            if str(doc["_id"]) in ids_a_ignorar:
                continue  # 👈 Evitar los ya registrados como fallidos

            score = calcular_similitud(embedding_consulta, doc["embedding"])
            if score >= umbral:
                resultados.append({
                    "id": str(doc["_id"]),
                    "nombre_archivo": doc["nombre_archivo"],
                    "score": round(score, 2),
                    "texto_completo": doc["texto_completo"][:500] + "..."
                })

        resultados.sort(key=lambda x: x["score"], reverse=True)
        return jsonify({"resultados": resultados})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

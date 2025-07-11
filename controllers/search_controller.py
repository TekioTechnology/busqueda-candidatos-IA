from flask import Blueprint, request, jsonify
from config.connection_bbdd import establecer_conexion
from utils.embedding import generar_embedding
import numpy as np
from bson import ObjectId
from collections import defaultdict

search_bp = Blueprint("search_bp", __name__)

def calcular_similitud(embedding1, embedding2):
    a = np.array(embedding1)
    b = np.array(embedding2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))) * 100  # en porcentaje

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

        # Historial de feedback para la misma consulta
        historial = db["learn"].find({"consulta": {"$regex": consulta, "$options": "i"}})

        ajustes_por_id = defaultdict(float)

        for h in historial:
            id_candidato = str(h.get("id_mejor_candidato"))
            if not id_candidato:
                continue

            if h.get("estado") == "fallo":
                ajustes_por_id[id_candidato] = max(-0.2, ajustes_por_id[id_candidato] - 0.1)
            elif h.get("estado") == "exito":
                ajustes_por_id[id_candidato] = min(0.3, ajustes_por_id[id_candidato] + 0.1)

        # Evaluar candidatos
        for doc in db["db.upload_cv"].find({"embedding": {"$exists": True}}):
            id_str = str(doc["_id"])
            embedding = doc.get("embedding")
            if not embedding:
                continue  # Por seguridad

            score_base = calcular_similitud(embedding_consulta, embedding)
            ajuste = ajustes_por_id.get(id_str, 0.0)
            score = max(0, min(100, score_base + ajuste * 100))  # Ajustamos score y lo normalizamos

            if score >= umbral:
                resultados.append({
                    "id": id_str,
                    "nombre_archivo": doc["nombre_archivo"],
                    "score": round(score, 2),
                    "score_base": round(score_base, 2),
                    "ajuste_aplicado": round(ajuste * 100, 2),
                    "texto_completo": doc["texto_completo"][:500] + "..."
                })

        resultados.sort(key=lambda x: x["score"], reverse=True)
        return jsonify({
    "resultados": resultados,
    "embedding_consulta": embedding_consulta
})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

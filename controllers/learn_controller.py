# learn_controller.py
from flask import Blueprint, request, jsonify
from config.connection_bbdd import establecer_conexion
from datetime import datetime

learn_bp = Blueprint("learn_bp", __name__)

@learn_bp.route("/registro-busqueda", methods=["POST"])
def registrar_busqueda():
    try:
        db = establecer_conexion()
        if db is None:
            return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

        datos = request.get_json()
        consulta = datos.get("consulta")
        umbral = datos.get("umbral")
        resultados_encontrados = datos.get("resultados_encontrados", 0)
        mejor_score = datos.get("mejor_score")
        id_mejor_candidato = datos.get("id_mejor_candidato")
        estado = datos.get("estado")  # "exito" o "fallo"
        posicion_ranking = datos.get("posicion_ranking", 0)
        modelo_version = datos.get("modelo_version", "desconocida")

        if not consulta or estado not in ["exito", "fallo"]:
            return jsonify({"error": "Datos insuficientes o inválidos"}), 400

        registro = {
            "consulta": consulta,
            "umbral": umbral,
            "resultados_encontrados": resultados_encontrados,
            "mejor_score": mejor_score,
            "id_mejor_candidato": id_mejor_candidato,
            "estado": estado,
            "posicion_ranking": posicion_ranking,
            "modelo_version": modelo_version,
            "timestamp": datetime.utcnow().isoformat()
        }

        db["learn"].insert_one(registro)
        return jsonify({"mensaje": "Registro guardado correctamente"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

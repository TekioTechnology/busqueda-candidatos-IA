from flask import Blueprint, request, jsonify
from config.connection_bbdd import establecer_conexion
from utils.azure_ocr import extraer_texto_ocr
from utils.escaner_extraer import escanear_pdf, dividir_secciones
from utils.spinner import mostrar_spinner
from bson.binary import Binary
from utils.embedding import generar_embedding


cv_bp = Blueprint("cv_bp", __name__)

@cv_bp.route("/", methods=["POST"])
def subir_cv():
    try:
        db = establecer_conexion()
        if db is None:
            return jsonify({"error": "No se pudo establecer conexión con la base de datos"}), 500

        if 'cv' not in request.files:
            return jsonify({"error": "No se envió ningún archivo"}), 400

        archivo_cv = request.files['cv']
        nombre_archivo = archivo_cv.filename

        if not nombre_archivo or not nombre_archivo.lower().endswith('.pdf'):
            return jsonify({"error": "El archivo debe ser PDF"}), 400

        # Iniciar el spinner
        detener_spinner = mostrar_spinner("🔄 Procesando CV con Azure OCR")

        # Leer el contenido del archivo
        contenido_pdf = archivo_cv.read()

        # Detener el spinner
        detener_spinner()

        # Procesar OCR
        texto_pdf = extraer_texto_ocr(contenido_pdf)

        # Extraer campos conocidos del PDF con expresiones regulares
        _, campos_extraidos = escanear_pdf(contenido_pdf)

        # Dividir secciones principales del texto OCR
        secciones = dividir_secciones(texto_pdf)

        embedding = generar_embedding(texto_pdf)

        # Construir el documento completo
        documento = {
            "nombre_archivo": nombre_archivo,
            "contenido": Binary(contenido_pdf),
            "texto_completo": texto_pdf,
            "embedding": embedding,
            "campos": campos_extraidos,
            **secciones  # acerca_de, educacion, experiencia, etc.
        }

        coleccion = db["db.upload_cv"]
        if coleccion.find_one({"nombre_archivo": nombre_archivo}):
            return jsonify({"error": "Este CV ya existe en tu base de datos"}), 400

        coleccion.insert_one(documento)

        return jsonify({
            "mensaje": "CV subido exitosamente",
            "campos_detectados": campos_extraidos
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

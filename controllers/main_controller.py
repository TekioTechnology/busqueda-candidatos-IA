# connection_bbdd.py
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


#----------------funcion de conexion con la base de datos
def establecer_conexion():
    uri = "mongodb+srv://mimika:1.Cambiame@databasecluster.ldcnr5i.mongodb.net/?retryWrites=true&w=majority&appName=DatabaseCluster"
    client = MongoClient(uri, server_api=ServerApi('1'))
    return client['ub_cv']  # Devuelve la base de datos 'ub_cv'



# mi_app/controllers/main_controller.py
from flask import Blueprint, render_template, request, current_app, send_from_directory, Response
import os
import json
import spacy
from unidecode import unidecode
from utils.cv_utils import extraer_texto_pdf, buscar_por_palabra_clave

#importamos la configuracion de la base de datos
# from connection_bbdd import establecer_conexion

main_controller = Blueprint('main_controller', __name__)


#--------------controlador para subir los cvs a la bbdd
@main_controller.route('/subir_cv', methods=['GET', 'POST'])
def subir_cv():
    try:
        client = establecer_conexion()
        if request.method == 'POST':
            if 'cv' in request.files:
                archivo_cv = request.files['cv']
                nombre_archivo = archivo_cv.filename
                
                #verificamos si el archivo ya existe en la base de datos
                if client.db.upload_cv.find_one({"nombre_archivo": nombre_archivo}):
                    return 'Este CV ya existe en tu base de datos.', 400

                contenido_pdf = archivo_cv.read()

                if nombre_archivo.lower().endswith('.pdf'):
                    # Realiza la búsqueda por palabras clave solo si es un archivo PDF
                    texto_pdf = extraer_texto_pdf(contenido_pdf)
                    # Resto del código...

                client.db.upload_cv.insert_one({
                    "nombre_archivo": nombre_archivo,
                    "contenido": contenido_pdf
                })

                return 'CV subido exitosamente', 200
    except Exception as e:
        return str(e), 500

    return render_template('formulario.html')
    
# import fitz
# def extraer_texto_pdf(contenido_pdf):
#     texto=""
#     try:
#         #abrimos el documento pdf
#         documento=fitz.open(stream=contenido_pdf,filetype="pdf")
#         #extrae el texto de cada pagina
#         for pagina in documento:
#             texto +=pagina.get_text()
#     except Exception as e:
#         print("error al extraer el texto pdf")
#         return texto

#funcion de buscar pdf
@main_controller.route('/buscar', methods=['GET'])
def mostrar_buscador():
    return render_template('buscador.html')

# @main_controller.route('/buscar', methods=['POST'])
# def buscar():
#     palabra_clave = request.form.get('palabra_clave', '')
#     palabra_clave_normalizada = unidecode(palabra_clave).lower()
#     resultados = []

#     db = establecer_conexion()
#     for pdf in db.upload_cv.find():
#         contenido_pdf = pdf["contenido"]
#         nombre_archivo = pdf["nombre_archivo"]

#         # Extraer texto del PDF
#         texto_pdf = extraer_texto_pdf(contenido_pdf)

#         # Buscar la palabra clave en el texto extraído
#         if palabra_clave_normalizada in unidecode(texto_pdf).lower():
#             resultados.append(nombre_archivo)

#     print(f'palabra clave buscada: {palabra_clave}')
#     print(f'Resultados encontrados: {resultados}')

#     return render_template('buscador.html', palabra_clave=palabra_clave, resultados=resultados)
# @main_controller.route('/descargar/<nombre_archivo>')
# def descargar(nombre_archivo):
#     pdf = client.ub_cv.upload_cv.find_one({"nombre_archivo": nombre_archivo})
#     if pdf:
#         contenido_pdf = pdf["contenido"]
#         return Response(contenido_pdf, mimetype='application/pdf', headers={'Content-Disposition': f'attachment; filename="{nombre_archivo}"'})
#     else:
#         return "El archivo no fue encontrado en la base de datos"

# @main_controller.route('/visualizar_pdf/<nombre_archivo>')
# def visualizar_pdf(nombre_archivo):
#     pdf = client.ub_cv.upload_cv.find_one({"nombre_archivo": nombre_archivo})
#     if pdf:
#         contenido_pdf = pdf["contenido"]
#         return Response(contenido_pdf, mimetype='application/pdf')
#     else:
#         return "El archivo no fue encontrado en la base de datos."




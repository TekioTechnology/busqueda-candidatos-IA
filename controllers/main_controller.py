# connection_bbdd.py
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


#----------------funcion de conexion con la base de datos
def establecer_conexion():
    uri = "mongodb+srv://mimika:1.Cambiame@databasecluster.ldcnr5i.mongodb.net/?retryWrites=true&w=majority&appName=DatabaseCluster"
    client = MongoClient(uri, server_api=ServerApi('1'))
    return client['ub_cv']  # Devuelve la base de datos 'ub_cv'



# mi_app/controllers/main_controller.py
from flask import Blueprint, render_template, request,Response,jsonify,send_file

import os
import json

import base64
from unidecode import unidecode
from utils.cv_utils import extraer_texto_pdf, buscar_por_palabra_clave

from io import BytesIO
from PyPDF2 import PdfReader

#importamos la configuracion de la base de datos
# from connection_bbdd import establecer_conexion

main_controller = Blueprint('main_controller', __name__)



#funcion de buscar pdf
@main_controller.route('/buscar', methods=['GET'])
def mostrar_buscador():
    return render_template('buscador.html')
#no se encuentra la pagina
@main_controller.app_errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

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

#funcion para verificar si el archivo esta en la base de datos
def verificar_archivo(nombre_archivo):
    try:
        client = establecer_conexion()
        if client.db.upload_cv.find_one({"nombre_archivo": nombre_archivo}):
            return "El archivo existe en la base de datos."
        else:
            return "El archivo no existe en la base de datos."
    except Exception as e:
        return str(e)
#aqui lo empleamos como ruta para visualizarlo por url 
@main_controller.route('/verificar_archivo/<nombre_archivo>', methods=['GET'])
def verificar_archivo_route(nombre_archivo):
    mensaje = verificar_archivo(nombre_archivo)
    return jsonify({"mensaje": mensaje})

#funcion para visualizar todos los archivos de la base de datos
@main_controller.route('/ver_todos_los_archivos', methods=['GET'])
def ver_todos_los_archivos():
    try:
        client = establecer_conexion()
        archivos = client.db.upload_cv.find({}, {"_id": 0, "nombre_archivo": 1, "contenido": 1})  # Obtener nombres de archivo y contenido
        datos_archivos = [{"nombre_archivo": archivo["nombre_archivo"], "contenido": archivo["contenido"]} for archivo in archivos]
        return render_template('ver_todos_los_archivos.html', datos_archivos=datos_archivos)
    except Exception as e:
        return str(e), 500




#---FUNCION PARA DESCARGAR ARCHIVOS
@main_controller.route('/descargar_archivo/<nombre_archivo>', methods=['GET'])
def descargar_archivo(nombre_archivo):
    try:
        client = establecer_conexion()
        archivo = client.db.upload_cv.find_one({"nombre_archivo": nombre_archivo})
        if archivo:
            contenido_pdf = archivo["contenido"]
            return send_file(BytesIO(contenido_pdf), mimetype='application/pdf', as_attachment=True, download_name=nombre_archivo)
        else:
            return "El archivo no fue encontrado en la base de datos."
    except Exception as e:
        return str(e), 500



#-funcion para ver todos los archivos de la base de datos 
@main_controller.route('/ver_archivo/<nombre_archivo>', methods=['GET'])
def ver_archivo(nombre_archivo):
    try:
        client = establecer_conexion()
        archivo = client.db.upload_cv.find_one({"nombre_archivo": nombre_archivo})
        if archivo:
            contenido_pdf = archivo["contenido"]
            return Response(contenido_pdf, mimetype='application/pdf')
        else:
            return "El archivo no fue encontrado en la base de datos."
    except Exception as e:
        return str(e), 500


#funcion para editar los nombres de los pdfs
@main_controller.route('/editar_nombre_archivo/<nombre_archivo>', methods=['POST'])
def editar_nombre_archivo(nombre_archivo):
    try:
        nuevo_nombre = request.form.get('nuevo_nombre')
        client = establecer_conexion()
        resultado = client.db.upload_cv.update_one({"nombre_archivo": nombre_archivo}, {"$set": {"nombre_archivo": nuevo_nombre}})
        mensaje = f"El nombre del archivo '{nombre_archivo}' se ha actualizado correctamente a '{nuevo_nombre}'." if resultado.modified_count > 0 else "No se encontró el archivo especificado para editar."
        return render_template('mensaje_edicion.html', mensaje=mensaje)
    except Exception as e:
        return str(e), 500
    

#funcion de busqueda
@main_controller.route('/buscar_pdf', methods=['POST'])
def buscar_pdf():
    try:
        palabra_clave = request.form.get('palabra_clave')
        resultados = []

        client = establecer_conexion()
        for archivo in client.db.upload_cv.find():
            contenido_pdf_codificado = archivo["contenido"]
            contenido_pdf_decodificado = base64.b64decode(contenido_pdf_codificado)
            
            # Utiliza PyPDF2 para extraer el texto del PDF
            with BytesIO(contenido_pdf_decodificado) as pdf_buffer:
                pdf_reader = PdfReader(pdf_buffer)
                texto_pdf = ""
                for page in pdf_reader.pages:
                    texto_pdf += page.extract_text()

            # Busca la palabra clave en el texto extraído
            if palabra_clave.lower() in texto_pdf.lower():
                resultados.append(archivo["nombre_archivo"])

        return jsonify(resultados=resultados)
    except Exception as e:
        return str(e), 500
    
@main_controller.route('/buscar_por_palabras_clave', methods=['GET'])
def mostrar_formulario_busqueda():
    return render_template('formulario_busqueda.html')

                






    
# @main_controller.route('/visualizar_pdf/<nombre_archivo>')
# def visualizar_pdf(nombre_archivo):
#     client=establecer_conexion()
#     pdf = client.ub_cv.upload_cv.find_one({"nombre_archivo": nombre_archivo})
#     if pdf:
#         contenido_pdf = pdf["contenido"]
#         # Decodificar el contenido binario a bytes
#         contenido_bytes = contenido_pdf.decode('utf-8')
        
#         # Crear un objeto BytesIO a partir de los bytes
#         pdf_bytes_io = BytesIO(contenido_bytes)
        
#         # Enviar el objeto BytesIO como archivo adjunto
#         return send_file(pdf_bytes_io, mimetype='application/pdf', download_name=nombre_archivo)
#     else:
#         return "El archivo no fue encontrado en la base de datos."
    



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




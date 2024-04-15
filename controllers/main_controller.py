# mi_app/controllers/main_controller.py
from flask import Blueprint, render_template, request, current_app, send_from_directory
import os
import json
import spacy
from unidecode import unidecode
from utils.cv_utils import extraer_texto_pdf, buscar_por_palabra_clave








main_controller = Blueprint('main_controller', __name__)


@main_controller.route('/subir_cv', methods=['GET', 'POST'])
def subir_cv():
    if request.method == 'POST':
        try:
            if 'cv' in request.files:
                archivo_cv = request.files['cv']
                
                # obtenemos el nombre original del archivo
                nombre_archivo = archivo_cv.filename
                
                # verificamos si el archivo ya existe
                if client.UB_cvs.pdfs.find_one({"nombre_archivo": nombre_archivo}):
                    return 'Este CV ya existe en tu base de datos.'

                # convertimos el archivo a bytes
                contenido_pdf = archivo_cv.read()
                
                # Guarda el archivo en la base de datos
                client.UB_cvs.pdfs.insert_one({
                    "nombre_archivo": nombre_archivo,
                    "contenido": contenido_pdf
                })

                print(f'Se ha subido el CV: {nombre_archivo}')

                # Realiza la búsqueda por palabras clave solo si es un archivo PDF
                if nombre_archivo.lower().endswith('.pdf'):
                    texto_pdf = extraer_texto_pdf(contenido_pdf)
                    # Resto del código...
                    print(f'El CV es un archivo PDF: {nombre_archivo}')
                else:
                    print(f'El CV no es un archivo PDF: {nombre_archivo}')

                return 'CV subido exitosamente'
        except Exception as e:
            return str(e), 500

    # Si la solicitud es GET, renderiza el formulario
    return render_template('formulario.html')

@main_controller.route('/buscar', methods=['GET'])
def mostrar_buscador():
    return render_template('buscador.html')

@main_controller.route('/buscar', methods=['POST'])
def buscar():
    palabra_clave = request.form.get('palabra_clave', '')
    palabra_clave_normalizada = unidecode(palabra_clave).lower()

    resultados = []

    for pdf in client.UB_cvs.pdfs.find():
        contenido_pdf = pdf["contenido"]
        nombre_archivo = pdf["nombre_archivo"]
        
        if buscar_por_palabra_clave(contenido_pdf, palabra_clave_normalizada):
            resultados.append(nombre_archivo)
                
            print(f'palabra clave buscada: {palabra_clave}')
            print(f'Resultados encontrados: {resultados}')

            # Guardamos la palabra clave en un archivo JSON
            ruta_json = os.path.join(current_app.root_path, 'mineri_text', 'data.json')
            print(f'Ruta del archivo JSON: {ruta_json}')

            # Estructura del JSON inicial
            estructura_json = {"words": []}
            if os.path.exists(ruta_json):
                with open(ruta_json, 'r') as archivo_json:
                    estructura_json = json.load(archivo_json)

            # Palabra clave solo si no existe en el archivo JSON
            if palabra_clave_normalizada not in estructura_json["words"]:
                estructura_json["words"].append(palabra_clave_normalizada)

                with open(ruta_json, 'w') as archivo_json:
                    json.dump(estructura_json, archivo_json, indent=2)

                print(f'Palabra clave guardada: {palabra_clave_normalizada}')

    return render_template('buscador.html', palabra_clave=palabra_clave, resultados=resultados)

@main_controller.route('/descargar/<nombre_archivo>')
def descargar(nombre_archivo):
    return send_from_directory(os.path.join(current_app.root_path, 'uploads'), nombre_archivo, as_attachment=True)

@main_controller.route('/visualizar_pdf/<nombre_archivo>')
def visualizar_pdf(nombre_archivo):
    return send_from_directory(os.path.join(current_app.root_path, 'uploads'), nombre_archivo, as_attachment=False)

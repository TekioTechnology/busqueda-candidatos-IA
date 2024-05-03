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

from utils.escaner_extraer import escanear_pdf
from io import BytesIO


main_controller = Blueprint('main_controller', __name__)




#--------------EDITAR CODIGO 
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
                    texto_pdf, campos = escanear_pdf(contenido_pdf)

                    # Resto del código...

                client.db.upload_cv.insert_one({
                    "nombre_archivo": nombre_archivo,
                        "contenido": contenido_pdf,
                        "texto_completo": texto_pdf,
                        "campos": campos
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
@main_controller.route('/buscar', methods=['GET', 'POST'])
def buscar():
    if request.method == 'POST':
        try:
            palabras_clave = request.form.get('palabras_clave', '').split()
            client = establecer_conexion()

            resultados = []

            # Buscamos en la base de datos
            for documento in client.db.upload_cv.find():
                texto_completo = documento.get('texto_completo', '')
                campos = documento.get('campos', {})

                # Verificamos si alguna palabra clave está en el texto completo
                for palabra in palabras_clave:
                    if palabra.lower() in texto_completo.lower():
                        resultados.append(documento)
                        break

                # Verificamos si alguna palabra clave está en los campos
                for campo_valor in campos.values():
                    if isinstance(campo_valor, str):
                        for palabra in palabras_clave:
                            if palabra.lower() in campo_valor.lower():
                                resultados.append(documento)
                                break

            return render_template('prom_busqueda.html', resultados=resultados)

        except Exception as e:
            return str(e), 500
    else:
        # Si la solicitud es GET, mostramos el formulario de búsqueda
        return render_template('prom_busqueda.html')
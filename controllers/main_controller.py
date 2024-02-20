# mi_app/controllers/main_controller.py
from flask import Blueprint, render_template, request, current_app,send_from_directory
import os


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
                nombre_archivo=archivo_cv.filename
                
                #verificamos si el archivo ya existe
                ruta_archivo_existente=os.path.join(current_app.root_path,'uploads',nombre_archivo)
                if os.path.exists(ruta_archivo_existente):
                    return 'Este CV ya existe en tu base de datos.'

                # Guarda el archivo en el directorio uploads
                ruta_uploads = os.path.join(current_app.root_path, 'uploads')
                archivo_cv.save(os.path.join(ruta_uploads, nombre_archivo))

                print(f'Se ha subido el CV: {nombre_archivo}')

                # Realiza la búsqueda por palabras clave solo si es un archivo PDF
                if extension.lower() == '.pdf':
                    ruta_pdf = os.path.join(ruta_uploads, nombre_archivo)
                    texto_pdf = extraer_texto_pdf(ruta_pdf)
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

    for nombre_archivo in os.listdir(os.path.join(current_app.root_path, 'uploads')):
        if nombre_archivo.lower().endswith('.pdf'):
            ruta_pdf = os.path.join(current_app.root_path, 'uploads', nombre_archivo)
            if buscar_por_palabra_clave(ruta_pdf, palabra_clave_normalizada):
                resultados.append(nombre_archivo)

    return render_template('buscador.html', palabra_clave=palabra_clave, resultados=resultados)

@main_controller.route('/descargar/<nombre_archivo>')
def descargar(nombre_archivo):
    return send_from_directory(os.path.join(current_app.root_path, 'uploads'), nombre_archivo, as_attachment=True)


@main_controller.route('/visualizar_pdf/<nombre_archivo>')
def visualizar_pdf(nombre_archivo):
    return send_from_directory(os.path.join(current_app.root_path, 'uploads'), nombre_archivo, as_attachment=False)
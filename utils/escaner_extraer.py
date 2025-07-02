import re
from PyPDF2 import PdfReader
from io import BytesIO



def dividir_secciones(texto):
    secciones = {
        "acerca_de": "",
        "educacion": "",
        "experiencia": "",
        "habilidades": "",
        "idiomas": "",
        "otros": ""
    }

    patrones = {
        "acerca_de": r"(ACERCA DE M[IÍ]|PERFIL|SOBRE M[IÍ])",
        "educacion": r"(EDUCACI[ÓO]N|FORMACI[ÓO]N)",
        "experiencia": r"(EXPERIENCIA|TRAYECTORIA|CARRERA PROFESIONAL)",
        "habilidades": r"(HABILIDADES|COMPETENCIAS|CONOCIMIENTOS)",
        "idiomas": r"(IDIOMAS)",
    }

    texto = texto.upper()
    secciones_detectadas = list(patrones.keys())

    indices = {}
    for clave, patron in patrones.items():
        match = re.search(patron, texto)
        if match:
            indices[clave] = match.start()

    # Ordenamos las secciones encontradas
    secciones_ordenadas = sorted(indices.items(), key=lambda x: x[1])

    for i, (clave, inicio) in enumerate(secciones_ordenadas):
        fin = secciones_ordenadas[i+1][1] if i+1 < len(secciones_ordenadas) else len(texto)
        secciones[clave] = texto[inicio:fin].strip()

    # Resto del texto se guarda como "otros"
    texto_seccionado = "".join(secciones.values())
    resto = texto.replace(texto_seccionado, "")
    secciones["otros"] = resto.strip()

    return secciones




def extraer_texto_pdf(contenido_pdf):
    # Creamos un objeto PdfReader
    pdf = PdfReader(BytesIO(contenido_pdf))
    
    texto = ""
    
    # Iteramos sobre todas las páginas y extraemos el texto
    for page in pdf.pages:
        texto += page.extract_text()
    
    return texto 

# Funciones para extraer campos específicos del texto PDF
def extraer_correo(texto_pdf):
    # Implementa la lógica para extraer el correo electrónico del texto PDF
    correo = re.search(r'[\w\.-]+@[\w\.-]+', texto_pdf)
    if correo:
        return correo.group(0)
    else:
        return None

def extraer_telefono(texto_pdf):
    # Implementa la lógica para extraer el número de teléfono del texto PDF
    telefono = re.search(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', texto_pdf)
    if telefono:
        return telefono.group(0)
    else:
        return None

def extraer_nombre(texto_pdf):
    # Implementa la lógica para extraer el nombre del texto PDF
    nombre = re.search(r'(?i)nombre[:\s]([^\n]+)', texto_pdf)
    if nombre:
        return nombre.group(1)
    else:
        return None

def extraer_formacion(texto_pdf):
    # Implementa la lógica para extraer la formación del texto PDF
    formacion = re.search(r'(?i)formación[:\s]([^\n]+)', texto_pdf)
    if formacion:
        return formacion.group(1)
    else:
        return None

def extraer_experiencia(texto_pdf):
    # Implementa la lógica para extraer la experiencia del texto PDF
    experiencia = re.search(r'(?i)experiencia[:\s]([^\n]+)', texto_pdf)
    if experiencia:
        return experiencia.group(1)
    else:
        return None

def escanear_pdf(contenido_pdf):
    texto_pdf = extraer_texto_pdf(contenido_pdf)
    
    # Escaneamos los campos específicos del PDF
    campos = {
        "correo": extraer_correo(texto_pdf),
        "telefono": extraer_telefono(texto_pdf),
        "nombre": extraer_nombre(texto_pdf),
        "formacion": extraer_formacion(texto_pdf),
        "experiencia": extraer_experiencia(texto_pdf),
    }
    
    return texto_pdf, campos

def extraer_campos_desde_texto(texto_pdf):
    return {
        "correo": extraer_correo(texto_pdf),
        "telefono": extraer_telefono(texto_pdf),
        "nombre": extraer_nombre(texto_pdf),
        "formacion": extraer_formacion(texto_pdf),
        "experiencia": extraer_experiencia(texto_pdf),
    }

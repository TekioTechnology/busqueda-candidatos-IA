# utils/cv_utils.py
import os
import fitz  # PyMuPDF
from unidecode import unidecode


def extraer_texto_pdf(ruta_pdf):
    texto = ""
    try:
        with fitz.open(ruta_pdf) as pdf_doc:
            for pagina_num in range(pdf_doc.page_count):
                pagina = pdf_doc[pagina_num]
                texto += pagina.get_text()
    except Exception as e:
        print(f"Error al extraer texto del PDF: {e}")

    return texto

def buscar_por_palabra_clave(ruta_pdf, palabra_clave):
   texto_pdf=extraer_texto_pdf(ruta_pdf)
   texto_normalizado=unidecode(texto_pdf).lower()
   palabra_clave_normalizada=unidecode(palabra_clave).lower()
   
   return palabra_clave_normalizada in texto_normalizado
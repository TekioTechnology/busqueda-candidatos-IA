import os
import tempfile
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

load_dotenv()

def extraer_texto_ocr(pdf_bytes: bytes) -> str:
    # Obtener credenciales en tiempo de ejecución
    endpoint = os.getenv("AZURE_DOC_INTEL_ENDPOINT")
    key = os.getenv("AZURE_DOC_INTEL_KEY")

    if not endpoint or not key:
        raise ValueError("Faltan variables de entorno: AZURE_DOC_INTEL_ENDPOINT o AZURE_DOC_INTEL_KEY")

    client = DocumentIntelligenceClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
        tmp_file.write(pdf_bytes)
        tmp_file_path = tmp_file.name

    with open(tmp_file_path, "rb") as f:
        poller = client.begin_analyze_document(
            model_id="prebuilt-read",
            body=f,
            content_type="application/pdf"
        )
        result = poller.result()

    texto = result.content if result else ""
    return texto

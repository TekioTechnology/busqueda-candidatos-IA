from sentence_transformers import SentenceTransformer

# Puedes cambiar este modelo por otro si deseas (más rápido o preciso)
model = SentenceTransformer("all-MiniLM-L6-v2")

def generar_embedding(texto):
    try:
        embedding = model.encode(texto, show_progress_bar=False).tolist()
        return embedding
    except Exception as e:
        print(f"Error al generar embedding con Hugging Face: {e}")
        return None

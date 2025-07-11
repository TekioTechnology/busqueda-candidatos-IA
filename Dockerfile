# Usa una imagen oficial de Python como base
FROM python:3.12-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . .

# Instala las dependencias
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# Expone el puerto que usa Gunicorn
EXPOSE 8000

# Comando para ejecutar Gunicorn (ajústalo si tu módulo no se llama app:app)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "300", "--keep-alive", "2", "--max-requests", "1000", "--preload", "app:app"]

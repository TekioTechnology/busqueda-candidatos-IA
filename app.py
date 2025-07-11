import os
import sys
import logging
import time
from flask import Flask
from routes import register_routes
from werkzeug.exceptions import RequestEntityTooLarge
from dotenv import load_dotenv
from functools import lru_cache
import threading
from flask_cors import CORS


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Variables globales para el estado de la aplicación
_app_ready = False
_models_loaded = False
_initialization_lock = threading.Lock()

@lru_cache(maxsize=1)
def initialize_models():
    """Inicializa y cachea los modelos de ML una sola vez"""
    global _models_loaded
    
    if _models_loaded:
        return True
        
    try:
        logger.info("Iniciando carga de modelos...")
        start_time = time.time()
        
        # Aquí va tu código de inicialización de modelos
        # Por ejemplo, cargar modelos de Azure, transformers, etc.
        
        # Simular carga de modelos (reemplaza con tu código real)
        time.sleep(2)  # Simular tiempo de carga
        
        load_time = time.time() - start_time
        logger.info(f"Modelos cargados exitosamente en {load_time:.2f} segundos")
        
        _models_loaded = True
        return True
        
    except Exception as e:
        logger.error(f"Error cargando modelos: {str(e)}")
        return False

def create_app():
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__)
    CORS(app)

    
    # Configuración de la aplicación
    app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # Configurar logging de Flask
    if not app.debug:
        app.logger.setLevel(logging.INFO)
    
    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(e):
        return {"error": "El archivo es demasiado grande. Límite: 20 MB"}, 413
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        logger.error(f"Error interno del servidor: {str(e)}")
        return {"error": "Error interno del servidor"}, 500
    
    @app.errorhandler(404)
    def handle_not_found(e):
        return {"error": "Endpoint no encontrado"}, 404
    
    @app.route("/", methods=["GET"])
    def welcome():
        return {
            "mensaje": "Bienvenido a la API de búsqueda de candidatos",
            "status": "active",
            "timestamp": time.time(),
            "models_loaded": _models_loaded
        }
    
    @app.route("/health", methods=["GET"])
    def health_check():
        """Endpoint de salud para monitoring"""
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "models_loaded": _models_loaded,
            "app_ready": _app_ready
        }
    
    @app.route("/warm-up", methods=["GET"])
    def warm_up():
        """Endpoint para precalentar la aplicación y cargar modelos"""
        global _app_ready
        
        try:
            with _initialization_lock:
                if not _models_loaded:
                    logger.info("Iniciando warm-up de la aplicación...")
                    success = initialize_models()
                    if success:
                        _app_ready = True
                        logger.info("Warm-up completado exitosamente")
                        return {
                            "status": "warmed_up",
                            "models_loaded": True,
                            "timestamp": time.time()
                        }
                    else:
                        return {
                            "status": "error",
                            "message": "Error cargando modelos",
                            "timestamp": time.time()
                        }, 500
                else:
                    return {
                        "status": "already_warmed",
                        "models_loaded": True,
                        "timestamp": time.time()
                    }
                    
        except Exception as e:
            logger.error(f"Error en warm-up: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": time.time()
            }, 500
    
    @app.before_request
    def ensure_models_loaded():
        """Middleware para asegurar que los modelos están cargados"""
        from flask import request
        
        # Saltear para endpoints que no requieren modelos
        if request.endpoint in ['welcome', 'health_check', 'warm_up']:
            return
        
        if not _models_loaded:
            logger.info("Modelos no cargados, iniciando carga automática...")
            initialize_models()
    
    # Registrar las rutas
    register_routes(app)
    
    return app

# Crear la aplicación
app = create_app()

# Inicialización asíncrona en background
def background_initialization():
    """Inicialización en background para reducir cold start"""
    try:
        logger.info("Iniciando inicialización en background...")
        initialize_models()
        global _app_ready
        _app_ready = True
        logger.info("Inicialización en background completada")
    except Exception as e:
        logger.error(f"Error en inicialización background: {str(e)}")

# Iniciar inicialización en background
if not _models_loaded:
    background_thread = threading.Thread(target=background_initialization)
    background_thread.daemon = True
    background_thread.start()

if __name__ == "__main__":
    # CORREGIDO: Cambiar puerto de 3000 a 8000 para Azure App Service
    port = int(os.environ.get("PORT", 8000))
    debug_mode = os.environ.get("FLASK_ENV", "production") != "production"
    
    logger.info(f"Iniciando aplicación en puerto {port}")
    logger.info(f"Modo debug: {debug_mode}")
    
    app.run(host="0.0.0.0", port=port, debug=debug_mode, threaded=True)
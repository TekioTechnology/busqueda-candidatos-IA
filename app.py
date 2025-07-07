import os
from flask import Flask
from routes import register_routes
from werkzeug.exceptions import RequestEntityTooLarge
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB

    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(e):
        return {"error": "El archivo es demasiado grande. Límite: 20 MB"}, 413

    @app.route("/", methods=["GET"])
    def welcome():
        return {"mensaje": "Bienvenido a la API de búsqueda de candidatos"}

    register_routes(app)
    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 3000))  # <-- usa el puerto proporcionado por Azure
    app.run(host="0.0.0.0", port=port, debug=True)

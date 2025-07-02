from flask import Flask
from controllers.cv_controller import cv_bp
from controllers.search_controller import search_bp
from controllers.learn_controller import learn_bp


def register_routes(app: Flask):
    app.register_blueprint(cv_bp, url_prefix="/api/cv")
    app.register_blueprint(search_bp, url_prefix="/api/buscar")
    app.register_blueprint(learn_bp, url_prefix="/api")




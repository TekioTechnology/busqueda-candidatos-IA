from flask import Flask
from controllers.main_controller import main_controller
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.register_blueprint(main_controller)

@app.route('/')
def index():
    return '¡Hola, mundo!'

if __name__ == '__main__':
    app.run(debug=True,port=9000)

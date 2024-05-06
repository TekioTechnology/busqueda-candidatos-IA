from flask import Flask,render_template
from controllers.main_controller import main_controller
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'Ub_2024'  # Reemplaza esto con tu propia clave secreta
CORS(app)
app.register_blueprint(main_controller)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True,port=9000)

from flask import Flask,render_template
from controllers.main_controller import main_controller
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.register_blueprint(main_controller)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True,port=9000)

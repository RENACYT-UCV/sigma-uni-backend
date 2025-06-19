from flask import Flask, render_template, Response
from components.numeros import NumerosDetector


app = Flask(__name__)
detector_numeros = NumerosDetector()

@app.route('/')
def index():
    return render_template('index.html')  # o la ruta que uses

@app.route('/numeros')
def numeros():
    return Response(detector_numeros.generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)

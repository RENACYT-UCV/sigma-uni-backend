from flask import Flask, render_template, Response
from components.letras import LetrasDetector
from components.numeros import NumerosDetector

app = Flask(__name__)

detector_letras = LetrasDetector()
detector_numeros = NumerosDetector()

# Página principal con texto o enlaces a letras y números
@app.route('/')
def index():
    return render_template('index.html')

# Página que muestra solo la detección de letras
@app.route('/letras')
def letras():
    return render_template('letras.html')  # Tiene el stream de letras

# Página que muestra solo la detección de números
@app.route('/numeros')
def numeros():
    return render_template('numeros.html')  # Tiene el stream de números

# Stream de video (letras)
@app.route('/stream/letras')
def stream_letras():
    return Response(detector_letras.generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Stream de video (números)
@app.route('/stream/numeros')
def stream_numeros():
    return Response(detector_numeros.generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)

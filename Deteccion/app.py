from flask import Flask, render_template, Response
from components.letras import LetrasDetector
from components.numeros import NumerosDetector
from components.frases import FrasesDetector
from components.alimentos import AlimentosDetector

app = Flask(__name__)

# Instanciar los detectores
detector_letras = LetrasDetector()
detector_numeros = NumerosDetector()
frases_detector = FrasesDetector()
alimentos_detector = AlimentosDetector()

# Página principal
@app.route('/')
def index():
    return render_template('index.html')


# Páginas HTML de letras y números
@app.route('/letras')
def letras():
    return render_template('letras.html')

@app.route('/numeros')
def numeros():
    return render_template('numeros.html')


# Streams para cada categoría

@app.route('/stream/letras')
def stream_letras():
    return Response(detector_letras.generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stream/numeros')
def stream_numeros():
    return Response(detector_numeros.generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/frases')
def frases_feed():
    return Response(frases_detector.generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/alimentos')
def alimentos_feed():
    return Response(alimentos_detector.generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# Compatibilidad con ruta /video_feed (opcional, para pruebas rápidas)
@app.route('/video_feed')
def video_feed():
    return Response(detector_letras.generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)

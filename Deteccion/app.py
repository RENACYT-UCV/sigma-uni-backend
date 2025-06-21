from flask import Flask, render_template, Response
from components.letras import LetrasDetector
from components.frases import FrasesDetector
from components.alimentos import AlimentosDetector
from components.numeros import NumerosDetector

app = Flask(__name__)

# Instanciar los detectores
letras_detector = LetrasDetector()
frases_detector = FrasesDetector()
alimentos_detector = AlimentosDetector()
numeros_detector = NumerosDetector()

# Rutas principales


@app.route('/')
def index():
    return render_template('index.html')

# Rutas de video para cada categoría


@app.route('/letras')
def letras_feed():
    return Response(letras_detector.generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/frases')
def frases_feed():
    return Response(frases_detector.generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/alimentos')
def alimentos_feed():
    return Response(alimentos_detector.generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/numeros')
def numeros_feed():
    return Response(numeros_detector.generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Mantener compatibilidad con video_feed original


@app.route('/video_feed')
def video_feed():
    return Response(letras_detector.generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True, threaded=True)

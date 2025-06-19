from flask import Flask, render_template, Response

from detection_model.detection import Dectector
from detectors.numbers import NumberDection

app = Flask(__name__)

detector = Dectector()

number_detector = NumberDection(detector)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(number_detector.generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True, threaded=True)

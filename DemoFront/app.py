from flask import Flask, request, redirect, url_for, render_template
from gradio_client import Client
import logging
import os
import shutil
from werkzeug.utils import secure_filename

logging.basicConfig(level=logging.DEBUG)
client = Client("http://127.0.0.1:7860/")
app = Flask(__name__)
 
UPLOAD_FOLDER = 'static/uploads/'
 
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_image():

    file = request.files['file']
    audio = request.files['audio']
    still =  bool(request.form.getlist('still'))
    enhancer = bool(request.form.getlist('enhancer'))

    if file and audio:
        # Save File
        file_name = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        file.save(file_path)
        # Save Audio
        audio_name = secure_filename(audio.filename)
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_name)
        audio.save(audio_path)

        result = client.predict(
            file_path,	# str (filepath or URL to image) in 'Source image' Image component
            audio_path,	# str (filepath or URL to file) in 'Input audio' Audio component
            "crop",	# str  in 'preprocess' Radio component
            still,	# bool  in 'w/ Still Mode (fewer hand motion, works with preprocess `full`)' Checkbox component
            enhancer,	# bool  in 'w/ GFPGAN as Face enhancer' Checkbox component
            api_name="/predict")
        result_path = os.path.split(result)
        video_name = result_path[1].strip()
        shutil.copyfile(result, os.path.join("static","uploads",video_name))

        return render_template('index.html', filename=file_name, videoname=video_name)
 
@app.route('/display/<filename>')
def display_file(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

if __name__ == "__main__":
    app.static_folder = 'static'
    app.run()
import os
import datetime
import urllib.request
from flask import Flask, flash, request, redirect, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from upload_video import get_authenticated_service, initialize_upload

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGHT'] = 16*1024*1024

ALLOWED_EXTENSIONS = set(['mp4', 'flv'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            resp = jsonify({'message' : 'No file in the request'})
            resp.status_code = 400
            return resp
        file = request.files['file']
        if file.filename == '':
            resp = jsonify({'message' : 'No file selected for uploading'})
            resp.status_code = 400
            return resp
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            extension = filename.split('.')[-1:][0]
            x = datetime.datetime.now()
            innerdir = x.strftime("%x:%X:%f").replace(':','').replace('/','')
            maindir = app.config['UPLOAD_FOLDER']+'/'+innerdir
            os.makedirs(maindir)
            filename  = str(len(os.listdir(maindir))+1)+'.'+extension
            filepath = os.path.join(maindir, filename)
            file.save(filepath)

            title = request.form['title']
            description = request.form['description']
            category = request.form['category']
            keywords = request.form['keywords']
            privacyStatus = request.form['privacyStatus']

            youtube = get_authenticated_service(filename)
            try:
                rs = initialize_upload(youtube, filepath, title, description, category, keywords, privacyStatus)
                resp = jsonify({'message' : rs})
                resp.status_code = 200
                return resp
            except Exception as e:
                resp = jsonify({'message' : "An HTTP error occurred:\n%s" % str(e)})
                resp.status_code = 400
                return resp
        else:
            resp = jsonify({'message' : "only mp4, flv file allowed"})
            resp.status_code = 400
            return resp
    else:
        resp = jsonify({'message' : "Invalid request"})
        resp.status_code = 500
        return resp
    
    resp = jsonify({'message' : "Invalid request"})
    resp.status_code = 500
    return resp

@app.route('/open_recorder')
def open_recorder():
    return render_template('recorder.html')

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename, cache_timeout=0)

@app.route('/uploads/<subdir>/<filename>')
def download_file_2(subdir,filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], subdir),
                               filename, cache_timeout=0)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug = True)
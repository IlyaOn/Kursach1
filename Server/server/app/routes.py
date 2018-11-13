from flask import render_template, request, flash, redirect, url_for, send_from_directory
from app import app
from app.wavNN import calc_new_music
from app.midiNN.remix import lets_do_it
from multiprocessing import Process
import os

ALLOWED_EXTENSIONS_MID = set(['mid'])
ALLOWED_EXTENSIONS_WAV = set(['wav'])
def allowed_file(filename, mode):
    if mode == 'MID':
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_MID
    else:
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_WAV

           
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/index', methods=['GET', 'POST'])  
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")

@app.route('/process_data/wav/', methods=['Get','POST'])
def wavadapt():
    if request.method == 'POST':
        # check if the post request has the file part
        if ('style' not in request.files) or ('music' not in request.files):
            return redirect(request.url)
        style = request.files['style']
        music = request.files['music']
        if style.filename == '' or music.filename == '':
            return redirect(request.url)
        if style and allowed_file(style.filename, 'wav') and music and allowed_file(music.filename, 'wav'):
            music.save(os.path.join(app.config['UPLOAD_FOLDER'], "music.wav"))
            style.save(os.path.join(app.config['UPLOAD_FOLDER'], "style.wav"))
            if os.path.isfile('{}/out.wav'.format(app.config['UPLOAD_FOLDER'])):
                os.remove('{}/out.wav'.format(app.config['UPLOAD_FOLDER']))
            p = Process(target=calc_new_music)
            p.start()
            return redirect(url_for('wait'))
        
    return render_template("wav.html")

@app.route('/process_data/mid/', methods=['Get','POST'])
def midadapt():
    if request.method == 'POST':
        if 'music' not in request.files:
            return redirect(request.url)
        music = request.files['music']
        if music.filename == '':
            return redirect(request.url)
        if music and allowed_file(music.filename, 'MID'):
            mode = request.form['style']
            music.save(os.path.join(app.config['UPLOAD_FOLDER'], "music.mid"))
            if os.path.isfile('{}/out.mid'.format(app.config['UPLOAD_FOLDER'])):
                os.remove('{}/out.mid'.format(app.config['UPLOAD_FOLDER']))
            p = Process(target=lets_do_it, args=(mode,))
            p.start()
            return redirect(url_for('wait'))
        
    return render_template("mid.html")

@app.route('/wait', methods=['GET', 'POST'])
def wait():
    if request.method == 'POST':
        if 'out.mid' in os.listdir(app.config['UPLOAD_FOLDER']):
            return redirect(url_for('uploaded_file',
                                    filename="out.mid"))
        if 'out.wav' in os.listdir(app.config['UPLOAD_FOLDER']):
            return redirect(url_for('uploaded_file',
                                    filename="out.wav"))
        return render_template("waitpage.html")
    return render_template("waitpage.html")

import os
import time
from app import app
import urllib.request
from flask import (Flask, 
                   flash, 
                   request, 
                   redirect, 
                   url_for, 
                   render_template, 
                   Response, 
                   jsonify)
from werkzeug.utils import secure_filename
from PIL import Image

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
WIDTH = app.config['PIXELS_WIDTH']
HEIGHT = app.config['PIXELS_HEIGHT']

LAST_PIXELS = 'pixels.png'
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        fpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(fpath)
        img = Image.open(fpath)
        pixels = img.resize((WIDTH, HEIGHT),resample=Image.BILINEAR)
        pixels_x4 = img.resize((int(WIDTH/2), int(HEIGHT/2)),resample=Image.BILINEAR)
        _pixels = pixels.resize(img.size,Image.NEAREST)
        t = time.time()
        pixels_name = f'result{t}.png'
        pixels_path = os.path.join(app.config['UPLOAD_FOLDER'], pixels_name)
        #result.save(pixels_path)
        app.config['LAST_PIXELS'] = pixels.tobytes()
        app.config['LAST_PIXELS_X4'] = pixels_x4.tobytes()
        app.config['PORTION'] = 0
        _pixels.save(pixels_path)
        #print('upload_image filename: ' + filename)
        flash('Image successfully uploaded and displayed below')
        return render_template('upload.html', 
                               rfilename=pixels_name,
                               ofilename=filename)
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)
    


@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/portion', methods=['GET', 'POST'])
def setget_portion():
    if request.method == 'POST':
        content = request.json
        print(content['portion_size'], type(content['portion_size']))
        por = content['portion_size']
        if por <= 0:
            por = 1
        if por > HEIGHT:
            por = HEIGHT
        app.config['PORTION_SIZE'] = por
        return jsonify({'status':'ok', 'portion_lines':str(por)})

@app.route('/get_portion')
def get_data_portion():
    if not 'PORTION' in app.config:
        return jsonify({'status':'fail', 'message':'set_image'}), 500
    else:
        data = app.config['LAST_PIXELS']
        por = app.config['PORTION']
        start = WIDTH*int(HEIGHT/2) * por
        end = WIDTH*int(HEIGHT/2) * (por + 1)
        PIXELS = WIDTH * HEIGHT * 3
        if start >= PIXELS:
            return Response(b'', mimetype="bytes", direct_passthrough=True)
        if end > PIXELS:
            end = PIXELS
        return Response(data[start: end], mimetype="bytes", direct_passthrough=True)
    
@app.route('/get_size')
def get_pixels_size():
    s = (app.config['PIXELS_WIDTH'], app.config['PIXELS_HEIGHT'])
    return jsonify({'status':'ok', 'size':s})

@app.route('/next_portion', methods=['POST'])
def next_data_portion():
    if not 'PORTION' in app.config:
        return jsonify({'status':'fail', 'message':'set_image'})
    else:
        app.config['PORTION'] = 1 + app.config['PORTION']
        cur = app.config['PORTION']
        return jsonify({'status':'ok', 'portion_lines':cur})


@app.route('/get_small')
def get_data_small():
    data = app.config['LAST_PIXELS_X4']
    return Response(data, mimetype="bytes", direct_passthrough=True)

@app.route('/get_big')
def get_data_big():
    data = app.config['LAST_PIXELS']
    return Response(data, mimetype="bytes", direct_passthrough=True)

if __name__ == "__main__":
    app.run('0.0.0.0')

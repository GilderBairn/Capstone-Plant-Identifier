from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import mysql.connector
import pickle
import cv2
from tensorflow import keras
import tensorflow.image as tfimage
import tensorflow.data as tfdata
from sklearn.linear_model import LogisticRegression
import os

app = Flask(__name__)

app.secret_key = b's*3%$oSej2N#p?'
UPLOAD_FOLDER = 'uploads'
ALLOWED_FILES = {'jpg', 'jpeg', 'png', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MODEL_PATH'] = 'logreg.pkl'
db = mysql.connector.connect(host='localhost', user='phpmyadmin', passwd='Lizziefarts303!', database='plantid')
# TODO add a new mysql user and replace this info
cursor = db.cursor()


def get_inceptionv3():
    base_model = keras.applications.inception_v3.InceptionV3(include_top=False, weights='imagenet',
                                                             input_shape=(299, 299, 3), pooling='avg')
    return base_model


def preprocess(image):
    resized_image = tfimage.resize(image, [299, 299])
    final_image = keras.applications.inception_v3.preprocess_input(resized_image)
    return final_image


def extract_image_features(fname):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], fname)
    image = cv2.imread(file_path)
    image = preprocess(image)
    in_tensor = tfdata.Dataset.from_tensors([image])
    inception = get_inceptionv3()
    return inception.predict(in_tensor, verbose=0, steps=1)


def get_model():
    with open(app.config['MODEL_PATH'], 'rb') as fp:
        result = pickle.load(fp)
    return result


@app.route('/')
def index():
    return render_template('index.html', test='homepage')


@app.route('/scan')
def scan_plant():
    return render_template('scan.html', test='test')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_FILES


@app.route('/results', methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Missing image file portion of scan request')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No image file selected for scan')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            model = get_model()
            features = extract_image_features(filename)
            prediction = model.predict(features)[0]
            #return redirect(url_for('results', image=filename))
            cursor.execute('SELECT * FROM species WHERE classID = %d' % int(prediction))
            info = cursor.fetchall()[0]
            genus = info[1]
            family = info[2]
            species = info[3]
            return render_template('results.html', image=filename, species=species, family=family, genus=genus)
        else:
            flash('Wrong file type')
            return redirect(request.url)
    return render_template('results.html')


@app.route('/upload/<filename>')
def result_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/about')
def about():
    return render_template('index.html', test='about')


if __name__ == '__main__':
    app.run(debug=True)

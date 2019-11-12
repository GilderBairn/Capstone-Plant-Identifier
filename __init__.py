from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

app.secret_key = b's*3%$oSej2N#p?'
UPLOAD_FOLDER = 'uploads'
ALLOWED_FILES = {'jpg', 'jpeg', 'png', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#sql = MySQL()
#TODO add a new mysql user and replace this info
#app.config['MYSQL_DATABASE_USER'] = 'phpmyadmin'
#app.config['MYSQL_DATABASE_PASSWORD'] = 'Lizziefarts303!'
#app.config['MYSQL_DATABASE_DB'] = 'plantid'
#app.config['MYSQL_DATABSE_HOST'] = 'localhost'
#sql.init_app(app)

#connection = sql.connect()
#cursor = connection.cursor()


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
            #return redirect(url_for('results', image=filename))
            return render_template('results.html', image=filename)
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

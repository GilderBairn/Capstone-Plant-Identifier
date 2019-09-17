from flask import Flask, render_template
from flask.ext.mysql import MySQL

app = Flask(__name__)

sql = MySQL()
#TODO add a new mysql user and replace this info
app.config['MYSQL_DATABASE_USER'] = 'phpmyadmin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Lizziefarts303!'
app.config['MYSQL_DATABASE_DB'] = 'plantid'
app.config['MYSQL_DATABSE_HOST'] = 'localhost'
sql.init_app(app)

connection = sql.connect()
cursor = connection.cursor()


@app.route('/')
def index():
    return render_template('index.html', test='butts')


@app.route('/scan')
def scan_plant():
    return render_template('index.html', test=str(cursor))


if __name__ == '__main__':
    app.run(debug=True)

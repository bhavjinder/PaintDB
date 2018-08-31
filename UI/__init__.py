import os
from flask import Flask
from flask import render_template, redirect, url_for, request, flash
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import current_app
engine = create_engine('sqlite:///C:\\Users\\olgas\\Desktop\\PaIntDB.db', echo=True)
Session = sessionmaker(bind=engine)

def removeFiles():
    for root, dirs, files in os.walk(current_app.config['UPLOAD_FOLDER']):
        for file in files:
            filename = os.path.splitext(file)[0]
            if (filename == 'proteins') | (filename == 'metabolites'):
                os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], file))

def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        UPLOAD_FOLDER= os.path.join('user_upload'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    # a simple page that says hello
    @app.route('/')
    def PaIntDB():
        return redirect(url_for('home'))

    @app.route('/home', methods = ['GET', 'POST'])
    def home():
        removeFiles()
        return render_template('home.html')

    from . import info
    app.register_blueprint(info.bp)

    from . import query
    app.register_blueprint(query.bp)

    return app
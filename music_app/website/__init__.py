from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path




db = SQLAlchemy()
DB_NAME = "database.db"





def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dfjdfgngjngjkrgn'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    

    from .views import views
    from .auth import auth
    from .playlist import playlist
    from .album import album
    from .admin import admin

    app.register_blueprint(views, url_prefix= '/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(playlist, url_prefix='/')
    app.register_blueprint(album, url_prefix='/')
    app.register_blueprint(admin, url_prefix= '/admin')

    return app



def create_database():
    if not path.exists('website/' + DB_NAME):
        db.create_all()
#        print("Database Created")
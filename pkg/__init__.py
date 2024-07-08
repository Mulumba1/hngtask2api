
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager


db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    from pkg.models import db
    app = Flask(__name__, instance_relative_config=True)  
    app.config.from_pyfile('config.py', silent=True)  
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)


    return app

app = create_app()

from pkg import api_routes





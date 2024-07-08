from datetime import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()



class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    phone = db.Column(db.String)
    user_datereg = db.Column(db.DateTime(), default=datetime.utcnow)
    user_org = db.Column(db.String, db.ForeignKey('organisations.org_id'))
    org = db.relationship('Organisation', backref='users', lazy=True)

class Organisation(db.Model):
    __tablename__ = 'organisations'
    org_id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    

class UserOrganisation(db.Model):
    __tablename__ = 'user_organisation'
    user_id = db.Column(db.String, db.ForeignKey('users.user_id'), primary_key=True)
    org_id = db.Column(db.String, db.ForeignKey('organisations.org_id'), primary_key=True)

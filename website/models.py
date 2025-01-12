from . import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Business(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    registry_code = db.Column(db.String(10), nullable=False)
    total_capital = db.Column(db.Float, nullable=False)
    founding_date = db.Column(db.Date, nullable=False, default=func.now())
    shareholders = relationship('Shareholder', backref='business')
    shares = relationship('Share', backref='business')

class Shareholder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_founder = db.Column(db.Boolean, nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=True)
    shares = relationship('Share', backref='shareholder')

class Share(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shareholder_id = db.Column(db.Integer, db.ForeignKey('shareholder.id'), nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False)
    share = db.Column(db.Float, nullable=False)

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    surname = db.Column(db.String(256), nullable=False)
    personal_code = db.Column(db.String(11), nullable=False, unique=True)
    shareholders = relationship('Shareholder', backref='person')
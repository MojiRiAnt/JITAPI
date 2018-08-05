# pylint: disable=E1101
import string
import random
import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

_STRING_SIZE = 128
_UNKNOWN_PHOTO_PATH = "undefined.png"

def token_generator():
    ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))

def client_secret_generator():
    ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(_STRING_SIZE), nullable=False)
    login = db.Column(db.String(_STRING_SIZE), unique=True, nullable=False)
    password = db.Column(db.String(_STRING_SIZE), nullable=False)
    access = db.Column(db.String(_STRING_SIZE), unique=True, default=token_generator)
    permission = db.Column(db.Integer, default=0, nullable=False) 
    register = db.Column(db.DateTime, default=datetime.datetime.now)
    photo = db.Column(db.String, default=_UNKNOWN_PHOTO_PATH)
    cafe_id = db.Column(db.Integer, db.ForeignKey("cafe.id"), default=-1)
    cafe = db.relationship('Cafe', backref=db.backref('employees', lazy=True))

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(_STRING_SIZE), nullable=False)
    permission = db.Column(db.Integer(), nullable=False, default=0)
    secret = db.Column(db.Integer, default=client_secret_generator, nullable=False)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(_STRING_SIZE), nullable=False)
    address = db.Column(db.String(_STRING_SIZE), nullable=False)

class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #employees = backref to its employees

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(_STRING_SIZE), nullable=False)
    expiry = db.Column(db.Interval, nullable=False)

class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(_STRING_SIZE), nullable=False)
    mass = db.Column(db.Float, default=0, nullable=False)
    is_visible = db.Column(db.Boolean, default=True, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    describe = db.Column(db.String(_STRING_SIZE), default="", nullable=False)
    photo_path = db.Column(db.String(_STRING_SIZE), default=_UNKNOWN_PHOTO_PATH, nullable=False)
    tags = db.Column(db.String(_STRING_SIZE), default="[]", nullable=False)
    ingredients = db.Column(db.String(_STRING_SIZE), default="[]", nullable=False)

class Wish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(_STRING_SIZE), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    customer = db.relationship('Customer', backref=db.backref('orders', lazy=True))

class Good(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mass = db.Column(db.Float, nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredient.id"), nullable=False)
    ingredient = db.relationship("Ingredient")
    cafe_id = db.Column(db.Integer, db.ForeignKey("cafe.id"), nullable=False)
    cafe = db.relationship("Cafe")
    date = db.Column(db.DateTime, default=datetime.datetime.now)
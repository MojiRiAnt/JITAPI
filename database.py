# pylint: disable=E1101
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from json import dumps, loads
from crypto import random_string

db = SQLAlchemy()

# ====== Database variables ====== # IN DEVELOPMENT

_PHOTO_PATH = "resources/public/unknown.png"
_STRING_SIZE = 127
_TOKEN_SIZE = 16
_SECRET_SIZE = 16

# ====== Database functions ======= # IN DEVELOPMENT

def td_to_str(td):
    minutes = td.seconds % 3600
    hours = int(td.seconds / 3600)
    return "{}-{}-{}".format(td.days, hours, minutes)

def str_to_td(s):
    vals = list(map(int, s.split('-')))
    return timedelta(days=vals[0], hours=vals[1], minutes=vals[2])

def token_gen():
    return random_string(_TOKEN_SIZE)

def secret_gen():
    return random_string(_SECRET_SIZE)

# ====== Database models ====== # IN DEVELOPMENT

class Employee(db.Model): # Cafe employee

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(_STRING_SIZE), nullable=False)
    login = db.Column(db.String(_STRING_SIZE), unique=True, nullable=False)
    password = db.Column(db.String(_STRING_SIZE), nullable=False)
    token = db.Column(db.String(_STRING_SIZE), default=token_gen)
    coordinats = db.Column(db.String(_STRING_SIZE), default="0, 0")
    permission = db.Column(db.Integer, default=0, nullable=False) 
    registered = db.Column(db.DateTime, default=datetime.now)
    photo = db.Column(db.String, default=_PHOTO_PATH)
    cafe_id = db.Column(db.Integer, db.ForeignKey("cafe.id"), default=-1)
    cafe = db.relationship('Cafe', backref=db.backref('employees', lazy=True))

    @classmethod
    def load(cls, employee):
        try:
            return Employee(**employee)
        except Exception as err:
            raise err


class Client(db.Model): # Client app

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(_STRING_SIZE), nullable=False)
    secret = db.Column(db.String(_STRING_SIZE), default=secret_gen, nullable=False)


class Customer(db.Model): # Orders' adress
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(_STRING_SIZE), nullable=False)
    address = db.Column(db.String(_STRING_SIZE), nullable=False)
    #wishes = backref to their wishes


class Cafe(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    #employees = backref to its employees

    @classmethod
    def load(cls, cafe):
        try:
            return Cafe(**cafe)
        except Exception as err:
            raise err


class Ingredient(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(_STRING_SIZE), nullable=False)
    expiry = db.Column(db.Interval, nullable=False)

    def dump(self):
        return {
            "id": self.id,
            "title": self.title,
            "expiry" : td_to_str(self.expiry)
        }

    @classmethod
    def load(cls, ingredient):
        ingredient["expiry"] = str_to_td(ingredient.get("expiry"))
        return Ingredient(**ingredient)


class Dish(db.Model): # They form our menu

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(_STRING_SIZE), nullable=False)
    mass = db.Column(db.Float, default=0, nullable=False)
    is_visible = db.Column(db.Boolean, default=True, nullable=False)
    is_favourite = db.Column(db.Boolean, default=False, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    describe = db.Column(db.String(_STRING_SIZE), default="", nullable=False)
    photo = db.Column(db.String(_STRING_SIZE), default=_PHOTO_PATH, nullable=False)
    tags = db.Column(db.String(_STRING_SIZE), default="[]", nullable=False)
    ingredients = db.Column(db.String(_STRING_SIZE), default="[]", nullable=False)

    def dump(self):
        return {
            "id": self.id,
            "title": self.title,
            "mass": self.mass,
            "is_visible": self.is_visible,
            "is_favourite": self.is_favourite,
            "cost": self.cost,
            "describe": self.describe,
            "photo": self.photo,
            "tags": loads(self.tags),
            "ingredients": loads(self.ingredients),
        }

    # When uncommenting, don't forget to import dumps at the beginning of the file
    @classmethod
    def load(cls, dish):
        try:
            dish["tags"] = dumps(dish.get("tags"))
            dish["ingredients"] = dumps(dish.get("ingredients"))
            return Dish(**dish)
        except Exception as err:
            raise err
      

class Wish(db.Model): # An order of Dish from Customer

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Integer, default=0)
    dishes = db.Column(db.String(2 ** 16), nullable=False)
    address = db.Column(db.String(2 ** 16), nullable=False)
    coordinats = db.Column(db.String(2 ** 16), default="0.0, 0.0")

    @classmethod
    def load(cls, wish):
        wish["dishes"] = dumps(wish.get("dishes"))
        return Wish(**wish)

    def dump(self):
        return {
            "id": self.id,
            "dishes": loads(self.dishes),
            "address": self.address,
            "coordinats": self.coordinats
        }

class Good(db.Model):
    """
    Some amount of ingredient. (Ingredient -- abstract type)
    """
    id = db.Column(db.Integer, primary_key=True)
    mass = db.Column(db.Float, nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredient.id"), nullable=False)
    ingredient = db.relationship("Ingredient")
    cafe_id = db.Column(db.Integer, db.ForeignKey("cafe.id"), nullable=False)
    cafe = db.relationship("Cafe")
    date = db.Column(db.DateTime, default=datetime.now)

    def dump(self):
        return {
            "id": self.id,
            "mass": self.mass,
            "ingredient_id": self.ingredient_id,
            "date": self.date.strftime("%d%m%Y")
        }

    @classmethod
    def load(cls, good):
        return Good(**good)

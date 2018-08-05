from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///var/database.db" # Initializing app
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_ENV'] = "development"

import database as db

db.db.init_app(app)                                                 # Initializing database

# ====== Routes & queries ====== # IN DEVELOPMENT

from flask import Blueprint, request
from functools import wraps
from json import dumps, loads

COOK = 2 ** 0
DRIVER = 2 ** 1
WRH_MANAGER = 2 ** 2
EMP_MANAGER = 2 ** 3
ADMIN = 2 ** 4

def rsp(status, msg = None, res = None):
    return dumps({
        "status": status,
        "message": msg,
        "res": res
    }, indent=2)

def keys_valid(given, required):
    for required_key in required:
        if required_key not in given:
            return False
    return True

"""
Usage of next 2 decorators example:
@app.route("/route")
@check_emloyee()
@check_permission(ADMIN | COOK)
def handle(employee):
...
NOTE: recomended to use this decorators together and only in given order
NOTE: check_permission decorator push into end function employee argument so don't miss it
"""

def check_employee():
    def real_decorator(func):
        @wraps(func)
        def wrapper(**args):
            if not keys_valid(request.args.keys(), ["login", "token"]):
                return rsp(400, "doesn't given login or token")

            emp = db.Employee.query.filter_by(
                login=request.args.get("login"),
                token=request.args.get("token")
            ).first()

            if not emp:
                return rsp(400, "couldn't prove given employee")
            return func(**args)
        return wrapper
    return real_decorator

def check_permission(required_permissions):
    def real_decorator(func):
        @wraps(func)
        def wrapper(**args):
            emp = db.Employee.query.filter_by(
                login=request.args.get("login")
            ).first()

            if emp.permission & required_permissions != required_permissions:
                return rsp(400, "permissions of given employee denied")
            return func(employee=emp, **args)
        return wrapper
    return real_decorator

# --------------------------------------------------------------------------------

@app.route("/add/ingredient", methods=["POST"])
@check_employee()
@check_permission(ADMIN)
def add_ingredient_handle(employee):
    try:
        ing = db.Ingredient.load(loads(request.data))
    except Exception as _:
        return rsp(400, "couldn't parse data")


if __name__ == '__main__':

	# LOAD YOUR DEBUG HERE, AND DON'T COMMIT IT
	app.run(host='0.0.0.0', port='5000', debug=True) # WARNING : Debug mode is ON
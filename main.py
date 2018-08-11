# pylint: disable=E1101
from flask import Flask

app = Flask(__name__,
	template_folder="resources/private/templates",
	static_folder="resources")

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///var/database.db" # Initializing app
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_ENV'] = "development"

import database as db

db.db.init_app(app)                                                 # Initializing database

# ====== Routes & queries ====== # IN DEVELOPMENT

from flask import Blueprint, request, render_template, send_from_directory
from functools import wraps
from json import dumps, loads, load

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

def json_load_byteified(file_handle):
    return _byteify(
        load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )

def json_loads_byteified(json_text):
    return _byteify(
        loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )

def _byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data

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

# ------- ADMIN SECTION -------- # COMPLETED

@app.route("/add/ingredient", methods=["POST"])
@check_employee()
@check_permission(ADMIN)
def add_ingredient_handle(employee):
	try:
		ing = db.Ingredient.load(json_loads_byteified(request.data))
	except Exception as _:
		return rsp(400, "couldn't parse ingredient")

	print(db.db.session)
	db.db.session.add(ing)
	db.db.session.commit()
	return rsp(200, "ingredient were added")

@app.route("/get/ingredient/<int:ingredient_id>", methods=["POST"])
@check_employee()
@check_permission(ADMIN)
def get_ingredient_handle(employee, ingredient_id):
	ing = db.Ingredient.query.filter_by(id=ingredient_id).first()

	if not ing:
		return rsp(400, "couldn't ingredient with such id")

	return rsp(200, "ingredient were sent", ing.dump())

@app.route("/get/ingredients", methods=["POST"])
@check_employee()
@check_permission(ADMIN)
def get_ingredients_handle(employee):
	ing = db.Ingredient.query.all()

	return rsp(200, "ingredients were sent", list(map(db.Ingredient.dump, ing)))

@app.route("/add/dish", methods=["POST"])
@check_employee()
@check_permission(ADMIN)
def add_dish_handle(emloyee):
	try:
		dish = db.Dish.load(json_loads_byteified(request.data))
	except Exception as _:
		return rsp(200, "couldn't parse a dish")

# ------- WAREHOUSE MANAGER SECTION --------- # COMPLETED

@app.route("/supply", methods=["POST"])
@check_employee()
@check_permission(WRH_MANAGER)
def supply_handle(employee):
	try:
		supply = json_loads_byteified(request.data)
		for good in supply:
			good["cafe_id"] = employee.cafe_id

		goods = map(db.Good.load, supply)
	except Exception as _:
		return rsp(400, "couldn't parse supply")

	for good in goods:
		db.db.session.add(good)
	db.db.session.commit()
	return rsp(200, "supply were added")
	
@app.route("/get/goods", methods=["POST"])
@check_employee()
@check_permission(WRH_MANAGER)
def get_goods_handle(employee):
	goods = db.Good.query.filter_by(cafe_id=employee.cafe_id).all()
	goods = list(map(db.Good.dump, goods))
	return rsp(200, "goods were sent", dumps(goods, indent=2))

# ------- EMPLOYEES MANAGER SECTION ---------- # IN DEVELOPMENT

# ------- PUBLIC MANAGER SECTION ------------- # IN DEVELOPMENT

@app.route("/public/<path:pt>")
def public_handle(pt):
	return send_from_directory("resources/public", pt)

@app.route("/get/dishes", methods=["GET"])
def get_dishes_handle():
	dishes = db.Dish.query.filter_by(is_visible=True).all()
	dishes = list(map(db.Dish.dump, dishes))
	return rsp(200, "dish were sent", dumps(dishes))

@app.errorhandler(404)
def error_404(e):
	return render_template('error_404.html'), 404

if __name__ == '__main__':

	# LOAD YOUR DEBUG HERE, AND DON'T COMMIT IT

	app.run(host='0.0.0.0', port='5000', debug=True) # WARNING : Debug mode is ON
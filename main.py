# pylint: disable=E1101, E0611, E0401
from flask import Flask, Blueprint, request, render_template, send_from_directory
from flask_cors import CORS
from functools import wraps
from json import dumps, loads, load
from crypto import random_string
from time import sleep
import requests
import hashlib
import os

app = Flask(__name__,
	template_folder="resources/private/templates",
	static_folder="resources")

# make possible to send crossdomain request on this host
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///var/database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_ENV'] = "development"
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.join(os.getcwd(), "resources"), "public")

import database as db

db.db.init_app(app)

# masks of permissions
COOK = 2 ** 0
DRIVER = 2 ** 1
WRH_MANAGER = 2 ** 2
EMP_MANAGER = 2 ** 3
ADMIN = 2 ** 4

# states of order
WAITING_FOR_COOKING = 0
COOKING = 1
WAITING_FOR_DELIVERING = 2
DELIVERING = 3
DELIVERED = 4

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

def stringify(data):
	if type(data) is bytes:
		return bytes.decode(data)
	else:
		return data

def check_is_unique(path, filename):
	return filename not in os.listdir(path)

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

def check_employee_():
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

def check_permission_(required_permissions):
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

# Created to disable authorization and authentification without 
# changing other code if it necessary

def check_employee_fake_():
	def real_decorator(func):
		@wraps(func)
		def wrapper(**args):
			return func(**args)
		return wrapper
	return real_decorator

def check_permission_fake_(required_permission):
	def real_decorator(func):
		@wraps(func)
		def wrapper(**args):
			return func(employee=None, **args)
		return wrapper
	return real_decorator

# check_employee = check_employee_
# check_permission = check_permission_
check_employee = check_employee_fake_
check_permission = check_permission_fake_

# ------- ADMIN SECTION -------- # COMPLETED

@app.route("/add/ingredient", methods=["POST", "GET"])
@check_employee()
@check_permission(ADMIN)
def add_ingredient_handle(employee):
	try:
		ing = db.Ingredient.load(loads(stringify(request.data)))
	except Exception as _:
		return rsp(400, "couldn't parse ingredient")

	db.db.session.add(ing)
	db.db.session.commit()
	return rsp(200, "ingredient were added")


@app.route("/delete/ingredient/<int:id>", methods=["POST", "GET"])
@check_employee()
@check_permission(ADMIN)
def delete_ingredient_handle(employee, id):
	ingredients = db.Ingredient.query.filter_by(id=id)

	if not ingredients:
		return rsp(400, "There is no ingredient with such id") 

	ingredient = ingredients[0]
	db.db.session.delete(ingredient)
	db.db.session.commit()

	return rsp(200, "Ingredient was deleted")


@app.route("/get/ingredient/<int:ingredient_id>", methods=["POST", "GET"])
@check_employee()
@check_permission(ADMIN)
def get_ingredient_handle(employee, ingredient_id):
	ing = db.Ingredient.query.filter_by(id=ingredient_id).first()

	if not ing:
		return rsp(400, "couldn't ingredient with such id")

	return rsp(200, "ingredient were sent", ing.dump())


@app.route("/get/ingredients", methods=["POST", "GET"])
@check_employee()
@check_permission(ADMIN)
def get_ingredients_handle(employee):
	ing = db.Ingredient.query.all()

	return rsp(200, "ingredients were sent", list(map(db.Ingredient.dump, ing)))


@app.route("/add/dish", methods=["POST", "GET"])
@check_employee()
@check_permission(ADMIN)
def add_dish_handle(emloyee):
	try:
		dish = db.Dish.load(stringify(loads((request.data))))
	except Exception as _:
		return rsp(400, "couldn't parse a dish")

	db.db.session.add(dish)
	db.db.session.commit()

	return rsp(200, "dish were addded")


@app.route("/delete/dish/<int:id>", methods=["POST", "GET"])
@check_employee()
@check_permission(ADMIN)
def delete_dish_handle(employee, id):
	dishes = db.Dish.query.filter_by(id=id).all()

	if not dishes:
		return rsp(400, "There is no such dish!")

	dish = dishes[0]
	db.db.session.delete(dish)
	db.db.session.commit()

	return rsp(200, "Dish was deleted")


@app.route("/upload/photo", methods=["POST", "GET"])
def upload_dish_photo_handle():
	filename = random_string(16)

	while not check_is_unique(app.config.get('UPLOAD_FOLDER'), filename):
		filename = random_string(16)

	try:
		file = request.files.get('file')
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	except Exception as _:
		return rsp(400, "couldn't upload the file")

	return rsp(200, "file was uploaded", filename)


@app.route("/get/orders", methods=["POST", "GET"])
@check_employee()
@check_permission(ADMIN)
def get_orders_handle(employee):
	with app.app_context():
		orders = db.Wish.query.filter_by(status=0).all()

	orders = list(map(lambda order : order.dump(), orders))

	return rsp(200, "Orders were sent", orders)

@app.route("/get/order_history", methods=["POST", "GET"])
@check_employee()
@check_permission(ADMIN)
def get_order_history_handle(employee):
	with app.app_context():
		orders = db.Wish.query.all()

	orders = list(map(lambda order : order.dump(), orders))

	return rsp(200, "Orders were sent", orders)

@app.route("/get/state_hashes", methods=["POST", "GET"])
@check_employee()
@check_permission(ADMIN)
def get_state_hashes(employee):
	result = {
		"dishes_hash": "1",
		"pictures_hash": "2",
		"orders_hash": "3",
		"ingredient_hash": "4",
	}

	dishes = db.Dish.query.all()
	pictures = os.listdir("{}/resources/public/".format(os.getcwd()))
	orders = db.Wish.query.all()
	ingredients = db.Ingredient.query.all()

	dishes = list(map(lambda x: str(x.id), dishes))
	orders = list(map(lambda x: str(x.id), orders))
	ingredients = list(map(lambda x: str(x.id), ingredients))

	result["dishes_hash"] = hashlib.sha256(str.encode(','.join(dishes))).hexdigest()
	result["pictures_hash"] = hashlib.sha256(str.encode(','.join(pictures))).hexdigest()
	result["orders_hash"] = hashlib.sha256(str.encode(','.join(orders))).hexdigest()
	result["ingredient_hash"] = hashlib.sha256(str.encode(','.join(ingredients))).hexdigest()	

	return rsp(200, "Hashes was sent", result)

@app.route("/get/images")
@check_employee()
@check_permission(ADMIN)
def get_images_handle(employee):
	pictures = os.listdir("{}/resources/public/".format(os.getcwd()))

	return rsp(200, "This is all files in /resources/public", pictures)


@app.route("/get/waiting_for_delivering_orders")
@check_employee()
@check_permission(ADMIN)
def waiting_for_delivering_orders_handle(employee):
	delivered_orders = db.Wish.query.filter_by(status=WAITING_FOR_COOKING).all()
	delivered_orders = list(map(db.Wish.dump, delivered_orders))
	return rsp(200, "This is orders that are already delivered", delivered_orders)


@app.route("/get/delivered_orders")
@check_employee()
@check_permission(ADMIN)
def get_deivered_orders_handle(employee):
	delivered_orders = db.Wish.query.filter_by(status=DELIVERED).all()
	delivered_orders = list(map(db.Wish.dump, delivered_orders))
	return rsp(200, "This is orders that are already delivered", delivered_orders)

# ------- WAREHOUSE MANAGER SECTION --------- # COMPLETED

@app.route("/supply", methods=["POST", "GET"])
@check_employee()
@check_permission(WRH_MANAGER)
def supply_handle(employee):
	try:
		print(stringify(request.data))
		supply = loads(stringify((request.data)))
		print(supply)
		supply = db.Supply.load(supply)

	except Exception as _:
		return rsp(400, "couldn't parse supply")

	db.db.session.add(supply)
	db.db.session.commit()

	return rsp(200, "supply were added")
	

@app.route("/delete/supply/<int:id>", methods=["POST", "GET"])
@check_employee()
@check_permission(WRH_MANAGER)
def delete_supply_handle(employee, id):
	supply = db.Supply.query.filter_by(id1=id).all()
	if not supply:
		return rsp(400, "There is no such supply :(")

	db.db.session.delete(supply[0])
	db.db.session.commit()
	return rsp(200, "Supply was deleted")

@app.route("/get/goods", methods=["POST", "GET"])
@check_employee()
@check_permission(WRH_MANAGER)
def get_goods_handle(employee):
	goods = db.Supply.query.all()
	goods = list(map(lambda x: x.dump(), goods))
	return rsp(200, "goods were sent", goods)

# ------- DRIVER SECTION -------- #

@app.route("/ready", methods=["POST", "GET"])
@check_employee()
@check_permission(DRIVER)
def ready_handle(employee):
	while True:
		with app.app_context():
			wishes = db.Wish.query.filter_by(status=WAITING_FOR_COOKING).all()

			if wishes:
				order = wishes[0]
				order.status = DELIVERING
				db.db.session.commit()
				return rsp(200, "order was sent", order.dump())

		sleep(0.25)

# This is fake version of ready that just send 
# and fake order after 1.5 seconds of waiting
@app.route("/ready_fake", methods=["POST", "GET"])
@check_employee()
@check_permission(DRIVER)
def ready_fake_handle(employee):
	sleep(1.5)

	wish = db.Wish.load({
		"address": "Kharkiv Darvina 19 40",
		"coordinats": "49.997752, 36.245775", 
		"dishes": [
			{
				"id": 1,
				"number": 2
			},
			{
				"id": 2,
				"number": 3
			}
		]
	}).dump()

	return rsp(200, "order were sent", wish)

@app.route("/note", methods=["POST", "GET"])
@check_employee_()
@check_permission_(DRIVER)
def note_handle(employee):
	if request.args.get("coordinats") is None:
		return rsp(400, "You don't sent us your coordinats")

	coords = request.args.get("coordinats")
	employee.coordinats = coords
	db.db.session.commit()

	return rsp(200, "You coordinats was successfull received!")

@app.route("/delivered", methods=["POST", "GET"])
@check_employee_()
@check_permission_(DRIVER)
def delivered_hadnle(employee):
	if request.args.get("order_id") is None:
		return rsp(400, "You don't set us an order id")

	id = request.args.get("order_id")

	orders = db.Wish.query.filter_by(id=id, status=2).all()

	if not orders:
		return rsp(400, "There is no order with such id that is delivering now")

	order = orders[0]
	order.status = DELIVERED
	db.db.session.commit()

	return rsp(200, "You ready with this! Congradulations!")

# ------- EMPLOYEES MANAGER SECTION ---------- #

# ------- PUBLIC SECTION ------------- #

@app.route("/public/<path:pt>")
def public_handle(pt):
	return send_from_directory("resources/public", pt)

@app.route("/get/dishes", methods=["POST", "GET"])
def get_dishes_handle():
	dishes = db.Dish.query.filter_by(is_visible=True).all()
	dishes = list(map(db.Dish.dump, dishes))
	return rsp(200, "dish were sent", dishes)

@app.route("/login", methods=["POST", "GET"])
def login_handle():
	login = request.args.get("login")
	pwd = request.args.get("password")

	with app.app_context():
		employee = db.Employee.query.filter_by(
			login=login,
			password=pwd
		).all()

	if not employee:
		return rsp(400, "no such employee")

	employee = employee[0]
	return rsp(200, "there is such employee", {
		"id": employee.id,
		"login": employee.login,
		"token": employee.token
	})

"""
Here debug curl request:
curl 'api.torianik.online:5000/make_order' -X GET -H 'Content-Type: application/json' -d \
'{"address": "Kharkiv Darvina 19 40","dishes": [{"dish_name": "snacks","number": 3},
{"dish_name": "burger","number": 1},{"dish_name": "harcho","number": 2}]}' 
"""
@app.route("/make_order", methods=["POST", "GET"])
def make_order_handle():

	try:
		obj_request = loads(stringify(request.data))
	except Exception:
		return rsp(400, "Couldn't parse json")

	try:
		address = obj_request.get("address")
		google_maps_host = "https://maps.googleapis.com/maps/api/geocode/json"
		secret_google_key = "AIzaSyBhoLgP6V1iOA6NmnASdQEBsm6HET0oQPg"
		address = '+'.join(address.split())

		url = "{}?address={}&key={}&language=ru".format(
			google_maps_host, 
			address, 
			secret_google_key
		)

		google_maps_request = requests.get(url)
		result = loads(stringify(google_maps_request.text)).get("results")[0]
		position = result.get("geometry").get("viewport").get("northeast")
		coordinats = "{}, {}".format(position.get("lat"), position.get("lng"))	

		obj_request["coordinats"] = coordinats
	except Exception:
		return rsp(400, "Google maps internal error(it is very bad!)")

	try:
		order = db.Wish.load(obj_request)
	except Exception as _:
		return rsp(400, "Couldn't parse order")

	google_maps_host = "https://maps.googleapis.com/maps/api/geocode/json"
	secret_google_key = "AIzaSyBhoLgP6V1iOA6NmnASdQEBsm6HET0oQPg"
	address = '+'.join(order.address.split())

	url = "{}?address={}&key={}&language=ru".format(
		google_maps_host, 
		address, 
		secret_google_key	
	)
	db.db.session.add(order)
	order.coordinats = coordinats
	db.db.session.commit()

	return rsp(200, "order was appended")	

@app.errorhandler(404)
def error_404(e):
	return render_template('error_404.html'), 404

if __name__ == '__main__':
	app.run(host='0.0.0.0', port='5000', debug=True)

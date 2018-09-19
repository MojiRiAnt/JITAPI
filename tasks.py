# pylint: disable=E1101
from invoke import task
from main import app, db
from json import loads

@task()
def rdb(c):
    """
    Reload database
    """
    with app.app_context():
        db.db.drop_all()
        db.db.create_all()

@task(rdb)
def load(c):
    """
    Load test dataset
    """
    def load(path, class_to_load):
        with open(path) as f:
            data = loads(f.read())
            with app.app_context():
                for obj in data:
                    db.db.session.add(class_to_load.load(obj))
                db.db.session.commit()

    load("resources/private/dishes.json", db.Dish)
    load("resources/private/cafes.json", db.Cafe)
    load("resources/private/employees.json", db.Employee)
    load("resources/private/ingredients.json", db.Ingredient)
    

    

@task()
def show_emps(c):
    """
    Display employees login and token
    """
    with app.app_context():
        emps = db.Employee.query.all()

    for emp in emps:
        print("{}:{}".format(emp.login, emp.token))

@task()
def run(c):
    app.run(host="0.0.0.0", port=5000, debug=True)
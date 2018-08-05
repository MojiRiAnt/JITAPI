from os import mkdir
from invoke import task, Collection
from main import app, db

@task()
def mkdir_var(c):
    try:
        mkdir("var")
    # pylint: disable=E0602
    except FileExistsError as _:
        pass

@task(mkdir_var)
def reload_db(c):
    with app.app_context():
        db.drop_all()
        db.create_all()

ns = Collection()
app_ns = Collection("app")
debug_ns = Collection("debug")

app_ns.add_task(reload_db)

ns.add_collection(app_ns)
ns.add_collection(debug_ns)
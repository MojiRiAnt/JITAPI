from functools import wraps
from json import dumps
from flask import request, Blueprint

# ====== Variables ====== # FINISHED PART

COOK = 2 ** 0
DRIVER = 2 ** 1
WRH_MANAGER = 2 ** 2
EMP_MANAGER = 2 ** 3
ADMIN = 2 ** 4

# ====== Functions ====== # WARNING : THIS PART SHOULD BE CHECKED

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
            if not (request.args.keys(), ["login", "token"]):
                return rsp(400, "doesn't given login or token")
            from database import Employee
            emp = Employee.query.filter_by(
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
            from database import Employee
            emp = Employee.query.filter_by(
                login=request.args.get("login")
            ).first
             if emp.permission & required_permissions != required_permissions:
                return rsp(400, "permissions of given employee denied")
             return func(employee=emp, **args)
        return wrapper
    return real_decorator

# ====== Routes ====== # IN DEVELOPMENT


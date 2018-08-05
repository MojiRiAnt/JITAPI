# ====== Initial app ====== # FINISHED PART

import flask

app = flask.Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///var/database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_ENV'] = "development"

# ====== Database stuff ====== # FINISHED PART

import database as db

db.db.init_app(app)

# ====== Routes & queries ====== # IN DEVELOPMENT

@app.route('/test')
def testroute():
	return "<h1>Welcome to the test route! Danik sosi</h1>"

# ====== Running and Debugging ====== # FINISHED PART

if __name__ == '__main__':

	# LOAD YOUR DEBUG HERE, AND DON'T COMMIT IT

	app.run(host='0.0.0.0', port='5000', debug=True) # WARNING : Debug mode is ON
import flask

app = flask.Flask(__name__)

# Configuration stuff here

# Crypto stuff here

# Database stuff here

# Routes & queries here

@app.route('/test')
def testroute():
	return "<h1>Welcome to the test route! Danik sosi</h1>"

if __name__ == '__main__':
	app.run(host='0.0.0.0', port='5000', debug=True) # WARNING : Debug mode is ON
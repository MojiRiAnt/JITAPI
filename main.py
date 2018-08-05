from os import getcwd
from flask import Flask
from database import db
from routes import bp

app = Flask(__name__)

app.config.update(
    SQLALCHEMY_DATABASE_URI="sqlite:///{}/var/database.db".format(getcwd()),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    FLASK_ENV="development"
)

db.init_app(app)
app.register_blueprint(bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
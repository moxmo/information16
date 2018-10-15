from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

class Config(object):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "mysql://route:mysql@localhost:information16"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app.config.from_object(Config)

db = SQLAlchemy(app)

@app.route("/")
def helloworld():
    return "helloworld100"

if __name__ == "__main__":
    app.run()
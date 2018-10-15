from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis

app = Flask(__name__)

class Config(object):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "mysql://route:mysql@localhost:information16"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

app.config.from_object(Config)

db = SQLAlchemy(app)

redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT,decode_responses=True)

@app.route("/")
def helloworld():

    redis_store.set("name","li")
    print(redis_store.get("name"))

    return "helloworld100"

if __name__ == "__main__":
    app.run()
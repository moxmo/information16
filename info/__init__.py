from flask import Flask,session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf import CSRFProtect
from config import Config

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db = SQLAlchemy(app)

    redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT,decode_responses=True)

    CSRFProtect(app)

    Session(app)

    return app

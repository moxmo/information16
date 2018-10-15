import redis


class Config(object):

    DEBUG = True
    SECRET_KEY = "HI"


    SQLALCHEMY_DATABASE_URI = "mysql://route:mysql@localhost:information16"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 3600*24*2#两天期限
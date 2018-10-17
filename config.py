import logging
import redis


class Config(object):

    DEBUG = True
    SECRET_KEY = "HI"


    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@localhost:3306/information16"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 3600*24*2#两天期限,单位默认是秒

    LEVEL = logging.DEBUG
#开发环境
class DevelopConfig(Config):

    pass

#线上环境(生产环境)
class ProductConfig(Config):
    DUBUG = False
    LEVEL = logging.ERROR

#测试环境
class TestingConfig(Config):
    TESTING = True

#配置环境的统一访问路口
config_dict = {
    "develop":DevelopConfig,
    "product":ProductConfig,
    "testing":TestingConfig
}

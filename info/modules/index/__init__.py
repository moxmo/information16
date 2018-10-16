from flask import Blueprint


#创建蓝图对象
index_blu = Blueprint("index",__name__)

#装饰试图函数
from . import views
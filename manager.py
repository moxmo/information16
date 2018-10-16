import logging

from flask import current_app

from info import create_app

#调用业务模块获取app
app = create_app("develop")



if __name__ == "__main__":
    app.run()
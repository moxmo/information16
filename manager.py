import logging

from flask import current_app

from info import create_app,db,models
from flask_script import Manager
from flask_migrate import MigrateCommand,Migrate

#调用业务模块获取app
app = create_app("develop")

manager = Manager(app)

#使用Migrate 关联app,db
Migrate(app,db)

#给manager添加操作命令
manager.add_command("db",MigrateCommand)

if __name__ == "__main__":
    manager.run()
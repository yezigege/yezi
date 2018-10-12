from flask import Flask, session
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from info import db, create_app

# 通过指定的配置名字创建对应配置的app
app = create_app('development')
manager = Manager(app)
# 将 app 与 db 关联
Migrate(app, db)
# 将迁移命令添加到manager中
manager.add_command('db', MigrateCommand)

@app.route('/')
def index():
    session["name"] = "yezi"
    return "yezi "


if __name__ == '__main__':
    manager.run()


from flask import Flask, session
from flask.ext.sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_session import Session
from flask_wtf import CSRFProtect
from redis import StrictRedis

from config import Config

app = Flask(__name__)
# 加载配置
app.config.from_object(Config)
# 初始化数据库
db = SQLAlchemy(app)

# 初始化redis存储对象
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 开启当前项目的 CSRF 保护，只做服务验证功能
CSRFProtect(app)
# 设置session保存指定位置
Session(app)

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


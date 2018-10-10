from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis


class  Config(object):
    """工程配置信息"""
    DEBUG = True
    # 数据库的配置信息
    SQLALCHEMY_DATABASW_URI = "mysql://root:mysql@127.0.0.1:3306/chonggou"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis 的配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

app = Flask(__name__)
# 加载配置
app.config.from_object(Config)
# 初始化数据库
db = SQLAlchemy(app)

# 初始化redis存储对象
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 开启当前项目的 CSRF 保护，只做服务验证功能
CSRFProtect(app)

@app.route('/')
def index():
    return "yezi "


if __name__ == '__main__':
    app.run()


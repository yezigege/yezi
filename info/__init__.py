import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from redis import StrictRedis

from config import config


# 初始化数据库
# 在Flask很多扩展里面都可以先初始化扩展的 对象，然后再去调用 init_app 方法去初始化
from info.utils.common import do_index_class

db = SQLAlchemy()

redis_store = None  # type: StrictRedis

def setup_log(config_name):
    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL) # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    # 配置日志, 并且传入配置名字，以便能获取到指定配置所对应的日志等级
    setup_log(config_name)
    # 创建Flask对象
    app = Flask(__name__)
    # 加载配置
    app.config.from_object(config[config_name])

    # 通过app初始化
    db.init_app(app)
    # 初始化redis存储对象
    global redis_store
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT, decode_responses=True)
    # 开启当前项目 CSRF 保护，只做服务器验证功能
    # 帮我们做了：从cookie中取出随机值，从表单中取出随机，然后进行校验，并且响应校验结果
    # 我们需要做：1. 在返回响应的时候，往cookie中添加一个csrf_token，2. 并且在表单中添加一个隐藏的csrf_token
    # 而我们现在登录或者注册不是使用的表单，而是使用 ajax 请求，所以我们需要在 ajax 请求的时候带上 csrf_token 这个随机值就可以了
    CSRFProtect(app)
    # 设置session保存指定位置
    Session(app)

    # 添加自定义过滤器
    app.add_template_filter(do_index_class, "index_class")

    @app.after_request
    def after_response(response):
        # 生成随机的csrf_token的值
        csrf_token = generate_csrf()
        # 设置一个cookie
        response.set_cookie("csrf_token", csrf_token)
        return response

    # 注册蓝图
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)

    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)

    return app
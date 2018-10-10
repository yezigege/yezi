from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy



class  Config(object):
    """工程配置信息"""
    DEBUG = True
    # 数据库的配置信息
    SQLALCHEMY_DATABASW_URI = "mysql://root:mysql@127.0.0.1:3306/chonggou"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

@app.route('/')
def index():
    return "yezi "


if __name__ == '__main__':
    app.run()


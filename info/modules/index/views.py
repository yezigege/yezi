from flask import render_template, current_app

from info import redis_store
from . import index_blu


@index_blu.route('/')
def index():
    return render_template('news/index.html')


# 在打开网页的时候，浏览器默认回去请求/+favicon.ico做网站标签的小图标
# send_static_file 是 flask 去查找指定静态文件所调用的方法
@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')
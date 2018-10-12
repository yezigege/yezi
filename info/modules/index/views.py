from info import redis_store
from info.modules.index import index_blu


@index_blu.route('/')
def index():
    # 向redis中保存一个值 name tom
    redis_store.set("name", "tom")
    return 'index'
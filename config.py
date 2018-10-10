from redis import StrictRedis


class  Config(object):
    """工程配置信息"""
    SECRET_KEY = "b'xagZkmSwJyRiWW4EI7Tc4/aCu8X91oWtEMOcbub3ORXSz/252XMd2nGFDV9cl5hU'"

    DEBUG = True
    # 数据库的配置信息
    SQLALCHEMY_DATABASW_URI = "mysql://root:mysql@127.0.0.1:3306/chonggou"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis 的配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # Session保存配置
    SESSION_TYPE = "redis"
    # 开启session签名
    SESSION_USE_SIGNER = True
    # 指定 Session 保存的 redis
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 设置需要过期
    SESSION_PERMANENT = False
    # 设置过期时间
    PERMANENT_SESSION_LIFETIME = 86400 * 2
import logging

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

    # 设置日志等级
    LOG_LEVEL = logging.DEBUG


class ProductionConfig(Config):
    """生产环境下的配置"""
    DEBUG = False
    LOG_LEVEL = logging.WARNING

class DevelopmentConfig(Config):
    """开发环境下的配置"""
    DEBUG = True

class TestingConfig(Config):
    """单元测试环境下的配置"""
    DEBUG = True
    TESTING = True


config = {
    "production":ProductionConfig,
    "development":DevelopmentConfig,
    "testing":TestingConfig
}



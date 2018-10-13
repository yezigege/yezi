import random
import re
from datetime import datetime

from flask import request, abort, current_app, make_response, session
from flask.json import jsonify

from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.utils.response_code import RET
from . import passport_blu
from info.utils.captcha.captcha import captcha


@passport_blu.route('/register', methods=["POST"])
def register():
    """
    注册的逻辑
    1. 获取参数
    2. 校验参数
    3. 取到服务器保存的真实的短信验证码内容
    4. 校验用户输入的短信验证码内容和真实验证码内容是否一致
    5. 如果一致，初始化User模型，并且赋值
    6. 将 User 模型添加数据库
    7. 返回相应
    :return:
    """
    # 1. 获取参数
    param_dict = request.json

    mobile = param_dict.get("mobile")
    smscode = param_dict.get("smscode")
    password = param_dict.get("password")

    # 2. 校验参数
    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 校验手机号是否正确
    if not re.match("1[35678]\\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    # 3. 取到服务器保存的真实的短信验证码内容
    try:
        real_sms_code = redis_store.get("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="验证码已过期")

    # 4. 校验用户输入的短信验证码内容和真实验证码内容是否一致
    if real_sms_code != smscode:
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 5. 如果一致，初始化User模型，并且赋值
    user = User()
    user.mobile = mobile
    # 暂时没有昵称，使用手机号代替
    user.nick_name = mobile
    # 记录用户最后一次登录时间
    user.last_login = datetime.now()
    # todo 对密码进行处理

    # 6. 将 User 模型添加数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    # 往session中保存数据表示当前已经登录，因为注册完成即可代表已经登录
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name

    # 7. 返回响应
    return jsonify(errno=RET.OK, errmsg="注册成功")


@passport_blu.route('/sms_code', methods=["POST"])
def send_sms_code():
    """
    发送短信验证码的逻辑
    1. 获取参数：手机号，图片验证码，图片随机id
    2. 校验参数（手机号是否符合规则，判断是否有值）
    3. 从redis中取出真实验证码内容
    4. 与用户发送过来的验证码进行对比（如果不一致，就返回验证码输入错误）
    5. 如果一致，生成验证码内容（随即数据）
    6. 发送短信验证码
    7. 返回结果
    :return:
    """
    # 1. 获取参数：手机号，图片验证码，图片随机id
    # 前端返回过来的数据是data原始字符串，需要转换为字典来进行更好的检索
    # 有两种方式以供选择
    # 一：params_dict = json.loads(request.data)
    params_dict = request.json

    mobile = params_dict.get("mobile")
    image_code = params_dict.get("image_code")
    image_code_id = params_dict.get("image_code_id")

    # 2. 校验参数（手机号是否符合规则，判断是否有值）
    if not all([mobile, image_code_id, image_code]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")
    # 校验手机好是否正确
    if not re.match("1[35678]\\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    # 3. 从redis中取出真实验证码内容
    try:
        real_image_code = redis_store.get("ImageCodeId_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码已过期")

    # 4. 与用户发送过来的验证码进行对比（如果不一致，就返回验证码输入错误）
    if real_image_code.upper() != image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 5. 如果一致，生成验证码内容（随即数据）
    # 随机数字，保证数字长度为6位。不够的话在前面补0
    sms_code_str = "%06d" % random.randint(0, 999999)
    current_app.logger.debug("短信验证码的内容为:%s" % sms_code_str)

    # 6. 发送短信验证码
    # 注意： 测试的短信模板编号为1
    result = CCP().send_template_sms(mobile, [sms_code_str, constants.SMS_CODE_REDIS_EXPIRES / 5], "1")
    if result != 0:
        # 代表发送不成功
        return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")

    # 保存验证码内容到redis中
    try:
        redis_store.set("SMS_" + mobile, sms_code_str, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    # 7.返回结果
    return jsonify(errno=RET.OK, errmsg="发送成功")


@passport_blu.route('/image_code')
def get_image_code():
    """
    生成图片验证码并返回
    1. 取到参数
    2. 校验参数
    3. 生成图片验证码
    4. 保存图片验证码文字内容到redis
    5. 返回验证码图片
    :return:
    """
    # 1. 取到参数
    # args: 取到url中? 后面的参数
    image_code_id = request.args.get("imageCodeId", None)

    # 2. 校验 参数
    if not image_code_id:
        return abort(403)

    # 3. 生成图片验证码
    name, text, image = captcha.generate_captcha()

    # 4. 保存图片验证码文字内容到redis
    try:
        redis_store.set("ImageCodeId_" + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

    # 5. 返回验证码图片
    response = make_response(image)
    # 设置数据的类型，以便浏览器能够更智能的识别
    response.headers["Content-Type"] = "image/jpg"
    return response

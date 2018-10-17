import random
import re
import json
from flask import current_app, jsonify
from flask import json
from flask import make_response
from flask import request
from flask import session

from info import constants,db
from info import redis_store
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.utils.response_code import RET
from . import passport_blue
from info.utils.captcha.captcha import captcha


#### 注册用户思路分析
#功能描述: 登陆用户
# 请求路径: /passport/login
# 请求方式: POST
# 请求参数: mobile,password
# 返回值: errno, errmsg
@passport_blue.route('/register', methods=['POST'])
def register():
    # 1.获取参数
    dict_data = request.json
    mobile = dict_data.get("mobile")
    sms_code = dict_data.get("sms_code")
    password = dict_data.get("password")

    # 2.校验参数,为空校验
    if not all([mobile,sms_code,password]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不完整")
    # 3.手机号格式校验
    if not re.match("1[356789]\d{9}",mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号格式错误")
    # 4.通过手机号取出redis中的短信验证码
    try:
        redis_sms_code = redis_store.get("sms_code:%s"%mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取短信验证码异常")
    # 5.判断短信验证码是否过期
    if not redis_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码过期")
    # 6.删除redis中的短信验证码
    try:
        redis_store.delete("sms_code:%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="删除短信验证码异常")
    # 7.校验传入的短信验证码和,redis中的是否相等
    if sms_code != redis_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码填写错误")
    # 8.创建用户对象,设置属性
    user = User()
    user.nick_name = mobile
    user.password_hash = password
    user.mobile = mobile

    # 9.保存用户到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="用户注册失败")
    # 10.返回响应
    return jsonify(errno=RET.OK,errmsg="注册成功")

#获取短信验证码
#请求地址:/passport/sms_code
#请求方式:POST
#请求参数:mobile,image_code,image_code_id
#返回值：errno,errmsg
@passport_blue.route('/sms_code', methods=['POST'])
def sms_code():
    """
    1.获取参数
    2.校验参数,为空检验
    3.校验手机号格式
    4.根据传入的图片验证码编号获取redis中的图片验证码A
    5.判断图片验证码A,是否过期
    6.删除redis中的图片验证码A
    7.判断传入的验证码B, 和redis中的验证码A是否相等
    8.生成短信验证码
    9.调用CCP发送,并判断
    10.将短信验证码保存一份到redis
    11.返回响应
    :return:
    """
    #1.获取参数
    json_data = request.data
    dict_data = json.loads(json_data)
    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")
    #2.校验参数, 为空检验
    if not all([mobile,image_code,image_code_id]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不能为空")
    #3.校验手机号格式
    if not re.match("1[356789]\d{9}",mobile):
        return jsonify(errno=RET.DATAERR,errmsg="手机号格式不正确")
    #4.根据传入的图片验证码编号获取redis中的图片验证码A
    redis_image_code = redis_store.get("image_code:%s"%image_code_id)

    #5.判断图片验证码A, 是否过期
    if not redis_image_code:
        return jsonify(errno=RET.NODATA,errmsg="图片验证码过期")

    #6.删除redis中的图片验证码A
    redis_store.delete("image_code:%s"%image_code_id)

    #7.判断传入的验证码B, 和redis中的验证码A是否相等
    if image_code != redis_image_code:
        return jsonify(errno=RET.DATAERR,errmsg="图片验证码填写错误")

    #8.生成短信验证码
    sms_code = "%06d"%random.randint(0,999999)

    #9.调用CCP发送, 并判断
    ccp = CCP()
    result = ccp.send_template_sms(mobile,[sms_code,constants.SMS_CODE_REDIS_EXPIRES/60],1)

    if result == -1:
        return jsonify(errno=RET.DATAERR,errmsg="短信发送失败")

    #10.将短信验证码保存一份到redis
    redis_store.set("sms_code:%s"%mobile,sms_code,constants.SMS_CODE_REDIS_EXPIRES)
    #11.返回响应
    return jsonify(errno=RET.OK,errmsg="短信发送成功")


#获取图片验证码
#请求方式:/passport/image_code
#请求方式:GET
#请求参数:cur_id,pre_id
#返回值：图片验证码
@passport_blue.route('/image_code')
def image_code():
    """
    1,获取请求参数
    2,参数的校验
    3,生成图片验证码
    4,判断是否有上个图片验证码编号
    5,保存一份到redis
    6,返回图片验证码
    :return:
    """
    #1,获取请求参数
    cur_id = request.args.get("cur_id")
    pre_id = request.args.get("pre_id")

    #2,参数的校验
    if not cur_id:
        return "必须传递验证码编号"

    #3,生成图片验证码
    name,text,image_data = captcha.generate_captcha()
    print(text)

    try:
        #4,判断是否有上个图片验证码编号,有就删除
        if pre_id:
            redis_store.delete("image_code:%s"%pre_id)

        #5,保存一份到redis
        redis_store.set("image_code:%s"%cur_id,text,constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return "redis操作图片失败"

    #6,返回图片验证码
    response = make_response(image_data)
    response.headers["Content-Type"] = "image/jpg"
    return response
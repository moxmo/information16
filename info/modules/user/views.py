from flask import current_app
from flask import g, jsonify
from flask import redirect
from flask import request

from info import constants, db
from info.models import News, Category, User
from info.utils.commons import user_login_data
from info.utils.response_code import RET
from . import user_blue
from flask import render_template

#功能：作者页面信息展示
# 请求路径: /user/other
# 请求方式: GET
# 请求参数:id
# 返回值: 渲染other.html页面,字典data数据
@user_blue.route('/other')
@user_login_data
def other_info():
    """
    - 1.获取参数
    - 2.校验参数,为空
    - 3.通过编号查询,并判断作者是否存在
    - 4.携带作者信息,渲染页面
    :return:
    """
    #- 1.获取参数
    author_id = request.args.get("id")

    # 2.校验参数,为空
    if not author_id:
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    #- 3.通过编号查询,并判断作者是否存在
    try:
        author = User.query.get(author_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="用户查询失败")

    if not author:
        return redirect("/")

    ## - 4.携带作者信息,渲染页面
    data = {
        "author":author.to_dict(),
        "user_info": g.user.to_dict() if g.user else ""
    }


    return render_template("news/other.html",data=data)









#- 获取我的关注
# 请求路径: /user/news_follow
# 请求方式: GET
# 请求参数:p
# 返回值: 渲染user_follow.html页面  字典data数据
@user_blue.route('/user_follow')
@user_login_data
def user_follow():

    # - 1.获取参数
    page = request.args.get("p", "1")

    # - 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        page = 1

    # - 3.分页查询
    try:
        paginate = g.user.followed.paginate(page, 4,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")

        # - 4.获取分页对象属性,总页数,当前页,当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # - 5.对象列表转成字典列表
    author_list = []
    for author in items:
        author_list.append(author.to_dict())

        # - 6.携带数据渲染页面
    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "author_list": author_list
    }
    return render_template("news/user_follow.html", data=data)






#- 获取新闻发布列表
# 请求路径: /user/news_list
# 请求方式: GET
# 请求参数:p
# 返回值: GET渲染user_list.html页面
@user_blue.route('/news_list')
@user_login_data
def news_list():

  # - 1.获取参数
    page = request.args.get("p","1")

  # - 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        page = 1

  # - 3.分页查询
    try:
        paginate = News.query.filter(News.user_id == g.user.id).order_by(News.create_time.desc()).paginate(page,6,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取新闻失败")

  # - 4.获取分页对象属性,总页数,当前页,当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

  # - 5.对象列表转成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_review_dict())

  # - 6.携带数据渲染页面
    data = {
        "totalPage":totalPage,
        "currentPage":currentPage,
        "news_list":news_list
    }
    return render_template("news/user_news_list.html",data=data)



#- 新闻发布
# 请求路径: /user/news_release
# 请求方式: GET,  POST
# 请求参数:GET无,  POST,title,category_id,digest,index_image,content
# 返回值: GET请求,user_news_release.html,data分类列表字段数据,POST,errno,errmsg
def image_storage():
    pass


@user_blue.route('/news_release', methods=['GET', 'POST'])
@user_login_data
def news_release():
    #   - 0.判断是否是GET请求,携带分类数据展示
    if request.method == "GET":

        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="获取分类失败")

        #分类对象列表  转字典列表
        category_list = []
        for category in categories:
            category_list.append(category.to_dict())

        return render_template("news/user_news_release.html", categories=category_list)

    # - 1.如果是POST,获取参数
    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    # index_image = request.files.get("index_image")
    content = request.form.get("content")

  # - 2.校验参数,为空校验
    if not all([title,category_id,digest,content]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")


  # - 3.上传新闻图片
  #   try:
  #      image_name = image_storage(index_image.read())
  #   except Exception as e:
  #       current_app.logger.error(e)
  #       return jsonify(errno=RET.THIRDERR, errmsg="七牛云上传失败")
  #
  # # - 4.判断图片是否上传成功
  #   if not image_name:
  #       return jsonify(errno=RET.NODATA, errmsg="上传失败")

  # - 5.创建新闻对象,设置新闻属性
    news = News()
    news.title = title
    news.source = g.user.nick_name
    news.digest = digest
    # news.index_image_url = constants.QINIU_DOMIN_PREFIX + image_name
    news.content = content
    news.category_id = category_id
    news.user_id = g.user.id
    news.status = 1


  # - 6.保存到数据库
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="新闻发布失败")

  # - 7.返回响应
    return jsonify(errno=RET.OK, errmsg="发布成功")



#- 获取收藏新闻
# 请求路径: /user/collection
# 请求方式: GET,POST
# 请求参数:p  页数
# 返回值: user_collection.html页面,携带新闻数据data
@user_blue.route('/collection')
@user_login_data
def collection():
    # - 1.获取参数,页数
    page = request.args.get("p","1")

  # - 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        page = 1

  # - 3.分页查询,获取到分页对象
    try:
        paginate = g.user.collection_news.order_by(News.create_time.desc()).paginate(page,10,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取新闻失败")

  # - 4.获取分页对象属性,总页数,当前页,当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

  # - 5.对象列表转成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_dict())

  # - 6.拼接数据渲染页面
    data = {
        "totalPage":totalPage,
        "currentPage":currentPage,
        "news_list":news_list
    }
    return render_template("news/user_collection.html",data=data)





# - 密码修改
# 请求路径: /user/pass_info
# 请求方式: GET,POST
# 请求参数: GET无  POST请求有参数,old_password,new_password
# 返回值: user_pass_info.html页面,data字典数据,POST请求：errno,errmsg
@user_blue.route('/pass_info', methods=['GET', 'POST'])
@user_login_data
def pass_info():
    pass

#   - 1.判断请求方式,如果是GET,渲染页面
    if request.method == "GET":
        return render_template("news/user_pass_info.html")
#   - 2.如果是POST请求,获取参数
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

#   - 3.为空校验参数
    if not all ([old_password,new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

#   - 4.判断旧密码是否正确
    if not g.user.check_passowrd(old_password):
        return jsonify(errno=RET.DATAERR, errmsg="旧密码错误")

#   - 5.修改新密码
    g.user.password = new_password

#   - 6.返回响应
    return jsonify(errno=RET.OK, errmsg="修改成功")






#功能：展示基本信息资料
# 请求路径: /user/base_info
# 请求方式: GET,POST
# 请求参数: POST请求有参数,nick_name,signature,gender
# 返回值: errno,errmsg
@user_blue.route('/base_info',methods=["GET","POST"])
@user_login_data
def base_info():

    #判断如果是GET,携带用户数据  渲染页面
    if request.method == "GET":

        return render_template("news/user_base_info.html",user=g.user.to_dict())

    #如果是POST 获取参数
    # 1.获取参数
    nick_name=request.json.get("nick_name")
    signature=request.json.get("signature")
    gender=request.json.get("gender")

    # 2.校验参数, 为空校验
    if not all([nick_name,signature,gender]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    # 3.性别类型校验
    if not gender in ["MAN","WOMAN"]:
        return jsonify(errno=RET.DATAERR, errmsg="性别异常")

    # 4.修改用户信息
    g.user.signature = signature
    g.user.nick_name = nick_name
    g.user.gender = gender

    # 5.返回响应
    return jsonify(errno=RET.OK, errmsg="修改成功")




#功能：获取用户个人中心页面
# 请求路径: /user/info
# 请求方式: GET
# 请求参数: 无
# 返回值: user.html页面,用户字典data 数据
@user_blue.route('/info')
@user_login_data
def user_info():

    #判断用户是否有登陆
    if not g.user:
        return redirect("/")

    data = {
        "user_info":g.user.to_dict()
    }
    return render_template("news/user.html",data=data)

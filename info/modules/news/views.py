from flask import abort
from flask import current_app, jsonify
from flask import g
from flask import request
from flask import session

from info import db
from info.models import News, User, Comment
from info.utils.commons import user_login_data
from info.utils.response_code import RET
from . import news_blue
from flask import render_template

#- 评论思路分析
# 请求路径: /news/news_comment
# 请求方式: POST
# 请求参数: news_id,comment,parent_id,g.user
# 返回值: errno,errmsg,评论字典
@news_blue.route('/news_comment', methods=['POST'])
@user_login_data
def news_comment():
    #   - 1.判断用户是否登陆
    if not g.user:
        return jsonify(errno=RET.NODATA,errmsg="用户未登录")

#   - 2.获取参数
    news_id = request.json.get("news_id")
    content = request.json.get("comment")
    parent_id = request.json.get("parent_id")

#   - 3.校验参数,为空检验
    if not all([news_id,content]):
        return jsonify(errno=RET.NODATA,errmsg="参数不全")
#   - 4.根据新闻编号取出新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取新闻失败")

#   - 5.判断新闻对象是否存在
    if not news: return jsonify(errno=RET.NODATA, errmsg="新闻不存在")

#   - 6.创建评论对象,设置属性
    comment = Comment()
    comment.user_id = g.user.id
    comment.news_id = news_id
    comment.content = content
    if parent_id:
        comment.parent_id = parent_id

#   - 7.保存评论到数据库
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="评论失败")

#   - 8.返回响应
    return jsonify(errno=RET.OK, errmsg="评论成功", data=comment.to_dict())

#收藏与取消收藏
# 请求路径: /news/news_collect
# 请求方式: POST
# 请求参数: news_id,action,g.user
# 返回值: errno,errmsg
@news_blue.route('/news_collect', methods=['POST'])
@user_login_data
def news_collect():
    # 1.判断用户登陆状态
    if not g.user:
        return jsonify(errno=RET.NODATA,errmsg="用户未登录")
    # 2.获取参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    # 3.校验参数, 为空校验
    if not all ([news_id,action]):
        return jsonify(errno=RET.NODATA, errmsg="参数不全")
    # 4.判断操作类型
    if not action in ["collect","cancel_collect"]:
        return jsonify(errno=RET.DATAERR, errmsg="操作类型有误")
    # 5.通过新闻编号取出新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="新闻获取失败")
    # 6.判断新闻对象是否存在
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻不存在")

    try:
        # 7.根据操作类型, 收藏, 取消操作
        if action == "collect":
            if  not news in g.user.collection_news:
                print("fasdfsafa")
                g.user.collection_news.append(news)
        else:
            if news in g.user.collection_news:
                g.user.collection_news.remove(news)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="操作失败")
    # 8.返回响应
    return jsonify(errno=RET.OK, errmsg="操作成功")

#功能描述: 获取新闻详情
# 请求路径: /news/<int:news_id>
# 请求方式: GET
# 请求参数: news_id
# 返回值: datail.html页面,用户data字典数据
@news_blue.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):

    #根据新闻编号获取新闻对象
    try:
        new = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="新闻获取失败")
    #判断新闻对象是否存在,后续会对404做统一处理
    if not new:
        abort(404)
    # 2.1热门新闻,按照新闻点击量,查询前十条新闻
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(10).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")
    # 2.2将新闻列表对象,字典列表对象
    click_news_list = []
    for news in news_list:
        click_news_list.append(news.to_dict())
    #2.3判断用户是否收藏了该新闻
    is_collected = False
    if g.user and new in g.user.collection_news:
        is_collected = True

    #2.4获取该新闻所有评论数据
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取评论失败")

    # 2.5 将评论的对象列表,转成字典列表
    comment_list = []
    for comment in comments:
        comment_list.append(comment.to_dict())



    #携带新闻数据,到模板页面展示
    data = {
        "news":new.to_dict(),
        "click_news_list":click_news_list,
        "user_info": g.user.to_dict() if g.user else "",
        "is_collected":is_collected,
        "comments":comment_list
    }
    return render_template("news/detail.html",data=data)
from . import news_blue
from flask import render_template

#功能描述: 获取新闻详情
# 请求路径: /news/<int:news_id>
# 请求方式: GET
# 请求参数: news_id
# 返回值: datail.html页面,用户data字典数据
@news_blue.route('/<int:news_id>')
def news_detail(news_id):

    return render_template("news/detail.html")
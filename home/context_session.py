
from .views import *
from .models import *

# 通用函数，获取session并返回用户信息
def head_session(request):
    if request.session.get('userinfo'):
        user = jsonpickle.loads(request.session.get('userinfo'))
        user = User.objects.get(uid=user.uid)
        logmsgs = {'msg': '已登录'}
        return {'user': user, 'logmsgs': logmsgs}
    else:
        user = None
        logmsgs = {'msg': '登录/注册'}
        return {'user': user, 'logmsgs': logmsgs}

# 获取近期新闻和公告:
def getRecentNewsAndAmnt(request):
    # 近六条新闻
    r_news = News.objects.order_by('-id')[:6]

    # 近六条公告
    r_anmts = Announcement.objects.order_by('-id')[:6]

    # 查询帖子标题带有“反馈”的帖子
    feedbacks = Post.objects.filter(p_title__contains='反馈').order_by('-pid')[:6]

    return {'r_news': r_news, 'r_anmts': r_anmts, 'feedbacks': feedbacks}
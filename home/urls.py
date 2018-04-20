from django.conf.urls import url
from home import views

urlpatterns = [
    url(r'^$', views.index_view),   #主页

    url(r'^news/', views.news_view),   #新闻
    url(r'^newcont/', views.newcont_view),   #主体内容
    url(r'^announcement/', views.announcement_view),   #公告
    url(r'^anmtcont/', views.anmtcont_view),   #公告

    url(r'^register/', views.register_view),   #注册
    url(r'^login/', views.login_view),    #登录
    url(r'^user/', views.user_view),    #用户中心

    url(r'^forum/', views.forum_view),    #论坛
    url(r'^post/', views.post_view),  #帖子
    url(r'^space/', views.space_view),  # 空间

    url(r'^head/', views.user_headSet),    #头像设置
    url(r'^basicsInfo/', views.user_basicsInfoSet),    #基本信息设置
    url(r'^going/', views.user_goingSet),    #工作情况设置
    url(r'^perInfo/', views.user_perInfoSet),    #个人信息设置
    url(r'^safe/', views.user_safeSet),    #安全设置

]
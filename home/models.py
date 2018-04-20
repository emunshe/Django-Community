from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import models
from django.db.models import Count
from django.db import connection
from ckeditor_uploader.fields import RichTextUploadingField


# 用户信息
class User(models.Model):

    uid = models.AutoField(primary_key=True)
    # 头像
    head = models.ImageField(upload_to='heads', verbose_name='用户头像', null=True, blank=True)

    # 基本资料
    username = models.CharField(max_length=20, unique=True, verbose_name='用户名')
    name = models.CharField(max_length=20, verbose_name='真实姓名', null=True, blank=True)
    education = models.CharField(max_length=10, verbose_name='学历', null=True, blank=True)
    age = models.PositiveIntegerField(verbose_name='年龄', null=True, blank=True)
    sex = models.CharField(max_length=10, verbose_name='性别', null=True, blank=True)
    hobby = models.CharField(max_length=50, verbose_name='兴趣', null=True, blank=True)
    signature = models.CharField(max_length=100, verbose_name='个性签名', null=True, blank=True)

    # 工作情况
    company = models.CharField(max_length=30, verbose_name='公司', null=True, blank=True)
    profession = models.CharField(max_length=20, verbose_name='职业', null=True, blank=True)
    position = models.CharField(max_length=20, verbose_name='职位', null=True, blank=True)
    income = models.CharField(max_length=20, verbose_name='收入', null=True, blank=True)

    # 个人信息
    email = models.EmailField(max_length=30, unique=True, verbose_name='邮箱', null=True, blank=True)
    address = models.CharField(max_length=100, unique=True, verbose_name='家庭地址', null=True, blank=True)
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号', blank=True)
    qq = models.CharField(max_length=10, unique=True, verbose_name='QQ号', blank=True)

    # 账户安全
    password = models.CharField(max_length=16, verbose_name='用户密码')

    creating = models.DateField(auto_now_add=True, verbose_name='创建时间')
    modify = models.DateTimeField(auto_now=True, verbose_name='修改时间')

    # 汉化字段
    def __str__(self):
        return "用户名:%s"%self.username

    # 汉化表
    class Meta:
        verbose_name_plural = '用户信息'

# 公告信息
class Announcement(models.Model):

    a_title = models.CharField(max_length=100, verbose_name='公告标题')
    a_desc = models.CharField(max_length=100, verbose_name='公告前言', null=True, blank=True)
    a_content = RichTextUploadingField(verbose_name='公告内容', null=True, blank=True)
    a_creating = models.DateField(auto_now_add=True, verbose_name='创建时间')
    a_modify = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    a_isdelete = models.BooleanField()

    def __str__(self):
        return "标题:%s" %self.a_title

    class Meta:
        verbose_name_plural = '公告信息'

# 新闻信息
class News(models.Model):

    n_title = models.CharField(max_length=100, verbose_name='新闻标题')
    n_desc = models.CharField(max_length=100, verbose_name='新闻概述', null=True, blank=True)
    n_content = RichTextUploadingField(verbose_name='新闻内容', null=True, blank=True)
    n_creating = models.DateField(auto_now_add=True, verbose_name='创建时间')
    n_isdelete = models.BooleanField(default=False, verbose_name='是否删除')

    def __str__(self):
        return "标题:%s" % self.n_title

    class Meta:
        verbose_name_plural = '新闻信息'

#论坛
class Post(models.Model):

    pid = models.AutoField(primary_key=True)
    p_title = models.CharField(max_length=100, verbose_name='帖子标题')
    p_content = RichTextUploadingField(verbose_name='发帖内容', null=True, blank=True)
    p_image = models.ImageField(upload_to='post/images', null=True, blank=True, verbose_name='上传图片')
    p_file = models.FileField(upload_to='post/files', null=True, blank=True, verbose_name='上传文件')
    p_creating = models.DateField(auto_now_add=True, verbose_name='创建时间')
    p_isdelete = models.BooleanField(default=False, verbose_name='是否删除')
    user = models.ForeignKey(User, verbose_name='用户')

    def __str__(self):
        return "标题:%s" % self.p_title

    class Meta:
        verbose_name_plural = '论坛'

# 留言
class Message(models.Model):
    mid = models.AutoField(primary_key=True)
    m_msg = RichTextUploadingField(verbose_name='留言内容', null=True, blank=True)
    m_image = models.ImageField(upload_to='message/images', null=True, blank=True, verbose_name='上传图片')
    m_creating = models.DateField(auto_now_add=True, verbose_name='创建时间')
    user = models.ForeignKey(User, verbose_name='用户')
    post = models.ForeignKey(Post, verbose_name='帖子')

    def __str__(self):
        return "标题:%s" % self.mid

    class Meta:
        verbose_name_plural = '留言'


# 查看帖子
def post_show(pid):
    msgs = Message.objects.filter(post_id=pid)
    return msgs

# 保存留言
def save_msg(msg, pid, uid):
    Message.objects.create(m_msg=msg, user_id=uid, post_id=pid)
    msgs = Message.objects.filter(post_id=pid)
    post = Post.objects.get(pid=pid)
    return msgs, post

# 个人空间帖子查询分页
def space_paginator(uid, page, num):
    user = User.objects.filter(uid=uid)[0]
    posts = query_sql('select p.pid,p.p_title,p.p_creating,COUNT(post_id),p.user_id from home_message m RIGHT JOIN home_post p  on  m.post_id = p.pid  GROUP BY pid ORDER BY pid DESC')
    latepost = posts[0]
    space_posts = []
    for post in posts:
        if post[4] == uid:
            space_posts.append(post)
    paginator = Paginator(space_posts, num)

    try:
        t_pre_page = paginator.page(page)
    except PageNotAnInteger:
        t_pre_page = paginator.page(1)
    except EmptyPage:
        t_pre_page = paginator.page(paginator.num_pages)
    return user, t_pre_page, paginator, latepost

# 论坛帖子查询与分页
def post_paginator(num):
    # posts = Post.objects.all().order_by('-pid')
    posts = query_sql('SELECT * FROM '
                      '(select p.pid,p.p_title,p.p_creating,COUNT(post_id) from home_message m RIGHT JOIN home_post p  on  m.post_id = p.pid  GROUP BY pid ORDER BY pid DESC) as pm '
                      'LEFT JOIN (select p.pid,username,uid from home_user u right JOIN home_post p on p.user_id = u.uid) as pu on pu.pid=pm.pid ;')
    paginator = Paginator(posts, 15)

    try:
        t_pre_page = paginator.page(num)
    except PageNotAnInteger:
        t_pre_page = paginator.page(1)
    except EmptyPage:
        t_pre_page = paginator.page(paginator.num_pages)
    return t_pre_page, paginator

# 新闻查询
def newsShowPage(num):
    num = int(num)
    news = News.objects.all().order_by('-n_creating')
    paginator = Paginator(news, 9)
    if num < 1:
        num = 1
    if num > paginator.num_pages:
        num = paginator.num_pages
    start = int(((num - 1) / 10) * 10 + 1)
    end = start + 10
    if end > paginator.num_pages:
        end = paginator.num_pages + 1

    return paginator.page(num), range(start, end)

# 获取新闻内容
def newContShow(nid):
    new = News.objects.get(id=nid)
    return new

# 公告查询
def anmtShowPage(num):
    num = int(num)
    anmts = Announcement.objects.all().order_by('-a_creating')
    paginator = Paginator(anmts, 9)
    if num < 1:
        num = 1
    if num > paginator.num_pages:
        num = paginator.num_pages
    start = int(((num - 1) / 10) * 10 + 1)
    end = start + 10
    if end > paginator.num_pages:
        end = paginator.num_pages + 1

    return paginator.page(num), range(start, end)

# 获取公告内容
def anmtContShow(aid):
    anmt = Announcement.objects.get(id=aid)
    return anmt

# 删除帖子
def postDel(post_del_id):
    for id in post_del_id:
        pdel = Post.objects.filter(pid=id)
        pdel.delete()
# 删除留言
def msgDel(msg_del_id):
    mdel = Message.objects.filter(mid=msg_del_id)
    mdel.delete()

# 原生查询
def query_sql(sql):
    with connection.cursor() as c:
        c.execute(sql)
        data = c.fetchall()
        return data
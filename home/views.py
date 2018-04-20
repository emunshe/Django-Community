from datetime import time

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.views.decorators.csrf import csrf_protect

from home.models import *
import jsonpickle
from django.db.models import Q,F


# 登录
def login_view(request):
    user = session(request)
    if request.method == 'GET':
        if user:
            return render(request, 'login.html', {'uname': user.username, 'pwd': user.password})
        return render(request, 'login.html')
    uname = request.POST.get('username', '')
    pwd = request.POST.get('password', '')
    rmb = request.POST.get('rmb', '')

    # 登录不成功时返回原账户密码
    login_info = {}
    login_info['username'] = uname
    login_info['password'] = pwd

    # 获取用户信息对象
    users = User.objects.all()
    errors = {}
    response = HttpResponseRedirect('/user/')
    for user in users:
        if user.username == uname and user.password == pwd:
            if rmb == 'yes':
                request.session['userinfo'] = jsonpickle.dumps(user)
                return response
            else:
                request.session['userinfo'] = jsonpickle.dumps(user)
                request.session.set_expiry(0)       # 设置session过期时间（关闭浏览器）
                return response

        if user.username != uname and user.password == pwd:
            errors['log_username'] = '账户不正确'
        if user.username == uname and user.password != pwd:
            errors['log_password'] = '密码不正确'
    return render(request, 'login.html', {'errors': errors, 'login_info': login_info})

# 注册
def register_view(request):
    if request.method == 'GET':
        return render(request, 'login.html')

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    qq = request.POST.get('qq', '')
    mobile = request.POST.get('mobile', '')

    # 注册出错返回注册信息
    reg_info = {}
    reg_info['username'] = username
    reg_info['password'] = password
    reg_info['qq'] = qq
    reg_info['mobile'] = mobile

    errors = {}
    users = User.objects.all()
    for user in users:
        if user.username == username:
            errors['reg_username'] = '账户已存在'
        if user.qq == qq:
            errors['reg_qq'] = 'qq已被注册'
        if user.mobile == mobile:
            errors['reg_mobile'] = '手机已被注册'

    if errors:
        errors['defeat'] = '注册失败,请重新注册'
        return render(request, 'login.html', {'errors': errors, 'reg_info': reg_info})
    else:
        user = User.objects.create(username=username, password=password, qq=qq, mobile=mobile, head='heads/head.png')
        user.save()
        errors['secceed'] = '注册成功，请登录'
        return render(request, 'login.html', {'errors': errors})

# 通用函数，获取session并返回用户信息
def session(request):
    if request.session.get('userinfo'):
        user = jsonpickle.loads(request.session.get('userinfo'))
        user = User.objects.get(uid=user.uid)
        return user
    else:
        return None

# 首页
def index_view(request):
    return render(request, 'index.html')

# 新闻
def news_view(request):
    num = request.GET.get('page', 1)
    news_page, pages_num = newsShowPage(num)
    return render(request, 'news.html', {'news': news_page, 'pages_num': pages_num})

# 公告
def announcement_view(request):
    num = request.GET.get('page', 1)
    anmts_page, pages_num = anmtShowPage(num)
    return render(request, 'announcement.html', {'anmts': anmts_page, 'pages_num': pages_num})

# 论坛
def forum_view(request):
    user = session(request)
    if request.method == 'GET':
        num = int(request.GET.get('num', 1))
        msgs = request.GET.get('msg', '')
        t_pre_page,  paginator = post_paginator(num)

        totalPage = paginator.num_pages

        # 分页
        showpage = []
        if totalPage < 10:
            pages = totalPage
            for i in range(1, pages):
                showpage.append(i)
        elif num < 5:
            start = num
            if num == totalPage-5:
                end = totalPage
                for i in range(start, end):
                    showpage.append(i)
            else:
                end = num+5
                for i in range(start, end):
                    showpage.append(i)
        else:
            start = num-4
            if num > totalPage-5:
                end = totalPage+1
                for i in range(start, end):
                    showpage.append(i)
            else:
                end = num+5
                for i in range(start, end):
                    showpage.append(i)

        return render(request, 'forum.html', {'msgs': msgs, 'totalPage': totalPage, 't_pre_page': t_pre_page, 'showpage': showpage})
    if user:
        # POST请求
        title = request.POST.get('p_title', '')

        content = request.POST.get('p_content', '')

        Post.objects.create(p_title=title, p_content=content, user_id=user.uid)

        return HttpResponseRedirect('/forum/')
    else:
        return HttpResponseRedirect('/forum/?msg=error')



#用户中心
def user_view(request):
    return render(request, 'user.html')

# iform头像设置
def user_headSet(request):
    user = session(request)
    if request.method == 'GET':
        return render(request, 'head_from.html', {'user': user})
    if user:
        uhead = request.FILES.get('uhead', '')
        # 对上传的头像进行改名
        index = uhead.name.rfind('.')
        headName = uhead.name[0:index]
        head_name = headName.replace(headName, 'head')
        userhead = (str(user.username)+'_'+head_name+uhead.name[index:])
        uhead.name = userhead
        # 修改头像
        user.head = uhead
        user.save()
        msgs = {}
        msgs['msg'] = '修改成功,请刷新查看'
        return render(request, 'head_from.html', {'msgs': msgs})
    else:
        msgs = {'msg': '请先登录!'}
        return render(request, 'head_from.html', {'msgs': msgs})

# iform基本资料设置
def user_basicsInfoSet(request):
    user = session(request)
    if request.method == 'GET':
        return render(request, 'basicsInfo.html', {'user': user})
    if user:
        real_name = request.POST.get('real_name', '暂无')
        education = request.POST.get('education', '暂无')
        age = request.POST.get('age', '')
        if age == 'None':
            age = 1
        sex = request.POST.get('sex', '暂无')
        hobby = request.POST.get('hobby', '暂无')
        signature = request.POST.get('signature', '暂无')
        user.name = real_name
        user.education = education
        user.age = age
        user.sex = sex
        user.hobby = hobby
        user.signature = signature
        user.save()
        msgs = {'msg': '修改成功,请刷新查看'}
        return render(request, 'basicsInfo.html', {'msgs': msgs})
    else:
        msgs = {'msg': '请先登录!'}
        return render(request, 'basicsInfo.html', {'msgs': msgs})

# iform工作设置设置
def user_goingSet(request):
    user = session(request)
    if request.method == 'GET':
        return render(request, 'going.html', {'user': user})
    if user:
        company = request.POST.get('company', '暂无')
        profession = request.POST.get('profession', '暂无')
        position = request.POST.get('position', '暂无')
        income = request.POST.get('income', '暂无')
        user.company = company
        user.profession = profession
        user.position = position
        user.income = income
        user.save()
        msgs = {}
        msgs['msg'] = '修改成功,请刷新查看'
        return render(request, 'going.html', {'msgs': msgs})
    else:
        msgs = {'msg': '请先登录!'}
        return render(request, 'basicsInfo.html', {'msgs': msgs})

# iform个人资料设置
def user_perInfoSet(request):
    user = session(request)
    if request.method == 'GET':
        return render(request, 'perInfo.html', {'user': user})
    if user:
        email = request.POST.get('email', '暂无')
        address = request.POST.get('address', '暂无')
        # mobile = request.POST.get('mobile', '')
        # qq = request.POST.get('qq', '')
        user.email = email
        user.address = address
        # user.mobile = mobile
        # user.qq = qq
        user.save()
        msgs = {}
        msgs['msg'] = '修改成功,请刷新查看'
        return render(request, 'perInfo.html', {'msgs': msgs})
    else:
        msgs = {'msg': '请先登录!'}
        return render(request, 'basicsInfo.html', {'msgs': msgs})

# iform账户安全设置
def user_safeSet(request):
    user = session(request)
    if request.method == 'GET':
        return render(request, 'safe.html')
    if user:
        oldpwd = request.POST.get('oldpwd', '')
        newpwd1 = request.POST.get('newpwd1', '')
        newpwd2 = request.POST.get('newpwd2', '')
        msgs = {}
        if user.password != oldpwd:
            msgs['msg1'] = '密码不对，请重新输入'
            return render(request, 'safe.html', {'msgs': msgs})
        elif newpwd1 != newpwd2:
            msgs['msg2'] = '两次输入密码不同，请重新输入'
            return render(request, 'safe.html', {'msgs': msgs})
        else:
            user.password = newpwd2
            user.save()
            msgs = {}
            msgs['msg3'] = '密码修改成功，记到起哦！'
            return render(request, 'safe.html', {'msgs': msgs})
    else:
        msgs = {'msg': '请先登录!'}
        return render(request, 'basicsInfo.html', {'msgs': msgs})

# 浏览帖子视图
def post_view(request):
    user = session(request)
    if request.method == 'GET':
        if user:
            pid = request.GET.get('pid', '')
            if Post.objects.filter(Q(pid=pid) & Q(user_id=user.uid)):
                msg_del_id = request.GET.get('del', '')
                post = Post.objects.get(pid=pid)
                msgs = post_show(pid)
                if msg_del_id:
                    msgDel(msg_del_id)
                    return render(request, 'mypost.html', {'post': post, 'user': user, 'msgs': msgs})
                return render(request, 'mypost.html', {'post': post, 'user': user, 'msgs': msgs})
            else:
                post = Post.objects.get(pid=pid)
                msgs = post_show(pid)
                return render(request, 'post.html', {'user': user, 'post': post, 'msgs': msgs})
        else:
            pid = request.GET.get('pid', '')
            post = Post.objects.get(pid=pid)
            msgs = post_show(pid)
            return render(request, 'post.html', {'user': user, 'post': post, 'msgs': msgs})

    # POST请求
    if user:
        msg = request.POST.get('m_content', '')
        print(msg)
        pid = request.GET.get('pid', '')
        uid = user.uid
        msgs, post = save_msg(msg, pid, uid)
        infos = {'info': '回复成功!'}
        return render(request, 'post.html', {'user': user, 'post': post, 'infos': infos, 'msgs': msgs})
    else:
        return HttpResponseRedirect('/forum/post/?msg=error')

# 浏览空间视图
def space_view(request):
    user = session(request)
    if request.method == 'GET':
        page = int(request.GET.get('page', 1))
        uid = int(request.GET.get('uid', '0'))
        if user:
            if user.uid == uid or uid == 0:
                uid = user.uid
                now_user, t_pre_page, paginator, latepost = space_paginator(uid, page, 8)
                return render(request, 'mySpace.html',
                              {'latepost': latepost, 'paginator': paginator, 't_pre_page': t_pre_page,
                               'now_user': now_user})
            else:
                now_user, t_pre_page, paginator, latepost = space_paginator(uid, page, 8)
                return render(request, 'mySpace.html',
                              {'latepost': latepost, 'paginator': paginator, 't_pre_page': t_pre_page,
                               'now_user': now_user})
        else:
            if uid:
                now_user, t_pre_page, paginator, latepost = space_paginator(uid, page, 8)
                return render(request, 'mySpace.html',
                              {'latepost': latepost, 'paginator': paginator, 't_pre_page': t_pre_page,
                               'now_user': now_user})
            else:
                return HttpResponseRedirect('/login/')


    post_del_id = request.POST.getlist('postDel', '')
    postDel(post_del_id)
    return HttpResponseRedirect('/space/')

# 新闻主题内容
def newcont_view(request):
    if request.method == 'GET':
        nid = int(request.GET.get("nid", ''))
        new = newContShow(nid)
        return render(request, 'newcont.html', {'new': new})

# 公告主题内容
def anmtcont_view(request):
    if request.method == 'GET':
        aid = int(request.GET.get('aid', ''))
        anmt = anmtContShow(aid)
        return render(request, 'anmtcont.html', {'anmt': anmt})

# 个人帖子
def mypost_view(request):
    msg_del_id = request.GET.get('del', '')
    msgDel(msg_del_id)
    return HttpResponseRedirect('/post/')



# @csrf_protect
# def upload_image(request):
#     if request.method == 'POST':
#         callback = request.GET.get('CKEditorFuncNum')
#         print('-----------------')
#         try:
#             path = "upload/" + time.strftime("%Y%m%d%H%M%S", time.localtime()) #< ---还有这里，这里path修改你要上传的路径，我记得我是修改了的，这样就上传到了upload文件夹
#             f = request.FILES["upload"]
#             file_name = path + "_" + f.name
#             des_origin_f = open(file_name, "wb+")
#             for chunk in f:                 #<--  # 我修改的是这里，因为python后期的版本放弃了chunk函数，直接遍历类文件类型就可以生成迭代器了。
#                 des_origin_f.write(chunk)
#             des_origin_f.close()
#         except Exception as e:
#             print(e)
#
#         res = r"<script>window.parent.CKEDITOR.tools.callFunction(" + callback + ",‘/" + file_name + "‘, ‘‘);</script>"
#         return HttpResponse(res)
#
#     else:
#         raise Http404()
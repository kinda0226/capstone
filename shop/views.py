#coding: utf-8

from __future__ import unicode_literals

from django.shortcuts import render, redirect, HttpResponse#, error_prompt("404")
from django.db.models import Q
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt

from models import *
from views_common import *

import math, random, base64
from hashlib import md5, sha1


def index(request):
    return mrender(request, 'index.html', {
        'shops': getPosts(postType='product-list', column_id=0, order='?')[:12],
    })


def post(request, id):
    p = Post.objects.filter(id=id).first()
    if not p:
        return error_prompt("404")

    column = p if p.column_id == 0 or p.postType.endswith('-list') else Post.objects.filter(id=p.column_id).first()
    if not column:
        return error_prompt("404")

    cid = column.id if column.column_id == 0 else column.column_id

    leftnav = []
    items = []
    tags = []

    leftnav = getPosts(column_id=cid, postType='product-list')

    if column.id == p.id:
        if column.postType.endswith('-list'):
            items = getItems(column.id)

    if 'viewed{}'.format(id) not in request.COOKIES:
        #print 'viewed'
        p.views += 1
        p.save()

    tmpl = p.postType.replace('-', '_') + '.html'
    from capstone import settings
    import os
    if not os.path.exists(settings.BASE_DIR + '/templates/' + tmpl):
        return error_prompt('该页面无法访问')

    resp = mrender(request, tmpl, {
        'current': cid,
        'post': p,
        'column': column,
        'uppercolumn': Post.objects.filter(id=cid).first(),
        'leftnav': leftnav,
        'tags': tags,
        'items': items,
    })

    resp.set_cookie(key='viewed{}'.format(id), value='1')

    return resp


def register(request):
    if 'step' not in request.POST:
        return mrender(request, 'register.html', { 'step': 1 })
    elif 'validate' in request.POST:
        k = request.POST['validate']
        v = request.POST['value']
        if k == 'verifyCode' and v == '__apply__':
            recv = request.POST['recv']
            request.session['sms_code'] = __generate_sms_code(recv)
            return HttpResponse('OK')
        elif '_' in k or SiteUser.objects.filter(**{k: v}).exists():
            return HttpResponse('FAIL')
        return HttpResponse('OK')
    elif request.session.get('captcha', '') != '__pass__':
        return error_prompt('验证码错误')

    step = int(request.POST['step'])

    if step == 2:
        if '_' in request.POST['verifyCode'] or request.POST['verifyCode'] != request.session['sms_code']:
            request.session['sms_code'] = '______'
            return error_prompt('短信验证码错误')

        u = SiteUser()
        for _, v in request.POST.items():
            if hasattr(u, _):
                setattr(u, _, v)
        u.password = SiteUser.encryptPassword(u.phoneNumber, u.password)
        u.save()
        request.session['user_id'] = u.id

    return mrender(request, 'register.html', {'step': step})


def login(request):
    message = ''

    if request.siteUser:
        return redirect('/')

    if 'username' in request.POST:
        # try manual login
        request.siteUser, request.account = SiteUser.login(request.POST['username'], request.POST['password'])
        if not request.siteUser:
            message = '错误的用户名密码'
        else:
            request.session['user_id'] = request.siteUser.id
            resp = redirect('/')
            return resp

    return mrender(request, 'login.html', {'message': message})


def logout(request):
    if not request.siteUser: return redirect('/login')
    del request.session['user_id']

    return redirect('/?logout=1')


def profile(request, uname=''):
    if not request.siteUser: return redirect('/login')

    if uname:
        user = SiteUser.objects.filter(username=uname).first()
    else:
        uname = request.siteUser.username
        user = request.siteUser

    message = ''

    section = request.GET.get('section', 'orders')
    edit = True
    navs = [
            {
                'id': 'security',
                'active': section == 'security',
                'title': 'Security',
                'url': '?section=security'
            }, {
                'id': 'orders',
                'active': section == 'orders',
                'title': 'Orders',
                'url': '?section=orders'
            }
        ]

    if len([x for x in navs if x['active']]) == 0 or section not in [_['id'] for _ in navs]:
        navs[1]['active'] = True
        section = 'orders'

    if request.method == "POST":
        user = request.siteUser
        if section == 'security':
            if request.POST.get('newpassword'):
                if user.changePassword(request.POST['password'], request.POST['newpassword']):
                    logout(request)
                    return redirect('/login')
                else:
                    message = 'Wrong old password'

    items = []
    if section == 'orders':
        user = request.siteUser
        items = SiteUserOrder.objects.filter(siteUser=user)

    return mrender(request, 'profile.html', {
        'section': section,
        'user': user,
        'message': message,
        'uppercolumn': {'title': 'Profile'},
        'leftnav': navs,
        'edit': edit,
        'fieldstype': {
        },
        'fieldsname': FIELDS_NAME if edit else {},
        'column': {
            'id': section,
            'title': [_ for _ in navs if _['active']][0]['title']
        },
        'items': items
    })


def avatar(request, id):
    from capstone import settings
    import os
    avt = '/uploads/avatars/{}.jpg'.format(id)
    if os.path.exists(settings.STATICFILES_DIRS[0] + avt):
        return redirect('/static/' + avt)
    return redirect('/static/images/avatar.png')


def search(request):
    if not request.siteUser: return redirect('/login')
    q = Q(title='')
    kws = request.GET.get('q', '')
    if kws:
        q = Q()
        kws = kws.split(' ')
        for kw in kws:
            if not kw: continue
            q &= Q(title__contains=kw) | Q(content__contains=kw) | Q(id__in=PostMeta.objects.filter(value__contains=kw).values('post_id'))
    return mrender(request, 'search.html', {
        'uppercolumn': {
            'title': 'Search'
        },
        'column': {
            'title': 'Search'
        },
        'items': Post.objects.filter(q, postType='product')
    })


def buy(request, product):
    if not request.siteUser: return redirect('/login')

    product = Post.objects.get(id=int(product))
    subtotal = product.price * int(request.POST['count'])

    if request.POST.get('confirm'):
        o = SiteUserOrder(
            siteUser=request.siteUser,
            pubdate=datetime.datetime.now()
        )
        o.save()
        oi = SiteUserOrderItem(
            order=o,
            product=product,
            count=int(request.POST['count']),
            subtotal=subtotal
        )
        oi.save()
        return mrender(request, 'buy.html', {
            'message': 'Please remember your order number: #{}'.format(o.id)
        })

    return mrender(request, 'buy.html', {
        'product': product,
        'subtotal': subtotal
    })


### admin views

from views_admin import admin_router

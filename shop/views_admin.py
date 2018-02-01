#coding: utf-8

from __future__ import unicode_literals

from django.shortcuts import render, redirect, HttpResponse, Http404
from django.http.response import JsonResponse
from django.db import transaction
from django.db.models import Q, QuerySet, F
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from models import *
from views_common import *

import math, random

POST_TYPES = {
            Post.PT_product_list: 'Category/Shop',
            Post.PT_product: 'Product'
        }


def __fields_name(model):
    return dict([
        (_.name, _.verbose_name or _.name)
        for _ in model._meta.fields
    ])


def __fields_type(model):
    return dict([
        (_.name, {
            'BooleanField': bool,
        }.get(_.get_internal_type()))
        for _ in model._meta.fields
    ])


def admin_router(request, func):
    if not request.siteUser or request.siteUser.authority == 0:
        return render(request, 'admin_login.html')

    funcs = globals()
    params = func.split('/')
    func = params[0]
    params = params[1:]

    if not func or func not in funcs: func = 'dashboard'

    vm = funcs[func](request, *params) or {}
    if isinstance(vm, HttpResponse): return vm

    model = Post
    if 'item' in vm and isinstance(vm['item'], models.Model):
        model = type(vm['item'])

    if model:
        vm['fields_name'] = __fields_name(model)
        vm['fields_type'] = __fields_type(model)

    vm['myshops'] = Post.objects.filter(column_id=0, owner_id=request.siteUser.id)
    vm['myorders'] = orders(request, False)['items'].count()

    return mrender(request, 'admin_{}.html'.format(func), vm)


def dashboard(request):
    from django.db.models import Sum

    _default_image = 'data:image/gif;base64,R0lGODlhAQABAIABAAJ12AAAACwAAAAAAQABAAACAkQBADs='
    stats_tables = {
        'Total Pages': ('files-o', Post.objects.all()                                ),
        'Total Users': ('users', SiteUser.objects.all()                            ),
        'Orders': ('star', SiteUserOrder.objects.all()                         ),
        'Order Items': ('eye', SiteUserOrderItem.objects.aggregate(Sum('count'))['count__sum']),
    }

    return {
        'stats': [
            {
                'name': name,
                'number': val.count() if isinstance(val, QuerySet) else len(val) if isinstance(val, list) else val,
                'image': _default_image,
                'icon': icon
            }
            for name, (icon, val) in stats_tables.items()
        ],
        'items': list(Post.objects.order_by('-pubdate')[:10])
    }


def help(request):
    pass


def orders(request, showAll=True):
    items = SiteUserOrder.objects.filter(siteuserorderitem__product__owner=request.siteUser)
    deal = request.GET.get('deal')
    if deal:
        items.filter(id=deal).update(dealt=True)
        return redirect('/admin/orders')

    if not showAll:
        items = items.filter(dealt=False)
    return {
        'items': items.distinct()
    }


def users(request):
    if request.siteUser.authority <= 1:
        return redirect('/admin/')

    oper_hint = ''

    if request.method == 'POST':
        oper_hint = 'No such operation.'

        if 'action' in request.POST and 'ids' in request.POST:
            ids = [int(_) for _ in request.POST['ids'].split(',') if _]

            action = request.POST['action']
            if action == 'reset_password':
                SiteUser.objects.filter(id__in=ids).update(password='')
                oper_hint = 'Success'

    return {
        'items': SiteUser.objects.all(),
        'oper_hint': oper_hint
    }


def basic(request):
    if request.method == 'POST':
        d = SiteBasic.getDict()

        for k, v in request.POST.items():
            if k not in d: continue
            b = SiteBasic.objects.get(settingName=k)
            if b.settingValue.startswith('json:'):
                import json
                try:
                    assert v.startswith('json:')
                    j_ = json.loads(v[5:])
                except:
                    return error_prompt('Malformatted data')

            b.settingValue = v
            b.save()

        SiteBasic.getDict(True)

    return {
        'items': list(SiteBasic.objects.all().order_by('settingDescription'))
    }


def column(request, id=0):
    id = int(id)
    col = Post.objects.get(id=id) if id > 0 else {'title': 'Shop/Category'}
    return {
        'column': col,
        'items': Post.objects.filter(column_id=id),
        'new': "location = '/admin/post?column_id={}#type={}';".format(
            id,
            'product-list' if isinstance(col, dict) or col.column_id == 0 else 'product'
        )
    }


def post(request, id=0):
    if id > 0:
        p = Post.objects.get(id=id)
    else:
        p = Post()

    if request.method == 'POST':
        p.postType = request.POST['type']
        for _, v in request.POST.items():
            k = _
            if _ == 'pubdatestr': k = 'pubdate'
            if hasattr(p, k):
                print k.encode('utf-8'), v.encode('utf-8')
                setattr(p, k, v)
        p.save()
            
        SiteBasic.getDict(True)
            
        return redirect('/admin/post/{}'.format(p.id))

    return {
        'item': p,
        'postTypes': POST_TYPES,
        'usergroups': dict([('', '')] + [(_['name'], _['name']) for _ in SiteBasic.getDict()['userGroups']]),
        # 'fields_type': __fields_type(Post),
        # 'fields_name': __fields_name(Post),
        'users': None if request.siteUser.authority <= 1 else SiteUser.objects.filter(authority__gt=0)
    }


def uploadlist(request):
    from capstone import settings
    import os
    return JsonResponse({'results': [
        '/static/uploads/' + _
        for _ in os.listdir(settings.STATICFILES_DIRS[0] + '/uploads/')
        if not _.startswith('.') and _[_.rfind('.') + 1:].lower() in 'png,jpg,jpeg,gif'
    ]})


def uploadfile(request):
    fname = write_all_files(request)
    if len(fname) == 0: fname = None
    else: fname = '/static' + fname[0]

    if 'tinymce' in request.POST or 'tinymce' in request.GET:
        return HttpResponse("<script>top.$('.mce-btn.mce-open').parent().find('.mce-textbox').val('{}').closest('.mce-window').find('.mce-primary').click();</script>".format(fname))
    return JsonResponse({'url': fname, 'location': fname})


def edit(request): # notice: this is for ajax use only
    id, source = request.POST['id'], request.POST['source']
    if '/ads' in source: table = Advertisement
    elif '/users' in source: table = SiteUser
    elif '/column' in source: table = Post
    else: return JsonResponse({'error': 'Edit not allowed.'})
    
    p = table.objects.get(id=id)
    oPostType = p.postType if table is Post else ''
    for _, v in request.POST.items():
        if _ in ['id', 'table', 'password', 'securityQuestion', 'securityAnswer']: continue
        k = _
        if k == 'pubdatestr': k = 'pubdate'
        if k == 'birthday' and not v:
            v = None
        setattr(p, k, v)
    p.save()

    SiteBasic.getDict(True)
    return JsonResponse({'status': 'OK'})


def delete(request):
    ref = request.POST['ref']
    ids = request.POST['ids']
    ids = [int(_) for _ in ids.split(',')]
    table = None
    if '/column' in ref:
        table = Post
        if Post.objects.filter(column_id__in=ids).exists():
            return JsonResponse({'error': 'Delete or transfer the products belonging to this list first.'})
    else:
        return JsonResponse({'error': 'Deletion not allowed.'})

    table.objects.filter(id__in=ids).delete()
    return JsonResponse({'status': 'OK'})


def transfer_col(request):
    try:
        cid = int(request.POST['col_id'])
        assert cid > 0
        ids = request.POST['ids']
        ids = [int(_) for _ in ids.split(',')]
    except:
        return JsonResponse({'error': 'Error'})

    Post.objects.filter(id__in=ids).update(column_id=cid)
    return JsonResponse({'status': 'OK'})


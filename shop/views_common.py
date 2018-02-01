#coding: utf-8

from __future__ import unicode_literals

from django.shortcuts import render, redirect, HttpResponse, Http404
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

from models import *
from views_common import *

import math, random, time


FIELDS_NAME = {
        }

def getPosts(order='order,-pubdate', **kwfilters):
    return Post.objects.filter(**kwfilters).exclude(postType='proposed').order_by(*order.split(','))

def getItems(colid, order='order,-pubdate'):
    i = Post.objects.filter(postType=Post.PT_product).exclude(postType='proposed')
    q = Q(column_id=colid)
    for c in SiteBasic.getDict()['childrenColumns'].get(colid, ''):
        q |= Q(column_id=c.id)
    return i.filter(q).order_by(*order.split(','))

def paginate(request, items):
    if isinstance(items, list): return items, {}

    count = int(request.GET.get('count', 15))
    total = len(items) if isinstance(items, list) else items.count()
    totalPages = int(math.ceil(float(total) / count))
    currentPage = int(request.GET.get('page', 0))
    order = request.GET.get('order', 'desc')

    by = request.GET.get('by', '')
    # if by not in ['', 'pubdate', 'views', 'favs']: by = ''
    if not by:
        if items.model is Post:
            by = 'order,-pubdate'
        else:
            by = 'id'
    if order == 'desc' and ',' not in by:
        by = '-' + by

    items = items.order_by(*by.split(','))

    items = items[currentPage*count:(currentPage+1)*count]


    pagination = {
        'pages': zip(range(max(0, currentPage-2), min(currentPage+3, totalPages)), range(1+max(0, currentPage-2), 1+min(currentPage+3, totalPages))),
        'other_params': '&'.join(['{}={}'.format(_, v) for _, v in request.GET.items() if _ != 'page']),
        'current_page': currentPage,
        'total': total,
    }

    return items, pagination

def mrender(request, template, vm):
    vm['basic'] = SiteBasic.getDict()
    vm['siteUser'] = request.siteUser
    if 'items' in vm:
        vm['items'], vm['pagination'] = paginate(request, vm['items'])
    if 'user' in vm:
        u = {
            'id': vm['user'].id,
            'username': vm['user'].username,
            # 'userGroup': vm['user'].userGroup,
            # 'showDetails': vm['user'].showDetails
        }
        for _ in FIELDS_NAME:
            u[_] = getattr(vm['user'], _) or ''

        vm['user'] = u

    return render(request, template, vm)

def success_prompt(redir='javascript:history.go(-1)'):
    return redirect('/static/success.html?redir={}'.format(redir))

def error_prompt(message=''):
    return redirect('/static/error.html?q={}'.format(message))

def write_all_files(request, filename='', return_orig_name=False):
    from capstone import settings
    fnames = []
    for _ in request.FILES:
        forig = request.FILES[_].name
        ext = forig[forig.rfind('.'):]
        fname = '/uploads/' + ((str(int(time.time() * 1000000)) + ext) if not filename else filename)
        with open(settings.STATICFILES_DIRS[0] + fname, 'wb') as f:
            f.write(request.FILES[_].read())
        if return_orig_name:
            fnames.append((fname, forig[:forig.rfind('.')]))
        else:
            fnames.append(fname)
    return fnames
#coding: utf-8

from __future__ import unicode_literals

from django import template
from django.db import models
from django.utils.safestring import mark_safe

from shop.models import Post
import datetime

register = template.Library()

@register.filter
def keyvalue(o, key):
    if o is None: return ''
    if isinstance(o, dict):
        d = o.get(key)
    else:
        d = getattr(o, key)
    if d is None or d == 'None':
        return ''
    else:
        return d

@register.filter
def islist(o, key):
    return isinstance(o[key], list)

@register.filter
def items(o):
    filtered = [_.strip() for _ in '''
                notifications receiver sender verifyCode 
                meta productMeta PT_article_forum_list PT_article_list PT_article_page PT_product PT_product_list DoesNotExist objects MultipleObjectsReturned encryptPassword accessToken changePassword check clean clean_fields date_error_message delete from_db full_clean get_deferred_fields id login password phoneNumber pk prepare_database_save refresh_from_db save save_base securityAnswer securityQuestion serializable_value siteuseraccount siteuseraccountlog_set siteuserfav_set unique_error_message validate_unique
                '''.lower().strip().split(' ')
                if _.strip()]

    if o:
        if isinstance(o, dict):
            for _ in o.items():
                yield _
        elif isinstance(o, models.Model):
            for _ in o._meta.fields:
                k, v = _.name, getattr(o, _.name)
                if k.lower() in filtered: continue
                if isinstance(v, models.Model):
                    if not isinstance(v, Post):
                        continue
                elif isinstance(v, (datetime.datetime, datetime.date)):
                    v = v.strftime('%Y-%m-%d %H:%M:%S')
                yield k, v
        else:
            for _ in dir(o):
                if '_' in _ or _.lower() in filtered: continue
                v = getattr(o, _)
                if not isinstance(v, (str, unicode, int, bool)): continue
                # try:
                yield _, v
                # except: pass

@register.filter
def keys(o):
    if isinstance(o, dict):
        return o.keys()
    elif o:
        return dir(o)
    else:
        return []

@register.filter
def add(v, i):
    return int(v)+i

@register.filter
def sub(v, i):
    return int(v)-i

@register.simple_tag
def ad(title, layout, p1, p2=0):
    return ''

@register.simple_tag
def uname(uid):
    from shop.models import SiteUser
    return SiteUser.objects.get(id=uid).username

@register.simple_tag
def ugroup(uid):
    return ''

@register.simple_tag
def render_value(dtype, dval, name=""):
    name_id = 'id="ux_{name}" name="{name}"'.format(name=name) if name else ''

    if dtype is bool or type(dtype) is bool:
        name_id2 = 'id="ux_chk_{name}" onclick="ux_{name}.value=this.checked?1:0;"'.format(name=name) if name else ''
        h = '<input type="hidden" value="{val}" {name_id}><input type="checkbox" value="1" {name_id2} {checked}>'.format(
            name_id=name_id, name_id2=name_id2, val=1 if dval else 0, checked='checked="checked"' if dval else '')
        return mark_safe(h)
    elif isinstance(dtype, (dict, list)):
        types = list(dtype.items() if isinstance(dtype, dict) else enumerate(dtype))
        if isinstance(dtype, dict) and dval not in dtype:
            dval, __ = types[-1]
        return mark_safe('<select {}>'.format(name_id) +
                         ''.join([
                             '<option value="{val}" {selected}>{show}</option>'.format(
                                 selected='selected' if val == dval else '',
                                 show=show,
                                 val=val
                             )
                         for val, show in types
                         ]) +
                         '</select>')
    elif isinstance(dval, Post):
        return mark_safe('<a href="/view/{}" target="_blank">{}</a>'.format(dval.id, dval.title))
    else:
        return '' if dval is None else dval

@register.filter
def fromjson(o):
    import json
    return json.loads(o)

@register.filter
def jsonify(o):
    import json
    return json.dumps(o)
    
@register.filter
def concat(a, b):
    return '{}{}'.format(a, b)
    
@register.filter
def isnumeric(a):
    return a.isnumeric()
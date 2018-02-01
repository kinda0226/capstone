#coding: utf-8

from __future__ import unicode_literals

from django.db import models
from django.contrib import admin
import datetime
from django.db.models import Q, Count

from hashlib import md5, sha1

import re, json, base64


class SiteBasic(models.Model):
    settingName = models.CharField(max_length=150, unique=True)
    settingValue = models.TextField()
    settingDescription = models.CharField(max_length=150)
    settingValueType = models.CharField(max_length=150)

    minimalKeys = ['']
    _dict = None

    @staticmethod
    def getDict(refresh=False):
        if not SiteBasic._dict or refresh:

            d = {}

            for _ in SiteBasic.objects.all():
                s = _.settingValue
                d[_.settingName] = s

            d['columns'] = Post.objects.filter(column_id=0)
            d['childrenColumns'] = dict([
                (_.id, Post.objects.filter(column_id=_.id, postType__endswith='-list').order_by('order'))
                for _ in d['columns']
            ])

            if not d.get('userGroups'):
                d['userGroups'] = [{'name': '', 'style': ''}]

            SiteBasic._dict = d

        return SiteBasic._dict

    @staticmethod
    def putDict(d):
        SiteBasic._dict = None
        for _, v in d.items():
            if _ == 'key': continue
            s = v
            k = SiteBasic.objects.filter(settingName=_).first()
            if not k: k = SiteBasic(settingName=_, settingValue=s)
            else: k.settingValue = s
            k.save()


class SiteUser(models.Model):
    username = models.CharField(max_length=50, unique=True, verbose_name="Username")
    password = models.CharField(max_length=150, null=False, verbose_name="Password")
    authority = models.IntegerField(default=False, verbose_name="Authority")

    @staticmethod
    def encryptPassword(username, plaintext):
        if plaintext == '': return ''
        salt = sha1(username).hexdigest()
        return sha1(salt + plaintext).hexdigest()

    @staticmethod
    def login(uname, password):
        ut = SiteUser.objects.filter(username=uname).first()
        if not ut:
            return None, None

        if ut.password == password:
            return ut, None

        return None, None

    def changePassword(self, oldpassword, newpassword):
        if SiteUser.encryptPassword(self.username, oldpassword) == self.password:
            self.password = SiteUser.encryptPassword(self.username, newpassword)
            return True

        return False


class Post(models.Model):
    title = models.CharField(max_length=150, blank=False, verbose_name="Title")
    pubdate = models.DateTimeField(auto_now=True, verbose_name="Date")
    content = models.TextField(default='', verbose_name="Content")
    abstract = models.TextField(default='', verbose_name="Abstract")
    postType = models.CharField(max_length=50, db_index=True, verbose_name="Page Type")
    column_id = models.IntegerField(default=0, verbose_name="Shop ID")
    image = models.CharField(max_length=150, blank=False, default='', verbose_name="Image")
    order = models.IntegerField(default=0, verbose_name="Order")
    showInIndex = models.BooleanField(default=False, verbose_name="Featured")
    views = models.IntegerField(default=0, verbose_name="Views")
    price = models.FloatField(default=0, verbose_name="Price")
    owner = models.ForeignKey(SiteUser, verbose_name="Owner")

    PT_product_list = 'product-list'
    PT_product = 'product'

    @property
    def pubdatestr(self):
        if self.pubdate:
            return self.pubdate.strftime("%Y-%m-%d %H:%M:%S")

    @pubdatestr.setter
    def pubdatestr(self, newval):
        self.pubdate = newval


class SiteUserOrder(models.Model):
    pubdate = models.DateTimeField(auto_now=True, verbose_name="Date")
    siteUser = models.ForeignKey(SiteUser, verbose_name="User")
    dealt = models.BooleanField(default=False, verbose_name="Dealt")

    @property
    def pubdatestr(self):
        return self.pubdate.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def items(self):
        return SiteUserOrderItem.objects.filter(order=self)

    @property
    def total(self):
        from django.db.models import Sum
        return self.items.aggregate(Sum('subtotal'))['subtotal__sum']


class SiteUserOrderItem(models.Model):
    product = models.ForeignKey(Post, null=True, verbose_name="Product")
    count = models.IntegerField(default=1, verbose_name="Count")
    subtotal = models.FloatField(default=0, verbose_name="Subtotal")
    order = models.ForeignKey(SiteUserOrder, verbose_name="Order")

    @property
    def detail(self):
        return '{} x{}\n  Subtotal: ${}'.format(self.product.title, self.count, self.subtotal)

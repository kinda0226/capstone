# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-11-16 17:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_auto_20171116_1737'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitebasic',
            name='settingDescription',
            field=models.CharField(max_length=150, verbose_name='\u8bf4\u660e'),
        ),
        migrations.AlterField(
            model_name='sitebasic',
            name='settingValueType',
            field=models.CharField(max_length=150, verbose_name='\u6570\u636e\u7c7b\u578b'),
        ),
    ]

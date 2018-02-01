# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-11-16 07:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_siteuser_showdetails'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='siteuseraccount',
            name='id',
        ),
        migrations.AddField(
            model_name='post',
            name='allowComments',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='siteuseraccountlog',
            name='ip',
            field=models.CharField(default='.', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='siteuseraccount',
            name='siteUser',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='shop.SiteUser'),
        ),
    ]

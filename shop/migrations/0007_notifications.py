# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-11-16 08:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_auto_20171116_0725'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pubdate', models.DateTimeField(auto_created=True)),
                ('content', models.CharField(max_length=500)),
                ('read', models.BooleanField(default=False)),
                ('sender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sender', to='shop.SiteUser')),
                ('siteUser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to='shop.SiteUser')),
            ],
        ),
    ]

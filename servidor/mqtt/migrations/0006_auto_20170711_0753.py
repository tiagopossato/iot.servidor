# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-11 10:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mqtt', '0005_auto_20170711_0752'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='publickey',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='Chave pública'),
        ),
    ]

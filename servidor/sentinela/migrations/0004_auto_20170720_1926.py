# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-20 22:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sentinela', '0003_auto_20170720_1903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='central',
            name='id',
            field=models.UUIDField(default='51ff7375ea8b4ee4918ecbae73cd1191', primary_key=True, serialize=False, verbose_name='Identificador'),
        ),
    ]

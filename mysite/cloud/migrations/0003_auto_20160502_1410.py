# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-02 06:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cloud', '0002_auto_20160502_1408'),
    ]

    operations = [
        migrations.AlterField(
            model_name='threshold',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]

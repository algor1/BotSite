# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-30 13:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_botuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='myprofile',
            name='wallet',
            field=models.FloatField(blank=True, default=0),
        ),
    ]

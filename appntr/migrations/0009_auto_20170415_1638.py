# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-15 16:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('appntr', '0008_auto_20170412_1950'),
    ]

    operations = [
        migrations.AddField(
            model_name='invite',
            name='added_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='invite',
            name='changed_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='invite',
            name='reminded_at',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]

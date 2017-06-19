# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-19 10:52
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('appntr', '0002_auto_20170618_1123'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('can_lead', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='config', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

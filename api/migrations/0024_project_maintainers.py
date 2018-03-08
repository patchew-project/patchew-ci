# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-08 08:15
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0023_auto_20180308_0810'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='maintainers',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
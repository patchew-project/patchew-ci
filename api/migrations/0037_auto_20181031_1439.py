# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-31 14:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0036_populate_message_tags'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='message',
            index_together=set([('is_series_head', 'project', 'date'), ('is_series_head', 'date'), ('is_series_head', 'last_reply_date'), ('is_series_head', 'project', 'last_reply_date')]),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-04 06:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_populate_last_comment_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='receivers',
            new_name='recipients',
        ),
    ]
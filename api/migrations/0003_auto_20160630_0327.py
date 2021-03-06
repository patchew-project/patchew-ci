# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-30 03:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20160630_0243'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectProperty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=1024, unique=True)),
                ('value', models.TextField(blank=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Project')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='projectproperty',
            unique_together=set([('project', 'name')]),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-31 05:44
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.encoder
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_auto_20180426_0829'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_xz', models.BinaryField()),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('last_update', models.DateTimeField()),
                ('status', models.CharField(max_length=7, validators=[django.core.validators.RegexValidator(code='invalid', message='status must be one of pending, success, failure, running', regex='pending|success|failure|running')])),
                ('data', jsonfield.fields.JSONField(dump_kwargs={'cls': jsonfield.encoder.JSONEncoder, 'separators': (',', ':')}, load_kwargs={})),
            ],
        ),
        migrations.CreateModel(
            name='MessageResult',
            fields=[
                ('result_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.Result')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='api.Message')),
            ],
            bases=('api.result',),
        ),
        migrations.CreateModel(
            name='ProjectResult',
            fields=[
                ('result_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.Result')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='api.Project')),
            ],
            bases=('api.result',),
        ),
        migrations.AddField(
            model_name='result',
            name='log_entry',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.LogEntry'),
        ),
        migrations.AlterIndexTogether(
            name='result',
            index_together=set([('status', 'name')]),
        ),
    ]

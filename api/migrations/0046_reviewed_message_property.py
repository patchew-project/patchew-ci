# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations

def delete_reviewed(apps, schema_editor):
    MessageProperty = apps.get_model('api', 'MessageProperty')
    MessageProperty.objects.filter(name='reviewed').delete()

def add_reviewed(apps, schema_editor):
    Message = apps.get_model('api', 'Message')
    MessageProperty = apps.get_model('api', 'MessageProperty')
    props = MessageProperty.objects.filter(name='reviewers')
    for p in props:
        if p.value:
            new_prop = MessageProperty(message=p.message, name='reviewed', value=True)
            new_prop.save()

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0045_message_maintainers'),
    ]

    operations = [
        migrations.RunPython(delete_reviewed,
                             reverse_code=add_reviewed),
    ]

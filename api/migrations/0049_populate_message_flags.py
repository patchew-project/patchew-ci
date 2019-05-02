# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations

from api.search import FLAG_TESTED, FLAG_REVIEWED, FLAG_OBSOLETE

def property_to_flags(apps, schema_editor):
    MessageProperty = apps.get_model('api', 'MessageProperty')
    for p in MessageProperty.objects.filter(name='obsoleted-by'):
        p.message.flags += FLAG_OBSOLETE
        p.message.save()
    for p in MessageProperty.objects.filter(name='reviewed'):
        p.message.flags += FLAG_REVIEWED
        p.message.save()
    for p in MessageProperty.objects.filter(name='testing.done'):
        p.message.flags += FLAG_TESTED
        p.message.save()
    MessageProperty.objects.filter(name='reviewed').delete()
    MessageProperty.objects.filter(name='testing.done').delete()

def flags_to_property(apps, schema_editor):
    Message = apps.get_model('api', 'Message')
    for m in Message.objects.exclude(flags=''):
        if '[reviewed]' in m.flags:
            new_prop = MessageProperty(message=p.message, name='reviewed', value=True)
            new_prop.save()
        if FLAG_TESTED in m.flags:
            new_prop = MessageProperty(message=p.message, name='testing.done', value=True)
            new_prop.save()

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0048_message_flags'),
    ]

    operations = [
        migrations.RunPython(property_to_flags,
                             reverse_code=flags_to_property),
    ]

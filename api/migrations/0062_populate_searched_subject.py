# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.db.models import Q

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0061_message_searched_subject'),
    ]

    operations = [
        migrations.RunSQL(
            'update api_message set searched_subject = replace(replace(subject, ".", " "), "/", " ") where subject like "%.%" or subject like "%/%"'
        )

    ]

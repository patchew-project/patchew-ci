# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from api.migrations import PostgresOnlyMigration

class Migration(PostgresOnlyMigration):

    dependencies = [
        ('api', '0062_populate_searched_subject'),
    ]

    operations = [
        migrations.RunSQL("create index api_message_searched_subject_gin on api_message using gin(to_tsvector('english', searched_subject::text));",
                          "drop index api_message_searched_subject_gin"),
        migrations.RunSQL("drop index api_message_subject_gin",
                          "create index api_message_subject_gin on api_message using gin(to_tsvector('english', subject::text));"),
    ]

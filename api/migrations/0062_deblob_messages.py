#! /usr/bin/env python3
from __future__ import unicode_literals

from django.db import migrations, transaction

from . import load_blob, delete_blob

def deblob_messages(apps, schema_editor):
    Project = apps.get_model("api", "Project")
    Message = apps.get_model("api", "Message")
    done = 0
    for p in Project.objects.all():
        start = Message.objects.filter(project=p, mbox_bytes=None).order_by("-date").first()
        while start:
            first_date = start.date
            print(done, p, first_date)
            with transaction.atomic():
                previously = done
                q = Message.objects.filter(project=p, date__lte=first_date, mbox_bytes=None).order_by("-date")[:1000]
                for msg in q:
                    try:
                        mbox_decoded = load_blob(msg.message_id)
                        msg.mbox_bytes = mbox_decoded.encode("utf-8")
                        msg.save()
                        delete_blob(msg.message_id)
                        done += 1
                    except Exception as e:
                        print(msg, type(e))
                    start = msg
                if done == previously and start.date == first_date:
                    start = None

class Migration(migrations.Migration):

    dependencies = [("api", "0061_message_mbox_bytes")]

    operations = [
        migrations.RunPython(deblob_messages, reverse_code=migrations.RunPython.noop)
    ]


# Generated by Django 3.1.3 on 2021-10-13 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0060_auto_20210106_1120'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='gen',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
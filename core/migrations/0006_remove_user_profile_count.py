# Generated by Django 2.1.5 on 2021-07-25 20:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20210725_2317'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='profile_count',
        ),
    ]

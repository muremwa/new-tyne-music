# Generated by Django 2.1.5 on 2021-08-05 10:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0020_song_album'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='song',
            name='album',
        ),
    ]

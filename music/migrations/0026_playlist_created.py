# Generated by Django 2.1.5 on 2021-08-05 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0025_auto_20210805_2331'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default='1970-01-01 00:00:00+00:00'),
            preserve_default=False,
        ),
    ]

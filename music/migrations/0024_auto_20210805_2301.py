# Generated by Django 2.1.5 on 2021-08-05 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0023_auto_20210805_1804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlist',
            name='modified',
            field=models.DateField(auto_now=True),
        ),
    ]

# Generated by Django 2.1.5 on 2021-08-03 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0010_auto_20210803_1556'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='artists',
            field=models.ManyToManyField(blank=True, to='music.Artist'),
        ),
    ]

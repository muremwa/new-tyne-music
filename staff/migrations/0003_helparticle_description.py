# Generated by Django 2.1.5 on 2021-08-12 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0002_helparticle_is_staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='helparticle',
            name='description',
            field=models.CharField(default='A simple description for this article', max_length=2000),
            preserve_default=False,
        ),
    ]

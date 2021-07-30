# Generated by Django 2.1.5 on 2021-07-30 13:07

from django.db import migrations, models
import music.models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0004_creator_users'),
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('avi', models.ImageField(default='/defaults/genre.png', upload_to=music.models.upload_genre_image)),
                ('cover', models.ImageField(default='/defaults/genre_wide.png', upload_to=music.models.upload_genre_image)),
            ],
        ),
    ]
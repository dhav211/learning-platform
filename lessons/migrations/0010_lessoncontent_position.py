# Generated by Django 5.1 on 2024-08-31 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0009_uploadedimageblock_caption_uploadedimageblock_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessoncontent',
            name='position',
            field=models.IntegerField(default=0),
        ),
    ]

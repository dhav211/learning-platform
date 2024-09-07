# Generated by Django 5.1 on 2024-08-31 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0008_alter_lesson_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadedimageblock',
            name='caption',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='uploadedimageblock',
            name='image',
            field=models.ImageField(default='default-image-file.png', upload_to='images/'),
        ),
    ]

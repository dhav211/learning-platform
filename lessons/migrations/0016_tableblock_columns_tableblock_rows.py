# Generated by Django 5.1 on 2024-09-06 01:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0015_alter_lessoncontent_content_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='tableblock',
            name='columns',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tableblock',
            name='rows',
            field=models.IntegerField(default=0),
        ),
    ]

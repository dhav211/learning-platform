# Generated by Django 5.1 on 2024-08-28 21:42

import prose.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0005_exerciseblock_textblock_uploadedimageblock_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessoncontent',
            name='content_type',
            field=models.CharField(blank=True, choices=[('TXT', 'Text'), ('IMG', 'Image'), ('EXR', 'Exercise')], max_length=3),
        ),
        migrations.AlterField(
            model_name='textblock',
            name='text',
            field=prose.fields.RichTextField(null=True),
        ),
    ]

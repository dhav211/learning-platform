from typing import Any
from django.db import models
from prose.fields import RichTextField

class TextBlock(models.Model):
  text = RichTextField(null=True)

class UploadedImageBlock(models.Model):
  caption = models.CharField(max_length=512, null=True, blank=True)
  image = models.ImageField(upload_to="images/", default="default-image-file.png")

class TableCell(models.Model):
  row = models.IntegerField()
  column = models.IntegerField()
  data = models.CharField(max_length=512, null=True, blank=True)

class TableBlock(models.Model):
  rows = models.IntegerField(default=0)
  columns = models.IntegerField(default=0)
  cells = models.ManyToManyField(TableCell)

class LessonContent(models.Model):
  CONTENT_TYPE_CHOICES = {
    "TXT": "Text",
    "IMG": "Image",
    "EXR": "Exercise",
    "TBL": "Table",
  }
  
  position = models.IntegerField(default=0)
  content_type = models.CharField(max_length=3, choices=CONTENT_TYPE_CHOICES, blank=True)
  text = models.OneToOneField(TextBlock, models.CASCADE, null=True)
  image = models.OneToOneField(UploadedImageBlock, models.CASCADE, null=True)
  table = models.OneToOneField(TableBlock, models.CASCADE, null=True)

class Lesson(models.Model):
  name = models.CharField(max_length=50, default="", blank=True)
  content = models.ManyToManyField(LessonContent)

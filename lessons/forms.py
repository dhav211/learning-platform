from django import forms
from django.forms import ModelForm
from lessons.models import TextBlock, UploadedImageBlock, TableBlock, TableCell

class TextBlockForm(ModelForm):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['text'].label = ""

  class Meta:
    model = TextBlock
    fields = ["text"]

class UploadedImageBlockForm(ModelForm):
  is_filled = forms.CharField(widget=forms.HiddenInput(), initial=False)

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['image'].widget = forms.FileInput() 

  class Meta:
    model = UploadedImageBlock
    fields = ["caption", "image", "is_filled"]

class TableBlockForm(ModelForm):
  class Meta:
    model = TableBlock
    fields = ["rows", "columns"]

class TableCellForm(ModelForm):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['data'].label = ""

  class Meta:
    model = TableCell
    fields = ["data"]
"""
    Text is simple to handle since we are just worried about the html contents within the text-editor. This data persists
    between page refreshes so we can simply just resubmit all of them on save by just grabbing the POST data.
"""
import logging
from django.http import HttpResponse
from lessons.forms import TextBlockForm
from lessons.models import Lesson, TextBlock

logger = logging.getLogger('main_logger')

class TextBlockRenderData:
  def __init__(self, type, lesson, content, id):
    self.type = type
    self.lesson = lesson
    self.content = content
    self.id = id
  
  def get_data(self):
    return {"type": self.type, "lesson": self.lesson, "content": self.content, "id": self.id}

class TextBlockView:
  @staticmethod
  def create(lesson, content):
    text_block = TextBlock()
    text_block.save()
    content.content_type = "TXT"
    content.text = text_block

    content.save()
    lesson.content.add(content)
    lesson.save()

    form = TextBlockForm(instance=text_block, auto_id="f{lesson_content.id}_%s")
    render_data = TextBlockRenderData(content.content_type, lesson, form, content.id)

    return {
      "data": render_data.get_data(),
      "temptlate_to_render": "text_block_form.html",
    }

  @staticmethod
  def post_form(request, contents):
    contents = contents.order_by("position")
    for count, content in enumerate(contents):
      form = TextBlockForm(request.POST, instance=content.text)

      if form.is_valid():
        block = form.save(commit=False)
        block.text = request.POST.getlist('text')[count]
        block.save()
      else:
        return HttpResponse(form.errors)
  
  @staticmethod
  def get_form(content_block, lesson):
    text_block_form = TextBlockForm(instance=content_block.text, auto_id=f"{content_block.id}_%s")
    render_data = TextBlockRenderData(content_block.content_type, lesson, text_block_form, content_block.id)
    return render_data.get_data()
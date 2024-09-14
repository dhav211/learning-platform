import logging
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from lessons.models import Lesson, LessonContent, TextBlock, UploadedImageBlock, TableBlock, TableCell
from lessons.forms import TextBlockForm, UploadedImageBlockForm, TableBlockForm, TableCellForm
from lessons.views.text import TextBlockView
from lessons.views.image import ImageBlockView
from lessons.views.table import TableBlockView

logger = logging.getLogger('main_logger')

def show_lesson(request, lesson_id):
  lesson = get_object_or_404(Lesson, id=lesson_id)
  content = []

  if lesson.content.exists:
    for content_block in lesson.content.all().order_by("position"):
      if content_block.content_type == "TXT":
        content.append({"type": "TXT", "content": content_block.text.text})
      elif content_block.content_type == "IMG":
        content.append({"type": "IMG", "content": content_block.image.image})
      elif content_block.content_type == "TBL":
        cells = []
        for i in range(0, content_block.table.rows):
          row = content_block.table.cells.filter(row=i).order_by("column")
          row_forms = []
          for cell in row:
            row_forms.append(cell)
          cells.append(row_forms)
        content.append({"type": "TBL", "content": cells, "rows": content_block.table.rows, "columns": content_block.table.columns})

  return render(request, "lesson.html", {"content": content})

def lesson_creation(request, lesson_id):
  lesson = get_object_or_404(Lesson, id=lesson_id)

  if request.method == "GET":
    """
    Since the forms need TODO write the rest
    """
    forms = [None] * lesson.content.count() # list will be filled based on contents position
    table_amount = 0

    if lesson.content.exists:
      for content_block in lesson.content.all().order_by("position"):
        if content_block.content_type == "TXT":
          forms.append(TextBlockView.get_form(content_block, lesson))
        elif content_block.content_type == "IMG":
          forms.append(ImageBlockView.get_form(content_block, lesson))
        elif content_block.content_type == "TBL":
          forms.append(TableBlockView.get_form(content_block, lesson, table_amount))
          table_amount +=1
  
    data = {
      "lesson": lesson,
      "forms": forms
    }

    return render(request, "lesson_creation.html", data)      
  else:
    """
    Since each type of block is unique and we don't need to control the order they are rendered we will seperate them into
    different arrays based on their type and then ordered by position. We will handle each array, and once all is complete we
    will redirect to the lesson template
    """

    text_contents = lesson.content.filter(content_type="TXT")
    if len(text_contents) > 0:
      form_post = TextBlockView.post_form(request, text_contents)
      if form_post is not None:
        return form_post


    image_contents = lesson.content.filter(content_type="IMG")
    if len(image_contents) > 0:
      form_post = ImageBlockView.post_form(request, image_contents)
      if form_post is not None:
        return form_post
    
    table_contents = lesson.content.filter(content_type="TBL")
    if len(table_contents) > 0:
      form_post = TableBlockView.post_form(request, table_contents)
      if form_post is not None:
        return form_post

    
    return redirect("show_lesson", lesson_id)

def new(request):
  """An entry point to create a lesson. This is here simplfy the lesson creation function, Here we just create the new
  lesson and then immediatly redirect to the actual creation function"""
  lesson = Lesson()
  lesson.save()
  
  return redirect("lesson_creation", lesson.id)

def new_block(request, lesson_id):
  """Create an empty lesson block based up a parameter given in the request. This will create the block, add it to the 
  given lesson and then finally return the new block to be rendered in the lesson creation form"""
  lesson = get_object_or_404(Lesson, id=lesson_id)
  lesson_content = LessonContent()
  lesson_content.position = lesson.content.count()
  
  if request.GET.get("type") == "TXT":
    new_block = TextBlockView.create(lesson, lesson_content)
  
  elif request.GET.get("type") == "IMG":
    new_block = ImageBlockView.create(lesson, lesson_content)
  
  elif request.GET.get("type") == "TBL":
    new_block = TableBlockView.create(lesson, lesson_content)

  return render(request, new_block["temptlate_to_render"], new_block["data"])

def remove_block(request, lesson_id, content_block_id):
  lesson = get_object_or_404(Lesson, id=lesson_id)
  content_block = get_object_or_404(LessonContent, id=content_block_id)

  lesson.content.remove(content_block)
  content_block.delete()

  lesson.save()

  return HttpResponse()

def update_block(request, lesson_id, content_block_id):
  lesson = get_object_or_404(Lesson, id=lesson_id)
  lesson_content = get_object_or_404(LessonContent, id=content_block_id)
  render_data = {}

  if lesson_content.content_type == "TBL":
    render_data = {
      "template": "table_creation.html",
      "data": TableBlockView.change_table_size(request, lesson_content, lesson)
    }

  return render(request, render_data["template"], render_data["data"])
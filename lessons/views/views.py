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

  return render(request, "lesson.html", {"content": content})

def lesson_creation(request, lesson_id):
  lesson = get_object_or_404(Lesson, id=lesson_id)

  if request.method == "GET":
    """
    Since the forms need TODO write the rest
    """
    forms = [None] * lesson.content.count() # list will be filled based on contents position

    if lesson.content.exists:
      for content_block in lesson.content.all().order_by("position"):
        if content_block.content_type == "TXT":
          forms.append(TextBlockView.get_form(content_block, lesson))
        elif content_block.content_type == "IMG":
          forms.append(ImageBlockView.get_form(content_block, lesson))
        elif content_block.content_type == "TBL":
          forms.append(TableBlockView.get_form(content_block, lesson))
  
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

#TODO this will be called update block and will work similarly as previous method where it checks the type and called the
#correct method. FOr now this may one work with tables, but whateve
def change_table(request, lesson_id, content_block_id):
  logger.info(request.POST)
  lesson = get_object_or_404(Lesson, id=lesson_id)
  lesson_content = get_object_or_404(LessonContent, id=content_block_id)

  initial_cells = []
  for i in range(0, lesson_content.table.rows):
    initial_cells.append(lesson_content.table.cells.filter(row=i).order_by("column"))

  cell_forms = [] # These are the inputted form values

  # TODO check the POST request and see where the cell forms come into play
  
  initial_column_size = lesson_content.table.columns
  initial_row_size = lesson_content.table.rows
  new_column_size = int(request.POST.get('row'))
  new_row_size = int(request.POST.get('col'))

  updated_table_difference = (new_column_size * new_row_size) - (initial_row_size * initial_column_size)

  for x in range(0, new_column_size):
    for y in range(0, new_row_size):
      if updated_table_difference > 0: # Table is growing in size
        if x >= initial_row_size or y >= initial_column_size:
          # Create new new table cells that will be added to the database
          new_cell = TableCell()
          new_cell.column = x
          new_cell.row = y
          new_cell.save()
          lesson_content.table.cells.add(new_cell)
          pass
        else:
          #save the cell with the forms data
          pass
      elif updated_table_difference < 0: # Table is shrinking
        pass
      else: # No changeds to the table, just save
        pass
    
  lesson_content.table.rows = new_row_size
  lesson_content.table.columns = new_column_size
  lesson_content.table.save()

  # Order all the cells and turn them into forms to be fed to the template
  updated_cell_forms = []
  for i in range(0, lesson_content.table.rows):
    row = lesson_content.table.cells.filter(row=i).order_by("column")
    row_forms = []
    for cell in row:
      row_forms.append(TableCellForm(instance=cell, auto_id=f"{cell.id}_%s"))
    updated_cell_forms.append(row_forms)

  return render(request, "table_creation.html", {"cell_forms": updated_cell_forms})
import logging
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from lessons.models import Lesson, LessonContent, TextBlock, UploadedImageBlock, TableBlock, TableCell
from lessons.forms import TextBlockForm, UploadedImageBlockForm, TableBlockForm, TableCellForm

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
          text_block_form = TextBlockForm(instance=content_block.text, auto_id=f"{content_block.id}_%s")
          forms.append({"type": content_block.content_type, "content": text_block_form, "id": content_block.id})
        elif content_block.content_type == "IMG":
          uploaded_image_block_form = UploadedImageBlockForm(instance=content_block.image, auto_id=f"{content_block.id}_%s")
          forms.append({"type": content_block.content_type, "content": uploaded_image_block_form, "id": content_block.id, "image": content_block.image.image})
        elif content_block.content_type == "TBL":
          cell_forms = []
          for i in range(0, content_block.table.rows):
            row = content_block.table.cells.filter(row=i).order_by("column")
            for cell in row:
              cell_forms.append(TableCellForm(instance=cell, auto_id=f"{cell.id}_%s"))
          forms.append({"type": content_block.content_type, "table": content_block.table, "cell_forms": cell_forms, "id": content_block.id})
          
  else:
    """
    Since each type of block is unique and we don't need to control the order they are rendered we will seperate them into
    different arrays based on their type and then ordered by position. We will handle each array, and once all is complete we
    will redirect to the lesson template
    """

    text_contents = lesson.content.filter(content_type="TXT").order_by("position")
    """
    Text is simple to handle since we are just worried about the html contents within the text-editor. This data persists
    between page refreshes so we can simply just resubmit all of them on save by just grabbing the POST data.
    """
    for count, content in enumerate(text_contents):
      form = TextBlockForm(request.POST, instance=content.text)

      if form.is_valid():
        block = form.save(commit=False)
        block.text = request.POST.getlist('text')[count]
        block.save()
      else:
        return HttpResponse(form.errors)

    image_contents = lesson.content.filter(content_type="IMG").order_by("position")
    """
    Image is a bit more complicated as the input value doesn't presist between page loads like the text editor.
    So must manage if the element has been changed with javascript, that data will be posted here so when we loop
    through each image we check to see if that value has been filled, if it has then we can submit the data.
    We will load the image data by saving all the request files in an array and as we loop through the images
    we set the image as the first in that array and then remove it so it won't be used again on the next loop
    """
    current_uploads = request.FILES.getlist('image')

    for count, content in enumerate(image_contents):
      if request.POST.getlist("is_filled")[count] == "True":
        form = UploadedImageBlockForm(request.POST, request.FILES, instance=content.image)

        if form.is_valid():
          block = form.save(commit=False)
          block.image = current_uploads.pop(0)
          block.caption = request.POST.getlist('caption')[count]
          block.save()
        else:
          return HttpResponse(forms.errors)
    
    return redirect("show_lesson", lesson_id)

  data = {
    "lesson": lesson,
    "forms": forms
  }

  return render(request, "lesson_creation.html", data)

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
  data = {}
  temptlate_to_render = ""
  
  if request.GET.get("type") == "TXT":
    text_block = TextBlock()
    text_block.save()
    lesson_content.content_type = "TXT"
    lesson_content.text = text_block

    lesson_content.save()
    lesson.content.add(lesson_content)
    lesson.save()

    form = TextBlockForm(instance=text_block, auto_id="f{lesson_content.id}_%s")
    data = {"form": form, "lesson": lesson, "id": lesson_content.id}
    temptlate_to_render = "text_block_form.html"
  
  elif request.GET.get("type") == "IMG":
    uploaded_image_block = UploadedImageBlock()
    uploaded_image_block.save()
    lesson_content.content_type = "IMG"
    lesson_content.image = uploaded_image_block

    lesson_content.save()
    lesson.content.add(lesson_content)
    lesson.save()

    form = UploadedImageBlockForm(instance=uploaded_image_block, auto_id=f"{lesson_content.id}_%s")
    data = {"form": form, "lesson": lesson, "id": lesson_content.id, "image_url": uploaded_image_block.image.url}
    temptlate_to_render = "upload_image_form.html"
  
  elif request.GET.get("type") == "TBL":
    table_block = TableBlock()
    table_block.save()
    lesson_content.content_type = "TBL"
    lesson_content.table = table_block
    
    lesson_content.save()
    lesson.content.add(lesson_content)
    lesson.save()

    form = TableBlockForm(instance=table_block, auto_id=f"{lesson_content.id}_%s")
    data = { "form": form, "lesson": lesson, "id": lesson_content.id }
    temptlate_to_render = "table_block_form.html"

  return render(request, temptlate_to_render, data)

def remove_block(request, lesson_id, content_block_id):
  lesson = get_object_or_404(Lesson, id=lesson_id)
  content_block = get_object_or_404(LessonContent, id=content_block_id)

  lesson.content.remove(content_block)
  content_block.delete()

  lesson.save()

  return HttpResponse()

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
          new_cell.row = x
          new_cell.column = y
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
    for cell in row:
      updated_cell_forms.append(TableCellForm(instance=cell, auto_id=f"{cell.id}_%s"))

  return render(request, "table_creation.html", {"cell_forms": updated_cell_forms})
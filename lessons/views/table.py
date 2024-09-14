import logging
from django.http import HttpResponse
from lessons.forms import TableBlockForm, TableCellForm
from lessons.models import Lesson, TableBlock, TableCell

logger = logging.getLogger('main_logger')

class TableBlockRenderData:
  def __init__(self, type, lesson, content, id, cell_forms, current_number):
    self.type = type
    self.lesson = lesson
    self.content = content
    self.id = id
    self.cell_forms = cell_forms
    self.current_number = current_number
  
  def get_data(self):
    return {"type": self.type, "lesson": self.lesson, "content": self.content, "id": self.id, "cell_forms": self.cell_forms, "number": self.current_number}

class TableBlockView:  
  @staticmethod
  def create(lesson, content):
    table_block = TableBlock()
    table_block.save()
    content.content_type = "TBL"
    content.table = table_block
    
    content.save()
    lesson.content.add(content)
    lesson.save()

    form = TableBlockForm(instance=table_block, auto_id=f"{content.id}_%s")
    render_data =  TableBlockRenderData(content.content_type, lesson, content.table, content.id, [], lesson.content.filter(content_type="TBL").count() - 1)
    
    return {
      "data": render_data.get_data(),
      "temptlate_to_render": "table_block_form.html",
    }

  @staticmethod
  def post_form(request, contents):
    contents = contents.order_by("position")
    logger.info(request.POST)
    for count, content in enumerate(contents):
      form = TableBlockForm(request.POST, instance=content.table)
      rows = content.table.rows
      columns = content.table.columns
      cell_data_range = _cell_data_slice_range(request, columns, rows, count)
      cell_data = request.POST.getlist("data")[cell_data_range]
      
      if form.is_valid():
        cells = []
        for i in range(0, rows):
          row = content.table.cells.filter(row=i).order_by("column")
          row_forms = []
          for cell in row:
            row_forms.append(cell)
          cells.append(row_forms)
        for y in range(0, rows):     
          for x in range(0, columns):
            try:
              _save_cell(request, cells[y][x], cell_data.pop(0))
            except IndexError:
              logger.info(f"Out of bounds! Row = {y}   Column= {x}")

      else:
        return HttpResponse(form.errors)
  
  @staticmethod
  def get_form(content_block, lesson, table_amount):
    cell_forms = []
    for i in range(0, content_block.table.rows):
      row = content_block.table.cells.filter(row=i).order_by("column")
      row_forms = []
      for cell in row:
        row_forms.append(TableCellForm(instance=cell, auto_id=f"{cell.id}_%s"))
      cell_forms.append(row_forms)

    render_data = TableBlockRenderData(content_block.content_type, lesson, content_block.table, content_block.id, cell_forms, table_amount)
    return render_data.get_data()

  @staticmethod
  def change_table_size(request, content, lesson):
    logger.info(request.POST)

    form = TableBlockForm(request.POST, instance=content)

    if form.is_valid():
      table_number = int(request.POST.get('table_number'))
      initial_column_size = content.table.columns
      initial_row_size = content.table.rows
      new_column_size = int(request.POST.getlist('columns')[table_number])
      new_row_size = int(request.POST.getlist('rows')[table_number])

      # Get a slice of the cell data from the POST request, this will only contain the data needed for this table
      cell_data_range = _cell_data_slice_range(request, initial_column_size, initial_row_size, table_number)
      cell_data = request.POST.getlist("data")[cell_data_range]

      # Grab the cells that are already in the table for easy editing, deleting etc later on
      initial_cells = []
      for i in range(0, content.table.rows):
        row = content.table.cells.filter(row=i).order_by("column")
        row_forms = []
        for cell in row:
          row_forms.append(cell)
        initial_cells.append(row_forms)

      # table difference value will let us know if the table is growing or shrinking
      updated_table_difference = (new_column_size * new_row_size) - (initial_row_size * initial_column_size)

      # This has to be seperated in the multiple loops because the range of the loops will be different depending on
      # wether the table is growing or shrinking.
      if updated_table_difference > 0: # Table is growing in size
        for y in range(0, new_row_size):          
          for x in range(0, new_column_size):
            if x >= initial_column_size or y >= initial_row_size:
              # Create new new table cells that will be added to the database
              new_cell = TableCell()
              new_cell.column = x
              new_cell.row = y
              new_cell.save()
              content.table.cells.add(new_cell)
            else:
              try:
                _save_cell(request, initial_cells[y][x], cell_data.pop(0))
              except IndexError:
                logger.info(f"Out of bounds! Row = {y}   Column= {x}")

      elif updated_table_difference < 0: # Table is shrinking
        for y in range(0, initial_row_size):     
          for x in range(0, initial_column_size):
            if x >= new_column_size or y >= new_row_size:
              # Get cell and then remove it
              cell = initial_cells[y][x]
              cell.delete()     
            else:
              try:
                _save_cell(request, initial_cells[y][x], cell_data.pop(0))
              except IndexError:
                logger.info(f"Out of bounds! Row = {y}   Column= {x}")

      else: # No changeds to the table, just save
        for y in range(0, new_row_size):          
          for x in range(0, new_column_size):
              try:
                _save_cell(request, initial_cells[y][x], cell_data.pop(0))
              except IndexError:
                logger.info(f"Out of bounds! Row = {y}   Column= {x}")
              
      # Save the changes do the table itself
      content.table.rows = new_row_size
      content.table.columns = new_column_size
      content.table.save()

      # Order all the cells and turn them into forms to be fed to the template
      # TODO lets get rid of this in future use, we can create and manage a list somewhere instead 
      updated_cell_forms = []
      for i in range(0, content.table.rows):
        row = content.table.cells.filter(row=i).order_by("column")
        row_forms = []
        for cell in row:
          row_forms.append(TableCellForm(instance=cell, auto_id=f"{cell.id}_%s"))
        updated_cell_forms.append(row_forms)
      
      render_data =  TableBlockRenderData(content.content_type, lesson, form, content.id, updated_cell_forms, int(request.POST.get('table_number')))
      return render_data.get_data()
    else: # Form was not valid
      logger.info("Form failed!")
      logger.info(form.errors)


#### Helper methods that shouldn't be accessed outside of this module ####


def _cell_data_slice_range(request, initial_column_size, initial_row_size, table_number):
  rows = request.POST.getlist('rows')
  columns = request.POST.getlist('columns')
  start = 0
  if table_number > 0:
    end = int(rows[0]) * int(columns[0]) - 1
  else:
    end = (initial_column_size * initial_row_size) - 1
  
  for i in range(1, table_number + 1):
    start += int(rows[i-1]) * int(columns[i-1])
    if i is not table_number:
      end += int(rows[i]) * int(columns[i])
    else:
      end += (initial_column_size * initial_row_size)
  return slice(start, end + 1)

def _save_cell(request, cell, data):
  form = TableCellForm(request.POST, instance=cell)
  if form.is_valid():
    cell.data = data
    cell.save()
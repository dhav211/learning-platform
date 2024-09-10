import logging
from django.http import HttpResponse
from lessons.forms import TableBlockForm, TableCellForm
from lessons.models import Lesson, TableBlock

logger = logging.getLogger('main_logger')

class TableBlockRenderData:
  def __init__(self, type, lesson, content, id, cell_forms):
    self.type = type
    self.lesson = lesson
    self.content = content
    self.id = id
    self.cell_forms = cell_forms
  
  def get_data(self):
    return {"type": self.type, "lesson": self.lesson, "content": self.content, "id": self.id, "cell_forms": self.cell_forms}

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
    render_data =  TableBlockRenderData(content.content_type, lesson, form, content.id, [])
    
    return {
      "data": render_data.get_data(),
      "temptlate_to_render": "table_block_form.html",
    }

  @staticmethod
  def post_form(request, contents):
    pass
  
  @staticmethod
  def get_form(content_block, lesson):
    cell_forms = []
    for i in range(0, content_block.table.rows):
      row = content_block.table.cells.filter(row=i).order_by("column")
      row_forms = []
      for cell in row:
        row_forms.append(TableCellForm(instance=cell, auto_id=f"{cell.id}_%s"))
      cell_forms.append(row_forms)

    render_data = TableBlockRenderData(content_block.content_type, lesson, content_block.table, content_block.id, cell_forms)
    return render_data.get_data()
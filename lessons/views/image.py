import logging
from django.http import HttpResponse
from lessons.forms import UploadedImageBlockForm
from lessons.models import UploadedImageBlock

logger = logging.getLogger('main_logger')

class ImageBlockRenderData:
  def __init__(self, type, lesson, content, id, image, image_url) -> None:
    self.type = type
    self.lesson = lesson
    self.content = content
    self.id = id
    self.image = image
    self.image_url = image_url

  def get_data(self):
    return {"type": self.type, "lesson": self.lesson, "content": self.content, "id": self.id, "image": self.image, "image_url": self.image_url} 

class ImageBlockView:
  @staticmethod
  def create(lesson, content):
    uploaded_image_block = UploadedImageBlock()
    uploaded_image_block.save()
    content.content_type = "IMG"
    content.image = uploaded_image_block

    content.save()
    lesson.content.add(content)
    lesson.save()

    uploaded_image_block_form = UploadedImageBlockForm(instance=uploaded_image_block, auto_id=f"{content.id}_%s")
    render_data = ImageBlockRenderData(content.content_type,
                                    lesson,
                                    uploaded_image_block_form, 
                                    content.id, 
                                    content.image.image,
                                    content.image.image.url)

    return {
      "data": render_data.get_data(),
      "temptlate_to_render": "upload_image_form.html",
    }

  @staticmethod
  def post_form(request, contents):
    """
    Image is a bit more complicated as the input value doesn't presist between page loads like the text editor.
    So must manage if the element has been changed with javascript, that data will be posted here so when we loop
    through each image we check to see if that value has been filled, if it has then we can submit the data.
    We will load the image data by saving all the request files in an array and as we loop through the images
    we set the image as the first in that array and then remove it so it won't be used again on the next loop
    """
    contents = contents.order_by("position")
    current_uploads = request.FILES.getlist('image')
    
    for count, content in enumerate(contents):
      form = UploadedImageBlockForm(request.POST, request.FILES, instance=content.image)

      if form.is_valid():
        block = form.save(commit=False)

        # The image will be updated only when user tries to upload one
        if request.POST.getlist("is_filled")[count] == "True":
          block.image = current_uploads.pop(0)

        logger.info(request.POST.getlist('caption')[count])
        block.caption = request.POST.getlist('caption')[count]
        block.save()
      else:
        return HttpResponse(form.errors)
  
  @staticmethod
  def get_form(content_block, lesson):
    uploaded_image_block_form = UploadedImageBlockForm(instance=content_block.image, auto_id=f"{content_block.id}_%s")

    logger.info(f"HEEYYOOO {content_block.image.image.url}")

    render_data = ImageBlockRenderData(content_block.content_type,
                                       lesson,
                                       uploaded_image_block_form, 
                                       content_block.id, 
                                       content_block.image.image,
                                       content_block.image.image.url)
    
    return render_data
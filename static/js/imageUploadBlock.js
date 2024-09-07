class ImageUpload {
  constructor() {
    this.isFilledField = undefined
    this.uploadField = undefined
    this.previewImage = undefined
  }

  setIsFilledField(id) {
    this.isFilledField = document.getElementById(`${id}_is_filled`)
  }

  setPreviewImage(id) {
    this.previewImage = document.getElementById(`preview-image-${id}`)
  }

  setUploadField(id) {
    this.uploadField = document.getElementById(`${id}_image`)

    // When the user tries to upload a file then let the hidden input field to true. This will let the POST know
    // which image block is currently trying to change
    // I set a reverse value just incase there is a I don't know about on undoing a file upload
    this.uploadField.onchange = () => {
      if (this.isFilledField.value === "False") {
        this.isFilledField.value = "True"
      }
      else if (this.isFilledField.value === "True") {
        this.isFilledField.value = "False"
      }

      // This changes the upload preview image to the image you have currently selected
      if (this.uploadField.files && this.uploadField.files[0]) {
        let fileReader = new FileReader();
        fileReader.addEventListener("load", (e) => { this.previewImage.src = e.target.result })

        fileReader.readAsDataURL(this.uploadField.files[0])
      }
    }
  }
}
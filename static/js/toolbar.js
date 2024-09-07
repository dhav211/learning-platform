class TextToolbar {
  constructor() {
    this.toolbar = undefined
    this.bottomRowButtons = undefined
  }

  // Remove the image attacment, history buttons, and various spacers from the editor
  removeUnwantedIcons() {
    let iconRow = this.toolbar.children[0]
    for (let i = 2; i <= 4; i++) {
      if (iconRow.children[i])
        iconRow.children[i].remove()
    }
  }

  show() {
    if (this.toolbar) {
      this.toolbar.style.visibility = "visible"
      this.bottomRowButtons.style.visibility = "visible"
    }
  }

  hide() {
    if (this.toolbar) {
      this.toolbar.style.visibility = "hidden"
      this.bottomRowButtons.style.visibility = "hidden"
    }
  }

  setToolbar(element) {
    this.toolbar = element.getElementsByTagName(`trix-toolbar`)[0]
  }

  setBottomRowButtons(id) {
    this.bottomRowButtons = document.getElementById(`text-bottom-row-${id}`)
  }
}
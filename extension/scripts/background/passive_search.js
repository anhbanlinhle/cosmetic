//SECTION - keyboard event

let selectedText = null
let selectedElement = null

document.addEventListener('mouseup', (event) => {
  selectedText = window.getSelection().toString()
  selectedElement = window.getSelection().baseNode.parentElement
  // selectedElement.classList.add("detected-product")
})

chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
  if (message.message === "trigger_search") {
    console.log(selectedText)
    if (selectedText.length > 0) {
      response = await queryElastic(selectedText)
      console.log(response)
    }
    selectedText = ""
    selectedElement = null
  }
})

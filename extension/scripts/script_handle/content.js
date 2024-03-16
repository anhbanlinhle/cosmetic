const FOUND = "#6eff92"
const FOUND_MANY = "#d1d1d1"
const NOT_FOUND = "none"
const COLOR = {
  "-1": NOT_FOUND,
  "1": FOUND_MANY,
  "0": FOUND
}

let queryElastic = async (queryData) => {
  res = await fetch('http://localhost:9200/test-5/_search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Basic ZWxhc3RpYzpjaGFuZ2VtZQ=='
    },
    body: JSON.stringify({
      "query": {
          "match": {
              "name": {
                  "query": queryData,
                  "minimum_should_match": "80%"
              }
          }
      }
    })
  })
  response = JSON.parse(await res.text())
  return response
}

let checkWordImportance = async (word) => {
  response = await queryElastic(word)
  let result = response.hits.hits.length

  if (result > 1)
    return 1
  if (result === 1) 
    return 0
  return -1
}

let scanForTexts = async (element) => {
  for (const child of element.childNodes) {
    if (child.nodeName === "SCRIPT" || child.nodeName === "NOSCRIPT" || 
    child.nodeName === "STYLE" || child.nodeName === "HEADER" || child.nodeName === "FOOTER") {
      continue
    }
    if (child.nodeType === Node.TEXT_NODE) {
      let text = child.textContent;
      if (text.trim().length < 15)
        continue
      
      let color = await checkWordImportance(text)
      element.style.background = COLOR[color]
    } 
    else if (child.nodeType === Node.ELEMENT_NODE) {
      scanForTexts(child)
    }
  }
}

scanForTexts(document.body);

let selectedText = null
let selectedElement = null

document.addEventListener('mouseup', (event) => {
  selectedText = window.getSelection().toString()
  selectedElement = window.getSelection().baseNode.parentElement
  selectedElement.classList.add("detected-product")
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

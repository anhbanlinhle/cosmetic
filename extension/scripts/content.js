const body = document.querySelector("body");
const RED = "#ff4a4d";
const ORANGE = "#ffee03";
const YELLOW = "#1cff03";
const GREEN = "#ff792b";

function trimWord(word) {
  return word.trim();
}

const textNodes = [];
function getTextNodes(element) {
  for (const child of element.childNodes) {
    if (child.nodeType === Node.TEXT_NODE) {
      textNodes.push(child);
    } else if (child.nodeType === Node.ELEMENT_NODE) {
      getTextNodes(child);
    }
  }
}

getTextNodes(body);

function checkWordImportance(word) {
  if (word === "Kem Chống Nắng Nature Republic Nâng Tone Tự Nhiên 57ml") {
    return RED;
  } else if (word === "Kem Chống Nắng Nature Republic California Aloe Daily Sun Block SPF50+PA++++ 57ml") {
    return ORANGE;
  } else if (word === "Mặt Nạ Celderma Crystal Skin Mask 23g") {
    return YELLOW;
  } else if (word === "Alexei Navalny") {
    return GREEN;
  } else {
    return "none";
  }
}

for (const textNode of textNodes) {
  let originalText = textNode.textContent;
  const coloredWords = [];

  const color = checkWordImportance(originalText);

  if (color !== "none") {
    const cosmeticName = document.createElement("span");
    cosmeticName.style.backgroundColor = color;
    cosmeticName.style.color = "black";
    cosmeticName.textContent = originalText;

    coloredWords.push(cosmeticName);
  }
  else {
    coloredWords.push(document.createTextNode(originalText));
  }

  const combinedContent = document.createDocumentFragment();
  combinedContent.append(...coloredWords);
  textNode.parentNode.replaceChild(combinedContent, textNode);
}

let selectedText = "";

document.addEventListener('mouseup', (event) => {
  selectedText = window.getSelection().toString();
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.message === "trigger_search") {
    console.log(selectedText);
    if (selectedText.length > 0) {
      fetch('http://localhost:9200/test-2/_search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ZWxhc3RpYzpjaGFuZ2VtZQ=='
      },
      body: JSON.stringify({
        "query": {
            "match": {
                "name": {
                    "query": selectedText
                }
            }
        }
      })
    })
    .then(response => response.json())
    .then(data => {
      // Handle the search response data here
      console.log(data);
    })
    .catch(error => {
      console.error(error);
    });
    }
    selectedText = ""; // Reset selected text
  }
});
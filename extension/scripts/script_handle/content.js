const excludedTags = new Set(["HEADER", "FOOTER", "IMG", "SVG", "INPUT", "SCRIPT", "LINK", "STYLE", "IFRAME", "BUTTON", "desc"]);
const excludedTagsMutation = new Set(["HEADER", "FOOTER", "IMG", "SVG", "INPUT", "SCRIPT", "LINK", "STYLE", "IFRAME", "BODY", "BUTTON", "desc"]);
let countElImportant = 0;
let countElUnimportant = 0;
const config = { subtree: true, childList: true };

const isTextElement = (element) => {
  return Array.from(element.childNodes).every(child => child.nodeType === Node.TEXT_NODE);
}

const hasTextSibling = (element) => {
  const nextSibling = element.nextSibling;
  const previousSibling = element.previousSibling;
  const nextElementSibling = element.nextElementSibling;
  const previousElementSibling = element.previousElementSibling;

  const nextSiblingTextNodeIsValid = (nextSibling !== null && nextSibling.nodeType == Node.TEXT_NODE && nextSibling.data.trim().length > 0);
  const previousSiblingTextNodeIsValid = (previousSibling !== null && previousSibling.nodeType == Node.TEXT_NODE && previousSibling.data.trim().length > 0);
  const nextElementSiblingIsValid = (nextElementSibling !== null && isTextElement(nextElementSibling));
  const previousElementSiblingIsValid = (previousElementSibling !== null && isTextElement(previousElementSibling));

  return (nextSiblingTextNodeIsValid || previousSiblingTextNodeIsValid || nextElementSiblingIsValid || previousElementSiblingIsValid);
}

const directTextElementIsImportant = (element) => {
  // if (!isTextElement(element)) {
  //   return false;
  // }

  let merged = "";

  for (const child of element.childNodes) {
    merged += child.data.trim();
  }

  // check pagination tag
  if (element.tagName == "A" && !isNaN(Number(merged))) {
    return false;
  }

  return (merged.length >= 15 && merged.includes(" ")) || hasTextSibling(element);
}

const callback = (mutationList, observer) => {
  for (const mutation of mutationList) {
    if (!excludedTagsMutation.has(mutation.target.tagName) && mutation.addedNodes.length > 0) {
      for (const child of mutation.addedNodes) {  
        // traverse(child);
        console.log(child);
      }
    }
  }
};

const hasDirectText = (element) => {
  return Array.prototype.some.call(element.childNodes, function(child) {
    return child.nodeType === Node.TEXT_NODE && /\S/.test(child.nodeValue);
  })
}

const traverse = (element) => {
  if (excludedTags.has(element.tagName)) {
    return;
  }

  if (hasDirectText(element)) {
    if (isTextElement(element) && !directTextElementIsImportant(element)) {
      // console.log(element, " --- unimportant");
      // countElUnimportant++;
    } else {
      countElImportant++;
      console.log(element, element.tagName);
    }
    console.log("----------------------------------");
  }
  
  for (const child of element.children) {
    traverse(child);
  }
}


window.addEventListener("load", (event) => {
  const observer = new MutationObserver(callback);

  const body = document.querySelector("body");
  observer.observe(body, config);
  traverse(body);

  setTimeout(() => {
    console.log("important: ", countElImportant);
    console.log("unimportant: ", countElUnimportant);
  }, 10000);
});

// const RED = "#ff4a4d";
// const ORANGE = "#ffee03";
// const YELLOW = "#1cff03";
// const GREEN = "#ff792b";

// let getTextNodes = (element) => {
//   for (const child of element.childNodes) {
//     if (child.nodeType === Node.TEXT_NODE) {
//       textNodes.push(child);
//     } else if (child.nodeType === Node.ELEMENT_NODE) {
//       getTextNodes(child);
//     }
//   }
// }

// let checkWordImportance = (word) => {
//   if (word === "Thích") {
//     return RED;
//   } else if (word === "Kem Chống Nắng Nature Republic California Aloe Daily Sun Block SPF50+PA++++ 57ml") {
//     return ORANGE;
//   } else if (word === "Mặt Nạ Celderma Crystal Skin Mask 23g") {
//     return YELLOW;
//   } else if (word === "Alexei Navalny") {
//     return GREEN;
//   } else {
//     return "none";
//   }
// }

// let paragraphToWords = (paragraph) => {
//   const regex = /(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s/;
//   return paragraph.split(regex);
// }

// const textNodes = [];
// getTextNodes(body);

// for (const textNode of textNodes) {
//   let originalText = paragraphToWords(textNode.textContent);

//   const coloredWords = [];

//   for (const word of originalText) {
//     const color = checkWordImportance(word);

//     if (color !== "none") {   
//       const cosmeticName = document.createElement("span");
//       cosmeticName.style.backgroundColor = color;
//       cosmeticName.style.color = "black";
//       cosmeticName.textContent = word + ' ';

//       coloredWords.push(cosmeticName);
//     }
//     else {
//       coloredWords.push(document.createTextNode(word + ' '));
//     }
//   }

//   const combinedContent = document.createDocumentFragment();
//   combinedContent.append(...coloredWords);
//   textNode.parentNode.replaceChild(combinedContent, textNode);
// }

// let selectedText = "";

// document.addEventListener('mouseup', (event) => {
//   selectedText = window.getSelection().toString();
// });

// chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
//   if (message.message === "trigger_search") {
//     console.log(selectedText);
//     if (selectedText.length > 0) {
//       response = await queryElastic(selectedText);
//       console.log(response);
//     }
//     selectedText = "";
//   }
// });

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
                  "minimum_should_match": "70%"
              }
          }
      }
    })
  })
  response = JSON.parse(await res.text())
  return response;
}
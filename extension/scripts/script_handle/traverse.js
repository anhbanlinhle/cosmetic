const checkWordImportance = require('./fetchElastic').checkWordImportance

const hasDirectText = require('./utility').hasDirectText
const isTextElement = require('./utility').isTextElement
const directTextElementIsImportant = require('./utility').directTextElementIsImportant
const notUndefinedAndNull = require('./utility').notUndefinedAndNull
const hasTextSibling = require('./utility').hasTextSibling

const excludedTags = new Set(["HEADER", "FOOTER", "IMG", "SVG", "INPUT", "SCRIPT", "LINK", "STYLE", "IFRAME", "BUTTON", "desc"]);
const excludedTagsMutation = new Set(["HEADER", "FOOTER", "IMG", "SVG", "INPUT", "SCRIPT", "LINK", "STYLE", "IFRAME", "BODY", "BUTTON", "desc"]);

const FOUND = "#6eff92"
const FOUND_MANY = "#d1d1d1"
const NOT_FOUND = "none"
const COLOR = {
  "-1": NOT_FOUND,
  "1": FOUND_MANY,
  "0": FOUND
}

//SECTION - traverse dom

const callback = (mutationList, observer) => {
  for (const mutation of mutationList) {
    if (!excludedTagsMutation.has(mutation.target.tagName) && mutation.addedNodes.length > 0) {
      for (const child of mutation.addedNodes) {  
        traverse(child);
        // console.log(child);
      }
    }
  }
};

const traverse = async (element) => {
  if (excludedTags.has(element.tagName)) {
    return;
  }

  if (hasDirectText(element)) {
    if (isTextElement(element) && !directTextElementIsImportant(element)) {
      // console.log(element, " --- unimportant");
    } else {
      // console.log(element, element.tagName);
      // console.log(element.textContent.trim());
      let color = await checkWordImportance(element.textContent.trim());
      element.style.background = COLOR[color]
      // element.innerHTML =  `<span style="background: ${COLOR[color]};">${element.innerHTML}</span>`
    }
    // console.log("----------------------------------");
  }
  
  for (const child of element.children) {
    traverse(child);
  }
}

module.exports = {
  traverse,
  callback
}
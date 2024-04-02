const excludedTags = new Set(["HEADER", "FOOTER", "IMG", "SVG", "INPUT", "SCRIPT", "LINK", "STYLE", "IFRAME", "BUTTON", "desc"]);
const excludedTagsMutation = new Set(["HEADER", "FOOTER", "IMG", "SVG", "INPUT", "SCRIPT", "LINK", "STYLE", "IFRAME", "BODY", "BUTTON", "desc"]);
const config = { subtree: true, childList: true };
const MINIMUM_TEXT_LENGTH_THRESHOLD = 15;
let countElImportant = 0;
let countElUnimportant = 0;

const notUndefinedAndNull = (obj) => {
    return obj !== undefined && obj !== null;
}

const isTextElement = (element) => {
  return Array.from(element.childNodes).every(child => child.nodeType === Node.TEXT_NODE);
}

const hasTextSibling = (element) => {
  const nextSibling = element.nextSibling;
  const previousSibling = element.previousSibling;
  const nextElementSibling = element.nextElementSibling;
  const previousElementSibling = element.previousElementSibling;

  const nextSiblingNotEmpty = notUndefinedAndNull(nextSibling);
  const previousSiblingNotEmpty = notUndefinedAndNull(previousSibling);
  const nextElementSiblingNotEmpty = notUndefinedAndNull(nextElementSibling);
  const previousElementSiblingNotEmpty = notUndefinedAndNull(previousElementSibling);

  const nextSiblingTextNodeIsValid = (nextSiblingNotEmpty && nextSibling.nodeType == Node.TEXT_NODE && nextSibling.data.trim().length > 0);
  const previousSiblingTextNodeIsValid = (previousSiblingNotEmpty && previousSibling.nodeType == Node.TEXT_NODE && previousSibling.data.trim().length > 0);
  const nextElementSiblingIsValid = (nextElementSiblingNotEmpty && isTextElement(nextElementSibling));
  const previousElementSiblingIsValid = (previousElementSiblingNotEmpty && isTextElement(previousElementSibling));

  let total_text_length = 0;
  if (nextSiblingNotEmpty && nextSibling.nodeType == Node.TEXT_NODE) {
    total_text_length += nextSibling.data.trim().length;
  }
  if (previousSiblingNotEmpty && previousSibling.nodeType == Node.TEXT_NODE) {
    total_text_length += previousSibling.data.trim().length;
  }
  if (nextElementSiblingNotEmpty) {
    total_text_length += nextElementSibling.textContent.trim().length;
  }
  if (previousElementSiblingNotEmpty) {
    total_text_length += previousElementSibling.textContent.trim().length;
  }

  return {
    "has_sibling": (nextSiblingTextNodeIsValid || previousSiblingTextNodeIsValid || nextElementSiblingIsValid || previousElementSiblingIsValid),
    "sibling_text_length": total_text_length
  }
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

  const thisElementHasTextSibling = hasTextSibling(element);

  return (merged.length >= MINIMUM_TEXT_LENGTH_THRESHOLD && merged.includes(" ")) || 
            (thisElementHasTextSibling.has_sibling && (merged.length + thisElementHasTextSibling.sibling_text_length >= MINIMUM_TEXT_LENGTH_THRESHOLD));
}

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
      console.log(element, " --- unimportant");
      countElUnimportant++;
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

//   setTimeout(() => {
//     console.log("important: ", countElImportant);
//     console.log("unimportant: ", countElUnimportant);
//   }, 10000);
});

const body = document.querySelector("body");

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
  if (word === "Sữa Rửa Mặt Dr.G pH Cleansing Gel Foam 200ml") {
    return "#ff173e";
  } else if (word === "Kem Chống Nắng Nature Republic California Aloe Daily Sun Block SPF50+PA++++ 57ml") {
    return "#ffee03";
  } else if (word === "Mặt Nạ Celderma Crystal Skin Mask 23g") {
    return "#1cff03";
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

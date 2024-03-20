const traverse = require('./traverse').traverse
const callback = require('./traverse').callback

const config = { subtree: true, childList: true };

window.addEventListener("load", (event) => {
  const observer = new MutationObserver(callback);

  const body = document.querySelector("body");
  observer.observe(body, config);
  traverse(body);
});

chrome.commands.onCommand.addListener((command) => {
  if (command === "trigger_search") {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs && tabs.length > 0) {
        chrome.tabs.sendMessage(tabs[0].id, { message: "trigger_search" });
      }
    });
  }
});

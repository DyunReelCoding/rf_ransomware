// content.js - This script runs in the context of the web page
console.log("Ransomware detection content script loaded.");

// Listen for messages from the popup or background script (optional)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'checkFile') {
    // Optionally, you could perform actions here based on messages
    console.log("Checking file for ransomware...");
    sendResponse({ result: 'safe' });  // Just as an example response
  }
});

// You can inject content into the page or interact with the DOM as needed
// For instance, you could display a message or inject a button
// (Currently, it's just a logging setup for debugging)
document.body.insertAdjacentHTML('beforeend', `
  <div id="ransomwareStatus" style="position: fixed; top: 10px; right: 10px; background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; font-size: 14px;">
    <strong>Ransomware Detection Active</strong>
  </div>
`);


document.addEventListener("DOMContentLoaded", () => {
  // Communicate with the background script
  chrome.runtime.sendMessage({ action: "getFilePath" }, (response) => {
    const filePath = response.filePath;
    const message = `The file ${filePath} is classified as ransomware.`;

    // Update the message in the popup
    document.getElementById("fileMessage").textContent = message;

    // Attach event listeners to the buttons
    document.getElementById("deleteButton").addEventListener("click", () => {
      chrome.runtime.sendMessage({ action: "deleteFile", filePath: filePath });
      window.close(); // Close the popup after action
    });

    document.getElementById("keepButton").addEventListener("click", () => {
      chrome.runtime.sendMessage({ action: "keepFile" });
      window.close(); // Close the popup after action
    });
  });
});

document.getElementById("checkDownloadBtn").addEventListener("click", () => {
  // Send message to background.js to check the downloads folder
  chrome.runtime.sendMessage({ action: "checkDownloads" }, (response) => {
    if (response.success) {
      alert("Detection initiated for any EXE files in the Downloads folder.");
    } else {
      alert("No EXE files found in the Downloads folder or error occurred.");
    }
  });
});

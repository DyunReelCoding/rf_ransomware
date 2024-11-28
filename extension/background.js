const serverUrl = "http://localhost:5000/detect_ransomware";
const downloadDir = "/home/jonriel/Downloads";
let currentRansomwareFile = null;

// Monitor downloads
chrome.downloads.onChanged.addListener((downloadDelta) => {
  if (downloadDelta.state && downloadDelta.state.current === "complete") {
    chrome.downloads.search({ id: downloadDelta.id }, (results) => {
      if (results && results[0]) {
        const filePath = results[0].filename;

        // Check if the file is an .exe in the specified directory
        if (filePath.startsWith(downloadDir) && filePath.endsWith(".exe")) {
          console.log(`New .exe file detected: ${filePath}`);
          processFile(filePath, results[0].id);
        }
      }
    });
  }
});

// Function to send the file path to the Flask server
function processFile(filePath, downloadId) {
  fetch(serverUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ file_path: filePath }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`);
      }
      return response.json();
    })
    .then((result) => {
      if (result.file_status === "ransomware") {
        console.warn(`Warning: The file ${filePath} is classified as ransomware.`);
        currentRansomwareFile = filePath;

        // Open the popup
        chrome.windows.create({
          url: "popup.html",
          type: "popup",
          width: 400,
          height: 300,
        });
      } else {
        console.log(`The file ${filePath} is safe.`);
      }
    })
    .catch((error) => {
      console.error("Error communicating with the Flask server:", error);
    });
}

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "getFilePath") {
    sendResponse({ filePath: currentRansomwareFile });
  } else if (message.action === "deleteFile") {
    deleteFile(message.filePath);
  } else if (message.action === "keepFile") {
    console.log("User chose to keep the file.");
  }
});

// Function to delete the ransomware file
function deleteFile(filePath) {
  // Search for the download ID by filename
  chrome.downloads.search({ filename: filePath }, function (results) {
    if (results && results[0]) {
      const downloadId = results[0].id;

      // Remove the file using chrome.downloads.removeFile()
      chrome.downloads.removeFile(downloadId, function (success) {
        if (success) {
          console.log(`File deleted: ${filePath}`);
        } else {
          console.error(`Failed to delete file: ${filePath}`);
        }
      });
    } else {
      console.error(`File not found in downloads: ${filePath}`);
    }
  });
}

chrome.downloads.onChanged.addListener((delta) => {
  if (delta.state && delta.state.current === "complete") {
    chrome.downloads.search({ id: delta.id }, (results) => {
      if (results.length === 0) {
        return;
      }

      const filePath = results[0].filename;
      const fileName = filePath.split('/').pop();

      chrome.fileSystem.chooseEntry({ type: 'openFile', accepts: [{ extensions: ['exe'] }] }, async (entry) => {
        try {
          const fileContent = await readFileContent(entry);
          const blob = new Blob([fileContent], { type: 'application/octet-stream' });

          const formData = new FormData();
          formData.append('file', blob, fileName);

          const response = await fetch('http://localhost:5000/detect_ransomware', {
            method: 'POST',
            body: formData
          });

          const data = await response.json();
          if (data.file_status === "ransomware") {
            const notificationId = "ransomware_detected_" + Math.random().toString(36).substring(7);

            chrome.notifications.create(notificationId, {
              type: "basic",
              iconUrl: "icon48.png",
              title: "Ransomware Detected!",
              message: `The file "${fileName}" is classified as ransomware. What would you like to do?`,
              buttons: [
                { title: "Delete File" },
                { title: "Keep File" }
              ],
              requireInteraction: true
            });

            chrome.notifications.onButtonClicked.addListener((notifId, btnIdx) => {
              if (notifId === notificationId) {
                if (btnIdx === 0) {
                  chrome.downloads.removeFile(results[0].id, () => {
                    console.log(`File ${fileName} deleted.`);
                  });
                } else if (btnIdx === 1) {
                  console.log(`File ${fileName} kept.`);
                }
                chrome.notifications.clear(notificationId);
              }
            });
          }
        } catch (error) {
          console.error("Error processing file:", error);
        }
      });
    });
  }
});

async function readFileContent(entry) {
  return new Promise((resolve, reject) => {
    entry.file(file => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(reader.error);
      reader.readAsArrayBuffer(file);
    });
  });
}

// utils.js

async function fetchFile(filePath) {
    // Assuming this will fetch the EXE file content
    const response = await fetch(filePath);
    const arrayBuffer = await response.arrayBuffer();
    return arrayBuffer;
  }
  
  export { fetchFile };
  
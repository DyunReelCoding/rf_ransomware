import os
import time
import requests

download_dir = "/home/jonriel/Downloads"

def monitor_directory(path):
    before = dict([(f, None) for f in os.listdir(path)])
    while True:
        time.sleep(5)  # Check every 5 seconds
        after = dict([(f, None) for f in os.listdir(path)])
        added = [f for f in after if not f in before]
        if added:
            for file in added:
                if file.endswith('.exe'):
                    full_path = os.path.join(path, file)
                    print(f"New file detected: {full_path}")
                    process_file(full_path)
        before = after

def process_file(file_path):
    url = "http://localhost:5000/detect_ransomware"
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f)}
        response = requests.post(url, files=files)
        if response.status_code == 200:
            result = response.json()
            if result['file_status'] == 'ransomware':
                print(f"Warning: The file {file_path} is classified as ransomware.")
            else:
                print(f"The file {file_path} is safe.")
        else:
            print(f"Failed to process the file {file_path}. Server response: {response.status_code}")

if __name__ == "__main__":
    monitor_directory(download_dir)

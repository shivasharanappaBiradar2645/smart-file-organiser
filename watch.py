import os
import hashlib
import datetime
import requests
import json
import logging


logging.basicConfig(filename="scanner.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# API Config
API_URL = "http://localhost.com/upload"  
DEVICE_ID = "DEVICE123" 
USERNAME = "user001"  

# File Categories Mapping
EXTENSION_MAP = {
    'documents': ['.pdf', '.docx', '.txt'],
    'images': ['.jpg', '.jpeg', '.png'],
    'videos': ['.mp4', '.mov', '.avi'],
    'audio': ['.mp3', '.wav'],
    'archives': ['.zip', '.tar', '.rar'],
    'others': []
}
EXT_TO_CATEGORY = {ext: cat for cat, exts in EXTENSION_MAP.items() for ext in exts}

# Directories & File Types to Exclude
EXCLUDED_DIRS = {'Library', '.config', '.local', '.cache', 'Applications', 'node_modules', 'venv', '.npm', '.git'}
EXCLUDED_FILE_TYPES = {'.log', '.tmp', '.bak'}

# Generate SHA-256 hash for a file
def generate_hash(file_path):
    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(4096):  
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logging.warning(f"Failed to read {file_path}: {e}")
        return None  


def categorize_file(filename):
    return EXT_TO_CATEGORY.get(os.path.splitext(filename)[1].lower(), 'others')


def send_to_api(file_data):
    try:
        response = requests.post(API_URL, json=file_data, timeout=5)
        if response.status_code == 201:
            logging.info(f"Sent: {file_data['path']}")
        elif response.status_code == 409:
            logging.info(f" Already exists: {file_data['path']}")
        else:
            logging.error(f"Failed to send {file_data['path']}: {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"🚨 Network error sending {file_data['path']}: {e}")


def scan_home_directory():
    home_dir = os.path.expanduser("~")
    scanned_count = 0

    for root, _, files in os.walk(home_dir):
       
        if any(folder.startswith('.') or folder in EXCLUDED_DIRS for folder in root.split(os.sep)):
            continue

        for file in files:
            if file.startswith('.') or file.startswith('_'):  
                continue  

            file_path = os.path.join(root, file)

      
            if os.path.splitext(file)[1].lower() in EXCLUDED_FILE_TYPES:
                continue

            try:
              
                stat_info = os.stat(file_path, follow_symlinks=True)
                file_size = stat_info.st_size
                last_access_time = datetime.datetime.fromtimestamp(stat_info.st_atime)

              
                file_hash = generate_hash(file_path)
                if not file_hash:
                    continue  

              
                category = categorize_file(file)

              
                file_data = {
                    "device_id": DEVICE_ID,
                    "username": USERNAME,
                    "name": file,
                    "path": file_path,
                    "size": file_size,
                    "hash": file_hash,
                    "category": category,
                    "last_access": last_access_time.isoformat()
                }

              
                send_to_api(file_data)

              
                scanned_count += 1
                if scanned_count == 50:
                    logging.info(" Scanned 50 files, stopping for now...")
                    return

            except Exception as e:
                logging.error(f"Error processing {file_path}: {e}")


if __name__ == '__main__':
    scan_home_directory()


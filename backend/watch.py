import os
import hashlib
import datetime
import requests
import json
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from google import genai
from google.genai import types
import imagehash
from PIL import Image
import PIL
from dotenv import load_dotenv
import threading

load_dotenv()
geminkey = os.getenv("gemini_key")


from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']  # Modify scope if needed

def authenticate_drive():
    creds = None

    # Load saved credentials if they exist
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If no valid credentials, request authentication
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("/home/shiv/programming/hackathon/smart-file-organiser/client_secret_420192572773-igkcgfbj8i3f4audaolfebnoaj0fiaqe.apps.googleusercontent.com.json", SCOPES)
        
        # Since it's a desktop app, we use `run_console()` instead of a local server
        creds = flow.run_local_server(port=0)

        # Save credentials for future use
        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())

    return creds

def upload_file(file_path):
    creds = authenticate_drive()
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaFileUpload(file_path, resumable=True)

    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"File uploaded successfully! File ID: {file.get('id')}")


logging.basicConfig(filename="scanner.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# API Config
API_URL = "http://192.168.134.67:5000"  
DEVICE_ID = "device_002" 
USERNAME = "shiv"  

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





def generate_hash(file_path):
    """Generate a SHA-256 or perceptual hash based on file type"""
    try:
        # Check if the file is an image
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')):
            with Image.open(file_path) as img:
                return str(imagehash.phash(img))  # Perceptual hash
        else:
            # For non-image files, use SHA-256
            hasher = hashlib.sha256()
            with open(file_path, "rb") as f:
                while chunk := f.read(4096):
                    hasher.update(chunk)
            return hasher.hexdigest()
    except Exception as e:
        print(f"Error generating hash for {file_path}: {e}")
        return None

TRASH_DIRS = [
    os.path.expanduser("~/.local/share/Trash/files"),  # Linux
    os.path.expanduser("~/.Trash"),  # macOS
    "C:\\$Recycle.Bin"  # Windows (may require admin permissions)
]


def categorize_file(filename):
    return EXT_TO_CATEGORY.get(os.path.splitext(filename)[1].lower(), 'others')


def send_to_api(file_data):
    try:
        response = requests.post(API_URL+"/upload", json=file_data, timeout=5)
        data = response.json()
        if response.status_code == 201:
            logging.info(f"Sent: {file_data['path']}")
            if file_data['category'] == "images":
                image = PIL.Image.open(file_data['path'])
                client = genai.Client(api_key=geminkey)
                response = client.models.generate_content(model="gemini-2.0-flash",contents=["What is this image?", image])
                requests.post(API_URL+"/image/upload",json={
                     "device_id": file_data["device_id"],
                    "username": file_data["username"],
                    "name": file_data["name"],
                    "path": file_data["path"],
                    "response": response.text.lower()
                },timeout=5)
                print(response.text + "/n/n")


        elif response.status_code == 409:
            logging.info(f" Already exists: {file_data['path']}")
            if data["clean"]:
                try:
                    os.remove(file_data['path'])
                except:
                    print("failed")
        else:
            logging.error(f"Failed to send {file_data['path']}: {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f" Network error sending {file_data['path']}: {e}")

def del_to_api(filename):
    try:
        file_data = {
                    "device_id": DEVICE_ID,
                    "username": USERNAME,
                    "name": filename
                }
        response = requests.post(API_URL+"/delete", json=file_data, timeout=5)
        if response.status_code == 201:
            logging.info(f"delete: {file_data['name']}")
        elif response.status_code == 409:
            logging.info(f" doesnt exists: {file_data['name']}")
        else:
            logging.error(f"Failed to del {file_data['name']}: {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error sending {file_data['name']}: {e}")


def mov_to_api(filename,old,new):
    try:
        file_data = {
                    "device_id": DEVICE_ID,
                    "username": USERNAME,
                    "name": filename,
                    "old":old,
                    "new":new
                }
        response = requests.post(API_URL+"/mov", json=file_data, timeout=5)
        if response.status_code == 201:
            logging.info(f"move: {file_data['name']}")
        elif response.status_code == 409:
            logging.info(f" doesnt exists: {file_data['name']}")
        else:
            logging.error(f"Failed to mov {file_data['name']}: {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error sending {file_data['name']}: {e}")

def acc_to_api(filename,dates):
    try:
        file_data = {
                    "device_id": DEVICE_ID,
                    "username": USERNAME,
                    "name": filename,
                    "date": dates
                }
        response = requests.post(API_URL+"/acc", json=file_data, timeout=5)
        if response.status_code == 201:
            logging.info(f"access: {file_data['name']}")
        elif response.status_code == 409:
            logging.info(f" doesnt exists: {file_data['name']}")
        else:
            logging.error(f"Failed to update {file_data['name']}: {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error sending {file_data['name']}: {e}")


def scan_home_directory():
    #home_dir = os.path.expanduser("~")
    #scanned_count = 0
    home_dir = "/home/shiv/programming/hackathon/smart-file-organiser/test"

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

              
                # scanned_count += 1
                # if scanned_count == 50:
                #     logging.info(" Scanned 50 files, stopping for now...")
                #     return

            except Exception as e:
                logging.error(f"Error processing {file_path}: {e}")



class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        file_path = event.src_path
        file = os.path.basename(file_path)

        # Check if any parent directory is hidden
        parts = file_path.split(os.sep)  # Split path into parts
        if any(part.startswith('.') for part in parts):
            logging.info(f"Excluded: {file_path} (inside hidden directory)")
            return  

        # Exclude unwanted file types
        if os.path.splitext(file)[1].lower() in EXCLUDED_FILE_TYPES:
            logging.info(f"Excluded file type: {file_path}")
            return 

        # Wait to ensure the file is fully written
        time.sleep(1)

        try:
            stat_info = os.stat(file_path, follow_symlinks=True)
            file_size = stat_info.st_size
            last_access_time = datetime.datetime.fromtimestamp(stat_info.st_atime)

            # Generate hash (if file is readable)
            file_hash = generate_hash(file_path) or "failed"

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
        except Exception as e:
            logging.error(f"Failed to process {file_path}: {e}")
    
    def on_modified(self, event):
        """Trigger when a file is opened (read access detected)."""
        if event.is_directory:
            return
        file_path = event.src_path
        file = os.path.basename(file_path)
        if file=="scanner.log":
            return

        # Check if any parent directory is hidden
        parts = file_path.split(os.sep)  # Split path into parts
        if any(part.startswith('.') for part in parts):
            logging.info(f"Excluded: {file_path} (inside hidden directory)")
            return  

        # Exclude unwanted file types
        if os.path.splitext(file)[1].lower() in EXCLUDED_FILE_TYPES:
            logging.info(f"Excluded file type: {file_path}")
            return 

        logging.info(f"Access detected: {file_path}")
        acc_to_api(file,datetime.datetime.now().isoformat())

    def on_moved(self, event):
    
        src_path = os.path.abspath(event.src_path)  # Ensure absolute path
        dest_path = os.path.abspath(event.dest_path)  # Ensure absolute path
        file = os.path.basename(src_path)

    # Check if moved file is in any known trash folder
        if any(dest_path.startswith(os.path.abspath(trash)) for trash in TRASH_DIRS):
            logging.info(f"File moved to trash: {file}")
            del_to_api(file)
            return

        logging.info(f"File moved: {src_path} → {dest_path}")
        mov_to_api(file, src_path, dest_path)



    def on_deleted(self,event):
        file_path = event.src_path
        file = os.path.basename(file_path)

        parts = file_path.split(os.sep)  
        if any(part.startswith('.') for part in parts):
            return  

        if os.path.splitext(file)[1].lower() in EXCLUDED_FILE_TYPES:
            return 

    
        time.sleep(1)
        try:
            del_to_api(file)
        except Exception as e:
            logging.error(f"Failed to process {file_path}: {e}")


def monitor():
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler,os.path.expanduser("~"),recursive=True)
    observer.start()
    try: 
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

        



TASKS_API = API_URL + "/tasks"
COMPLETE_TASK_API = API_URL + "/task/done"

def process_task(task):
    print(f"Processing {task['action']} for {task['path']}")
    
    if task["action"] == "sync":
        upload_file(task["path"])
    elif task["action"] == "archive":
        os.rename(task["path"], task["path"] + ".archived")

    # Mark task as done
    requests.post(COMPLETE_TASK_API + f"/{task['id']}")

def poll_tasks():
    while True:
        try:
            response = requests.get(TASKS_API)
            tasks = response.json()

            if tasks:
                threads = []
                for task in tasks:
                    t = threading.Thread(target=process_task, args=(task,))
                    t.start()
                    threads.append(t)
                
                for t in threads:
                    t.join()
        except Exception as e:
            print(f"Error fetching tasks: {e}")
        
        time.sleep(5)

if __name__ == '__main__':
    scan_home_directory()
    threading.Thread(target=poll_tasks, daemon=True).start()
    monitor()




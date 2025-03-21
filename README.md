# Smart File Organizer

## Overview

Smart File Organizer is a system that helps users manage and organize their files efficiently. It consists of three main components:

1. **Frontend** - A user-friendly interface for interaction.
2. **Backend** - Handles requests and processes data.
3. **Watch Script (Watchdog)** - Monitors file changes locally on the user's device.

## Features

- **Real-time File Monitoring**: The Watchdog script runs on user devices and tracks file-related operations.
- **Folder-Specific Demonstration**: Initially designed to manage all files, but for demo purposes, it is restricted to a specific folder.
- **Google Drive Sync**: Users can sync their files with Google Drive when triggered from the backend.
- **Data Privacy**: Files never leave the user's ecosystem. The system only processes metadata, ensuring data security.
- **Image Scanning with Transformers**: The Watchdog script can analyze images using Gemini api to extract information without sending the image to the backend.

## Setup and Installation

### Prerequisites

- Python 3.x
- Required Python libraries: `watchdog`, `requests`
- A Google Cloud Platform (GCP) project with OAuth credentials for Google Sign-In

### Backend Setup

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd smart-file-organizer/backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the backend server:
   ```bash
   python main.py
   ```

### Watchdog Script Setup

1. Modify the script to include the backend IP address.
2. Run the script on the user's device:
   ```bash
   python watch.py
   ```

### Google Drive Integration

- The user must sign in with their Google account for the first-time setup.
- Since this is a test app, users need to verify themselves as test users.
- Once the app is verified by Google, this step will be skipped.
- The GCP client token is required for authentication.

## Testing Sync and Archive Actions

To test Google Drive sync and archive actions manually, run:

```python
import requests
requests.post("http://<backend_ip>:5000/task", json={
    "device_id": "device_001",
    "username": "shiv",
    "action": "sync",
    "path": "path_to_the_file"
})
```

Replace `<backend_ip>` with the actual backend server IP.

## Observations

- The Watchdog script has monitored various file operations over 6-7 hours, capturing key file-related activities. The log data is stored in `scanner.log`.
- The system ensures privacy as all file operations occur on the user's device or Google Drive.

## Future Improvements

- Implement sync and archive actions in the frontend.
- Enhance UI/UX for better user interaction.
- Automate Google Drive authentication post-app verification.

## Contribution

Feel free to submit issues or contribute by creating pull requests.

## License

[Specify the license here]


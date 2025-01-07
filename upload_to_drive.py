import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# Load token.pickle yang sudah disiapkan sebelumnya
TOKEN_PATH = 'token.pickle'

if not os.path.exists(TOKEN_PATH):
    print("Error: token.pickle file not found")
    exit(1)

with open(TOKEN_PATH, 'rb') as token:
    creds = pickle.load(token)

if creds.expired and creds.refresh_token:
    creds.refresh(Request())

# Initialize Google Drive API
service = build('drive', 'v3', credentials=creds)

# Fungsi untuk meng-upload file ke Google Drive
def upload_to_drive(file_path, folder_id="root"):
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    file_id = file.get('id')
    permission = {
        'type': 'anyone',
        'role': 'reader'
    }
    service.permissions().create(fileId=file_id, body=permission).execute()

    link = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
    return link

# Folder ID di Google Drive tempat file akan diupload
folder_id = '1MiWsyPAOiMYko6Jp2pDXMf614nuwPWe_'  # Ganti dengan folder ID yang sesuai

# Menelusuri folder dan meng-upload file satu per satu
extracted_folder = 'extracted'
for root, dirs, files in os.walk(extracted_folder):
    for file in files:
        file_path = os.path.join(root, file)
        print(f"Uploading {file_path} to Google Drive...")
        link = upload_to_drive(file_path, folder_id)
        print(f"File uploaded. Download link: {link}")

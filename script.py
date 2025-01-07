import os
import sys
import rarfile
import zipfile
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials


# Fungsi untuk autentikasi Google Drive
def authenticate_gdrive():
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    creds = Credentials.from_authorized_user_file('token.pickle', SCOPES)
    return build('drive', 'v3', credentials=creds)


# Fungsi untuk mengunggah file ke Google Drive
def upload_to_gdrive(service, file_path, parent_folder_id=None):
    file_metadata = {'name': os.path.basename(file_path)}
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]
    
    media = MediaFileUpload(file_path, resumable=True)
    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    print(f"File '{file_path}' uploaded to Google Drive with ID: {uploaded_file.get('id')}")


# Fungsi untuk mengekstrak file RAR/ZIP
def extract_file(archive_path):
    extracted_files = []
    extract_dir = os.path.splitext(archive_path)[0]  # Nama folder hasil ekstraksi

    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)

    # Ekstraksi file RAR
    if archive_path.endswith(".rar"):
        try:
            with rarfile.RarFile(archive_path) as rf:
                rf.extractall(extract_dir)
                extracted_files.extend(rf.namelist())
        except Exception as e:
            print(f"Error extracting RAR {archive_path}: {e}")

    # Ekstraksi file ZIP
    elif archive_path.endswith(".zip"):
        try:
            with zipfile.ZipFile(archive_path) as zf:
                zf.extractall(extract_dir)
                extracted_files.extend(zf.namelist())
        except Exception as e:
            print(f"Error extracting ZIP {archive_path}: {e}")

    # Return path lengkap untuk semua file yang diekstrak
    return [os.path.join(extract_dir, f) for f in extracted_files]


# Fungsi utama
def main(archive_path):
    # Autentikasi ke Google Drive
    gdrive_service = authenticate_gdrive()

    # Ekstrak file RAR/ZIP
    print(f"Processing archive: {archive_path}")
    extracted_files = extract_file(archive_path)

    # Upload semua file yang berhasil diekstrak
    if extracted_files:
        for file_path in extracted_files:
            print(f"Uploading {file_path} to Google Drive...")
            upload_to_gdrive(gdrive_service, file_path)
    else:
        print(f"No files extracted from {archive_path}. Skipping upload.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 script.py <path_to_archive>")
        sys.exit(1)

    archive_file = sys.argv[1]

    if not os.path.exists(archive_file):
        print(f"File {archive_file} does not exist.")
        sys.exit(1)

    main(archive_file)

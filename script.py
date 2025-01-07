import os
import sys
import rarfile
import zipfile
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# Fungsi untuk mengunggah file ke Google Drive
def upload_to_drive(file_path, folder_id=None):
    credentials = Credentials.from_authorized_user_file("token.pickle", ["https://www.googleapis.com/auth/drive"])
    service = build("drive", "v3", credentials=credentials)

    file_metadata = {"name": os.path.basename(file_path)}
    if folder_id:
        file_metadata["parents"] = [folder_id]

    media = MediaFileUpload(file_path, resumable=True)
    uploaded_file = service.files().create(body=file_metadata, media_body=media, fields="id, webViewLink").execute()
    return uploaded_file.get("webViewLink")

# Fungsi untuk membuat folder di Google Drive jika belum ada
def check_and_create_folder(folder_name="Extracted Files"):
    credentials = Credentials.from_authorized_user_file("token.pickle", ["https://www.googleapis.com/auth/drive"])
    service = build("drive", "v3", credentials=credentials)

    # Cek apakah folder sudah ada
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]

    # Jika folder belum ada, buat folder baru
    file_metadata = {"name": folder_name, "mimeType": "application/vnd.google-apps.folder"}
    folder = service.files().create(body=file_metadata, fields="id").execute()
    return folder["id"]

# Fungsi untuk mengekstrak file
def extract_file(archive_path):
    extracted_files = []
    extract_dir = os.path.splitext(archive_path)[0]

    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)

    # Ekstrak file RAR
    if archive_path.endswith(".rar"):
        with rarfile.RarFile(archive_path) as rf:
            rf.extractall(extract_dir)
            extracted_files.extend(rf.namelist())

    # Ekstrak file ZIP
    elif archive_path.endswith(".zip"):
        with zipfile.ZipFile(archive_path) as zf:
            zf.extractall(extract_dir)
            extracted_files.extend(zf.namelist())

    # Tambahkan path lengkap untuk setiap file
    return [os.path.join(extract_dir, f) for f in extracted_files]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide the archive file name as an argument.")
        exit(1)

    archive = sys.argv[1]
    if not os.path.exists(archive):
        print(f"Error: {archive} does not exist.")
        exit(1)

    print(f"Extracting {archive}...")
    extracted_files = extract_file(archive)

    if not extracted_files:
        print(f"No files extracted from {archive}. Skipping upload.")
        exit(1)

    print(f"Uploading extracted files from {archive} to Google Drive...")

    folder_id = check_and_create_folder()
    for extracted_file in extracted_files:
        if os.path.exists(extracted_file):
            print(f"Uploading {extracted_file}...")
            link = upload_to_drive(extracted_file, folder_id)
            print(f"File uploaded successfully. Download it at: {link}")
        else:
            print(f"Error: {extracted_file} does not exist.")

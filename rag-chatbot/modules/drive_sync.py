# drive_sync.py
import os
import json
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from modules.document_loader import load_document_chunks
from modules.embed import upsert_documents_to_pinecone
from utils.env_loader import get_env_var

# Constants
DRIVE_FOLDER_ID = get_env_var("DRIVE_FOLDER_ID")
RAW_DIR = os.path.join("data", "raw")
PROCESSED_LOG = os.path.join("data", "processed_files.json")
# SERVICE_ACCOUNT_FILE = get_env_var("SERVICE_ACCOUNT_FILE")


service_account_info = {
    "type": os.getenv("TYPE"),
    "project_id": os.getenv("PROJECT_ID"),
    "private_key_id": os.getenv("PRIVATE_KEY_ID"),
    "private_key": os.getenv("PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("CLIENT_EMAIL"),
    "client_id": os.getenv("CLIENT_ID"),
    "auth_uri": os.getenv("AUTH_URI"),
    "token_uri": os.getenv("TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("UNIVERSE_DOMAIN"),
}
# Ensure raw folder exists
os.makedirs(RAW_DIR, exist_ok=True)

def load_processed_files():
    if os.path.exists(PROCESSED_LOG):
        with open(PROCESSED_LOG, "r") as f:
            return json.load(f)
    return []

def save_processed_files(file_list):
    with open(PROCESSED_LOG, "w") as f:
        json.dump(file_list, f, indent=2)

def download_drive_files():
    print("🔐 Authenticating Google Drive service account...")
    creds = creds = service_account.Credentials.from_service_account_info(service_account_info)
    drive_service = build("drive", "v3", credentials=creds)

    processed_files = load_processed_files()
    updated_processed = processed_files.copy()

    print("🔎 Fetching files from Google Drive...")
    query = f"'{DRIVE_FOLDER_ID}' in parents and mimeType='application/pdf'"
    results = drive_service.files().list(q=query, pageSize=100).execute()
    files = results.get('files', [])

    if not files:
        print("⚠️ No files found in the Drive folder.")
        return

    for file in files:
        file_name = file['name']
        if file_name in processed_files:
            continue  # Already handled

        file_id = file['id']
        print(f"📥 Downloading new file: {file_name}")

        # Download to data/raw/
        file_path = os.path.join(RAW_DIR, file_name)
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.FileIO(file_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        print(f"📄 Extracting + chunking: {file_name}")
        try:
            chunks = load_document_chunks(file_path)
            if chunks:
                print(f"📌 Embedding & storing {len(chunks)} chunks in Pinecone...")
                upsert_documents_to_pinecone(chunks, file_id=file_name.replace(".pdf", ""))
                updated_processed.append(file_name)
            else:
                print(f"⚠️ No chunks extracted from: {file_name}")
        except Exception as e:
            print(f"❌ Error processing {file_name}: {e}")

    save_processed_files(updated_processed)
    print("✅ Drive sync complete.")

if __name__ == "__main__":
    download_drive_files()
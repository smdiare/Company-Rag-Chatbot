from modules.query_handler import handle_query
from modules.drive_sync import download_drive_files  # 👈 Import the sync function

if __name__ == "__main__":
    print("🔄 Syncing files from Google Drive...")
    download_drive_files()  # ✅ Step 1: auto sync and embed new PDFs

    print("✅ Ready. Ask me anything about company policies or documents.")

    while True:
        q = input("\n❓ Ask a question (or type 'exit'): ")
        if q.lower() == 'exit':
            break
        print("\n💬 Answer:", handle_query(q))

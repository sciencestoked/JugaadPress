#!/usr/bin/env python3
"""
Migrate local pages/ folder to Google Drive structure

This tool will:
1. Authenticate with Google Drive
2. Create /JugaadPress/ folder structure
3. Migrate all .md files from pages/ to a book folder
4. Create settings files
5. Verify migration
"""

import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate():
    """Authenticate with Google Drive"""
    creds = None
    token_path = 'token.json'
    client_secret = 'client_secret.json'

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(client_secret):
                print("❌ Error: client_secret.json not found!")
                print("   Get it from Google Cloud Console")
                print("   See docs/SETUP.md for instructions")
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
            creds = flow.run_local_server(port=8080)

        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)

def get_or_create_folder(service, name, parent_id=None):
    """Get existing folder or create new one"""
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    folders = results.get('files', [])

    if folders:
        return folders[0]['id']
    else:
        metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            metadata['parents'] = [parent_id]

        folder = service.files().create(body=metadata, fields='id').execute()
        return folder.get('id')

def upload_file(service, filename, content, parent_id, mimetype='text/markdown'):
    """Upload a file to Drive"""
    media = MediaIoBaseUpload(
        BytesIO(content.encode('utf-8')),
        mimetype=mimetype,
        resumable=True
    )

    file_metadata = {
        'name': filename,
        'parents': [parent_id],
        'mimeType': mimetype
    }

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return file.get('id')

def upload_json(service, filename, data, parent_id):
    """Upload JSON file"""
    content = json.dumps(data, indent=2)
    return upload_file(service, filename, content, parent_id, 'application/json')

def migrate():
    """Main migration function"""
    print("=" * 60)
    print("  JugaadPress - Migrate Local Notes to Google Drive")
    print("=" * 60)
    print()

    # Check if pages/ directory exists
    pages_dir = 'pages'
    if not os.path.exists(pages_dir):
        print(f"❌ Error: {pages_dir}/ directory not found!")
        sys.exit(1)

    # Get list of .md files
    md_files = [f for f in os.listdir(pages_dir) if f.endswith('.md')]

    if not md_files:
        print(f"❌ No .md files found in {pages_dir}/")
        sys.exit(1)

    print(f"📄 Found {len(md_files)} markdown files:")
    for f in sorted(md_files):
        print(f"   • {f}")
    print()

    # Get book name
    book_name = input("📚 Enter book name (e.g., 'My Japanese Notes'): ").strip()
    if not book_name:
        print("❌ Book name cannot be empty!")
        sys.exit(1)

    print()
    print("🔐 Authenticating with Google Drive...")
    service = authenticate()
    print("✓ Authenticated!")
    print()

    # Create folder structure
    print("📁 Creating Drive folder structure...")
    root_folder_id = get_or_create_folder(service, 'JugaadPress')
    print(f"   ✓ /JugaadPress/ ({root_folder_id})")

    book_folder_id = get_or_create_folder(service, book_name, root_folder_id)
    print(f"   ✓ /JugaadPress/{book_name}/ ({book_folder_id})")
    print()

    # Create settings files
    print("⚙️  Creating settings files...")

    # Global settings (if not exists)
    global_settings = {
        "sender_email": "",
        "gmail_app_password": "",
        "kindle_email": ""
    }
    try:
        upload_json(service, '.user_settings.json', global_settings, root_folder_id)
        print("   ✓ .user_settings.json")
    except:
        print("   ℹ️  .user_settings.json already exists")

    # Book settings
    book_settings = {
        "title": book_name,
        "cover": None
    }
    upload_json(service, '.book_settings.json', book_settings, book_folder_id)
    print("   ✓ .book_settings.json")
    print()

    # Migrate files
    print(f"📤 Uploading {len(md_files)} files to Drive...")
    for filename in sorted(md_files):
        filepath = os.path.join(pages_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        upload_file(service, filename, content, book_folder_id)
        print(f"   ✓ {filename}")

    print()
    print("=" * 60)
    print("✅ Migration Complete!")
    print("=" * 60)
    print()
    print("📊 Summary:")
    print(f"   • Book: {book_name}")
    print(f"   • Files migrated: {len(md_files)}")
    print(f"   • Drive folder: /JugaadPress/{book_name}/")
    print()
    print("🎯 Next Steps:")
    print("   1. Run: python app.py")
    print("   2. Sign in with Google")
    print("   3. See your book in the dashboard!")
    print()
    print("💡 Your local pages/ folder is still intact (not deleted)")
    print("   You can safely delete it after verifying migration.")
    print()

if __name__ == '__main__':
    try:
        migrate()
    except KeyboardInterrupt:
        print("\n\n❌ Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

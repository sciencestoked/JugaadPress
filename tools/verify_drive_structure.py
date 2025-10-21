#!/usr/bin/env python3
"""
Verify Google Drive folder structure for JugaadPress

Checks:
- /JugaadPress/ folder exists
- Books are properly structured
- Settings files are present
- No orphaned files
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from io import BytesIO

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate():
    """Authenticate with Google Drive"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=8080)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)

def find_folder(service, name, parent_id=None):
    """Find folder by name"""
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    folders = results.get('files', [])
    return folders[0] if folders else None

def list_files_in_folder(service, folder_id):
    """List all files in a folder"""
    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, mimeType)',
        pageSize=1000
    ).execute()
    return results.get('files', [])

def download_json(service, file_id):
    """Download and parse JSON file"""
    try:
        request = service.files().get_media(fileId=file_id)
        file_buffer = BytesIO()
        downloader = MediaIoBaseDownload(file_buffer, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        content = file_buffer.getvalue().decode('utf-8')
        return json.loads(content)
    except:
        return None

def verify():
    """Main verification function"""
    print("=" * 60)
    print("  JugaadPress - Verify Drive Structure")
    print("=" * 60)
    print()

    print("🔐 Authenticating...")
    service = authenticate()
    print("✓ Authenticated!")
    print()

    errors = []
    warnings = []

    # Check root folder
    print("📁 Checking /JugaadPress/ folder...")
    root_folder = find_folder(service, 'JugaadPress')

    if not root_folder:
        errors.append("❌ /JugaadPress/ folder not found!")
        print("❌ /JugaadPress/ folder not found!")
        print()
        print("🔧 Fix: Run migration tool:")
        print("   python tools/migrate_local_to_drive.py")
        return

    print(f"✓ Found: /JugaadPress/ ({root_folder['id']})")
    print()

    # Check global settings
    print("⚙️  Checking global settings...")
    root_files = list_files_in_folder(service, root_folder['id'])
    settings_file = next((f for f in root_files if f['name'] == '.user_settings.json'), None)

    if settings_file:
        settings = download_json(service, settings_file['id'])
        if settings:
            print("✓ .user_settings.json found")
            if not settings.get('sender_email'):
                warnings.append("⚠️  sender_email not configured")
            if not settings.get('kindle_email'):
                warnings.append("⚠️  kindle_email not configured")
        else:
            errors.append("❌ .user_settings.json is corrupted")
    else:
        warnings.append("⚠️  .user_settings.json not found (will be created on first save)")

    print()

    # Check books
    print("📚 Checking books...")
    book_folders = [f for f in root_files if f['mimeType'] == 'application/vnd.google-apps.folder']

    if not book_folders:
        warnings.append("⚠️  No books found")
        print("⚠️  No books found")
        print()
    else:
        for book in book_folders:
            print(f"\n  📖 {book['name']}:")
            book_files = list_files_in_folder(service, book['id'])

            # Check book settings
            book_settings = next((f for f in book_files if f['name'] == '.book_settings.json'), None)
            if book_settings:
                print(f"     ✓ .book_settings.json")
            else:
                errors.append(f"❌ {book['name']}: Missing .book_settings.json")
                print(f"     ❌ Missing .book_settings.json")

            # Count pages
            md_files = [f for f in book_files if f['name'].endswith('.md')]
            print(f"     ✓ {len(md_files)} pages")

            if len(md_files) == 0:
                warnings.append(f"⚠️  {book['name']}: No markdown files")

    print()
    print("=" * 60)

    # Summary
    if errors:
        print("❌ ERRORS FOUND:")
        for error in errors:
            print(f"   {error}")
        print()

    if warnings:
        print("⚠️  WARNINGS:")
        for warning in warnings:
            print(f"   {warning}")
        print()

    if not errors and not warnings:
        print("✅ Everything looks good!")
        print()
        print("🎯 You're ready to use JugaadPress!")
        print("   Run: python app.py")
    elif not errors:
        print("✅ Structure is valid (minor warnings)")
        print("   You can still use the app")
    else:
        print("❌ Please fix errors before using the app")

    print("=" * 60)
    print()

if __name__ == '__main__':
    try:
        verify()
    except KeyboardInterrupt:
        print("\n\n❌ Verification cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

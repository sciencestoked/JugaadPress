"""
JugaadPress Web Application
Web-based version with Google OAuth and multi-book support
"""

import os
import json
import time
import re
from io import BytesIO
from flask import Flask, request, render_template, jsonify, session, redirect, url_for, send_file
from functools import wraps
import secrets
import logging
import markdown2

# Google OAuth imports
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Generate a consistent secret key (stored in file for persistence)
SECRET_KEY_FILE = 'secret_key.txt'
if os.path.exists(SECRET_KEY_FILE):
    with open(SECRET_KEY_FILE, 'r') as f:
        app.secret_key = f.read().strip()
else:
    app.secret_key = secrets.token_hex(32)
    with open(SECRET_KEY_FILE, 'w') as f:
        f.write(app.secret_key)

# Session configuration for OAuth
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

# Google OAuth Configuration
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/drive.file'
]

CLIENT_SECRETS_FILE = "client_secret.json"
REDIRECT_URI = "http://localhost:5001/oauth2callback"

# ============================================================================
# HELPER CLASSES
# ============================================================================

class DriveManager:
    """Manages Google Drive operations for a user"""

    def __init__(self, credentials):
        self.service = build('drive', 'v3', credentials=credentials)
        self.root_folder_id = None

    def _retry_on_error(self, func, *args, **kwargs):
        """Retry API calls with exponential backoff"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except HttpError as e:
                if e.resp.status in [500, 502, 503, 504]:
                    # Server errors - retry
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 1
                        logger.warning(f"Drive API error {e.resp.status}, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                logger.error(f"Drive API error: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise

    def _get_or_create_folder(self, name, parent_id=None):
        """Get existing folder or create new one"""
        def _execute():
            query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            if parent_id:
                query += f" and '{parent_id}' in parents"

            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()

            folders = results.get('files', [])

            if folders:
                logger.info(f"Found existing folder: {name}")
                return folders[0]['id']
            else:
                logger.info(f"Creating new folder: {name}")
                metadata = {
                    'name': name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                if parent_id:
                    metadata['parents'] = [parent_id]

                folder = self.service.files().create(
                    body=metadata,
                    fields='id'
                ).execute()

                return folder.get('id')

        return self._retry_on_error(_execute)

    def initialize_user_folder(self):
        """Create /JugaadPress/ folder structure"""
        self.root_folder_id = self._get_or_create_folder('JugaadPress')
        return self.root_folder_id

    def list_books(self):
        """List all book folders"""
        def _execute():
            query = f"'{self.root_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"

            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, modifiedTime)',
                orderBy='name'
            ).execute()

            books = []
            for folder in results.get('files', []):
                # Skip hidden folders (starting with .)
                if folder['name'].startswith('.'):
                    continue

                # Count pages in this book
                page_count = self._count_pages_in_folder(folder['id'])

                books.append({
                    'name': folder['name'],
                    'id': folder['id'],
                    'pageCount': page_count,
                    'lastModified': folder.get('modifiedTime')
                })

            logger.info(f"Listed {len(books)} books from Drive")
            return books

        return self._retry_on_error(_execute)

    def _count_pages_in_folder(self, folder_id):
        """Count .md files in a folder"""
        query = f"'{folder_id}' in parents and name contains '.md' and trashed=false"

        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id)'
        ).execute()

        return len(results.get('files', []))

    def create_book(self, book_name):
        """Create a new book folder"""
        book_id = self._get_or_create_folder(book_name, self.root_folder_id)

        # Create initial settings file
        settings = {
            'title': book_name,
            'cover': None
        }
        self._write_json_file(f'.book_settings.json', settings, book_id)

        return book_id

    def delete_book(self, book_name):
        """Delete a book folder (move to trash)"""
        book_id = self._get_book_id(book_name)
        if not book_id:
            return False

        self.service.files().update(
            fileId=book_id,
            body={'trashed': True}
        ).execute()

        return True

    def _get_book_id(self, book_name):
        """Get folder ID for a book"""
        query = f"name='{book_name}' and '{self.root_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"

        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id)'
        ).execute()

        folders = results.get('files', [])
        return folders[0]['id'] if folders else None

    def get_book_settings(self, book_name):
        """Read book settings from .book_settings.json"""
        book_id = self._get_book_id(book_name)
        if not book_id:
            return {}

        return self._read_json_file('.book_settings.json', book_id) or {'title': book_name}

    def save_book_settings(self, book_name, settings):
        """Save book settings"""
        book_id = self._get_book_id(book_name)
        if not book_id:
            return False

        return self._write_json_file('.book_settings.json', settings, book_id)

    def get_global_settings(self):
        """Read global settings from .user_settings.json"""
        return self._read_json_file('.user_settings.json', self.root_folder_id) or {}

    def save_global_settings(self, settings):
        """Save global settings"""
        return self._write_json_file('.user_settings.json', settings, self.root_folder_id)

    def _read_json_file(self, filename, parent_id):
        """Read JSON file from Drive"""
        try:
            # Find file
            query = f"name='{filename}' and '{parent_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id)'
            ).execute()

            files = results.get('files', [])
            if not files:
                return None

            file_id = files[0]['id']

            # Download content
            from googleapiclient.http import MediaIoBaseDownload

            request = self.service.files().get_media(fileId=file_id)
            file_buffer = BytesIO()
            downloader = MediaIoBaseDownload(file_buffer, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            content = file_buffer.getvalue().decode('utf-8')
            return json.loads(content)

        except Exception as e:
            logger.error(f"Error reading JSON file {filename}: {e}")
            return None

    def _write_json_file(self, filename, data, parent_id):
        """Write JSON file to Drive"""
        try:
            from googleapiclient.http import MediaIoBaseUpload

            content = json.dumps(data, indent=2)
            media = MediaIoBaseUpload(
                BytesIO(content.encode('utf-8')),
                mimetype='application/json',
                resumable=True
            )

            # Check if file exists
            query = f"name='{filename}' and '{parent_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id)'
            ).execute()

            files = results.get('files', [])

            if files:
                # Update existing
                self.service.files().update(
                    fileId=files[0]['id'],
                    media_body=media
                ).execute()
            else:
                # Create new
                file_metadata = {
                    'name': filename,
                    'parents': [parent_id],
                    'mimeType': 'application/json'
                }
                self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()

            return True

        except Exception as e:
            logger.error(f"Error writing JSON file {filename}: {e}")
            return False

    def list_pages(self, book_name):
        """List all pages in a book"""
        def _execute():
            book_id = self._get_book_id(book_name)
            if not book_id:
                return []

            query = f"'{book_id}' in parents and name contains '.md' and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                orderBy='name'
            ).execute()

            pages = [f['name'] for f in results.get('files', []) if f['name'].endswith('.md')]
            logger.info(f"Found {len(pages)} pages in book: {book_name}")
            return pages

        return self._retry_on_error(_execute)

    def read_page(self, book_name, filename):
        """Read content of a page"""
        def _execute():
            book_id = self._get_book_id(book_name)
            if not book_id:
                return None

            # Find file
            query = f"name='{filename}' and '{book_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id)'
            ).execute()

            files = results.get('files', [])
            if not files:
                return None

            file_id = files[0]['id']

            # Download content
            from googleapiclient.http import MediaIoBaseDownload

            request = self.service.files().get_media(fileId=file_id)
            file_buffer = BytesIO()
            downloader = MediaIoBaseDownload(file_buffer, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            content = file_buffer.getvalue().decode('utf-8')
            return content

        return self._retry_on_error(_execute)

    def write_page(self, book_name, filename, content):
        """Write content to a page"""
        def _execute():
            from googleapiclient.http import MediaIoBaseUpload

            book_id = self._get_book_id(book_name)
            if not book_id:
                return False

            media = MediaIoBaseUpload(
                BytesIO(content.encode('utf-8')),
                mimetype='text/markdown',
                resumable=True
            )

            # Check if file exists
            query = f"name='{filename}' and '{book_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id)'
            ).execute()

            files = results.get('files', [])

            if files:
                # Update existing
                self.service.files().update(
                    fileId=files[0]['id'],
                    media_body=media
                ).execute()
                logger.info(f"Updated existing page: {filename}")
            else:
                # Create new
                file_metadata = {
                    'name': filename,
                    'parents': [book_id],
                    'mimeType': 'text/markdown'
                }
                self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                logger.info(f"Created new page: {filename}")

            return True

        return self._retry_on_error(_execute)

    def delete_page(self, book_name, filename):
        """Delete a page (move to trash)"""
        def _execute():
            book_id = self._get_book_id(book_name)
            if not book_id:
                return False

            # Find file
            query = f"name='{filename}' and '{book_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id)'
            ).execute()

            files = results.get('files', [])
            if not files:
                return False

            # Move to trash
            self.service.files().update(
                fileId=files[0]['id'],
                body={'trashed': True}
            ).execute()

            logger.info(f"Deleted page: {filename}")
            return True

        return self._retry_on_error(_execute)


# ============================================================================
# AUTHENTICATION DECORATORS
# ============================================================================

def login_required(f):
    """Decorator to require user login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'credentials' not in session:
            return redirect(url_for('landing'))
        return f(*args, **kwargs)
    return decorated_function


def get_drive_manager():
    """Get DriveManager instance for current user"""
    if 'credentials' not in session:
        return None

    credentials = Credentials(**session['credentials'])
    dm = DriveManager(credentials)
    dm.initialize_user_folder()
    return dm


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def landing():
    """Landing page"""
    if 'credentials' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')


@app.route('/login')
def login():
    """Initiate Google OAuth flow"""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    session['state'] = state
    session.permanent = True  # Make session persistent
    logger.info(f"OAuth flow initiated, state: {state}")
    return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    """Handle OAuth callback"""
    # Get state from session
    state = session.get('state')

    logger.info(f"OAuth callback received, state in session: {state}")
    logger.info(f"Request URL: {request.url}")

    if not state:
        logger.error("No state in session!")
        return """
        <h1>Session Expired</h1>
        <p>Your session expired. This can happen if you pressed the back button or took too long.</p>
        <p><a href="/">Click here to sign in again</a></p>
        """, 400

    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            state=state,
            redirect_uri=REDIRECT_URI
        )

        flow.fetch_token(authorization_response=request.url)

        credentials = flow.credentials
        session['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

        # Get user info
        from google.oauth2.credentials import Credentials as OAuthCredentials
        creds = OAuthCredentials(**session['credentials'])

        user_info_service = build('oauth2', 'v2', credentials=creds)
        user_info = user_info_service.userinfo().get().execute()

        session['user_email'] = user_info.get('email')
        session['user_name'] = user_info.get('name')
        session.permanent = True

        logger.info(f"User authenticated: {session['user_email']}")
        return redirect(url_for('dashboard'))

    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        return f"""
        <h1>Authentication Error</h1>
        <p>Error: {str(e)}</p>
        <p><a href="/">Click here to try again</a></p>
        """, 500


@app.route('/logout')
def logout():
    """Log out user"""
    session.clear()
    return redirect(url_for('landing'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')


# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/api/user')
@login_required
def api_user():
    """Get current user info"""
    return jsonify({
        'email': session.get('user_email'),
        'name': session.get('user_name')
    })


@app.route('/api/books', methods=['GET'])
@login_required
def api_list_books():
    """List all books"""
    try:
        dm = get_drive_manager()
        if not dm:
            return jsonify({'error': 'Not authenticated'}), 401

        books = dm.list_books()
        return jsonify(books)
    except Exception as e:
        logger.error(f"Error listing books: {e}")
        return jsonify({'error': 'Failed to list books from Drive'}), 500


@app.route('/api/books', methods=['POST'])
@login_required
def api_create_book():
    """Create new book"""
    try:
        data = request.get_json()
        book_name = data.get('name')

        if not book_name or not book_name.strip():
            return jsonify({'error': 'Book name required'}), 400

        dm = get_drive_manager()
        if not dm:
            return jsonify({'error': 'Not authenticated'}), 401

        logger.info(f"Creating book: {book_name}")
        book_id = dm.create_book(book_name.strip())

        return jsonify({'id': book_id, 'name': book_name}), 201
    except Exception as e:
        logger.error(f"Error creating book: {e}")
        return jsonify({'error': 'Failed to create book in Drive'}), 500


@app.route('/api/books/<book_name>', methods=['DELETE'])
@login_required
def api_delete_book(book_name):
    """Delete a book"""
    try:
        dm = get_drive_manager()
        if not dm:
            return jsonify({'error': 'Not authenticated'}), 401

        logger.info(f"Deleting book: {book_name}")
        success = dm.delete_book(book_name)

        if success:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': 'Book not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting book: {e}")
        return jsonify({'error': 'Failed to delete book'}), 500


@app.route('/api/books/<book_name>/settings', methods=['GET'])
@login_required
def api_get_book_settings(book_name):
    """Get book settings"""
    try:
        dm = get_drive_manager()
        if not dm:
            return jsonify({'error': 'Not authenticated'}), 401

        settings = dm.get_book_settings(book_name)
        return jsonify(settings)
    except Exception as e:
        logger.error(f"Error getting book settings: {e}")
        return jsonify({'error': 'Failed to load book settings'}), 500


@app.route('/api/books/<book_name>/settings', methods=['POST'])
@login_required
def api_save_book_settings(book_name):
    """Save book settings"""
    try:
        settings = request.get_json()
        dm = get_drive_manager()
        if not dm:
            return jsonify({'error': 'Not authenticated'}), 401

        logger.info(f"Saving settings for book: {book_name}")
        success = dm.save_book_settings(book_name, settings)

        if success:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': 'Failed to save settings'}), 500
    except Exception as e:
        logger.error(f"Error saving book settings: {e}")
        return jsonify({'error': 'Failed to save book settings'}), 500


@app.route('/api/settings/global', methods=['GET'])
@login_required
def api_get_global_settings():
    """Get global user settings"""
    try:
        dm = get_drive_manager()
        if not dm:
            return jsonify({'error': 'Not authenticated'}), 401

        settings = dm.get_global_settings()
        return jsonify(settings)
    except Exception as e:
        logger.error(f"Error getting global settings: {e}")
        return jsonify({'error': 'Failed to load global settings'}), 500


@app.route('/api/settings/global', methods=['POST'])
@login_required
def api_save_global_settings():
    """Save global user settings"""
    try:
        settings = request.get_json()
        dm = get_drive_manager()
        if not dm:
            return jsonify({'error': 'Not authenticated'}), 401

        logger.info("Saving global settings")
        success = dm.save_global_settings(settings)

        if success:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': 'Failed to save settings'}), 500
    except Exception as e:
        logger.error(f"Error saving global settings: {e}")
        return jsonify({'error': 'Failed to save global settings'}), 500


@app.route('/editor/<book_name>')
@login_required
def editor(book_name):
    """Editor page for a specific book"""
    # This will load the existing index.html editor
    # But we need to pass the book_name context
    return render_template('index.html', book_name=book_name)


@app.route('/api/pages', methods=['GET'])
@login_required
def api_list_pages():
    """List all pages in a book"""
    try:
        book_name = request.args.get('book')
        if not book_name:
            return jsonify({'error': 'Book name required'}), 400

        dm = get_drive_manager()
        if not dm:
            return jsonify({'error': 'Not authenticated'}), 401

        logger.info(f"Listing pages for book: {book_name}")
        pages = dm.list_pages(book_name)
        return jsonify(pages)
    except Exception as e:
        logger.error(f"Error listing pages: {e}")
        return jsonify({'error': 'Failed to list pages from Drive'}), 500


@app.route('/api/pages/<path:filename>', methods=['GET'])
@login_required
def api_get_page(filename):
    """Get content of a specific page"""
    try:
        book_name = request.args.get('book')
        if not book_name:
            return "Book name required", 400

        dm = get_drive_manager()
        if not dm:
            return "Not authenticated", 401

        logger.info(f"Getting page: {filename} from book: {book_name}")
        content = dm.read_page(book_name, filename)

        if content is None:
            return "Page not found", 404

        # Return plain text, not JSON
        return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception as e:
        logger.error(f"Error reading page: {e}")
        return f"Error: {str(e)}", 500


@app.route('/api/pages/<path:filename>', methods=['POST'])
@login_required
def api_save_page(filename):
    """Save content of a specific page"""
    try:
        data = request.get_json()
        book_name = data.get('book')
        content = data.get('content')

        if not book_name or content is None:
            return jsonify({'error': 'Book name and content required'}), 400

        dm = get_drive_manager()
        if not dm:
            return jsonify({'error': 'Not authenticated'}), 401

        logger.info(f"Saving page: {filename} to book: {book_name}")
        success = dm.write_page(book_name, filename, content)

        if success:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': 'Failed to save page'}), 500
    except Exception as e:
        logger.error(f"Error saving page: {e}")
        return jsonify({'error': 'Failed to save page to Drive'}), 500


@app.route('/api/pages/<path:filename>', methods=['DELETE'])
@login_required
def api_delete_page(filename):
    """Delete a page"""
    try:
        book_name = request.args.get('book')
        if not book_name:
            return jsonify({'error': 'Book name required'}), 400

        dm = get_drive_manager()
        if not dm:
            return jsonify({'error': 'Not authenticated'}), 401

        logger.info(f"Deleting page: {filename} from book: {book_name}")
        success = dm.delete_page(book_name, filename)

        if success:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': 'Page not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting page: {e}")
        return jsonify({'error': 'Failed to delete page'}), 500


@app.route('/api/books/<book_name>/download', methods=['GET'])
@login_required
def api_download_book(book_name):
    """Download book as EPUB or PDF"""
    try:
        format_type = request.args.get('format', 'epub').lower()

        if format_type not in ['epub', 'pdf']:
            return jsonify({'error': 'Invalid format. Use epub or pdf'}), 400

        dm = get_drive_manager()
        if not dm:
            return jsonify({'error': 'Not authenticated'}), 401

        logger.info(f"Generating {format_type.upper()} for book: {book_name}")

        # Get book settings
        settings = dm.get_book_settings(book_name)
        book_title = settings.get('title', book_name)
        cover_base64 = settings.get('cover')

        # Get all pages
        pages = dm.list_pages(book_name)
        if not pages:
            return jsonify({'error': 'No pages found in book'}), 404

        # Sort pages by name
        pages.sort()

        # Generate the book
        if format_type == 'epub':
            file_data = generate_epub(dm, book_name, book_title, pages, cover_base64)
            mimetype = 'application/epub+zip'
            filename = f"{book_name}.epub"
        else:  # pdf
            file_data = generate_pdf(dm, book_name, book_title, pages, cover_base64)
            mimetype = 'application/pdf'
            filename = f"{book_name}.pdf"

        # Return the file
        return send_file(
            BytesIO(file_data),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.error(f"Error generating {format_type}: {e}", exc_info=True)
        return jsonify({'error': f'Failed to generate {format_type.upper()}'}), 500


def generate_epub(dm, book_name, book_title, pages, cover_base64=None):
    """Generate EPUB file from markdown pages"""
    from ebooklib import epub
    import base64

    book = epub.EpubBook()

    # Set metadata
    book.set_identifier(f'jugaadpress-{book_name}')
    book.set_title(book_title)
    book.set_language('en')
    book.add_author('JugaadPress User')

    # Add cover image if available
    if cover_base64:
        try:
            # Extract base64 data (remove data:image/...;base64, prefix if present)
            if ',' in cover_base64:
                cover_base64 = cover_base64.split(',')[1]

            cover_data = base64.b64decode(cover_base64)
            book.set_cover('cover.jpg', cover_data)
        except Exception as e:
            logger.warning(f"Failed to add cover image: {e}")

    # Create chapters from pages
    chapters = []
    toc = []
    spine = ['nav']

    for i, page_file in enumerate(pages):
        # Read page content
        content = dm.read_page(book_name, page_file)
        if not content:
            continue

        # Convert markdown to HTML
        html_content = markdown2.markdown(content, extras=['fenced-code-blocks', 'tables', 'header-ids'])

        # Create chapter
        chapter = epub.EpubHtml(
            title=page_file.replace('.md', '').replace('_', ' '),
            file_name=f'chapter_{i}.xhtml',
            lang='en'
        )
        chapter.content = f'<html><body>{html_content}</body></html>'

        # Add to book
        book.add_item(chapter)
        chapters.append(chapter)
        toc.append(chapter)
        spine.append(chapter)

    # Set up table of contents and spine
    book.toc = tuple(toc)
    book.spine = spine

    # Add default NCX and Nav files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Write to BytesIO
    output = BytesIO()
    epub.write_epub(output, book)
    output.seek(0)

    return output.read()


def generate_pdf(dm, book_name, book_title, pages, cover_base64=None):
    """Generate PDF file from markdown pages"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Preformatted
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
        from reportlab.lib.colors import HexColor
        import base64
        from html.parser import HTMLParser

        output = BytesIO()
        doc = SimpleDocTemplate(
            output,
            pagesize=letter,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        story = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=HexColor('#3fb950'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        h1_style = ParagraphStyle(
            'CustomH1',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=HexColor('#3fb950'),
            spaceAfter=12,
            spaceBefore=16,
            fontName='Helvetica-Bold'
        )

        h2_style = ParagraphStyle(
            'CustomH2',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#58a6ff'),
            spaceAfter=10,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )

        h3_style = ParagraphStyle(
            'CustomH3',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=HexColor('#8b949e'),
            spaceAfter=8,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=8
        )

        code_style = ParagraphStyle(
            'CustomCode',
            parent=styles['Code'],
            fontSize=9,
            leftIndent=20,
            rightIndent=20,
            spaceAfter=10,
            spaceBefore=10,
            backColor=HexColor('#21262d'),
            textColor=HexColor('#e6edf3'),
            fontName='Courier'
        )

        # Add title page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(book_title, title_style))
        story.append(Spacer(1, 0.5*inch))

        # Add cover image if available
        if cover_base64:
            try:
                if ',' in cover_base64:
                    cover_base64 = cover_base64.split(',')[1]
                cover_data = base64.b64decode(cover_base64)
                cover_io = BytesIO(cover_data)
                img = Image(cover_io, width=3*inch, height=4*inch)
                story.append(img)
            except Exception as e:
                logger.warning(f"Failed to add cover to PDF: {e}")

        story.append(PageBreak())

        # HTML parser for better markdown conversion
        class MarkdownHTMLParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.elements = []
                self.current_text = []
                self.current_tag = None
                self.in_code_block = False

            def handle_starttag(self, tag, attrs):
                if self.current_text and self.current_tag:
                    text = ''.join(self.current_text).strip()
                    if text:
                        self.elements.append((self.current_tag, text))
                    self.current_text = []
                self.current_tag = tag
                if tag == 'pre':
                    self.in_code_block = True

            def handle_endtag(self, tag):
                if self.current_text and self.current_tag:
                    text = ''.join(self.current_text).strip()
                    if text:
                        self.elements.append((self.current_tag, text))
                self.current_text = []
                self.current_tag = None
                if tag == 'pre':
                    self.in_code_block = False

            def handle_data(self, data):
                self.current_text.append(data)

        # Add content from each page
        for page_file in pages:
            content = dm.read_page(book_name, page_file)
            if not content:
                continue

            # Add page title
            page_title = page_file.replace('.md', '').replace('_', ' ')
            story.append(Paragraph(page_title, h1_style))
            story.append(Spacer(1, 0.2*inch))

            # Convert markdown to HTML
            html_content = markdown2.markdown(content, extras=['fenced-code-blocks', 'tables', 'header-ids'])

            # Parse HTML and convert to PDF elements
            parser = MarkdownHTMLParser()
            parser.feed(html_content)

            for tag, text in parser.elements:
                # Clean up text
                text = text.strip()
                if not text:
                    continue

                # Escape special characters for reportlab
                text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

                if tag == 'h1':
                    story.append(Paragraph(text, h1_style))
                elif tag == 'h2':
                    story.append(Paragraph(text, h2_style))
                elif tag == 'h3':
                    story.append(Paragraph(text, h3_style))
                elif tag == 'pre' or tag == 'code':
                    # Code blocks
                    story.append(Preformatted(text, code_style))
                elif tag == 'p':
                    story.append(Paragraph(text, body_style))
                elif tag == 'li':
                    story.append(Paragraph('• ' + text, body_style))
                else:
                    # Default to body text
                    if text:
                        story.append(Paragraph(text, body_style))

            story.append(PageBreak())

        # Build PDF
        doc.build(story)
        output.seek(0)
        return output.read()

    except ImportError:
        # If reportlab is not installed, return error
        logger.error("reportlab not installed - cannot generate PDF")
        raise Exception("PDF generation requires reportlab library. Please install it: pip install reportlab")


if __name__ == '__main__':
    # For development
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Allow HTTP for localhost
    app.run(host='0.0.0.0', port=5001, debug=True)

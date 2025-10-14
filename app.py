import os
import re
import smtplib
import uuid
from flask import Flask, request, render_template, jsonify
import markdown2
from ebooklib import epub
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from io import BytesIO

# --- CONFIGURATION (from config.py) ---
try:
    from config import SENDER_EMAIL, SENDER_PASSWORD, KINDLE_EMAIL, BOOK_TITLE, COVER_FILENAME

except ImportError:
    print("ERROR: config.py not found or variables missing.")
    exit()

PAGES_DIR = "pages"

app = Flask(__name__)

def compile_book_html():
    """Finds all .md files, compiles them into a single HTML book with a TOC."""
    pages = sorted([f for f in os.listdir(PAGES_DIR) if f.endswith('.md')])
    
    # 1. Build Table of Contents
    toc_html = "<h1>Table of Contents</h1><ul>"
    for page in pages:
        page_name = page.replace('.md', '')
        page_title = page_name.replace('_', ' ').title()
        toc_html += f'<li><a href="#{page_name}">{page_title}</a></li>'
    toc_html += "</ul><hr>"

    # 2. Compile and combine content
    full_content_html = ""
    for page in pages:
        page_name = page.replace('.md', '')
        with open(os.path.join(PAGES_DIR, page), 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Convert Markdown to HTML
        html_content = markdown2.markdown(markdown_content, extras=["tables", "fenced-code-blocks", "cuddled-lists"])
        
        # Rewrite internal links (e.g., [link](./02_notes.md) -> <a href="#02_notes">)
        pattern = re.compile(r'<a href="\.\/(.*?)\.md">')
        rewritten_html = pattern.sub(r'<a href="#\1">', html_content)

        # Wrap each page in a div with an ID for linking
        full_content_html += f'<div id="{page_name}"><h1>{page_name.replace("_", " ").title()}</h1>{rewritten_html}</div><hr>'
        
    return toc_html + full_content_html

@app.route('/')
def index():
    """Render the main editor page."""
    return render_template('index.html')

@app.route('/api/pages', methods=['GET'])
def list_pages():
    """Return a list of all page filenames."""
    pages = sorted([f for f in os.listdir(PAGES_DIR) if f.endswith('.md')])
    return jsonify(pages)

@app.route('/api/page/<filename>', methods=['GET'])
def get_page(filename):
    """Return the raw markdown content of a page."""
    filepath = os.path.join(PAGES_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return "File not found.", 404

@app.route('/api/page/<filename>', methods=['POST'])
def save_page(filename):
    """Save markdown content to a page."""
    filepath = os.path.join(PAGES_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(request.data.decode('utf-8'))
    return "Saved!", 200

@app.route('/api/page', methods=['POST'])
def create_page():
    """Create a new markdown page."""
    data = request.get_json()
    filename = data.get('filename', '').strip()

    if not filename:
        return "Filename is required.", 400

    if not filename.endswith('.md'):
        filename += '.md'

    filepath = os.path.join(PAGES_DIR, filename)

    if os.path.exists(filepath):
        return "Page already exists.", 400

    # Create empty file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {filename.replace('.md', '').replace('_', ' ').title()}\n\n")

    return jsonify({"filename": filename}), 201

@app.route('/api/page/<filename>', methods=['DELETE'])
def delete_page(filename):
    """Delete a markdown page."""
    filepath = os.path.join(PAGES_DIR, filename)

    if not os.path.exists(filepath):
        return "File not found.", 404

    try:
        os.remove(filepath)
        return "Page deleted successfully.", 200
    except Exception as e:
        print(f"Error deleting file: {e}")
        return f"Error: {e}", 500

@app.route('/api/page/<filename>/rename', methods=['POST'])
def rename_page(filename):
    """Rename a markdown page."""
    data = request.get_json()
    new_filename = data.get('new_filename', '').strip()

    if not new_filename:
        return "New filename is required.", 400

    if not new_filename.endswith('.md'):
        new_filename += '.md'

    old_filepath = os.path.join(PAGES_DIR, filename)
    new_filepath = os.path.join(PAGES_DIR, new_filename)

    if not os.path.exists(old_filepath):
        return "File not found.", 404

    if os.path.exists(new_filepath):
        return "A page with that name already exists.", 400

    try:
        os.rename(old_filepath, new_filepath)
        return jsonify({"old_filename": filename, "new_filename": new_filename}), 200
    except Exception as e:
        print(f"Error renaming file: {e}")
        return f"Error: {e}", 500

@app.route('/api/send-to-kindle', methods=['POST'])
def send_to_kindle():
    """
    Compiles all notes into a single, valid EPUB file and sends it to Kindle.
    This is the definitive, correct method that Kindle actually understands.
    """
    # 1. Create a new EPUB book
    book = epub.EpubBook()

    # Use stable UUID for consistent book identification
    # Same title = same UUID = Kindle recognizes as update
    book_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, BOOK_TITLE)
    book.set_identifier(str(book_uuid))

    book.set_title(BOOK_TITLE)
    book.set_language('en')  # Change to 'ja' for Japanese if needed
    book.add_author('JugaadPress')

    # 2. Add the cover image
    try:
        with open(COVER_FILENAME, 'rb') as f:
            cover_data = f.read()
            book.set_cover("cover.jpg", cover_data, create_page=True)
    except FileNotFoundError:
        print(f"{COVER_FILENAME} not found, sending without a cover.")

    # 3. Create a chapter for each markdown file
    pages = sorted([f for f in os.listdir(PAGES_DIR) if f.endswith('.md')])
    chapters = []

    # Build mapping: filename.md -> filename.xhtml
    page_map = {f: f.replace('.md', '.xhtml') for f in pages}

    for page_file in pages:
        page_name = page_file.replace('.md', '')
        page_title = page_name.replace('_', ' ').title()

        with open(os.path.join(PAGES_DIR, page_file), 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        # Convert markdown to HTML for the chapter content
        html_content = markdown2.markdown(
            markdown_content,
            extras=["tables", "fenced-code-blocks", "cuddled-lists"]
        )

        # Fix internal links to point to EPUB chapters
        # Handles: <a href="./file.md"> with URL encoding
        def replace_link(match):
            import urllib.parse
            encoded_filename = match.group(1)

            # Decode URL encoding
            filename = urllib.parse.unquote(encoded_filename)

            # Ensure .md extension
            if not filename.endswith('.md'):
                filename += '.md'

            # Convert to .xhtml if it exists in our pages
            if filename in page_map:
                return f'<a href="{page_map[filename]}">'

            # Keep original if not found
            return match.group(0)

        # Match: <a href="./filename.md"> (may have URL encoding)
        pattern = re.compile(r'<a href="\./([^"]+)">')
        html_content = pattern.sub(replace_link, html_content)

        # Add "Back to Index" link at bottom (if this isn't the first page)
        # Use first page (alphabetically) as index
        first_page = pages[0] if pages else None
        if first_page and page_file != first_page:
            index_xhtml = page_map[first_page]
            html_content += f'''
<hr style="margin-top: 3em; border: none; border-top: 1px solid #ccc;">
<p style="text-align: right; font-size: 0.85em; color: #666; margin-top: 1em;">
    <a href="{index_xhtml}" style="text-decoration: none; color: #666;">← Back to Table of Contents</a>
</p>'''

        # Create an EPUB HTML chapter object (no auto-heading, content has it)
        chapter = epub.EpubHtml(
            title=page_title,
            file_name=f'{page_name}.xhtml',
            lang='en'
        )
        chapter.content = html_content  # Use content as-is, no extra heading
        book.add_item(chapter)
        chapters.append(chapter)

    # 4. Define the book's structure (Table of Contents and reading order)
    book.toc = chapters
    book.spine = ['cover'] + chapters if os.path.exists(COVER_FILENAME) else chapters
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # 5. Write the EPUB file to memory
    epub_bytes = BytesIO()
    epub.write_epub(epub_bytes, book, {})
    epub_data = epub_bytes.getvalue()  # Get the actual bytes BEFORE seeking

    # Save a local copy for debugging
    local_filename = f"{BOOK_TITLE}.epub"
    try:
        with open(local_filename, 'wb') as f:
            f.write(epub_data)
        print(f"✓ Local copy saved: {local_filename}")
    except Exception as e:
        print(f"Warning: Could not save local copy: {e}")

    # 6. Create proper multipart email with EPUB as attachment
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = KINDLE_EMAIL
    msg['Subject'] = 'Convert'  # 'Convert' tells Kindle to process the file

    # Add a simple text body (Kindle ignores this but email needs a body)
    body = MIMEText('Please find the attached ebook.', 'plain')
    msg.attach(body)

    # Attach the EPUB file as a proper attachment
    epub_attachment = MIMEApplication(epub_data, _subtype='epub+zip')
    epub_attachment.add_header('Content-Disposition', 'attachment', filename=f"{BOOK_TITLE}.epub")
    msg.attach(epub_attachment)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, KINDLE_EMAIL, msg.as_string())
        server.quit()
        print(f"✓ Book sent to Kindle successfully!")
        return "Book sent to Kindle!", 200
    except Exception as e:
        print(f"✗ Error sending email: {e}")
        return f"Error: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

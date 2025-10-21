# JugaadPress - Technical Reference & Changelog

> Complete technical documentation for developers and power users

**Quick Links:** [README](./README.md) | [Installation](#installation) | [Architecture](#architecture) | [API Reference](#api-reference) | [Changelog](#changelog)

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Installation & Setup](#installation--setup)
3. [Architecture](#architecture)
4. [API Reference](#api-reference)
5. [Frontend Components](#frontend-components)
6. [EPUB Generation](#epub-generation)
7. [Design System](#design-system)
8. [Keyboard Shortcuts](#keyboard-shortcuts)
9. [Known Limitations](#known-limitations)
10. [Changelog](#changelog)

---

## Project Overview

**JugaadPress** is a single-page web application for creating and managing Markdown notes, compiling them into professionally-formatted EPUB ebooks, and delivering them directly to Kindle devices via email.

### Tech Stack
- **Backend:** Flask 3.1.2 (Python 3.13.2)
- **Frontend:** Vanilla JavaScript with Marked.js for Markdown rendering
- **Storage:** File-based (pages/ directory)
- **Styling:** Custom CSS with GitHub Dark-inspired theme
- **EPUB:** EbookLib 0.19 for book generation

### Use Cases
- Learning notes (language study, technical documentation)
- Personal knowledge base
- Book drafts and long-form writing
- Study materials compilation for Kindle

---

## Installation & Setup

### Prerequisites
- Python 3.13+ (works with 3.8+)
- Gmail account with 2FA enabled
- Amazon Kindle device/app

### Step-by-Step Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd JugaadPress

# 2. Create virtual environment
python3 -m venv jugaadpressenv
source jugaadpressenv/bin/activate  # macOS/Linux
# jugaadpressenv\Scripts\activate   # Windows

# 3. Install dependencies
pip install Flask==3.1.2 markdown2==2.5.4 EbookLib==0.19

# 4. Create configuration file
cat > config.py << EOF
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "xxxx-xxxx-xxxx-xxxx"  # Gmail App Password
KINDLE_EMAIL = "your-device@kindle.com"
BOOK_TITLE = "My Learning Notes"
COVER_FILENAME = "cover.jpg"
EOF

# 5. Add cover image (optional)
# Place a cover.jpg file in the root directory

# 6. Run the application
python app.py
```

### Gmail App Password Setup

1. Enable 2-Factor Authentication on your Google account
2. Go to [App Passwords](https://myaccount.google.com/apppasswords)
3. Create a new app password for "Mail"
4. Use the 16-character password in `config.py`

### Kindle Email Whitelist

1. Go to [Amazon Kindle Settings](https://www.amazon.com/hz/mycd/myx#/home/settings/payment)
2. Scroll to "Personal Document Settings"
3. Add your Gmail address to "Approved Personal Document E-mail List"

---

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  index.html (Single-Page Application)                  │ │
│  │  - Editor (Native Textarea)                            │ │
│  │  - Live Preview (Marked.js)                            │ │
│  │  - Sidebar (Page Management)                           │ │
│  │  - Toolbar (Formatting)                                │ │
│  └─────────────────────┬──────────────────────────────────┘ │
└────────────────────────┼────────────────────────────────────┘
                         │ REST API (JSON)
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  Flask Backend (app.py)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Endpoints                                        │  │
│  │  - GET/POST/DELETE pages                             │  │
│  │  - Rename operations                                  │  │
│  │  - Send to Kindle                                     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  EPUB Generation                                      │  │
│  │  - markdown2: MD → HTML                              │  │
│  │  - ebooklib: HTML → EPUB                             │  │
│  │  - UUID generation (stable book IDs)                 │  │
│  │  - Internal link rewriting                           │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Email Delivery (smtplib)                            │  │
│  │  - Gmail SMTP (port 587, STARTTLS)                  │  │
│  │  - MIME multipart with EPUB attachment              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  File System Storage                         │
│  pages/                                                      │
│    ├── 0_Index.md                                           │
│    ├── 1.1_Notes.md                                         │
│    └── ...                                                   │
└──────────────────────────────────────────────────────────────┘
```

### File Structure

```
JugaadPress/
├── app.py                     # Flask application (289 lines)
├── config.py                  # Configuration (gitignored)
├── cover.jpg                  # Book cover image
├── .gitignore                 # Git exclusions
├── README.md                  # User documentation
├── REFERENCE.md               # This file
├── pages/                     # Markdown content files
│   ├── 0_Index.md
│   ├── 1.1 は vs が.md
│   ├── 1.2 を.md
│   └── ...
├── templates/
│   └── index.html             # Frontend SPA (2392 lines)
└── jugaadpressenv/            # Python virtual environment
```

---

## API Reference

### Base URL
`http://localhost:5000`

### Endpoints

#### `GET /`
Serves the main editor interface.

**Response:** HTML page (index.html)

---

#### `GET /api/pages`
Returns a list of all markdown files in `pages/` directory.

**Response:**
```json
[
  "0_Index.md",
  "1.1 は vs が.md",
  "1.2 を.md"
]
```

---

#### `GET /api/page/<filename>`
Retrieves the raw Markdown content of a specific page.

**Parameters:**
- `filename` (string): The markdown filename (e.g., `01_intro.md`)

**Response:**
```
# My Page Title

Content here...
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - File does not exist

---

#### `POST /api/page/<filename>`
Saves Markdown content to a page.

**Parameters:**
- `filename` (string): The markdown filename

**Request Body:** Raw Markdown text (Content-Type: `text/plain`)

**Response:**
```
Saved!
```

**Status Codes:**
- `200 OK` - Success

---

#### `POST /api/page`
Creates a new markdown page.

**Request Body:**
```json
{
  "filename": "03_new_page"
}
```

**Response:**
```json
{
  "filename": "03_new_page.md"
}
```

**Status Codes:**
- `201 Created` - Success
- `400 Bad Request` - Filename missing or invalid
- `400 Bad Request` - File already exists

---

#### `DELETE /api/page/<filename>`
Deletes a markdown page.

**Parameters:**
- `filename` (string): The markdown filename

**Response:**
```
Page deleted successfully.
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - File does not exist
- `500 Internal Server Error` - Deletion failed

---

#### `POST /api/page/<filename>/rename`
Renames a markdown page.

**Parameters:**
- `filename` (string): Current filename

**Request Body:**
```json
{
  "new_filename": "04_renamed_page"
}
```

**Response:**
```json
{
  "old_filename": "03_old_page.md",
  "new_filename": "04_renamed_page.md"
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - New filename missing
- `404 Not Found` - Original file does not exist
- `400 Bad Request` - New filename already exists
- `500 Internal Server Error` - Rename failed

---

#### `POST /api/send-to-kindle`
Compiles all pages into an EPUB and emails it to Kindle.

**Response:**
```
Book sent to Kindle!
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - EPUB generation or email failed

**Side Effects:**
- Creates local file: `{BOOK_TITLE}.epub`
- Sends email via Gmail SMTP

---

## Frontend Components

### State Management

The application uses a global state object:

```javascript
const state = {
    currentPage: null,              // Currently loaded page filename
    saveTimeout: null,              // Auto-save timer ID
    previewVisible: false,          // Preview pane visibility
    previewPage: null,              // Page shown in preview (independent)
    unsavedChanges: false,          // Dirty flag for editor
    sending: false,                 // Kindle send in progress
    allPages: [],                   // List of all page filenames
    autocompleteVisible: false,     // Autocomplete dropdown state
    selectedAutocompleteIndex: 0    // Autocomplete selection index
};
```

### Core Functions

#### Page Management

**`loadPageList()`** (`index.html:2116-2172`)
- Fetches all pages via `/api/pages`
- Populates sidebar with page list
- Adds delete buttons and click handlers
- Loads first page if none selected

**`loadPageContent(filename)`** (`index.html:2174-2189`)
- Checks for unsaved changes
- Shows confirmation modal if needed
- Calls `loadPage()` to fetch content

**`loadPage(filename)`** (`index.html:2191-2222`)
- Fetches page content via `/api/page/<filename>`
- Updates editor with smooth fade transition (50ms)
- Marks page as active in sidebar
- Updates preview if visible

**`savePageContent()`** (`index.html:2224-2241`)
- Sends editor content to `/api/page/<filename>`
- Updates status indicator
- Shows toast notification
- Clears unsaved changes flag

**`createNewPage(filename)`** (`index.html:2288-2323`)
- Creates page via `/api/page`
- Reloads page list
- Loads newly created page
- Handles button disabled state

**`deletePage(filename)`** (`index.html:2325-2364`)
- Shows confirmation modal
- Deletes via `/api/page/<filename>`
- Clears editor if deleted page was active
- Reloads page list

**`enableRename(pageNameSpan, filename)`** (`index.html:1915-2001`)
- Creates inline input field
- Handles Enter/Escape/Blur events
- Sends rename request to API
- Updates state and reloads list

#### Editor Functions

**`wrapSelection(before, after)`** (`index.html:1377-1403`)
- Smart toggle wrapping (detects existing formatting)
- Uses `document.execCommand('insertText')` to preserve undo
- Handles bold, italic, strikethrough, code
- Shows toast feedback

**`insertAtLineStart(prefix)`** (`index.html:1405-1430`)
- Inserts/removes prefix at line start
- Smart toggle for headings, lists, quotes
- Preserves undo history

**`duplicateLine()`** (`index.html:1441-1453`)
- Duplicates current line below cursor
- Preserves undo history

**`deleteLine()`** (`index.html:1455-1475`)
- Deletes entire current line
- Handles edge cases (first/last/only line)

**`moveLineUp()`/`moveLineDown()`** (`index.html:1528-1576`)
- Swaps current line with adjacent line
- Maintains cursor position

**`increaseHeading()`/`decreaseHeading()`** (`index.html:1578-1616`)
- Adds/removes `#` from heading lines
- Validates heading format

**`toggleComment()`** (`index.html:1489-1507`)
- Wraps/unwraps selection with `<!-- -->`
- Smart toggle detection

**`toggleCodeBlock()`** (`index.html:1509-1526`)
- Wraps/unwraps selection with triple backticks
- Smart toggle detection

#### Preview Functions

**`togglePreview()`** (`index.html:1657-1664`)
- Shows/hides preview pane
- Updates button active state
- Triggers preview render

**`updatePreview(pageToShow)`** (`index.html:1666-1714`)
- Converts Markdown to HTML with Marked.js
- Supports independent preview navigation
- Intercepts internal link clicks
- Fetches page content on demand
- Shows toast notifications

#### Autocomplete Functions

**`showAutocomplete(pages, cursorPos, customText)`** (`index.html:2004-2034`)
- Displays dropdown with page list
- Positions near cursor
- Stores custom text for toolbar mode
- Marks first item as selected

**`hideAutocomplete()`** (`index.html:2036-2042`)
- Hides dropdown
- Resets selection index
- Clears context

**`insertPageLink(page, customText)`** (`index.html:2044-2082`)
- **Two modes:**
  - `[[` mode: Auto-generates link text from filename
  - Toolbar mode: Uses selected text or custom text
- URL-encodes filenames for spaces
- Preserves undo history
- Positions cursor after link

**`updateAutocompleteSelection(direction)`** (`index.html:2084-2101`)
- Moves selection up/down with arrow keys
- Wraps around at edges
- Updates visual selection

#### UI Functions

**`showToast(message, isError)`** (`index.html:1320-1327`)
- Displays slide-in notification
- Color-codes success/error
- Auto-dismisses after 3 seconds

**`showModal(title, message, onConfirm)`** (`index.html:1329-1361`)
- Displays confirmation dialog
- Handles confirm/cancel/overlay click
- Cleans up event listeners

**`showInputModal(title, message, placeholder, onConfirm)`** (`index.html:1863-1912`)
- Displays input dialog for new pages
- Handles Enter key submission
- Validates input before confirming

**`showShortcutsModal()`/`hideShortcutsModal()`** (`index.html:1618-1635`)
- Displays keyboard shortcuts reference
- Closes on Esc or outside click
- Two-column categorized layout

**`updateStatus(text, type)`** (`index.html:1363-1366`)
- Updates status bar text
- Sets CSS class for color coding
- Types: `normal`, `saving`, `saved`, `error`

#### Auto-Save Mechanism

```javascript
editor.addEventListener('input', () => {
    state.unsavedChanges = true;
    updatePreview();
    clearTimeout(state.saveTimeout);
    updateStatus('Typing...', 'normal');
    state.saveTimeout = setTimeout(savePageContent, 1500);
});
```

**Behavior:**
- Triggers on every keystroke
- Debounces save by 1.5 seconds
- Updates preview in real-time
- Shows "Typing..." status
- Auto-saves after inactivity

### Event Handling

#### Keyboard Shortcuts (`index.html:1717-1837`)

All shortcuts preserve native undo/redo by using `document.execCommand`.

**Modifier Detection:**
```javascript
if (e.ctrlKey || e.metaKey) {
    // Cmd on Mac, Ctrl on Windows/Linux
}
```

**Autocomplete Navigation:**
- `ArrowUp/Down` - Navigate dropdown
- `Enter` - Select current item
- `Escape` - Close dropdown

**Alt Key Shortcuts:**
- `Alt + ↑/↓` - Move line up/down

#### Click Handling

**Single vs Double Click Detection:**
```javascript
let clickTimeout = null;
let clickCount = 0;

pageName.onclick = (e) => {
    clickCount++;
    if (clickCount === 1) {
        clickTimeout = setTimeout(() => {
            loadPageContent(page);  // Single click
            clickCount = 0;
        }, 200);
    } else if (clickCount === 2) {
        clearTimeout(clickTimeout);
        enableRename(pageName, page);  // Double click
        clickCount = 0;
    }
};
```

**200ms delay** allows double-click detection while feeling snappy.

---

## EPUB Generation

### Process Flow (`app.py:150-286`)

```
Markdown Files → HTML Conversion → EPUB Structure → Email Delivery
     │                  │                 │                │
     ▼                  ▼                 ▼                ▼
pages/*.md     markdown2.markdown()   ebooklib       smtplib
                   + extras          .EpubBook()    Gmail SMTP
```

### Implementation Details

#### 1. Book Initialization

```python
book = epub.EpubBook()

# Stable UUID (same title = same UUID = Kindle recognizes updates)
book_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, BOOK_TITLE)
book.set_identifier(str(book_uuid))

book.set_title(BOOK_TITLE)
book.set_language('en')
book.add_author('JugaadPress')
```

**Why UUID v5?**
- Deterministic (same input = same output)
- Based on DNS namespace + book title
- Intended to help Kindle detect duplicates (but Kindle's detection is unreliable)

#### 2. Cover Image

```python
with open(COVER_FILENAME, 'rb') as f:
    cover_data = f.read()
    book.set_cover("cover.jpg", cover_data, create_page=True)
```

**Note:** `create_page=True` adds cover as first page in book.

#### 3. Chapter Creation

```python
pages = sorted([f for f in os.listdir(PAGES_DIR) if f.endswith('.md')])
chapters = []
page_map = {f: f.replace('.md', '.xhtml') for f in pages}

for page_file in pages:
    # Read markdown
    with open(os.path.join(PAGES_DIR, page_file), 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # Convert to HTML
    html_content = markdown2.markdown(
        markdown_content,
        extras=["tables", "fenced-code-blocks", "cuddled-lists"]
    )

    # Fix internal links (./file.md → file.xhtml)
    html_content = fix_internal_links(html_content, page_map)

    # Add "Back to TOC" link (except first page)
    if page_file != pages[0]:
        html_content += back_to_toc_link(pages[0])

    # Create chapter
    chapter = epub.EpubHtml(
        title=page_title,
        file_name=f'{page_name}.xhtml',
        lang='en'
    )
    chapter.content = html_content  # No auto-heading!
    book.add_item(chapter)
    chapters.append(chapter)
```

**Key Points:**
- Files sorted alphabetically
- First page = Table of Contents
- No auto-generated headings (uses your markdown headings as-is)
- All pages get "Back to TOC" link except first

#### 4. Internal Link Rewriting (`app.py:196-218`)

**Problem:** Markdown links use `.md` extension, but EPUB uses `.xhtml`

**Solution:**
```python
def replace_link(match):
    import urllib.parse
    encoded_filename = match.group(1)

    # Decode URL encoding (e.g., %20 → space)
    filename = urllib.parse.unquote(encoded_filename)

    # Ensure .md extension
    if not filename.endswith('.md'):
        filename += '.md'

    # Convert to .xhtml if page exists
    if filename in page_map:
        return f'<a href="{page_map[filename]}">'

    return match.group(0)  # Keep original if not found

pattern = re.compile(r'<a href="\./([^"]+)">')
html_content = pattern.sub(replace_link, html_content)
```

**Handles:**
- URL-encoded filenames (`1.1%20は%20vs%20が.md`)
- Relative paths (`./file.md`)
- Missing extensions (adds `.md` if needed)
- Non-existent pages (keeps original link)

#### 5. Back to TOC Link (`app.py:220-229`)

```python
first_page = pages[0] if pages else None
if first_page and page_file != first_page:
    index_xhtml = page_map[first_page]
    html_content += f'''
<hr style="margin-top: 3em; border: none; border-top: 1px solid #ccc;">
<p style="text-align: right; font-size: 0.85em; color: #666; margin-top: 1em;">
    <a href="{index_xhtml}" style="text-decoration: none; color: #666;">← Back to Table of Contents</a>
</p>'''
```

**Styling:**
- Right-aligned
- Small font (0.85em)
- Gray color (#666)
- Horizontal rule separator
- Not intrusive but always accessible

#### 6. Book Structure

```python
book.toc = chapters  # Table of Contents
book.spine = ['cover'] + chapters  # Reading order
book.add_item(epub.EpubNcx())  # Navigation file
book.add_item(epub.EpubNav())  # EPUB3 navigation
```

**Spine Order:**
1. Cover page
2. All chapters (alphabetically)

#### 7. EPUB File Generation

```python
epub_bytes = BytesIO()
epub.write_epub(epub_bytes, book, {})
epub_data = epub_bytes.getvalue()

# Save local copy for debugging
with open(f"{BOOK_TITLE}.epub", 'wb') as f:
    f.write(epub_data)
```

**Note:** `getvalue()` before seeking ensures we get complete data.

#### 8. Email Delivery

```python
msg = MIMEMultipart()
msg['From'] = SENDER_EMAIL
msg['To'] = KINDLE_EMAIL
msg['Subject'] = 'Convert'  # Magic subject for Kindle

# Add text body (Kindle ignores but email needs body)
body = MIMEText('Please find the attached ebook.', 'plain')
msg.attach(body)

# Attach EPUB
epub_attachment = MIMEApplication(epub_data, _subtype='epub+zip')
epub_attachment.add_header(
    'Content-Disposition',
    'attachment',
    filename=f"{BOOK_TITLE}.epub"
)
msg.attach(epub_attachment)

# Send via Gmail SMTP
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(SENDER_EMAIL, SENDER_PASSWORD)
server.sendmail(SENDER_EMAIL, KINDLE_EMAIL, msg.as_string())
server.quit()
```

**Email Requirements:**
- Subject must be "Convert" (tells Kindle to process file)
- MIME type: `application/epub+zip`
- Gmail requires STARTTLS on port 587
- Must use App Password (not regular password)

---

## Design System

### Color Palette (GitHub Dark-Inspired)

```css
:root {
    /* Backgrounds */
    --bg-primary: #0d1117;        /* Deep dark background */
    --bg-secondary: #161b22;      /* Sidebar/toolbar */
    --bg-tertiary: #21262d;       /* Elevated surfaces, hovers */

    /* Accents */
    --accent-primary: #3fb950;    /* Green (success, active) */
    --accent-secondary: #58a6ff;  /* Blue (interactive) */
    --accent-danger: #f85149;     /* Red (errors, delete) */

    /* Text */
    --text-primary: #e6edf3;      /* Main text */
    --text-secondary: #8b949e;    /* Secondary text */
    --text-dim: #6e7681;          /* Dim text, hints */

    /* UI Elements */
    --border-color: #30363d;      /* Borders */
    --shadow-glow: rgba(63, 185, 80, 0.15);   /* Green glow */
    --shadow-glow-secondary: rgba(88, 166, 255, 0.1);  /* Blue glow */
    --code-bg: #1c2128;           /* Code blocks */
    --link-color: #58a6ff;        /* Links */
}
```

### Typography

**Fonts:**
- **UI:** JetBrains Mono (monospace, terminal aesthetic)
- **Editor:** Fira Code (coding ligatures)
- **Preview:** System fonts (readability)

**Sizes:**
- Editor: 15px, line-height 1.7, letter-spacing 0.3px
- UI buttons: 13px
- Status/hints: 11-12px

### Visual Effects

**Transitions:**
```css
transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);  /* Snappy */
transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); /* Smooth */
transition: all 0.3s ease;                          /* Slow */
```

**Animations:**
```css
@keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

@keyframes fadeInScale {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
}

@keyframes slideInRight {
    from { transform: translateX(400px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
```

**Hover Effects:**
- `transform: translateY(-1px)` - Subtle lift
- `box-shadow: 0 0 15px var(--shadow-glow)` - Glow effect
- Color shifts: secondary → primary

### Custom Scrollbar

```css
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: var(--bg-secondary);
}
::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: var(--accent-primary);
}
```

---

## Keyboard Shortcuts

### Complete Reference

| Shortcut | Action | Implementation |
|----------|--------|----------------|
| **Formatting** |||
| `Cmd+B` / `Ctrl+B` | Bold | `wrapSelection('**')` |
| `Cmd+I` / `Ctrl+I` | Italic | `wrapSelection('*')` |
| `Cmd+`` ` `` / `Ctrl+`` ` `` | Inline Code | `wrapSelection('`')` |
| `Cmd+H` / `Ctrl+H` | Heading | `insertAtLineStart('## ')` |
| `Cmd+Q` / `Ctrl+Q` | Quote | `insertAtLineStart('> ')` |
| `Cmd+E` / `Ctrl+E` | Code Block | `toggleCodeBlock()` |
| `Cmd+/` / `Ctrl+/` | Comment | `toggleComment()` |
| **Lists** |||
| `Cmd+L` / `Ctrl+L` | Bullet List | `insertAtLineStart('- ')` |
| `Cmd+Shift+L` / `Ctrl+Shift+L` | Numbered List | `insertAtLineStart('1. ')` |
| **Editing** |||
| `Cmd+D` / `Ctrl+D` | Duplicate Line | `duplicateLine()` |
| `Cmd+Shift+K` / `Ctrl+Shift+K` | Delete Line | `deleteLine()` |
| `Cmd+Enter` / `Ctrl+Enter` | New Line Below | `insertLineBelow()` |
| `Cmd+[` / `Ctrl+[` | Decrease Heading | `decreaseHeading()` |
| `Cmd+]` / `Ctrl+]` | Increase Heading | `increaseHeading()` |
| `Alt+↑` | Move Line Up | `moveLineUp()` |
| `Alt+↓` | Move Line Down | `moveLineDown()` |
| `Cmd+Z` / `Ctrl+Z` | Undo | Native browser |
| `Cmd+Y` / `Ctrl+Y` | Redo | Native browser |
| **Navigation** |||
| `Cmd+K` / `Ctrl+K` | Insert Link | `showAutocomplete()` |
| `Cmd+P` / `Ctrl+P` | Toggle Preview | `togglePreview()` |
| `Cmd+S` / `Ctrl+S` | Force Save | `savePageContent()` |
| **Autocomplete** |||
| `[[` | Trigger Link Picker | Auto-detect in input |
| `↑` | Navigate Up | `updateAutocompleteSelection(-1)` |
| `↓` | Navigate Down | `updateAutocompleteSelection(1)` |
| `Enter` | Select | `selectCurrentAutocomplete()` |
| `Esc` | Cancel | `hideAutocomplete()` |

### Undo/Redo Preservation

**Critical Implementation Detail:**

All editing functions use `document.execCommand('insertText', false, text)` instead of direct `editor.value = newValue` assignments.

**Why?**
- Direct assignment destroys browser's native undo stack
- `execCommand` creates undo history entries
- Allows native Cmd+Z/Ctrl+Z to work properly

**Example:**
```javascript
// ❌ BAD - Destroys undo history
editor.value = newText;

// ✅ GOOD - Preserves undo history
editor.setSelectionRange(start, end);
document.execCommand('insertText', false, newText);
```

---

## Known Limitations

### Kindle Duplicate Detection

**Issue:** Kindle sometimes creates duplicate books despite stable UUIDs.

**Root Cause:** Amazon's duplicate detection algorithm is unreliable and proprietary.

**Workaround:** Manually delete old versions from Kindle library.

**What We Tried:**
- Stable UUID v5 based on book title
- Consistent metadata (title, author, language)
- Same identifier for same book

**Conclusion:** This is an Amazon limitation, not fixable on our end.

### Emoji Rendering on Kindle

**Issue:** Emojis in markdown don't render on Kindle (show as boxes).

**Root Cause:** Kindle E-Ink displays don't support color emoji fonts.

**Workaround:** Use text-based symbols instead: `>`, `*`, `[x]`, etc.

### Image Embedding

**Current:** Only cover image supported.

**Limitation:** No support for images within markdown content.

**Reason:** File path resolution and EPUB resource management complexity.

**Future:** Possible to implement with base64 encoding or EPUB resource management.

### Gmail SMTP Only

**Current:** Hardcoded Gmail SMTP configuration.

**Limitation:** Cannot use other email providers without code changes.

**Workaround:** Update `smtplib` configuration in `send_to_kindle()` function.

### Single Book Configuration

**Current:** One `config.py` file with single book title/cover.

**Limitation:** Cannot manage multiple books simultaneously.

**Workaround:** Create separate project directories or implement book profiles.

---

## Changelog

### v1.0 - Initial Release (October 2025)

**Core Features:**
- ✅ Flask backend with REST API
- ✅ File-based markdown storage
- ✅ Single-page web editor
- ✅ Basic toolbar (bold, italic, headings)
- ✅ EPUB generation with ebooklib
- ✅ Gmail SMTP integration
- ✅ Auto-save mechanism

### v2.0 - GitHub Dark Theme (October 2025)

**Major UI/UX Overhaul:**
- ✅ Complete redesign with GitHub Dark theme
- ✅ Removed EasyMDE dependency, native textarea editor
- ✅ Split-pane live preview with Marked.js
- ✅ Smart toggle formatting (click again to remove)
- ✅ Modal confirmation dialogs
- ✅ Toast notifications system
- ✅ Unsaved changes detection
- ✅ Full keyboard shortcut support
- ✅ Animated UI elements (glows, pulses, slide-ins)
- ✅ Custom scrollbars
- ✅ Professional error handling
- ✅ Color-coded status indicators

**Design Improvements:**
- Green (#3fb950) and blue (#58a6ff) accents
- Glowing box shadows on interactive elements
- Terminal-style blinking cursor in header
- Smooth 200-300ms transitions
- Monospace fonts (JetBrains Mono, Fira Code)
- Better visual hierarchy

### v2.1 - Page Management (October 2025)

**New Features:**
- ✅ Create new pages via modal dialog
- ✅ Delete pages with confirmation
- ✅ Inline rename (double-click page name)
- ✅ Auto-save with debouncing (1.5s)
- ✅ Page list with active state highlighting
- ✅ Smooth page switching with fade transitions

**Bug Fixes:**
- Fixed page loading race conditions
- Improved error handling for API calls
- Better disabled button states

### v2.2 - Smart Links & Preview (October 2025)

**New Features:**
- ✅ Page link autocomplete (`[[` trigger)
- ✅ URL encoding for filenames with spaces
- ✅ Independent preview navigation (click links without affecting editor)
- ✅ Internal link rewriting in EPUB
- ✅ URL decoding for EPUB links
- ✅ "Back to Table of Contents" in EPUB chapters

**Implementation:**
- `encodeURIComponent()` for link generation
- `decodeURIComponent()` for EPUB link mapping
- Preview state tracking (`previewPage`)
- Link interception in preview pane

**Bug Fixes:**
- ✅ Fixed broken links in preview
- ✅ Fixed broken links in EPUB
- ✅ Removed quotes from link format (was causing HTML escaping)

### v2.3 - Undo/Redo Preservation (October 2025)

**Critical Fix:**
- ✅ Replaced all `editor.value = ...` with `document.execCommand('insertText')`
- ✅ Native browser undo/redo now works perfectly
- ✅ All formatting functions preserve undo history

**Affected Functions:**
- `wrapSelection()`
- `insertAtLineStart()`
- `insertPageLink()`
- `duplicateLine()`
- `deleteLine()`
- `moveLineUp()`/`moveLineDown()`
- `toggleComment()`
- `toggleCodeBlock()`

### v2.4 - Advanced Editing (October 2025)

**New Keyboard Shortcuts:**
- ✅ `Cmd+D` - Duplicate line
- ✅ `Cmd+Shift+K` - Delete line
- ✅ `Cmd+Enter` - Insert line below
- ✅ `Alt+↑/↓` - Move line up/down
- ✅ `Cmd+[` / `Cmd+]` - Increase/decrease heading
- ✅ `Cmd+/` - Toggle comment
- ✅ `Cmd+E` - Toggle code block

**New Functions:**
- `duplicateLine()`
- `deleteLine()`
- `insertLineBelow()`
- `moveLineUp()`/`moveLineDown()`
- `increaseHeading()`/`decreaseHeading()`
- `toggleComment()`
- `toggleCodeBlock()`

### v2.5 - Shortcuts Modal (October 2025)

**New Features:**
- ✅ Beautiful shortcuts modal (replaces ugly `alert()`)
- ✅ Two-column categorized layout
- ✅ Mac-style key symbols (⌘, ⇧, ⌥, ↵)
- ✅ Category emojis (✨ ✂️ 🔗 🎯)
- ✅ Hover effects on shortcut items
- ✅ Click "View Shortcuts" or press Esc to close

**UI Improvements:**
- GitHub Dark themed modal
- Green glow effect
- Scrollable content area
- Close on Esc or outside click

### v2.6 - EPUB Polish (October 2025)

**EPUB Improvements:**
- ✅ Removed auto-generated headings (uses your markdown headings)
- ✅ Fixed "Back to Index" link (uses first page dynamically)
- ✅ Changed link text to "← Back to Table of Contents"
- ✅ Added proper styling (right-aligned, gray, small font)
- ✅ Stable UUID v5 for book identification

**Bug Fixes:**
- Fixed hardcoded index page reference
- Improved back link aesthetics
- Better chapter content handling

### v2.7 - Kindle Library Link (October 2025)

**New Features:**
- ✅ Added "My Kindle Library" link in bottom bar
- ✅ Direct link to Amazon Kindle library (Japan)
- ✅ Hover effect (blue → green)
- ✅ Icon: book-open

**UI Improvements:**
- Clickable text instead of keyboard-only shortcuts hint
- Better spacing in bottom bar

### v2.8 - Git Repository (October 2025)

**Infrastructure:**
- ✅ Created `.gitignore` (excludes config.py, venv, generated files)
- ✅ Initial commit with all features
- ✅ Set up GitHub repository with SSH
- ✅ Updated documentation

**Security:**
- `config.py` excluded from version control
- SSH key authentication set up
- App passwords used for Gmail

### v2.9 - Documentation Overhaul (October 2025)

**New Documentation:**
- ✅ Created `README.md` - User-friendly quick start guide
- ✅ Created `REFERENCE.md` - Complete technical reference
- ✅ Cross-linked both documents
- ✅ Comprehensive API documentation
- ✅ Architecture diagrams
- ✅ Complete changelog
- ✅ Known limitations documented

**Documentation Features:**
- Quick start guide for new users
- Full API reference with examples
- Frontend component documentation
- EPUB generation deep dive
- Design system reference
- Keyboard shortcuts table
- Troubleshooting guide

---

## Development Notes

### Adding New Features

**Backend (Flask):**
1. Add route in `app.py`
2. Update API documentation in this file
3. Test with browser dev tools or `curl`

**Frontend (UI):**
1. Add HTML structure in `templates/index.html`
2. Add styles in `<style>` section
3. Add JavaScript logic in `<script>` section
4. Update state object if needed

**EPUB Generation:**
1. Modify `send_to_kindle()` function in `app.py`
2. Test with local EPUB file
3. Validate with EPUB readers (Calibre, Apple Books)
4. Test on actual Kindle device

### Debugging Tips

**Backend Issues:**
```bash
# Run Flask in debug mode
python app.py

# Check terminal for errors
# Logs appear in console
```

**Frontend Issues:**
- Open browser DevTools (F12)
- Check Console tab for JavaScript errors
- Check Network tab for API failures
- Use `showToast()` for quick debugging

**EPUB Issues:**
- Check local copy: `{BOOK_TITLE}.epub`
- Open with Calibre or Apple Books
- Validate with [EPUBCheck](https://www.w3.org/publishing/epubcheck/)
- Test internal links by clicking in reader

**Email Delivery Issues:**
- Check Gmail App Password is correct
- Verify sender email is whitelisted in Kindle settings
- Check spam folder
- Test with simple email client first

### Code Style

**Python:**
- Follow PEP 8
- Use f-strings for formatting
- Type hints optional but encouraged

**JavaScript:**
- Use `const` for constants, `let` for variables
- Camelcase for functions: `loadPageList()`
- Event handler naming: `handleConfirm()`, `handleCancel()`

**CSS:**
- Use CSS variables for colors
- BEM-like naming: `#component-element`
- Group related styles together

### Testing Checklist

Before committing changes:

- [ ] Flask server starts without errors
- [ ] All API endpoints respond correctly
- [ ] Page create/read/update/delete works
- [ ] Auto-save functions properly
- [ ] Preview renders markdown correctly
- [ ] Internal links work in preview
- [ ] EPUB generates without errors
- [ ] EPUB opens in reader
- [ ] Internal links work in EPUB
- [ ] Email sends successfully
- [ ] Book arrives on Kindle
- [ ] All keyboard shortcuts work
- [ ] Undo/redo functions properly
- [ ] No JavaScript console errors
- [ ] UI animations are smooth
- [ ] Status indicators update correctly

---

## Future Enhancements

### Planned Features
- [ ] Image upload and embedding
- [ ] Multiple book profiles
- [ ] Export to PDF
- [ ] Dark/light theme toggle
- [ ] Search across all pages
- [ ] Tag system for organization
- [ ] Version history / page snapshots
- [ ] Collaborative editing
- [ ] Cloud storage integration (Dropbox, Google Drive)
- [ ] Mobile-responsive design
- [ ] PWA support (offline editing)

### Under Consideration
- [ ] Spell check integration
- [ ] Word count statistics
- [ ] Export to other formats (MOBI, AZW3)
- [ ] Custom CSS for EPUB output
- [ ] Table of contents generator
- [ ] Footnotes/endnotes support
- [ ] Bibliography management
- [ ] Math equation support (LaTeX)
- [ ] Diagram support (Mermaid)

---

## Support & Contributing

### Getting Help
- Check [README.md](./README.md) for common issues
- Review this REFERENCE.md for technical details
- Open an issue on GitHub with:
  - Description of problem
  - Steps to reproduce
  - Error messages
  - Browser/OS version

### Contributing
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly
5. Commit: `git commit -m "Add amazing feature"`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code of Conduct
- Be respectful and constructive
- Test your changes before submitting
- Document new features
- Follow existing code style
- Keep commits focused and atomic

---

## License

MIT License - See LICENSE file for details

---

**Last Updated:** October 14, 2025
**Version:** 2.9
**Python:** 3.13.2
**Flask:** 3.1.2

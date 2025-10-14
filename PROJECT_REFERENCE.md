# JugaadPress - Project Reference

## 🎯 Project Overview

**JugaadPress** is a web-based Markdown editor designed to compile notes into a professional EPUB ebook and send it directly to your Kindle device via email. It features a refined GitHub-inspired dark theme interface with an intuitive sidebar, smart link autocomplete, and real-time auto-saving.

**Primary Use Case:** Create and organize learning notes (e.g., language study, technical documentation) and compile them into a proper EPUB ebook with table of contents, cover image, and working internal navigation for Kindle.

---

## 📁 Project Structure

```
JugaadPress/
├── app.py                 # Main Flask application (backend + API)
├── config.py              # Email and Kindle configuration (gitignored)
├── cover.jpg              # Book cover image (attached to Kindle email)
├── .gitignore             # Excludes config.py, __pycache__, venv
├── jugaadpressenv/        # Python virtual environment (Python 3.13)
├── pages/                 # Markdown content files
│   ├── 01_index.md        # Main landing page with navigation
│   └── 02_notes.md        # Example notes page
└── templates/
    └── index.html         # Frontend UI (single-page application)
```

---

## 🏗️ Architecture & Components

### **Backend (Flask - `app.py`)**

**Key Responsibilities:**
- Serve the web UI
- Provide REST API for page management
- Compile Markdown files into a single HTML book
- Send compiled book to Kindle via SMTP

**API Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serve main editor interface |
| `GET` | `/api/pages` | List all `.md` files in `pages/` directory |
| `GET` | `/api/page/<filename>` | Retrieve raw Markdown content of a page |
| `POST` | `/api/page/<filename>` | Save Markdown content to a page |
| `POST` | `/api/page` | Create a new markdown page |
| `DELETE` | `/api/page/<filename>` | Delete a markdown page |
| `POST` | `/api/page/<filename>/rename` | Rename a markdown page |
| `POST` | `/api/send-to-kindle` | Compile EPUB & email to Kindle |

**Core Functions:**

1. **`send_to_kindle()`** (`app.py:147-243`)
   - Creates a complete EPUB book using `ebooklib`
   - **Stable UUID:** Uses `uuid.uuid5(uuid.NAMESPACE_DNS, BOOK_TITLE)` for consistent book identification (same title = same UUID)
   - Embeds cover image as Base64 (no duplicates)
   - Converts each `.md` file to an EPUB chapter
   - **No Auto-Heading:** Uses markdown content as-is (preserves your custom headings)
   - Fixes internal links with URL decoding (`.md` → `.xhtml`)
   - **Link Handling:** Decodes URL-encoded filenames (`%20` for spaces) before mapping to `.xhtml`
   - **Back to Table of Contents:** Automatically adds "← Back to Table of Contents" link at bottom of each chapter (except first page)
   - Links to first page alphabetically (not hardcoded to specific filename)
   - Right-aligned, small, gray footer with horizontal rule separator
   - Generates proper TOC and navigation
   - Saves local copy for debugging (`{BOOK_TITLE}.epub`)
   - Creates multipart email with EPUB attachment
   - Subject: "Convert" (tells Kindle to process)
   - Sends via Gmail SMTP (port 587, STARTTLS)
   - Returns success/error status
   - **Note:** Kindle duplicate detection is unreliable even with stable UUIDs - manual deletion may be needed

2. **`create_page()`** (`app.py:81-102`)
   - Creates new markdown file with initial header
   - Validates filename and checks for duplicates
   - Returns new filename in JSON response

3. **`delete_page()`** (`app.py:104-117`)
   - Deletes markdown file from pages directory
   - Validates file existence before deletion

4. **`rename_page()`** (`app.py:119-145`)
   - Renames markdown files
   - Validates new filename and checks for conflicts
   - Returns old and new filenames in JSON

### **Frontend (Single-Page App - `templates/index.html`)**

**Technology Stack:**
- **Editor:** Custom native `<textarea>` with full undo/redo support
- **Markdown Parser:** [Marked.js](https://marked.js.org/) for live preview
- **Icons:** Font Awesome 6.5.1
- **Fonts:** JetBrains Mono (UI) & Fira Code (Editor) (Google Fonts)
- **Theme:** Refined GitHub Dark-inspired theme with professional colors
- **Smart Features:** Page link autocomplete, inline renaming, click-based page management

**Design Philosophy:**
- **GitHub-Inspired:** Refined dark theme with professional color palette
- **Snappy & Responsive:** Fast transitions (150-200ms) with smooth aesthetics
- **Intuitive UX:** Smart autocomplete, inline editing, visual feedback
- **Keyboard-First:** Full keyboard shortcut support for power users
- **Professional Polish:** Toast notifications, modal confirmations, proper feedback states

**UI Components:**

1. **Sidebar** (`#sidebar`)
   - **Header:** Animated blinking prompt (`>JUGAADPRESS`) with subtitle
   - **Page Controls:** "New" button with ripple hover effect for creating pages
   - **Page List:** Larger click areas (32px min-height), smooth slide animations
   - **Delete Button:** Appears on hover, red glow effect, confirmation modal
   - **Inline Rename:** Double-click page name to rename with auto-selected input
   - **Active State:** Green highlight with glow shadow effect
   - **Custom Scrollbar:** Themed scrollbar with accent colors

2. **Toolbar** (`#toolbar`)
   - **Labeled Buttons:** Icon + Text labels (Bold, Italic, Strike, etc.)
   - **Formatting Tools:** Bold, Italic, Strikethrough, Heading, Quote, Code
   - **List Tools:** Bullets, Numbers with clear labels
   - **Smart Link Tool:** Opens autocomplete dropdown, supports custom link text
   - **Preview Toggle:** Split-pane live preview with active state
   - **Visual Feedback:** Hover effects with blue glow and border highlights
   - **Separators:** Visual grouping of related tools

3. **Editor & Preview** (`#editor-container`)
   - **Split-Pane Layout:** Editor on left, optional preview on right
   - **Native Textarea:** Full browser undo/redo support (Ctrl+Z/Y)
   - **Smart Autocomplete:** Type `[[` to trigger page link dropdown
   - **Arrow Navigation:** ↑/↓ to navigate, Enter to select, Escape to cancel
   - **Live Preview:** Real-time Markdown rendering with GitHub-style formatting
   - **Decoupled Preview:** Preview navigates independently - clicking links doesn't affect editor
   - **Preview State:** Tracks separate `previewPage` state, fetches content on-demand
   - **Auto-Save:** 1.5s debounce with visual status indicators
   - **Snappy Loading:** 50ms fade transitions for instant feel
   - **Better Typography:** 15px font, 1.7 line-height, 0.3px letter-spacing

4. **Bottom Bar** (`#bottom-bar`)
   - **Status Indicator:** Color-coded dots (blue=saving, green=saved, red=error)
   - **View Shortcuts Link:** Clickable text to show all keyboard shortcuts
   - **Kindle Library Link:** Direct link to Amazon Kindle library (Japan) with hover effect
   - **Send Button:** Gradient glow effect with hover animation

5. **Modal System** (`#modal-overlay`)
   - **Confirmation Dialogs:** For destructive actions (send to Kindle)
   - **Unsaved Changes Warning:** Before page switching
   - **Backdrop Blur:** Professional overlay effect
   - **Smooth Animations:** Fade-in with slide-up effect

6. **Shortcuts Modal** (`#shortcuts-modal-overlay`)
   - **Beautiful Design:** GitHub Dark themed with green glow
   - **Two-Column Layout:** Organized by category (Formatting, Lists, Editing, Navigation, Autocomplete)
   - **Mac-Style Keys:** ⌘, ⇧, ⌥, ↵, ↑↓ symbols with styled kbd elements
   - **25 Total Shortcuts:** All shortcuts documented with descriptions
   - **Hover Effects:** Subtle background highlight on each shortcut item
   - **Close Options:** Click outside, press Esc, or click X button
   - **Trigger:** Click "View Shortcuts" in bottom bar
   - **Category Emojis:** ✨ Formatting, 📝 Lists, ✂️ Editing, 🔗 Navigation, 🎯 Autocomplete

7. **Toast Notifications** (`#toast`)
   - **Non-Intrusive Feedback:** Slide-in from right
   - **Success/Error States:** Color-coded borders and icons (✓ checkmarks)
   - **Auto-Dismiss:** 3-second timeout
   - **Clear Messaging:** Action confirmation and error details

8. **Autocomplete Dropdown** (`#autocomplete-dropdown`)
   - **Smart Triggering:** `[[` in editor or Link toolbar button
   - **Page Icon:** 📄 emoji for visual clarity
   - **Keyboard Navigation:** Full arrow key + Enter/Escape support
   - **Two Modes:**
     - `[[` mode: Auto-inserts `[Page Name]("./file.md")`
     - Toolbar mode: Uses selected text `[Custom Text]("./file.md")`
   - **Quoted Paths:** All links use quotes for space-safe filenames

**Key JavaScript Logic:**

**State Management:**
```javascript
const state = {
    currentPage: null,
    saveTimeout: null,
    previewVisible: false,
    unsavedChanges: false,
    sending: false
};
```

**Core Functions:**
- **`loadPageList()`:** Fetches page list, stores in state, populates sidebar with delete buttons
- **`loadPageContent(filename)`:** 200ms delay for double-click detection, checks unsaved changes
- **`savePageContent()`:** Auto-saves with error handling and toast feedback
- **`sendToKindle()`:** Shows confirmation modal, handles send with loading state
- **`createNewPage(filename)`:** Creates page, disables button, reloads list, loads new page
- **`deletePage(filename)`:** Shows warning modal, clears editor if active, reloads list
- **`enableRename(pageNameSpan, filename)`:** Inline input field, Enter/Escape/Blur handling
- **`showAutocomplete(pages, cursorPos, customText)`:** Smart dropdown with context
- **`insertPageLink(page, customText)`:** Two modes - `[[` auto or toolbar custom text, uses URL encoding

**Advanced Editing Functions (Preserve Undo/Redo):**
- **`duplicateLine()`:** Duplicates current line below using `document.execCommand`
- **`deleteLine()`:** Deletes entire line, handles edge cases (first/last/only line)
- **`insertLineBelow()`:** Inserts new line below cursor and moves cursor
- **`toggleComment()`:** Wraps/unwraps selection with `<!-- -->`
- **`toggleCodeBlock()`:** Wraps/unwraps selection with triple backticks
- **`moveLineUp()`/`moveLineDown()`:** Swaps current line with adjacent line
- **`increaseHeading()`/`decreaseHeading()`:** Adds/removes `#` from headings
- **`wrapSelection(before, after)`:** Smart toggle wrapping (bold, italic, etc.)
- **`insertAtLineStart(prefix)`:** Smart toggle for line-start formatting (headings, lists)

**Critical: All editing functions use `document.execCommand('insertText')` instead of `editor.value = ...` to preserve native browser undo/redo history.**
- **`wrapSelection(before, after)`:** Smart toggle formatting (detects existing formatting)
- **`insertAtLineStart(prefix)`:** Line-based formatting with toggle support
- **`togglePreview()`:** Shows/hides split-pane preview with state sync
- **`updatePreview()`:** Real-time Markdown → HTML conversion
- **`showToast(message, isError)`:** User feedback system with ✓/✗ icons
- **`showModal(title, message, onConfirm)`:** Reusable confirmation dialog
- **`showInputModal(title, message, placeholder, onConfirm)`:** Input dialog for new pages

**Auto-Save Mechanism:**
```javascript
editor.addEventListener('input', () => {
    state.unsavedChanges = true;
    updatePreview();
    clearTimeout(state.saveTimeout);
    updateStatus('Typing...', 'normal');
    state.saveTimeout = setTimeout(savePageContent, 1500);
});
```

**Keyboard Shortcuts (Mac: Cmd, Windows/Linux: Ctrl):**

**FORMATTING:**
- `Cmd/Ctrl+B` - **Bold** (toggleable)
- `Cmd/Ctrl+I` - *Italic* (toggleable)
- `Cmd/Ctrl+` ` - Inline code (toggleable)
- `Cmd/Ctrl+H` - Heading (toggleable)
- `Cmd/Ctrl+Q` - Quote
- `Cmd/Ctrl+E` - Code block (triple backticks)
- `Cmd/Ctrl+/` - HTML Comment

**LISTS:**
- `Cmd/Ctrl+L` - Bullet list
- `Cmd/Ctrl+Shift+L` - Numbered list

**EDITING:**
- `Cmd/Ctrl+D` - Duplicate current line
- `Cmd/Ctrl+Shift+K` - Delete line
- `Cmd/Ctrl+Enter` - Insert line below
- `Cmd/Ctrl+[` - Decrease heading level (## → #)
- `Cmd/Ctrl+]` - Increase heading level (# → ##)
- `Alt+↑/↓` - Move line up/down
- `Cmd/Ctrl+Z` - Undo (native, preserved)
- `Cmd/Ctrl+Y` - Redo (native, preserved)

**NAVIGATION:**
- `Cmd/Ctrl+K` - Insert link (shows autocomplete dropdown)
- `Cmd/Ctrl+P` - Toggle live preview
- `Cmd/Ctrl+S` - Force save
- Click "View Shortcuts" - Show all shortcuts

**AUTOCOMPLETE:**
- `[[` - Trigger page link autocomplete
- `↑/↓` - Navigate, `Enter` - Select, `Esc` - Cancel

**Smart Toggle Feature:**
All formatting tools detect existing formatting and remove it if present. For example:
- Select `**bold text**` → Click Bold → Becomes `bold text`
- Select `text` → Click Bold → Becomes `**text**`

**Error Handling:**
- Network errors show toast notifications
- Failed saves display error status
- API errors include descriptive messages
- Graceful fallbacks for missing data

---

## 🔧 Configuration (`config.py`)

**Note:** This file is gitignored and must be created manually.

```python
SENDER_EMAIL = "your-gmail@gmail.com"
SENDER_PASSWORD = "your-app-password"  # Gmail App Password (not regular password)
KINDLE_EMAIL = "your-kindle-email@kindle.com"
BOOK_TITLE = "My Japanese Notes"
COVER_FILENAME = "cover.jpg"
```

**Security Note:** Uses Gmail App Passwords (requires 2FA enabled on Google account).

---

## 📦 Dependencies

**Python (Flask Backend):**
```
Flask==3.1.2
markdown2==2.5.4
ebooklib==0.18
```

**Frontend (CDN):**
- Marked.js (Markdown to HTML parser for live preview)
- Font Awesome 6.5.1 (icons)
- Google Fonts (JetBrains Mono, Fira Code)

**Python Standard Library:**
- `smtplib` - SMTP email sending
- `email.mime.*` - Email attachment handling (MIMEMultipart, MIMEApplication, MIMEText)
- `os`, `re` - File operations and regex
- `io.BytesIO` - In-memory file handling for EPUB

---

## 🎨 Design System (GitHub Dark-Inspired Theme)

**Color Palette:**
```css
--bg-primary: #0d1117;        /* Deep dark background */
--bg-secondary: #161b22;      /* Sidebar/toolbar background */
--bg-tertiary: #21262d;       /* Elevated surfaces, hover states */
--accent-primary: #3fb950;    /* Green (success, active states) */
--accent-secondary: #58a6ff;  /* Blue (interactive elements) */
--accent-danger: #f85149;     /* Error red */
--text-primary: #e6edf3;      /* Main text */
--text-secondary: #8b949e;    /* Secondary text */
--text-dim: #6e7681;          /* Dim text, hints */
--border-color: #30363d;      /* Borders */
--shadow-glow: rgba(63, 185, 80, 0.15);   /* Green glow effect */
--shadow-glow-secondary: rgba(88, 166, 255, 0.1);  /* Blue glow effect */
--code-bg: #1c2128;           /* Code block background */
--link-color: #58a6ff;        /* Link color */
```

**Typography:**
- **Primary:** JetBrains Mono (monospace, terminal feel)
- **Editor:** Fira Code (coding ligatures support)
- **Fallbacks:** System monospace fonts

**Visual Effects:**
- **Snappy Transitions:** 150-200ms cubic-bezier for responsive feel
- **Smooth Animations:** Fade-in scale for page list items
- **Ripple Effects:** Expanding circle on "New" button hover
- **Pulsing Animations:** Status indicators, live preview header
- **Blinking Cursor:** Terminal-style prompt in sidebar header
- **Gradient Buttons:** Send button with primary-to-secondary gradient
- **Hover Feedback:** Subtle translateY (-1px to -2px) on buttons
- **Custom Scrollbars:** Themed with accent colors on hover
- **Loading States:** 50ms opacity fade for instant page switching feel

---

## 🔄 Workflow

1. **Creating/Editing Notes:**
   - Open browser → Navigate to `http://localhost:5000`
   - Click "New" button or select existing page from sidebar
   - Edit Markdown content with smart autocomplete
   - Auto-saves after 1.5s of inactivity

2. **Managing Pages:**
   - **Create:** Click "New" button, enter filename, starts editing
   - **Rename:** Double-click page name in sidebar, edit inline
   - **Delete:** Hover over page, click trash icon, confirm deletion
   - **Navigate:** Single click to load (200ms delay for double-click detection)

3. **Smart Linking (Fixed & Working):**
   - **Method 1:** Type `[[` → Select from dropdown → Auto-inserts `[Page Name](./file.md)`
   - **Method 2:** Select text → Click Link button → Choose page → `[Custom Text](./file.md)`
   - **URL Encoding:** Filenames with spaces/special chars automatically URL-encoded (`%20` for spaces)
   - **Preview Navigation:** Click links in preview to navigate independently (editor stays put)
   - **EPUB Links:** Automatically converted to proper `.xhtml` chapter references with URL decoding

4. **Sending to Kindle:**
   - Click "🚀 Send to Kindle" button
   - Backend compiles all pages → EPUB ebook with proper structure
   - Embeds cover image as Base64 (no duplicates)
   - Creates TOC and chapter navigation
   - Saves local copy: `{BOOK_TITLE}.epub`
   - Sends via Gmail SMTP with subject "Convert"
   - Kindle receives and converts EPUB → native format

---

## 🚀 Running the Application

**Setup:**
```bash
# Create virtual environment
python -m venv jugaadpressenv

# Activate environment
source jugaadpressenv/bin/activate  # macOS/Linux
# jugaadpressenv\Scripts\activate  # Windows

# Install dependencies
pip install Flask==3.1.2 markdown2==2.5.4 ebooklib==0.18

# Create config.py with your credentials
nano config.py
```

**Start Server:**
```bash
python app.py
# Server runs on http://0.0.0.0:5000 (accessible on local network)
```

---

## 📝 Page File Naming Convention

- Files must be `.md` (Markdown)
- Prefix with numbers for sorting (e.g., `01_index.md`, `02_notes.md`)
- Underscores converted to spaces in UI (e.g., `02_notes` → "02 Notes")

---

## 🔐 Security Considerations

1. **Config File:** Contains sensitive credentials → gitignored
2. **Gmail App Password:** Use dedicated app password (not account password)
3. **Kindle Email:** Whitelist sender email in Amazon Kindle settings
4. **No Authentication:** App has no user authentication (intended for local use)

---

## 🐛 Known Limitations & Future Enhancements

**Current Limitations:**
- No image embedding in Markdown (only cover image supported)
- Gmail SMTP only (hardcoded)
- Single book configuration (one title/cover)

**Potential Enhancements:**
- Support multiple books/collections
- Image upload and embedding
- User authentication for multi-user setups
- Export to PDF format
- Cloud storage integration (Dropbox, Google Drive)

---

## 🧭 Quick Reference for Claude

**When working on this project:**

1. **Adding Features to Backend:**
   - Flask routes in `app.py`
   - Modify `compile_book_html()` for book generation logic
   - Update email handling in `send_to_kindle()`

2. **Adding Features to Frontend:**
   - UI/CSS in `templates/index.html`
   - JavaScript in `<script>` section (lines 693-1037)
   - Color variables in `:root` (lines 15-28)
   - Cyberpunk theme uses custom design system (not Nord)

3. **Page Management:**
   - Markdown files in `pages/` directory
   - Naming: `##_filename.md` format (numbers optional, spaces supported)
   - Internal links: `[text](./filename.md)` with automatic URL encoding for spaces
   - All pages are equal - no special treatment for "index" page

4. **Testing Email:**
   - Ensure `config.py` exists with valid credentials
   - Whitelist sender email in Kindle settings
   - Check `cover.jpg` exists in root directory

5. **Dependencies:**
   - Always work within virtual environment (`jugaadpressenv`)
   - Update `pip freeze` if adding new packages

**File Change Impact Map:**
- `app.py` changes → Restart Flask server
- `index.html` changes → Refresh browser (hard refresh: Cmd+Shift+R)
- `pages/*.md` changes → Auto-detected by app
- `config.py` changes → Restart Flask server

---

## 📚 External Resources

- [Marked.js Documentation](https://marked.js.org/)
- [markdown2 Documentation](https://github.com/trentm/python-markdown2)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Font Awesome Icons](https://fontawesome.com/icons)
- [JetBrains Mono Font](https://www.jetbrains.com/lp/mono/)
- [Fira Code Font](https://github.com/tonsky/FiraCode)
- [Amazon Kindle Email Docs](https://www.amazon.com/gp/sendtokindle/email)

---

## 🎉 Recent Updates (v2.0 - Cyberpunk Edition)

**Major UI/UX Overhaul:**
- ✅ Complete redesign with cyberpunk/hacker aesthetic
- ✅ Removed EasyMDE dependency, now using native `<textarea>` with full undo/redo
- ✅ Smart toggle formatting (click icon again to remove formatting)
- ✅ Split-pane live preview with Marked.js
- ✅ Modal confirmation dialogs for destructive actions
- ✅ Toast notifications for user feedback
- ✅ Unsaved changes detection and warnings
- ✅ Full keyboard shortcut support (Ctrl+B, Ctrl+I, Ctrl+P, etc.)
- ✅ Animated UI elements (glows, pulses, slide-ins)
- ✅ Custom scrollbars and visual polish
- ✅ Professional error handling with clear messaging
- ✅ Loading states and disabled button handling
- ✅ Color-coded status indicators (saving/saved/error)

**Design Improvements:**
- Neon green (`#00ff9f`) and cyan (`#00d4ff`) accents
- Glowing box shadows on interactive elements
- Terminal-style blinking cursor in header
- Smooth animations throughout (0.2-0.3s transitions)
- Monospace fonts (JetBrains Mono, Fira Code)
- Professional modal and toast systems
- Better visual hierarchy and spacing

---

**Last Updated:** October 8, 2025
**Python Version:** 3.13.2
**Project Type:** Flask Web Application + Markdown Editor
**UI Version:** 2.0 (Cyberpunk Edition)

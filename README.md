# JugaadPress

> A lightweight web-based Markdown editor that compiles your notes into professional EPUB ebooks and sends them directly to your Kindle.

![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg) ![Flask](https://img.shields.io/badge/flask-3.1.2-green.svg)

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd JugaadPress

# Create virtual environment
python3 -m venv jugaadpressenv
source jugaadpressenv/bin/activate  # macOS/Linux
# jugaadpressenv\Scripts\activate   # Windows

# Install dependencies
pip install Flask==3.1.2 markdown2==2.5.4 EbookLib==0.19
```

### Configuration

Create a `config.py` file in the root directory:

```python
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-app-password"  # Gmail App Password (requires 2FA)
KINDLE_EMAIL = "your-kindle@kindle.com"
BOOK_TITLE = "My Learning Notes"
COVER_FILENAME = "cover.jpg"
```

**Important:**
- Use a [Gmail App Password](https://support.google.com/accounts/answer/185833), not your regular password
- Add your sender email to your [Kindle's approved email list](https://www.amazon.com/hz/mycd/myx#/home/settings/payment)
- Place a `cover.jpg` file in the root directory (optional, but recommended)

### Run

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## 📖 Usage

### Writing Notes

1. **Create a new page:** Click the "New" button in the sidebar
2. **Write Markdown:** Use the toolbar or keyboard shortcuts to format text
3. **Auto-save:** Your work saves automatically every 1.5 seconds
4. **Live Preview:** Toggle preview with `Cmd+P` / `Ctrl+P`

### Managing Pages

- **Navigate:** Click a page name to load it
- **Rename:** Double-click a page name to rename
- **Delete:** Hover over a page and click the trash icon
- **Link pages:** Type `[[` to get a dropdown of all pages

### Sending to Kindle

Click **"Send to Kindle"** button to:
1. Compile all markdown files into a single EPUB book
2. Add a table of contents and navigation
3. Email it to your Kindle device
4. Save a local copy as `{BOOK_TITLE}.epub`

Your book appears on Kindle in ~2-5 minutes.

---

## ⌨️ Keyboard Shortcuts

### Formatting
- `Cmd/Ctrl + B` - **Bold**
- `Cmd/Ctrl + I` - *Italic*
- `Cmd/Ctrl + H` - Heading
- `Cmd/Ctrl + Q` - Quote
- `Cmd/Ctrl + `` ` `` - Inline code
- `Cmd/Ctrl + E` - Code block
- `Cmd/Ctrl + /` - HTML comment

### Lists
- `Cmd/Ctrl + L` - Bullet list
- `Cmd/Ctrl + Shift + L` - Numbered list

### Editing
- `Cmd/Ctrl + D` - Duplicate line
- `Cmd/Ctrl + Shift + K` - Delete line
- `Cmd/Ctrl + Enter` - New line below
- `Cmd/Ctrl + [` - Decrease heading level
- `Cmd/Ctrl + ]` - Increase heading level
- `Alt + ↑/↓` - Move line up/down
- `Cmd/Ctrl + Z` - Undo
- `Cmd/Ctrl + Y` - Redo

### Navigation
- `Cmd/Ctrl + K` - Insert link
- `Cmd/Ctrl + P` - Toggle preview
- `Cmd/Ctrl + S` - Force save
- `[[` - Trigger page link autocomplete

**Click "View Shortcuts" in the bottom bar to see the full list.**

---

## 🎨 Features

- **GitHub Dark Theme** - Professional dark interface with green/blue accents
- **Smart Autocomplete** - Type `[[` to link between pages
- **Live Preview** - Real-time Markdown rendering with syntax highlighting
- **Undo/Redo Support** - Full native browser undo history preserved
- **Auto-save** - Never lose your work
- **Page Management** - Create, rename, delete pages with inline editing
- **EPUB Generation** - Proper book structure with TOC and navigation
- **Internal Links** - Links work both in preview and final EPUB
- **Kindle Integration** - One-click send to Kindle via email
- **Keyboard First** - 25+ shortcuts for efficient editing

---

## 📝 Tips

### File Naming
- Prefix files with numbers for sorting: `01_intro.md`, `02_chapter1.md`
- Use underscores or spaces (spaces are supported via URL encoding)
- Files appear in alphabetical order in sidebar and book TOC

### Linking Between Pages
```markdown
<!-- Auto-insert page link -->
Type [[ and select from dropdown

<!-- Manual link -->
[Link Text](./01_intro.md)

<!-- Links with spaces -->
[Chapter 1](./01_My%20Chapter.md)
```

### Book Structure
- The **first page alphabetically** becomes your table of contents
- All pages are compiled in alphabetical order
- Each chapter gets a "← Back to Table of Contents" link (except first page)

---

## 🐛 Troubleshooting

### Book not arriving on Kindle?
1. Check sender email is approved in [Kindle settings](https://www.amazon.com/hz/mycd/myx#/home/settings/payment)
2. Verify Gmail App Password is correct (not regular password)
3. Check spam folder in your email
4. Wait 5-10 minutes (delivery can be slow)

### Links not working?
- Make sure filenames match exactly (case-sensitive)
- Use URL encoding for spaces: `%20` or `./file%20name.md`
- The `[[` autocomplete handles encoding automatically

### Undo/Redo not working?
- This is a known issue if you manually edited `editor.value` in browser console
- Refresh the page to reset undo history

### Duplicate books on Kindle?
- Kindle's duplicate detection is unreliable (Amazon limitation)
- Delete old versions manually from Kindle library
- We use stable UUIDs, but Kindle still sometimes creates duplicates

---

## 📦 Project Structure

```
JugaadPress/
├── app.py                 # Flask backend (API + EPUB generation)
├── config.py              # Email/Kindle configuration (gitignored)
├── cover.jpg              # Book cover image
├── pages/                 # Your markdown files go here
│   ├── 0_Index.md
│   ├── 1.1_Notes.md
│   └── ...
├── templates/
│   └── index.html         # Frontend UI (single-page app)
└── jugaadpressenv/        # Python virtual environment
```

---

## 🔗 Links

- **Detailed Documentation:** See [REFERENCE.md](./REFERENCE.md) for technical details
- **Changelog & Features:** See [REFERENCE.md](./REFERENCE.md#changelog) for complete feature list
- **Report Issues:** [GitHub Issues](https://github.com/your-repo/issues)

---

## 📄 License

MIT License - Use freely for personal or commercial projects.

---

## 🙏 Credits

Built with:
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [markdown2](https://github.com/trentm/python-markdown2) - Markdown to HTML
- [ebooklib](https://github.com/aerkalov/ebooklib) - EPUB generation
- [Marked.js](https://marked.js.org/) - Live preview
- [Font Awesome](https://fontawesome.com/) - Icons
- [Fira Code](https://github.com/tonsky/FiraCode) & [JetBrains Mono](https://www.jetbrains.com/lp/mono/) - Fonts

---

**Made with ❤️ for learning and note-taking**

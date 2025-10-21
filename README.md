# 📚 JugaadPress

> Transform your Markdown notes into Kindle books. Store everything in Google Drive. 100% free.

![Status](https://img.shields.io/badge/status-beta-yellow) ![Python](https://img.shields.io/badge/python-3.13-blue) ![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

- **📝 Markdown Editor** - Write notes with live preview
- **☁️ Cloud Sync** - Files stored in YOUR Google Drive
- **📚 Multi-Book Support** - Organize notes into separate projects
- **⚙️ Dashboard** - Manage all books and settings in one place
- **📱 Cross-Device** - Access from anywhere
- **📖 Send to Kindle** - One-click EPUB generation and delivery

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
source jugaadpressenv/bin/activate
pip install -r requirements.txt
```

### 2. Set Up Google OAuth
See [docs/SETUP.md](docs/SETUP.md) for detailed instructions.

**Quick version:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable Drive API
3. Create OAuth credentials
4. Download as `client_secret.json`

### 3. Migrate Existing Notes (Optional)
If you have local notes in `pages/`:
```bash
python tools/migrate_local_to_drive.py
```

### 4. Run the App
```bash
python app.py
```

Open http://localhost:5001 and sign in with Google!

---

## 📖 Usage

### First Time Setup
1. Click **"Sign in with Google"**
2. Allow Drive access
3. Create your first book
4. Configure settings (Gmail, Kindle email)

### Daily Workflow
1. Open JugaadPress
2. Select book from dashboard
3. Click **Edit** → Write notes
4. Click **Send to Kindle**

---

## 🗂️ Project Structure

```
JugaadPress/
├── app.py                  # Main application
├── requirements.txt        # Dependencies
├── templates/              # Web pages
│   ├── landing.html       # Sign-in page
│   ├── dashboard.html     # Book manager
│   └── editor.html        # Markdown editor
├── tools/                  # Utilities
│   ├── migrate_local_to_drive.py
│   ├── verify_drive_structure.py
│   └── sync_drive_to_local.py
└── docs/                   # Documentation
    ├── SETUP.md           # Setup guide
    └── API.md             # API reference
```

---

## 📁 Drive Structure

Your Google Drive will have:
```
/JugaadPress/
  ├── .user_settings.json      # Global settings
  └── My Book/                 # Each book is a folder
      ├── .book_settings.json
      ├── 01_intro.md
      └── 02_notes.md
```

---

## 🛠️ Tools

### Migrate Local Notes to Drive
```bash
python tools/migrate_local_to_drive.py
```

### Verify Drive Structure
```bash
python tools/verify_drive_structure.py
```

### Sync Drive to Local (Backup)
```bash
python tools/sync_drive_to_local.py
```

---

## 📚 Documentation

- **[SETUP.md](docs/SETUP.md)** - Detailed setup guide
- **[API.md](docs/API.md)** - API reference for developers
- **[TESTING_GUIDE.md](docs/TESTING_GUIDE.md)** - How to test the app

---

## 🐛 Troubleshooting

### "client_secret.json not found"
Get OAuth credentials from Google Cloud Console. See [SETUP.md](docs/SETUP.md).

### "OAuth redirect error"
Add `http://localhost:5001/oauth2callback` to authorized redirect URIs in Google Cloud Console.

### "No books found"
Run migration tool or create a new book from dashboard.

---

## 🎯 Roadmap

- [x] Google Drive storage
- [x] Multi-book support
- [x] Dashboard with settings editor
- [ ] Markdown editor integration
- [ ] Send to Kindle functionality
- [ ] Cover image upload
- [ ] Deploy to Vercel
- [ ] Mobile app

---

## 💰 Cost

**Free Forever!**
- Hosting: Vercel free tier
- Storage: User's Google Drive (15GB free)
- OAuth: Google Cloud (free)

---

## 📄 License

MIT License - See LICENSE file

---

## 🙏 Credits

Built with:
- Flask
- Google Drive API
- markdown2
- ebooklib

---

**Questions?** Open an issue on GitHub!

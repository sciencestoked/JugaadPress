# JugaadPress Setup Guide

Complete setup instructions to get JugaadPress running.

---

## 📋 Prerequisites

- Python 3.13+ (or 3.8+)
- Google account
- Terminal/Command Line access

---

## 🔧 Step 1: Install Dependencies

```bash
# Activate virtual environment
source jugaadpressenv/bin/activate

# Install all required packages
pip install -r requirements.txt
```

**What gets installed:**
- Flask (web framework)
- Google Auth libraries
- Google Drive API
- markdown2 (Markdown to HTML)
- ebooklib (EPUB generation)

---

## 🔐 Step 2: Set Up Google OAuth

### 2.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name: `JugaadPress`
4. Click "Create"

### 2.2 Enable Drive API

1. Go to **APIs & Services** → **Library**
2. Search: "Google Drive API"
3. Click → **Enable**

### 2.3 Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Choose: **External**
3. Fill in:
   - App name: `JugaadPress`
   - User support email: Your email
   - Developer contact: Your email
4. Click "Save and Continue"

### 2.4 Add Scopes

1. Click "Add or Remove Scopes"
2. Search and add:
   - `https://www.googleapis.com/auth/drive.file`
3. Click "Update" → "Save and Continue"

### 2.5 Add Test Users

1. Click "Add Users"
2. Enter your Gmail address
3. Click "Add" → "Save and Continue"

### 2.6 Create OAuth Client

1. Go to **APIs & Services** → **Credentials**
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: **Web application**
4. Name: `JugaadPress Web Client`
5. Authorized redirect URIs:
   ```
   http://localhost:5001/oauth2callback
   ```
6. Click "Create"

### 2.7 Download Credentials

1. Click **Download JSON**
2. Save as `client_secret.json` in JugaadPress directory

---

## 📦 Step 3: Migrate Existing Notes (Optional)

If you have notes in `pages/` folder:

```bash
python tools/migrate_local_to_drive.py
```

Follow prompts:
1. Sign in with Google
2. Enter book name (e.g., "My Japanese Notes")
3. Wait for migration
4. Verify in Google Drive

---

## ▶️ Step 4: Run the App

```bash
python app.py
```

Expected output:
```
 * Running on http://0.0.0.0:5001
 * Debug mode: on
```

---

## 🌐 Step 5: First Sign-In

1. Open http://localhost:5001
2. Click **"Sign in with Google"**
3. Choose your Google account
4. Click **"Allow"** (grants Drive access)
5. Redirects to dashboard

---

## ✅ Step 6: Verify Setup

```bash
python tools/verify_drive_structure.py
```

Should show:
```
✅ Everything looks good!
```

---

## 🎯 Next Steps

1. **Configure global settings:**
   - Gmail app password
   - Kindle email

2. **Create your first book:**
   - Click "+ New Book"
   - Enter name
   - Start writing!

3. **Send to Kindle:**
   - Click "Send to Kindle" button
   - Book arrives in 2-5 minutes

---

## 🐛 Common Issues

### "client_secret.json not found"

Make sure file is in root directory:
```bash
ls client_secret.json
```

### "redirect_uri_mismatch"

Add exact URI to Google Cloud Console:
```
http://localhost:5001/oauth2callback
```

### "Access blocked: This app's request is invalid"

Add yourself as test user in OAuth consent screen.

### "No module named 'google'"

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 📧 Get Gmail App Password

1. Go to [Google Account](https://myaccount.google.com/)
2. Security → 2-Step Verification → **App passwords**
3. Select app: **Mail**
4. Copy 16-character password
5. Paste in JugaadPress settings

---

## 📱 Add Kindle Email to Whitelist

1. Go to [Amazon Kindle Settings](https://www.amazon.com/hz/mycd/myx#/home/settings/payment)
2. Scroll to "Personal Document Settings"
3. Add your Gmail to "Approved Personal Document E-mail List"

---

## 🎉 You're Ready!

Your setup is complete. Enjoy using JugaadPress!

**Need help?** See [TESTING_GUIDE.md](./TESTING_GUIDE.md) or open an issue on GitHub.

# JugaadPress - Complete Testing Guide

## 🎯 What We Built

A full web application with:
- **Landing page** with Google Sign-In
- **Dashboard** with book management + settings editor
- **Multi-book support** (multiple projects per user)
- **Global + Book-specific settings** (all editable from dashboard)
- **Google Drive storage** (everything in user's Drive)

---

## 📋 Prerequisites

### 1. Install Dependencies

```bash
source jugaadpressenv/bin/activate
pip install -r requirements.txt
```

### 2. Set Up Google Cloud OAuth

Follow [GOOGLE_DRIVE_SETUP.md](./GOOGLE_DRIVE_SETUP.md) to:
1. Create Google Cloud project
2. Enable Drive API
3. Create OAuth credentials
4. Download `client_secret.json`

**Important:** Add these redirect URIs in Google Cloud Console:
```
http://localhost:5001/oauth2callback
```

---

## 🚀 How to Test

### Step 1: Start the Web App

```bash
python app_web.py
```

**Expected output:**
```
 * Running on http://0.0.0.0:5001
 * Debug mode: on
```

---

### Step 2: Test Landing Page

1. Open http://localhost:5001

**What you should see:**
```
┌────────────────────────────────────────┐
│  📚 JugaadPress                         │
│  Transform Your Notes Into Kindle Books │
│                                        │
│  ✨ Features (4 cards)                 │
│  [Sign in with Google] button          │
│  Privacy notice                        │
└────────────────────────────────────────┘
```

2. Click **"Sign in with Google"**

---

### Step 3: Test Google OAuth Flow

**What happens:**
1. Redirects to Google sign-in page
2. Select your Google account
3. **Permission screen shows:**
   ```
   JugaadPress wants to:
   ✓ See your email address
   ✓ See your personal info
   ✓ See and manage Google Drive files created by this app
   ```
4. Click **"Allow"**
5. Redirects back to dashboard

**Troubleshooting:**
- **"redirect_uri_mismatch"** → Check redirect URI in Google Cloud Console matches exactly
- **"access_denied"** → You clicked "Cancel", try again
- **"invalid_client"** → `client_secret.json` is wrong or missing

---

### Step 4: Test Dashboard

After OAuth, you should land on the dashboard:

```
┌─────────────────┬──────────────────────────┐
│ MY BOOKS        │ SETTINGS                 │
│                 │ [Global] [Book-Specific] │
│ (empty)         │                          │
│                 │ ⚙️ GLOBAL SETTINGS       │
│ [+ New Book]    │ Sender Email: [____]     │
│                 │ Gmail App Password:[___] │
│                 │ Kindle Email: [____]     │
│                 │ [Save Global Settings]   │
└─────────────────┴──────────────────────────┘
```

**Test:**
1. ✅ User email shows in header (your@gmail.com)
2. ✅ "MY BOOKS" panel is empty (first time)
3. ✅ Global Settings tab is active
4. ✅ Sign Out button works

---

### Step 5: Test Creating a Book

1. Click **[+ New Book]**
2. Enter book name: `My Study Notes`
3. Click OK

**What should happen:**
- Book appears in left panel
- Shows "0 pages"
- Has [Edit] and [Delete] buttons

**Check Google Drive:**
- Go to https://drive.google.com
- You should see `/JugaadPress/` folder
- Inside: `/JugaadPress/My Study Notes/` folder
- Inside that: `.book_settings.json` file

---

### Step 6: Test Global Settings

1. Fill in the form:
   - **Sender Email:** `your@gmail.com`
   - **Gmail App Password:** `xxxx-xxxx-xxxx-xxxx` (get from Google)
   - **Kindle Email:** `your-kindle@kindle.com`

2. Click **[Save Global Settings]**

**What should happen:**
- Alert: "✓ Global settings saved!"
- Settings are stored in Drive

**Check Drive:**
- `/JugaadPress/.user_settings.json` file created
- Contains your settings (Gmail password is stored - will encrypt later!)

---

### Step 7: Test Book Settings

1. Click on a book in the left panel (e.g., "My Study Notes")
2. Book becomes highlighted (green border)
3. Right panel switches to **Book Settings** tab
4. Form shows:
   - **Book Title:** `My Study Notes` (pre-filled)
   - **Cover Image:** File upload
   - [Save Book Settings] button
   - [Send This Book to Kindle] button

**Test:**
1. Change book title to: `My Awesome Notes`
2. Click [Save Book Settings]
3. Alert: "✓ Book settings saved!"

**Check Drive:**
- `/JugaadPress/My Study Notes/.book_settings.json` updated

---

### Step 8: Test Creating Multiple Books

1. Create 3 books:
   - `My Study Notes`
   - `Novel Draft`
   - `Japanese Learning`

2. Click between them

**What should happen:**
- Selected book highlights in green
- Right panel shows that book's settings
- Each book has independent settings

---

### Step 9: Test Deleting a Book

1. Click trash icon on a book
2. Confirm deletion
3. Book disappears from list

**Check Drive:**
- Book folder moved to trash (not permanently deleted)
- Can restore from Drive if needed

---

### Step 10: Check Drive Structure

Go to Google Drive and verify:

```
/JugaadPress/
  ├── .user_settings.json           ← Global settings
  ├── My Study Notes/
  │   └── .book_settings.json       ← Book settings
  ├── Novel Draft/
  │   └── .book_settings.json
  └── Japanese Learning/
      └── .book_settings.json
```

Perfect! 🎉

---

## 🧪 Advanced Testing

### Test Sign Out & Sign In Again

1. Click **Sign Out**
2. Should redirect to landing page
3. Click **Sign in with Google**
4. Should authenticate faster (token cached)
5. Dashboard loads with your books still there

### Test Multiple Google Accounts

1. Sign out
2. Sign in with different Google account
3. Should see empty dashboard (different user)
4. Each user has separate `/JugaadPress/` folder in THEIR Drive

### Test Settings Persistence

1. Set global settings
2. Close browser completely
3. Reopen, sign in
4. Settings still there! (stored in Drive)

---

## ❌ What's NOT Working Yet

These features are coded but need the editor integration:

1. **[Edit] button** → Opens editor (need to update index.html)
2. **[Send to Kindle]** → Generates EPUB (need to integrate with app_web.py)
3. **Page management** → Currently no pages created yet

---

## 🐛 Common Issues

### "No module named 'google'"

```bash
pip install google-auth google-auth-oauthlib google-api-python-client
```

### "client_secret.json not found"

Make sure file is in root directory:
```bash
ls client_secret.json
```

### OAuth redirect error

Check `REDIRECT_URI` in `app_web.py` matches Google Cloud Console:
```python
REDIRECT_URI = "http://localhost:5001/oauth2callback"
```

### Session expires / "credentials not found"

Sign out and sign in again. Sessions expire after browser close (will fix with persistent tokens).

---

## ✅ Success Checklist

After testing, you should have:

- [ ] Landing page loads
- [ ] Google Sign-In works
- [ ] Dashboard shows after auth
- [ ] Can create multiple books
- [ ] Can see books in left panel
- [ ] Can edit global settings
- [ ] Can edit book-specific settings
- [ ] Settings persist in Google Drive
- [ ] Can delete books
- [ ] Can sign out and back in
- [ ] Drive folder structure is correct

---

## 📊 What We Have vs What's Next

### ✅ Done:
- Landing page
- Google OAuth
- Dashboard UI
- Multi-book management
- Settings editor (Global + Book)
- Drive storage
- Session management

### 🚧 Next Steps:
1. Integrate editor (click Edit → opens index.html with that book's pages)
2. Update index.html to work with book context
3. Implement "Send to Kindle" for specific book
4. Add cover image upload
5. Deploy to Vercel

---

## 🎉 What You Can Tell Users Now

> "JugaadPress is a web app where you sign in with Google, create multiple books/projects, write notes in Markdown, and send them to your Kindle. Everything is stored in YOUR Google Drive. We never see your data. 100% free!"

**Features:**
- ✅ Multi-book support
- ✅ Cloud sync via Google Drive
- ✅ Privacy-first (data in user's Drive)
- ✅ Zero hosting costs
- ✅ Settings management
- 🚧 Markdown editor (coming next)
- 🚧 Send to Kindle (coming next)

---

**Questions?** Let me know what's not working and I'll help debug!

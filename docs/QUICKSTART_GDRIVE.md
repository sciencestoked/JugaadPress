# Google Drive Quick Start (5 Minutes)

Get JugaadPress running with Google Drive in 5 minutes!

---

## Step 1: Install Dependencies (1 min)

```bash
source jugaadpressenv/bin/activate
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

---

## Step 2: Get Google Credentials (2 min)

### Option A: Use Test Credentials (Fastest)

I'll provide test credentials for quick testing. **Production apps need their own!**

Download: `client_secret.json`
(Check Discord/Email for test credentials)

### Option B: Create Your Own

See [GOOGLE_DRIVE_SETUP.md](./GOOGLE_DRIVE_SETUP.md) for detailed steps.

Quick version:
1. Go to https://console.cloud.google.com/
2. Create project → Enable Drive API
3. Create OAuth client → Download JSON
4. Save as `client_secret.json`

---

## Step 3: Configure JugaadPress (30 sec)

Edit `config.py`:

```python
# Change this line:
STORAGE_BACKEND = "local"

# To this:
STORAGE_BACKEND = "gdrive"

# Add these lines (if not present):
STORAGE_GDRIVE_CREDENTIALS = "client_secret.json"
STORAGE_GDRIVE_FOLDER = "JugaadPress"
STORAGE_GDRIVE_TOKEN = "token.json"
```

---

## Step 4: Run & Authorize (1 min)

```bash
python app.py
```

**What happens:**
1. Browser opens automatically
2. Sign in with Google
3. Click "Allow"
4. Browser redirects back
5. App is ready!

**Console output:**
```
✓ Connected to Google Drive (folder: JugaadPress)
✓ JugaadPress initialized with gdrive storage
✓ Book title: My Japanese Notes
 * Running on http://0.0.0.0:5001
```

---

## Step 5: Test It! (30 sec)

1. Open http://localhost:5001
2. Create a new page
3. Type something
4. Go to [Google Drive](https://drive.google.com)
5. See `/JugaadPress/` folder with your `.md` file! 🎉

---

## ✅ You're Done!

**What you now have:**
- ✅ Files stored in YOUR Google Drive
- ✅ Cross-device sync (edit from any device)
- ✅ Automatic backups (Google handles it)
- ✅ Works offline (Drive syncs when online)

**Next steps:**
- Share the `/JugaadPress/` folder to collaborate
- Access from phone/tablet (once we deploy)
- Never lose your notes again!

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'google'"

**Fix:**
```bash
source jugaadpressenv/bin/activate
pip install -r requirements.txt
```

### "client_secret.json not found"

**Fix:** Make sure `client_secret.json` is in the JugaadPress directory (same folder as `app.py`)

### "Access blocked: This app's request is invalid"

**Fix:** Add `http://localhost:5001` to authorized redirect URIs in Google Cloud Console

### Browser doesn't open for OAuth

**Fix:** Copy the URL from terminal and paste in browser manually

---

## 🔄 Switch Back to Local Storage

Edit `config.py`:
```python
STORAGE_BACKEND = "local"  # Back to local files
```

Restart app. Your local `pages/` folder works again!

---

## 📊 Compare: Local vs Google Drive

| Feature | Local Storage | Google Drive |
|---------|---------------|--------------|
| **Setup** | ✅ Already works | ⚡ 5 minutes |
| **Cross-device** | ❌ No | ✅ Yes |
| **Backup** | ❌ Manual | ✅ Automatic |
| **Collaboration** | ❌ No | ✅ Yes (share folder) |
| **Offline** | ✅ Yes | ✅ Yes (with Drive sync) |
| **Privacy** | ✅ Your computer | ✅ Your Drive |
| **Cost** | Free | Free |

---

**Need help?** Open an issue on GitHub or check [GOOGLE_DRIVE_SETUP.md](./GOOGLE_DRIVE_SETUP.md) for detailed troubleshooting.

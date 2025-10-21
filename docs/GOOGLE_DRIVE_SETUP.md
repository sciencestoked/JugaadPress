# Google Drive Integration Setup

Complete guide to set up Google Drive storage for JugaadPress.

---

## Prerequisites

- Google account
- Python 3.13+
- JugaadPress codebase (with storage abstraction)

---

## Step 1: Create Google Cloud Project

### 1.1 Go to Google Cloud Console

Visit: https://console.cloud.google.com/

### 1.2 Create New Project

1. Click "Select a project" dropdown (top bar)
2. Click "New Project"
3. Enter details:
   - **Project name:** `JugaadPress`
   - **Organization:** (leave as is)
4. Click "Create"
5. Wait for project creation (~30 seconds)

---

## Step 2: Enable Google Drive API

### 2.1 Enable the API

1. In the Cloud Console, go to **APIs & Services** → **Library**
2. Search for "Google Drive API"
3. Click on "Google Drive API"
4. Click **"Enable"**
5. Wait for API to be enabled

---

## Step 3: Create OAuth 2.0 Credentials

### 3.1 Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Choose **"External"** (allows any Google user)
3. Click **"Create"**

4. Fill in App Information:
   - **App name:** `JugaadPress`
   - **User support email:** Your email
   - **App logo:** (optional, can add later)
   - **Application home page:** `http://localhost:5001` (for now)
   - **Authorized domains:** (leave empty for local testing)
   - **Developer contact:** Your email

5. Click **"Save and Continue"**

### 3.2 Add Scopes

1. Click **"Add or Remove Scopes"**
2. Filter for: `drive.file`
3. Select:
   - ✅ `https://www.googleapis.com/auth/drive.file`
     (Create, read, and modify files created by this app)
4. Click **"Update"**
5. Click **"Save and Continue"**

### 3.3 Add Test Users (for development)

1. Click **"Add Users"**
2. Enter your Gmail address
3. Click **"Add"**
4. Click **"Save and Continue"**

### 3.4 Review and Submit

1. Review all settings
2. Click **"Back to Dashboard"**

**Note:** For local testing, the app stays in "Testing" mode. For public release, you'll submit for verification later.

---

## Step 4: Create OAuth Client ID

### 4.1 Create Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **"+ Create Credentials"** → **"OAuth client ID"**
3. Choose **"Web application"**

### 4.2 Configure Web Client

Fill in:
- **Name:** `JugaadPress Web Client`
- **Authorized JavaScript origins:**
  ```
  http://localhost:5001
  http://localhost:3000
  ```
- **Authorized redirect URIs:**
  ```
  http://localhost:5001/oauth2callback
  http://localhost:3000/oauth2callback
  ```

Click **"Create"**

### 4.3 Download Credentials

1. A popup will show your Client ID and Secret
2. Click **"Download JSON"**
3. Save the file as `client_secret.json` in your JugaadPress directory

**File structure:**
```json
{
  "web": {
    "client_id": "123456789-abc.apps.googleusercontent.com",
    "client_secret": "GOCSPX-xxxxxxxxxxxxx",
    "redirect_uris": ["http://localhost:5001/oauth2callback"],
    ...
  }
}
```

---

## Step 5: Install Python Dependencies

```bash
source jugaadpressenv/bin/activate
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

Update `requirements.txt`:
```bash
pip freeze | grep google > requirements_google.txt
cat requirements_google.txt >> requirements.txt
```

---

## Step 6: Configure JugaadPress

### 6.1 Update config.py

```python
# config.py

# Storage backend
STORAGE_BACKEND = "gdrive"

# Google Drive settings
STORAGE_GDRIVE_CREDENTIALS = "client_secret.json"
STORAGE_GDRIVE_FOLDER = "JugaadPress"  # Folder name in Drive
STORAGE_GDRIVE_TOKEN = "token.json"    # Saved OAuth token (auto-generated)

# Email/Kindle settings (still needed for sending books)
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-app-password"
KINDLE_EMAIL = "your-kindle@kindle.com"
BOOK_TITLE = "My Notes"
COVER_FILENAME = "cover.jpg"
```

### 6.2 Update .gitignore

Add these lines to `.gitignore`:
```
client_secret.json
token.json
credentials.json
```

**Important:** Never commit OAuth credentials to Git!

---

## Step 7: Test Locally

### 7.1 Run the app

```bash
python app.py
```

### 7.2 First-time OAuth Flow

1. Visit http://localhost:5001
2. Browser will redirect to Google sign-in
3. Sign in with the Google account you added as test user
4. Click **"Allow"** to grant Drive access
5. Browser redirects back to app
6. A `token.json` file is created (stores your OAuth token)

### 7.3 Verify Drive Integration

1. Create a new page in JugaadPress
2. Go to [Google Drive](https://drive.google.com)
3. You should see a `/JugaadPress/` folder
4. Inside: your `.md` files

---

## Step 8: Production Deployment (Vercel)

### 8.1 Update OAuth URLs

When deploying to production (e.g., `jugaadpress.com`):

1. Go back to Google Cloud Console → Credentials
2. Edit your OAuth client
3. Add production URLs:
   - **Authorized JavaScript origins:**
     ```
     https://jugaadpress.com
     https://jugaadpress.vercel.app
     ```
   - **Authorized redirect URIs:**
     ```
     https://jugaadpress.com/oauth2callback
     https://jugaadpress.vercel.app/oauth2callback
     ```

### 8.2 Submit App for Verification

For public release (not in "Testing" mode):

1. Go to **OAuth consent screen**
2. Click **"Publish App"**
3. Submit for verification (required if asking for sensitive scopes)
4. Google reviews in 3-5 business days

---

## Security Best Practices

### ✅ Do's

- ✅ Use `drive.file` scope (most restrictive)
- ✅ Store tokens securely (encrypted at rest)
- ✅ Never commit `client_secret.json` to Git
- ✅ Use HTTPS in production
- ✅ Implement token refresh logic
- ✅ Handle expired tokens gracefully

### ❌ Don'ts

- ❌ Don't use `drive` scope (too broad, asks for full Drive access)
- ❌ Don't store tokens in plaintext database
- ❌ Don't expose client secret in frontend
- ❌ Don't skip OAuth consent screen
- ❌ Don't hardcode credentials

---

## Troubleshooting

### "Access blocked: This app's request is invalid"

**Cause:** Redirect URI mismatch

**Fix:** Ensure the redirect URI in your OAuth client matches exactly (including http/https, port, path)

---

### "The app is in testing mode"

**Cause:** App not published or you're not a test user

**Fix:**
- Add yourself as test user in OAuth consent screen
- OR publish the app (for public release)

---

### "Token has been expired or revoked"

**Cause:** OAuth token expired

**Fix:**
- Delete `token.json`
- Re-authenticate (will generate new token)
- Implement automatic token refresh

---

### "Invalid grant: account not found"

**Cause:** Signed in with different Google account

**Fix:** Sign in with the account that has Drive permissions

---

## Next Steps

1. ✅ Complete setup above
2. ✅ Test locally
3. 🚧 Implement automatic token refresh
4. 🚧 Add offline sync support
5. 🚧 Deploy to Vercel
6. 🚧 Submit for Google verification
7. 🚧 Public launch

---

## Useful Links

- [Google Drive API Docs](https://developers.google.com/drive/api/v3/about-sdk)
- [OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
- [Drive API Python Quickstart](https://developers.google.com/drive/api/quickstart/python)
- [OAuth Scopes Reference](https://developers.google.com/identity/protocols/oauth2/scopes#drive)

---

**Need help?** Open an issue on GitHub with your error message and I'll help debug!

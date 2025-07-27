# Google OAuth Setup Guide

## The AccessDeniedError Issue

The `AccessDeniedError` you're encountering typically happens when:

1. **User denies the OAuth request** - The user clicked "Cancel" or "Deny" during the Google OAuth flow
2. **Missing or incorrect credentials** - The `credentials.json` file is missing or incorrect
3. **OAuth configuration issues** - The Google Cloud Console project isn't set up correctly

## How to Fix This

### Step 1: Set Up Google Cloud Console Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click on it and press "Enable"

### Step 2: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Web application" as the application type
4. Add these Authorized redirect URIs:
   - `http://localhost:5050/google/callback` (for development)
   - `https://yourdomain.com/google/callback` (for production)
5. Click "Create"
6. Download the JSON file and rename it to `credentials.json`

### Step 3: Place Credentials File

Put the `credentials.json` file in your project root directory (same level as `app.py`).

### Step 4: Test the OAuth Flow

1. Run the development server:
   ```bash
   python run_dev.py
   ```

2. Go to your calendar page and try the Google OAuth again

## Common Issues and Solutions

### Issue: "Google OAuth credentials file not found"
**Solution**: Make sure `credentials.json` is in the project root directory.

### Issue: "access_denied" error
**Solutions**:
1. Make sure you're clicking "Allow" when Google asks for permissions
2. Check that your redirect URI matches exactly in Google Cloud Console
3. Ensure the Google Calendar API is enabled

### Issue: "redirect_uri_mismatch"
**Solution**: Update the redirect URI in Google Cloud Console to match your application URL exactly.

## File Structure After Setup

```
student_study_planner/
├── app.py
├── credentials.json          # ← Add this file
├── run_dev.py
├── __init__.py
├── models.py
├── config.py
├── utils.py
├── routes/
│   ├── auth.py
│   ├── main.py
│   └── calendar.py
└── templates/
```

## Testing the OAuth Flow

1. Start the server: `python run_dev.py`
2. Go to `http://localhost:5050/calendar`
3. Click "Sync with Google Calendar"
4. You should be redirected to Google's OAuth page
5. Click "Allow" to grant permissions
6. You should be redirected back and see a success message

## Troubleshooting

If you're still getting errors:

1. **Check the browser console** for any JavaScript errors
2. **Check the Flask logs** for detailed error messages
3. **Verify your credentials.json** has the correct format
4. **Make sure you're using the development server** (`run_dev.py`) for local testing

The improved error handling in the updated code will now provide more specific error messages to help you debug any issues. 
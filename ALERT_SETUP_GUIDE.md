# Alert System Setup Guide

This guide will help you configure the email alert system to send notifications when spreadsheets are uploaded to Supabase.

## Quick Overview

**Current Status**: ✅ Code is ready, but requires two configurations:
1. **Email backend** - Choose between console (testing) or SMTP (production)
2. **Supabase webhook** - Configure Supabase to notify your app of file uploads

---

## Step 1: Configure Email Backend

You have two options:

### Option A: Console Backend (Testing Only)
**Current default** - No configuration needed. Emails print to terminal where Django runs.

✅ **Pros**: No setup required, good for testing  
❌ **Cons**: Users don't receive actual emails

**To use**: Leave your `.env` file without `EMAIL_HOST` setting.

### Option B: SMTP Backend (Production)
Send real emails to users. Choose a provider:

#### Using Gmail (Easiest for Testing)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password

3. **Add to `.env` file**:
   ```env
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-16-char-app-password
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   ```

4. **Restart Django server**

#### Using SendGrid (Recommended for Production)

1. **Sign up** at https://sendgrid.com (Free: 100 emails/day)
2. **Create API Key**: Settings → API Keys → Create API Key
3. **Add to `.env` file**:
   ```env
   EMAIL_HOST=smtp.sendgrid.net
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=apikey
   EMAIL_HOST_PASSWORD=your-sendgrid-api-key
   DEFAULT_FROM_EMAIL=noreply@yourdomain.com
   ```

4. **Restart Django server**

---

## Step 2: Configure Supabase Webhook

**This is REQUIRED** - Without this, your Django app won't know when files are uploaded.

### For Local Testing with ngrok

If you want to test locally before deploying:

1. **Install ngrok**: https://ngrok.com/download

2. **Start your Django server**:
   ```bash
   python manage.py runserver 8001
   ```

3. **In a new terminal, start ngrok**:
   ```bash
   ngrok http 8001
   ```

4. **Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

5. **Configure Supabase webhook** (see below) using:
   ```
   https://abc123.ngrok.io/webhooks/storage/
   ```

### Supabase Dashboard Configuration

1. **Log into Supabase**: https://supabase.com/dashboard

2. **Select your project**

3. **Navigate to Database → Webhooks** (or **Database → Functions & Triggers → Webhooks**)

4. **Create new webhook** with these settings:
   - **Name**: `file-upload-alert`
   - **Table**: `storage.objects`
   - **Events**: Check ✅ **INSERT**
   - **Type**: HTTP Request
   - **Method**: `POST`
   - **URL**: 
     - Local testing: `https://your-ngrok-url/webhooks/storage/`
     - Production: `https://yourdomain.com/webhooks/storage/`
   - **HTTP Headers**: `Content-Type: application/json`

5. **Save the webhook**

6. **Test it**: Upload a file to your Supabase bucket

### For Production Deployment

When deploying to production (Heroku, Railway, DigitalOcean, etc.):

1. Deploy your Django app
2. Get your production URL (e.g., `https://myapp.herokuapp.com`)
3. Update Supabase webhook URL to: `https://myapp.herokuapp.com/webhooks/storage/`

---

## Step 3: Testing the Alert System

### Test 1: Verify Alert Saving

1. **Start Django server**:
   ```bash
   python manage.py runserver 8001
   ```

2. **Login to your app**: http://localhost:8001/

3. **Navigate to Alerts page**: http://localhost:8001/alerts/

4. **Select some counties** (e.g., Fulton, DeKalb, Gwinnett)

5. **Click "Save Alerts"**

6. **Verify in Supabase**:
   - Go to Supabase Dashboard → Table Editor → `alerts` table
   - Should see your selected counties with your `user_id`

### Test 2: Test Webhook Locally (Without Supabase)

Use the provided test script to simulate a webhook:

```bash
python test_webhook_trigger.py
```

**What to look for**:
- Terminal should show: `New file uploaded: Fulton-County-Auction-2024-12-08.csv`
- Terminal should show: `Matched counties: ['Fulton']`
- Terminal should show: `Sending alert to user@example.com`
- If using console backend: Full email text prints to terminal
- If using SMTP backend: Check your email inbox

**Edit the test script** to test different county names:
```python
"name": "YourCounty-Test-File.csv",  # Change this line
```

### Test 3: End-to-End Test

**Requirements**: Supabase webhook configured + Email backend configured

1. **Save alerts** for a specific county (e.g., "Fulton")

2. **Upload a file to Supabase** with that county in the filename:
   - Go to Supabase Dashboard → Storage → your bucket
   - Upload file named: `Fulton-County-Auction-2024-12-08.csv`

3. **Check your Django server logs**:
   - Should see: `New file uploaded: Fulton-County-Auction-2024-12-08.csv`
   - Should see: `Sending alert to...`

4. **Check email**:
   - Console backend: Check terminal output
   - SMTP backend: Check inbox of user who saved the alert

---

## Troubleshooting

### Emails not being sent

**Check 1**: Is email backend configured correctly?
```bash
# In Django shell:
python manage.py shell
>>> from django.conf import settings
>>> print(settings.EMAIL_BACKEND)
>>> print(settings.EMAIL_HOST)
```

**Check 2**: Test email sending manually:
```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

**Check 3**: Check Django server logs for errors

### Webhook not triggering

**Check 1**: Is webhook configured in Supabase?
- Go to Dashboard → Database → Webhooks
- Verify URL is correct
- Verify INSERT event is checked

**Check 2**: Is webhook URL accessible?
- For ngrok: Make sure ngrok is still running
- For production: Make sure app is deployed and accessible

**Check 3**: Check Supabase webhook logs
- Supabase Dashboard → Database → Webhooks → Your webhook → Logs

**Check 4**: Test webhook manually:
```bash
python test_webhook_trigger.py
```

### Alerts not saving

**Check 1**: Check browser console for JavaScript errors

**Check 2**: Check Django server logs when clicking "Save Alerts"

**Check 3**: Verify Supabase connection:
```bash
python test_supabase_connection.py
```

---

## How It Works

1. **User saves alerts** → Keywords stored in Supabase `alerts` table
2. **File uploaded to Supabase** → Supabase webhook fires
3. **Django receives webhook** → `storage_webhook()` function called
4. **Filename checked for counties** → Matches against Georgia counties list
5. **Find subscribed users** → Query `alerts` table for matching keywords
6. **Send emails** → `send_mail()` to each subscribed user

---

## Security Notes

- **Never commit `.env` file** to git (already in `.gitignore`)
- **Use App Passwords** for Gmail, not your main password
- **Rotate API keys** periodically
- **Use HTTPS** for webhook URLs in production
- **Validate webhook payload** (already implemented in code)

---

## Next Steps

1. Choose email backend (console or SMTP)
2. If SMTP: Add credentials to `.env` and restart server
3. Configure Supabase webhook (required for production)
4. Test with `test_webhook_trigger.py`
5. Upload a real file to Supabase to test end-to-end

**Questions?** Review the implementation plan for more details.

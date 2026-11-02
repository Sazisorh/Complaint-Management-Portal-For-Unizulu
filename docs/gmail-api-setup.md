# Gmail API setup

Use the Gmail API to send from a Gmail account over HTTPS. This works on
Railway plans that block outbound SMTP. The app requests only Gmail's
`gmail.send` OAuth scope.

## Create Google OAuth credentials

1. In [Google Cloud Console](https://console.cloud.google.com/), select or
   create a project and enable the **Gmail API**.
2. Configure the Google Auth Platform consent screen. Add the Gmail sender as a
   test user while the app is in testing mode.
3. Create an OAuth client with application type **Desktop app**. Open the
   created client and copy both its client ID and client secret.
4. Put the client ID, client secret, and sending address in the ignored local
   `.env` file:

   ```env
   GMAIL_OAUTH_CLIENT_ID=your-desktop-client-id
   GMAIL_OAUTH_CLIENT_SECRET=your-desktop-client-secret
   EMAIL_USERNAME=your-sender@gmail.com
   EMAIL_FROM=your-sender@gmail.com
   ```

5. Run the OAuth setup script from the project root:

   ```powershell
   .\.venv\Scripts\python.exe scripts\setup_gmail_api.py
   ```

   Sign in to the Gmail account used for `EMAIL_USERNAME` and grant send
   permission. The script uses a loopback callback with PKCE and writes
   `GMAIL_OAUTH_REFRESH_TOKEN` to `.env` without displaying it. It also sets
   `EMAIL_PROVIDER=gmail_api`.
6. To deploy, add these variables to the web service's secret/environment
   manager:

   ```text
   EMAIL_PROVIDER=gmail_api
   EMAIL_USERNAME=your-sender@gmail.com
   EMAIL_FROM=your-sender@gmail.com
   GMAIL_OAUTH_CLIENT_ID=<Desktop OAuth client ID>
   GMAIL_OAUTH_CLIENT_SECRET=<Desktop OAuth client secret>
   GMAIL_OAUTH_REFRESH_TOKEN=<refresh token from local .env>
   ```

   Keep the client secret and refresh token private. Do not commit `.env` or
   send either value in chat.
7. Restart the app and check `/email_status` reports
   `"configured": true` and `"auth_method": "oauth2"`. Then send a one-time
   test notification. The status route confirms configuration only; the test
   message confirms delivery.

## OAuth consent-screen status

An external OAuth app left in **Testing** issues refresh tokens that expire
after seven days for this Gmail scope. For continuous production sending, move
the app to **In production** and complete any Google verification required
for the sensitive Gmail scope. Google may show an unverified-app warning until
verification is complete.

## SMTP alternative

On a host that permits outbound SMTP, Gmail SMTP can still be configured with
an app password instead of the API:

```env
EMAIL_PROVIDER=smtp
EMAIL_AUTH_METHOD=password
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_USE_SSL=false
EMAIL_USERNAME=your-sender@gmail.com
EMAIL_PASSWORD=your-google-app-password
EMAIL_FROM=your-sender@gmail.com
```

Railway Trial, Free, and Hobby plans block outbound SMTP; use Gmail API or an
HTTPS provider on those plans. See [Railway deployment](./railway-deployment.md)
for deployment details.

## User notification addresses

New accounts must provide an email address at registration. Administrators can
add an email address to existing accounts from the user-management table. The
app stores addresses with user records in its configured user-state store and
uses those saved addresses for grievance confirmations and status updates.

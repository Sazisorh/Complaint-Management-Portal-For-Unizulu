"""Run Google OAuth consent and save Gmail API credentials to the local .env file."""

import base64
import hashlib
import json
import os
import secrets
import sys
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / '.env'
SCOPE = 'https://www.googleapis.com/auth/gmail.send'
TIMEOUT_SECONDS = 15
AUTH_TIMEOUT_SECONDS = 300


def read_env_file():
    values = {}
    if not ENV_FILE.exists():
        return values

    with ENV_FILE.open('r', encoding='utf-8') as env_file:
        for line in env_file:
            stripped = line.strip()
            if not stripped or stripped.startswith('#') or '=' not in stripped:
                continue
            key, value = stripped.split('=', 1)
            values[key.strip()] = value.strip().strip('"\'')
    return values


def update_env_file(values):
    existing_lines = []
    if ENV_FILE.exists():
        with ENV_FILE.open('r', encoding='utf-8', newline='') as env_file:
            existing_lines = env_file.readlines()

    updated_keys = set()
    updated_lines = []
    for line in existing_lines:
        stripped = line.lstrip()
        key = stripped.split('=', 1)[0].strip() if '=' in stripped and not stripped.startswith('#') else None
        if key in values:
            updated_lines.append(f'{key}={values[key]}\n')
            updated_keys.add(key)
        else:
            updated_lines.append(line)

    for key, value in values.items():
        if key not in updated_keys:
            updated_lines.append(f'{key}={value}\n')

    with ENV_FILE.open('w', encoding='utf-8', newline='') as env_file:
        env_file.writelines(updated_lines)


def create_callback_handler(expected_state, result):
    class OAuthCallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            query = parse_qs(urlsplit(self.path).query)
            state = query.get('state', [None])[0]
            if urlsplit(self.path).path != '/oauth2callback' or state != expected_state:
                self.send_error(400, 'Invalid OAuth response.')
                return

            result['error'] = query.get('error', [None])[0]
            result['code'] = query.get('code', [None])[0]
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(
                b'Gmail authorization received. You can close this browser tab.'
            )

        def log_message(self, _format, *_args):
            del _format, _args

    return OAuthCallbackHandler


def authorize_gmail(client_id, client_secret):
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('ascii')).digest()
    ).decode('ascii').rstrip('=')
    state = secrets.token_urlsafe(32)
    result = {}

    callback_server = HTTPServer(
        ('127.0.0.1', 0),
        create_callback_handler(state, result),
    )
    callback_server.timeout = 1
    redirect_uri = f'http://127.0.0.1:{callback_server.server_port}/oauth2callback'
    authorization_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urlencode({
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': SCOPE,
        'access_type': 'offline',
        'prompt': 'consent',
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256',
        'state': state,
    })

    print('A browser will open. Sign in as the Gmail sender and grant send access.')
    if not webbrowser.open(authorization_url):
        print(f'Open this URL to authorize Gmail: {authorization_url}')

    expires_at = time.monotonic() + AUTH_TIMEOUT_SECONDS
    try:
        while not result and time.monotonic() < expires_at:
            callback_server.handle_request()
    finally:
        callback_server.server_close()

    if not result:
        raise RuntimeError('Gmail authorization timed out.')
    if result.get('error'):
        raise RuntimeError('Gmail authorization was not completed.')
    if not result.get('code'):
        raise RuntimeError('Google did not return an authorization code.')

    token_request = Request(
        'https://oauth2.googleapis.com/token',
        data=urlencode({
            'client_id': client_id,
            'client_secret': client_secret,
            'code': result['code'],
            'code_verifier': code_verifier,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
        }).encode('ascii'),
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        method='POST',
    )
    try:
        with urlopen(token_request, timeout=TIMEOUT_SECONDS) as response:
            token_data = json.loads(response.read().decode('utf-8'))
    except HTTPError as error:
        try:
            error_data = json.loads(error.read().decode('utf-8'))
        except (UnicodeDecodeError, ValueError):
            error_data = {}
        error_code = error_data.get('error') if isinstance(error_data, dict) else None
        error_description = (
            error_data.get('error_description')
            if isinstance(error_data, dict)
            else None
        )
        details = ', '.join(
            value for value in (error_code, error_description)
            if isinstance(value, str) and value
        )
        raise RuntimeError(
            f'Google token exchange failed (HTTP {error.code})'
            f'{f": {details}" if details else "."}'
        ) from error
    except (URLError, OSError, ValueError) as error:
        raise RuntimeError('Could not complete the Google token exchange.') from error

    refresh_token = token_data.get('refresh_token') if isinstance(token_data, dict) else None
    if not isinstance(refresh_token, str) or not refresh_token:
        raise RuntimeError(
            'Google did not issue a refresh token. Revoke the existing app grant '
            'and rerun setup with consent enabled.'
        )
    return refresh_token


def main():
    settings = read_env_file()
    client_id = os.getenv('GMAIL_OAUTH_CLIENT_ID') or settings.get('GMAIL_OAUTH_CLIENT_ID')
    client_secret = (
        os.getenv('GMAIL_OAUTH_CLIENT_SECRET')
        or settings.get('GMAIL_OAUTH_CLIENT_SECRET')
    )
    if not client_id:
        print(
            'Set GMAIL_OAUTH_CLIENT_ID in .env after enabling the Gmail API and '
            'creating a Google Desktop OAuth client.'
        )
        return 1
    if not client_secret:
        print(
            'Set GMAIL_OAUTH_CLIENT_SECRET in .env using the client secret '
            'from the same Google Desktop OAuth client.'
        )
        return 1

    try:
        refresh_token = authorize_gmail(client_id, client_secret)
        update_env_file({
            'EMAIL_PROVIDER': 'gmail_api',
            'GMAIL_OAUTH_REFRESH_TOKEN': refresh_token,
        })
    except (HTTPError, URLError, OSError, RuntimeError, ValueError) as error:
        print(f'Gmail API setup failed: {error}')
        return 1

    print('Gmail API is configured in the local .env file. The refresh token was not displayed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

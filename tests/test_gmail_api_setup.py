"""Verify Gmail OAuth setup, PKCE handling, and safe .env updates."""

import base64
import hashlib
import importlib.util
import threading
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import urlopen


SCRIPT_PATH = Path(__file__).resolve().parents[1] / 'scripts' / 'setup_gmail_api.py'
SPEC = importlib.util.spec_from_file_location('setup_gmail_api', SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError('Could not load Gmail API setup script for tests.')
gmail_setup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gmail_setup)


def test_gmail_setup_uses_pkce_and_saves_google_refresh_token(monkeypatch):
    captured = {}
    callback_errors = []

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            del args
            return None

        def read(self):
            return b'{"refresh_token":"test-refresh-token"}'

    def fake_urlopen(request, timeout):
        captured['token_request'] = request
        captured['timeout'] = timeout
        return FakeResponse()

    def fake_browser_open(authorization_url):
        authorization = parse_qs(urlsplit(authorization_url).query)
        captured['authorization'] = authorization

        def approve_authorization():
            redirect = authorization['redirect_uri'][0]
            callback_url = redirect + '?' + urlencode({
                'code': 'test-authorization-code',
                'state': authorization['state'][0],
            })
            try:
                with urlopen(callback_url, timeout=5) as response:
                    captured['callback_status'] = response.status
            except Exception as error:
                callback_errors.append(error)

        callback_thread = threading.Thread(target=approve_authorization, daemon=True)
        callback_thread.start()
        captured['callback_thread'] = callback_thread
        return True

    monkeypatch.setattr(gmail_setup, 'urlopen', fake_urlopen)
    monkeypatch.setattr(gmail_setup.webbrowser, 'open', fake_browser_open)

    assert gmail_setup.authorize_gmail('test-client-id', 'test-client-secret') == 'test-refresh-token'
    captured['callback_thread'].join(timeout=5)

    authorization = captured['authorization']
    form = parse_qs(captured['token_request'].data.decode('ascii'))
    verifier = form['code_verifier'][0]
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode('ascii')).digest()
    ).decode('ascii').rstrip('=')
    assert not callback_errors
    assert captured['callback_status'] == 200
    assert authorization['client_id'] == ['test-client-id']
    assert authorization['scope'] == [gmail_setup.SCOPE]
    assert authorization['access_type'] == ['offline']
    assert authorization['code_challenge_method'] == ['S256']
    assert authorization['code_challenge'] == [challenge]
    assert form['client_id'] == ['test-client-id']
    assert form['client_secret'] == ['test-client-secret']
    assert form['code'] == ['test-authorization-code']
    assert form['grant_type'] == ['authorization_code']
    assert form['redirect_uri'] == authorization['redirect_uri']
    assert captured['token_request'].full_url == 'https://oauth2.googleapis.com/token'
    assert captured['timeout'] == gmail_setup.TIMEOUT_SECONDS


def test_gmail_setup_updates_env_keys_without_replacing_other_settings(tmp_path, monkeypatch):
    env_file = tmp_path / '.env'
    env_file.write_text(
        'EMAIL_HOST=smtp.gmail.com\nGMAIL_OAUTH_REFRESH_TOKEN=old-token\n# keep me\n',
        encoding='utf-8',
    )
    monkeypatch.setattr(gmail_setup, 'ENV_FILE', env_file)

    gmail_setup.update_env_file({
        'EMAIL_PROVIDER': 'gmail_api',
        'GMAIL_OAUTH_REFRESH_TOKEN': 'new-token',
    })

    content = env_file.read_text(encoding='utf-8')
    assert 'EMAIL_HOST=smtp.gmail.com\n' in content
    assert 'GMAIL_OAUTH_REFRESH_TOKEN=new-token\n' in content
    assert 'EMAIL_PROVIDER=gmail_api\n' in content
    assert '# keep me\n' in content
    assert 'old-token' not in content

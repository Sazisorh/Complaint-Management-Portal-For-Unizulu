from getpass import getpass
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import app as portal


def main():
    portal.load_mysql_state_before_request()

    username = input('Administrator username: ').strip()
    full_name = input('Administrator full name: ').strip()
    email = input('Administrator email: ').strip()
    password = getpass('Administrator password (minimum 12 characters): ')
    confirmation = getpass('Confirm password: ')

    if not username or not full_name:
        print('Username and full name are required.')
        return 1
    if not portal.is_valid_email_address(email):
        print('Enter a valid administrator email address.')
        return 1
    if username in portal.users_db:
        print('That username already exists.')
        return 1
    if len(password) < 12:
        print('The administrator password must be at least 12 characters.')
        return 1
    if password != confirmation:
        print('The passwords do not match.')
        return 1

    portal.users_db[username] = {
        'password': portal.hash_password(password),
        'full_name': full_name,
        'role': 'admin',
        'email': email,
    }
    portal.persist_state()
    print('Administrator account created.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

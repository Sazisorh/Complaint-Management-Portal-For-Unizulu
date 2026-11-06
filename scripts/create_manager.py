"""Interactively create a management account in the portal state."""

from getpass import getpass
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import app as portal


def main():
    portal.load_mysql_state_before_request()

    username = input('Management username: ').strip()
    if not portal.is_valid_username_for_role(username, 'manager'):
        print('Management username must be exactly 9 digits and start with 40.')
        return 1

    full_name = input('Management full name: ').strip()
    email = input('Management email: ').strip()
    password = getpass('Management password (minimum 12 characters): ')
    confirmation = getpass('Confirm password: ')

    if not full_name:
        print('Management full name is required.')
        return 1
    if not portal.is_valid_email_address(email):
        print('Enter a valid management email address.')
        return 1
    if username in portal.users_db:
        print('That username already exists.')
        return 1
    if len(password) < 12:
        print('The management password must be at least 12 characters.')
        return 1
    if password != confirmation:
        print('The passwords do not match.')
        return 1

    portal.users_db[username] = {
        'password': portal.hash_password(password),
        'full_name': full_name,
        'role': 'manager',
        'email': email,
    }
    portal.persist_state()
    print('Management account created.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

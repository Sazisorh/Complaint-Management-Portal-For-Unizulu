from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import app as portal


def main():
    connection = portal.get_database_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS users ('
            'id INT AUTO_INCREMENT PRIMARY KEY, '
            'username VARCHAR(100) NOT NULL UNIQUE, '
            'full_name VARCHAR(255) NOT NULL, '
            'email VARCHAR(150) NOT NULL, '
            'password VARCHAR(255) NOT NULL, '
            "role ENUM('student', 'staff', 'admin') NOT NULL, "
            "department VARCHAR(100) NOT NULL DEFAULT 'Academic Affairs', "
            'password_reset_token_version VARCHAR(64) NULL, '
            'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            ')'
        )
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS complaints ('
            'id INT PRIMARY KEY, '
            'student_id INT NULL, '
            'username VARCHAR(100) NULL, '
            'full_name VARCHAR(255) NOT NULL, '
            'title VARCHAR(255) NOT NULL, '
            'description TEXT NOT NULL, '
            "assigned_category VARCHAR(100) DEFAULT 'Unassigned', "
            "department VARCHAR(100) NOT NULL DEFAULT 'Academic Affairs', "
            "status VARCHAR(50) NOT NULL DEFAULT 'Pending', "
            'created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, '
            'reference_number VARCHAR(64) NULL UNIQUE, '
            'is_anonymous BOOLEAN NOT NULL DEFAULT FALSE, '
            'evidence_path VARCHAR(500) NULL, '
            'CONSTRAINT grievance_portal_complaints_student_fk '
            'FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE SET NULL'
            ')'
        )

        user_columns = {
            row[0] for row in _fetch_column_names(cursor, 'users')
        }
        for column, definition in {
            'full_name': "VARCHAR(255) NOT NULL DEFAULT ''",
            'department': "VARCHAR(100) NOT NULL DEFAULT 'Academic Affairs'",
            'password_reset_token_version': 'VARCHAR(64) NULL',
        }.items():
            if column not in user_columns:
                cursor.execute(f'ALTER TABLE users ADD COLUMN {column} {definition}')

        cursor.execute(
            'SELECT INDEX_NAME FROM information_schema.STATISTICS '
            'WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND NON_UNIQUE = 0 '
            'GROUP BY INDEX_NAME HAVING COUNT(*) = 1 AND MAX(COLUMN_NAME) = %s',
            ('users', 'email'),
        )
        for row in cursor.fetchall():
            index_name = row[0].replace('`', '``')
            cursor.execute(f'ALTER TABLE users DROP INDEX `{index_name}`')

        complaint_columns = {
            row[0] for row in _fetch_column_names(cursor, 'complaints')
        }
        for column, definition in {
            'username': 'VARCHAR(100) NULL',
            'full_name': "VARCHAR(255) NOT NULL DEFAULT ''",
            'department': "VARCHAR(100) NOT NULL DEFAULT 'Academic Affairs'",
            'reference_number': 'VARCHAR(64) NULL',
            'is_anonymous': 'BOOLEAN NOT NULL DEFAULT FALSE',
            'evidence_path': 'VARCHAR(500) NULL',
        }.items():
            if column not in complaint_columns:
                cursor.execute(f'ALTER TABLE complaints ADD COLUMN {column} {definition}')

        cursor.execute(
            'SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE '
            'WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s '
            'AND REFERENCED_TABLE_NAME IS NOT NULL',
            ('complaints', 'student_id'),
        )
        for row in cursor.fetchall():
            constraint_name = row[0].replace('`', '``')
            cursor.execute(f'ALTER TABLE complaints DROP FOREIGN KEY `{constraint_name}`')
        cursor.execute('ALTER TABLE complaints MODIFY student_id INT NULL')
        cursor.execute(
            "ALTER TABLE complaints MODIFY status VARCHAR(50) NOT NULL DEFAULT 'Pending'"
        )
        cursor.execute(
            'ALTER TABLE complaints ADD CONSTRAINT grievance_portal_complaints_student_fk '
            'FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE SET NULL'
        )

        cursor.execute(
            'SELECT COUNT(*) FROM information_schema.STATISTICS '
            'WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s AND NON_UNIQUE = 0',
            ('complaints', 'reference_number'),
        )
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                'ALTER TABLE complaints ADD UNIQUE KEY grievance_portal_reference_number_uq (reference_number)'
            )

        cursor.execute(
            'CREATE TABLE IF NOT EXISTS evidence_files ('
            'id INT AUTO_INCREMENT PRIMARY KEY, '
            'complaint_id INT NULL, '
            'original_filename VARCHAR(255) NOT NULL, '
            'stored_filename VARCHAR(255) NOT NULL UNIQUE, '
            'stored_path VARCHAR(500) NOT NULL, '
            'mime_type VARCHAR(127) NOT NULL, '
            'size_bytes BIGINT UNSIGNED NOT NULL, '
            'file_data LONGBLOB NOT NULL, '
            'uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            ')'
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()

    print('Portal user, complaint, and evidence tables are ready.')
    return 0


def _fetch_column_names(cursor, table_name):
    cursor.execute(f'SHOW COLUMNS FROM {table_name}')
    return cursor.fetchall()


if __name__ == '__main__':
    sys.exit(main())

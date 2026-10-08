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

    print('Evidence storage table is ready.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

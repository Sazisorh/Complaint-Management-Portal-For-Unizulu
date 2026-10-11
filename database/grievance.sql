CREATE DATABASE IF NOT EXISTS grievance_db;
USE grievance_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(150) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('student', 'staff', 'admin') NOT NULL,
    department VARCHAR(100) NOT NULL DEFAULT 'Academic Affairs',
    password_reset_token_version VARCHAR(64) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS complaints (
    id INT PRIMARY KEY,
    student_id INT NULL,
    username VARCHAR(100) NULL,
    full_name VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    assigned_category VARCHAR(100) DEFAULT 'Unassigned',
    department VARCHAR(100) NOT NULL DEFAULT 'Academic Affairs',
    status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reference_number VARCHAR(64) NULL UNIQUE,
    is_anonymous BOOLEAN NOT NULL DEFAULT FALSE,
    evidence_path VARCHAR(500) NULL,
    CONSTRAINT grievance_portal_complaints_student_fk
        FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS evidence_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id INT NULL,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL UNIQUE,
    stored_path VARCHAR(500) NOT NULL,
    mime_type VARCHAR(127) NOT NULL,
    size_bytes BIGINT UNSIGNED NOT NULL,
    file_data LONGBLOB NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

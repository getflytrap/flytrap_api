DROP TABLE IF EXISTS error_logs;
DROP TABLE IF EXISTS rejection_logs;
DROP TABLE IF EXISTS projects_users;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS users;

CREATE TABLE projects (
  id SERIAL PRIMARY KEY,
  pid VARCHAR(36) NOT NULL,
  name VARCHAR(255) NOT NULL
);

CREATE TABLE error_logs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    line_number INT,
    col_number INT,
    project_id INT REFERENCES projects(id) ON DELETE CASCADE,
    stack_trace TEXT,
    handled BOOLEAN NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE rejection_logs (
  id SERIAL PRIMARY KEY,
  value TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  project_id INT REFERENCES projects(id) ON DELETE CASCADE,
  handled BOOLEAN NOT NULL,
  resolved BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_root BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE projects_users (
  id SERIAL PRIMARY KEY,
  project_id INT REFERENCES projects(id) ON DELETE CASCADE,
  user_id INT REFERENCES users(id) ON DELETE CASCADE
);
DROP TABLE IF EXISTS error_logs;
DROP TABLE IF EXISTS rejection_logs;
DROP TABLE IF EXISTS projects_users;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS users;

CREATE TABLE projects (
  id SERIAL PRIMARY KEY,
  uuid VARCHAR(36) NOT NULL UNIQUE,
  name VARCHAR(255) NOT NULL,
  api_key VARCHAR(36) NOT NULL UNIQUE,
  platform VARCHAR(255) NOT NULL,
  sns_topic_arn VARCHAR(255) NOT NULL
);

CREATE INDEX idx_project_uuid ON projects(uuid);

CREATE TABLE error_logs (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    filename VARCHAR(255),
    line_number INT,
    col_number INT,
    project_id INT REFERENCES projects(id) ON DELETE CASCADE,
    stack_trace TEXT,
    handled BOOLEAN NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    contexts JSONB,
    method VARCHAR(10),
    path TEXT,
    ip VARCHAR(45),
    os VARCHAR(255),
    browser VARCHAR(255),
    runtime VARCHAR(255),
    error_hash VARCHAR(64)
);

CREATE INDEX idx_error_log_uuid ON error_logs(uuid); 

CREATE TABLE rejection_logs (
  id SERIAL PRIMARY KEY,
  uuid VARCHAR(36) NOT NULL UNIQUE,
  value TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  project_id INT REFERENCES projects(id) ON DELETE CASCADE,
  handled BOOLEAN NOT NULL,
  resolved BOOLEAN NOT NULL DEFAULT FALSE,
  method VARCHAR(10),
  path TEXT,
  ip VARCHAR(45),
  os VARCHAR(255),
  browser VARCHAR(255),
  runtime VARCHAR(255)
);

CREATE INDEX idx_rejection_log_uuid ON rejection_logs(uuid);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_root BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_uuid ON users(uuid); 

CREATE TABLE projects_users (
  id SERIAL PRIMARY KEY,
  project_id INT REFERENCES projects(id) ON DELETE CASCADE,
  user_id INT REFERENCES users(id) ON DELETE CASCADE,
  sns_subscription_arn VARCHAR(255),
  UNIQUE (project_id, user_id)
);

INSERT INTO users (uuid, first_name, last_name, email, password_hash, is_root)
VALUES (
  'root-uuid-123-456-789',
  'Flytrap',
  'Admin',
  'admin@admin.com',
  '$2b$12$5voKL8Dzp9muUhSZ/bsPL.JkWaDja.jrvBFk2wMfmOn.ILBLBvksW',
  true
);
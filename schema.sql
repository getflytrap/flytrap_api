DROP TABLE IF EXISTS error_logs;

CREATE TABLE error_logs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    line_number INT,
    col_number INT,
    project_id INT,
    stack_trace TEXT,
    handled BOOLEAN NOT NULL,
);

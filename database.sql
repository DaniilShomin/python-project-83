CREATE TABLE IF NOT EXISTS urls (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(255) UNIQUE NOT NULL,
    created_at DATE
);

CREATE TABLE IF NOT EXISTS url_checks (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url_id BIGINT NOT NULL REFERENCES urls(id),
    status_code INT,
    h1 VARCHAR(255),
    title VARCHAR(255),
    description TEXT,
    created_at DATE DEFAULT CURRENT_DATE
);
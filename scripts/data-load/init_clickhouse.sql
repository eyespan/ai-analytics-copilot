CREATE DATABASE IF NOT EXISTS github;

CREATE TABLE github.github_events
(
    event_time DateTime,
    event_type String,
    repo_name String,
    repo_url String,
    actor_login String,
    action String,
    language String,
    description String,
    stars UInt32 DEFAULT 0,
    forks UInt32 DEFAULT 0
)
ENGINE = MergeTree
ORDER BY (event_time, repo_name);

CREATE DATABASE IF NOT EXISTS ai_memory;

CREATE TABLE IF NOT EXISTS ai_memory.ai_memory
(
    event_id String,
    session_id String,
    timestamp DateTime,
    query String,
    response String,
    metadata String
)
ENGINE = MergeTree()
ORDER BY (session_id, timestamp);
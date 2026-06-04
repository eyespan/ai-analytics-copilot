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
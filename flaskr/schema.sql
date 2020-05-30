DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS post;

CREATE TABLE users(
    users_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username text unique NOT NULL,
    password text not null
);

CREATE TABLE post(
    id INTEGER primary key AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL default current_timestamp,
    title text NOT NULL,
    body text NOT NULL,
    FOREIGN KEY(author_id) REFERENCES users(users_id)
)
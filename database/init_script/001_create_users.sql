CREATE TABLE users (
    user_id     INT         GENERATED ALWAYS AS IDENTITY,
    public_id   VARCHAR(36) UNIQUE NOT NULL,
    username    VARCHAR(50) NOT NULL,
    mail        VARCHAR(50) UNIQUE NOT NULL,
    password    VARCHAR(88) NOT NULL, 
    PRIMARY KEY(user_id)
);
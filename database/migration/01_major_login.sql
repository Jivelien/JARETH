CREATE TABLE users (
    user_id     INT         GENERATED ALWAYS AS IDENTITY,
    public_id   VARCHAR(36) UNIQUE NOT NULL,
    username    VARCHAR(50) NOT NULL,
    mail        VARCHAR(50) UNIQUE NOT NULL,
    password    VARCHAR(88) NOT NULL, 
    PRIMARY KEY(user_id)
);
CREATE TABLE smoked_cigarettes (
    cigarette_id     INT         GENERATED ALWAYS AS IDENTITY,
    public_user_id   VARCHAR(36) NOT NULL,
    event_time       TIMESTAMP   NOT NULL,
    PRIMARY KEY(cigarette_id),
    UNIQUE (public_user_id, event_time),
    CONSTRAINT fk_user_cigarette
      FOREIGN KEY(public_user_id) 
	  REFERENCES users(public_id)
);
-- MANUAL : create an user and copy the public_id
SELECT public_id FROM users;
-- MANUAL : replace in following line the public_id
INSERT INTO smoked_cigarettes (public_user_id, event_time) SELECT '<public_id>', eventtime from event;
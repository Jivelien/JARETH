CREATE TABLE smoked_cigarettes (
    cigarette_id     INT         GENERATED ALWAYS AS IDENTITY,
    user_id          INT         NOT NULL,
    event_time       TIMESTAMP   UNIQUE          NOT NULL,
    PRIMARY KEY(cigarette_id),
     CONSTRAINT fk_user_cigarette
      FOREIGN KEY(user_id) 
	  REFERENCES users(user_id)
);
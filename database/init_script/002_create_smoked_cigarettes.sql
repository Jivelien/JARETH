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
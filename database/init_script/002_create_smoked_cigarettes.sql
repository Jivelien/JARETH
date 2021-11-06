CREATE TABLE smoked_cigarettes (
    cigarette_id     INT         GENERATED ALWAYS AS IDENTITY,
    public_user_id        INT         NOT NULL,
    event_time       TIMESTAMP   UNIQUE          NOT NULL,
    PRIMARY KEY(cigarette_id),
     CONSTRAINT fk_user_cigarette
      FOREIGN KEY(public_user_id) 
	  REFERENCES users(public_id)
);
CREATE TABLE objectives (
    objective_id                            INT GENERATED ALWAYS AS IDENTITY,
    public_user_id                          VARCHAR(36) UNIQUE NOT NULL,
    cigarette_per_day                       INT,
    delay_between_cigarette_in_minutes      INT,
    PRIMARY KEY(objective_id),
    CONSTRAINT fk_user_objective
        FOREIGN KEY(public_user_id) 
        REFERENCES users(public_id)
);
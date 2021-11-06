CREATE TABLE objectives (
    objective_id                            INT   GENERATED ALWAYS AS IDENTITY,
    user_id                                 INT   NOT NULL,
    cigarette_per_day                       INT,
    delay_between_cigarette_in_minutes      INT,
    is_active                               BOOL,
    PRIMARY KEY(objective_id),
    CONSTRAINT fk_user_objective
        FOREIGN KEY(user_id) 
        REFERENCES users(user_id)
);
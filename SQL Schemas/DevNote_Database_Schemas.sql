-- CREATE THE USERS TABLE --
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username varchar(45),
    email varchar(45),
    password varchar(200),
    full_name varchar(45)
)
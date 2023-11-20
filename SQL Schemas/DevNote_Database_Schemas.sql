-- CREATE THE USERS TABLE --
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username varchar(45),
    email varchar(45),
    password varchar(200),
    full_name varchar(45)
)


-- INSERT TEST USER INTO THE USERS TABLE --
INSERT INTO users (username, email, password, full_name)
VALUES ('tim', 'artemijs.testingprojects@gmail.com', '$2b$12$Ubbk6INq0Hd2uRqY.wDqyOhWRVXuiLYstLeXpQGvS2Koa.aWPxeCu', 'Thomas Matusev');
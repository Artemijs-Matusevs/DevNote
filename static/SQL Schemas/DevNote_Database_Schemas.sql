-- CREATE THE USERS TABLE --
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username varchar(45),
    email varchar(45),
    password varchar(200),
    full_name varchar(45)
)
cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY,username varchar(45) unique,email varchar(45) unique,password varchar(200),full_name varchar(45))") 


-- CREATE THE NOTEBOOK TABLE --
CREATE TABLE notebooks (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    notebook_header TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)


-- CREATE THE PAGES TABLE --
CREATE TABLE pages (
    id INTEGER PRIMARY KEY,
    notebook_id INTEGER,
    page_header TEXT,
    page_content TEXT,
    FOREIGN KEY (notebook_id) REFERENCES notebooks(id)
)

-- SELECT ALL PAGES OF SPECIFIC NOTEBOOK --
SELECT *
FROM pages
WHERE notebook_id = 1;



-- SELECT ALL RECORDS FROM USERS TABLE --
SELECT *
FROM users; 

-- INSERT TEST USER INTO THE USERS TABLE --
INSERT INTO users (username, email, password, full_name)
VALUES ('tim', 'artemijs.testingprojects@gmail.com', '$2b$12$Ubbk6INq0Hd2uRqY.wDqyOhWRVXuiLYstLeXpQGvS2Koa.aWPxeCu', 'Thomas Matusev');
cursor.execute("INSERT INTO users (username, email, password, full_name) VALUES ('tim', 'artemijs.testingprojects@gmail.com', '$2b$12$Ubbk6INq0Hd2uRqY.wDqyOhWRVXuiLYstLeXpQGvS2Koa.aWPxeCu', 'Thomas Matusev');") 
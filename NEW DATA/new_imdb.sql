-- CREATE DATABASE imdb;
USE imdb;

DROP TABLE IF EXISTS title_rating;
DROP TABLE IF EXISTS title_cast;
DROP TABLE IF EXISTS title_episode;
DROP TABLE IF EXISTS title_akas;
DROP TABLE IF EXISTS title_crew;
DROP TABLE IF EXISTS name_basics;
DROP TABLE IF EXISTS title_basics;

-- PARENT TABLES --

CREATE TABLE title_basics (
    genre ENUM('scifi', 'comedy', 'romance', 'action', 'adventure', 'fantasy', 'horror', 'drama', 'romantic_comedy') NOT NULL,
    tconst INT PRIMARY KEY,
	CHECK (tconst > 999999),
    titleType ENUM('movie', 'tv_series', 'tv_episode') NOT NULL,
    title VARCHAR(255) NOT NULL,
    isAdult BOOLEAN NOT NULL,
    startYear INT NOT NULL,
    endYear INT DEFAULT NULL
);

CREATE TABLE name_basics (
    nconst INT PRIMARY KEY,
    CHECK (nconst > 9999),
    originalName VARCHAR(255) NOT NULL,
    birthYear INT NOT NULL,
    deathYear INT,
    knownName VARCHAR(255) NOT NULL,
    primaryProfession VARCHAR(255)
);



-- CHILD TABLES --

CREATE TABLE title_crew (
    tconst INT PRIMARY KEY,
    directorNconst INT NOT NULL,
    writerNconst INT NOT NULL,
    FOREIGN KEY (tconst) REFERENCES title_basics(tconst)
        ON UPDATE CASCADE 
        ON DELETE CASCADE,
    FOREIGN KEY (directorNconst) REFERENCES name_basics(nconst)
        ON UPDATE CASCADE 
        ON DELETE CASCADE,
    FOREIGN KEY (writerNconst) REFERENCES name_basics(nconst)
        ON UPDATE CASCADE 
        ON DELETE CASCADE
);

CREATE TABLE title_akas (
    tconst INT,
    ordering INT,
    title VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    isOriginal BOOLEAN NOT NULL,
    PRIMARY KEY (tconst, ordering),
    FOREIGN KEY (tconst) REFERENCES title_basics(tconst) 
        ON UPDATE CASCADE 
        ON DELETE CASCADE
);

CREATE TABLE title_episode (
    tconst INT NOT NULL,
    parentTconst INT NOT NULL,
    seasonNumber INT DEFAULT NULL,
    episodeNumber INT DEFAULT NULL,
    PRIMARY KEY (tconst),
    FOREIGN KEY (tconst) REFERENCES title_basics(tconst) 
        ON UPDATE CASCADE 
        ON DELETE CASCADE,
    FOREIGN KEY (parentTconst) REFERENCES title_basics(tconst) 
        ON UPDATE CASCADE 
        ON DELETE CASCADE
);

CREATE TABLE title_cast (
    tconst INT NOT NULL,
    ordering INT NOT NULL,
    nconst INT NOT NULL,
    category ENUM('main_character', 'side_character', 'guest') NOT NULL,
    characterName VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (tconst, ordering),
    FOREIGN KEY (tconst) REFERENCES title_basics(tconst)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (nconst) REFERENCES name_basics(nconst)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE title_rating (
    tconst INT PRIMARY KEY,
    averageRating FLOAT NOT NULL CHECK (averageRating >= 0.0 AND averageRating <= 5.0),
    numVotes INT NOT NULL,
    FOREIGN KEY (tconst) REFERENCES title_basics(tconst)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

LOAD DATA LOCAL INFILE '/Users/feyzanur/Desktop/Projects/BLG-317E-Project/Feyza/sql/name_basics.csv'
INTO TABLE name_basics
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'  
LINES TERMINATED BY '\n'     
IGNORE 1 LINES
(nconst, originalName, birthYear, deathYear, knownName, primaryProfession);

LOAD DATA LOCAL INFILE '/Users/feyzanur/Desktop/Projects/BLG-317E-Project/Feyza/sql/title_basics.csv'
INTO TABLE title_basics
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'  
LINES TERMINATED BY '\n'     
IGNORE 1 LINES
(genre, tconst, titleType, title, isAdult, startYear, endYear);

-- Loading data for title_crew
LOAD DATA LOCAL INFILE '/Users/feyzanur/Desktop/Projects/BLG-317E-Project/Feyza/sql/title_crew.csv'
INTO TABLE title_crew
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'  
LINES TERMINATED BY '\n'     
IGNORE 1 LINES
(tconst, directorNconst, writerNconst);

-- Loading data for title_akas
LOAD DATA LOCAL INFILE '/Users/feyzanur/Desktop/Projects/BLG-317E-Project/Feyza/sql/title_akas.csv'
INTO TABLE title_akas
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'  
LINES TERMINATED BY '\n'     
IGNORE 1 LINES
(tconst, ordering, title, country, isOriginal);

-- Loading data for title_episode
LOAD DATA LOCAL INFILE '/Users/feyzanur/Desktop/Projects/BLG-317E-Project/Feyza/sql/title_episode.csv'
INTO TABLE title_episode
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'  
LINES TERMINATED BY '\n'     
IGNORE 1 LINES
(tconst, parentTconst, seasonNumber, episodeNumber);

-- Loading data for title_cast
LOAD DATA LOCAL INFILE '/Users/feyzanur/Desktop/Projects/BLG-317E-Project/Feyza/sql/title_cast.csv'
INTO TABLE title_cast
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'  
LINES TERMINATED BY '\n'     
IGNORE 1 LINES
(tconst, ordering, nconst, category, characterName);

-- Loading data for title_rating
LOAD DATA LOCAL INFILE '/Users/feyzanur/Desktop/Projects/BLG-317E-Project/Feyza/sql/title_ratings.csv'
INTO TABLE title_rating
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'  
LINES TERMINATED BY '\n'     
IGNORE 1 LINES
(tconst, averageRating, numVotes);


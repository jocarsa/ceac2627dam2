CREATE USER IF NOT EXISTS 'jocarsa'@'localhost' IDENTIFIED BY 'jocarsa';
ALTER USER 'jocarsa'@'localhost' IDENTIFIED BY 'jocarsa';
GRANT SELECT, INSERT, UPDATE, DELETE ON jocarsa.* TO 'jocarsa'@'localhost';

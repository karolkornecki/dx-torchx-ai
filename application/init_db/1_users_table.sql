CREATE TABLE USERS
(
    ID         SERIAL             NOT NULL PRIMARY KEY,
    EMAIL      VARCHAR(50) UNIQUE NOT NULL,
    FIRST_NAME VARCHAR(50)        NOT NULL,
    LAST_NAME  VARCHAR(50)        NOT NULL,
    PASSWORD   VARCHAR(100)       NOT NULL
);

--- Przykładowy lekarz - użytkownik aplikacji # hasło "lekarz" - bcrypt 12 rounds
INSERT INTO USERS (EMAIL, FIRST_NAME, LAST_NAME, PASSWORD)
VALUES ('karol.kornecki@gmail.com',
        'Karol',
        'Kornecki',
        '$2a$12$CcKVtHLdLfI2fS1gNEl0geMPwAlyhrMkqiQORGSDKlmJWbHGoQ1Fu');
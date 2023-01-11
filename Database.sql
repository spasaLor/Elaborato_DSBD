DROP DATABASE test_DSBD;
CREATE DATABASE test_DSBD;
use test_DSBD;


CREATE TABLE metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    partizione VARCHAR(20),
    UNIQUE(nome,partizione)
);
CREATE TABLE decomposition (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    partizione VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    tipologia ENUM ('seasonal', 'trend') NOT NULL,
    value FLOAT NOT NULL,
    FOREIGN KEY (nome) REFERENCES metrics(nome)
);
CREATE TABLE hodrick_prescott (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    partizione VARCHAR(20),
    timestamp TIMESTAMP NOT NULL,
    value FLOAT NOT NULL,
    FOREIGN KEY (nome) REFERENCES metrics(nome)
);
CREATE TABLE dickey_fuller (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    partizione VARCHAR(20),
    test_statistic FLOAT NOT NULL,
    p_value FLOAT NOT NULL,
    is_stationary BOOLEAN NOT NULL,
    crit_value_1 FLOAT NOT NULL,
    crit_value_5 FLOAT NOT NULL,
    crit_value_10 FLOAT NOT NULL,
    FOREIGN KEY (nome) REFERENCES metrics(nome)
);
CREATE TABLE aggregates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    partizione VARCHAR(20) NOT NULL,
    intervallo ENUM ('1h','3h','12h','10m') NOT NULL,
    tipologia ENUM ('max', 'min', 'mean','std_dev') NOT NULL,
    value FLOAT,
    valore_predetto FLOAT,
    FOREIGN KEY (nome) REFERENCES metrics(nome)
);
CREATE TABLE autocorrelation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    partizione VARCHAR(20),
    value FLOAT NOT NULL,
    FOREIGN KEY (nome) REFERENCES metrics(nome)
);
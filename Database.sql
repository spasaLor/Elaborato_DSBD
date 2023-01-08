DROP DATABASE test_DSBD;
CREATE DATABASE test_DSBD;
use test_DSBD;


CREATE TABLE metrics (
    ID INTEGER AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(30) NOT NULL,
    partizione VARCHAR(30),
    dickey_fuller VARCHAR(30) NOT NULL,
    hourly_max VARCHAR(30) NOT NULL,
    hourly_min VARCHAR(30) NOT NULL,
    hourly_mean VARCHAR(30) NOT NULL,
    hourly_std VARCHAR(30) NOT NULL,
    three_hourly_max VARCHAR(30) NOT NULL,
    three_hourly_min VARCHAR(30) NOT NULL,
    three_hourly_mean VARCHAR(30) NOT NULL,
    three_hourly_std VARCHAR(30) NOT NULL,
    twelve_hourly_max VARCHAR(30) NOT NULL,
    twelve_hourly_min VARCHAR(30) NOT NULL,
    twelve_hourly_mean VARCHAR(30) NOT NULL,
    twelve_hourly_std VARCHAR(30) NOT NULL,
    prediction_max VARCHAR(30) NOT NULL,
    prediction_min VARCHAR(30) NOT NULL,
    prediction_mean VARCHAR(30) NOT NULL
);

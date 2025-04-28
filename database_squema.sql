--DROP TABLE IF EXISTS car_scrape_history CASCADE;
--DROP TABLE IF EXISTS car_info CASCADE;
--DROP TABLE IF EXISTS cars CASCADE;
--DROP TABLE IF EXISTS version_details CASCADE;
--DROP TABLE IF EXISTS versions CASCADE;
--DROP TABLE IF EXISTS scrapes CASCADE;

CREATE TABLE versions (
	version_id SERIAL PRIMARY KEY,
	brand VARCHAR(50) NOT NULL,
	model VARCHAR(75) NOT NULL,
	version_name VARCHAR(75) NOT NULL,
	year_prod SMALLINT NOT NULL,
	body_style VARCHAR(25) NOT NULL,
	engine_displacement DECIMAL(3, 1) NOT NULL,
	transmission_type VARCHAR(25)
);

CREATE TABLE version_details (
	version_id BIGINT REFERENCES versions (version_id) UNIQUE,
	mileage DECIMAL(4, 1),
	cylinders SMALLINT,
	num_of_gears SMALLINT,
	fuel_range SMALLINT,
	engine_type VARCHAR(25),
	fuel_type VARCHAR(25),
	horsepower SMALLINT,
	rim_inches SMALLINT,
	rim_material VARCHAR(25),
	num_of_doors SMALLINT,
	num_of_passengers SMALLINT,
	num_of_airbags SMALLINT,
	has_abs BOOLEAN DEFAULT FALSE,
	interior_materials VARCHAR(25),
	has_start_button BOOLEAN DEFAULT FALSE,
	has_cruise_control BOOLEAN DEFAULT FALSE,
	has_distance_sensor BOOLEAN DEFAULT FALSE,
	has_bluetooth BOOLEAN DEFAULT FALSE,
	has_rain_sensor BOOLEAN DEFAULT FALSE,
	has_automatic_emergency_breaking BOOLEAN DEFAULT FALSE,
	has_gps BOOLEAN DEFAULT FALSE,
	has_sunroof BOOLEAN DEFAULT FALSE,
    has_carplay BOOLEAN DEFAULT FALSE,
    has_androidauto BOOLEAN DEFAULT FALSE,
	weight_kg SMALLINT
);



CREATE TABLE cars (
	car_id SERIAL PRIMARY KEY,
	identifier SERIAL NOT NULL,
	website VARCHAR(25) NOT NULL,
	url VARCHAR(250) NOT NULL,
	image_url VARCHAR(250),
	version_id BIGINT REFERENCES versions (version_id),
    CONSTRAINT unique_identifier_website UNIQUE (identifier, website)
);


CREATE TABLE scrapes (
	scrape_id SERIAL PRIMARY KEY,
	datetime_start TIMESTAMP NOT NULL,
	datetime_end TIMESTAMP,
	finish_ok BOOLEAN DEFAULT FALSE,
	error_type VARCHAR(35),
    error_msg TEXT
);


CREATE TABLE scrape_history (
	scrape_id INT REFERENCES scrapes (scrape_id),
	car_id INT REFERENCES cars (car_id),
	labels TEXT,
	CONSTRAINT history_pkey PRIMARY KEY (scrape_id, car_id)
);

CREATE TABLE car_info (
	car_id BIGINT REFERENCES cars (car_id) UNIQUE,
	city VARCHAR(75),
	odometer INT,
	image_path TEXT,
    report_path TEXT
);

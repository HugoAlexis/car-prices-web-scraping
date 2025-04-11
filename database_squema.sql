DROP TABLE IF EXISTS car_scrape_history CASCADE;
DROP TABLE IF EXISTS car_info CASCADE;
DROP TABLE IF EXISTS cars CASCADE;
DROP TABLE IF EXISTS version_details CASCADE;
DROP TABLE IF EXISTS versions CASCADE;
DROP TABLE IF EXISTS scrapes CASCADE;

CREATE TABLE versions (
	version_id SERIAL PRIMARY KEY,
	brand VARCHAR(35),
	model VARCHAR(75),
	version_name VARCHAR(75),
	year_prod SMALLINT,
	body_style VARCHAR(50),
	engine_displacement DECIMAL(3, 1),
	transmission_type VARCHAR(25)
);

CREATE TABLE version_details (
	version_id BIGINT REFERENCES versions (version_id),
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
	has_abs BOOLEAN,
	interior_materials VARCHAR(25),
	has_start_button BOOLEAN,
	has_cruise_control BOOLEAN,
	has_distance_sensor BOOLEAN,
	has_bluetooth BOOLEAN,
	has_rain_sensor BOOLEAN,
	has_automatic_emergency_breaking BOOLEAN,
	has_gps BOOLEAN,
	has_sunroof BOOLEAN,
	length_meters SMALLINT,
	height_meters SMALLINT,
	width_meters SMALLINT,
	weight_kg SMALLINT
);



CREATE TABLE cars (
	car_id SERIAL PRIMARY KEY,
	identifier SERIAL NOT NULL,
	website VARCHAR(25) NOT NULL,
	url VARCHAR(150) NOT NULL,
	image_url VARCHAR(150) NOT NULL,
	inspection_report_url VARCHAR(150) NOT NULL,
	version_id BIGINT REFERENCES versions (version_id)
);


CREATE TABLE scrapes (
	scrape_id SERIAL PRIMARY KEY,
	datetime_start TIMESTAMP NOT NULL,
	datetime_end TIMESTAMP NOT NULL,
	finish_ok BOOLEAN,
	error_type VARCHAR(35)
);


CREATE TABLE scrape_history (
	scrape_id BIGINT REFERENCES scrapes (scrape_id),
	car_id BIGINT REFERENCES cars (car_id),
	labels TEXT,
	CONSTRAINT history_pkey PRIMARY KEY (scrape_id, car_id)
);

CREATE TABLE car_info (
	car_id BIGINT REFERENCES cars (car_id),
	city VARCHAR(75),
	odometer INT,
	image_path TEXT(120)
);

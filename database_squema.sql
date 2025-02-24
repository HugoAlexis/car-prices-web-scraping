CREATE TABLE cars (
    id INTEGER PRIMARY KEY,
    url TEXT NOT NULL,
    price INTEGER,
    status TEXT
);

CREATE TABLE car_info (
    id INTEGER PRIMARY KEY,
    brand TEXT,
    model TEXT,
    version TEXT,
    year INTEGER,
    body_style TEXT,
    engine_displacement NUMERIC,
    odometer INTEGER,
    city TEXT,
    transmission TEXT,
    mileage NUMERIC,
    cylinders  INTEGER,
    horsepower INTEGER,
    number_of_gears INTEGER,
    doors INTEGER,
    number_of_airbags INTEGER,
    abs INTEGER,
    passengers INTEGER,
    interior_materials TEXT,
    start_button INTEGER,
    cruise_control INTEGER,
    price INTEGER,
    price_without_discount INTEGER
)
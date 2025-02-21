CREATE TABLE car_item (
    id INTEGER PRIMARY KEY,
    url TEXT NOT NULL,
    price INTEGER,
    status TEXT
);

CREATE TABLE item_info (
    id INTEGER PRIMARY KEY,
    version TEXT,
    body_type TEXT,
    engine_displacement NUMERIC,
    odometer INTEGER,
    location TEXT,
    transmission TEXT,
    mileage NUMERIC,
    cylinders  INTEGER,
    horsepower INTEGER,
    transmission_gears INTEGER,
    doors INTEGER,
    airbags INTEGER,
    abs INTEGER,
    passengers INTEGER,
    interior_material TEXT,
    start_button INTEGER,
    cruise_control INTEGER
)
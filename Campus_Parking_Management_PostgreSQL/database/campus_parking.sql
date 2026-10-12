-- CAMPUS PARKING MANAGEMENT SYSTEM
-- PostgreSQL database script
-- Create the database "campus_parking" in pgAdmin first, then run this file.

DROP TABLE IF EXISTS parking_records CASCADE;
DROP TABLE IF EXISTS vehicles CASCADE;
DROP TABLE IF EXISTS parking_slots CASCADE;

CREATE TABLE parking_slots (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    slot_number VARCHAR(20) UNIQUE NOT NULL,
    slot_type VARCHAR(20) NOT NULL DEFAULT 'Car'
        CHECK (slot_type IN ('Car','Bike','EV')),
    status VARCHAR(20) NOT NULL DEFAULT 'Available'
        CHECK (status IN ('Available','Occupied'))
);

CREATE TABLE vehicles (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vehicle_number VARCHAR(30) UNIQUE NOT NULL,
    owner_name VARCHAR(100) NOT NULL,
    vehicle_type VARCHAR(20) NOT NULL DEFAULT 'Car'
        CHECK (vehicle_type IN ('Car','Bike','EV')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE parking_records (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
    slot_id INTEGER NOT NULL REFERENCES parking_slots(id) ON DELETE RESTRICT,
    entry_time TIMESTAMP NOT NULL DEFAULT NOW(),
    exit_time TIMESTAMP NULL,
    fee NUMERIC(10,2) NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'Parked'
        CHECK (status IN ('Parked','Completed'))
);

INSERT INTO parking_slots(slot_number, slot_type, status) VALUES
('C-01','Car','Occupied'),
('C-02','Car','Available'),
('C-03','Car','Occupied'),
('C-04','Car','Available'),
('C-05','Car','Available'),
('C-06','Car','Occupied'),
('B-01','Bike','Available'),
('B-02','Bike','Occupied'),
('B-03','Bike','Available'),
('B-04','Bike','Available'),
('B-05','Bike','Occupied'),
('B-06','Bike','Available'),
('E-01','EV','Available'),
('E-02','EV','Occupied'),
('E-03','EV','Available'),
('E-04','EV','Available');

INSERT INTO vehicles(vehicle_number, owner_name, vehicle_type) VALUES
('TN37AB1234','Arun Kumar','Car'),
('TN38CD5678','Rahul S','Car'),
('TN39EF9012','Kavin Raj','Bike'),
('TN40GH3456','Vignesh M','Bike'),
('TN41JK7890','Sanjay R','EV'),
('TN42LM1122','Praveen K','Car'),
('TN43NP3344','Dinesh P','Bike'),
('TN45QR5566','Harish V','Car');

INSERT INTO parking_records(vehicle_id, slot_id, entry_time, exit_time, fee, status) VALUES
(1,1,NOW() - INTERVAL '2 hours',NULL,0,'Parked'),
(2,3,NOW() - INTERVAL '1 hour',NULL,0,'Parked'),
(3,8,NOW() - INTERVAL '45 minutes',NULL,0,'Parked'),
(4,11,NOW() - INTERVAL '3 hours',NULL,0,'Parked'),
(5,14,NOW() - INTERVAL '30 minutes',NULL,0,'Parked'),
(6,6,CURRENT_DATE + INTERVAL '8 hours',CURRENT_DATE + INTERVAL '10 hours',40,'Completed'),
(7,2,CURRENT_DATE - INTERVAL '1 day' + INTERVAL '9 hours',
   CURRENT_DATE - INTERVAL '1 day' + INTERVAL '12 hours',60,'Completed'),
(8,4,CURRENT_DATE - INTERVAL '2 days' + INTERVAL '10 hours',
   CURRENT_DATE - INTERVAL '2 days' + INTERVAL '13 hours',60,'Completed');

-- Keep slot status synchronized with the sample active records.
UPDATE parking_slots SET status='Occupied' WHERE id IN (1,3,6,8,11,14);
UPDATE parking_slots SET status='Available' WHERE id IN (2,4,5,7,9,10,12,13,15,16);

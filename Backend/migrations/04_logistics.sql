-- ==========================================================
-- Migration 04: Logistics, Warehouses & Shipments (Logistics Blueprint)
-- ==========================================================

CREATE TABLE IF NOT EXISTS WAREHOUSES (
    warehouse_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city_id INT NOT NULL,
    address VARCHAR(255) NOT NULL,
    capacity_sqft INT NOT NULL DEFAULT 50000,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (city_id) REFERENCES TEXAS_CITY(city_id)
);

CREATE TABLE IF NOT EXISTS SHIPMENTS (
    shipment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL UNIQUE,
    carrier VARCHAR(50) NOT NULL DEFAULT 'Texas Express Logistics',
    tracking_number VARCHAR(100) NOT NULL UNIQUE,
    origin_warehouse_id INT,
    destination_city_id INT NOT NULL,
    shipment_status ENUM('Label Created', 'In Transit', 'Out for Delivery', 'Delivered', 'Delayed') NOT NULL DEFAULT 'Label Created',
    shipped_at TIMESTAMP NULL,
    delivered_at TIMESTAMP NULL,
    estimated_delivery TIMESTAMP NULL,
    FOREIGN KEY (order_id) REFERENCES ORDERS(order_id) ON DELETE CASCADE,
    FOREIGN KEY (origin_warehouse_id) REFERENCES WAREHOUSES(warehouse_id),
    FOREIGN KEY (destination_city_id) REFERENCES TEXAS_CITY(city_id)
);

CREATE TABLE IF NOT EXISTS DELIVERY_ROUTES (
    route_id INT AUTO_INCREMENT PRIMARY KEY,
    origin_city_id INT NOT NULL,
    destination_city_id INT NOT NULL,
    distance_miles DECIMAL(6, 2) NOT NULL,
    estimated_hours DECIMAL(4, 2) NOT NULL,
    is_major_corridor BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (origin_city_id) REFERENCES TEXAS_CITY(city_id),
    FOREIGN KEY (destination_city_id) REFERENCES TEXAS_CITY(city_id)
);

-- Seed Warehouses
INSERT INTO WAREHOUSES (warehouse_id, name, city_id, address, capacity_sqft, is_active)
VALUES
    (1, 'DFW Central Distribution Hub', 3, '2100 Logistics Pkwy, Dallas, TX', 250000, 1),
    (2, 'Gulf Coast Regional Fulfillment', 1, '8800 Port Access Rd, Houston, TX', 180000, 1),
    (3, 'Austin Tech Logistics Depot', 4, '450 Tech Ridge Blvd, Austin, TX', 95000, 1)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    capacity_sqft = VALUES(capacity_sqft);

-- Seed Delivery Routes between Texas Cities
INSERT INTO DELIVERY_ROUTES (route_id, origin_city_id, destination_city_id, distance_miles, estimated_hours, is_major_corridor)
VALUES
    (1, 3, 4, 195.0, 3.2, 1), -- Dallas to Austin (I-35)
    (2, 3, 1, 239.0, 3.8, 1), -- Dallas to Houston (I-45)
    (3, 1, 2, 197.0, 3.0, 1), -- Houston to San Antonio (I-10)
    (4, 4, 2, 79.5, 1.4, 1),  -- Austin to San Antonio (I-35)
    (5, 3, 6, 635.0, 9.5, 1), -- Dallas to El Paso (I-20/I-10)
    (6, 3, 10, 345.0, 5.2, 0) -- Dallas to Lubbock (US-84)
ON DUPLICATE KEY UPDATE
    distance_miles = VALUES(distance_miles),
    estimated_hours = VALUES(estimated_hours);

-- Seed Shipments
INSERT INTO SHIPMENTS (shipment_id, order_id, carrier, tracking_number, origin_warehouse_id, destination_city_id, shipment_status, shipped_at, delivered_at, estimated_delivery)
VALUES
    (1, 1, 'Texas Freight Lines', 'TX-TRK-770011', 3, 4, 'Delivered', '2026-08-15 11:00:00', '2026-08-16 14:20:00', '2026-08-16 18:00:00'),
    (2, 2, 'LoneStar Express', 'TX-TRK-770022', 1, 1, 'In Transit', '2026-09-02 08:30:00', NULL, '2026-09-13 17:00:00'),
    (3, 3, 'Texas Freight Lines', 'TX-TRK-770033', 1, 3, 'Label Created', NULL, NULL, '2026-09-14 18:00:00')
ON DUPLICATE KEY UPDATE
    shipment_status = VALUES(shipment_status),
    tracking_number = VALUES(tracking_number);

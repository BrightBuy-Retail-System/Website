-- ==========================================================
-- Migration 00: Foundation - TEXAS_CITY Lookup Table & Seed
-- Shared Seed Script required by CUSTOMER and ORDERS
-- ==========================================================

CREATE TABLE IF NOT EXISTS TEXAS_CITY (
    city_id INT AUTO_INCREMENT PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL UNIQUE,
    city_type ENUM('Main', 'Other') NOT NULL DEFAULT 'Other',
    state_code VARCHAR(2) NOT NULL DEFAULT 'TX',
    postal_code_prefix VARCHAR(10) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed foundational Texas cities (Main hubs and Other regional cities)
INSERT INTO TEXAS_CITY (city_name, city_type, state_code, postal_code_prefix)
VALUES
    -- Major Metropolitan Hubs ('Main')
    ('Houston', 'Main', 'TX', '770'),
    ('San Antonio', 'Main', 'TX', '782'),
    ('Dallas', 'Main', 'TX', '752'),
    ('Austin', 'Main', 'TX', '787'),
    ('Fort Worth', 'Main', 'TX', '761'),
    ('El Paso', 'Main', 'TX', '799'),
    ('Arlington', 'Main', 'TX', '760'),
    ('Corpus Christi', 'Main', 'TX', '784'),
    ('Plano', 'Main', 'TX', '750'),
    ('Lubbock', 'Main', 'TX', '794'),
    ('Laredo', 'Main', 'TX', '780'),
    ('Irving', 'Main', 'TX', '750'),
    ('Garland', 'Main', 'TX', '750'),
    ('Frisco', 'Main', 'TX', '750'),
    ('McKinney', 'Main', 'TX', '750'),
    
    -- Regional & Surrounding Cities ('Other')
    ('Amarillo', 'Other', 'TX', '791'),
    ('Brownsville', 'Other', 'TX', '785'),
    ('Killeen', 'Other', 'TX', '765'),
    ('Pasadena', 'Other', 'TX', '775'),
    ('Mesquite', 'Other', 'TX', '751'),
    ('McAllen', 'Other', 'TX', '785'),
    ('Denton', 'Other', 'TX', '762'),
    ('Waco', 'Other', 'TX', '767'),
    ('Carrollton', 'Other', 'TX', '750'),
    ('Midland', 'Other', 'TX', '797'),
    ('Abilene', 'Other', 'TX', '796'),
    ('Beaumont', 'Other', 'TX', '777'),
    ('Round Rock', 'Other', 'TX', '786'),
    ('Odessa', 'Other', 'TX', '797'),
    ('Wichita Falls', 'Other', 'TX', '763'),
    ('Tyler', 'Other', 'TX', '757'),
    ('College Station', 'Other', 'TX', '778'),
    ('San Angelo', 'Other', 'TX', '769')
ON DUPLICATE KEY UPDATE 
    city_type = VALUES(city_type),
    state_code = VALUES(state_code),
    postal_code_prefix = VALUES(postal_code_prefix);

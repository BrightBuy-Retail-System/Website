-- ==========================================================
-- Migration 02: Customers, Authentication & Cart (Auth & Cart Blueprint)
-- ==========================================================

CREATE TABLE IF NOT EXISTS CUSTOMERS (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    address_line VARCHAR(255),
    city_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (city_id) REFERENCES TEXAS_CITY(city_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS CARTS (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT UNIQUE,
    session_token VARCHAR(100) UNIQUE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES CUSTOMERS(customer_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS CART_ITEMS (
    cart_item_id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES CARTS(cart_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(product_id) ON DELETE CASCADE,
    UNIQUE KEY uq_cart_product (cart_id, product_id)
);

-- Seed Sample Customers linked to Texas Cities
INSERT INTO CUSTOMERS (customer_id, first_name, last_name, email, phone, address_line, city_id)
VALUES
    (1, 'Wyatt', 'Morgan', 'wyatt.morgan@texastech.edu', '512-555-0143', '104 Congress Ave', 4), -- Austin
    (2, 'Sarah', 'Jenkins', 'sarah.j@houstonenergy.com', '713-555-0199', '2400 Westheimer Rd', 1), -- Houston
    (3, 'Marcus', 'Sterling', 'm.sterling@dallastx.org', '214-555-0182', '1500 Main St', 3), -- Dallas
    (4, 'Elena', 'Rodriguez', 'elena.rodriguez@satx.net', '210-555-0120', '800 E Commerce St', 2) -- San Antonio
ON DUPLICATE KEY UPDATE
    first_name = VALUES(first_name),
    last_name = VALUES(last_name),
    email = VALUES(email),
    phone = VALUES(phone),
    city_id = VALUES(city_id);

-- Initialize sample carts
INSERT INTO CARTS (cart_id, customer_id, session_token)
VALUES
    (1, 1, 'sess_wyatt_001'),
    (2, 2, 'sess_sarah_002')
ON DUPLICATE KEY UPDATE
    session_token = VALUES(session_token);

INSERT INTO CART_ITEMS (cart_id, product_id, quantity)
VALUES
    (1, 1, 2),
    (1, 4, 1),
    (2, 8, 3)
ON DUPLICATE KEY UPDATE
    quantity = VALUES(quantity);

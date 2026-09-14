-- ==========================================================
-- Migration 03: Orders & Order Line Items (Orders Blueprint)
-- ==========================================================

CREATE TABLE IF NOT EXISTS ORDERS (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    customer_id INT NOT NULL,
    shipping_city_id INT NOT NULL,
    shipping_address VARCHAR(255) NOT NULL,
    order_status ENUM('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled') NOT NULL DEFAULT 'Pending',
    payment_status ENUM('Pending', 'Paid', 'Failed', 'Refunded') NOT NULL DEFAULT 'Pending',
    subtotal DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    tax DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    shipping_cost DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES CUSTOMERS(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (shipping_city_id) REFERENCES TEXAS_CITY(city_id)
);

CREATE TABLE IF NOT EXISTS ORDER_ITEMS (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10, 2) NOT NULL,
    line_total DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES ORDERS(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(product_id)
);

-- Seed Sample Orders
INSERT INTO ORDERS (order_id, order_number, customer_id, shipping_city_id, shipping_address, order_status, payment_status, subtotal, tax, shipping_cost, total_amount, order_date)
VALUES
    (1, 'TX-ORD-2026-1001', 1, 4, '104 Congress Ave, Austin, TX', 'Delivered', 'Paid', 259.98, 21.45, 12.00, 293.43, '2026-08-15 10:30:00'),
    (2, 'TX-ORD-2026-1002', 2, 1, '2400 Westheimer Rd, Houston, TX', 'Shipped', 'Paid', 499.00, 41.17, 18.50, 558.67, '2026-09-01 14:15:00'),
    (3, 'TX-ORD-2026-1003', 3, 3, '1500 Main St, Dallas, TX', 'Processing', 'Paid', 378.50, 31.23, 15.00, 424.73, '2026-09-08 09:45:00'),
    (4, 'TX-ORD-2026-1004', 4, 2, '800 E Commerce St, San Antonio, TX', 'Pending', 'Pending', 89.00, 7.34, 10.00, 106.34, '2026-09-11 16:20:00')
ON DUPLICATE KEY UPDATE
    order_status = VALUES(order_status),
    payment_status = VALUES(payment_status),
    total_amount = VALUES(total_amount);

-- Seed Order Items
INSERT INTO ORDER_ITEMS (order_item_id, order_id, product_id, quantity, unit_price, line_total)
VALUES
    (1, 1, 1, 2, 129.99, 259.98),
    (2, 2, 2, 1, 499.00, 499.00),
    (3, 3, 3, 2, 189.50, 379.00),
    (4, 4, 4, 1, 89.00, 89.00)
ON DUPLICATE KEY UPDATE
    quantity = VALUES(quantity),
    unit_price = VALUES(unit_price),
    line_total = VALUES(line_total);

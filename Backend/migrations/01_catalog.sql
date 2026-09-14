-- ==========================================================
-- Migration 01: Product Catalog & Categories (Catalog Blueprint)
-- ==========================================================

CREATE TABLE IF NOT EXISTS CATEGORIES (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50) DEFAULT 'bi-box-seam',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS PRODUCTS (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT,
    name VARCHAR(150) NOT NULL,
    sku VARCHAR(50) NOT NULL UNIQUE,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    description TEXT,
    image_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES CATEGORIES(category_id) ON DELETE SET NULL
);

-- Seed Categories
INSERT INTO CATEGORIES (category_id, name, slug, description, icon)
VALUES
    (1, 'Electronics & Gadgets', 'electronics', 'Cutting-edge tech, sensors, devices, and accessories', 'bi-cpu'),
    (2, 'Apparel & Workwear', 'apparel', 'Durable Texas-ready workwear, boots, and casual gear', 'bi-tag'),
    (3, 'Home & Living', 'home-living', 'Furniture, ranch decor, and home essentials', 'bi-house-door'),
    (4, 'Tools & Industrial', 'tools-industrial', 'Heavy-duty tools, hardware, and supplies', 'bi-tools'),
    (5, 'Food & Texas Specialties', 'food-specialties', 'Artisan BBQ sauces, seasonings, and Texas snacks', 'bi-cup-hot')
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    slug = VALUES(slug),
    description = VALUES(description),
    icon = VALUES(icon);

-- Seed Sample Products
INSERT INTO PRODUCTS (category_id, name, sku, price, stock_quantity, description, image_url, is_active)
VALUES
    (1, 'LoneStar Smart IoT Thermostat', 'TX-ELEC-001', 129.99, 45, 'Smart WiFi thermostat optimized for high-efficiency Texas summer cooling.', 'https://images.unsplash.com/photo-1545259741-2ea3ebf61fa3?w=500&auto=format&fit=crop&q=60', 1),
    (1, 'Solar Power Station 1000W', 'TX-ELEC-002', 499.00, 20, 'Portable backup battery generator for emergency weather resilience.', 'https://images.unsplash.com/photo-1509391365360-2e959784a276?w=500&auto=format&fit=crop&q=60', 1),
    (2, 'Austin Premium Leather Boots', 'TX-APP-001', 189.50, 60, 'Handcrafted genuine leather boots with cushioned all-day arch support.', 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&auto=format&fit=crop&q=60', 1),
    (2, 'Heavyweight Denim Work Jacket', 'TX-APP-002', 89.00, 35, 'Rugged triple-stitched denim jacket designed for field work.', 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500&auto=format&fit=crop&q=60', 1),
    (3, 'Reclaimed Cedar Coffee Table', 'TX-HOME-001', 249.99, 15, 'Solid cedar table crafted from sustainable Hill Country timber.', 'https://images.unsplash.com/photo-1532372320572-cda25653a26d?w=500&auto=format&fit=crop&q=60', 1),
    (3, 'Cast Iron Dutch Oven 6qt', 'TX-HOME-002', 65.00, 40, 'Pre-seasoned cast iron pot for traditional Texas chili and roasts.', 'https://images.unsplash.com/photo-1584990347449-39908cfd5218?w=500&auto=format&fit=crop&q=60', 1),
    (4, 'Cordless Brushless Impact Driver 20V', 'TX-TOOL-001', 119.00, 50, 'High torque impact driver with twin lithium-ion battery packs.', 'https://images.unsplash.com/photo-1504148455328-c376907d081c?w=500&auto=format&fit=crop&q=60', 1),
    (5, 'Authentic Mesquite Smoked BBQ Sauce (3-Pack)', 'TX-FOOD-001', 24.99, 120, 'Award-winning sweet & tangy mesquite BBQ sauce from Lockhart, TX.', 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=500&auto=format&fit=crop&q=60', 1)
ON DUPLICATE KEY UPDATE
    price = VALUES(price),
    stock_quantity = VALUES(stock_quantity),
    description = VALUES(description);

# DATABASE_SCHEMA.md: BrightBuy Retail Inventory & Order Management System

This specification defines the canonical relational database schema for the BrightBuy platform. It enforces Boyce-Codd Normal Form (BCNF) / Third Normal Form (3NF), guarantees ACID compliance, implements regional Texas delivery business logic, and provides physical PostgreSQL DDL definitions, procedures, triggers, indexes, and reporting queries.
## 1. System Metadata & Design Standards

- **Target DBMS:** PostgreSQL 15+
    
- **Primary Key Standard:** Surrogate identity keys (`BIGINT` or `INT GENERATED ALWAYS AS IDENTITY`).
    
- **Temporal Standard:** `TIMESTAMPTZ` defaulted to `CURRENT_TIMESTAMP`.
    
- **Monetary Standard:** `DECIMAL(10, 2)` for exact monetary calculation without floating-point error.
    
- **Boolean Standard:** Native `BOOLEAN` (`TRUE` / `FALSE`).
    
- **Normalization Standard:**
    
    - All 14 tables strictly conform to BCNF/3NF.
        
    - Logistics lead times and pricing at checkout are modeled as **immutable contractual snapshots** to ensure historical integrity without transitive dependency anomalies.
        
- **Concurrency Standard:** Row-level locks (`FOR UPDATE`) are utilized inside stored procedures during inventory checks and deductions to prevent checkout race conditions.
    

## 2. Enumerated Domain Types (PostgreSQL ENUMs)

```
CREATE TYPE staff_role AS ENUM (
    'ADMIN', 
    'WAREHOUSE_MANAGER', 
    'FULFILLMENT_STAFF', 
    'SUPPORT_AGENT'
);

CREATE TYPE city_type_enum AS ENUM (
    'MAIN', 
    'OTHER'
);

CREATE TYPE delivery_mode_enum AS ENUM (
    'STORE_PICKUP', 
    'STANDARD_DELIVERY'
);

CREATE TYPE payment_method_enum AS ENUM (
    'COD', 
    'CARD'
);

CREATE TYPE payment_status_enum AS ENUM (
    'PENDING', 
    'PAID', 
    'FAILED', 
    'REFUNDED'
);

CREATE TYPE order_status_enum AS ENUM (
    'PLACED', 
    'PROCESSING', 
    'SHIPPED', 
    'DELIVERED', 
    'CANCELLED'
);
```

## 3. Relational Schemas & DDL

### 3.1. Subsystem: Regional Logistics

#### `texas_city`

Stores predefined Texas delivery regions used to calculate transit times and delivery commitments.

- **Normal Form:** BCNF
    
- **Candidate Key:** `{"city_id"}`
    
- **Dependencies:** $\text{city\_id} \to \{\text{city\_name}, \text{city\_type}\}$
    

```
CREATE TABLE texas_city (
    city_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL UNIQUE,
    city_type city_type_enum NOT NULL
);
```

### 3.2. Subsystem: Catalog & Inventory

#### `brand`

Manufacturers and product brands.

- **Normal Form:** BCNF
    
- **Candidate Key:** `{"brand_id"}`
    
- **Dependencies:** $\text{brand\_id} \to \{\text{brand\_name}\}$
    

```
CREATE TABLE brand (
    brand_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    brand_name VARCHAR(100) NOT NULL UNIQUE
);
```

#### `category`

Product classifications (e.g., Mobiles, Audio Devices, Toys).

- **Normal Form:** BCNF
    
- **Candidate Key:** `{"category_id"}`
    
- **Dependencies:** $\text{category\_id} \to \{\text{category\_name}, \text{description}\}$
    

```
CREATE TABLE category (
    category_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);
```

#### `product`

Abstract product entities. Contains no price or inventory fields.

- **Normal Form:** BCNF
    
- **Candidate Key:** `{"product_id"}`
    
- **Dependencies:** $\text{product\_id} \to \{\text{brand\_id}, \text{title}, \text{description}, \text{is\_active}, \text{created\_at}\}$
    
- **Foreign Keys:**
    
    - `brand_id` $\to$ `brand(brand_id)` (`ON DELETE RESTRICT`)
        

```
CREATE TABLE product (
    product_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    brand_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_product_brand FOREIGN KEY (brand_id) 
        REFERENCES brand(brand_id) ON DELETE RESTRICT
);
```

#### `product_category`

Bridge relation resolving the $M:N$ relationship between `product` and `category`.

- **Normal Form:** BCNF (All-key relation)
    
- **Candidate Key:** `{"product_id", "category_id"}`
    
- **Foreign Keys:**
    
    - `product_id` $\to$ `product(product_id)` (`ON DELETE CASCADE`)
        
    - `category_id` $\to$ `category(category_id)` (`ON DELETE CASCADE`)
        

```
CREATE TABLE product_category (
    product_id INT NOT NULL,
    category_id INT NOT NULL,
    PRIMARY KEY (product_id, category_id),
    CONSTRAINT fk_pc_product FOREIGN KEY (product_id) 
        REFERENCES product(product_id) ON DELETE CASCADE,
    CONSTRAINT fk_pc_category FOREIGN KEY (category_id) 
        REFERENCES category(category_id) ON DELETE CASCADE
);
```

#### `product_variant`

The physical sellable SKU. Holds the catalog unit price and warehouse inventory counter.

- **Normal Form:** BCNF
    
- **Candidate Keys:** `{"variant_id"}`, `{"sku"}`
    
- **Dependencies:**
    
    - $\text{variant\_id} \to \{\text{product\_id}, \text{sku}, \text{variant\_name}, \text{price}, \text{stock\_quantity}, \text{is\_active}\}$
        
    - $\text{sku} \to \{\text{product\_id}, \text{variant\_id}, \text{variant\_name}, \text{price}, \text{stock\_quantity}, \text{is\_active}\}$
        
- **Foreign Keys:**
    
    - `product_id` $\to$ `product(product_id)` (`ON DELETE CASCADE`)
        

```
CREATE TABLE product_variant (
    variant_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id INT NOT NULL,
    sku VARCHAR(50) NOT NULL UNIQUE,
    variant_name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0.00),
    stock_quantity INT NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_variant_product FOREIGN KEY (product_id) 
        REFERENCES product(product_id) ON DELETE CASCADE
);
```

### 3.3. Subsystem: Customer Identity & Cart

#### `customer`

Registered customer accounts. Guests browse without an entry in this table.

- **Normal Form:** BCNF
    
- **Candidate Keys:** `{"customer_id"}`, `{"email"}`
    
- **Dependencies:** $\text{customer\_id} \to \{\text{email}, \text{password\_hash}, \text{full\_name}, \text{phone\_number}, \text{default\_city\_id}, \text{created\_at}\}$
    
- **Foreign Keys:**
    
    - `default_city_id` $\to$ `texas_city(city_id)` (`ON DELETE SET NULL`)
        

```
CREATE TABLE customer (
    customer_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20),
    default_city_id INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_customer_city FOREIGN KEY (default_city_id) 
        REFERENCES texas_city(city_id) ON DELETE SET NULL
);
```

#### `cart`

Active shopping basket. Strictly $1:1$ with `customer`.

- **Normal Form:** BCNF
    
- **Candidate Keys:** `{"cart_id"}`, `{"customer_id"}`
    
- **Dependencies:** $\text{cart\_id} \to \{\text{customer\_id}, \text{created\_at}, \text{updated\_at}\}$
    
- **Foreign Keys:**
    
    - `customer_id` $\to$ `customer(customer_id)` (`ON DELETE CASCADE`)
        

```
CREATE TABLE cart (
    cart_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id INT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cart_customer FOREIGN KEY (customer_id) 
        REFERENCES customer(customer_id) ON DELETE CASCADE
);
```

#### `cart_item`

Transient items placed into an active basket. Does NOT store unit price.

- **Normal Form:** BCNF
    
- **Candidate Keys:** `{"cart_item_id"}`, `{"cart_id", "variant_id"}`
    
- **Dependencies:**
    
    - $\text{cart\_item\_id} \to \{\text{cart\_id}, \text{variant\_id}, \text{quantity}, \text{added\_at}\}$
        
    - $\{\text{cart\_id}, \text{variant\_id}\} \to \{\text{cart\_item\_id}, \text{quantity}, \text{added\_at}\}$
        
- **Foreign Keys:**
    
    - `cart_id` $\to$ `cart(cart_id)` (`ON DELETE CASCADE`)
        
    - `variant_id` $\to$ `product_variant(variant_id)` (`ON DELETE RESTRICT`)
        

```
CREATE TABLE cart_item (
    cart_item_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cart_id INT NOT NULL,
    variant_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    added_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_cart_variant UNIQUE (cart_id, variant_id),
    CONSTRAINT fk_ci_cart FOREIGN KEY (cart_id) 
        REFERENCES cart(cart_id) ON DELETE CASCADE,
    CONSTRAINT fk_ci_variant FOREIGN KEY (variant_id) 
        REFERENCES product_variant(variant_id) ON DELETE RESTRICT
);
```

### 3.4. Subsystem: Order Processing & Delivery

#### `orders`

Legally binding purchase contracts. Contains customer snapshots, fulfillment state, and delivery lead time commitments.

- **Normal Form:** BCNF (Delivery parameters represent immutable contractual SLA commitments recorded at checkout).
    
- **Candidate Key:** `{"order_id"}`
    
- **Foreign Keys:**
    
    - `customer_id` $\to$ `customer(customer_id)` (`ON DELETE RESTRICT`)
        
    - `city_id` $\to$ `texas_city(city_id)` (`ON DELETE RESTRICT`)
        

```
CREATE TABLE orders (
    order_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id INT NOT NULL,
    city_id INT,
    order_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    delivery_mode delivery_mode_enum NOT NULL,
    payment_method payment_method_enum NOT NULL,
    payment_status payment_status_enum NOT NULL DEFAULT 'PENDING',
    order_status order_status_enum NOT NULL DEFAULT 'PLACED',
    shipping_address TEXT,
    delivery_lead_time_days SMALLINT NOT NULL CHECK (delivery_lead_time_days >= 0),
    has_out_of_stock_items BOOLEAN NOT NULL DEFAULT FALSE,
    estimated_delivery_date DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) 
        REFERENCES customer(customer_id) ON DELETE RESTRICT,
    CONSTRAINT fk_orders_city FOREIGN KEY (city_id) 
        REFERENCES texas_city(city_id) ON DELETE RESTRICT,
    CONSTRAINT chk_pickup_address CHECK (
        (delivery_mode = 'STORE_PICKUP') OR 
        (delivery_mode = 'STANDARD_DELIVERY' AND shipping_address IS NOT NULL AND city_id IS NOT NULL)
    )
);
```

#### `order_item`

Immutable line items. Freezes `unit_price` at the instant of order confirmation.

- **Normal Form:** BCNF
    
- **Candidate Keys:** `{"order_item_id"}`, `{"order_id", "variant_id"}`
    
- **Dependencies:**
    
    - $\text{order\_item\_id} \to \{\text{order\_id}, \text{variant\_id}, \text{quantity}, \text{unit\_price}\}$
        
    - $\{\text{order\_id}, \text{variant\_id}\} \to \{\text{order\_item\_id}, \text{quantity}, \text{unit\_price}\}$
        
- **Foreign Keys:**
    
    - `order_id` $\to$ `orders(order_id)` (`ON DELETE CASCADE`)
        
    - `variant_id` $\to$ `product_variant(variant_id)` (`ON DELETE RESTRICT`)
        

```
CREATE TABLE order_item (
    order_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT NOT NULL,
    variant_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0.00),
    CONSTRAINT uq_order_variant UNIQUE (order_id, variant_id),
    CONSTRAINT fk_oi_orders FOREIGN KEY (order_id) 
        REFERENCES orders(order_id) ON DELETE CASCADE,
    CONSTRAINT fk_oi_variant FOREIGN KEY (variant_id) 
        REFERENCES product_variant(variant_id) ON DELETE RESTRICT
);
```

### 3.5. Subsystem: Financial Ledger & Operational Audit

#### `staff`

Internal BrightBuy administrative, warehouse, and support personnel.

- **Normal Form:** BCNF
    
- **Candidate Keys:** `{"staff_id"}`, `{"email"}`
    
- **Dependencies:** $\text{staff\_id} \to \{\text{email}, \text{full\_name}, \text{role}, \text{password\_hash}, \text{is\_active}, \text{created\_at}\}$
    

```
CREATE TABLE staff (
    staff_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    role staff_role NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

#### `payment_transaction`

Append-only ledger of payment processing and refund attempts.

- **Normal Form:** BCNF
    
- **Candidate Key:** `{"payment_id"}`
    
- **Foreign Keys:**
    
    - `order_id` $\to$ `orders(order_id)` (`ON DELETE RESTRICT`)
        

```
CREATE TABLE payment_transaction (
    payment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0.00),
    transaction_reference VARCHAR(100) NOT NULL UNIQUE,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_payment_order FOREIGN KEY (order_id) 
        REFERENCES orders(order_id) ON DELETE RESTRICT
);
```

#### `order_status_history`

Append-only state machine audit trail tracking transitions of `orders.order_status`.

- **Normal Form:** BCNF
    
- **Candidate Key:** `{"history_id"}`
    
- **Foreign Keys:**
    
    - `order_id` $\to$ `orders(order_id)` (`ON DELETE CASCADE`)
        
    - `changed_by_staff_id` $\to$ `staff(staff_id)` (`ON DELETE SET NULL`)
        

```
CREATE TABLE order_status_history (
    history_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT NOT NULL,
    changed_by_staff_id INT,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    previous_status order_status_enum,
    new_status order_status_enum NOT NULL,
    CONSTRAINT fk_history_order FOREIGN KEY (order_id) 
        REFERENCES orders(order_id) ON DELETE CASCADE,
    CONSTRAINT fk_history_staff FOREIGN KEY (changed_by_staff_id) 
        REFERENCES staff(staff_id) ON DELETE SET NULL
);
```

## 4. Performance Indexes

```
-- Catalog Browsing & Search
CREATE INDEX idx_variant_product_id ON product_variant(product_id);
CREATE INDEX idx_product_brand ON product(brand_id);
CREATE INDEX idx_product_category_cat ON product_category(category_id);

-- Cart Session Fetching
CREATE INDEX idx_cart_item_cart ON cart_item(cart_id);

-- Management Reports 1 & 2: Sales over time & Top-selling products
CREATE INDEX idx_orders_order_date ON orders(order_date);
CREATE INDEX idx_orders_status ON orders(order_status, payment_status);
CREATE INDEX idx_order_item_variant ON order_item(variant_id);

-- Management Report 4: Upcoming delivery scheduling
CREATE INDEX idx_orders_delivery_schedule ON orders(estimated_delivery_date) 
    WHERE order_status NOT IN ('DELIVERED', 'CANCELLED');

-- Management Report 5: Customer order histories
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```

## 5. ACID Integrity & Business Rules (Database Routines)

### 5.1. Delivery Date Calculation Function

Enforces BrightBuy's regional transit policy:

$$\text{Days} = \begin{cases} 5 & \text{if } \text{city\_type} = \text{'MAIN'} \land \neg\text{backordered} \\ 8 & \text{if } \text{city\_type} = \text{'MAIN'} \land \text{backordered} \\ 7 & \text{if } \text{city\_type} = \text{'OTHER'} \land \neg\text{backordered} \\ 10 & \text{if } \text{city\_type} = \text{'OTHER'} \land \text{backordered} \end{cases}$$

```
CREATE OR REPLACE FUNCTION fn_calculate_delivery_date(
    p_city_id INT,
    p_has_out_of_stock BOOLEAN,
    OUT p_lead_time SMALLINT,
    OUT p_est_date DATE
)
RETURNS RECORD AS $$
DECLARE
    v_type city_type_enum;
BEGIN
    SELECT city_type INTO v_type FROM texas_city WHERE city_id = p_city_id;
    
    IF v_type = 'MAIN' THEN
        p_lead_time := 5;
    ELSE
        p_lead_time := 7;
    END IF;

    IF p_has_out_of_stock THEN
        p_lead_time := p_lead_time + 3;
    END IF;

    p_est_date := CURRENT_DATE + (p_lead_time * INTERVAL '1 day');
END;
$$ LANGUAGE plpgsql STABLE;
```

### 5.2. Automated Status Audit Trigger

Fires on transitions of `orders.order_status`, writing to `order_status_history`.

```
CREATE OR REPLACE FUNCTION trg_fn_audit_order_status()
RETURNS TRIGGER AS $$
BEGIN
    IF (OLD.order_status IS DISTINCT FROM NEW.order_status) THEN
        INSERT INTO order_status_history (
            order_id, 
            changed_by_staff_id, 
            changed_at, 
            previous_status, 
            new_status
        ) VALUES (
            NEW.order_id, 
            NULL,
            CURRENT_TIMESTAMP, 
            OLD.order_status, 
            NEW.order_status
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_order_status_update
AFTER UPDATE OF order_status ON orders
FOR EACH ROW
EXECUTE FUNCTION trg_fn_audit_order_status();
```

### 5.3. Atomic Checkout Procedure (`sp_place_order`)

Guarantees atomicity and validates stock decrement via row-level locks (`FOR UPDATE`).

```
CREATE OR REPLACE PROCEDURE sp_place_order(
    p_customer_id INT,
    p_city_id INT,
    p_delivery_mode delivery_mode_enum,
    p_payment_method payment_method_enum,
    p_shipping_address TEXT,
    INOUT p_order_id BIGINT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_cart_id INT;
    v_has_backordered BOOLEAN := FALSE;
    v_lead_days SMALLINT;
    v_est_date DATE;
    v_item RECORD;
BEGIN
    -- 1. Identify Cart
    SELECT cart_id INTO v_cart_id FROM cart WHERE customer_id = p_customer_id;
    IF v_cart_id IS NULL THEN
        RAISE EXCEPTION 'Active cart not found for customer %', p_customer_id;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM cart_item WHERE cart_id = v_cart_id) THEN
        RAISE EXCEPTION 'Cannot checkout an empty cart';
    END IF;

    -- 2. Inspect stock levels to flag backorders
    IF EXISTS (
        SELECT 1 
        FROM cart_item ci
        JOIN product_variant pv ON ci.variant_id = pv.variant_id
        WHERE ci.cart_id = v_cart_id AND pv.stock_quantity < ci.quantity
    ) THEN
        v_has_backordered := TRUE;
    END IF;

    -- 3. Calculate delivery timeline
    IF p_delivery_mode = 'STANDARD_DELIVERY' THEN
        SELECT p_lead_time, p_est_date 
        INTO v_lead_days, v_est_date 
        FROM fn_calculate_delivery_date(p_city_id, v_has_backordered);
    ELSE
        v_lead_days := 1;
        v_est_date := CURRENT_DATE + INTERVAL '1 day';
    END IF;

    -- 4. Create Order Record
    INSERT INTO orders (
        customer_id, city_id, delivery_mode, payment_method, 
        payment_status, order_status, shipping_address, 
        delivery_lead_time_days, has_out_of_stock_items, estimated_delivery_date
    ) VALUES (
        p_customer_id, p_city_id, p_delivery_mode, p_payment_method,
        'PENDING', 'PLACED', p_shipping_address,
        v_lead_days, v_has_backordered, v_est_date
    ) RETURNING order_id INTO p_order_id;

    -- 5. Atomic Stock Deduction & Line Item Snapshotting (with row-level locks)
    FOR v_item IN (
        SELECT ci.variant_id, ci.quantity, pv.price, pv.stock_quantity
        FROM cart_item ci
        JOIN product_variant pv ON ci.variant_id = pv.variant_id
        WHERE ci.cart_id = v_cart_id
        FOR UPDATE OF pv
    ) LOOP
        -- Snapshot unit price at purchase instant
        INSERT INTO order_item (order_id, variant_id, quantity, unit_price)
        VALUES (p_order_id, v_item.variant_id, v_item.quantity, v_item.price);

        -- Decrement inventory
        UPDATE product_variant 
        SET stock_quantity = GREATEST(0, stock_quantity - v_item.quantity)
        WHERE variant_id = v_item.variant_id;
    END LOOP;

    -- 6. Insert Initial Audit History
    INSERT INTO order_status_history (order_id, changed_by_staff_id, previous_status, new_status)
    VALUES (p_order_id, NULL, NULL, 'PLACED');

    -- 7. Flush Active Cart Items
    DELETE FROM cart_item WHERE cart_id = v_cart_id;
END;
$$;
```

## 6. Mandatory Analytical Reports

### Report 1: Quarterly Sales Report for a Given Year

```
SELECT 
    EXTRACT(QUARTER FROM o.order_date) AS order_quarter,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COALESCE(SUM(oi.quantity * oi.unit_price), 0.00) AS total_revenue
FROM orders o
JOIN order_item oi ON o.order_id = oi.order_id
WHERE EXTRACT(YEAR FROM o.order_date) = 2026 
  AND o.payment_status = 'PAID'
GROUP BY EXTRACT(QUARTER FROM o.order_date)
ORDER BY order_quarter;
```

### Report 2: Top-Selling Products in a Given Period

```
SELECT 
    p.product_id,
    p.title,
    pv.sku,
    SUM(oi.quantity) AS total_units_sold,
    SUM(oi.quantity * oi.unit_price) AS total_generated_revenue
FROM order_item oi
JOIN product_variant pv ON oi.variant_id = pv.variant_id
JOIN product p ON pv.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_date BETWEEN '2026-01-01' AND '2026-09-01'
  AND o.payment_status = 'PAID'
GROUP BY p.product_id, p.title, pv.sku
ORDER BY total_units_sold DESC
LIMIT 10;
```

### Report 3: Category-Wise Total Number of Orders

```
SELECT 
    c.category_id,
    c.category_name,
    COUNT(DISTINCT o.order_id) AS total_orders
FROM category c
JOIN product_category pc ON c.category_id = pc.category_id
JOIN product p ON pc.product_id = p.product_id
JOIN product_variant pv ON p.product_id = pv.product_id
JOIN order_item oi ON pv.variant_id = oi.variant_id
JOIN orders o ON oi.order_id = o.order_id
GROUP BY c.category_id, c.category_name
ORDER BY total_orders DESC;
```

### Report 4: Delivery Time Estimates for Upcoming Orders

```
SELECT 
    o.order_id,
    o.order_date,
    tc.city_name,
    tc.city_type,
    o.delivery_lead_time_days,
    o.estimated_delivery_date,
    o.order_status
FROM orders o
JOIN texas_city tc ON o.city_id = tc.city_id
WHERE o.order_status NOT IN ('DELIVERED', 'CANCELLED')
ORDER BY o.estimated_delivery_date ASC;
```

### Report 5: Customer-Wise Order Summary and Payment Status

```
SELECT 
    c.customer_id,
    c.full_name,
    c.email,
    COUNT(o.order_id) AS total_orders,
    COALESCE(SUM(oi.quantity * oi.unit_price), 0.00) AS total_expenditure,
    COUNT(CASE WHEN o.payment_status = 'PAID' THEN 1 END) AS successful_payments,
    COUNT(CASE WHEN o.payment_status = 'PENDING' THEN 1 END) AS pending_payments
FROM customer c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN order_item oi ON o.order_id = oi.order_id
GROUP BY c.customer_id, c.full_name, c.email
ORDER BY total_orders DESC;
```
-- ==========================================================
-- Migration 05: Analytics Views & Reporting (Analytics Blueprint)
-- ==========================================================

CREATE OR REPLACE VIEW v_sales_by_city AS
SELECT 
    tc.city_id,
    tc.city_name,
    tc.city_type,
    COUNT(o.order_id) AS total_orders,
    COALESCE(SUM(o.total_amount), 0.00) AS gross_revenue,
    COALESCE(AVG(o.total_amount), 0.00) AS avg_order_value
FROM TEXAS_CITY tc
LEFT JOIN ORDERS o ON tc.city_id = o.shipping_city_id
GROUP BY tc.city_id, tc.city_name, tc.city_type;

CREATE OR REPLACE VIEW v_top_products AS
SELECT 
    p.product_id,
    p.name AS product_name,
    p.sku,
    c.name AS category_name,
    p.price,
    p.stock_quantity,
    COALESCE(SUM(oi.quantity), 0) AS units_sold,
    COALESCE(SUM(oi.line_total), 0.00) AS total_revenue
FROM PRODUCTS p
LEFT JOIN CATEGORIES c ON p.category_id = c.category_id
LEFT JOIN ORDER_ITEMS oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name, p.sku, c.name, p.price, p.stock_quantity;

CREATE OR REPLACE VIEW v_category_performance AS
SELECT 
    c.category_id,
    c.name AS category_name,
    COUNT(DISTINCT p.product_id) AS product_count,
    COALESCE(SUM(oi.quantity), 0) AS total_units_sold,
    COALESCE(SUM(oi.line_total), 0.00) AS total_revenue
FROM CATEGORIES c
LEFT JOIN PRODUCTS p ON c.category_id = p.category_id
LEFT JOIN ORDER_ITEMS oi ON p.product_id = oi.product_id
GROUP BY c.category_id, c.name;

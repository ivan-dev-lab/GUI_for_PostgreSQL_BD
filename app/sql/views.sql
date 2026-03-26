CREATE OR REPLACE VIEW v_order_costs AS
SELECT
    po.id AS order_number,
    c.contract_number,
    c.customer_name,
    c.object_name,
    s.name AS supplier_name,
    CONCAT_WS(' ', f.name, COALESCE('(' || f.variety || ')', '')) AS flower_name,
    po.quantity,
    po.unit_price_snapshot,
    po.line_amount,
    c.price_coefficient,
    (po.line_amount * c.price_coefficient) AS final_amount,
    po.order_date,
    po.planned_delivery_date,
    po.actual_delivery_date,
    po.status
FROM purchase_orders po
JOIN contracts c ON c.id = po.contract_id
JOIN flowers f ON f.id = po.flower_id
JOIN suppliers s ON s.id = f.supplier_id;

CREATE OR REPLACE VIEW v_contract_totals AS
SELECT
    c.contract_number,
    c.customer_name,
    c.object_name,
    COUNT(po.id) AS orders_count,
    COALESCE(SUM(po.line_amount), 0) AS total_amount_without_coefficient,
    c.price_coefficient,
    (COALESCE(SUM(po.line_amount), 0) * c.price_coefficient) AS total_amount_with_coefficient
FROM contracts c
LEFT JOIN purchase_orders po ON po.contract_id = c.id
GROUP BY c.id;

CREATE OR REPLACE VIEW v_supplier_orders AS
SELECT
    s.name AS supplier_name,
    COUNT(po.id) AS orders_count,
    COALESCE(SUM(po.quantity), 0) AS total_quantity,
    COALESCE(SUM(po.line_amount), 0) AS total_purchase_amount
FROM suppliers s
LEFT JOIN flowers f ON f.supplier_id = s.id
LEFT JOIN purchase_orders po ON po.flower_id = f.id
GROUP BY s.id;

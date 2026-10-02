WITH source_orders AS (
    SELECT * FROM {{ source('thelook_ecommerce', 'order_items') }}
)
SELECT
    FARM_FINGERPRINT(CAST(id AS STRING)) AS sk_venta,
    id AS order_item_id,
    order_id,
    FARM_FINGERPRINT(CAST(user_id AS STRING)) AS fk_cliente,
    FARM_FINGERPRINT(CAST(product_id AS STRING)) AS fk_producto,
    FORMAT_DATE('%Y%m%d', DATE(created_at)) AS fk_fecha,
    sale_price AS monto_venta,
    status AS estado_orden
FROM source_orders
WHERE status != 'Cancelled'
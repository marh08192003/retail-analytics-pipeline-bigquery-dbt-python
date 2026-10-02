WITH source_products AS (
    SELECT * FROM {{ source('thelook_ecommerce', 'products') }}
)
SELECT
    FARM_FINGERPRINT(CAST(id AS STRING)) AS sk_producto,
    id AS product_id,
    name AS product_name,
    category,
    brand,
    retail_price
FROM source_products
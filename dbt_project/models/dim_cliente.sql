WITH source_users AS (
    SELECT * FROM {{ source('thelook_ecommerce', 'users') }}
)
SELECT
    FARM_FINGERPRINT(CAST(id AS STRING)) AS sk_cliente,
    id AS customer_id,
    CONCAT(first_name, ' ', last_name) AS customer_name,
    email,
    gender,
    country,
    city
FROM source_users
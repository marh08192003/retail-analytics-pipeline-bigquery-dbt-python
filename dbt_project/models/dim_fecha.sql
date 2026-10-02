WITH fechas AS (
    SELECT 
        FORMAT_DATE('%Y%m%d', fecha) AS sk_fecha,
        fecha AS fecha_completa,
        EXTRACT(YEAR FROM fecha) AS anio,
        EXTRACT(MONTH FROM fecha) AS mes,
        FORMAT_DATE('%B', fecha) AS nombre_mes,
        EXTRACT(DAYOFWEEK FROM fecha) AS dia_semana,
        CASE WHEN EXTRACT(DAYOFWEEK FROM fecha) IN (1, 7) THEN TRUE ELSE FALSE END AS es_fin_semana
    FROM UNNEST(GENERATE_DATE_ARRAY('2020-01-01', '2026-12-31', INTERVAL 1 DAY)) AS fecha
)
SELECT * FROM fechas
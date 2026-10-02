# Proyecto dbt Core - BigQuery Google Trends

Este proyecto dbt transforma y analiza los datos públicos de **Google Trends** hospedados en **Google Cloud BigQuery Sandbox** como parte del entregable práctico de la ruta de aprendizaje de Data Engineering.

---

## Requisitos Previos

* Python 3.8+
* Una cuenta en Google Cloud Platform (GCP) con un proyecto activo en BigQuery Sandbox.
* Cuenta de servicio en GCP con la clave descargada en formato `.json` y los permisos:
  * `BigQuery User`
  * `BigQuery Data Editor`
  * `BigQuery Job User`

---

## Configuración e Instalación

### 1. Clona/Abre el proyecto e instala dependencias
```bash
pip install dbt-bigquery
```

### 2. Configura tu perfil de dbt (`profiles.yml`)
Asegúrate de tener tu archivo `~/.dbt/profiles.yml` configurado apuntando a tu proyecto de GCP:

```yaml
dbt_prueba:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: practica-510016
      dataset: google_trends
      threads: 4
      keyfile: /ruta/a/tu/practica-510016-37faa2ea8069.json
      timeout_seconds: 300
      priority: interactive
```

---

##  Modelos Incluidos

* **`my_first_dbt_model.sql`**: Consulta los datos del dataset público `bigquery-public-data.google_trends.top_terms`, filtrando los 10 términos de búsqueda más populares a partir de 2024 y creando una vista persistente en el dataset `practica-510016.google_trends`.

---

##  Comandos Útiles de Ejecución

Probar la conexión con BigQuery:
```bash
dbt debug
```

Ejecutar las transformaciones y crear las vistas/tablas en BigQuery:
```bash
dbt run
```

Probar el modelo (si hay pruebas declaradas):
```bash
dbt test
```

Generar y servir la documentación local del proyecto dbt:
```bash
dbt docs generate
dbt docs serve
```
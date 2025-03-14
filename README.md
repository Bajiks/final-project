# TP Final - Certificación de MLOps - ITBA

Este repositorio contiene el proyecto final desarrollado como parte de la Certificación de MLOps del ITBA.

## Descripción

El proyecto implementa un sistema recomendador que integra herramientas y tecnologías modernas para la orquestación, transformación y seguimiento de experimentos en Machine Learning. Entre las principales tecnologías se encuentran:

- **Dagster**: Orquestación y ejecución de pipelines de datos.
- **DBT**: Transformación y modelado de datos.
- **MLflow**: Gestión y seguimiento de experimentos de Machine Learning.
- **Airbyte**: Ingesta de datos desde diversas fuentes.

## Estructura del Proyecto

```
.
├── .env
├── .gitignore
├── README.md
├── dagster_home/
├── db_postgres/
├── logs/
├── mlartifacts/
├── mlflow_data/
├── mlruns/
└── recommender_system/
    ├── ...
```

## Exportar variables de entorno desde .env

set -o allexport && source .env && set +o allexport

## Ejecución de Airbyte (servidor local)

Ejecutar desde el directorio raíz del proyecto:

  abctl local install

## Ejecución de mlflow (servidor local) persistente en postgresql (servidor local)

Ejecutar desde el directorio recommender_system:

  mlflow ui --backend-store-uri \
  postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST/$MLFLOW_POSTGRES_DB

## Ejecución de dagster (servidor local)

Ejecutar desde el directorio recommender_system:

  dagster dev

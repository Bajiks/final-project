from dagster import Definitions, define_asset_job, AssetSelection
from recommender_system.configs import job_training_config, job_dbt_config, job_data_config
from dagster_airbyte import AirbyteResource, load_assets_from_airbyte_instance
from recommender_system.assets import recommender_assets, dbt_assets
from recommender_system.dbt_resource import dbt_resource
from .resources import dbt_io_manager, keras_model_io_manager
from dagster_mlflow import mlflow_tracking
from recommender_system.configs import mlflow_resource_config

airbyte_assets = load_assets_from_airbyte_instance(
    AirbyteResource(
        host="localhost",
        port="8000",
        username="dbajikr@gmail.com",
        password="1234",
        request_timeout=800,
    ),
    key_prefix="airbyte"
)

all_assets = [airbyte_assets, *recommender_assets, *dbt_assets]

airbyte_job = define_asset_job(
    name="get_airbyte_data",
    selection=AssetSelection.groups("airbyte"),
    config=job_data_config
)

dbt_job = define_asset_job(
    name="dbt_job",
    selection=AssetSelection.groups("dbt_assets"),
)

only_training_job = define_asset_job(
    name="only_training",
    selection=AssetSelection.groups("recommender"),
    config=job_training_config
)

combined_job = define_asset_job(
    name="airbyte_dbt_training",
    selection=AssetSelection.all(),
    config={**job_data_config, **job_dbt_config, **job_training_config}
)

defs = Definitions(
    assets=all_assets,
    jobs=[airbyte_job, only_training_job, dbt_job, combined_job],
    resources={
        "dbt": dbt_resource,
        "io_manager": dbt_io_manager,
        "mlflow": mlflow_tracking.configured(mlflow_resource_config),
        "keras_io_manager": keras_model_io_manager,
    }
)

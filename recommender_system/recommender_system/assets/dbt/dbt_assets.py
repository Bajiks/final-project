from dagster import AssetExecutionContext
from dagster_dbt import dbt_assets, DbtCliResource

from recommender_system.project import dbt_project

@dbt_assets(
    manifest=dbt_project.manifest_path
)
def dbt_sources(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["run"], context=context).stream()

from pathlib import Path
from dagster_dbt import DbtProject

dbt_project = DbtProject(
  project_dir=Path(__file__).parent.joinpath("db_postgres").resolve(),
)

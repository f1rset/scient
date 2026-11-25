"""Read only named serving tables with native parameter binding."""

import os
import re

from databricks import sql
from databricks.sdk.core import Config, oauth_service_principal


TABLES = {
    "topic_overview", "topic_trends", "emerging_topics", "indicator_explanations", "related_topics"
}


def table_name(table):
    if table not in TABLES:
        raise ValueError("Unknown Serving table")
    parts = [os.getenv("RESEARCH_CATALOG", ""), os.getenv("RESEARCH_SERVING_SCHEMA", "serving"), table]
    if any(not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", part) for part in parts):
        raise ValueError("Set valid RESEARCH_CATALOG and RESEARCH_SERVING_SCHEMA app variables")
    return ".".join(f"`{part}`" for part in parts)


def query(table, statement, parameters=None):
    target = table_name(table)
    warehouse = os.getenv("DATABRICKS_WAREHOUSE_ID")
    if not warehouse:
        raise ValueError("Attach the research-warehouse SQL resource")
    config = Config()
    with sql.connect(
        server_hostname=config.host.removeprefix("https://").rstrip("/"),
        http_path=f"/sql/1.0/warehouses/{warehouse}",
        credentials_provider=lambda: oauth_service_principal(config),
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(statement.format(table=target), parameters or {})
            return [row.asDict() for row in cursor.fetchall()]

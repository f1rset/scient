"""Minimal Unity Catalog DDL and atomic single-table writes."""

from research_landscape.constants import CONTRACTS


def initialize(spark, settings):
    for layer in settings.values["schemas"]:
        spark.sql(f"CREATE SCHEMA IF NOT EXISTS {settings.schema(layer)}")
    for key, (ddl, _, _) in CONTRACTS.items():
        spark.sql(f"CREATE TABLE IF NOT EXISTS {settings.table(key)} ({ddl}) USING DELTA")


def merge(spark, target, frame, keys):
    from uuid import uuid4

    view = f"batch_{uuid4().hex}"
    frame.createOrReplaceTempView(view)
    predicate = " AND ".join(f"target.`{key}` = source.`{key}`" for key in keys)
    try:
        spark.sql(f"""
            MERGE INTO {target} AS target
            USING {view} AS source ON {predicate}
            WHEN MATCHED THEN UPDATE SET *
            WHEN NOT MATCHED THEN INSERT *
        """)
    finally:
        spark.catalog.dropTempView(view)


def overwrite(spark, settings, key, frame):
    target = settings.table(key)
    columns = spark.table(target).columns
    frame.select(*columns).write.mode("overwrite").saveAsTable(target)

"""OpenAlex work identifiers and latest-record normalization."""

import re


def normalize_id(value, prefix):
    match = re.fullmatch(
        rf"(?:https://openalex\.org/)?({prefix}[0-9]+)", str(value).strip(), re.IGNORECASE
    )
    if not match:
        raise ValueError(f"Invalid OpenAlex {prefix} identifier")
    return match[1].upper()


def normalized(column, prefix):
    from pyspark.sql import functions as f

    result = f.regexp_extract(f.trim(column), rf"(?i)^(?:https://openalex\.org/)?({prefix}[0-9]+)$", 1)
    return f.when(result != "", f.upper(result))


def latest(frame):
    from pyspark.sql import Window, functions as f

    order = Window.partitionBy("source_id").orderBy(
        f.desc("ingested_at"), f.desc("run_id"), f.desc("payload")
    )
    return frame.withColumn("_row", f.row_number().over(order)).where("_row = 1").drop("_row")


def parse(frame):
    from pyspark.sql import functions as f

    schema = """
        title STRING, publication_year INT, cited_by_count BIGINT,
        primary_topic STRUCT<id:STRING>, topics ARRAY<STRUCT<id:STRING,score:DOUBLE>>,
        referenced_works ARRAY<STRING>
    """
    return latest(frame).select("source_id", f.from_json("payload", schema).alias("work"))


def normalize_works(frame):
    from pyspark.sql import functions as f

    return parse(frame).select(
        f.col("source_id").alias("work_id"), "work.title", "work.publication_year",
        normalized(f.col("work.primary_topic.id"), "T").alias("primary_topic_id"),
        "work.cited_by_count",
        f.array_distinct(f.filter(
            f.transform("work.referenced_works", lambda value: normalized(value, "W")),
            lambda value: value.isNotNull(),
        )).alias("referenced_works"),
    )

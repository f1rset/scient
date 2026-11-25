from research_landscape.transformations.works import latest, normalized, parse


def normalize_topics(frame):
    from pyspark.sql import functions as f

    hierarchy = "STRUCT<id:STRING,display_name:STRING>"
    levels = ("subfield", "field", "domain")
    schema = "display_name STRING, " + ", ".join(f"{level} {hierarchy}" for level in levels)
    return latest(frame).select(
        f.col("source_id").alias("topic_id"), f.from_json("payload", schema).alias("topic")
    ).select(
        "topic_id", f.col("topic.display_name").alias("topic_name"),
        *[
            col
            for level in levels
            for col in (
                f.regexp_extract(f.col(f"topic.{level}.id"), r"([0-9]+)$", 1).alias(f"{level}_id"),
                f.col(f"topic.{level}.display_name").alias(f"{level}_name"),
            )
        ],
    )


def work_topics(frame, works):
    from pyspark.sql import functions as f

    assignments = parse(frame).select(
        f.col("source_id").alias("work_id"), f.explode("work.topics").alias("assignment")
    ).select(
        "work_id", normalized(f.col("assignment.id"), "T").alias("topic_id"),
        f.col("assignment.score").alias("relevance"),
    ).where("topic_id IS NOT NULL")
    primary = works.select(
        "work_id", f.col("primary_topic_id").alias("topic_id")
    ).where("topic_id IS NOT NULL")
    return assignments.withColumn("is_primary", f.lit(False)).unionByName(
        primary.withColumn("is_primary", f.lit(True)).withColumn("relevance", f.lit(None).cast("double"))
    ).groupBy("work_id", "topic_id").agg(
        f.max("is_primary").alias("is_primary"), f.max("relevance").alias("relevance")
    )


def primary_assignments(works, topics):
    return works.join(topics, works.primary_topic_id == topics.topic_id).select(
        "work_id", "topic_id", "field_id", "publication_year"
    )

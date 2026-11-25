"""Calendar-aligned growth measures using only trailing observations."""


def relative_change(current, previous):
    return None if previous is None or previous <= 0 else (current - previous) / previous


def annual_metrics(context, *, by_topic):
    from pyspark.sql import functions as f
    from research_landscape.transformations.topics import primary_assignments

    keys = ["topic_id", "field_id"] if by_topic else ["field_id"]
    values = context.settings.values
    assignments = primary_assignments(context.read("silver.works"), context.read("silver.topics"))
    counts = assignments.groupBy(*keys, "publication_year").count()
    years = counts.groupBy(*keys).agg(f.min("publication_year").alias("first_year"))
    grid = years.select(
        *keys, f.explode(f.sequence("first_year", f.lit(values["end_year"]))).alias("publication_year")
    )
    return grid.join(counts, keys + ["publication_year"], "left").select(
        *keys, "publication_year", f.coalesce("count", f.lit(0)).alias("publication_count")
    )


def indicators(topic, field, *, window, complete_through):
    from pyspark.sql import Window, functions as f

    years = Window.partitionBy("topic_id").orderBy("publication_year")

    def divide(numerator, denominator):
        return f.when(denominator > 0, numerator / denominator)

    field_counts = field.withColumnRenamed("publication_count", "field_count")
    frame = topic.join(field_counts, ["field_id", "publication_year"], "left").where(
        f.col("publication_year") <= complete_through
    )
    current = f.col("publication_count")
    previous = f.lag(current).over(years)
    historical = f.lag(current, window).over(years)
    field_count = f.col("field_count")
    prior_field = f.lag(field_count).over(years)
    relative = divide(current - previous, previous)
    frame = (frame.withColumn("absolute_growth", current - previous)
             .withColumn("relative_growth", relative)
             .withColumn("cagr", f.pow(divide(current, historical), 1 / window) - 1)
             .withColumn("topic_share", divide(current, field_count))
             .withColumn("field_adjusted_growth", relative - divide(field_count - prior_field, prior_field)))
    relative = f.col("relative_growth")
    share = f.col("topic_share")
    return (frame.withColumn("acceleration", relative - f.lag(relative).over(years))
            .withColumn("volatility", f.stddev_samp(relative).over(years.rowsBetween(1 - window, 0)))
            .withColumn("share_change", share - f.lag(share).over(years))
            .drop("field_count"))

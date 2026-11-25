"""Persist quality outcomes before failing a critical check."""

from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc)


def record(context, name, failures, severity="critical"):
    context.append(
        "ops.data_quality_results",
        (context.run_id, context.stage, name, severity, failures, now()),
    )
    if failures and severity == "critical":
        raise ValueError(f"{name} failed for {failures} records")


def distinct_keys(context, frame, *keys):
    from functools import reduce
    from operator import or_
    from pyspark.sql import functions as f

    record(context, "missing_keys", frame.where(reduce(or_, [f.col(key).isNull() for key in keys])).count())
    duplicates = frame.groupBy(*keys).count().where("count > 1").count()
    record(context, "duplicate_keys", duplicates)


def count_change(context, table_key, frame):
    from pyspark.sql import functions as f

    current = frame.count()
    checks = context.read("ops.data_quality_results")
    previous = checks.where(
        (f.col("stage") == context.stage) & (f.col("check_name") == f"row_count:{table_key}")
    ).orderBy(f.desc("checked_at")).select("failures").first()
    context.append("ops.data_quality_results", (
        context.run_id, context.stage, f"row_count:{table_key}", "info", current, now()
    ))
    if previous and previous.failures:
        record(context, f"unexpected_change:{table_key}", int(abs(current / previous.failures - 1) > 0.5), "warning")
    return current

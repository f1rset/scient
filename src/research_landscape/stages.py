"""Executable pipeline stages and explicit boundaries for unfinished analyses."""

from research_landscape.analytics.growth import annual_metrics, indicators
from research_landscape.ingestion import corpus_id, ingest
from research_landscape.transformations.citations import citation_edges
from research_landscape.transformations.topics import normalize_topics, work_topics
from research_landscape.transformations.works import normalize_works
from research_landscape.constants import CONTRACTS
from research_landscape.utils.validation import count_change, distinct_keys, record

PENDING = {
    "emergence_scores": "Fit per-year component scaling and score eligible topics",
    "indicator_comparison": "Compare component and baseline rankings",
    "historical_evaluation": "Build cutoff-scoped features and independent future outcomes",
    "evaluation_summary": "Summarize rank performance at each cutoff and horizon",
    "publish_rankings": "Publish rankings and score contributions",
    "topic_cooccurrence": "Aggregate distinct within-work topic pairs",
    "topic_citation_network": "Aggregate directed citations between primary topics",
    "network_metrics": "Compute degree and weighted degree",
    "community_detection": "Fit seeded communities on a bounded graph",
    "publish_related_topics": "Publish weighted neighbors for the app",
}


def active_works(context):
    from pyspark.sql import functions as f

    return context.read("bronze.works_raw").where(f.col("corpus") == corpus_id(context.settings))


def profile_bronze(context):
    for key, frame in {
        "bronze.works_raw": active_works(context),
        "bronze.topics_raw": context.read("bronze.topics_raw"),
    }.items():
        record(context, f"empty:{key}", int(count_change(context, key, frame) == 0))


def validate_silver(context):
    from pyspark.sql import functions as f

    works = context.read("silver.works")
    topics = context.read("silver.topics")
    assignments = context.read("silver.work_topics")
    start = context.settings.values["start_year"]
    end = context.settings.values["end_year"]
    for key, frame in (("silver.works", works), ("silver.topics", topics), ("silver.work_topics", assignments)):
        count_change(context, key, frame)
        distinct_keys(context, frame, *CONTRACTS[key][1].split(", "))
    record(context, "empty_works", int(not works.limit(1).count()))
    year = f.col("publication_year")
    record(context, "invalid_years", works.where(year.isNull() | ~year.between(start, end)).count())
    record(context, "missing_primary_topic", works.where("primary_topic_id IS NULL").count(), "warning")
    record(context, "missing_title", works.where("title IS NULL").count(), "warning")
    record(context, "unknown_work", assignments.join(works, "work_id", "left_anti").count())
    record(context, "unknown_primary_topic",
           assignments.where("is_primary").join(topics, "topic_id", "left_anti").count())
    record(context, "unknown_secondary_topic",
           assignments.where("NOT is_primary").join(topics, "topic_id", "left_anti").count(), "warning")
    record(context, "missing_field", topics.where("field_id IS NULL OR field_id = ''").count())


def growth(context):
    from pyspark.sql import functions as f

    values = context.settings.values
    result = indicators(
        context.read("gold.topic_year_metrics"), context.read("gold.field_year_metrics"),
        window=values["growth_window"], complete_through=values["complete_through"],
    )
    share = f.col("topic_share")
    record(context, "invalid_topic_share", result.where(f.isnan(share) | (share < 0) | (share > 1)).count())
    context.publish("gold.topic_growth_indicators", result)


def overview(context):
    from pyspark.sql import functions as f

    totals = context.read("gold.topic_year_metrics").groupBy("topic_id").agg(
        f.sum("publication_count").alias("publication_count")
    )
    return context.read("silver.topics").join(totals, "topic_id")


def trends(context):
    # Join complete-year indicators to activity so incomplete years still display counts.
    return context.read("gold.topic_year_metrics").join(
        context.read("gold.topic_growth_indicators").select(
            "topic_id", "publication_year", "relative_growth", "topic_share"
        ), ["topic_id", "publication_year"], "left"
    )


def execute(context):
    stage = context.stage
    if stage == "build_citation_edges" and not context.settings.values["network"]["enabled"]:
        raise ValueError("Set network.enabled to true to run the optional network workflow")
    if stage in PENDING:
        raise NotImplementedError(PENDING[stage])
    if stage in {"ingest_works", "ingest_topics"}:
        ingest(context, stage.removeprefix("ingest_"))
        return
    if stage == "profile_raw_data":
        profile_bronze(context)
        return
    if stage == "validate_silver":
        validate_silver(context)
        return
    if stage == "growth_indicators":
        growth(context)
        return
    if stage == "temporal_analysis":
        context.read("gold.topic_growth_indicators").orderBy("publication_year", "topic_id").show(20)
        return

    stages = {
        "normalize_topics": ("silver.topics", lambda: normalize_topics(context.read("bronze.topics_raw"))),
        "normalize_works": ("silver.works", lambda: normalize_works(active_works(context))),
        "build_work_topics": ("silver.work_topics", lambda: work_topics(active_works(context), context.read("silver.works"))),
        "build_citation_edges": ("silver.citation_edges", lambda: citation_edges(context.read("silver.works"))),
        "topic_year_metrics": ("gold.topic_year_metrics", lambda: annual_metrics(context, by_topic=True)),
        "field_year_metrics": ("gold.field_year_metrics", lambda: annual_metrics(context, by_topic=False)),
        "publish_topic_overview": ("serving.topic_overview", lambda: overview(context)),
        "publish_topic_trends": ("serving.topic_trends", lambda: trends(context)),
    }
    target, transform = stages[stage]
    context.publish(target, transform())

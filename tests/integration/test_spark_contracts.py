from datetime import datetime
import json
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_SPARK_TESTS") != "1", reason="Opt in with RUN_SPARK_TESTS=1 and local PySpark"
)


@pytest.fixture(scope="module")
def spark():
    from pyspark.sql import SparkSession

    session = SparkSession.builder.master("local[2]").appName("research-contract-tests").getOrCreate()
    yield session
    session.stop()


def test_latest_primary_and_multi_topic_relationships(spark):
    from research_landscape.transformations.citations import citation_edges
    from research_landscape.transformations.topics import primary_assignments, work_topics
    from research_landscape.transformations.works import normalize_id, normalize_works

    records = json.loads((Path(__file__).parents[1] / "fixtures/works.json").read_text())
    bronze = spark.createDataFrame(
        [(normalize_id(row["id"], "W"), datetime(2025, 1, 3 - i), str(i), json.dumps(row))
         for i, row in enumerate(records)],
        "source_id STRING, ingested_at TIMESTAMP, run_id STRING, payload STRING",
    )
    works = normalize_works(bronze)
    assert works.count() == 2
    assert works.where("work_id = 'W1'").first().publication_year == 2020
    links = {(row.work_id, row.topic_id): row for row in work_topics(bronze, works).collect()}
    assert links["W1", "T1"].is_primary
    assert links["W1", "T2"].relevance == 0.6
    assert not links["W1", "T2"].is_primary
    taxonomy = spark.createDataFrame([("T1", "17"), ("T2", "17")], "topic_id STRING, field_id STRING")
    assert primary_assignments(works, taxonomy).count() == 2
    flags = {row.cited_work_id: row.cited_in_corpus for row in citation_edges(works).collect()}
    assert flags == {"W2": True, "W3": False}


def test_growth_and_feature_cutoff(spark):
    from research_landscape.analytics.evaluation import feature_rows
    from research_landscape.analytics.growth import indicators

    topic = spark.createDataFrame(
        [("T1", "17", 2018, 0), ("T1", "17", 2019, 5), ("T1", "17", 2020, 10)],
        "topic_id STRING, field_id STRING, publication_year INT, publication_count BIGINT",
    )
    field = spark.createDataFrame(
        [("17", 2018, 10), ("17", 2019, 20), ("17", 2020, 30)],
        "field_id STRING, publication_year INT, publication_count BIGINT",
    )
    result = indicators(feature_rows(topic, 2019), feature_rows(field, 2019), window=2, complete_through=2019)
    data = {r.publication_year: r for r in result.collect()}
    assert set(data) == {2018, 2019}
    assert data[2019].absolute_growth == 5
    assert data[2019].relative_growth is None
    assert data[2019].topic_share == 0.25

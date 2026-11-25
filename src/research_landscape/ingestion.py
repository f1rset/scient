"""Write Bronze pages before advancing the cursor. Replaying a page is safe."""

import json

from research_landscape.openalex.client import OpenAlexClient
from research_landscape.openalex.filters import fingerprint, work_filters
from research_landscape.openalex.pagination import pages
from research_landscape.transformations.works import normalize_id
from research_landscape.utils.delta import merge
from research_landscape.utils.validation import now


def corpus_id(settings):
    return fingerprint(settings.profile, work_filters(settings.values), settings.values["max_works"])


def ingest(context, entity):
    from pyspark.sql import functions as f

    p = context.parameters
    v = context.settings.values
    if not p["secret_scope"] or not p["secret_key"]:
        raise ValueError("Set the OpenAlex secret scope and key before running ingestion")
    works = entity == "works"
    if works and not any(v[key] for key in ("fields", "subfields", "topics")):
        raise ValueError("Select at least one OpenAlex field, subfield or topic before ingesting works")
    since = p["updated_since"] if works and p["ingestion_mode"] == "incremental" else ""
    filters = work_filters(v, since) if works else ""
    cap = v["max_works"] if works else None
    if since and cap is not None:
        raise ValueError("Incremental works ingestion requires an uncapped initial corpus")
    corpus = corpus_id(context.settings)
    stream = fingerprint(entity, corpus if works else "", filters, v["api"]["page_size"])
    extraction = p["extraction_id"] or context.run_id
    checkpoint_key = "ops.ingestion_checkpoints"
    checkpoints = context.read(checkpoint_key)
    state = checkpoints.where(
        (f.col("stream_id") == stream) & (f.col("extraction_id") == extraction)
    ).first()
    if state and state.complete:
        return
    api = v["api"]
    client = OpenAlexClient(context.dbutils.secrets.get(p["secret_scope"], p["secret_key"]),
                            timeout_seconds=api["timeout_seconds"], max_attempts=api["max_attempts"],
                            min_interval_seconds=api["min_interval_seconds"])

    def fetch(params):
        if filters:
            params["filter"] = filters
        return client.fetch(entity, params)

    key = f"bronze.{entity}_raw"
    for items, cursor, count, complete in pages(
        fetch, cursor=state.next_cursor if state else "*", records=state.records if state else 0,
        max_records=cap, max_requests=api["max_requests"], page_size=api["page_size"],
    ):
        batch = {}
        timestamp = now()
        for item in items:
            source_id = normalize_id(item.get("id"), "W" if works else "T")
            row = (source_id, timestamp, context.run_id, json.dumps(item, ensure_ascii=False))
            batch[source_id] = row + (corpus,) if works else row
        if batch:
            frame = context.spark.createDataFrame(list(batch.values()), context.read(key).schema)
            keys = ("corpus", "source_id") if works else ("source_id",)
            merge(context.spark, context.settings.table(key), frame, keys)
        frame = context.spark.createDataFrame(
            [(stream, extraction, cursor, count, complete, timestamp)], checkpoints.schema
        )
        merge(context.spark, context.settings.table(checkpoint_key), frame, ("stream_id", "extraction_id"))
        context.log.info("OpenAlex %s records scanned: %s (complete=%s)", entity, count, complete)
        if complete:
            return
    raise RuntimeError(f"OpenAlex {entity} page budget reached. Resume using extraction_id={extraction}")

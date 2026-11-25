"""Shared notebook setup, lifecycle events, validation and stage dispatch."""

from dataclasses import dataclass
from datetime import date
from uuid import uuid4

from research_landscape.configuration import Settings
from research_landscape.constants import CONTRACTS
from research_landscape.logging import logger
from research_landscape.utils import delta
from research_landscape.utils.validation import distinct_keys, now, record


@dataclass
class Context:
    spark: object
    dbutils: object
    settings: Settings
    parameters: dict
    stage: str

    @property
    def run_id(self):
        return self.parameters["run_id"]

    @property
    def log(self):
        return logger(__name__)

    def read(self, key):
        return self.spark.table(self.settings.table(key))

    def append(self, key, row):
        self.spark.createDataFrame([row], self.read(key).schema).write.mode("append").saveAsTable(
            self.settings.table(key)
        )

    def publish(self, key, frame):
        distinct_keys(self, frame, *CONTRACTS[key][1].split(", "))
        delta.overwrite(self.spark, self.settings, key, frame)
        self.log.info("Published %s", self.settings.table(key))


def validate_tables(context):
    for key, (ddl, _, _) in CONTRACTS.items():
        # Spark resolves the registered table and parses its declared schema.
        actual = [(field.name, field.dataType) for field in context.read(key).schema]
        expected = [(field.name, field.dataType) for field in context.spark.createDataFrame([], ddl).schema]
        if actual != expected:
            raise ValueError(f"Schema differs from contract for {context.settings.table(key)}")


def run_notebook(stage, spark, dbutils, root):
    from research_landscape.stages import execute

    defaults = {
        "catalog": "", "profile": "development", "secret_scope": "", "secret_key": "",
        "extraction_id": "", "ingestion_mode": "full", "updated_since": "", "run_id": "",
    }
    for key, default in defaults.items():
        dbutils.widgets.text(key, default)
    parameters = {key: dbutils.widgets.get(key).strip() for key in defaults}
    parameters["run_id"] = parameters["run_id"] or uuid4().hex
    settings = Settings.load(root, parameters["catalog"], parameters["profile"])
    mode = parameters["ingestion_mode"]
    if mode not in ("full", "incremental"):
        raise ValueError("ingestion_mode must be full or incremental")
    if mode == "incremental":
        date.fromisoformat(parameters["updated_since"])
    context = Context(spark, dbutils, settings, parameters, stage)
    if stage == "initialize_environment":
        delta.initialize(spark, settings)
    context.append("ops.pipeline_runs", (context.run_id, stage, now(), "running"))
    try:
        if stage in {"initialize_environment", "validate_configuration"}:
            validate_tables(context)
        else:
            execute(context)
    except Exception:
        try:
            context.append("ops.pipeline_runs", (context.run_id, stage, now(), "failed"))
        except Exception:
            context.log.exception("Could not record failure in the stage log")
        raise
    context.append("ops.pipeline_runs", (context.run_id, stage, now(), "succeeded"))
    context.log.info("%s succeeded (run %s)", stage, context.run_id)

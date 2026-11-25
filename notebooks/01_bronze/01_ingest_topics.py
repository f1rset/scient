# Databricks notebook source
# MAGIC %md
# MAGIC # Ingest Topics
# MAGIC Capture the current OpenAlex topic taxonomy.
# MAGIC
# MAGIC **Inputs** — Runtime configuration
# MAGIC
# MAGIC **Outputs** — bronze.topics_raw, ops.ingestion_checkpoints
# MAGIC
# MAGIC Parameters are available in the widgets. See docs/deployment.md for configuration.
# MAGIC The shared stage runner records execution status and applies stage-specific validation and persistence.

# COMMAND ----------

from pathlib import Path
import sys

dbutils.widgets.text("project_root", "")
configured_root = dbutils.widgets.get("project_root")
if configured_root and not configured_root.startswith("/Workspace/"):
    configured_root = "/Workspace/" + configured_root.lstrip("/")
root = Path(configured_root) if configured_root else Path.cwd().parents[1]
sys.path.insert(0, str(root / "src"))

from research_landscape.runtime import run_notebook

run_notebook("ingest_topics", spark, dbutils, root)

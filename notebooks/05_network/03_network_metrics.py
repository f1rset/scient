# Databricks notebook source
# MAGIC %md
# MAGIC # Network Metrics
# MAGIC Define graph degree statistics.
# MAGIC
# MAGIC **Inputs** — gold.topic_cooccurrence_edges, gold.topic_citation_edges
# MAGIC
# MAGIC **Outputs** — gold.topic_network_metrics
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

run_notebook("network_metrics", spark, dbutils, root)

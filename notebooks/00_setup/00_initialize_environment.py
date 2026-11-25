# Databricks notebook source
# MAGIC %md
# MAGIC # Initialize Environment
# MAGIC Create the schemas and Delta table contracts in an existing catalog.
# MAGIC
# MAGIC **Inputs** — Runtime configuration
# MAGIC
# MAGIC **Outputs** — All registered Delta contracts
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

run_notebook("initialize_environment", spark, dbutils, root)

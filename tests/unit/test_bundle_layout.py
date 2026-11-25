"""Check notebook entry points and task dependencies without a workspace."""

from pathlib import Path

import yaml


ROOT = Path(__file__).parents[2]


def test_bundle_notebooks_and_task_dependencies():
    bundle = yaml.safe_load((ROOT / "databricks.yml").read_text())
    assert set(bundle["targets"]) == {"development", "production"}
    notebooks = set()
    task_signatures = {}
    jobs = set()
    for path in (ROOT / "resources").glob("*.job.yml"):
        for job_key, job in yaml.safe_load(path.read_text())["resources"]["jobs"].items():
            jobs.add(job_key)
            pending = {}
            environments = {env["environment_key"] for env in job["environments"]}
            for task in job["tasks"]:
                key = task["task_key"]
                notebook = (path.parent / task["notebook_task"]["notebook_path"]).resolve()
                assert notebook.read_text().startswith("# Databricks notebook source\n")
                assert task["environment_key"] in environments
                assert key not in pending
                pending[key] = {dep["task_key"] for dep in task.get("depends_on", [])}
                notebooks.add(notebook)
                signature = dict(task)
                signature.pop("depends_on", None)
                assert task_signatures.setdefault(key, signature) == signature
            while pending:
                ready = {key for key, deps in pending.items() if not deps}
                assert ready, f"Cycle or missing dependency in {job_key}"
                pending = {key: deps - ready for key, deps in pending.items() if key not in ready}
    assert jobs == {"setup", "ingestion", "analytics", "research_pipeline", "network_analysis"}
    assert notebooks == set((ROOT / "notebooks").rglob("*.py"))

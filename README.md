# Scientific Research Landscape Explorer

Team Синевир · Mapping the Evolution of Scientific Research

This Databricks scaffold uses OpenAlex, PySpark, Delta Lake, Unity Catalog, Lakeflow Jobs, and Streamlit. The default publication period is 2015–2025. Choose the corpus filters and final collection size in the target configuration.

## Start here

1. For a workspace upload, import the source ZIP into a Databricks Workspace folder. For CLI deployment, unzip it locally and work from the folder containing `databricks.yml`.
2. Set the target catalog, OpenAlex filters, and secret identifiers. Follow [Deployment](docs/deployment.md) to validate and deploy the bundle.
3. Run setup, then a capped development ingestion. For a baseline walkthrough, execute the Silver and Gold stages through growth indicators, followed by the overview and trends publishers. These publishers can be run independently.
4. Build emergence scoring and rankings, then indicator comparison and retrospective evaluation. Connect and verify the app against the published Serving tables. Implement the optional network workflow last.

## Status

| Implemented | Pending implementation |
| --- | --- |
| Target configuration, Unity Catalog DDL, stage logs and quality records | Automated Delta and Databricks workspace integration tests |
| Bounded OpenAlex pagination, retry, replay-safe Bronze upserts and extraction checkpoints | Corpus deletion/reconciliation policies and production capacity validation |
| Silver normalization, assignments, citation edges and validation | Network aggregation, metrics, communities and related-topic publication |
| Primary-topic activity, growth, relative share and baseline overview/trends publishers | Composite scoring, rank comparison, retrospective evaluation and rankings publication |
| Streamlit page scaffolds and warehouse access through the Apps service principal | Full dashboard and application smoke test in Databricks |

Full and analytics jobs intentionally stop at `emergence_scores`. The optional network job starts with citation-edge materialization and stops at the first unfinished network stages. Pending stages raise explicit errors. For a smoke test, use setup and ingestion jobs plus the implemented notebooks described in [Deployment](docs/deployment.md).

- [Architecture and layers](docs/architecture.md)
- [Full notebook inventory, inputs, outputs and workflow DAGs](docs/orchestration.md)
- [Delta contracts, keys, producers and consumers](docs/data_model.md)
- [Methodology, limitations and outstanding decisions](docs/methodology.md)
- [Deployment and configuration](docs/deployment.md)
- [Directory tree](docs/tree.md)

## Local development

```bash
python -m pip install -e '.[test]'
python -m pytest
python -m pip install -e '.[test,spark]'
RUN_SPARK_TESTS=1 python -m pytest
```

Spark tests require a compatible Java runtime and local socket access. Test fixtures are synthetic and test runs make no OpenAlex requests.

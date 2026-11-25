# Databricks deployment

## Workspace ZIP upload

In **Workspace**, open your destination folder, choose **Import**, then select `scientific-research-landscape.zip`. Open the imported project folder and check that the 26 files under `notebooks/` are recognized as notebooks. The remaining files include the Python package, YAML configuration and bundle sources. If your workspace supports the bundle editor, open this folder as a bundle. Use the CLI path below to deploy its workflow resources. [Databricks workspace import documentation](https://docs.databricks.com/gcp/en/files/workspace-basics)

To run an imported notebook directly, attach Unity Catalog-capable Python compute with PyYAML installed. Supply its `catalog` and `profile` widgets, plus the secret widget names for ingestion. The checkout root is inferred from the notebook working directory on compatible runtimes. If needed, set `project_root` to the project's absolute `/Workspace/…` path. The first run may create widgets and stop when required values are blank. Set the widgets and rerun. Run setup before data stages.

## CLI deployment

Use a Databricks CLI that supports Asset Bundles and job environments. The jobs target serverless compute and install PyYAML through a job environment. The bundle syncs `src/` and `config/`. Notebook tasks receive the synced root through the `project_root` job parameter and import modules on the driver. Deployment requires serverless Jobs, Unity Catalog grants, and outbound HTTPS to OpenAlex on ingestion compute. [Databricks bundle job examples](https://docs.databricks.com/aws/en/dev-tools/bundles/examples)

```bash
unzip scientific-research-landscape.zip
cd scientific-research-landscape
databricks auth login --host "$DATABRICKS_HOST" --profile research
export DATABRICKS_CONFIG_PROFILE=research
export BUNDLE_VAR_catalog=YOUR_EXISTING_DEVELOPMENT_CATALOG
export BUNDLE_VAR_secret_scope=YOUR_SCOPE
export BUNDLE_VAR_secret_key=YOUR_KEY_NAME
databricks bundle validate -t development
databricks bundle deploy -t development
databricks bundle run -t development setup
databricks bundle run -t development ingestion --params extraction_id=dev-smoke-01
```

Set work filters before deployment. The secret key name points to the stored OpenAlex API key. Grant the job identity `USE CATALOG`, schema/table creation and write privileges, and secret access. For production, set a different catalog, confirm write access to the configured bundle root, review the extraction limits, and repeat validation and deployment with `-t production`.

Use the individual notebooks for a baseline smoke test. Run the two normalizers, build work topics, validate Silver, run both annual metrics stages and then growth indicators. Run the overview and trends publishers from the resulting tables. Once the pending stages are implemented, run `databricks bundle run -t development analytics` to reuse Bronze or `databricks bundle run -t development research_pipeline` for the entire core DAG. Enable the optional network job with `network.enabled` and run it after Silver is available.

## Manual configuration

| Location | Values to supply or review |
| --- | --- |
| CLI authentication | Workspace host and configuration profile |
| Bundle variables | Existing development/production catalog and Databricks secret scope/key name |
| Target configuration YAML | Choose numeric field/subfield IDs or `T…` IDs. Multiple values within a category are ORed and categories are ANDed. Review schema names, dates, complete-through year, API budgets, sample size, scoring and graph settings. |
| Job run parameters | Choose a stable `extraction_id` across resume attempts. For incremental work extraction set `ingestion_mode=incremental` and an ISO date for `updated_since`. |
| Databricks Apps | Attach the SQL warehouse resource, set catalog and Serving schema, and grant app identity access. |

### Ingestion modes and checkpoints

Full mode scans the filtered publication range and upserts latest records. It preserves older keys if an upstream work is deleted or reclassified out of the filters. Use a fresh schema/catalog for an exact rebuild pending reconciliation support. Development defaults to 2,000 scanned works. The production target has no page or publication cap by default. Select a budget after profiling and verifying the API quota.

Each extraction keeps its cursor and scanned record count. If a page budget stops the task, rerun with the same extraction ID and filter settings. Use a new ID to restart a scan. Job retries default to the same run ID when no extraction ID was supplied. The cursor advances after the Delta merge so a page can replay safely after interruption. The request limit counts logical pages per invocation. The retry policy can add HTTP attempts.

Incremental mode uses the explicit, inclusive `from_updated_date` filter for works. It requires an uncapped initial corpus and OpenAlex daily sync entitlement. Use a date overlap and stable filters and update the supplied date only after successful completion. Topics always refresh through their standalone cursor stream. [OpenAlex incremental sync](https://help.openalex.org/access/sync/)

## Databricks Apps

Create an app, attach a SQL warehouse resource with key `research-warehouse`, and grant the app service principal warehouse access. Set `RESEARCH_CATALOG` and `RESEARCH_SERVING_SCHEMA` in `app/app.yaml`. Grant the principal `USE CATALOG`, `USE SCHEMA`, and `SELECT` on the Serving tables. Deploy from the uploaded or bundle-synced `app/` workspace folder. The warehouse resource injects the warehouse ID as `DATABRICKS_WAREHOUSE_ID`. The SQL connector uses Apps OAuth credentials. [Databricks Apps warehouse resources](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/sql-warehouse)

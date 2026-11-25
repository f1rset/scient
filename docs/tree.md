# Directory tree

```text
scientific-research-landscape/
├── .gitignore
├── README.md
├── app/
│   ├── app.py
│   ├── app.yaml
│   ├── components/
│   │   ├── __init__.py
│   │   └── views.py
│   ├── pages/
│   │   ├── 01_Research_Overview.py
│   │   ├── 02_Topic_Explorer.py
│   │   ├── 03_Emerging_Topics.py
│   │   ├── 04_Indicator_Comparison.py
│   │   └── 05_Citation_Network.py
│   ├── requirements.txt
│   └── services/
│       ├── __init__.py
│       └── warehouse.py
├── config/
│   ├── default.yml
│   ├── development.yml
│   └── production.yml
├── databricks.yml
├── docs/
│   ├── architecture.md
│   ├── data_model.md
│   ├── deployment.md
│   ├── methodology.md
│   ├── orchestration.md
│   └── tree.md
├── notebooks/
│   ├── 00_setup/
│   │   ├── 00_initialize_environment.py
│   │   └── 01_validate_configuration.py
│   ├── 01_bronze/
│   │   ├── 01_ingest_topics.py
│   │   ├── 02_ingest_works.py
│   │   └── 03_profile_raw_data.py
│   ├── 02_silver/
│   │   ├── 01_normalize_topics.py
│   │   ├── 02_normalize_works.py
│   │   ├── 03_build_work_topics.py
│   │   ├── 04_build_citation_edges.py
│   │   └── 05_validate_silver.py
│   ├── 03_gold/
│   │   ├── 01_topic_year_metrics.py
│   │   ├── 02_field_year_metrics.py
│   │   ├── 03_growth_indicators.py
│   │   └── 04_emergence_scores.py
│   ├── 04_analytics/
│   │   ├── 01_temporal_analysis.py
│   │   ├── 02_indicator_comparison.py
│   │   ├── 03_historical_evaluation.py
│   │   └── 04_evaluation_summary.py
│   ├── 05_network/
│   │   ├── 01_topic_cooccurrence.py
│   │   ├── 02_topic_citation_network.py
│   │   ├── 03_network_metrics.py
│   │   └── 04_community_detection.py
│   └── 06_serving/
│       ├── 01_publish_topic_overview.py
│       ├── 02_publish_topic_trends.py
│       ├── 03_publish_rankings.py
│       └── 04_publish_related_topics.py
├── pyproject.toml
├── resources/
│   ├── analytics.job.yml
│   ├── ingestion.job.yml
│   ├── network_analysis.job.yml
│   ├── research_pipeline.job.yml
│   └── setup.job.yml
├── src/
│   └── research_landscape/
│       ├── __init__.py
│       ├── analytics/
│       │   ├── __init__.py
│       │   ├── emergence.py
│       │   ├── evaluation.py
│       │   ├── growth.py
│       │   └── networks.py
│       ├── configuration.py
│       ├── constants.py
│       ├── ingestion.py
│       ├── logging.py
│       ├── openalex/
│       │   ├── __init__.py
│       │   ├── client.py
│       │   ├── filters.py
│       │   └── pagination.py
│       ├── runtime.py
│       ├── stages.py
│       ├── transformations/
│       │   ├── __init__.py
│       │   ├── citations.py
│       │   ├── topics.py
│       │   └── works.py
│       └── utils/
│           ├── __init__.py
│           ├── delta.py
│           └── validation.py
└── tests/
    ├── fixtures/
    │   └── works.json
    ├── integration/
    │   ├── README.md
    │   └── test_spark_contracts.py
    └── unit/
        ├── test_bundle_layout.py
        └── test_foundations.py
```

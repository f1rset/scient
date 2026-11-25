# Integration tests

Run the synthetic Spark tests with `RUN_SPARK_TESTS=1 python -m pytest tests/integration` after installing the Spark extra and a compatible Java runtime.

For Delta integration, use a dedicated scratch Unity Catalog catalog. Execute setup twice and compare schemas to the contracts. Replay a synthetic page with the same logical keys, verify row counts remain stable, then run Silver stage notebooks with fixture-backed Bronze tables. Induce an invalid year and verify the warning or error row and dependent task status. The workspace integration suite remains to be automated.

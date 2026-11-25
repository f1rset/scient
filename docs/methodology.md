# Analytical methodology

## Counting and growth

One classified work contributes one publication to its primary topic and that topic's parent field. Secondary topics are preserved for network analysis. Works without a primary topic are reported and excluded from both counts. Share is the topic count divided by the count of all primary topics in that field **within the collected corpus**. A corpus scoped to particular topics can therefore change the denominator substantially. Fractional counting is an extension. It should split one publication across assigned topics and compute field totals from the same fractions.

Annual grids start at the first observed publication in each group. An unobserved year after that first observation has a zero count, assuming the extraction covered it. Omit partial years from growth calculations by setting `complete_through`. Activity totals can include partial years. Development results summarize an API sample and have no population interpretation.

| Measure | Calculation |
| --- | --- |
| Absolute annual growth | Current count minus previous count |
| Relative annual growth | Absolute change divided by the previous count |
| Compound annual growth | (Current count / count at configured lag) raised to 1/window, minus 1 |
| Acceleration | Difference between consecutive relative growth values |
| Volatility | Sample standard deviation of trailing available annual growth rates |
| Topic share change | Current share minus prior-year share, in percentage-point units when multiplied by 100 |
| Field-adjusted growth | Topic relative growth minus parent-field relative growth |

Undefined denominators and insufficient history produce null indicators. The emergence stage should apply the configured minimum count before ranking, scale components within each scoring year using eligible topics, and persist weighted contributions. The team still needs to select scaling, treatment of missing components and ties, and sensitivity checks for extreme growth and small baseline counts.

## Retrospective evaluation

For each cutoff and horizon that ends by `complete_through`, build the feature frame and topic eligibility using years through the cutoff. Fit scaling and any data-dependent thresholds on that frame. Build the future outcome independently from counts at the horizon. Evaluate subsequent absolute and relative growth with explicit handling of zero baseline counts. Retain volume and simple recent-growth baselines, compare each indicator and composite, and report Spearman correlation, precision@K and top-K overlap with a documented tie policy. A candidate topic must be observable at the cutoff. Store the maximum feature observation year and assert that it falls at or before the cutoff.

Historical citation features may only aggregate citation edges from publications dated at or before the cutoff. Today's cumulative citation counts are excluded from historical features. Current topics and metadata can reflect later classification and correction. The planned experiment is a retrospective evaluation. Historical snapshots and metadata availability timestamps would be needed for fully point-in-time evaluation.

## Network extension

Aggregate within-work unordered topic pairs and directed citation counts between primary topics. External references remain in Silver. Topic-level citation aggregation requires known topic metadata for both endpoints. Decide on edge thresholds, year slicing, edge weights, citation age treatment and community resolution after profiling. NetworkX can handle bounded driver graphs. Larger corpora require distributed processing or another supported graph engine.

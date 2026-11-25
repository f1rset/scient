CONTRACTS = {'bronze.works_raw': ('source_id STRING, ingested_at TIMESTAMP, run_id STRING, '
                      'payload STRING, corpus STRING',
                      'corpus, source_id',
                      'Latest raw work JSON for the configured corpus'),
 'bronze.topics_raw': ('source_id STRING, ingested_at TIMESTAMP, run_id '
                       'STRING, payload STRING',
                       'source_id',
                       'Latest raw topic JSON'),
 'silver.works': ('work_id STRING, title STRING, publication_year INT, '
                  'primary_topic_id STRING, cited_by_count BIGINT, '
                  'referenced_works ARRAY<STRING>',
                  'work_id',
                  'Normalized publications with current citation totals'),
 'silver.topics': ('topic_id STRING, topic_name STRING, subfield_id STRING, '
                   'subfield_name STRING, field_id STRING, field_name STRING, '
                   'domain_id STRING, domain_name STRING',
                   'topic_id',
                   'Topic taxonomy and parent hierarchy'),
 'silver.work_topics': ('work_id STRING, topic_id STRING, is_primary BOOLEAN, '
                        'relevance DOUBLE',
                        'work_id, topic_id',
                        'Assigned topics and relevance'),
 'silver.citation_edges': ('citing_work_id STRING, cited_work_id STRING, '
                           'citing_year INT, cited_in_corpus BOOLEAN',
                           'citing_work_id, cited_work_id',
                           'Directed references including external works'),
 'gold.topic_year_metrics': ('topic_id STRING, field_id STRING, '
                             'publication_year INT, publication_count BIGINT',
                             'topic_id, publication_year',
                             'Annual primary-topic counts'),
 'gold.field_year_metrics': ('field_id STRING, publication_year INT, '
                             'publication_count BIGINT',
                             'field_id, publication_year',
                             'Annual field counts in the collected corpus'),
 'gold.topic_growth_indicators': ('topic_id STRING, field_id STRING, '
                                  'publication_year INT, publication_count '
                                  'BIGINT, absolute_growth BIGINT, '
                                  'relative_growth DOUBLE, cagr DOUBLE, '
                                  'acceleration DOUBLE, volatility DOUBLE, '
                                  'topic_share DOUBLE, share_change DOUBLE, '
                                  'field_adjusted_growth DOUBLE',
                                  'topic_id, publication_year',
                                  'Trailing growth and relative prominence'),
 'gold.topic_emergence_scores': ('topic_id STRING, publication_year INT, '
                                 'composite_score DOUBLE, components '
                                 'MAP<STRING,DOUBLE>',
                                 'topic_id, publication_year',
                                 'Composite and individual score components'),
 'gold.indicator_comparison': ('publication_year INT, indicator STRING, '
                               'baseline STRING, spearman DOUBLE, '
                               'top_k_overlap DOUBLE',
                               'publication_year, indicator, baseline',
                               'Agreement among indicator rankings'),
 'gold.historical_evaluation': ('cutoff_year INT, horizon INT, topic_id '
                                'STRING, indicator STRING, score DOUBLE, '
                                'observed_growth DOUBLE, feature_max_year INT',
                                'cutoff_year, horizon, topic_id, indicator',
                                'Retrospective feature and outcome pairs'),
 'gold.evaluation_summary': ('cutoff_year INT, horizon INT, indicator STRING, '
                             'k INT, spearman DOUBLE, precision_at_k DOUBLE, '
                             'top_k_overlap DOUBLE',
                             'cutoff_year, horizon, indicator, k',
                             'Ranking performance by cutoff'),
 'gold.topic_cooccurrence_edges': ('source_topic_id STRING, target_topic_id '
                                   'STRING, weight BIGINT',
                                   'source_topic_id, target_topic_id',
                                   'Undirected topic pairs ordered by ID'),
 'gold.topic_citation_edges': ('source_topic_id STRING, target_topic_id '
                               'STRING, weight BIGINT',
                               'source_topic_id, target_topic_id',
                               'Directed edges between primary topics'),
 'gold.topic_network_metrics': ('network STRING, topic_id STRING, degree '
                                'BIGINT, weighted_degree DOUBLE',
                                'network, topic_id',
                                'Degree statistics by network'),
 'gold.topic_communities': ('network STRING, topic_id STRING, community_id '
                            'STRING',
                            'network, topic_id',
                            'Community assignments by network'),
 'serving.topic_overview': ('topic_id STRING, topic_name STRING, field_id '
                            'STRING, field_name STRING, publication_count '
                            'BIGINT',
                            'topic_id',
                            'Corpus publication totals by topic'),
 'serving.topic_trends': ('topic_id STRING, field_id STRING, publication_year '
                          'INT, publication_count BIGINT, relative_growth '
                          'DOUBLE, topic_share DOUBLE',
                          'topic_id, publication_year',
                          'Topic time series'),
 'serving.emerging_topics': ('topic_id STRING, field_id STRING, '
                             'publication_year INT, indicator STRING, score '
                             'DOUBLE, rank BIGINT',
                             'topic_id, publication_year, indicator',
                             'Rankings for the app'),
 'serving.indicator_explanations': ('topic_id STRING, publication_year INT, '
                                    'indicator STRING, component STRING, '
                                    'contribution DOUBLE',
                                    'topic_id, publication_year, indicator, '
                                    'component',
                                    'Contributions to individual rankings'),
 'serving.related_topics': ('source_topic_id STRING, target_topic_id STRING, '
                            'network STRING, weight BIGINT',
                            'source_topic_id, target_topic_id, network',
                            'Topic neighbors'),
 'ops.pipeline_runs': ('run_id STRING, stage STRING, recorded_at TIMESTAMP, '
                       'status STRING',
                       'run_id, stage, recorded_at',
                       'Stage lifecycle events'),
 'ops.ingestion_checkpoints': ('stream_id STRING, extraction_id STRING, '
                               'next_cursor STRING, records BIGINT, complete '
                               'BOOLEAN, updated_at TIMESTAMP',
                               'stream_id, extraction_id',
                               'Latest cursor and record budget for one '
                               'extraction'),
 'ops.data_quality_results': ('run_id STRING, stage STRING, check_name STRING, '
                              'severity STRING, failures BIGINT, checked_at '
                              'TIMESTAMP',
                              'run_id, stage, check_name, checked_at',
                              'Recorded invariant and warning results')}

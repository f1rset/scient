def citation_edges(works):
    from pyspark.sql import functions as f

    citing = works.select(
        f.col("work_id").alias("citing_work_id"),
        f.col("publication_year").alias("citing_year"),
        f.explode("referenced_works").alias("cited_work_id"),
    )
    referenced = works.select(
        f.col("work_id").alias("cited_work_id"), f.lit(True).alias("cited_in_corpus")
    )
    return citing.where("citing_work_id <> cited_work_id").join(
        referenced, "cited_work_id", "left"
    ).fillna(False, subset=["cited_in_corpus"])

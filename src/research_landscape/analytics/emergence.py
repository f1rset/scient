"""Publication-based emergence components and future scoring interface."""

COMPONENTS = ("relative_growth", "acceleration", "share_change", "field_adjusted_growth")
BASELINES = ("publication_count", "absolute_growth")


def composite_scores(indicators, weights, minimum_count):
    # TODO: Fit scaling within each scoring year and persist component contributions.
    raise NotImplementedError("Composite emergence scoring is pending")

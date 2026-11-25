import pytest

from research_landscape.analytics.evaluation import enforce_cutoff, evaluation_windows
from research_landscape.analytics.growth import relative_change
from research_landscape.openalex.filters import work_filters
from research_landscape.openalex.pagination import pages
from research_landscape.transformations.works import normalize_id


def test_openalex_identifier():
    assert normalize_id("https://openalex.org/w42", "W") == "W42"
    with pytest.raises(ValueError):
        normalize_id("T42", "W")


def test_pages_resume_and_respect_caps():
    calls = []

    def fetch(params):
        calls.append(params)
        if params["cursor"] == "*":
            return {"results": [{"id": "W1"}], "meta": {"next_cursor": "next"}}
        return {"results": [{"id": "W2"}], "meta": {"next_cursor": "more"}}

    first, = pages(fetch, page_size=2, max_requests=1)
    assert first[1:] == ("next", 1, False)
    second, = pages(fetch, cursor=first[1], records=first[2], max_records=2)
    assert second[1:] == ("more", 2, True)
    assert calls[1]["per_page"] == 1


def test_repeated_cursor_fails():
    with pytest.raises(RuntimeError, match="same cursor"):
        list(pages(lambda _: {"results": [1], "meta": {"next_cursor": "*"}}))


def test_filters_apply_to_primary_topics():
    config = dict(start_year=2015, end_year=2025, fields=[17], subfields=[1702], topics=["T1"])
    value = work_filters(config, "2025-12-01")
    assert "primary_topic.subfield.id:1702" in value
    assert "primary_topic.id:T1" in value
    assert "from_updated_date:2025-12-01" in value


def test_growth_and_zero_denominator():
    assert relative_change(15, 10) == 0.5
    assert relative_change(0, 10) == -1
    assert relative_change(1, 0) is None
    assert relative_change(1, None) is None


def test_cutoff_and_complete_outcomes():
    assert evaluation_windows([2019, 2022], [1, 3], 2024) == [(2019, 1), (2019, 3), (2022, 1)]
    enforce_cutoff(2019, 2019)
    with pytest.raises(ValueError, match="cutoff"):
        enforce_cutoff(2020, 2019)

"""Cursor pagination with explicit per-extraction and per-invocation budgets."""


def pages(fetch, *, cursor="*", records=0, max_records=None, max_requests=None, page_size=100):
    requests = 0
    while cursor is not None and (max_requests is None or requests < max_requests):
        remaining = page_size if max_records is None else min(page_size, max_records - records)
        if remaining <= 0:
            return
        response = fetch({"cursor": cursor, "per_page": remaining})
        rows = response["results"]
        if len(rows) > remaining:
            raise RuntimeError("OpenAlex returned more records than requested")
        following = response["meta"].get("next_cursor") if rows else None
        if following == cursor:
            raise RuntimeError("OpenAlex returned the same cursor twice")
        requests += 1
        records += len(rows)
        complete = following is None or (max_records is not None and records == max_records)
        yield rows, following, records, complete
        if complete:
            return
        cursor = following

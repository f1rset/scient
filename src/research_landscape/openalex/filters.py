from datetime import date
import hashlib
import json


def work_filters(settings, updated_since=""):
    rules = [
        f"from_publication_date:{settings['start_year']}-01-01",
        f"to_publication_date:{settings['end_year']}-12-31",
    ]
    for key, attribute in (("fields", "field.id"), ("subfields", "subfield.id"), ("topics", "id")):
        if settings[key]:
            values = "|".join(sorted({str(value) for value in settings[key]}))
            rules.append(f"primary_topic.{attribute}:{values}")
    if updated_since:
        rules.append(f"from_updated_date:{date.fromisoformat(updated_since).isoformat()}")
    return ",".join(rules)


def fingerprint(*values):
    return hashlib.sha256(json.dumps(values, sort_keys=True).encode()).hexdigest()

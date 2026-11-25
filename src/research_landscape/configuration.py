"""Validate target configuration and resolve Unity Catalog identifiers."""

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re

import yaml


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        raise ValueError("Catalog, schema and table names must be simple SQL identifiers")
    return f"`{value}`"


def overlay(base, overrides):
    return {
        **base,
        **{
            key: overlay(base[key], value)
            if isinstance(value, dict) and isinstance(base.get(key), dict)
            else value
            for key, value in overrides.items()
        },
    }


@dataclass(frozen=True)
class Settings:
    catalog: str
    profile: str
    values: dict

    @classmethod
    def load(cls, root: Path, catalog: str, profile: str):
        identifier(catalog)
        if profile not in {"development", "production"}:
            raise ValueError("Select development or production")
        base = yaml.safe_load((root / "config/default.yml").read_text())
        override = yaml.safe_load((root / f"config/{profile}.yml").read_text())
        settings = cls(catalog, profile, overlay(base, override))
        settings.validate()
        return settings

    def validate(self):
        v = self.values
        schemas = v["schemas"]
        if len({name.lower() for name in schemas.values()}) != len(schemas):
            raise ValueError("Each layer needs a distinct schema")
        for name in schemas.values():
            identifier(name)
        if not 1800 <= v["start_year"] <= v["complete_through"] <= v["end_year"] <= date.today().year:
            raise ValueError("Check publication years and complete_through")
        api = v["api"]
        if not 1 <= api["page_size"] <= 100 or any(
            api[key] <= 0 for key in ("timeout_seconds", "max_attempts", "min_interval_seconds")
        ):
            raise ValueError("Invalid OpenAlex request configuration")
        for limit in (api["max_requests"], v["max_works"]):
            if limit is not None and (type(limit) is not int or limit <= 0):
                raise ValueError("Request and work limits must be positive integers or null")
        for filter_name, pattern in (("fields", r"[0-9]+"), ("subfields", r"[0-9]+"), ("topics", r"T[0-9]+")):
            if any(not re.fullmatch(pattern, str(item)) for item in v[filter_name]):
                raise ValueError(f"Invalid OpenAlex IDs in {filter_name}")
        for key in ("minimum_count", "growth_window", "top_k"):
            if type(v[key]) is not int or v[key] <= 0:
                raise ValueError(f"{key} must be a positive integer")
        if any(not v["start_year"] <= year < v["complete_through"] for year in v["cutoffs"]):
            raise ValueError("Cutoffs must fall before the last complete publication year")
        if any(type(h) is not int or h <= 0 for h in v["horizons"]):
            raise ValueError("Evaluation horizons must be positive integers")
        if not v["weights"] or any(weight < 0 for weight in v["weights"].values()) or not sum(v["weights"].values()):
            raise ValueError("Use nonnegative emergence weights with a positive total")
        if v["network"]["max_edges"] <= 0:
            raise ValueError("Network edge limit must be positive")

    def schema(self, layer):
        return ".".join((identifier(self.catalog), identifier(self.values["schemas"][layer])))

    def table(self, key):
        layer, table = key.split(".")
        return f"{self.schema(layer)}.{identifier(table)}"

"""Small, testable USDA Quick Stats parsing helpers."""
from __future__ import annotations
import re

SUPPORTED_CROPS = {"CORN", "SOYBEANS", "WHEAT"}


def numeric_value(value: object) -> float | None:
    """Parse Quick Stats formatted numbers; suppressions and nonnumbers -> None."""
    if value is None:
        return None
    raw = str(value).strip().replace(",", "")
    if not raw or raw.upper() in {"(D)", "(Z)", "(NA)", "(S)", "NA", "N/A", "NULL", "-"}:
        return None
    try:
        result = float(raw)
    except ValueError:
        return None
    if result != result or result in (float("inf"), float("-inf")):
        return None
    return result


def standardize_crop(name: str) -> str | None:
    crop = re.sub(r"\s+", " ", str(name).upper().strip())
    return crop if crop in SUPPORTED_CROPS else None


def valid_year(year: object) -> bool:
    try:
        n = int(str(year))
        return 1900 <= n <= 2100
    except (ValueError, TypeError):
        return False

"""Check a USDA NASS Quick Stats CSV before the Spark/Delta pipeline runs.

No external packages required. This script does not invent or impute USDA values.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import json
import re
from pathlib import Path

REQUIRED = {"year", "state_name", "commodity_desc", "statisticcat_desc", "unit_desc",
            "value", "agg_level_desc", "domain_desc", "freq_desc"}
CROPS = {"CORN", "SOYBEANS", "WHEAT"}
CATEGORIES = {"PRODUCTION", "YIELD"}
SUPPRESSED = {"(D)", "(Z)", "(NA)", "(S)", "(X)", "(H)", "(L)", "", "-"}


def text(row, field):
    return (row.get(field) or "").strip().upper()


def numeric(s):
    s = (s or "").strip()
    if s.upper() in SUPPRESSED:
        return None
    try:
        n = float(s.replace(",", ""))
        if not (-float("inf") < n < float("inf")):
            return None
        return n
    except ValueError:
        return None



def adapt_web_spreadsheet(row):
    """Convert USDA Quick Stats *website spreadsheet* headers to API-style fields.

    Only final annual records are eligible; monthly forecasts are excluded.
    Derive statistic and units from the full Data Item label, not from guesses.
    """
    if not ("data item" in row and "geo level" in row and "period" in row):
        return row, None
    period = text(row, "period")
    if period != "YEAR":
        return row, "excluded_forecast_or_nonannual"
    item = text(row, "data item")
    # e.g. CORN, GRAIN - YIELD, MEASURED IN BU / ACRE
    m = re.search(r"-\s*(YIELD|PRODUCTION)\s*,\s*MEASURED IN\s+(.+)$", item)
    if not m:
        return row, "excluded_unrecognized_data_item"
    new = dict(row)
    new.update({
        "state_name": text(row, "state"),
        "commodity_desc": text(row, "commodity"),
        "statisticcat_desc": m.group(1),
        "unit_desc": m.group(2).strip(),
        "agg_level_desc": text(row, "geo level"),
        "domain_desc": text(row, "domain"),
        "freq_desc": "ANNUAL",
    })
    return new, None


def audit(path: Path, clean_path: Path | None = None, report_path: Path | None = None):
    if not path.is_file():
        raise FileNotFoundError(f"USDA export not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("Empty CSV or missing header")
        # Preserve the original header values for CSV readers that care about casing.
        lookup = {name.strip().lower(): name for name in reader.fieldnames}
        website_export = {"data item", "geo level", "period", "state", "commodity", "domain", "year", "value"}.issubset(lookup)
        missing = REQUIRED - (set(lookup) | (REQUIRED if website_export else set()))
        if missing:
            raise ValueError(f"Missing Quick Stats columns: {', '.join(sorted(missing))}. "
                             "Download a Quick Stats spreadsheet CSV rather than a summary PDF.")
        counts = Counter()
        rows = []
        keys = defaultdict(list)
        by_crop, by_year, by_state = Counter(), Counter(), Counter()
        dimension_fields = [x for x in ("source_desc", "sector_desc", "class_desc", "prodn_practice_desc",
                                        "util_practice_desc", "reference_period_desc", "short_desc",
                                        "domaincat_desc") if x in lookup]
        for raw in reader:
            counts["input_rows"] += 1
            row = {name: (raw.get(original) or "").strip() for name, original in lookup.items()}
            if website_export:
                row, skip_reason = adapt_web_spreadsheet(row)
                if skip_reason:
                    counts[skip_reason] += 1
                    continue
            if not (text(row, "commodity_desc") in CROPS and text(row, "statisticcat_desc") in CATEGORIES
                    and text(row, "agg_level_desc") == "STATE" and text(row, "freq_desc") == "ANNUAL"
                    and text(row, "domain_desc") == "TOTAL"):
                counts["excluded_scope"] += 1
                continue
            try:
                year = int(text(row, "year"))
                if not 1900 <= year <= 2100:
                    raise ValueError()
            except ValueError:
                counts["invalid_year"] += 1
                continue
            if not text(row, "state_name") or not text(row, "unit_desc"):
                counts["missing_dimensions"] += 1
                continue
            val = numeric(row.get("value"))
            if val is None:
                counts["suppressed_or_invalid_value"] += 1
                continue
            counts["eligible_numeric_rows"] += 1
            key = (str(year), text(row, "state_name"), text(row, "commodity_desc"),
                   text(row, "statisticcat_desc"), text(row, "unit_desc"))
            keys[key].append((val, {f: row.get(f, "") for f in dimension_fields}))
            rows.append(row)
            by_crop[key[2]] += 1
            by_year[str(year)] += 1
            by_state[key[1]] += 1
    ambiguous = []
    duplicate_identical = 0
    for key, group in keys.items():
        if len(group) > 1:
            vals = {x[0] for x in group}
            if len(vals) > 1:
                ambiguous.append({"key": list(key), "distinct_values": sorted(vals),
                                  "source_dimensions": [x[1] for x in group[:5]]})
            else:
                duplicate_identical += len(group)-1
    report = {
        "source_file": str(path.resolve()), "website_export_detected": website_export,
        "counts": dict(counts),
        "distinct_states": len(by_state), "distinct_years": len(by_year),
        "crops": dict(sorted(by_crop.items())), "years": dict(sorted(by_year.items())),
        "identical_duplicate_rows": duplicate_identical,
        "ambiguous_metric_keys": len(ambiguous),
        "ambiguous_examples": ambiguous[:10],
        "dimension_fields_available": dimension_fields,
        "interpretation": "Filtered STATE/ANNUAL/TOTAL crop PRODUCTION or YIELD results. "
                          "Suppressed values are missing, not zero. Compare only matching unit/statistic definitions."
    }
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not counts["eligible_numeric_rows"]:
        raise ValueError("No eligible numeric state-level annual crop rows. Review export filters.")
    if ambiguous:
        raise ValueError(f"{len(ambiguous)} conflicting state/year/crop/statistic/unit groups. "
                         "Review the audit JSON and narrow source, class, practice, or reporting period. "
                         "Refusing to average incompatible estimates.")
    if clean_path:
        clean_path.parent.mkdir(parents=True, exist_ok=True)
        # Output just columns expected by the ETL so Spark sees unique metric keys.
        with clean_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["year", "state_name", "commodity_desc", "statisticcat_desc", "unit_desc",
                             "value", "agg_level_desc", "domain_desc", "freq_desc"])
            for key, group in sorted(keys.items()):
                year, state, crop, metric, unit = key
                writer.writerow([year, state, crop, metric, unit, group[0][0], "STATE", "TOTAL", "ANNUAL"])
        report["unique_eligible_keys_written"] = len(keys)
        if report_path:
            report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, type=Path, help="Downloaded official USDA Quick Stats CSV")
    parser.add_argument("--clean-out", type=Path, default=Path("data/raw/usda_state_crop_clean.csv"))
    parser.add_argument("--report", type=Path, default=Path("output/real_usda_preflight.json"))
    args = parser.parse_args()
    result = audit(args.csv, args.clean_out, args.report)
    print("USDA preflight passed:", result["counts"])
    print("Unique state/year/crop/statistic/unit keys:", result["unique_eligible_keys_written"])
    print("Clean data:", args.clean_out)
    print("Audit:", args.report)


if __name__ == "__main__":
    main()

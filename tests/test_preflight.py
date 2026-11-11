import csv
from pathlib import Path
import tempfile
import unittest
from src.preflight import audit, numeric

HEADERS = ["year", "state_name", "commodity_desc", "statisticcat_desc", "unit_desc", "value", "agg_level_desc", "domain_desc", "freq_desc"]

class PreflightTests(unittest.TestCase):
    def test_numeric(self):
        self.assertEqual(numeric("1,234"), 1234)
        self.assertIsNone(numeric("(D)"))
        self.assertIsNone(numeric("(Z)"))

    def test_synthetic_preflight(self):
        project = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            r = audit(project/"data/sample/usda_quickstats_SYNTHETIC.csv", d/"clean.csv", d/"audit.json")
            self.assertEqual(r["counts"]["input_rows"], 147)
            self.assertEqual(r["unique_eligible_keys_written"], 144)
            self.assertEqual(r["counts"]["suppressed_or_invalid_value"], 1)
            self.assertEqual(r["counts"]["excluded_scope"], 2)

    def test_conflicting_reporting_series_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/"conflict.csv"
            with p.open("w", newline="") as f:
                w=csv.writer(f); w.writerow(HEADERS)
                w.writerow([2024,"IOWA","CORN","YIELD","BU / ACRE",178,"STATE","TOTAL","ANNUAL"])
                w.writerow([2024,"IOWA","CORN","YIELD","BU / ACRE",180,"STATE","TOTAL","ANNUAL"])
            with self.assertRaisesRegex(ValueError,"conflicting"):
                audit(p,report_path=Path(tmp)/"report.json")

if __name__ == '__main__':
    unittest.main()

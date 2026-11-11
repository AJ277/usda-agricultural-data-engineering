"""Optional Spark/Delta integration check: run after pip requirements and Java installation."""
import csv
from pathlib import Path
import tempfile
import unittest


class SparkTests(unittest.TestCase):
    def test_delta_round_trip(self):
        try:
            from src.pipeline import run
        except ImportError as exc:
            self.skipTest(f"PySpark/Delta not installed: {exc}")
        source = Path(__file__).resolve().parents[1] / 'data' / 'sample' / 'usda_quickstats_SYNTHETIC.csv'
        with tempfile.TemporaryDirectory() as tmp:
            result = run(source, Path(tmp) / 'delta')
            self.assertGreater(result['bronze_rows'], 0)
            self.assertGreater(result['silver_rows'], 0)
            self.assertGreater(result['gold_groups'], 0)


if __name__ == '__main__':
    unittest.main()

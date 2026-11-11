import unittest
from src.normalize import numeric_value, standardize_crop, valid_year


class ParseTests(unittest.TestCase):
    def test_numbers(self):
        self.assertEqual(numeric_value('1,234,500'), 1234500.0)
        self.assertEqual(numeric_value('34.2'), 34.2)

    def test_suppression(self):
        for v in ('(D)', '(Z)', '(NA)', '', None, 'bad'):
            self.assertIsNone(numeric_value(v))

    def test_crop(self):
        self.assertEqual(standardize_crop(' corn '), 'CORN')
        self.assertIsNone(standardize_crop('BARLEY'))

    def test_year(self):
        self.assertTrue(valid_year('2024'))
        self.assertFalse(valid_year('no-year'))


if __name__ == '__main__':
    unittest.main()

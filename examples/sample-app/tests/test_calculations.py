import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sample_app import total


class TotalTests(unittest.TestCase):
    def test_empty_collection_is_zero(self):
        self.assertEqual(total([]), 0)

    def test_none_is_zero(self):
        self.assertEqual(total(None), 0)

    def test_values_are_summed(self):
        self.assertEqual(total([2, 3, 5]), 10)


if __name__ == "__main__":
    unittest.main()

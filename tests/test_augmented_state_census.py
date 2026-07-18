import json
from pathlib import Path
import tempfile
import unittest

from tools.augmented_state_census import write_census


class AugmentedStateCensusTests(unittest.TestCase):
    def test_census_is_complete_compared_and_immutable(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "census.json"
            record = write_census(output, size=2, plies=3, comparison_depth=1)
            self.assertEqual(record["status"], "completed")
            self.assertEqual(record["disagreement_count"], 0)
            self.assertEqual(record["comparison_count"], record["augmented_state_count"])
            self.assertEqual(json.loads(output.read_text())["schema"],
                             "fold-go-augmented-state-census/v1")
            with self.assertRaises(FileExistsError):
                write_census(output, size=2, plies=3, comparison_depth=1)


if __name__ == "__main__":
    unittest.main()

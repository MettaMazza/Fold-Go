import tempfile
from pathlib import Path
import unittest

from tools import measure_go as go
from tools.verify_match_receipts import verify_match


class DevelopmentReceiptVerifierTests(unittest.TestCase):
    def test_development_configuration_and_games_replay(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "development"
            go.run_tournament(
                size=1, rounds=1, depth=0, komi=0,
                output_dir=output, development=True)
            verification = verify_match(output)
            self.assertEqual(verification["status"], "verified")
            self.assertEqual(verification["run_kind"], "development")
            self.assertEqual(verification["verified_games"], 1)
            self.assertEqual(
                verification["semantic_replay"], "passed")


if __name__ == "__main__":
    unittest.main()

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools import measure_go as go
from tools.verify_match_receipts import verify_match


class AugmentedStateTests(unittest.TestCase):
    def setUp(self):
        go.tt_gen[0] += 1
        go.nodes_left[0] = go.NODE_BUDGET
        go.pass_aborted[0] = 0

    def test_initial_position_is_in_superko_history_and_pass_does_not_mutate_it(self):
        board = go.SFTGoBoard(2)
        self.assertEqual(board.history, {"0000"})
        before = set(board.history)
        self.assertTrue(board.play_move(go.PASS, 1))
        self.assertEqual(board.history, before)

    def test_augmented_key_binds_mover_pass_and_complete_history(self):
        board = go.SFTGoBoard(2)
        base = go.canonical_augmented_state(board, 1, False)
        self.assertNotEqual(base, go.canonical_augmented_state(board, 2, False))
        self.assertNotEqual(base, go.canonical_augmented_state(board, 1, True))
        changed = board.copy()
        changed.history.add("1000")
        self.assertNotEqual(base, go.canonical_augmented_state(changed, 1, False))

    def test_symmetry_admission_transforms_every_history_position(self):
        board = go.SFTGoBoard(2)
        board.history.add("1000")
        admitted = go.get_augmented_symmetries(board)
        self.assertLess(len(admitted), 8)
        for transform in admitted:
            self.assertTrue(all(
                go.transform_position(position, board.size, transform) == position
                for position in board.history
            ))

    def test_root_always_contains_pass_and_resign_is_distinct(self):
        board = go.SFTGoBoard(2)
        self.assertTrue(board.get_legal_moves(1))
        self.assertIn(go.PASS, go.root_candidates(board, 1))
        self.assertIsNone(go.gtp_to_index("pass", 2))
        self.assertEqual(go.gtp_to_index("resign", 2), go.RESIGN)

    def test_empty_board_preserves_every_legal_symmetry_orbit(self):
        for size in (5, 9, 19):
            board = go.SFTGoBoard(size)
            legal = board.get_legal_moves(1)
            symmetries = go.get_augmented_symmetries(board)
            expected = sorted({
                go.get_orbit_representative(move, size, symmetries)
                for move in legal
            })
            selected = go.get_dynamic_sparse_moves(board, 1, legal)
            self.assertEqual(selected, expected)
            self.assertEqual(
                {go.get_orbit_representative(move, size, symmetries)
                 for move in legal},
                set(selected),
            )

    def test_quiescence_preserves_every_legal_active_front_without_liberty_cutoff(self):
        board = go.SFTGoBoard(5)
        center = 2 * board.size + 2
        self.assertTrue(board.play_move(center, 1))
        _, liberties = board.get_group(center)
        self.assertGreater(len(liberties), 2)
        legal = board.get_legal_moves(2)
        symmetries = go.get_augmented_symmetries(board)
        expected = {
            go.get_orbit_representative(move, board.size, symmetries)
            for move in liberties if move in legal
        }
        selected = set(go.get_dynamic_sparse_moves(
            board, 2, legal, tactical_only=True))
        self.assertEqual(selected, expected)

    def test_root_pass_after_prior_pass_uses_terminal_area_value(self):
        board = go.SFTGoBoard(2, komi=0)
        move, value = go._eval_root_candidate(
            (board, 1, go.PASS, 3, True))
        self.assertIs(move, go.PASS)
        self.assertEqual(value, go.terminal_area_value(board, 1))
        self.assertEqual(go.pass_aborted[0], 0)

    def test_root_pass_without_prior_pass_searches_the_child(self):
        board = go.SFTGoBoard(1, komi=0)
        move, value = go._eval_root_candidate(
            (board, 1, go.PASS, 1, False))
        self.assertIs(move, go.PASS)
        self.assertIsNotNone(value)

    def test_typed_tt_matches_no_cache_all_actions_on_small_board(self):
        board = go.SFTGoBoard(2)
        with_tt = go.alphabeta_sft(
            board, 2, go.VALUE_FLOOR, go.VALUE_CEILING, 1, False, True)
        self.assertEqual(go.pass_aborted[0], 0)
        go.nodes_left[0] = go.NODE_BUDGET
        go.pass_aborted[0] = 0
        without_tt = go.alphabeta_sft(
            board, 2, go.VALUE_FLOOR, go.VALUE_CEILING, 1, False, False)
        self.assertEqual(go.pass_aborted[0], 0)
        self.assertEqual(with_tt, without_tt)

    def test_tt_matches_no_cache_over_reachable_augmented_state_census(self):
        frontier = [(go.SFTGoBoard(2), 1, False)]
        census = {}
        for _ in range(5):
            next_frontier = []
            for board, color, last_passed in frontier:
                key = go.canonical_augmented_state(board, color, last_passed)
                census[key] = (board, color, last_passed)
                for move in board.get_legal_moves(color) + [go.PASS]:
                    if move is go.PASS and last_passed:
                        continue
                    child = board.copy()
                    self.assertTrue(child.play_move(move, color))
                    next_frontier.append((child, 3 - color, move is go.PASS))
            frontier = next_frontier
        self.assertGreater(len(census), 10)
        for board, color, last_passed in census.values():
            go.tt_gen[0] += 1
            go.nodes_left[0] = go.NODE_BUDGET
            go.pass_aborted[0] = 0
            with_tt = go.alphabeta_sft(
                board, 1, go.VALUE_FLOOR, go.VALUE_CEILING,
                color, last_passed, True)
            self.assertEqual(go.pass_aborted[0], 0)
            go.nodes_left[0] = go.NODE_BUDGET
            go.pass_aborted[0] = 0
            without_tt = go.alphabeta_sft(
                board, 1, go.VALUE_FLOOR, go.VALUE_CEILING,
                color, last_passed, False)
            self.assertEqual(go.pass_aborted[0], 0)
            self.assertEqual(with_tt, without_tt, key)

    def test_tt_requires_exact_state_and_respects_bound_type(self):
        board = go.SFTGoBoard(2)
        key = go.canonical_augmented_state(board, 1, False)
        go.tt_store(key, 3, go.VALUE_DRAW, go.TT_EXACT)
        value, _, _ = go.tt_probe(key, 2, go.VALUE_FLOOR, go.VALUE_CEILING)
        self.assertEqual(value, go.VALUE_DRAW)
        changed = board.copy()
        changed.history.add("1000")
        changed_key = go.canonical_augmented_state(changed, 1, False)
        value, _, _ = go.tt_probe(changed_key, 2, go.VALUE_FLOOR, go.VALUE_CEILING)
        self.assertIsNone(value)

    def test_registered_match_writes_hash_bound_receipts_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "sealed-match"
            result = go.run_tournament(
                size=1, rounds=1, depth=0, komi=0, output_dir=output)
            self.assertEqual(result["status"], "completed")
            registration = (output / "registration.json").read_bytes()
            registration_record = json.loads(registration)
            game = (output / "game-001.json").read_bytes()
            match = json.loads((output / "match.json").read_text())
            game_record = json.loads(game)
            self.assertEqual(
                game_record["registration_sha256"],
                hashlib.sha256(registration).hexdigest())
            self.assertEqual(
                match["games"][0]["sha256"], hashlib.sha256(game).hexdigest())
            self.assertTrue(game_record["gtp_transcript"])
            self.assertEqual(
                registration_record["schema"],
                "fold-go-match-registration/v3")
            self.assertEqual(
                set(registration_record["opponent"]["gtp_identity"]),
                {"protocol_version", "name", "version", "list_commands"})
            self.assertEqual(
                registration_record["opponent"]["command_file_bindings"], [])
            verification = verify_match(output)
            self.assertEqual(verification["status"], "verified")
            self.assertEqual(verification["verified_games"], 1)
            with self.assertRaises(FileExistsError):
                go.run_tournament(
                    size=1, rounds=1, depth=0, komi=0, output_dir=output)

    def test_opponent_command_files_are_hash_bound(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "engine.cfg"
            model = root / "weights.bin"
            config.write_text("rules=area\n")
            model.write_bytes(b"counted-model-input")
            bindings = go._command_file_bindings([
                "engine", f"--config={config}", "--model", str(model),
                "--threads", "8",
            ])
            self.assertEqual([row["argument_index"] for row in bindings], [1, 3])
            self.assertEqual([row["sha256"] for row in bindings], [
                hashlib.sha256(config.read_bytes()).hexdigest(),
                hashlib.sha256(model.read_bytes()).hexdigest(),
            ])

    def test_development_run_is_not_labelled_as_an_official_registration(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "development"
            result = go.run_tournament(
                size=1, rounds=1, depth=0, komi=0,
                output_dir=output, development=True)
            configuration = json.loads(
                (output / "development_configuration.json").read_text())
            self.assertEqual(
                configuration["schema"],
                "fold-go-development-configuration/v1")
            self.assertEqual(
                configuration["status"], "development-configured")
            self.assertFalse(configuration["governance_authority"])
            self.assertFalse((output / "registration.json").exists())
            self.assertIn(
                "development_configuration_sha256", result)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Verify the hash chain and bound source of a sealed Fold Go match directory."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import measure_go as go


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_match(directory: Path, require_current_source: bool = True) -> dict:
    directory = directory.resolve()
    registration_path = directory / "registration.json"
    development_path = directory / "development_configuration.json"
    if registration_path.exists() == development_path.exists():
        raise RuntimeError(
            "match directory must contain exactly one registration or development configuration")
    development = development_path.exists()
    configuration_path = development_path if development else registration_path
    match_path = directory / "match.json"
    registration = json.loads(configuration_path.read_text())
    match = json.loads(match_path.read_text())
    registration_sha = sha256(configuration_path)
    binding_field = ("development_configuration_sha256" if development
                     else "registration_sha256")
    if match.get(binding_field) != registration_sha:
        raise RuntimeError("match configuration hash mismatch")
    expected_configuration_schema = (
        "fold-go-development-configuration/v1" if development else None)
    if development:
        if registration.get("schema") != expected_configuration_schema or \
                registration.get("status") != "development-configured" or \
                registration.get("governance_authority") is not False:
            raise RuntimeError("unsupported development configuration")
    elif registration.get("schema") not in {
            "fold-go-match-registration/v1", "fold-go-match-registration/v2",
            "fold-go-match-registration/v3"}:
        raise RuntimeError("unsupported match registration")
    expected_match_schema = (
        "fold-go-development-measurement/v1" if development
        else "fold-go-match-receipt/v1")
    if match.get("schema") != expected_match_schema:
        raise RuntimeError("unsupported match receipt")
    if registration.get("schema") in {
            "fold-go-match-registration/v2", "fold-go-match-registration/v3"}:
        identity = registration.get("opponent", {}).get("gtp_identity", {})
        expected_commands = {"protocol_version", "name", "version", "list_commands"}
        if set(identity) != expected_commands or \
                any(not str(identity[name]).startswith("=") for name in expected_commands):
            raise RuntimeError("registered opponent GTP identity is incomplete")
    if (registration.get("schema") == "fold-go-match-registration/v3"
            or development):
        opponent = registration.get("opponent", {})
        if not isinstance(opponent.get("invocation_cwd"), str) or \
                not isinstance(opponent.get("command_file_bindings"), list):
            raise RuntimeError("registered opponent command provenance is incomplete")
        if require_current_source:
            for binding in opponent["command_file_bindings"]:
                path = Path(binding["resolved_path"])
                if not path.is_file() or path.stat().st_size != binding["bytes"] or \
                        sha256(path) != binding["sha256"]:
                    raise RuntimeError(
                        f"registered opponent command file drift: {binding['argument']}")
    if require_current_source:
        source = ROOT / registration["source_file"]
        if sha256(source) != registration["source_sha256"]:
            raise RuntimeError("registered match source no longer matches the checkout")
    verified_games = 0
    replay_result = {"SFT": 0, "Opponent": 0, "Draw": 0}
    for game_binding in match.get("games", []):
        game_path = directory / game_binding["file"]
        if sha256(game_path) != game_binding["sha256"]:
            raise RuntimeError(f"game receipt hash mismatch: {game_binding['file']}")
        game = json.loads(game_path.read_text())
        if game.get(binding_field) != registration_sha:
            raise RuntimeError(f"game configuration hash mismatch: {game_binding['file']}")
        expected_game_schemas = ({
            "fold-go-development-game/v1", "fold-go-development-game/v2"}
            if development else
            {"fold-go-game-receipt/v1", "fold-go-game-receipt/v2"})
        if game.get("schema") not in expected_game_schemas:
            raise RuntimeError(f"unsupported game receipt: {game_binding['file']}")
        if game.get("status") != "completed" or not game.get("gtp_transcript"):
            raise RuntimeError(f"incomplete game receipt: {game_binding['file']}")
        board = go.SFTGoBoard(registration["board_size"], komi=registration["komi"])
        passes = 0
        resigned_by = None
        for expected_ply, move_row in enumerate(game.get("moves", []), 1):
            if move_row.get("ply") != expected_ply:
                raise RuntimeError(f"non-contiguous ply receipt: {game_binding['file']}")
            expected_colour = 1 if expected_ply % 2 == 1 else 2
            if move_row.get("colour") != ("B" if expected_colour == 1 else "W"):
                raise RuntimeError(f"move colour mismatch: {game_binding['file']}")
            if (game["schema"].endswith("/v2")
                    and move_row.get("actor") == "SFT"):
                _verify_search_decision(
                    board, move_row, expected_colour, passes > 0,
                    registration, game_binding["file"])
            move = go.gtp_to_index(move_row["move"], board.size)
            if move == go.RESIGN:
                resigned_by = expected_colour
                if expected_ply != len(game["moves"]):
                    raise RuntimeError(f"moves recorded after resignation: {game_binding['file']}")
                break
            if not board.play_move(move, expected_colour):
                raise RuntimeError(f"semantic replay rejected move: {game_binding['file']}")
            passes = passes + 1 if move is go.PASS else 0
        if resigned_by is None and passes < 2:
            raise RuntimeError(f"completed game did not end pass-pass: {game_binding['file']}")
        if game.get("final_position") != board.position_key():
            raise RuntimeError(f"final position mismatch: {game_binding['file']}")
        history_sha = hashlib.sha256(
            "\n".join(sorted(board.history)).encode()).hexdigest()
        if game.get("complete_history_sha256") != history_sha:
            raise RuntimeError(f"complete history mismatch: {game_binding['file']}")
        black, white = go.get_area_score(board)
        white += board.komi
        if game.get("score") != {"black": black, "white_including_komi": white}:
            raise RuntimeError(f"score mismatch: {game_binding['file']}")
        if resigned_by is not None:
            winner_colour = "White" if resigned_by == 1 else "Black"
        elif black == white:
            winner_colour = "Draw"
        else:
            winner_colour = "Black" if black > white else "White"
        if game.get("winner_colour") != winner_colour:
            raise RuntimeError(f"winner colour mismatch: {game_binding['file']}")
        sft_colour = game["sft_side"]
        winner = "Draw" if winner_colour == "Draw" else (
            "SFT" if winner_colour == sft_colour else "Opponent")
        if game.get("winner") != winner:
            raise RuntimeError(f"winner attribution mismatch: {game_binding['file']}")
        replay_result[winner] += 1
        verified_games += 1
    if match.get("status") == "completed" and verified_games != registration["rounds"]:
        raise RuntimeError("completed match does not bind every registered round")
    declared_result = dict(match.get("result", {}))
    declared_result.setdefault("Draw", 0)
    if match.get("status") == "completed" and declared_result != replay_result:
        raise RuntimeError("match tally differs from semantic replay")
    return {
        "schema": "fold-go-match-verification/v1",
        "status": "verified",
        "match_status": match["status"],
        "run_kind": "development" if development else "measurement",
        "verified_games": verified_games,
        "configuration_sha256": registration_sha,
        "source_sha256": registration["source_sha256"],
        "opponent_executable_sha256": registration["opponent"]["executable_sha256"],
        "opponent_command_files": len(
            registration["opponent"].get("command_file_bindings", [])),
        "semantic_replay": "passed",
    }


def _selected_candidate(rows: list[dict]) -> str | None:
    selected = None
    selected_value = go.VALUE_FLOOR
    for row in rows:
        if row.get("status") != "completed":
            return None
        value = go.pack_value(row["numerator"], row["denominator"])
        if go.value_greater(value, selected_value):
            selected = row["move"]
            selected_value = value
    return selected


def _verify_search_decision(board, move_row: dict, colour: int,
                            last_passed: bool, registration: dict,
                            game_file: str) -> None:
    decision = move_row.get("search_decision")
    if not isinstance(decision, dict) or decision.get("schema") \
            != "fold-go-search-decision/v1":
        raise RuntimeError(f"missing SFT search decision: {game_file}")
    history_sha = hashlib.sha256(
        "\n".join(sorted(board.history)).encode()).hexdigest()
    expected_candidates = [
        go.index_to_gtp(move, board.size)
        for move in go.root_candidates(board, colour)
    ]
    if (decision.get("board_before") != board.position_key()
            or decision.get("complete_history_sha256") != history_sha
            or decision.get("to_move") != ("B" if colour == 1 else "W")
            or decision.get("root_last_passed") is not bool(last_passed)
            or decision.get("search_ceiling") != registration["search_ceiling"]
            or decision.get("node_budget_per_root_candidate")
            != registration["node_budget_per_root_candidate"]
            or decision.get("candidate_order") != expected_candidates
            or decision.get("selected") != move_row["move"]):
        raise RuntimeError(f"SFT search-decision binding mismatch: {game_file}")
    completed_depth = 0
    selected = expected_candidates[0]
    for expected_depth, depth in enumerate(decision.get("depths", []), 1):
        if depth.get("depth") != expected_depth:
            raise RuntimeError(f"non-contiguous search depth: {game_file}")
        if [row.get("move") for row in depth.get("candidates", [])] \
                != expected_candidates:
            raise RuntimeError(f"search candidate order mismatch: {game_file}")
        calculated = _selected_candidate(depth["candidates"])
        if depth.get("status") == "completed":
            if depth.get("selected") != calculated:
                raise RuntimeError(f"search argmax mismatch: {game_file}")
            if calculated is not None:
                selected = calculated
                completed_depth = expected_depth
        else:
            if depth.get("status") != "node-budget-incomplete" \
                    or calculated is not None or depth.get("selected") is not None:
                raise RuntimeError(f"invalid incomplete search pass: {game_file}")
            break
    if (decision.get("completed_depth") != completed_depth
            or decision.get("selected") != selected):
        raise RuntimeError(f"search final-selection mismatch: {game_file}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--allow-source-drift", action="store_true")
    args = parser.parse_args()
    print(json.dumps(verify_match(
        args.directory, require_current_source=not args.allow_source_drift), sort_keys=True))


if __name__ == "__main__":
    main()

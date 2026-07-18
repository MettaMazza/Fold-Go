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
    match_path = directory / "match.json"
    registration = json.loads(registration_path.read_text())
    match = json.loads(match_path.read_text())
    registration_sha = sha256(registration_path)
    if match.get("registration_sha256") != registration_sha:
        raise RuntimeError("match registration hash mismatch")
    if registration.get("schema") not in {
            "fold-go-match-registration/v1", "fold-go-match-registration/v2"}:
        raise RuntimeError("unsupported match registration")
    if match.get("schema") != "fold-go-match-receipt/v1":
        raise RuntimeError("unsupported match receipt")
    if registration.get("schema") == "fold-go-match-registration/v2":
        identity = registration.get("opponent", {}).get("gtp_identity", {})
        expected_commands = {"protocol_version", "name", "version", "list_commands"}
        if set(identity) != expected_commands or \
                any(not str(identity[name]).startswith("=") for name in expected_commands):
            raise RuntimeError("registered opponent GTP identity is incomplete")
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
        if game.get("registration_sha256") != registration_sha:
            raise RuntimeError(f"game registration hash mismatch: {game_binding['file']}")
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
        "verified_games": verified_games,
        "registration_sha256": registration_sha,
        "source_sha256": registration["source_sha256"],
        "opponent_executable_sha256": registration["opponent"]["executable_sha256"],
        "semantic_replay": "passed",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--allow-source-drift", action="store_true")
    args = parser.parse_args()
    print(json.dumps(verify_match(
        args.directory, require_current_source=not args.allow_source_drift), sort_keys=True))


if __name__ == "__main__":
    main()

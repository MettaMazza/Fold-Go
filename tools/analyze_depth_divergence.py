#!/usr/bin/env python3
"""Explain the first SFT move divergence between two matched Go receipts.

The instrument replays the shared receipt prefix, evaluates every current root
candidate at both named depths, and preserves the exact rational values used by
the engine.  It does not change move selection or declare a project result.
"""
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
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def load_games(directory: Path) -> list[tuple[Path, dict]]:
    match = json.loads((directory / "match.json").read_text())
    return [
        (directory / held["file"],
         json.loads((directory / held["file"]).read_text()))
        for held in match["games"]
    ]


def move_identity(move: dict) -> tuple:
    return move["actor"], move["colour"], move["move"]


def selected(rows: list[dict]) -> str | None:
    best = None
    best_value = go.VALUE_FLOOR
    for row in rows:
        if row["status"] != "completed":
            return None
        value = go.pack_value(row["numerator"], row["denominator"])
        if go.value_greater(value, best_value):
            best = row["move"]
            best_value = value
    return best


def evaluate(board: go.SFTGoBoard, colour: int, depth: int,
             root_last_passed: bool) -> dict:
    rows = []
    for move in go.root_candidates(board, colour):
        held_move, value = go._eval_root_candidate(
            (board, colour, move, depth, root_last_passed))
        if value is None:
            rows.append({"move": go.index_to_gtp(held_move, board.size),
                         "status": "node-budget-incomplete"})
        else:
            numerator, denominator = go.unpack_value(value)
            rows.append({
                "move": go.index_to_gtp(held_move, board.size),
                "status": "completed",
                "numerator": numerator,
                "denominator": denominator,
            })
    return {"depth": depth, "selected": selected(rows), "candidates": rows}


def replay_prefix(game: dict, prefix: int) -> tuple[go.SFTGoBoard, bool]:
    board = go.SFTGoBoard(5, komi=0)
    last_passed = False
    for move in game["moves"][:prefix]:
        colour = 1 if move["colour"] == "B" else 2
        point = go.gtp_to_index(move["move"], board.size)
        if not board.play_move(point, colour):
            raise RuntimeError(f"receipt replay failed at ply {move['ply']}")
        last_passed = point is go.PASS
    return board, last_passed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("shallower", type=Path)
    parser.add_argument("deeper", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    shallower = args.shallower.resolve()
    deeper = args.deeper.resolve()
    shallow_games = load_games(shallower)
    deep_games = load_games(deeper)
    if len(shallow_games) != len(deep_games):
        raise RuntimeError("matched receipts contain different game counts")

    analyses = []
    for (shallow_path, shallow), (deep_path, deep) in zip(
            shallow_games, deep_games):
        common = 0
        for left, right in zip(shallow["moves"], deep["moves"]):
            if move_identity(left) != move_identity(right):
                break
            common += 1
        if common >= min(len(shallow["moves"]), len(deep["moves"])):
            continue
        left = shallow["moves"][common]
        right = deep["moves"][common]
        if left["actor"] != "SFT" or right["actor"] != "SFT":
            raise RuntimeError("first matched divergence is not an SFT decision")
        board, last_passed = replay_prefix(shallow, common)
        colour = 1 if left["colour"] == "B" else 2
        analyses.append({
            "game": shallow["game"],
            "shared_prefix_plies": common,
            "colour": left["colour"],
            "shallower_receipt_move": left["move"],
            "deeper_receipt_move": right["move"],
            "root_last_passed": last_passed,
            "board_before_divergence": board.board,
            "evaluations": [
                evaluate(board, colour, 1, last_passed),
                evaluate(board, colour, 2, last_passed),
            ],
            "receipts": {
                "shallower_file": shallow_path.name,
                "shallower_sha256": sha256(shallow_path),
                "deeper_file": deep_path.name,
                "deeper_sha256": sha256(deep_path),
            },
        })

    result = {
        "schema": "fold-go-depth-divergence-analysis/v1",
        "status": "completed",
        "inputs": {
            "shallower_match_sha256": sha256(shallower / "match.json"),
            "deeper_match_sha256": sha256(deeper / "match.json"),
            "engine_source_sha256": sha256(ROOT / "tools/measure_go.py"),
            "instrument_source_sha256": sha256(Path(__file__)),
        },
        "analyses": analyses,
        "provenance": {
            "origin": "Codex-authored applied development instrument",
            "agent": "Codex",
            "model": "gpt-5.6-sol",
            "reasoning_level": "high",
            "authority": "Not Maria's official run, finding, loss, or rank conclusion.",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    stage = args.output.with_name(args.output.name + ".building")
    stage.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    stage.replace(args.output)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

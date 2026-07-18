#!/usr/bin/env python3
"""Seal an exhaustive bounded census of reachable augmented Go search states."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import measure_go as go


ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def enumerate_census(size: int, plies: int, comparison_depth: int) -> dict:
    if size < 1 or plies < 0 or comparison_depth < 0:
        raise ValueError("size must be positive; plies and comparison depth non-negative")
    frontier = [(go.SFTGoBoard(size), 1, False)]
    census = {}
    per_ply = []
    pass_pass_terminals = 0
    for ply in range(plies + 1):
        next_frontier = []
        new_at_ply = 0
        for board, colour, last_passed in frontier:
            key = go.canonical_augmented_state(board, colour, last_passed)
            if key in census:
                continue
            census[key] = (board, colour, last_passed, ply)
            new_at_ply += 1
            if ply == plies:
                continue
            for move in board.get_legal_moves(colour) + [go.PASS]:
                if move is go.PASS and last_passed:
                    pass_pass_terminals += 1
                    continue
                child = board.copy()
                if not child.play_move(move, colour):
                    raise RuntimeError("reachable-state generator produced an illegal action")
                next_frontier.append((child, 3 - colour, move is go.PASS))
        per_ply.append({"ply": ply, "new_augmented_states": new_at_ply})
        frontier = next_frontier

    disagreements = []
    state_records = []
    for key, (board, colour, last_passed, first_ply) in sorted(
            census.items(), key=lambda item: repr(item[0])):
        go.tt_gen[0] += 1
        go.nodes_left[0] = go.NODE_BUDGET
        go.pass_aborted[0] = 0
        with_tt = go.alphabeta_sft(
            board, comparison_depth, go.VALUE_FLOOR, go.VALUE_CEILING,
            colour, last_passed, True)
        if go.pass_aborted[0]:
            raise RuntimeError("typed-TT comparison pass exceeded its node budget")
        go.nodes_left[0] = go.NODE_BUDGET
        go.pass_aborted[0] = 0
        without_tt = go.alphabeta_sft(
            board, comparison_depth, go.VALUE_FLOOR, go.VALUE_CEILING,
            colour, last_passed, False)
        if go.pass_aborted[0]:
            raise RuntimeError("no-cache comparison pass exceeded its node budget")
        canonical_board, canonical_colour, canonical_pass, canonical_history = key
        record = {
            "board": canonical_board,
            "to_move": canonical_colour,
            "last_passed": canonical_pass,
            "history": list(canonical_history),
            "first_reached_ply": first_ply,
            "value_with_tt": with_tt,
            "value_without_tt": without_tt,
        }
        state_records.append(record)
        if with_tt != without_tt:
            disagreements.append(record)
    return {
        "schema": "fold-go-augmented-state-census/v1",
        "status": "completed" if not disagreements else "failed",
        "board_size": size,
        "max_plies": plies,
        "comparison_depth": comparison_depth,
        "augmented_state_count": len(census),
        "pass_pass_terminals": pass_pass_terminals,
        "per_ply": per_ply,
        "comparison_count": len(state_records),
        "disagreement_count": len(disagreements),
        "states": state_records,
        "source_commit": git_commit(),
        "source_sha256": {
            "tools/measure_go.py": sha256_file(ROOT / "tools/measure_go.py"),
            "tools/augmented_state_census.py": sha256_file(
                ROOT / "tools/augmented_state_census.py"),
        },
    }


def write_census(output: Path, size: int, plies: int, comparison_depth: int) -> dict:
    output = output.resolve()
    if output.exists():
        raise FileExistsError(f"census receipt already exists: {output}")
    record = enumerate_census(size, plies, comparison_depth)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--size", type=int, default=2)
    parser.add_argument("--plies", type=int, default=6)
    parser.add_argument("--comparison-depth", type=int, default=1)
    args = parser.parse_args()
    record = write_census(args.output, args.size, args.plies, args.comparison_depth)
    print(json.dumps({key: record[key] for key in (
        "status", "augmented_state_count", "pass_pass_terminals",
        "comparison_count", "disagreement_count")}, sort_keys=True))


if __name__ == "__main__":
    main()

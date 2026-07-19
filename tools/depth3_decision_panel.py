#!/usr/bin/env python3
"""Seal current exact decision traces on two real depth-3 game positions.

The positions are the first SFT turn from each colour in the preserved matched
5x5 GNU Go development receipt.  This is bounded calculation evidence, not a
new game, benchmark gate, Maria-authored conclusion, win or loss.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time

from tools import measure_go


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/match_receipts/development_matched_5x5_d3_seed20260719"
OUTPUT = ROOT / "tools/match_receipts/development_depth3_decision_panel_20260719.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(f"decision panel exists: {OUTPUT}")
    configuration = json.loads((SOURCE / "development_configuration.json").read_text())
    if (configuration.get("board_size") != 5
            or configuration.get("search_ceiling") != 3
            or configuration.get("komi") != 0):
        raise RuntimeError("source development protocol identity drift")

    rows = []
    for game_path in sorted(SOURCE.glob("game-*.json")):
        game = json.loads(game_path.read_text())
        board = measure_go.SFTGoBoard(5, komi=0)
        last_passed = False
        selected_source = None
        for move_row in game["moves"]:
            colour = 1 if move_row["colour"] == "B" else 2
            if move_row["actor"] == "SFT":
                selected_source = move_row
                began = time.monotonic()
                decision = {}
                move = measure_go.select_sft_move(
                    board, colour, ceiling=3,
                    root_last_passed=last_passed,
                    decision_trace=decision)
                elapsed = time.monotonic() - began
                observed = measure_go.index_to_gtp(move, 5)
                rows.append({
                    "source_game": game_path.name,
                    "source_game_sha256": sha256(game_path),
                    "source_ply": move_row["ply"],
                    "sft_side": game["sft_side"],
                    "recorded_move": move_row["move"],
                    "current_move": observed,
                    "move_identity": observed == move_row["move"],
                    "seconds": elapsed,
                    "decision": decision,
                })
                break
            move = measure_go.gtp_to_index(move_row["move"], 5)
            if move == measure_go.RESIGN or not board.play_move(move, colour):
                raise RuntimeError("source game did not replay to selected position")
            last_passed = move is measure_go.PASS
        if selected_source is None:
            raise RuntimeError(f"source game has no SFT move: {game_path.name}")

    result = {
        "schema": "fold-go-depth3-decision-panel/v1",
        "status": "completed",
        "result_type": "measured implementation result",
        "governance_authority": False,
        "benchmark_authority": False,
        "provenance": {
            "origin": "Codex implementation development run",
            "agent": "Codex",
            "model": "gpt-5.6-sol",
            "reasoning_level": "high",
            "authority": "Maria Smith assigns conclusions and official status.",
        },
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "declared_purpose": (
            "Bind complete exact depth-3 candidate rows to one real first-turn "
            "position for each SFT colour from the preserved matched games."),
        "protocol": {
            "board_size": 5,
            "komi": 0,
            "search_ceiling": 3,
            "position_selection": "first SFT turn from each colour schedule",
            "source_configuration_sha256": sha256(
                SOURCE / "development_configuration.json"),
        },
        "rows": rows,
        "tally": {
            "positions": len(rows),
            "move_identity": sum(row["move_identity"] for row in rows),
            "completed_depth_passes": sum(
                sum(depth["status"] == "completed"
                    for depth in row["decision"]["depths"])
                for row in rows),
            "exact_candidate_rows": sum(
                sum(len(depth["candidates"])
                    for depth in row["decision"]["depths"])
                for row in rows),
        },
        "sources": {
            "tools/measure_go.py": sha256(ROOT / "tools/measure_go.py"),
            "tools/depth3_decision_panel.py": sha256(Path(__file__)),
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "completed", **result["tally"]}, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Seal exact depth-3 decisions on each colour's second real SFT turn."""
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
OUTPUT = ROOT / "tools/match_receipts/development_depth3_second_turn_panel_20260719.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(f"decision panel exists: {OUTPUT}")
    rows = []
    for game_path in sorted(SOURCE.glob("game-*.json")):
        game = json.loads(game_path.read_text())
        board = measure_go.SFTGoBoard(5, komi=0)
        last_passed = False
        seen_sft_turns = 0
        for move_row in game["moves"]:
            colour = 1 if move_row["colour"] == "B" else 2
            if move_row["actor"] == "SFT":
                seen_sft_turns += 1
                if seen_sft_turns == 2:
                    decision = {}
                    began = time.monotonic()
                    move = measure_go.select_sft_move(
                        board, colour, ceiling=3,
                        root_last_passed=last_passed,
                        decision_trace=decision)
                    current = measure_go.index_to_gtp(move, 5)
                    rows.append({
                        "source_game": game_path.name,
                        "source_game_sha256": sha256(game_path),
                        "source_ply": move_row["ply"],
                        "sft_side": game["sft_side"],
                        "recorded_move": move_row["move"],
                        "current_move": current,
                        "move_identity": current == move_row["move"],
                        "seconds": time.monotonic() - began,
                        "decision": decision,
                    })
                    break
            move = measure_go.gtp_to_index(move_row["move"], 5)
            if move == measure_go.RESIGN or not board.play_move(move, colour):
                raise RuntimeError("source game did not replay")
            last_passed = move is measure_go.PASS
        else:
            raise RuntimeError(f"source game lacks a second SFT turn: {game_path}")

    tally = {
        "positions": len(rows),
        "move_identity": sum(row["move_identity"] for row in rows),
        "completed_depth_passes": sum(
            sum(depth["status"] == "completed"
                for depth in row["decision"]["depths"]) for row in rows),
        "exact_candidate_rows": sum(
            sum(len(depth["candidates"])
                for depth in row["decision"]["depths"]) for row in rows),
    }
    result = {
        "schema": "fold-go-depth3-second-turn-panel/v1",
        "status": "completed",
        "result_type": "measured implementation result",
        "governance_authority": False,
        "benchmark_authority": False,
        "provenance": {
            "origin": "Codex implementation development run",
            "agent": "Codex", "model": "gpt-5.6-sol",
            "reasoning_level": "high",
            "authority": "Maria Smith assigns conclusions and match timing.",
        },
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "declared_purpose": (
            "Extend complete exact decision trace from the opening to the "
            "second real SFT turn in each colour schedule."),
        "position_selection": "second SFT turn in each preserved game",
        "rows": rows,
        "tally": tally,
        "sources": {
            "tools/measure_go.py": sha256(ROOT / "tools/measure_go.py"),
            "tools/depth3_second_turn_panel.py": sha256(Path(__file__)),
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "completed", **tally}, sort_keys=True))


if __name__ == "__main__":
    main()

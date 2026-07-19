#!/usr/bin/env python3
"""
SFT Go Engine — Zero-Parameter, Fully SFT-Compliant

Every evaluation is the exact share of the One: my_command / (my_command + their_command).
Values are packed as num * PACK_BASE (2^32) + den (exact rational, cross-multiplication comparison).
No floats, no negatives, no irrationals, no arbitrary constants on the evaluation side.
Infrastructure constants are powers of 2 (fold-natural). Hash uses prime 131.

Domain: (0, 1]. The fold: x -> 2x mod 1. Generators: binary 2, colour 3.
"""
import sys
import subprocess
import os
import collections
import argparse
import hashlib
import json
import platform
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

PASS = None
RESIGN = "resign"

# ==================== ZERO-PARAMETER SFT GO ENGINE ====================

class SFTGoBoard:
    def __init__(self, size=9, komi=0):
        self.size = size
        self.komi = int(komi)
        self.board = [0] * (size * size)  # 0: empty, 1: black, 2: white
        self.ko_square = None
        # Complete positional-superko state.  The initial position is part of the
        # history; passes do not invent a new position.
        self.history = {self.position_key()}

    def position_key(self):
        return "".join(map(str, self.board))

    def copy(self):
        nb = SFTGoBoard(self.size, self.komi)
        nb.board = list(self.board)
        nb.ko_square = self.ko_square
        nb.history = set(self.history)
        return nb

    def get_neighbors(self, idx):
        neighbors = []
        r, c = idx // self.size, idx % self.size
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                neighbors.append(nr * self.size + nc)
        return neighbors

    def get_group(self, start_idx):
        color = self.board[start_idx]
        if color == 0:
            return set(), set()
        group = {start_idx}
        liberties = set()
        queue = collections.deque([start_idx])
        visited = {start_idx}
        while queue:
            curr = queue.popleft()
            for n in self.get_neighbors(curr):
                if self.board[n] == 0:
                    liberties.add(n)
                elif self.board[n] == color and n not in visited:
                    visited.add(n)
                    group.add(n)
                    queue.append(n)
        return group, liberties

    def is_legal(self, idx, color):
        if self.board[idx] != 0:
            return False
        if idx == self.ko_square:
            return False
        test_board = self.copy()
        test_board.board[idx] = color
        opponent = 3 - color
        captured_indices = []
        for n in test_board.get_neighbors(idx):
            if test_board.board[n] == opponent:
                grp, libs = test_board.get_group(n)
                if len(libs) == 0:
                    captured_indices.extend(grp)
        for c_idx in captured_indices:
            test_board.board[c_idx] = 0
        my_grp, my_libs = test_board.get_group(idx)
        if len(my_libs) == 0:
            return False
        state_str = "".join(map(str, test_board.board))
        if state_str in self.history:
            return False
        return True

    def play_move(self, idx, color):
        if idx is None:  # Pass
            self.ko_square = None
            return True
        if not self.is_legal(idx, color):
            return False
        self.board[idx] = color
        opponent = 3 - color
        captured_indices = []
        for n in self.get_neighbors(idx):
            if self.board[n] == opponent:
                grp, libs = self.get_group(n)
                if len(libs) == 0:
                    captured_indices.extend(grp)
        for c_idx in captured_indices:
            self.board[c_idx] = 0
        # Legality is pure positional superko (Tromp-Taylor): the history check in
        # is_legal already forbids any repetition. No ad-hoc ko square — it was
        # stricter than the real rules and could reject legal opponent moves.
        self.ko_square = None
        self.history.add(self.position_key())
        return True

    def get_legal_moves(self, color):
        moves = []
        for i in range(self.size * self.size):
            if self.is_legal(i, color):
                moves.append(i)
        return moves


# ==================== FOLD-NATURAL HASHING ====================
# Uses the chess engine's own approach: multiply-add with prime 131,
# modular reduction by a prime below 2^55. Pure integer arithmetic.

HASH_PRIME = 36028797018963913  # prime < 2^55, same as chess engine

def get_transformed_index(p, size, t):
    row, col = p // size, p % size
    if t == 0:
        r2, c2 = row, col
    elif t == 1:
        r2, c2 = size - 1 - row, col
    elif t == 2:
        r2, c2 = row, size - 1 - col
    elif t == 3:
        r2, c2 = size - 1 - row, size - 1 - col
    elif t == 4:
        r2, c2 = col, row
    elif t == 5:
        r2, c2 = size - 1 - col, row
    elif t == 6:
        r2, c2 = col, size - 1 - row
    else:
        r2, c2 = size - 1 - col, size - 1 - row
    return r2 * size + c2

def transform_position(position, size, transform):
    transformed = ["0"] * (size * size)
    for index, value in enumerate(position):
        transformed[get_transformed_index(index, size, transform)] = str(value)
    return "".join(transformed)


def canonical_augmented_state(board, to_move_color, last_passed):
    """Canonicalize board and the complete PSK history under one transform."""
    candidates = []
    current = board.position_key()
    for transform in range(8):
        transformed_board = transform_position(current, board.size, transform)
        transformed_history = tuple(sorted(
            transform_position(position, board.size, transform)
            for position in board.history
        ))
        candidates.append((transformed_board, to_move_color, int(bool(last_passed)),
                           transformed_history))
    return min(candidates)


def fold_hash(state_key):
    """Deterministic hash of an exact augmented-state key."""
    k = 0
    board_key, to_move_color, last_passed, history = state_key
    for value in board_key:
        k = (k * 131 + int(value)) % HASH_PRIME
    for value in (to_move_color, last_passed, len(history)):
        k = (k * 131 + value) % HASH_PRIME
    for position in history:
        for value in position:
            k = (k * 131 + int(value)) % HASH_PRIME
        k = (k * 131 + 3) % HASH_PRIME
    return k


# ==================== SFT COUNTED COMMAND (EVALUATION) ====================
# The exact analogue of the chess engine's side_units / share:
# A stone's "reach" is its group's unique liberty count.
# Position value = black_command / (black_command + white_command)
# — a fraction of the One, returned as (num, den).

def counted_command(board):
    """Returns (black_units, white_units) — both non-negative integers.
    Value = black / (black + white), compared by cross-multiplication."""
    sz = board.size
    visited = [False] * (sz * sz)
    black_units = 0
    white_units = 0

    for i in range(sz * sz):
        if board.board[i] != 0 and not visited[i]:
            grp, libs = board.get_group(i)
            for g in grp:
                visited[g] = True
            # Counted reach = number of unique liberties (geometric fact).
            # A group in atari (1 liberty) is naturally weak — reach is 1.
            # A dead group (0 liberties) is removed by the rules — reach is 0.
            reach = len(libs)
            # Stones themselves are also counted command (they hold territory).
            stones = len(grp)
            if board.board[i] == 1:
                black_units += reach + stones
            else:
                white_units += reach + stones

    # Territory: empty regions bordered by one colour only.
    # This is area scoring — a counting fact of the board geometry.
    visited2 = [False] * (sz * sz)
    for i in range(sz * sz):
        if board.board[i] == 0 and not visited2[i]:
            region = {i}
            queue = collections.deque([i])
            visited2[i] = True
            borders = set()
            while queue:
                curr = queue.popleft()
                for n in board.get_neighbors(curr):
                    if board.board[n] == 0:
                        if not visited2[n]:
                            visited2[n] = True
                            region.add(n)
                            queue.append(n)
                    else:
                        borders.add(board.board[n])
            if len(borders) == 1:
                # Geometric Eye criterion (counted, no constants): an empty region
                # is command only if it is tightly bound — bordered by one colour
                # AND every point of the region touches that colour's stones.
                # Open frameworks with unbound interior points count nothing.
                border_color = list(borders)[0]
                tightly_bound = all(
                    any(board.board[n] == border_color for n in board.get_neighbors(p))
                    for p in region
                )
                if tightly_bound:
                    if border_color == 1:
                        black_units += len(region)
                    elif border_color == 2:
                        white_units += len(region)

    # Guarantee non-zero denominator (domain (0,1] — no zero).
    if black_units == 0 and white_units == 0:
        black_units = 1
        white_units = 1

    return black_units, white_units


PACK_BASE = 1 << 32  # 4294967296 — the 2^32 domain the papers specify


def pack_value(num, den):
    """Pack a fraction num/den into num * PACK_BASE + den."""
    return num * PACK_BASE + den


def unpack_value(packed):
    """Unpack into (num, den)."""
    den = packed % PACK_BASE
    num = packed // PACK_BASE
    return num, den


def value_greater(packed_a, packed_b):
    """a/b > c/d  ⟺  a*d > c*b — exact cross-multiplication, no floats."""
    a_num, a_den = unpack_value(packed_a)
    b_num, b_den = unpack_value(packed_b)
    return a_num * b_den > b_num * a_den


# The floor and ceiling of the domain (0, 1]:
# Floor = 0/1 (approaches zero — the minimum, used as alpha init)
# Ceiling = 1/1 (the One — the maximum, used as beta init)
# Mate/checkmate equivalent: 1023/1024 (almost the One, for winning)
# Loss equivalent: 1/1024 (almost zero, for losing)
VALUE_FLOOR = pack_value(0, 1)      # 0/1 — alpha init
VALUE_CEILING = pack_value(1, 1)    # 1/1 — beta init
VALUE_DRAW = pack_value(1, 2)       # 1/2 — the lock


# ==================== DYNAMIC SPARSE MOVE GENERATOR ====================
# Selects moves adjacent to existing groups (the active fronts).
# This is geometric pruning — not a free parameter.

def get_augmented_symmetries(board):
    """Transforms admitted by both the board and every positional-superko state."""
    board_key = board.position_key()
    symmetries = [0]
    for t in range(1, 8):
        if transform_position(board_key, board.size, t) != board_key:
            continue
        if all(transform_position(position, board.size, t) == position
               for position in board.history):
            symmetries.append(t)
    return symmetries

def get_orbit_representative(p, size, allowed_symmetries):
    """Dihedral symmetry orbit reduction over valid symmetries."""
    rep = p
    for t in allowed_symmetries:
        q = get_transformed_index(p, size, t)
        if q < rep:
            rep = q
    return rep


def get_dynamic_sparse_moves(board, to_move_color, legal_moves, tactical_only=False):
    """Select candidate moves from the active fronts (geometric pruning) and orbit reductions."""
    size = board.size
    
    # Calculate active symmetries for the current board state
    active_symmetries = get_augmented_symmetries(board)
    
    empty = all(x == 0 for x in board.board)
    if empty:
        # The empty board has no stones from which to privilege a local front.
        # Preserve one representative of every legal move orbit instead of
        # importing a hand-listed star-point subset for selected board sizes.
        return sorted({
            get_orbit_representative(move, size, active_symmetries)
            for move in legal_moves
        })

    visited = [False] * (size * size)
    fronts = set()

    for i in range(size * size):
        if board.board[i] != 0 and not visited[i]:
            grp, libs = board.get_group(i)
            for g in grp:
                visited[g] = True
            for lib in libs:
                fronts.add(lib)

    # A quiescence leaf has no derived liberty-count threshold with which to
    # declare one active front tactical and another inert. Retain every legal
    # front in both the ordinary and quiescence surfaces; the existing depth
    # bound is the complete stopping rule. This removes the former authored
    # ``<= 2`` selector without adding a replacement preference.
    candidates = {move for move in legal_moves if move in fronts}

    if not candidates:
        if tactical_only:
            return []
        candidates = set(legal_moves)
        
    # Apply orbit reduction only under symmetries of the complete augmented state.
    reps = set()
    for m in candidates:
        reps.add(get_orbit_representative(m, size, active_symmetries))
        
    return list(reps)


# ==================== TRANSPOSITION TABLE ====================
# Size = 2^18 = 262144 slots (fold-natural, same as chess engine).

TT_SIZE = 1 << 18  # 262144
tt_keys = [0] * TT_SIZE
tt_values = [0] * TT_SIZE
tt_depths = [0] * TT_SIZE
tt_stamps = [0] * TT_SIZE
tt_flags = [0] * TT_SIZE
tt_gen = [1]

TT_EXACT = 1
TT_LOWER = 2
TT_UPPER = 3


def value_at_least(left, right):
    return left == right or value_greater(left, right)


def value_at_most(left, right):
    return left == right or value_greater(right, left)


def tt_probe(state_key, depth, alpha, beta):
    """Probe an exact augmented state and respect its bound type."""
    slot = fold_hash(state_key) % TT_SIZE
    if not (tt_stamps[slot] == tt_gen[0] and tt_keys[slot] == state_key
            and tt_depths[slot] >= depth):
        return None, alpha, beta
    value = tt_values[slot]
    flag = tt_flags[slot]
    if flag == TT_EXACT:
        return value, alpha, beta
    if flag == TT_LOWER and value_greater(value, alpha):
        alpha = value
    elif flag == TT_UPPER and value_greater(beta, value):
        beta = value
    if value_at_least(alpha, beta):
        return value, alpha, beta
    return None, alpha, beta


def tt_store(state_key, depth, value, flag):
    """Store a typed bound with exact state verification."""
    slot = fold_hash(state_key) % TT_SIZE
    tt_keys[slot] = state_key
    tt_values[slot] = value
    tt_depths[slot] = depth
    tt_flags[slot] = flag
    tt_stamps[slot] = tt_gen[0]


# ==================== MOVE ORDERING HEURISTICS (SFT-COMPLIANT) ====================
history_table = [0] * 1024
killer_moves = [[-1, -1] for _ in range(64)]

# ==================== NODE BUDGET (FOLD-NATURAL) ====================

NODE_BUDGET = 1 << 19  # 524288 = 2^19
nodes_left = [NODE_BUDGET]
pass_aborted = [0]


# ==================== ALPHA-BETA SEARCH (SFT FRACTION-PAIR) ====================
# Values are packed as num * PACK_BASE (2^32) + den.
# Comparison is by cross-multiplication: a/b > c/d ⟺ a*d > c*b.
# The search mirrors the chess engine's search_value exactly.

def invert_value(packed):
    """Invert a value for the opponent: if mine is num/den, theirs is (den-num)/den."""
    num, den = unpack_value(packed)
    return pack_value(den - num, den)


def terminal_area_value(board, to_move_color):
    black, white = get_area_score(board)
    white += board.komi
    total = black + white
    if total <= 0:
        return VALUE_DRAW
    return pack_value(black if to_move_color == 1 else white, total)


def alphabeta_sft(board, depth, alpha, beta, to_move_color, last_passed=False,
                  use_tt=True):
    """SFT-compliant alpha-beta. Returns packed value (num * PACK_BASE (2^32) + den)."""
    # Hard node bound
    nodes_left[0] -= 1
    if nodes_left[0] < 0:
        pass_aborted[0] = 1
        return VALUE_DRAW  # placeholder — discarded by driver

    original_alpha, original_beta = alpha, beta
    state_key = canonical_augmented_state(board, to_move_color, last_passed)
    if use_tt:
        tt_val, alpha, beta = tt_probe(state_key, depth, alpha, beta)
        if tt_val is not None:
            return tt_val

    if depth <= 0:
        # SFT Leaf evaluation / Stand pat for Quiescence Search
        b_units, w_units = counted_command(board)
        total = b_units + w_units
        stand_pat = pack_value(b_units, total) if to_move_color == 1 else pack_value(w_units, total)

        if depth <= -8:  # Q-search ceiling (power of 2)
            return stand_pat
            
        if value_greater(stand_pat, beta) or stand_pat == beta:
            return stand_pat
        if value_greater(stand_pat, alpha):
            alpha = stand_pat

    legal_moves = board.get_legal_moves(to_move_color)
    tactical_only = (depth <= 0)
    if board.size <= 3:
        candidates = legal_moves
    else:
        candidates = get_dynamic_sparse_moves(
            board, to_move_color, legal_moves, tactical_only=tactical_only)

    # Move ordering: evaluate each candidate at depth 0 (counted command) + Heuristics
    move_scores = []
    tengen_r, tengen_c = board.size // 2, board.size // 2
    for m in candidates:
        score = 0
        if depth > 0:
            if m == killer_moves[depth][0]:
                score += 1000000
            elif m == killer_moves[depth][1]:
                score += 500000
            score += history_table[m]
            
        nb = board.copy()
        nb.play_move(m, to_move_color)
        b_u, w_u = counted_command(nb)
        total = b_u + w_u
        my_num = b_u if to_move_color == 1 else w_u
        
        # Tengen integer distance (D^2). Smaller is closer to center.
        mr, mc = m // board.size, m % board.size
        d2 = (mr - tengen_r)**2 + (mc - tengen_c)**2
        
        # Sort key: Heuristics, then shallow evaluation my_num, then Tengen
        move_scores.append(((score, my_num), -d2, m))

    move_scores.sort(reverse=True, key=lambda x: (x[0][0], x[0][1], x[1]))

    best = VALUE_FLOOR  # 0/1 — the worst possible
    a = alpha

    for _, _, m in move_scores:
        if pass_aborted[0] == 1:
            break
        nb = board.copy()
        nb.play_move(m, to_move_color)
        # Recurse for the opponent, then invert.
        child_val = alphabeta_sft(nb, depth - 1, invert_value(beta), invert_value(a),
                                   3 - to_move_color, False, use_tt)
        if pass_aborted[0] == 1:
            break
        my_val = invert_value(child_val)

        if value_greater(my_val, best):
            best = my_val
        if value_greater(my_val, a):
            a = my_val
        if value_greater(a, beta) or a == beta:
            # Beta cutoff
            if depth > 0:
                history_table[m] += (1 << depth)
                if killer_moves[depth][0] != m:
                    killer_moves[depth][1] = killer_moves[depth][0]
                    killer_moves[depth][0] = m
            if use_tt:
                tt_store(state_key, depth, best, TT_LOWER)
            return best

    # Pass is an action at every node, not a fallback for move exhaustion.
    if pass_aborted[0] == 1:
        return VALUE_DRAW
    if last_passed:
        my_val = terminal_area_value(board, to_move_color)
    else:
        child_val = alphabeta_sft(board, depth - 1, invert_value(beta), invert_value(a),
                                   3 - to_move_color, True, use_tt)
        my_val = invert_value(child_val)
    if pass_aborted[0] == 0 and value_greater(my_val, best):
        best = my_val

    if value_at_most(best, original_alpha):
        flag = TT_UPPER
    elif value_at_least(best, original_beta):
        flag = TT_LOWER
    else:
        flag = TT_EXACT
    if use_tt:
        tt_store(state_key, depth, best, flag)
    return best


# ==================== MOVE SELECTION (ITERATIVE DEEPENING, PARALLEL ROOT) ====================
# Depth 1, 2, 3, ... up to the ceiling; the best move from the deepest COMPLETED
# pass plays. The root candidates are partitioned across worker processes — one
# per CPU core, a counted structural resource, not a tuned constant. Each
# candidate subtree is searched independently over the FULL value window with a
# fresh table and a fresh 2^19 node budget, so every returned value is the exact
# minimax value of that subtree. The parent reduces by exact cross-multiplication
# comparison in fixed candidate order (lowest board index wins ties), so the
# chosen move is identical regardless of worker scheduling — deterministic.

import multiprocessing as _mp

_POOL = [None]


def _get_pool():
    if _POOL[0] is None:
        ctx = _mp.get_context("fork")
        _POOL[0] = ctx.Pool(_mp.cpu_count())
    return _POOL[0]


def _eval_root_candidate(task):
    board, color, m, depth, root_last_passed = task
    # Fresh, task-local search state: no cross-task reuse (determinism).
    tt_gen[0] += 1
    nodes_left[0] = NODE_BUDGET
    pass_aborted[0] = 0
    for i in range(len(history_table)):
        history_table[i] = 0
    for km in killer_moves:
        km[0] = -1
        km[1] = -1
    # A pass after the opponent's pass ends the game at this root. Score the
    # literal terminal board; do not enter another search node and silently
    # reinterpret it as a first pass.
    if m is PASS and root_last_passed:
        return (m, terminal_area_value(board, color))
    nb = board.copy()
    nb.play_move(m, color)
    child_val = alphabeta_sft(nb, depth - 1, invert_value(VALUE_CEILING),
                              invert_value(VALUE_FLOOR), 3 - color, m is PASS)
    if pass_aborted[0] == 1:
        return (m, None)  # honest abort: this pass is incomplete
    return (m, invert_value(child_val))


def root_candidates(board, color):
    """Every root includes pass; point candidates retain deterministic order."""
    legal_moves = board.get_legal_moves(color)
    if board.size <= 3:
        candidates = sorted(legal_moves)
    else:
        candidates = sorted(get_dynamic_sparse_moves(board, color, legal_moves))
    return candidates + [PASS]


def _decision_row(move, value, size):
    if value is None:
        return {"move": index_to_gtp(move, size),
                "status": "node-budget-incomplete"}
    numerator, denominator = unpack_value(value)
    return {
        "move": index_to_gtp(move, size),
        "status": "completed",
        "numerator": numerator,
        "denominator": denominator,
    }


def select_sft_move(board, color, ceiling=8, root_last_passed=False,
                    decision_trace=None):
    """Select the best move and optionally expose the exact completed passes."""
    candidates = root_candidates(board, color)
    best_move = candidates[0]
    completed_depth = 0
    depth_receipts = []

    pool = _get_pool()
    for depth in range(1, ceiling + 1):
        results = pool.map(_eval_root_candidate,
                           [(board, color, m, depth, bool(root_last_passed))
                            for m in candidates])
        rows = [_decision_row(move, value, board.size)
                for move, value in results]
        if any(v is None for _, v in results):
            depth_receipts.append({
                "depth": depth,
                "status": "node-budget-incomplete",
                "selected": None,
                "candidates": rows,
            })
            break  # a subtree hit its node budget — keep the last completed pass
        depth_best_move = None
        depth_best_set = False
        depth_best_val = VALUE_FLOOR
        for m, v in results:  # fixed order: lowest index wins exact ties
            if value_greater(v, depth_best_val):
                depth_best_val = v
                depth_best_move = m
                depth_best_set = True
        if depth_best_set:
            best_move = depth_best_move
            completed_depth = depth
        depth_receipts.append({
            "depth": depth,
            "status": "completed",
            "selected": (index_to_gtp(depth_best_move, board.size)
                         if depth_best_set else None),
            "candidates": rows,
        })

    if decision_trace is not None:
        decision_trace.update({
            "schema": "fold-go-search-decision/v1",
            "board_before": board.position_key(),
            "complete_history_sha256": _sha256_bytes(
                "\n".join(sorted(board.history)).encode()),
            "to_move": "B" if color == 1 else "W",
            "root_last_passed": bool(root_last_passed),
            "search_ceiling": ceiling,
            "node_budget_per_root_candidate": NODE_BUDGET,
            "candidate_order": [index_to_gtp(move, board.size)
                                for move in candidates],
            "completed_depth": completed_depth,
            "selected": index_to_gtp(best_move, board.size),
            "depths": depth_receipts,
        })

    return best_move


# ==================== GTP PROTOCOL ENGINE ====================

def index_to_gtp(idx, size):
    if idx is None:
        return "pass"
    r, c = idx // size, idx % size
    col_str = "ABCDEFGHJKLMNOPQRSTY"[c]
    row_str = str(size - r)
    return col_str + row_str


def gtp_to_index(gtp_str, size):
    s = gtp_str.strip().upper()
    if s == "PASS":
        return PASS
    if s == "RESIGN":
        return RESIGN
    col_char = s[0]
    c = "ABCDEFGHJKLMNOPQRSTY".index(col_char)
    r = size - int(s[1:])
    return r * size + c


def run_gtp_server():
    size = 9
    board = SFTGoBoard(size)
    last_passed = False
    color_map = {"B": 1, "W": 2, "BLACK": 1, "WHITE": 2}

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            cmd_id = ""
            if parts[0].isdigit():
                cmd_id = parts.pop(0)

            cmd = parts[0]
            args = parts[1:]

            if cmd == "protocol_version":
                print(f"={cmd_id} 2\n")
            elif cmd == "name":
                print(f"={cmd_id} SFT_TypeZero_Go\n")
            elif cmd == "version":
                print(f"={cmd_id} 2.0\n")
            elif cmd == "known_command":
                known = cmd in ["protocol_version", "name", "version", "known_command",
                                "list_commands", "quit", "boardsize", "clear_board",
                                "komi", "play", "genmove"]
                print(f"={cmd_id} {'true' if known else 'false'}\n")
            elif cmd == "list_commands":
                print(f"={cmd_id} protocol_version\nname\nversion\nknown_command\n"
                      f"list_commands\nquit\nboardsize\nclear_board\nkomi\nplay\ngenmove\n")
            elif cmd == "quit":
                print(f"={cmd_id}\n")
                sys.exit(0)
            elif cmd == "boardsize":
                size = int(args[0])
                board = SFTGoBoard(size)
                last_passed = False
                print(f"={cmd_id}\n")
            elif cmd == "clear_board":
                board = SFTGoBoard(size, board.komi)
                last_passed = False
                print(f"={cmd_id}\n")
            elif cmd == "komi":
                komi_text = args[0]
                if not komi_text.lstrip("-").isdigit():
                    print(f"?{cmd_id} integer komi required\n")
                    sys.stdout.flush()
                    continue
                board.komi = int(komi_text)
                print(f"={cmd_id}\n")
            elif cmd == "play":
                color = color_map.get(args[0].upper(), 1)
                move = gtp_to_index(args[1], size)
                if move == RESIGN:
                    print(f"?{cmd_id} resign is not a play coordinate\n")
                    sys.stdout.flush()
                    continue
                ok = board.play_move(move, color)
                if ok:
                    last_passed = move is PASS
                    print(f"={cmd_id}\n")
                else:
                    print(f"?{cmd_id} illegal move\n")
            elif cmd == "genmove":
                color = color_map.get(args[0].upper(), 1)
                move = select_sft_move(
                    board, color, root_last_passed=last_passed)
                if not board.play_move(move, color):
                    raise RuntimeError("SFT selector returned an illegal move")
                last_passed = move is PASS
                print(f"={cmd_id} {index_to_gtp(move, size)}\n")
            else:
                print(f"?{cmd_id} unknown command\n")
            sys.stdout.flush()
        except Exception as e:
            print(f"? error: {str(e)}\n")
            sys.stdout.flush()


# ==================== TOURNAMENT REFEREE CLIENT ====================

class GTPClient:
    def __init__(self, cmd_line=None):
        self.cmd_line = cmd_line
        self.proc = None
        self.size = 9
        if cmd_line:
            self.proc = subprocess.Popen(
                cmd_line, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, text=True
            )

    def send(self, cmd_str):
        if self.proc:
            print(f">>> SEND: {cmd_str}")
            try:
                self.proc.stdin.write(cmd_str + "\n")
                self.proc.stdin.flush()
            except BrokenPipeError:
                print("!!! BROKEN PIPE.")
                raise
            response = []
            while True:
                line = self.proc.stdout.readline()
                if not line:
                    if not response:
                        raise RuntimeError(f"opponent EOF while answering {cmd_str!r}")
                    break
                if line.strip() == "":
                    break
                response.append(line.strip())
            print(f"<<< RECV: {response}")
            if not response:
                raise RuntimeError(f"empty opponent response to {cmd_str!r}")
            joined = "\n".join(response)
            if response[0].startswith("?"):
                raise RuntimeError(f"opponent rejected {cmd_str!r}: {joined}")
            if not response[0].startswith("="):
                raise RuntimeError(f"malformed opponent response to {cmd_str!r}: {joined}")
            return joined
        else:
            # Deterministic fallback opponent (no randomness — SFT compliant).
            # Plays the lowest-index legal move (deterministic, no random.choice).
            if "boardsize" in cmd_str:
                parts = cmd_str.split()
                self.size = int(parts[1])
                self.sim_board = SFTGoBoard(self.size)
                return "= "
            elif "clear_board" in cmd_str:
                self.sim_board = SFTGoBoard(self.size)
                return "= "
            elif "komi" in cmd_str:
                self.sim_board.komi = int(cmd_str.split()[1])
                return "= "
            elif "play" in cmd_str:
                parts = cmd_str.split()
                color = 1 if parts[1].upper() == "B" else 2
                move = gtp_to_index(parts[2], self.size)
                if move == RESIGN or not self.sim_board.play_move(move, color):
                    raise RuntimeError(f"fallback rejected play: {cmd_str}")
                return "= "
            elif "genmove" in cmd_str:
                parts = cmd_str.split()
                color = 1 if parts[1].upper() == "B" else 2
                legal = self.sim_board.get_legal_moves(color)
                if legal:
                    move = legal[0]  # deterministic: first legal move
                else:
                    move = None
                self.sim_board.play_move(move, color)
                return f"= {index_to_gtp(move, self.size)}"
            elif cmd_str == "protocol_version":
                return "= 2"
            elif cmd_str == "name":
                return "= deterministic-lowest-legal"
            elif cmd_str == "version":
                return "= fold-counted-v1"
            elif cmd_str == "list_commands":
                return "= boardsize\nclear_board\nkomi\nplay\ngenmove\nquit"
            return "= "

    def close(self):
        if self.proc:
            try:
                self.send("quit")
                self.proc.wait(timeout=2)
            except:
                self.proc.terminate()


def get_area_score(board):
    """Tromp-Taylor area score (integers only, no floats)."""
    sz = board.size
    visited = [False] * (sz * sz)
    black_score = 0
    white_score = 0
    for i in range(sz * sz):
        if board.board[i] == 1:
            black_score += 1
        elif board.board[i] == 2:
            white_score += 1
    for i in range(sz * sz):
        if board.board[i] == 0 and not visited[i]:
            region = {i}
            queue = collections.deque([i])
            visited[i] = True
            borders = set()
            while queue:
                curr = queue.popleft()
                for n in board.get_neighbors(curr):
                    if board.board[n] == 0:
                        if not visited[n]:
                            visited[n] = True
                            region.add(n)
                            queue.append(n)
                    else:
                        borders.add(board.board[n])
            if len(borders) == 1:
                border_color = list(borders)[0]
                if border_color == 1:
                    black_score += len(region)
                elif border_color == 2:
                    white_score += len(region)
    return black_score, white_score


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path):
    with open(path, "rb") as handle:
        return _sha256_bytes(handle.read())


def _git_commit(root):
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _command_file_bindings(opponent_cmd):
    """Hash every existing file supplied to the opponent command."""
    bindings = []
    for index, argument in enumerate((opponent_cmd or [])[1:], 1):
        candidate = argument.split("=", 1)[1] if \
            argument.startswith("-") and "=" in argument else argument
        path = Path(candidate).expanduser()
        if not path.is_file():
            continue
        resolved = path.resolve()
        bindings.append({
            "argument_index": index,
            "argument": argument,
            "resolved_path": str(resolved),
            "bytes": resolved.stat().st_size,
            "sha256": _sha256_file(resolved),
        })
    return bindings


def _opponent_identity(opponent_cmd):
    if not opponent_cmd:
        identity = {"kind": "deterministic-fallback", "command": None,
                    "executable": None, "executable_sha256": None}
    else:
        executable = shutil.which(opponent_cmd[0])
        if executable is None:
            raise FileNotFoundError(f"opponent executable not found: {opponent_cmd[0]}")
        identity = {
            "kind": "external-gtp",
            "command": list(opponent_cmd),
            "executable": str(Path(executable).resolve()),
            "executable_sha256": _sha256_file(executable),
            "invocation_cwd": str(Path.cwd().resolve()),
            "command_file_bindings": _command_file_bindings(opponent_cmd),
        }
    if not opponent_cmd:
        identity["invocation_cwd"] = str(Path.cwd().resolve())
        identity["command_file_bindings"] = []
    # Bind what the executable itself reports, not only its path and bytes.
    # This is a preflight identity receipt; it does not authorize a match.
    client = GTPClient(opponent_cmd)
    try:
        identity["gtp_identity"] = {
            command: client.send(command)
            for command in ("protocol_version", "name", "version", "list_commands")
        }
    finally:
        client.close()
    return identity


def _json_bytes(record):
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()


def run_tournament(opponent_cmd=None, size=9, rounds=4, depth=8,
                   output_dir=None, komi=7, development=False):
    """Run a registered match and seal immutable, hash-bound per-game receipts."""
    if output_dir is None:
        raise ValueError("an explicit output_dir is required for a registered match")
    output_dir = Path(output_dir).resolve()
    if output_dir.exists():
        raise FileExistsError(f"match receipt directory already exists: {output_dir}")
    if size < 1 or rounds < 1 or depth < 0 or not isinstance(komi, int):
        raise ValueError("size/rounds must be positive, depth non-negative, and komi integer")

    root = Path(__file__).resolve().parents[1]
    source_path = Path(__file__).resolve()
    registration = {
        "schema": ("fold-go-development-configuration/v1" if development
                   else "fold-go-match-registration/v3"),
        "status": "development-configured" if development else "registered",
        "registered_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_commit": _git_commit(root),
        "source_file": str(source_path.relative_to(root)),
        "source_sha256": _sha256_file(source_path),
        "opponent": _opponent_identity(opponent_cmd),
        "board_size": size,
        "rounds": rounds,
        "search_ceiling": depth,
        "node_budget_per_root_candidate": NODE_BUDGET,
        "rules": "Tromp-Taylor area scoring with positional superko",
        "komi": komi,
        "colour_schedule": "SFT black on odd games, white on even games",
        "governance_authority": False if development else None,
        "hardware": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "logical_cpu_count": os.cpu_count(),
        },
    }
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="fold-go-match-", dir=output_dir.parent))
    registration_bytes = _json_bytes(registration)
    configuration_name = (
        "development_configuration.json" if development else "registration.json")
    (stage / configuration_name).write_bytes(registration_bytes)
    binding_field = (
        "development_configuration_sha256" if development
        else "registration_sha256")

    print("=== SFT Go Tournament Referee ===")
    results = {"SFT": 0, "Opponent": 0, "Draw": 0}

    print(f"Starting {rounds}-round match on {size}x{size} board (search ceiling {depth})...")
    if opponent_cmd:
        print(f"Opponent command: {' '.join(opponent_cmd)}")
    else:
        print("No external engine specified; running against deterministic fallback.")

    game_hashes = []
    client = None
    try:
      for r in range(rounds):
        sft_color = 1 if r % 2 == 0 else 2
        board = SFTGoBoard(size, komi=komi)
        client = GTPClient(opponent_cmd)
        transcript = []
        moves = []

        def send(command):
            response = client.send(command)
            transcript.append({"command": command, "response": response})
            return response

        send(f"boardsize {size}")
        send("clear_board")
        send(f"komi {board.komi}")

        passes = 0
        moves_played = 0
        resigned_by = None
        # Games end on two consecutive passes (the rules). Safety bound is counted
        # from the board itself: 2 * N^2 moves, never a truncation of normal play.
        max_moves = 2 * size * size
        while passes < 2 and moves_played < max_moves:
            current_player = 1 if moves_played % 2 == 0 else 2

            if current_player == sft_color:
                decision = {}
                move = select_sft_move(
                    board, sft_color, ceiling=depth,
                    root_last_passed=passes > 0,
                    decision_trace=decision)
                if not board.play_move(move, sft_color):
                    raise RuntimeError("SFT selector returned an illegal move; round void")
                move_str = index_to_gtp(move, size)
                send(f"play {'B' if sft_color == 1 else 'W'} {move_str}")
                moves.append({"ply": moves_played + 1, "actor": "SFT",
                              "colour": "B" if sft_color == 1 else "W",
                              "move": move_str,
                              "search_decision": decision})
                if move is None:
                    passes += 1
                else:
                    passes = 0
            else:
                opp_color = 3 - sft_color
                resp = send(f"genmove {'B' if opp_color == 1 else 'W'}")
                parts = resp.split()
                move_str = "pass"
                if len(parts) > 1:
                    move_str = parts[1]
                move = gtp_to_index(move_str, size)
                moves.append({"ply": moves_played + 1, "actor": "Opponent",
                              "colour": "B" if opp_color == 1 else "W",
                              "move": move_str})
                if move == RESIGN:
                    resigned_by = opp_color
                    break
                if not board.play_move(move, opp_color):
                    # Honest abort: a desynced referee must halt, never score fiction.
                    print(f"REFEREE HALT: opponent move {move_str} rejected by the "
                          f"internal rules — board desync, round void.")
                    raise SystemExit(1)
                if move is None:
                    passes += 1
                else:
                    passes = 0

            moves_played += 1

        client.close()

        if passes < 2 and resigned_by is None:
            raise RuntimeError(f"round {r + 1} reached the move cap without pass-pass; round void")

        # Literal agreed area scoring and recorded integer komi.
        black_score, white_score = get_area_score(board)
        white_score += board.komi

        if resigned_by is not None:
            winner = "White" if resigned_by == 1 else "Black"
        elif black_score == white_score:
            winner = "Draw"
        else:
            winner = "Black" if black_score > white_score else "White"
        sft_won = (winner == "Black" and sft_color == 1) or \
                  (winner == "White" and sft_color == 2)

        if winner == "Draw":
            results["Draw"] += 1
        elif sft_won:
            results["SFT"] += 1
        else:
            results["Opponent"] += 1

        result_str = "Draw" if winner == "Draw" else (
            "SFT" if sft_won else "Opponent")
        game_record = {
            "schema": ("fold-go-development-game/v2" if development
                       else "fold-go-game-receipt/v2"),
            "status": "completed",
            "game": r + 1,
            "sft_side": "Black" if sft_color == 1 else "White",
            "winner": result_str,
            "winner_colour": winner,
            "score": {"black": black_score, "white_including_komi": white_score},
            "resigned_by": ("Black" if resigned_by == 1 else
                             "White" if resigned_by == 2 else None),
            "moves": moves,
            "final_position": board.position_key(),
            "complete_history_sha256": _sha256_bytes(
                "\n".join(sorted(board.history)).encode()),
            "gtp_transcript": transcript,
        }
        game_record[binding_field] = _sha256_bytes(registration_bytes)
        game_bytes = _json_bytes(game_record)
        game_name = f"game-{r + 1:03d}.json"
        (stage / game_name).write_bytes(game_bytes)
        game_hashes.append({"file": game_name, "sha256": _sha256_bytes(game_bytes)})
        print(f"Round {r + 1}: SFT={'Black' if sft_color == 1 else 'White'} | "
              f"Score B={black_score} W={white_score} | Winner: {result_str}")

      print(f"\nTournament complete!")
      print(f"Final Score: SFT {results['SFT']} - {results['Opponent']} Opponent"
            f" - {results['Draw']} Draw")

      match_record = {
          "schema": ("fold-go-development-measurement/v1" if development
                     else "fold-go-match-receipt/v1"),
          "status": "completed",
          "completed_at_utc": datetime.now(timezone.utc).isoformat(),
          "games": game_hashes,
          "result": {"SFT": results["SFT"], "Opponent": results["Opponent"],
                     "Draw": results["Draw"]},
      }
      match_record[binding_field] = _sha256_bytes(registration_bytes)
      (stage / "match.json").write_bytes(_json_bytes(match_record))
      os.replace(stage, output_dir)
      print(f"Immutable match receipts sealed at {output_dir}.")
      return match_record
    except BaseException as error:
      if client is not None:
          try:
              client.close()
          except Exception:
              pass
      void_record = {
          "schema": ("fold-go-development-measurement/v1" if development
                     else "fold-go-match-receipt/v1"),
          "status": "void",
          "failed_at_utc": datetime.now(timezone.utc).isoformat(),
          "completed_games": game_hashes,
          "error_type": type(error).__name__,
          "error": str(error),
      }
      void_record[binding_field] = _sha256_bytes(registration_bytes)
      (stage / "match.json").write_bytes(_json_bytes(void_record))
      os.replace(stage, output_dir)
      raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", action="store_true")
    parser.add_argument("--check-gtp", action="store_true")
    parser.add_argument("--size", type=int, default=9)
    parser.add_argument("--depth", type=int, default=8)
    parser.add_argument("--rounds", type=int, default=4)
    parser.add_argument("--komi", type=int, default=7)
    parser.add_argument("--development", action="store_true")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--engine", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.server:
        run_gtp_server()
    elif args.check_gtp:
        board = SFTGoBoard(args.size)
        move = select_sft_move(board, 1, ceiling=args.depth)
        print(f"GTP check passed. SFT plays first move: {index_to_gtp(move, args.size)}")
    else:
        if args.output_dir is None:
            parser.error("--output-dir is required for a tournament")
        run_tournament(args.engine, size=args.size, rounds=args.rounds,
                       depth=args.depth, output_dir=args.output_dir, komi=args.komi,
                       development=args.development)


if __name__ == "__main__":
    main()

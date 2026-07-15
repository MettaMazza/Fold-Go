"""R1's INDEPENDENT REFEREE: a second exact solver for Tromp-Taylor
no-suicide Go (positional superko as a path set, area scoring, pass-pass
terminal), independently written in a different language with different
constructions (tuples and sets, not signature strings). It must reproduce:
the oracle roots, the engine's referee-only roots (1x3, 2x3), and the
engine's FULL 2x2-space certification checksums (57 states x both movers).
Zero disagreements or R1 does not stand."""
import itertools, subprocess, re, sys
sys.setrecursionlimit(100000)

def neighbours(p, w, h):
    r, c = divmod(p, w)
    for r2, c2 in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
        if 0 <= r2 < h and 0 <= c2 < w:
            yield r2 * w + c2

def group_liberty(board, w, h, start):
    colour, group, front = board[start], {start}, [start]
    while front:
        q = front.pop()
        for q2 in neighbours(q, w, h):
            if board[q2] == 0:
                return True, group
            if board[q2] == colour and q2 not in group:
                group.add(q2); front.append(q2)
    return False, group

def play(board, w, h, p, colour):
    if board[p] != 0:
        return None
    nb = list(board); nb[p] = colour
    enemy = 3 - colour
    for q in neighbours(p, w, h):
        if nb[q] == enemy:
            alive, grp = group_liberty(nb, w, h, q)
            if not alive:
                for g in grp:
                    nb[g] = 0
    alive, _ = group_liberty(nb, w, h, p)
    return tuple(nb) if alive else None

def area(board, w, h):
    n, seen, diff = w * h, set(), 0
    for p in range(n):
        if board[p] == 1: diff += 1
        elif board[p] == 2: diff -= 1
        elif p not in seen:
            region, front, cols = {p}, [p], set()
            while front:
                q = front.pop()
                for q2 in neighbours(q, w, h):
                    if board[q2] == 0 and q2 not in region:
                        region.add(q2); front.append(q2)
                    elif board[q2]:
                        cols.add(board[q2])
            seen |= region
            if cols == {1}: diff += len(region)
            elif cols == {2}: diff -= len(region)
    return diff

def solve(board, w, h, to_move, passed, seen, alpha, beta):
    best = -1000 if to_move == 1 else 1000
    for p in range(w * h):
        nb = play(board, w, h, p, to_move)
        if nb is not None and nb not in seen:
            v = solve(nb, w, h, 3 - to_move, 0, seen | {nb}, alpha, beta)
            if to_move == 1:
                best = max(best, v); alpha = max(alpha, best)
            else:
                best = min(best, v); beta = min(beta, best)
            if alpha >= beta:
                return best
    pv = area(board, w, h) if passed else solve(board, w, h, 3 - to_move, 1, seen, alpha, beta)
    return max(best, pv) if to_move == 1 else min(best, pv)

def root(board, w, h, to_move=1):
    return solve(tuple(board), w, h, to_move, 0, {tuple(board)}, -1000, 1000)

def legal_positions(w, h):
    for cand in itertools.product((0, 1, 2), repeat=w * h):
        ok = True
        seen = set()
        for p in range(w * h):
            if cand[p] and p not in seen:
                alive, grp = group_liberty(cand, w, h, p)
                if not alive:
                    ok = False; break
                seen |= grp
        if ok:
            yield cand

if __name__ == "__main__":
    mine = {"1x1": root([0], 1, 1), "1x2": root([0, 0], 1, 2), "1x3": root([0, 0, 0], 1, 3),
            "2x2": root([0, 0, 0, 0], 2, 2), "2x3": root([0] * 6, 2, 3)}
    ORACLE = {"1x1": 0, "1x2": 0, "2x2": 1}
    for k, v in ORACLE.items():
        assert mine[k] == v, f"referee vs oracle at {k}: {mine[k]} vs {v}"
    states = list(legal_positions(2, 2))
    sum_b = sum(root(s, 2, 2, 1) for s in states)
    sum_w = sum(root(s, 2, 2, 2) for s in states)
    print(f"referee: roots {mine}; 2x2 space: {len(states)} states, sumB={sum_b}, sumW={sum_w}")
    out = subprocess.run(["./tests/fold_go_solve"], capture_output=True, text=True,
                         cwd="/Users/mettamazza/Desktop/Fold Go", timeout=7200).stdout
    print(out)
    eng = {m.group(1): int(m.group(2)) for m in re.finditer(r"(\dx\d) = (-?\d+)", out)}
    esb = int(re.search(r"sumB = (-?\d+)", out).group(1))
    esw = int(re.search(r"sumW = (-?\d+)", out).group(1))
    for k in ("1x1", "1x2", "1x3", "2x2", "2x3"):
        assert eng.get(k) == mine[k], f"ENGINE vs REFEREE at {k}: {eng.get(k)} vs {mine[k]}"
    assert (esb, esw) == (sum_b, sum_w), f"2x2 certification checksums differ: {(esb, esw)} vs {(sum_b, sum_w)}"
    print(f"R1 REFEREE: 5 roots + full 2x2 space (57x2 solves) engine==referee; "
          f"3 roots oracle-anchored -- zero disagreements")

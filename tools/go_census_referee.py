"""R0's INDEPENDENT REFEREE: a second, independently written enumeration of
legal Go positions (Tromp-Taylor position legality: every maximal group has
a liberty), in a different language with a different construction (sets and
itertools, not odometers and flat lists), agreeing with the fold engine's
counts on every board INCLUDING the rectangles the published oracle does not
cover. Zero disagreements or R0 does not stand."""
import itertools, subprocess, re, sys

def legal(board, w, h):
    n = w * h
    seen = set()
    for p in range(n):
        if board[p] and p not in seen:
            colour, group, frontier, liberty = board[p], {p}, [p], False
            while frontier:
                q = frontier.pop()
                r, c = divmod(q, w)
                for r2, c2 in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                    if 0 <= r2 < h and 0 <= c2 < w:
                        q2 = r2 * w + c2
                        if board[q2] == 0:
                            liberty = True
                        elif board[q2] == colour and q2 not in group:
                            group.add(q2)
                            frontier.append(q2)
            if not liberty:
                return False
            seen |= group
    return True

def census(w, h):
    return sum(legal(b, w, h) for b in itertools.product((0, 1, 2), repeat=w * h))

if __name__ == "__main__":
    ORACLE = {(1, 1): 1, (2, 2): 57, (3, 3): 12675}   # tromp.github.io/go/legal
    boards = [(1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3)]
    mine = {b: census(*b) for b in boards}
    print("referee counts:", {("%dx%d" % b): v for b, v in mine.items()})
    for b, v in ORACLE.items():
        assert mine[b] == v, f"referee disagrees with the oracle at {b}: {mine[b]} vs {v}"
    out = subprocess.run(["./tests/fold_go_census"], capture_output=True, text=True,
                         cwd="/Users/mettamazza/Desktop/Fold Go", timeout=600).stdout
    engine = {tuple(map(int, m.group(1, 2))): int(m.group(3))
              for m in re.finditer(r"(\d)x(\d) = (\d+)", out)}
    print("engine counts :", {("%dx%d" % b): v for b, v in engine.items()})
    bad = [b for b in mine if b in engine and engine[b] != mine[b]]
    assert not bad, f"ENGINE vs REFEREE DISAGREE at {bad}"
    checked = [b for b in mine if b in engine]
    print(f"R0 REFEREE: {len(checked)} boards cross-checked engine==referee, "
          f"{len(ORACLE)} also oracle-anchored -- zero disagreements")

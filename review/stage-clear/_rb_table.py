import csv
import collections
import pathlib

HERE = pathlib.Path(__file__).parent
edges = list(csv.DictReader(open(HERE / "citation-graph.tsv", encoding="utf-8"), delimiter="\t"))
deg = {r["file"]: r for r in csv.DictReader(open(HERE / "citation-indegree.tsv", encoding="utf-8"), delimiter="\t")}
citers = collections.defaultdict(list)
for e in edges:
    citers[e["cited"]].append((e["citer"], e["citer_status"]))
out = []
for f, r in sorted(deg.items()):
    if not (f.startswith("docs/") and f.count("/") == 1 and f.endswith(".md")):
        continue
    if r["status"] != "REFERENCE":
        continue
    live = sorted({(c, s) for c, s in citers.get(f, []) if s in ("CODE", "LIVING")})
    ledg = sorted({c for c, s in citers.get(f, []) if s == "LEDGER"})
    frozen = len({c for c, _ in citers.get(f, [])}) - len(live) - len(ledg)
    bucket = "A" if not live and not ledg else ("B" if not live else ("C" if any(s == "CODE" for _, s in live) else "D"))
    out.append((bucket, f, live, len(ledg), frozen))
lines = []
for b in "ABCD":
    rows = [x for x in out if x[0] == b]
    lines.append(f"### bucket {b} ({len(rows)})")
    for _, f, live, l, fr in rows:
        lv = "; ".join(f"`{c}`" for c, _ in live)
        lines.append(f"| `{f[5:]}` | {lv or '—'} | {l} | {fr} |")
(HERE / "_rb_table.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", len(out), "rows")

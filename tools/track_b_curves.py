"""Track B's demand (B1) and output (B2) curves, from both feeds.

    python tools/track_b_curves.py                     # print the document
    python tools/track_b_curves.py --out docs/track-b-curves.md
    python tools/track_b_curves.py --bot-dir X --human-dir Y

WHAT THIS IS. The charter's Track B (`docs/axis-validity-session-charter.md`
§4) wants two surfaces: **B1**, the empirical demand curve -- incoming damage
and required output per turn, per act, per fight class -- and **B2**, archetype
output curves laid over it. This tool builds both out of the per-fight
telemetry the Understudy apparatus writes, and it reads TWO feeds that share
one schema (`understudy/README.md`):

  * the **bot feed** -- `understudy/soak.py` driving the real game with
    policy_v1. Dense, cheap, and it dies in Act 1 (Understudy debt #3), so it
    fills Act 1 and nothing else.
  * the **human feed** -- `klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs`
    recording [USER]'s own sessions, co-op included. Sparse, arrives on the
    table's schedule, and it is the only thing that will ever fill Act 2 and
    Act 3.

THE THREE RULES THIS FILE IS WRITTEN TO ENFORCE, because a curve is exactly
the kind of artifact that gets quoted six weeks later with its caveats lost:

1. **Every row is labelled with its feed** (Guardrail 7). A bot-derived number
   is a bot-limited FLOOR: it is what a heuristic with declared reductions
   managed, not what the fight demands of a person. The two feeds are never
   averaged together, and the `feed` column is not optional.
2. **An empty cell stays empty and says why.** `--` means no fight of that
   shape has been recorded by that feed. It is never interpolated, never
   carried across from a neighbouring act, and never filled from the sim.
3. **B2 is a diagnostic surface, never an acceptance target** (R14). Nothing
   here is a floor, a band, or a pass mark, and no number here moves a balance
   value on its own.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

REPO = Path(__file__).resolve().parent.parent
BOT_DIR = REPO / "understudy" / "logs" / "soak"
SHEETS = ("furina-cards.yaml", "klee-cards.yaml", "kokomi-cards.yaml")

# The game's own profile root on Windows -- `user://` globalized. The C# writer
# creates `gits_telemetry/` under it (PlayTelemetry.LogPath), deliberately
# OUTSIDE `mods/klee/`, which `deploy.ps1` deletes and re-copies on every
# deploy. Overridable, because a path is a fact about one machine.
HUMAN_DIR_ENV = "GITS_HUMAN_FEED_DIR"


def default_human_dir() -> Path:
    override = os.environ.get(HUMAN_DIR_ENV)
    if override:
        return Path(override)
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / "SlayTheSpire2" / "gits_telemetry"
    return REPO / "understudy" / "logs" / "human"


ACTS = (1, 2, 3)
CLASSES = ("monster", "elite", "boss")
ARCHETYPES = ("salon", "fanfare", "spotlight", "generic")
EMPTY = "--"


# ------------------------------------------------------------------ input ---

@dataclass
class Fight:
    """One fight, one seat. The schema is `understudy/README.md`."""
    feed: str
    source: str
    intent: str
    seats: int
    act: int
    floor: int
    kind: str
    turns: int
    outcome: str
    hp_lost: int
    enemies: list = field(default_factory=list)
    incoming_by_turn: list = field(default_factory=list)
    enemy_pool_by_turn: list = field(default_factory=list)
    meters_by_turn: list = field(default_factory=list)
    block_at_turn_end: list = field(default_factory=list)
    cards_played: list = field(default_factory=list)
    damage_by_source: dict = field(default_factory=dict)

    @property
    def enemy_hp_total(self) -> int:
        return sum(int(e.get("max_hp") or 0) for e in self.enemies
                   if isinstance(e, dict))


def _fight(rec: dict[str, Any]) -> Fight:
    # A RECORD WITHOUT A FEED KEY IS A BOT RECORD, and saying so here rather
    # than at the call site keeps the pre-schema-1 soak logs (which predate the
    # label by a day) readable instead of silently unlabelled.
    return Fight(
        feed=str(rec.get("feed") or "bot"),
        source=str(rec.get("source") or "soak"),
        # A DECLARATION, NEVER AN INFERENCE (R99/4a). Absent key and empty
        # string are the same reading: nobody said what this deck was trying
        # to be. Nothing here looks at `cards_played` and guesses.
        intent=str(rec.get("intent") or "").strip().lower(),
        seats=int(rec.get("seats") or 1),
        act=int(rec.get("act") or 0),
        floor=int(rec.get("floor") or 0),
        kind=str(rec.get("kind") or "unknown"),
        turns=int(rec.get("turns") or 0),
        outcome=str(rec.get("outcome") or "unknown"),
        hp_lost=int(rec.get("hp_lost") or 0),
        enemies=list(rec.get("enemies") or []),
        incoming_by_turn=list(rec.get("incoming_by_turn") or []),
        enemy_pool_by_turn=list(rec.get("enemy_pool_by_turn") or []),
        meters_by_turn=list(rec.get("meters_by_turn") or []),
        block_at_turn_end=list(rec.get("block_at_turn_end") or []),
        cards_played=list(rec.get("cards_played") or []),
        damage_by_source=dict(rec.get("damage_by_source") or {}),
    )


def read_jsonl(path: Path) -> list[dict]:
    out: list[dict] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return out
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue                      # a torn last line is a killed game
    return out


def cut_by_intent(fights: Sequence[Fight], intent: str | None) -> list[Fight]:
    """R99/4a — the declared-intent cut.

    B2's Fanfare question could not be graded from mixed decks. The cut is the
    cheap half of the answer: keep only the fights whose run DECLARED the
    archetype, and B2 becomes a curve for decks that were trying to be that
    thing. Both feeds carry the key, so one flag cuts a human session and a
    committed soak arm the same way.

    `None` keeps everything, which is what every reader before this flag got.
    """
    if not intent:
        return list(fights)
    want = intent.strip().lower()
    return [f for f in fights if f.intent == want]


def load(dirs: Iterable[Path]) -> list[Fight]:
    fights: list[Fight] = []
    for d in dirs:
        if not d or not d.exists():
            continue
        for path in sorted(d.glob("*.jsonl")):
            for rec in read_jsonl(path):
                if rec.get("record") == "fight":
                    fights.append(_fight(rec))
    return fights


# ------------------------------------------------------------ archetypes ---

def card_archetypes() -> dict[str, tuple[str, ...]]:
    """Display NAME -> archetypes, off the three design sheets.

    Telemetry carries names because a name is what a human reading a log can
    check; the sheets are the only place that maps one to an archetype. An
    upgraded card logs as `Name+`, and both spellings resolve to the same row.
    """
    import yaml                                  # in the suite's dependencies

    out: dict[str, tuple[str, ...]] = {}
    for sheet in SHEETS:
        path = REPO / "docs" / sheet
        if not path.exists():
            continue
        for row in yaml.safe_load(path.read_text(encoding="utf-8")) or []:
            name = str(row.get("name") or "").strip()
            if not name:
                continue
            arch = tuple(row.get("archetypes") or ("generic",))
            out[name] = arch
            out[name + "+"] = arch
    return out


def archetype_of(name: str, table: dict[str, tuple[str, ...]]) -> str:
    """One archetype per card for the split, and the tie-break is DECLARED.

    A card may carry several. The split has to put its damage somewhere, so it
    goes to the first of `ARCHETYPES` the card names -- salon before fanfare
    before spotlight -- and a card matching none is `generic`, which includes
    every base-game and colorless card that has no sheet row at all.
    """
    arch = table.get(name.strip())
    if not arch:
        return "generic"
    for candidate in ARCHETYPES:
        if candidate in arch:
            return candidate
    return "generic"


# -------------------------------------------------------------- maths ------

def med(xs: Sequence[float]) -> float | None:
    xs = [float(x) for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def fmt(x: float | None, places: int = 0) -> str:
    return EMPTY if x is None else f"{x:.{places}f}"


def _by_turn(rows: Sequence[Sequence[Any]], index: int) -> dict[int, float]:
    out: dict[int, float] = {}
    for row in rows:
        if not isinstance(row, (list, tuple)) or len(row) <= index:
            continue
        try:
            out[int(row[0])] = float(row[index])
        except (TypeError, ValueError):
            continue
    return out


def pool_drops(f: Fight) -> dict[int, float]:
    """Damage the enemy side actually LOST, per turn, from pool samples.

    This is the output measure that does not depend on attribution: the pool is
    read at each turn opening, so the drop between two openings is everything
    that landed in between, whoever landed it. `damage_by_source` cannot say
    that -- it credits the play the reader happened to observe next -- so the
    two are reported separately and never added together.
    """
    pool = _by_turn(f.enemy_pool_by_turn, 1)
    rounds = sorted(pool)
    out: dict[int, float] = {}
    for i, rnd in enumerate(rounds[:-1]):
        out[rnd] = max(0.0, pool[rnd] - pool[rounds[i + 1]])
    return out


# ------------------------------------------------------------------- B1 ----

def demand_rows(fights: Sequence[Fight]) -> list[dict]:
    """Per (feed, act, class, turn): what the fight asks of the player."""
    buckets: dict[tuple[str, int, str, int], dict[str, list[float]]] = {}
    for f in fights:
        incoming = _by_turn(f.incoming_by_turn, 1)
        attackers = _by_turn(f.incoming_by_turn, 2)
        for rnd, dmg in incoming.items():
            key = (f.feed, f.act, f.kind, rnd)
            b = buckets.setdefault(key, {"incoming": [], "attackers": [],
                                         "required": []})
            b["incoming"].append(dmg)
            b["attackers"].append(attackers.get(rnd, 0.0))
            # REQUIRED OUTPUT is the pace this fight was actually cleared at:
            # the enemy HP pool over the turns it took. It is a description of
            # the observed clear, not a target -- a slower clear is a smaller
            # number here and a bigger HP bill in B1's own damage column.
            if f.turns > 0 and f.enemy_hp_total:
                b["required"].append(f.enemy_hp_total / f.turns)

    rows = []
    for (feed, act, kind, rnd), b in sorted(buckets.items()):
        rows.append({
            "feed": feed, "act": act, "kind": kind, "turn": rnd,
            "n": len(b["incoming"]),
            "incoming": med(b["incoming"]),
            "attackers": med(b["attackers"]),
            "required_output": med(b["required"]),
        })
    return rows


# ------------------------------------------------------------------- B2 ----

def output_rows(fights: Sequence[Fight],
                table: dict[str, tuple[str, ...]]) -> list[dict]:
    """Per (feed, act, turn): what the player's side produced."""
    buckets: dict[tuple[str, int, int], dict[str, Any]] = {}
    for f in fights:
        drops = pool_drops(f)
        block = _by_turn(f.block_at_turn_end, 1)
        plays: dict[int, dict[str, int]] = {}
        for row in f.cards_played:
            if not isinstance(row, (list, tuple)) or len(row) < 2:
                continue
            try:
                rnd = int(row[0])
            except (TypeError, ValueError):
                continue
            plays.setdefault(rnd, {}).setdefault(
                archetype_of(str(row[1]), table), 0)
            plays[rnd][archetype_of(str(row[1]), table)] += 1

        turns = set(drops) | set(block) | set(plays)
        for rnd in turns:
            key = (f.feed, f.act, rnd)
            b = buckets.setdefault(key, {"damage": [], "block": [],
                                         "plays": {a: 0 for a in ARCHETYPES},
                                         "fights": 0})
            b["fights"] += 1
            if rnd in drops:
                b["damage"].append(drops[rnd])
            if rnd in block:
                b["block"].append(block[rnd])
            for arch, n in plays.get(rnd, {}).items():
                b["plays"][arch] = b["plays"].get(arch, 0) + n

    rows = []
    for (feed, act, rnd), b in sorted(buckets.items()):
        rows.append({
            "feed": feed, "act": act, "turn": rnd, "fights": b["fights"],
            "damage": med(b["damage"]), "block": med(b["block"]),
            "plays": b["plays"],
        })
    return rows


def archetype_damage(fights: Sequence[Fight],
                     table: dict[str, tuple[str, ...]]) -> list[dict]:
    """Attributed damage per archetype per turn -- the Fanfare-shape lens.

    ATTRIBUTION-LIMITED, and the limit is one-directional: `damage_by_source`
    is credited per CARD but not per TURN in either writer, so a per-turn split
    has to distribute a card's total across the turns it was played in. That is
    an approximation, it is stated here rather than in a footnote, and it is
    why the pre-registration is graded against per-turn PLAYS and the pool
    curve as well as against this table.
    """
    buckets: dict[tuple[str, int, int, str], list[float]] = {}
    for f in fights:
        by_turn: dict[str, list[int]] = {}
        for row in f.cards_played:
            if isinstance(row, (list, tuple)) and len(row) >= 2:
                try:
                    by_turn.setdefault(str(row[1]), []).append(int(row[0]))
                except (TypeError, ValueError):
                    continue
        for name, total in f.damage_by_source.items():
            rounds = by_turn.get(name) or []
            if not rounds:
                continue
            share = float(total) / len(rounds)
            arch = archetype_of(name, table)
            for rnd in rounds:
                buckets.setdefault((f.feed, f.act, rnd, arch), []).append(share)

    return [{"feed": feed, "act": act, "turn": rnd, "archetype": arch,
             "damage": sum(v), "n": len(v)}
            for (feed, act, rnd, arch), v in sorted(buckets.items())]


# ------------------------------------------------------- the salon meter ---

def salon_fill(fights: Sequence[Fight]) -> dict[str, dict[str, Any]]:
    """R91/2b's pre-registration: when does the Salon fill, and how long is it
    full? Per feed, over fights that recorded a meter sample at all."""
    out: dict[str, dict[str, Any]] = {}
    for f in fights:
        rows = [r for r in f.meters_by_turn
                if isinstance(r, (list, tuple)) and len(r) >= 4]
        if not rows:
            continue
        bucket = out.setdefault(f.feed, {"fights": 0, "first_full": [],
                                         "never_full": 0, "turns": 0,
                                         "turns_full": 0, "peak": []})
        bucket["fights"] += 1
        first = None
        peak = 0
        for row in rows:
            rnd, salon, cap = int(row[0]), int(row[2]), int(row[3])
            bucket["turns"] += 1
            peak = max(peak, salon)
            if cap and salon >= cap:
                bucket["turns_full"] += 1
                if first is None:
                    first = rnd
        bucket["peak"].append(peak)
        if first is None:
            bucket["never_full"] += 1
        else:
            bucket["first_full"].append(first)
    return out


# ---------------------------------------------------------------- render ---

BANNER = (
    "> **Every curve below is labelled with its FEED, and the label is the "
    "point (Guardrail 7).** A bot-feed number is a *bot-limited floor*: what "
    "policy_v1 -- a heuristic with declared reductions, on read-back seeds "
    "(R95) -- managed, not what the fight demands of a person. A human-feed "
    "number is one table's play, not a distribution. The two are never "
    "averaged. `--` means **no fight of that shape has been recorded by that "
    "feed**; empty cells are never interpolated, never carried across from a "
    "neighbouring act, and never filled from the sim. B2 is a diagnostic "
    "surface and never an acceptance target (R14)."
)


def render(fights: Sequence[Fight], intent: str | None = None) -> str:
    table = card_archetypes()
    L: list[str] = []
    a = L.append

    feeds = sorted({f.feed for f in fights}) or ["bot"]
    a("# Track B — demand (B1) and output (B2) curves")
    a("")
    a("Generated by `tools/track_b_curves.py`. Feeds: the bot feed "
      "(`understudy/soak.py`, policy_v1) and the human feed "
      "(`klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs`, normal play "
      "including co-op). Both write the schema in `understudy/README.md`.")
    a("")
    a(BANNER)
    a("")
    if intent:
        a(f"> **CUT BY DECLARED INTENT: `{intent}`.** Every table below is "
          f"restricted to fights whose run declared this archetype — a human "
          f"session that wrote it in `intent.txt`, or a bot soak run under "
          f"`--commit {intent}`. This is a **declaration**, not a "
          f"classification of the deck: nothing infers an archetype from what "
          f"was played. Numbers under a cut are not comparable to numbers "
          f"without one.")
        a("")

    # ------------------------------------------------------------ coverage
    a("## 0. Coverage — which cells have data at all")
    a("")
    a("| feed | act | monster | elite | boss | seats |")
    a("|---|---|---|---|---|---|")
    for feed in feeds:
        for act in ACTS:
            cells = []
            for kind in CLASSES:
                n = sum(1 for f in fights
                        if f.feed == feed and f.act == act and f.kind == kind)
                cells.append(str(n) if n else EMPTY)
            seats = sorted({f.seats for f in fights
                            if f.feed == feed and f.act == act})
            a(f"| {feed} | {act} | " + " | ".join(cells) + " | "
              + (", ".join(str(s) for s in seats) if seats else EMPTY) + " |")
    a("")
    missing = [(feed, act) for feed in feeds for act in ACTS
               if not any(f.feed == feed and f.act == act for f in fights)]
    if missing:
        a("**Empty by act:** "
          + "; ".join(f"`{feed}` has nothing in act {act}" for feed, act in missing)
          + ". These stay empty until that feed plays there. The bot feed is "
            "not expected to fill acts 2–3 (Understudy debt #3: policy_v1 dies "
            "in act 1); the human feed is the only instrument that will.")
        a("")

    # ---------------------------------------------- declared intent (R99/4a)
    declared: dict[tuple[str, str], int] = {}
    for f in fights:
        declared[(f.feed, f.intent or "(none)")] = \
            declared.get((f.feed, f.intent or "(none)"), 0) + 1
    if declared:
        a("**Declared deck intent** — one line per session on the human feed "
          "(`intent.txt`), the `--commit` arm on the bot feed. `(none)` is a "
          "run nobody declared anything for, which is most of the record and "
          "is not a defect. Cut a curve to one of these with "
          "`--intent <archetype>`.")
        a("")
        a("| feed | declared intent | fights |")
        a("|---|---|---|")
        for (feed, word), n in sorted(declared.items()):
            a(f"| {feed} | {word} | {n} |")
        a("")

    # ------------------------------------------------------------------ B1
    a("## 1. B1 — the demand curve")
    a("")
    a("`incoming` is the sum of TELEGRAPHED attack intents at the turn "
      "opening, before block — this-turn-accurate and future-turn-blind, the "
      "same limit the wire adapter declares. `required output` is the enemy HP "
      "pool over the turns the fight actually took: a description of the "
      "observed clear, not a target.")
    a("")
    rows = demand_rows(fights)
    for feed in feeds:
        for act in ACTS:
            block = [r for r in rows if r["feed"] == feed and r["act"] == act]
            if not block:
                continue
            a(f"### feed `{feed}` — act {act}")
            a("")
            a("| class | turn | fights | median incoming | attackers | "
              "median required output/turn |")
            a("|---|---|---|---|---|---|")
            for r in sorted(block, key=lambda r: (r["kind"], r["turn"])):
                a(f"| {r['kind']} | {r['turn']} | {r['n']} | "
                  f"{fmt(r['incoming'])} | {fmt(r['attackers'], 1)} | "
                  f"{fmt(r['required_output'], 1)} |")
            a("")

    # ------------------------------------------------------------------ B2
    a("## 2. B2 — output curves, over the same turns")
    a("")
    a("`damage` is the enemy pool's own drop between two turn openings — "
      "complete, and independent of card attribution. `block` is what stood at "
      "the END of the player's turn, which is the quantity a demand curve is "
      "read against; block sampled at the turn OPENING is whatever survived the "
      "enemy and is a different number wearing the same word. Plays are "
      "counted by archetype off the design sheets.")
    a("")
    orows = output_rows(fights, table)
    for feed in feeds:
        for act in ACTS:
            block = [r for r in orows if r["feed"] == feed and r["act"] == act]
            if not block:
                continue
            a(f"### feed `{feed}` — act {act}")
            a("")
            a("| turn | fights | median damage/turn | median block at turn end | "
              + " | ".join(f"{x} plays" for x in ARCHETYPES) + " |")
            a("|---|---|---|---|" + "---|" * len(ARCHETYPES))
            for r in sorted(block, key=lambda r: r["turn"]):
                plays = " | ".join(str(r["plays"].get(x, 0)) for x in ARCHETYPES)
                a(f"| {r['turn']} | {r['fights']} | {fmt(r['damage'], 1)} | "
                  f"{fmt(r['block'], 1)} | {plays} |")
            a("")

    # ------------------------------------------- the archetype damage split
    a("### 2b. Attributed damage by archetype and turn")
    a("")
    a("Attribution-limited in one direction: a card's total is spread evenly "
      "across the turns it was played in, because neither writer credits "
      "damage per turn. Under-counts, never invents.")
    a("")
    arows = archetype_damage(fights, table)
    for feed in feeds:
        block = [r for r in arows if r["feed"] == feed]
        if not block:
            continue
        turns = sorted({r["turn"] for r in block})[:8]
        a(f"feed `{feed}`:")
        a("")
        a("| act | archetype | " + " | ".join(f"t{t}" for t in turns) + " |")
        a("|---|---|" + "---|" * len(turns))
        for act in ACTS:
            for arch in ARCHETYPES:
                cells = []
                for t in turns:
                    hit = [r for r in block if r["act"] == act
                           and r["turn"] == t and r["archetype"] == arch]
                    cells.append(fmt(hit[0]["damage"], 0) if hit else EMPTY)
                if all(c == EMPTY for c in cells):
                    continue
                a(f"| {act} | {arch} | " + " | ".join(cells) + " |")
        a("")

    # ----------------------------------------------------------- the salon
    a("## 3. Salon fill time (R91/2b pre-registration)")
    a("")
    fill = salon_fill(fights)
    if not fill:
        a("No fight recorded a Salon meter sample. The counter landed with "
          "the Track B telemetry additions; soaks and sessions from before it "
          "carry no `meters_by_turn`, and no number is inferred for them.")
        a("")
    else:
        a("| feed | fights w/ meter | median turn first at cap | never filled | "
          "fight-turns at cap | median peak members |")
        a("|---|---|---|---|---|---|")
        for feed, b in sorted(fill.items()):
            frac = (100.0 * b["turns_full"] / b["turns"]) if b["turns"] else None
            a(f"| {feed} | {b['fights']} | {fmt(med(b['first_full']), 1)} | "
              f"{b['never_full']} | {fmt(frac, 1)}% | "
              f"{fmt(med(b['peak']), 1)} |")
        a("")
        a("Reported, not acted on: R95's amendment routes this number to the "
          "bounded-meter `scaling`-tag question, and that revisit is a design "
          "decision this tool does not make.")
        a("")

    a("---")
    a("")
    a(f"{len(fights)} fight records read "
      + ", ".join(f"`{feed}`: {sum(1 for f in fights if f.feed == feed)}"
                  for feed in feeds)
      + ". Instruments: `understudy/soak.py` (bot), "
        "`klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs` (human). "
        "Schema: `understudy/README.md`.")
    return "\n".join(L)


# ------------------------------------------------------------------ main ---

def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--bot-dir", type=Path, default=BOT_DIR)
    ap.add_argument("--human-dir", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--intent", default=None,
                    help="R99/4a: cut every curve to fights whose run "
                         "DECLARED this archetype (human feed: intent.txt; "
                         "bot feed: soak --commit). Omit for everything.")
    args = ap.parse_args(argv)

    human = args.human_dir or default_human_dir()
    fights = cut_by_intent(load([args.bot_dir, human]), args.intent)
    doc = render(fights, intent=args.intent)
    if args.out:
        args.out.write_text(doc + "\n", encoding="utf-8")
        print(f"wrote {args.out} ({len(fights)} fight records)")
    else:
        print(doc)
    return 0


if __name__ == "__main__":
    sys.exit(main())

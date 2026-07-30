#!/usr/bin/env python3
"""Quantify card-pool DISTINCTNESS -- the "interestingness" instrument.

WHY THIS EXISTS
---------------
The felt gap (user, 2026-07-26): our pools read as "fewer unique effects,
lots of cards that are basically the same thing with minor variations --
thing plus a Strike, thing plus some Block." Taste catches this late and
expensively, one red-pen round per character. This tool turns the feeling
into numbers so it can become a GATE instead of a revision loop.

WHAT IT MEASURES (per pool)
---------------------------
Each card is canonicalized to a SIGNATURE: the multiset of its effect ops
with structural qualifiers (scaling? conditional? target class? multi-hit?)
and card-level flags (X-cost, exhaust) -- MAGNITUDES ARE STRIPPED. Two
cards that differ only in numbers have the same signature on purpose:
"6 damage + 4 block" and "9 damage + 6 block" are the same card idea.

  cards        pool size (draftable rows in the sheet)
  vocab        distinct EFFECTIVE ideas -- op names, but apply_power split
               by WHICH power (see the representation note below)
  hapax        ideas used by exactly ONE card: unique mechanical ideas
  top%         share of cards touched by the pool's single most-used idea
               -- concentration. A themed character concentrates on purpose;
               this says how hard.
  uniq%        cards whose full signature appears exactly once
  maxclu       largest same-signature family (the worst clone cluster)
  rider%       cards that are CORE+RIDER composites: at least one plain
               rider token (unscaled damage@one / block@self / draw /
               energy / small resource gain) attached to a non-rider core
  neardup      pairs of cards whose signatures become IDENTICAL when
               rider tokens are deleted -- the literal "same thing with
               minor variations" count
  decide%      cards whose text contains a decision or a changing number:
               conditional, select/choice, formula scaling, X-cost,
               aura interaction

None of these alone is "interestingness"; together they corner it. A pool
can be distinct-but-boring or samey-but-deep, and the table shows which.

THE REPRESENTATION ARTIFACT (corrected 2026-07-26)
--------------------------------------------------
`vocab` counted raw op NAMES, and that systematically flattered our pools
while understating any base-game anchor. Our DSL spells distinct ideas as
distinct ops (`place_bomb`, `detonate`, `gain_spark`); the base game spells
them as PARAMETERS of one op -- `apply_power` fires on 39 of 76 official
Ironclad cards and hides 28 different powers. Raw op names read Klee 23 vs
official 13, i.e. exactly backwards. Splitting apply_power by power gives
effective vocab official 40 / klee 34 / furina 26 / kokomi 21, which is the
honest ordering. Target class (`@one`, `@all`) is stripped: it is a
structural qualifier already carried in the signature, not a separate idea.

THE ANCHOR (IP rule respected)
------------------------------
Official StS2 pools are the calibration standard, extracted LOCALLY via
tools/extract_base_game_pool.py into game_ref/ (gitignored; decompiled
data never enters the repo -- csharp-build-spec.md §0.3). The ASSEMBLED
pool `<char>_pool.yaml` is preferred over the `<char>-cards.yaml`
extraction snapshot -- see _game_ref_pools() for why that distinction has
already cost one wrong report. In CI or a fresh clone the report covers mod
pools only. GATE NUMBERS ARE NOT HARDCODED BY GUESS: they are set relative
to the official rows.

  python tools/card_distinctness_report.py                # full report
  python tools/card_distinctness_report.py --pool furina  # one pool
  python tools/card_distinctness_report.py --families     # list clusters
  python tools/card_distinctness_report.py --by-rarity    # rarity-scoped rows
  python tools/card_distinctness_report.py --gate         # exit 1 on breach

GATE (RATIFIED [USER] 2026-07-27, TWO-ANCHOR: derivation and evidence in
docs/a2-gate-ratification-2026-07-27.md; supersedes the PROPOSED 2026-07-26
single-anchor draft of uniq>=75/maxclu<=4/neardup<=0.33). Hard floors sit
at the official FLOOR (Silent, the themed anchor) with modding headroom:

  uniq%  >= 70        maxclu <= 5        neardup <= 0.40 per card

  advisory band, printed by --gate and never pass/fail:
  official territory uniq 72-86 | maxclu 4-5 | neardup 0.24-0.36/card

vocab/top% carry NO GATE, permanently (ruled 2026-07-27): themed
concentration is design, not defect, and the official idea-count edge is
the same phenomenon uniq% already enforces from the other side --
double-gating one phenomenon invites gaming the metric. They remain report
columns and pool-sweep guidance. rider%/decide% carry NO gate --
measurement showed both are non-divergent (official rider% 26 sits inside
our 25-37; official decide% 20 equals Klee's).

The gate is also a RED TEST: tier0/tests/test_distinctness_gate.py runs
gate_breaches over every pool and fails on any breach not in its curated
known-failing list, so NEW regressions bite immediately while existing
debt is worked off by the pool-sweep pass.

THE SECOND ANCHOR, AND WHY NO THRESHOLD READ OFF IT HAS HELD STILL
(2026-07-27, Silent anchor sprint; full analysis in
docs/silent-anchor-sprint-log-2026-07-27.md). This docstring used to say
"Ratify after a SECOND official anchor". The second anchor arrived, and its
`uniq` moved SIX times across seven readings in one day as more of her pool
became expressible. Every reading is kept, because the SEQUENCE is the
finding and any single row of it would be a lie by omission:

  OFFICIAL:silent  22/88 (25%)  vocab  9  top 50%  uniq 59%  maxclu 3  FAIL
  OFFICIAL:silent  27/88 (31%)  vocab  9  top 48%  uniq 63%  maxclu 3  FAIL
  OFFICIAL:silent  46/88 (52%)  vocab 28  top 35%  uniq 78%  maxclu 3  pass
  OFFICIAL:silent  56/88 (64%)  vocab 29  top 39%  uniq 73%  maxclu 4  FAIL
  OFFICIAL:silent  59/88 (67%)  vocab 30  top 40%  uniq 72%  maxclu 4  FAIL
  OFFICIAL:silent  75/86 (87%)  vocab --  top --   uniq 73%  maxclu --  FAIL
  OFFICIAL:silent  85/86 (99%)  vocab 50  top 31%  uniq 72%  maxclu 5  FAIL

  (The 75-card row's other columns were not recorded when that reading was
  taken and the intermediate pool state is not reconstructible -- game_ref
  is not versioned. `--` is "unrecorded", not zero.)

  THE LAST ROW IS THE ONE THAT MATTERS, because coverage is no longer a
  confound: her pool is COMPLETE bar one card ([USER] sent Blade Of Ink to an
  enchantments design pass). `uniq` finished where it started -- 72% at 59
  cards and 72% at 85 -- having passed through 78% on the way. Twenty-six
  more cards moved it by nothing, `vocab` by twenty, and `maxclu` UP to 5.
  A finished real base-game pool fails two of the three thresholds.

  That is now a fact about the THRESHOLDS, not about the coverage. Ask A2
  deferred ratification until the pool completed; it has completed, and the
  question it was deferred for is answerable: no pool measured by this tool
  -- ours or the base game's -- has ever passed uniq 75%, and the one pool
  that did (at 46 cards) was the least complete reading taken.
  Every `cards` column above runs one HIGHER than the coverage numerator:
  the Shiv TOKEN is a pool row and is not one of the draftable cards.

  The /88 in the early rows is the denominator AS IT WAS READ AT THE TIME,
  kept unedited because a re-based history is not a history. It is now 86:
  the extractor reads CardMultiplayerConstraint and drops the two cards the
  game itself marks MultiplayerOnly (Flanking, Sneaky), which no DSL work
  could ever make appear in a single-player run. Ironclad's is 85, not 87,
  for the same reason (Demonic Shield, Tank). NONE of the gate columns moved
  when the denominator did -- distinctness is computed over the pool, so
  that change touched the coverage story and nothing about the measurement.

  * Two conclusions were drawn and then overturned by more coverage. At
    22-27 cards: "our pools post 56-62%, Ironclad posts 86%, so HE is the
    outlier and the gate condemns us for matching the other anchor." At 46:
    "the anchors agree with each other and disagree with us." Neither
    statement survived, and the completed pool retired the premise of both.
  * The control that licensed the first conclusion was a good experiment
    with a misleading answer: restricting IRONCLAD to his structurally
    simple subset RAISES his uniq (86 -> 89), which said "thinness does not
    depress uniq". It does not depress HIS. Coverage bias is a property of
    the SLICE -- her thin slices were poison/Sly cards that share signatures
    with each other -- and a control run on the other anchor cannot see it.
  * `maxclu` and `neardup` looked stable across the first five readings and
    then BOTH breached on the completed pool (5, and 31 against a 28 budget).
    Nothing in this table was safe to calibrate on early -- including the two
    columns that spent five readings looking like they were.

ASK A2 IS CLOSED (2026-07-27). The completed anchor failing the old
PROPOSED thresholds made them a statement about the thresholds, and [USER]
ruled: recalibrate off the completed second anchor. The ratified numbers
above are floors against the official BAND, not a portrait of Ironclad.
Standing lesson from the sequence below, recorded in the ratification doc:
partial-pool anchors can only loosen a threshold's credibility, never
certify it -- both of §6.5's would-be certifications (maxclu <= 4,
neardup <= 0.33) were overturned by the completed pool.

vocab/top% still carry NO GATE, and they moved the same way: at 22 cards her
vocabulary was NINE ideas against Ironclad's 40 and her top% read 50%, which
said "the most archetype-concentrated official character". At 59 it is 30
ideas and 40%. The thin readings were measuring the extractor, not her.

Applies to pools of 30+ cards (companion sheets exempt by size). That
exemption swallowed OFFICIAL:silent whole while she was under 30, which is
why --gate now PRINTS what it skipped: for two days the anchor added to
ratify the gate was never evaluated by it, and nothing said so.
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys
from collections import Counter, defaultdict

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SHEETS = sorted(glob.glob(os.path.join(REPO, "docs", "*-cards.yaml"))) + \
         [os.path.join(REPO, "docs", "mondstadt-companions.yaml")]


def _game_ref_pools() -> list[str]:
    """The ASSEMBLED official pools -- what the loader actually serves.

    THE NAMING TRAP THIS EXISTS TO AVOID. A `*-cards.yaml` glob (hyphen)
    matches `ironclad-cards.yaml`, which is the INITIAL EXTRACTION SNAPSHOT:
    35 cards plus a 52-entry `excluded:` dict of things the DSL could not
    express AT THE TIME. The live pool is `ironclad_pool.yaml` (underscore,
    so the hyphen glob never saw it) at 76 cards -- the snapshot plus passes
    4/5/6 (22 + 10 + 9), each of which implemented more of that excluded
    list. Reading the snapshot understated the official anchor by 41 cards
    and, worse, made the anchor look mechanically trivial (vocab 6,
    decide% 3%) because the excluded 52 were exactly the interesting ones.

    So: prefer `<char>_pool.yaml`, and fall back to `<char>-cards.yaml` only
    for a character that has no assembled pool yet. The `_pass<N>` layers are
    NOT globbed -- they are provenance, already merged into `_pool`, and
    including them would double-count every card they added.
    """
    ref = os.path.join(REPO, "game_ref")
    pools = sorted(glob.glob(os.path.join(ref, "*_pool.yaml")))
    have = {os.path.basename(p).replace("_pool.yaml", "") for p in pools}
    snapshots = [p for p in sorted(glob.glob(os.path.join(ref, "*-cards.yaml")))
                 if os.path.basename(p).replace("-cards.yaml", "") not in have]
    return pools + snapshots


GAME_REF = _game_ref_pools()

# Plain stat-riders: the "plus a Strike / plus some Block" vocabulary.
# An op counts as a rider only when UNSCALED and UNCONDITIONAL -- a scaling
# damage line is a card idea, a flat one stapled beside a core is filler.
RIDER_OPS = {"damage@one", "block@self", "draw", "energy",
             "gain_encore", "gain_spark", "gain_charge"}

DECISION_KEYS = {"if", "then", "else", "select", "bonus_formula",
                 "amount_formula", "bonus_vs_aura", "consumes_aura",
                 "applies_element", "cost_override"}

TARGET_CLASS = {
    "self": "self", "ally": "self", "all_allies": "self",
    "enemy": "one", "one": "one", "single": "one",
    "all": "all", "all_enemies": "all", "aoe": "all",
    "random": "rand", "random_enemy": "rand", "random_enemies": "rand",
}

# Gate thresholds. RATIFIED [USER] 2026-07-27 against the COMPLETE
# two-anchor band (docs/a2-gate-ratification-2026-07-27.md): hard floors
# sit at the official FLOOR with modest modding headroom, and the official
# band is printed as an advisory line so "passes the gate" is never
# mistaken for "matches Ironclad".
GATE_MIN_UNIQ = 70          # official floor 72 (silent), -2 headroom
GATE_MAX_CLUSTER = 5        # official floor is 5 (silent)
GATE_NEARDUP_PER_CARD = 0.40  # official floor 0.36 (silent), +headroom
# Advisory only, never pass/fail: where the two official anchors landed.
OFFICIAL_BAND = "uniq 72-86% | maxclu 4-5 | neardup 0.24-0.36/card"
# Companion sheets are exempt by SIZE, which is a proxy for "not a character
# pool" -- and a proxy that misfired: OFFICIAL:silent IS a character pool and
# spent two days under this floor, invisible to the gate she was added to
# ratify. She is over it now (60 rows) at nobody's decision but the
# extractor's, which is the argument for making the exemption by KIND. Until
# then --gate PRINTS what it skipped, so an exemption cannot read as a pass
# (2026-07-27, Silent anchor sprint E-2).
GATE_MIN_POOL = 30


def _is_scaled(e: dict) -> bool:
    amt = e.get("amount")
    return bool(e.get("bonus_formula") or e.get("amount_formula")
                or (isinstance(amt, str) and ("X" in amt or "per" in amt))
                or e.get("bonus_vs_aura") or (e.get("times", 1) not in (1, None)))


def _tokens(effects, wrapped=False):
    """Flatten an effects list (recursing through conditionals) to tokens."""
    out = []
    for e in effects or []:
        if not isinstance(e, dict):
            continue
        op = e.get("op", "?")
        if op == "conditional":
            inner = _tokens(e.get("then", []), True) + \
                    _tokens(e.get("else", []), True)
            out += [f"?{t}" for t in inner]
            continue
        tok = op
        tgt = TARGET_CLASS.get(str(e.get("target", "")).lower())
        if op in ("damage", "block", "apply_power", "apply_aura", "heal") and tgt:
            tok += f"@{tgt}"
        if op == "apply_power":
            tok += f":{e.get('power', '?')}"      # WHICH power is the idea
        if _is_scaled(e):
            tok += "~"
        if wrapped:
            tok = tok        # ? prefix added by caller
        out.append(tok)
    return out


def idea(tok: str) -> str:
    """A token reduced to its EFFECTIVE idea, for vocab/hapax/top%.

    Strips target class and the scaling/conditional qualifiers -- those are
    structure, already carried by the signature -- but KEEPS `:power`,
    because apply_power:vulnerable and apply_power:barricade are two ideas
    wearing one op name. See the representation-artifact note in the module
    docstring: getting this wrong inverted the whole vocab ranking.
    """
    return re.sub(r"@\w+", "", tok).rstrip("~").lstrip("?")


def signature(card: dict) -> tuple:
    toks = _tokens(card.get("effects"))
    if str(card.get("cost")) == "X":
        toks.append("#X")
    if card.get("exhaust"):
        toks.append("#exhaust")
    return tuple(sorted(Counter(toks).elements()))


def _is_rider(tok: str) -> bool:
    return tok in RIDER_OPS and "~" not in tok and not tok.startswith("?")


def core_signature(sig: tuple) -> tuple:
    return tuple(t for t in sig if not _is_rider(t))


def _has_decision(card: dict) -> bool:
    if str(card.get("cost")) == "X":
        return True
    def walk(effects):
        for e in effects or []:
            if not isinstance(e, dict):
                continue
            if DECISION_KEYS & set(e.keys()) or e.get("op") == "conditional":
                return True
            if walk(e.get("then")) or walk(e.get("else")):
                return True
        return False
    return walk(card.get("effects"))


def analyze(name: str, rows: list[dict]) -> dict:
    cards = [c for c in rows if isinstance(c, dict) and c.get("effects")]
    sigs = {c["id"]: signature(c) for c in cards}
    sig_count = Counter(sigs.values())
    ops = Counter()          # EFFECTIVE vocabulary: apply_power:vulnerable
    for c in cards:          # and apply_power:strength are different ideas
        for t in set(_tokens(c.get("effects"))):
            ops[idea(t)] += 1
    core = defaultdict(list)
    for cid, s in sigs.items():
        cs = core_signature(s)
        if cs != s:                      # only cards that HAVE riders
            core[cs].append(cid)
    neardup_families = {k: v for k, v in core.items() if len(v) > 1}
    neardup_pairs = sum(len(v) * (len(v) - 1) // 2
                        for v in neardup_families.values())
    rider_cards = [cid for cid, s in sigs.items()
                   if any(_is_rider(t) for t in s)
                   and any(not _is_rider(t) for t in s)]
    n = len(cards) or 1
    return {
        "pool": name, "cards": len(cards),
        "vocab": len(ops),
        "hapax": sum(1 for _, k in ops.items() if k == 1),
        "top%": 100 * max(ops.values(), default=0) / n,
        "uniq%": 100 * sum(1 for s in sigs.values()
                           if sig_count[s] == 1) / n,
        "maxclu": max(sig_count.values(), default=0),
        "rider%": 100 * len(rider_cards) / n,
        "neardup": neardup_pairs,
        "decide%": 100 * sum(1 for c in cards if _has_decision(c)) / n,
        "_families": {**neardup_families},
        "_clusters": {s: [cid for cid, x in sigs.items() if x == s]
                      for s, k in sig_count.items() if k > 1},
    }


def load_pool(path: str) -> list[dict]:
    """Every card row in a sheet, across ALL of its YAML documents.

    safe_load_all, not safe_load: the extractor emits game_ref sheets as a
    TWO-DOCUMENT stream -- the cards, then a `---` and an `excluded:` dict
    naming what the Tier 0 DSL could not express and why. safe_load raises
    on the second document, which silently dropped OFFICIAL:ironclad -- the
    one row the whole tool calibrates against -- while still printing a
    clean-looking table, because the error goes to stderr and any run that
    redirects stdout loses it entirely.

    encoding is EXPLICIT: these sheets are UTF-8 and the Windows default is
    cp1252, the same trap art_fetch.read_plan documents at length.
    """
    with open(path, encoding="utf-8") as fh:
        docs = list(yaml.safe_load_all(fh))
    return [c for d in docs if isinstance(d, list) for c in d]


def gate_breaches(reports: list[dict]) -> tuple[list[tuple], list[str]]:
    """Apply the RATIFIED gate. Returns (breaches, skipped).

    Each breach is (pool, metric, message) so the suite's red test can key
    its curated known-failing list on (pool, metric) instead of parsing
    strings. Shared by --gate and tier0/tests/test_distinctness_gate.py --
    one gate, two mouths.
    """
    breaches, skipped = [], []
    for r in reports:
        if r["cards"] < GATE_MIN_POOL or "/" in r["pool"]:
            if "/" not in r["pool"]:
                skipped.append(f"{r['pool']} ({r['cards']} cards)")
            continue
        if r["uniq%"] < GATE_MIN_UNIQ:
            breaches.append((r["pool"], "uniq",
                             f"{r['pool']}: uniq {r['uniq%']:.0f}% < "
                             f"{GATE_MIN_UNIQ}%"))
        if r["maxclu"] > GATE_MAX_CLUSTER:
            breaches.append((r["pool"], "maxclu",
                             f"{r['pool']}: maxclu {r['maxclu']} > "
                             f"{GATE_MAX_CLUSTER}"))
        if r["neardup"] > GATE_NEARDUP_PER_CARD * r["cards"]:
            breaches.append((r["pool"], "neardup",
                             f"{r['pool']}: neardup {r['neardup']} > "
                             f"{GATE_NEARDUP_PER_CARD * r['cards']:.0f}"))
    return breaches, skipped


def build_reports(pool_filter: str | None = None,
                  by_rarity: bool = False) -> list[dict]:
    """One analyzed report per readable pool -- the single producer behind
    both the CLI table and the suite's red gate test, so the two can never
    disagree about which pools exist or what they are called."""
    reports = []
    for path in SHEETS + GAME_REF:
        if not os.path.exists(path):
            continue
        name = os.path.basename(path).replace("-cards.yaml", "") \
                                     .replace("_pool.yaml", "") \
                                     .replace(".yaml", "")
        if "game_ref" in path:
            name = f"OFFICIAL:{name}"
        if pool_filter and pool_filter not in name:
            continue
        # An unreadable pool is a HARD FAILURE, not a stderr note. It used to
        # `continue`, which silently narrowed the gate's scope -- and because
        # tier0/tests/test_distinctness_gate.py asserts "no NEW breaches" over
        # whatever build_reports() returns, a pool that stopped parsing simply
        # left the comparison and its breaches became a passing test. The one
        # legitimate absence (a gitignored game_ref pool) is already handled by
        # the os.path.exists check above; PRESENT-BUT-UNPARSEABLE is a defect.
        try:
            rows = load_pool(path)
        except Exception as exc:
            raise RuntimeError(
                f"{name}: pool file exists but could not be read ({path}): "
                f"{type(exc).__name__}: {exc}. Refusing to report on a "
                f"narrowed pool set -- the gate would pass by not looking."
            ) from exc
        if rows:
            reports.append(analyze(name, rows))
            if by_rarity:
                for rar in ("common", "uncommon", "rare"):
                    sub = [c for c in rows if isinstance(c, dict)
                           and c.get("rarity") == rar]
                    if sub:
                        reports.append(analyze(f"{name}/{rar}", sub))
    return reports


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", help="restrict to one pool name substring")
    ap.add_argument("--families", action="store_true",
                    help="list near-duplicate families and clone clusters")
    ap.add_argument("--by-rarity", action="store_true",
                    help="emit one row per (pool, rarity)")
    ap.add_argument("--gate", action="store_true",
                    help="apply the RATIFIED gate; exit 1 on any breach")
    args = ap.parse_args()
    reports = build_reports(args.pool, args.by_rarity)

    print(f"{'pool':30} {'cards':>5} {'vocab':>5} {'hapax':>5} {'top%':>5} "
          f"{'uniq%':>6} {'maxclu':>6} {'rider%':>6} {'neardup':>7} "
          f"{'decide%':>7}")
    for r in reports:
        print(f"{r['pool']:30} {r['cards']:>5} {r['vocab']:>5} "
              f"{r['hapax']:>5} {r['top%']:>4.0f}% {r['uniq%']:>5.0f}% "
              f"{r['maxclu']:>6} {r['rider%']:>5.0f}% {r['neardup']:>7} "
              f"{r['decide%']:>6.0f}%")
    if not GAME_REF:
        print("\n  (no game_ref/ pools found -- run "
              "tools/extract_base_game_pool.py locally for official anchors)")

    if args.gate:
        # A gate with no anchor present is not a gate, it is three numbers
        # somebody typed. Say so rather than passing/failing against them.
        if not any(r["pool"].startswith("OFFICIAL:") for r in reports):
            print("\nGATE: NO OFFICIAL ANCHOR IN THIS RUN -- thresholds are "
                  "calibrated against one and cannot be checked without it. "
                  "Run tools/extract_base_game_pool.py locally.", file=sys.stderr)
            return 2
        breaches, skipped = gate_breaches(reports)
        print(f"\nGATE (RATIFIED 2026-07-27) -- official territory, "
              f"advisory only: {OFFICIAL_BAND}")
        if skipped:
            print(f"GATE SKIPPED (under {GATE_MIN_POOL} cards -- this is NOT "
                  f"a pass): {', '.join(skipped)}")
        if breaches:
            print("\nGATE BREACHES (thresholds RATIFIED against the "
                  "two-anchor floor -- docs/a2-gate-ratification-"
                  "2026-07-27.md; known debt is curated in "
                  "tier0/tests/test_distinctness_gate.py):")
            for _, _, b in breaches:
                print(f"  FAIL {b}")
            return 1
        print("\nGATE: all pools clear.")

    if args.families:
        for r in reports:
            fams = r["_families"]
            clus = r["_clusters"]
            if not fams and not clus:
                continue
            print(f"\n== {r['pool']} ==")
            for s, ids in sorted(clus.items(), key=lambda kv: -len(kv[1])):
                print(f"  CLONES {len(ids)}x {'+'.join(s) or '(vanilla)'}: "
                      f"{', '.join(sorted(ids))}")
            for cs, ids in sorted(fams.items(), key=lambda kv: -len(kv[1])):
                print(f"  NEARDUP core[{'+'.join(cs) or 'stat-only'}]: "
                      f"{', '.join(sorted(ids))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

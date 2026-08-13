"""Strict-domination lint across card sheets (worknote 2026-07-20 item 2).

Rarity buys different or bigger-with-a-twist, never "the common plus
stuff": two cards at the same cost/type/gates where
one's effect set is a superset of the other's with every shared amount
>= (and at least one strict excess) leave the lesser card a dead pick.
Confirmed class: cant_catch_me over warm_glow (Klee, queued errata),
pit_orchestra over macaron_break (Furina, resolves pass 2).

Scope per the assigning worknote, narrowed by R26 (2026-07-20): the law
protects draft decisions between cards competing at similar weight —
an ADJACENT-RARITY phenomenon (common<->uncommon, uncommon<->rare).
Adjacent-rarity strict dominations are findings; two-step gaps (rare
over common) print as informational only — rares are the designated
power spike, and a rare obsoleting a common's slot is the rarity ladder
working. Basics are excluded entirely — starters are supposed to be
outclassed (Strike is strictly dominated by half the base game, by
design). Cards are only compared inside an identical (cost, type,
encore_cost, fanfare_cost, exhaust, tags) group, so a resource gate or Exhaust
rider makes a pair incomparable rather than falsely dominated; formula
amounts also mark a card incomparable.

Effects are split into benefits and COSTS (self-damage, discard,
spend_encore): domination needs benefits superset-with-all->= AND costs
subset-with-all-<=. Hot Hands (spark 3 + 2 self-damage) does NOT
dominate Spark Collection (spark 2) — the blood is the twist that
uncommon legitimately buys. This matters: without it the lint's first
run flagged three ratified bigger-with-a-twist shapes as dominations.

KNOWN pairs are dominations already ruled on and awaiting their
scheduled fix: printed as notes, exit stays 0. Remove an entry when its
errata lands — the lint then guards the fix.

CROSS-SHEET SWEEP (tooling-hardening sprint, 2026-07-29). Until now this
lint compared cards only against SIBLINGS IN THE SAME FILE, and the sheets
are split by author and by nation rather than by what competes — so the
gate's scope was a filesystem accident. `sucrose_catalyst_conversion` lives
in mondstadt-companions.yaml and `moonlit_offering` in kokomi-cards.yaml,
and no rule in this repo could see that the shared Uncommon is strictly
better than the personal Rare. The precedent is on the record:
docs/archive/fontaine-rares-banner-sprint-log.md item 2, the Clorinde/Raiden pair
"flagged BY HAND because no lint could see it".

The comparability rules are IDENTICAL cross-sheet (same group tuple, same
adjacent-rarity narrowing, same benefit/cost split). The cross pass adds
exactly one question — CAN THESE TWO CARDS BE DRAFTED IN ONE RUN? — because
the law protects draft decisions, and two cards that never meet on a reward
screen are not a decision:

  * companions vs companions: YES. rewards.companion_pool() is every
    non-guest companion of EVERY nation; `nation` only weights the roll.
  * a personal sheet vs companions: YES. Both fill the same reward screen.
  * two personal sheets: NO. Klee's cards and Kokomi's never co-occur.

Non-draftable rows are excluded from BOTH sweeps — see `draftable`.

SCOPE REPORTING. The old summary printed a bare `CLEAN: <sheet names>`,
which claimed more than it had checked: rows with no `effects`, basics, and
cards whose amounts are FORMULAS were all dropped before comparison and
counted toward nothing. The scope block now states what was compared and
what was not, so "clean" is a statement with a denominator.

Usage: python tools/lint_strict_domination.py docs/klee-cards.yaml [...]
       python tools/lint_strict_domination.py --within-only [...]
Exit 0 clean; exit 1 with one finding per line.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(REPO))

from tools.effect_walk import sly_autoplays, sly_riders  # noqa: E402

# Known dominations awaiting their scheduled fix. Remove when landed.
# (cant_catch_me/warm_glow was here; FIXED by the R25 errata batch,
# 2026-07-20 — CCM block 4 -> 2. The lint now guards the fix.)
# (pit_orchestra/macaron_break was here; FIXED at Furina pass 2 —
# Encore rider trimmed to 1. The lint now guards the fix.)
KNOWN: set[frozenset] = set()

# Lint-discovered dominations with NO ruling yet (DECISIONS 76). They do
# not fail the lint — the sheets belong to their sessions and edits need
# red-pen first — but they print as NEEDS RULING until dispositioned:
# move to KNOWN with a schedule, fix the rows, or rule them accepted.
# (sparkly_explosion/big_badda_boom was here; CLEARED by R26 — a
# rare-over-common two-step gap is informational, not a finding.)
# (dodge_roll/hide_and_seek was here; RESOLVED by the R25 errata batch,
# 2026-07-20 — dodge_roll block 8 -> 6 < hide_and_seek's 7, so the
# superset no longer dominates. The lint now guards the fix.)
PENDING_RULING: set[frozenset] = set()

RARITY_ORDER = {"common": 0, "uncommon": 1, "rare": 2}

# CROSS-SHEET dominations that PREDATE the cross-sheet sweep (2026-07-29).
# Same pattern, and for the same reason, as test_distinctness_gate.KNOWN_FAILING
# and art_lint's PENDING sets: the sweep found real pairs the moment it was
# switched on, the sheets belong to their design sessions, and changing a
# printed card needs red-pen first. So these print as notes and CI stays green
# WITHOUT the findings disappearing -- they are enumerated here, with their
# numbers, and `test_the_cross_sheet_allowlist_is_not_stale` deletes an entry
# the day its pair stops dominating.
#
# NOT a blanket suppression: a NEW cross-sheet domination fails immediately.
# Every entry below is queued for docs/sprint-tooling-hardening-log-2026-07-29
# ("cross-sheet domination findings, for red-pen").
CROSS_KNOWN: set[frozenset] = {
    # THE HEADLINE, and the exact Clorinde/Raiden shape. Both 0-cost
    # self-Exhaust skills; identical benefits (1 energy + 1 draw); the RARE
    # additionally pays `discard 1`. A shared Uncommon any character can draw
    # is strictly better than one character's Rare.
    frozenset({"sucrose_catalyst_conversion", "moonlit_offering"}),
    # 1-cost skills. communion_of_tides: exhaust_from 1 (chosen) + draw 2.
    # lynette_box_trick: draw 2, nothing else. The Uncommon is the common plus
    # a free Exhaust trigger.
    frozenset({"communion_of_tides", "lynette_box_trick"}),
    # 0-cost skills. sayu_naptime: block 3 + draw 1. moon_signal: discard 1 +
    # draw 1 -- the Common pays a cost the Uncommon does not, and gains less.
    frozenset({"sayu_naptime", "moon_signal"}),
    # 0-cost skills, and the SAME PAIR SHAPE one row up. sucrose_gust was
    # bumped common -> uncommon by the 2026-08-06 sitting (family X2: infinite
    # cycling engines are gated to Uncommon+), which made it sayu_naptime's
    # twin against moon_signal: swirl + draw 1 vs discard 1 + draw 1. The
    # finding is inherited from the ratified rarity move, not a new design
    # choice; it queues for red-pen beside its twin.
    frozenset({"sucrose_gust", "moon_signal"}),
    # --- THE ELEMENT CLUSTER, four pairs of one shape. shinobu_thundergrust
    # is a 1-cost applier attack for 7; the four Commons are the same card at
    # 5-6. They differ ONLY in `element`, which this lint does not read,
    # because `applies_element: true` is the whole effect vocabulary for it.
    # Whether an element is a comparability dimension (a cryo applier and an
    # electro applier enable different reactions, so arguably they never
    # compete for one slot) is the RULING these four are waiting on -- see the
    # sprint log. Listed rather than pre-decided by a code change.
    frozenset({"shinobu_thundergrust", "dahlia_sacramental_shower"}),
    frozenset({"shinobu_thundergrust", "fischl_nightrider"}),
    frozenset({"shinobu_thundergrust", "kaeya_frostgnaw"}),
    frozenset({"shinobu_thundergrust", "freminet_pers_deploy"}),
}


def is_cost(eff: dict) -> bool:
    """Detrimental effect: paying it is worse, not better."""
    op = eff.get("op")
    return (op in ("discard", "spend_encore")
            or (op == "damage" and eff.get("target") == "self"))


def effect_maps(card: dict) -> tuple[dict, dict] | None:
    """(benefits, costs) as signature -> total amount; None if incomparable.

    Sly riders (Kokomi v0.2, 2026-07-24) are printed value the first lint
    build silently dropped -- which made every plain-Block common "dominate"
    a Sly card of equal face. They count as benefits under a ("sly","true")
    key so a Sly line is its own dimension, never conflated with the same
    op in the played face.

    EB-71 (R174): the reserved `sly_autoplay` marker is the base-game
    keyword, not a printed effect. It is INCOMPARABLE rather than a benefit
    of amount 1 -- what it is worth depends on the card it re-plays, so no
    signature over it can honestly say one row's copy beats another's."""
    if sly_autoplays(card):
        return None
    good: dict = {}
    bad: dict = {}
    tagged = ([(eff, False) for eff in card.get("effects", [])]
              + [(eff, True) for eff in sly_riders(card)])
    for eff, from_sly in tagged:
        m = bad if (is_cost(eff) and not from_sly) else good
        eff = dict(eff)
        amount = eff.pop("amount", 1)
        if not isinstance(amount, int):
            return None  # formula/complex amount
        if from_sly:
            eff["sly"] = "true"
        key = tuple(sorted((k, str(v)) for k, v in eff.items()))
        m[key] = m.get(key, 0) + amount
    return good, bad


def dominates(a: dict, b: dict) -> bool:
    ea, eb = effect_maps(a), effect_maps(b)
    if ea is None or eb is None:
        return False
    ga, ca = ea
    gb, cb = eb
    # benefits: a carries everything b does, at >= amounts
    if not set(gb) <= set(ga) or any(ga[k] < gb[k] for k in gb):
        return False
    # costs: a pays no cost b doesn't, at <= amounts
    if not set(ca) <= set(cb) or any(ca[k] > cb[k] for k in ca):
        return False
    return (ga, ca) != (gb, cb)


def comparison_group(card: dict) -> tuple:
    return (card.get("cost"), card.get("type"), card.get("encore_cost"),
            card.get("fanfare_cost"), card.get("exhaust"),
            tuple(sorted(card.get("tags", []))))


def draftable(card: dict) -> bool:
    """Can this row ever be OFFERED as a draft choice?

    The law's stated purpose is protecting "draft decisions between cards
    competing at similar weight", so a row that never reaches a reward screen
    is outside it by construction -- the same argument the docstring already
    makes for excluding basics.

    Two kinds are excluded, both read straight off the row:

      * `kit_card` -- Bursts. `rewards.character_pool` skips them ("kit, not
        loot -- never offered"), so they are in nobody's rarity ladder.
      * `guest_star` -- Furina's generated cameos. `rewards.companion_pool`
        skips them, and the only door in is a generator that serves them at
        EXACTLY its own rarity (`guest_star_generation_pool`). A rule about
        what rarity BUYS has nothing to say about a card rarity cannot be
        spent on.

    Deliberately NOT a way to shrink the gate: with both filters on, the
    within-sheet sweep still reports exactly what it reported before.
    """
    return not card.get("kit_card") and not card.get("guest_star")


def sheet_cards(path: Path) -> tuple[list[dict], dict[str, int]]:
    """(cards this lint will compare, scope counters).

    The counters exist because the summary line used to say CLEAN about a
    sheet whose rows it had mostly dropped. Every exclusion below is a row
    the sweep has NO OPINION about, and a gate that cannot say how many of
    those there were is not reporting its own scope.
    """
    rows = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    rows = [c for c in rows if isinstance(c, dict)]
    scope = {"rows": len(rows), "no_effects": 0, "basic": 0,
             "not_draftable": 0, "formula": 0, "compared": 0}
    cards = []
    for c in rows:
        if not c.get("effects"):
            scope["no_effects"] += 1
            continue
        if c.get("rarity") in (None, "basic"):
            scope["basic"] += 1
            continue
        if not draftable(c):
            scope["not_draftable"] += 1
            continue
        if effect_maps(c) is None:
            # A formula amount makes the card incomparable to EVERYTHING, so
            # it is dropped here rather than silently inside dominates().
            scope["formula"] += 1
            continue
        cards.append(c)
    scope["compared"] = len(cards)
    return cards, scope


def _verdict(a: dict, b: dict, msg: str, known: set[frozenset],
             findings: list[str], notes: list[str]) -> None:
    """The shared disposition: KNOWN, non-adjacent, pending, or a finding.

    Factored out so the cross-sheet sweep cannot drift away from the
    within-sheet one on the part that decides what counts.
    """
    pair = frozenset({a["id"], b["id"]})
    ra = RARITY_ORDER.get(a["rarity"])
    rb = RARITY_ORDER.get(b["rarity"])
    adjacent = ra is not None and rb is not None and abs(ra - rb) == 1
    if pair in known:
        notes.append(f"known (allowlisted): {msg}")
    elif not adjacent:
        notes.append(f"informational (non-adjacent rarities, R26): {msg}")
    elif pair in PENDING_RULING:
        notes.append(f"NEEDS RULING (pending, DECISIONS 76): {msg}")
    else:
        findings.append(msg)


def lint_sheet(path: Path) -> tuple[list[str], list[str], dict[str, int]]:
    cards, scope = sheet_cards(path)
    findings: list[str] = []
    notes: list[str] = []
    for a in cards:
        for b in cards:
            if a is b or a["rarity"] == b["rarity"]:
                continue
            if comparison_group(a) != comparison_group(b):
                continue
            if dominates(a, b):
                _verdict(a, b, f"{path.name}: {a['id']} ({a['rarity']}) "
                               f"strictly dominates {b['id']} ({b['rarity']}) "
                               f"at cost {a.get('cost')}",
                         KNOWN, findings, notes)
    return findings, notes, scope


def co_draftable(sheet_a: str, sheet_b: str) -> bool:
    """Can a card from sheet A and a card from sheet B appear in ONE run?

    Read off the pool assembly, not asserted: `rewards.companion_pool()`
    collects every non-guest companion of EVERY nation (nation only weights
    the roll in `_nation_weighted_choice`), and `rewards.character_pool()`
    requires `c.character == character_id`, which is set from the
    `<name>-cards.yaml` filename. So:

      companions x companions -> yes (one shared pool, every run)
      companions x personal   -> yes (they fill the same reward screen)
      personal   x personal   -> NO. Two characters' kits never co-occur, so
                                 a domination between them is not a draft
                                 decision and flagging it would be noise.
    """
    a_comp = sheet_a.endswith("-companions.yaml")
    b_comp = sheet_b.endswith("-companions.yaml")
    return a_comp or b_comp


def lint_cross_sheet(paths: list[Path]) -> tuple[list[str], list[str],
                                                 dict[str, int]]:
    """The pass the Clorinde/Raiden catch needed and did not have.

    Compares only pairs from DIFFERENT sheets (the within-sheet sweep owns
    the rest) and only where `co_draftable` says the two rows can meet.
    """
    tagged: list[tuple[str, dict]] = []
    scope = {"sheets": len(paths), "compared": 0, "sheet_pairs": 0}
    for p in paths:
        cards, _ = sheet_cards(p)
        tagged.extend((p.name, c) for c in cards)
    scope["compared"] = len(tagged)
    scope["sheet_pairs"] = sum(
        1 for i, a in enumerate(paths) for b in paths[i + 1:]
        if co_draftable(a.name, b.name))

    findings: list[str] = []
    notes: list[str] = []
    seen: set[frozenset] = set()
    for sheet_a, a in tagged:
        for sheet_b, b in tagged:
            if sheet_a == sheet_b or a["rarity"] == b["rarity"]:
                continue
            if not co_draftable(sheet_a, sheet_b):
                continue
            if comparison_group(a) != comparison_group(b):
                continue
            # One line per ordered pair, but never the same pair twice from
            # the two directions of the outer loops.
            key = frozenset({a["id"], b["id"]})
            if key in seen:
                continue
            if dominates(a, b):
                seen.add(key)
                _verdict(a, b,
                         f"CROSS-SHEET {sheet_a}:{a['id']} ({a['rarity']}) "
                         f"strictly dominates {sheet_b}:{b['id']} "
                         f"({b['rarity']}) at cost {a.get('cost')}",
                         CROSS_KNOWN, findings, notes)
    return findings, notes, scope


DEFAULT_SHEETS = ("klee-cards.yaml", "furina-cards.yaml",
                  "kokomi-cards.yaml", "mondstadt-companions.yaml",
                  "fontaine-companions.yaml", "inazuma-companions.yaml")


def main(argv: list[str]) -> int:
    within_only = "--within-only" in argv
    argv = [a for a in argv if a != "--within-only"]
    # Default = every canonical sheet (the pytest gate fans over the same
    # set); the old two-sheet default silently skipped Kokomi + companions
    # for anyone running the tool by hand.
    paths = [Path(a) for a in argv] or [REPO / "docs" / s
                                        for s in DEFAULT_SHEETS]
    findings: list[str] = []
    scopes: dict[str, dict[str, int]] = {}
    for p in paths:
        found, notes, scope = lint_sheet(p)
        findings.extend(found)
        scopes[p.name] = scope
        for n in notes:
            print(n)

    cross_scope = None
    if not within_only:
        found, notes, cross_scope = lint_cross_sheet(paths)
        findings.extend(found)
        for n in notes:
            print(n)

    for f in findings:
        print(f)

    # SCOPE, stated before the verdict. `CLEAN: <sheet names>` used to be the
    # entire report, and it read as "these sheets are clean" when what it meant
    # was "the subset of rows I compared had no findings". Everything this
    # sweep has no opinion about is now on the page with it.
    print("\nscope (rows this sweep has NO opinion about are itemised):")
    for name in sorted(scopes):
        s = scopes[name]
        print(f"  {name:<28} {s['compared']:>3}/{s['rows']:<3} compared  "
              f"(skipped: {s['no_effects']} no-effects, {s['basic']} basic, "
              f"{s['not_draftable']} non-draftable, {s['formula']} formula)")
    if cross_scope is not None:
        print(f"  CROSS-SHEET                 {cross_scope['compared']:>3} "
              f"cards over {cross_scope['sheet_pairs']} co-draftable sheet "
              f"pair(s) of {cross_scope['sheets']} sheets")
    else:
        print("  CROSS-SHEET                 NOT RUN (--within-only): a "
              "domination spanning two sheets is UNCHECKED")

    total = sum(s["compared"] for s in scopes.values())
    if not total:
        # A gate that compared nothing must never print CLEAN.
        print("VACUOUS: zero cards compared -- nothing was checked")
        return 1
    verdict = "CLEAN" if not findings else f"{len(findings)} finding(s)"
    print(f"{verdict} over {total} compared card(s) in "
          f"{len(paths)} sheet(s)"
          + ("" if not within_only else ", WITHIN-SHEET ONLY"))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

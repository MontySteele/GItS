"""`KLEESPARK-R2` — the Spark economy on NORMALIZED metrics. NOT REGISTERED.

THIS SCRIPT REGISTERS NOTHING AND PREDICTS NOTHING. It is an INSTRUMENT,
built under [USER]'s pick 6(d) (2026-08-29): *"fix pilot playability, then
re-register the probe on normalized metrics — spent / available Sparks and
affordable sinks skipped per turn — rather than the raw per-turn spend
rate."* The first half (playability) is code; this is the second half's
instrument only. The registration, the slate and any prediction are a LATER
slate and are deliberately absent here.

WHY A SIBLING AND NOT AN EDIT. `tier05/exp_klee_sparks_r1.py` is a PUBLISHED
instrument: the `KLEESPARK-R1` packet quotes its output at
`review/records/klee-sparks-r1-sim-2026-08-29.txt` and R101b says a published
measurement record stands as published. r1 is therefore byte-identical and
untouched, and this file is its successor.

WHAT R1's 0.72 ACTUALLY MEASURED, which is the whole reason this file exists.
r1 read a RAW rate — Sparks moved per player turn — and got 1.00 OFF against
0.72 ON, and the packet's sec.11.5 filed it as a MISS on P5. But r1 also
printed the income beside it: the OFF deck GAINED 1.14 Sparks/turn and the ON
deck gained 0.80. Both arms are income-bound, and the OFF arm's automatic
consume takes 3 whenever the bank permits, so on both arms the spend rate is
very nearly the generation rate. Normalized, the ON arm spent 213 of 235
Sparks it ever held (0.91) against the OFF arm's 243 of 276 (0.88): the priced
economy moved a HIGHER share of a SMALLER income. THE ARMS DIFFER IN THEIR
GENERATORS — PICK 4's one-for-one map converts four Spark GENERATORS into
Spark SINKS — so a raw per-turn rate is a measurement of the map, not of the
pilot. That confound is disclosed in this script's own header, per fight and
per arm, so it can never again be read past.

THE COLUMNS, defined here rather than after the numbers are seen:

  available   Sparks the turn COULD have spent = the bank at the turn's first
              decision (after every turn-start trigger) PLUS everything
              generated during the turn. Not the bank at any single instant.
  generated   `gain_spark` amounts inside the turn.
  spent       `spend_spark` amounts (printed prices and the strict Rare
              Power's debit) PLUS the retired base rule's automatic consume,
              which prints no amount and is charged at the threshold. On the
              ON arm the second half is structurally zero; on the OFF arm the
              first half is.
  spent/avail the normalized rate pick 6(d) names. Undefined (printed `-`)
              on a turn that had nothing available.
  skipped     AFFORDABLE SINKS SKIPPED. Counted at the moment the pilot
              DECLINES to play (its `None`), on the hand as it then stands: a
              card carrying a Spark price the bank can meet AND that
              `combat.card_playable` says is playable — so energy, gates and
              status clogs are already excluded and what is left is a CHOICE
              not to spend. A turn whose last decision played a card and was
              never asked again (the fight ended inside it) counts 0, because
              the instrument was not there to look.
  turns       player turns reached.
  win         the fight diagnostic. NOT A BALANCE CLAIM (R215 B), NOT
              quotable, Guardrail-7 applies whole. It is here because r1's
              40-versus-25 is the reason pick 6 was asked at all.

Usage: python -m tier05.exp_klee_sparks_r2 [--fights N] [--seed N]
                                           [--per-fight] [--per-turn]
"""

from __future__ import annotations

import sys

from tier0 import constants as C
from tier0.content import loader
from tier05 import expcli

# r1's two sets, unchanged and imported rather than retyped, so the arms this
# instrument compares are provably the arms r1 compared.
from tier05.exp_klee_sparks_r1 import (ENCOUNTER, PILOT, SHIPPED_SET,
                                       TIGHT_SET, _deck)


def _clear_caches() -> None:
    """Every memo a flag flip invalidates, in one place.

    `_card_prototype` and `_substituted_card_index` both read
    `C.SPARK_ALT_COST_ENABLED`, and `rewards.character_pool` reads the
    substitution map through `loader.pool_substitutions`. Flipping the flag
    without clearing all three silently serves the other arm's cards.
    """
    from tier05 import rewards
    loader._card_prototype.cache_clear()
    loader._substituted_card_index.cache_clear()
    rewards.character_pool.cache_clear()


def _generators(deck: list[str]) -> list[tuple[str, int]]:
    """`(id, sparks printed)` for every top-level `gain_spark` in the deck.

    THE INCOME CONFOUND, made visible before any rate is read. This is the
    quantity that differs between the arms by construction, and the reason the
    raw per-turn rate cannot be compared across them.
    """
    rows: dict[str, int] = {}
    for cid in deck:
        card = loader.peek_card(cid)
        n = sum(fx.get("amount", 1) for fx in card.effects
                if fx.get("op") == "gain_spark")
        if n:
            rows[cid] = rows.get(cid, 0) + n
    return sorted(rows.items())


def _sink_snapshot(state) -> int:
    """Priced cards in hand that are affordable AND playable right now."""
    from tier0.engine.combat import card_playable, spark_price
    n = 0
    for card in state.player.hand:
        price = spark_price(state, card)
        if price and price <= state.player.sparks and card_playable(state, card):
            n += 1
    return n


def _watched(pilot):
    """Wrap a pilot so each decision leaves a record, and nothing else.

    EMIT-ONLY: the wrapper reads state and returns exactly what the pilot
    returned, so a watched fight and an unwatched one are the same fight. The
    records are `(turn, bank, affordable sinks, played?)`, one per decision.
    """
    records: list[tuple[int, int, int, bool]] = []

    def watched(state):
        turn = state.turn
        bank = state.player.sparks
        sinks = _sink_snapshot(state)
        choice = pilot(state)
        records.append((turn, bank, sinks, choice is not None))
        return choice

    watched.records = records
    return watched


def _fight_rows(log: list[dict], records: list[tuple[int, int, int, bool]],
                threshold: int) -> list[dict]:
    """One row per player turn, from the log and the decision records."""
    gained: dict[int, int] = {}
    spent: dict[int, int] = {}
    for row in log:
        turn = row.get("turn")
        ev = row.get("event")
        if ev == "gain_spark":
            gained[turn] = gained.get(turn, 0) + row.get("amount", 0)
        elif ev == "spend_spark":
            spent[turn] = spent.get(turn, 0) + row.get("amount", 0)
        elif ev == "sparks_spent":
            # The retired rule's automatic consume prints no amount; it takes
            # the threshold, which is what `combat.play_card` took.
            spent[turn] = spent.get(turn, 0) + threshold

    opening: dict[int, int] = {}
    skipped: dict[int, int] = {}
    for turn, bank, sinks, played in records:
        opening.setdefault(turn, bank)
        # The LAST decision of a turn wins, and a turn only ends on a `None`.
        skipped[turn] = 0 if played else sinks

    rows = []
    for turn in sorted(set(opening) | set(gained) | set(spent)):
        avail = opening.get(turn, 0) + gained.get(turn, 0)
        rows.append({"turn": turn,
                     "opening": opening.get(turn, 0),
                     "generated": gained.get(turn, 0),
                     "spent": spent.get(turn, 0),
                     "available": avail,
                     "skipped": skipped.get(turn, 0)})
    return rows


def _arm(flag_on: bool, fights: int, seed: int) -> dict:
    from tier0.engine.combat import run_fight
    from tier0.pilot.policy import make_pilot

    _clear_caches()
    original = C.SPARK_ALT_COST_ENABLED
    C.SPARK_ALT_COST_ENABLED = flag_on
    try:
        _clear_caches()
        deck = _deck(flag_on)
        pilot = make_pilot(loader.pilot_weights(PILOT))
        stages = loader.encounter_stages(ENCOUNTER)
        fight_rows = []
        for i in range(fights):
            player = loader.build_player_from_ids("klee", list(deck))
            watched = _watched(pilot)
            state = run_fight(player, loader.build_encounter(stages[0]),
                              watched, seed=seed + i)
            turns = _fight_rows(state.log, watched.records,
                                C.SPARKS_FOR_FREE_ATTACK)
            fight_rows.append({
                "fight": i,
                "turns": turns,
                "won": bool(state.player.alive) and all(not e.alive
                                                        for e in state.enemies),
            })
        return {"deck": deck,
                "generators": _generators(deck),
                "fights": fight_rows,
                # The drafter-reachability fact, read live off the same seam
                # the drafter reads, so this header can never claim a
                # reachability the pool does not have.
                "offerable_protos": _offerable_protos()}
    finally:
        C.SPARK_ALT_COST_ENABLED = original
        _clear_caches()


def _offerable_protos() -> list[str]:
    from tier05 import rewards
    pool = rewards.character_pool("klee")
    return sorted(c.id for cards in pool.values() for c in cards
                  if c.id.startswith(loader.PROTOTYPE_ID_PREFIX))


def _totals(arm: dict) -> dict:
    t = {"turns": 0, "opening": 0, "generated": 0, "spent": 0,
         "available": 0, "skipped": 0, "wins": 0,
         "skipped_turns": 0}
    for fight in arm["fights"]:
        t["wins"] += int(fight["won"])
        for row in fight["turns"]:
            t["turns"] += 1
            for k in ("opening", "generated", "spent", "available", "skipped"):
                t[k] += row[k]
            t["skipped_turns"] += int(row["skipped"] > 0)
    return t


def _print_arm(label: str, arm: dict, per_fight: bool, per_turn: bool) -> dict:
    t = _totals(arm)
    turns = max(1, t["turns"])
    print(label)
    print(f"    generators in deck  "
          f"{', '.join(f'{cid} +{n}' for cid, n in arm['generators']) or 'NONE'}"
          f"   (printed total {sum(n for _, n in arm['generators'])})")
    print(f"    player turns        {t['turns']}")
    print(f"    Sparks available    {t['available']}  "
          f"({t['available'] / turns:.2f}/turn)"
          f"   [opening {t['opening']} + generated {t['generated']}]")
    print(f"    Sparks spent        {t['spent']}  "
          f"({t['spent'] / turns:.2f}/turn)")
    rate = t["spent"] / t["available"] if t["available"] else 0.0
    print(f"    spent / available   {rate:.3f}"
          + ("" if t["available"] else "   (undefined: nothing available)"))
    print(f"    sinks skipped       {t['skipped']}  "
          f"({t['skipped'] / turns:.2f}/turn, on {t['skipped_turns']} turn(s))")
    print(f"    fights won          {t['wins']}/{len(arm['fights'])}"
          f"   NOT A BALANCE CLAIM (R215 B)")
    if per_fight:
        print("      fight  turns  avail  spent  sp/av  skipped  won")
        for fight in arm["fights"]:
            rows = fight["turns"]
            av = sum(r["available"] for r in rows)
            sp = sum(r["spent"] for r in rows)
            sk = sum(r["skipped"] for r in rows)
            ratio = f"{sp / av:.2f}" if av else "-"
            print(f"      {fight['fight']:5d}  {len(rows):5d}  {av:5d}  "
                  f"{sp:5d}  {ratio:>5}  {sk:7d}  {int(fight['won'])}")
    if per_turn:
        print("      fight  turn  open  gen  spent  avail  sp/av  skipped")
        for fight in arm["fights"]:
            for r in fight["turns"]:
                ratio = (f"{r['spent'] / r['available']:.2f}"
                         if r["available"] else "-")
                print(f"      {fight['fight']:5d}  {r['turn']:4d}  "
                      f"{r['opening']:4d}  {r['generated']:3d}  "
                      f"{r['spent']:5d}  {r['available']:5d}  {ratio:>5}  "
                      f"{r['skipped']:7d}")
    print()
    return t


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fights", type=int, default=40)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--per-fight", action="store_true")
    ap.add_argument("--per-turn", action="store_true")
    args = ap.parse_args(argv)

    print("KLEESPARK-R2 — Spark economy on NORMALIZED metrics. "
          "NOT A REGISTRATION.")
    print(f"  encounter {ENCOUNTER}, pilot {PILOT}, "
          f"{args.fights} fight(s) per arm from seed {args.seed}")
    print("  NOT A BALANCE READ (R215 B). Counts only; Guardrail-7 applies.")
    print("  THE INCOME CONFOUND: the arms differ in their GENERATORS, not "
          "only in their sinks —")
    print("  PICK 4's map converts four Spark generators into Spark sinks, so "
          "a RAW per-turn")
    print("  spend rate compares the maps and not the economies. Read "
          "`spent / available`.")
    print(f"  ON  arm adds: {', '.join(TIGHT_SET)}")
    print(f"  OFF arm adds: {', '.join(SHIPPED_SET)}")
    print()

    totals = {}
    for label, flag in (("flag OFF (shipped rows)", False),
                        ("flag ON  (tight set)", True)):
        arm = _arm(flag, args.fights, args.seed)
        totals[flag] = _print_arm(label, arm, args.per_fight, args.per_turn)
        if flag:
            print(f"  drafter reachability under the flag: "
                  f"{len(arm['offerable_protos'])} prototype row(s) in "
                  f"`rewards.character_pool('klee')` —")
            print(f"    {', '.join(arm['offerable_protos'])}")
            print()

    off, on = totals[False], totals[True]
    off_norm = off["spent"] / off["available"] if off["available"] else 0.0
    on_norm = on["spent"] / on["available"] if on["available"] else 0.0
    off_raw = off["spent"] / off["turns"] if off["turns"] else 0.0
    on_raw = on["spent"] / on["turns"] if on["turns"] else 0.0
    print(f"NORMALIZED  spent/available {off_norm:.3f} OFF -> {on_norm:.3f} ON")
    print(f"RAW         spent/turn      {off_raw:.2f} OFF -> {on_raw:.2f} ON "
          f"(the confounded figure r1 read)")
    print(f"SKIPPED     affordable sinks skipped per turn "
          f"{off['skipped'] / max(1, off['turns']):.2f} OFF -> "
          f"{on['skipped'] / max(1, on['turns']):.2f} ON")
    return 0


if __name__ == "__main__":
    expcli.help_if_asked(__doc__)
    sys.exit(main())

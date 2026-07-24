"""Furina sheet pass 4 — pre-registered experiment battery.

Registered in docs/furina-sheet-pass-4-plan.md BEFORE running; null results
binding. Seed 20260724 throughout; deterministic.

Q1B. Fanfare saturation BASELINE (current constants, no overrides). Reports
     the registered Q1a metrics -- time-at-cap, overflow-waste, spends,
     mean held as a fraction of cap -- per archetype weighting and PER ACT,
     because the registered read ("a healthy band by act 3") cannot be
     answered by a run-level average.

     Registered divergence clause: if saturation is LOW here but was high in
     playtest, the divergence IS the finding (sim decks under-generate
     versus human piloting) and it goes to [USER] before any remedy cell is
     trusted.

R14: diagnostics feeding a ruling. No acceptance targets in this file.

Usage: python -m tier05.exp_furina_pass4 [q1b|q3] [--runs N]
"""

from __future__ import annotations

import sys

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine.combat import run_fight
from tier0.harness import axes, metrics
from tier0.pilot.policy import make_pilot
from tier05 import draft, fanfare_telemetry, model

SEED = 20260724
RUNS = 200
FIGHTS = 400
ENCOUNTERS = ("punisher", "swarm", "attrition", "tank_boss")

# Archetype weighting in RUN mode is the ASSIGNED archetype: run_many drafts
# toward it, so the deck emerges rather than being handed over. (A fixed
# "self_carry" package label would be inert here -- it would redraft the same
# fanfare deck and report the fanfare arm's numbers twice.)
# Primary read: fanfare. Salon is CO-primary this pass, because Salon v2
# member scaling reads the meter and a pinned pool flattens it. Spotlight is
# context.
CONFIGS = (
    ("fanfare", "fanfare"),
    ("salon", "salon"),
    ("spotlight", "spotlight"),
)


def _acts() -> int:
    return len(C.RUN_ACTS)


def _by_act(results: list) -> dict[int, list]:
    out: dict[int, list] = {}
    for res in results:
        for act_i, tr in res.fanfare_traces:
            out.setdefault(act_i, []).append(tr)
    return out


def q1b(runs: int = RUNS) -> None:
    print("=" * 78)
    print(f"Q1B. Fanfare saturation baseline — {runs} realistic runs/arm, "
          f"seed {SEED}")
    print(f"     constants: FANFARE_CAP_FRACTION {C.FANFARE_CAP_FRACTION}, "
          f"per-HP {C.FANFARE_PER_HP_LOST}, per-Encore-gained "
          f"{C.FANFARE_PER_ENCORE_GAINED}, per-Encore-spent "
          f"{C.FANFARE_PER_ENCORE_SPENT}, per-Spotlight-card "
          f"{C.FANFARE_PER_SPOTLIGHT_CARD}, SALON_FOCUS_PER "
          f"{C.SALON_FOCUS_PER}")
    print("=" * 78)

    for archetype, pilot_id in CONFIGS:
        results = model.run_many(
            "furina", archetype, pilot_id, draft.assigned_policy,
            runs, SEED, grant_relics=True, grant_potions=True)
        wr = sum(r.won for r in results) / len(results)
        every = [tr for r in results for _, tr in r.fanfare_traces]
        print(f"\n  assigned {archetype} (pilot {pilot_id}) "
              f"— run winrate {wr:.1%}")
        print(fanfare_telemetry.format_row("all acts",
                                           fanfare_telemetry.aggregate(every)))
        for act_i, traces in sorted(_by_act(results).items()):
            print(fanfare_telemetry.format_row(
                f"act {act_i + 1}", fanfare_telemetry.aggregate(traces)))


def _statline(deck_ids: list[str], pilot_id: str, fights: int) -> dict:
    """One battery over the registered encounters -> normalized 7-axis
    scores, against the frozen REF_IRONCLAD starter baseline."""
    pilot = make_pilot(loader.pilot_weights(pilot_id))
    ref_pilot = make_pilot(loader.pilot_weights("generic"))
    stats: dict[str, list] = {}
    ref: dict[str, list] = {}
    for enc in ENCOUNTERS:
        rows, ref_rows = [], []
        for i in range(fights):
            player = loader.build_player_from_ids("furina", deck_ids)
            state = run_fight(player, loader.build_encounter(enc), pilot,
                              seed=SEED + i)
            rows.append(metrics.extract(state, player.max_hp))
            base_player = loader.build_player("ref_ironclad", "starter")
            base_state = run_fight(base_player, loader.build_encounter(enc),
                                   ref_pilot, seed=SEED + i)
            ref_rows.append(metrics.extract(base_state, base_player.max_hp))
        stats[enc] = rows
        ref[enc] = ref_rows
    scores = axes.normalize(axes.raw_axes(stats), axes.raw_axes(ref))
    won = [s.won for rows in stats.values() for s in rows]
    scores["winrate"] = sum(won) / len(won)
    return scores


def q3(fights: int = FIGHTS) -> None:
    """Q3b/Q3c/Q3d — the Innate-on-upgrade Encore card.

    Arms are held to ONE variable: the same deck, the same seeds, with
    aria_of_recompense (a) unupgraded, (b) upgraded as the sheet rules it
    today (encore +3), (c) upgraded with `innate: true` added -- the
    proposal. The innate delta is applied as a RUNTIME override of the
    upgrade index, never a sheet edit: the sheet is a ratified artifact and
    this is a diagnostic (R14).
    """
    print("=" * 78)
    print(f"Q3. Innate-on-upgrade Encore card — {fights} fights/encounter, "
          f"seed {SEED}")
    print("=" * 78)

    print("\n  Q3a — engine check: SUPPORTED end to end, no pre-item needed.")
    print("    sim      tier0/content/upgrades.py applies {innate: true} to "
          "card.innate (only `true` is a ruling, R37);")
    print("             combat.surface_innate prepends innate cards to the "
          "shuffled draw pile at combat start.")
    print("    codegen  build_upgrade emits AddKeyword(CardKeyword.Innate) "
          "for the same delta, under the same rule.")
    print("    precedent klee-upgrades.yaml: catalytic_conversion "
          "{innate: true}. furina-upgrades.yaml has none yet.")
    print("    semantics 'top of the shuffled draw pile', not a reserved hand "
          f"slot — with {C.CARDS_DRAWN_PER_TURN} cards drawn it reaches the "
          "opening hand while fewer than that many innate cards exist.")

    base_deck = loader.starting_deck("furina")
    if "aria_of_recompense" not in base_deck:
        print("  !! aria_of_recompense is not in the starting deck; Q3b's "
              "premise (a basic, guaranteed in every deck) does not hold")
        return
    upgraded_deck = ["aria_of_recompense+" if cid == "aria_of_recompense"
                     else cid for cid in base_deck]

    index = upgrades._upgrade_index()
    original = dict(index["aria_of_recompense"])
    arms = [("base (aria unupgraded)", base_deck, None),
            ("aria+ as ruled today (encore +3)", upgraded_deck, None),
            ("aria+ WITH innate (proposal)", upgraded_deck,
             {**original, "innate": True})]

    print(f"\n  Q3c — A1 statline check ({len(ENCOUNTERS)} encounters)")
    print(f"  {'arm':<36} {'A1':>6} {'A3':>6} {'A4':>6} {'A7':>6} {'wr':>7}")
    try:
        for label, deck, override in arms:
            if override is not None:
                index["aria_of_recompense"] = override
            else:
                index["aria_of_recompense"] = original
            loader.get_card.cache_clear() if hasattr(
                loader.get_card, "cache_clear") else None
            s = _statline(deck, "fanfare", fights)
            print(f"  {label:<36} {s['A1_frontload']:>6.2f} "
                  f"{s['A3_block']:>6.2f} {s['A4_sustain']:>6.2f} "
                  f"{s['A7_setup_tax']:>6.2f} {s['winrate']:>7.1%}")
    finally:
        index["aria_of_recompense"] = original

    print("\n  Q3d — upgrade-priority interaction (read from rest_action, "
          "not measured):")
    print("    rest_action smiths an ON-PLAN card, payoffs before enablers. "
          "aria is role=enabler,")
    print("    so it is taken only once no on-plan PAYOFF is upgradable — it "
          "does not automatically")
    print("    dominate the first fire. Worth re-reading if the fanfare "
          "payoff set ever shrinks.")


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    runs = RUNS
    if "--runs" in args:
        i = args.index("--runs")
        runs = int(args[i + 1])
        del args[i:i + 2]
    block = args[0] if args else "q1b"
    if block == "q1b":
        q1b(runs)
    elif block == "q3":
        q3()
    else:
        print(f"unknown block: {block}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

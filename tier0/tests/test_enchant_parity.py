"""EB-84 — the C# enchantment leg, held as an eligibility correspondence.

The backlog row opened this as a port ("no C# enchant surface exists at
all"). It does exist: `sts2.dll` ships `EnchantmentModel`, a class for each
of the nine enchantments tier0's CATALOG names, the deck enchant screen, the
save format, and the payout hooks -- `Hook.ModifyDamage` and
`Hook.ModifyBlock` both consult `cardSource.Enchantment` before any other
modifier, so a mod card that deals its damage `.FromCard(this)` or gains its
Block with the `cardPlay` attached already collects Sharp / Corrupted /
Vigorous / Nimble with no mod code at all. LAW's standing rule (sweep the
decompiled game before building infrastructure) makes a second surface the
wrong answer, so what this module gates is the correspondence that CAN drift:
what each engine believes a card is eligible for.

These tests run everywhere -- they read committed source text, never the
game. The live half is owed as a smoke: enchant one mod card of each shape on
the deck screen and confirm the number moves.
"""

import subprocess
import sys
from pathlib import Path

from tier0.content import enchantments, loader

REPO = Path(loader.__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

import lint_enchant_parity as lep        # noqa: E402


def test_the_parity_lint_passes():
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_enchant_parity.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    # A verdict with no denominator is the confident half of a partial check
    # (the house reading of the strict-domination defect).
    # NINE since EB-83 (2026-09-02): `slither` joined the CATALOG the day
    # Wood Carvings converted and started granting it.
    assert "9 enchantments" in res.stdout, res.stdout


def test_every_shipped_enchantment_names_the_card_fact_its_game_rule_reads():
    """The vocabulary is the base game's; the mapping is what we maintain."""
    assert set(lep.GAME_RULES) == set(enchantments.CATALOG)
    for name, rule in lep.GAME_RULES.items():
        assert rule in (None, "attack", "block", "exhaust",
                        "fixed_cost"), (name, rule)
        # ...and the fact has to be one `cs_facts` can actually answer, or the
        # rule reads `False` for every card and the lint fails everywhere.
        if rule is not None:
            assert rule in lep.cs_facts(""), (name, rule)


def test_a_recorded_divergence_carries_its_reason():
    """Vacuous today on purpose -- EB-85 emptied the table -- and it stays
    here because the shape check is what a future row needs to satisfy."""
    for key, why in lep.KNOWN_DIVERGENCES.items():
        name, reason = key
        assert name in enchantments.CATALOG, key
        assert reason, key
        assert len(why.split()) >= 12, (key, why)


def test_no_enchantment_diverges_from_its_shipped_rule_any_more():
    """EB-85's own pin: the three eligibility splits the EB-84 sweep found
    are FIXED, not excused. An excuse table that quietly refills is the one
    way this batch un-does itself, so the emptiness is asserted rather than
    left to the lint's exit code."""
    assert lep.KNOWN_DIVERGENCES == {}
    assert not lep.findings()


def test_the_lint_bites_when_a_card_stops_declaring_that_it_gains_block(
        tmp_path, monkeypatch):
    """The regression that motivated the codegen half.

    `Nimble.CanEnchant` gates on `CardModel.GainsBlock`, and BaseLib's
    auto-detect only sees a BlockVar in CanonicalVars -- which a card whose
    Block row sits inside a `conditional` does not have. Three shipped cards
    are that shape. Without the explicit override the game would never offer
    them Nimble; this asserts the lint would say so rather than pass.

    THE FIXTURE IS BENNETT -- FANTASTIC VOYAGE (the Mondstadt companion
    overhaul) since 2026-10-01, when Warm-Up Act's shipped class left with the
    shipped kits. Before that it was Warm-Up Act since 2026-09-26: Prune -- Little
    Witch's Hunt, the card this used to strip, now declares a real BlockVar
    (its Klee-arm upgrade moves the Block through `{Block:diff()}`), so it is
    no longer the conditional-only shape.

    The broken fixture is built in `tmp_path`, never in the working tree: a
    test that strips a line out of a TRACKED generated card and restores it in
    a `finally` leaves that card silently wrong if pytest is killed mid-run,
    and dirties the tree the manifest-version gate reads. `_source_index` is
    the one seam needed, so it is the one thing monkeypatched -- every other
    card still resolves to its real committed source.
    """
    target = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
              / "Generated" / "ProtoMcBennettFantasticVoyage.cs")
    original = target.read_text(encoding="utf-8")
    line = "    public override bool GainsBlock => true;\n"
    assert line in original, "the fixture card no longer declares GainsBlock"

    broken = tmp_path / "ProtoMcBennettFantasticVoyage.cs"
    broken.write_text(original.replace(line, ""), encoding="utf-8")
    real = lep._source_index()
    assert "ProtoMcBennettFantasticVoyage" in real
    patched = dict(real, ProtoMcBennettFantasticVoyage=broken)
    monkeypatch.setattr(lep, "_source_index", lambda: patched)

    out = "\n".join(lep.findings())
    assert "proto_mc_bennett_fantastic_voyage" in out, out
    assert "nimble" in out, out
    # And the real committed card does NOT trip it -- the bite is the fixture's.
    monkeypatch.setattr(lep, "_source_index", lambda: real)
    assert not lep.findings()


def test_the_three_shapes_the_sweep_argued_about_now_all_agree():
    """`sim_reason` decides which splits are already-known, and after EB-85
    it has nothing to recognise: none of the three cards the sweep argued
    over is a split any more.

    Its first draft answered "block-next-turn" for every Skill, which
    swallowed exactly the finding the test above builds. That narrowness is
    the standing requirement on whoever adds the next excuse.
    """
    # The three cards the sweep argued over were shipped rows (Prune's Witch
    # Hunt, Tideline Watch, Freminet's Pressurized Floe), deleted at legacy
    # cleanup stage 6; their three SHAPES are spelled inline.
    from tier0.engine.state import Card

    def row(cid, ctype, effects):
        return Card.from_dict({"id": cid, "name": cid, "cost": 1,
                               "type": ctype, "rarity": "common",
                               "effects": effects})

    ordinary = row("probe_conditional_block", "skill", [   # conditional Block
        {"op": "conditional", "if": "enemy_has_aura",
         "then": [{"op": "block", "amount": 6}]}])
    assert enchantments.eligible(ordinary, "nimble")
    delayed = row("probe_block_next_turn", "skill", [      # next-turn only
        {"op": "block_next_turn", "amount": 8}])
    # EB-85 divergence 4: block_next_turn is not GainsBlock, in either engine.
    assert not enchantments.eligible(delayed, "nimble")
    # EB-85 divergence 1: a Block-granting Attack is eligible in both.
    attack = row("probe_attack_block", "attack", [
        {"op": "damage", "amount": 6, "target": "enemy"},
        {"op": "block", "amount": 4}])
    assert enchantments.eligible(attack, "nimble")
    for card in (ordinary, delayed, attack):
        assert lep.sim_reason("nimble", card, True) is None
        assert lep.sim_reason("nimble", card, False) is None

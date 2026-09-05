"""`EB-572`: the pilot resolves the base game's basics, so a Smith screen made
of them is a decision rather than a forced default.

THE FIND (Klee soak on `0.2.2789+proto`, soak-20260905-132107 lane 1, seed
5DWBV3ET2FJZ, decision 8). The Neow "Pomander" option opened a `card_select`
`upgrade` screen and the pilot logged `forced_default`: "the sim declined this
'upgrade' screen (no option resolves to a sim card row) and no option resolves
to a sim card row to break the tie with", index 0 taken. The two earlier soaks
on the same build resolved theirs, because their screens were mod rows.

THE CAUSE. `adapter.resolve_card` resolved a `KLEEMOD-` id and nothing else,
so every base-game card fell through to the text approximation and was dropped
by the callers that want an EXACT row. Draft 4 (R242 pick 3) made Klee's
starter four base Strikes, four base Defends and two rows of her own -- "Strike
and Defend are the base game's cards" -- so the FIRST screen of a Klee run is
made of exactly the ids the resolver could not read.

Reproduced headlessly here, both ways: the screen with the map, and the same
screen with it emptied.
"""

from __future__ import annotations

import pytest

from tier0 import constants as C
from understudy import adapter, policy_v1

STRIKE = {"id": "STRIKE_IRONCLAD", "name": "Strike", "type": "Attack",
          "cost": 1, "rarity": "basic", "description": "Deal 6 damage."}
DEFEND = {"id": "DEFEND_IRONCLAD", "name": "Defend", "type": "Skill",
          "cost": 1, "rarity": "basic", "description": "Gain 5 Block."}
JUMPY = {"id": "KLEEMOD-PROTO_KO_JUMPY_DUMPTY", "name": "Jumpy Dumpty",
         "type": "Skill", "cost": 0, "rarity": "basic",
         "description": "Place a Bomb 8."}


def _screen(cards):
    return {"state_type": "card_select",
            "card_select": {"screen_type": "upgrade", "cards": cards,
                            "can_confirm": False},
            "player": {"deck": cards, "hp": 62, "max_hp": 62}}


def test_the_basics_resolve_to_their_sheet_rows_exactly():
    for entry, sid in ((STRIKE, "strike"), (DEFEND, "defend")):
        card, approx = adapter.resolve_card(entry)
        assert card.id == sid
        # EXACT, not approximate: these are committed sheet rows at the base
        # stat line, so a caller that refuses an approximation is right to
        # take them.
        assert approx is False


def test_the_map_is_curated_and_an_unknown_base_id_is_still_approximate():
    """`STATUS_MAP`'s discipline: a base id is decompiled game data and the
    sim's row is a committed sheet row, so the only honest join is one somebody
    checked. Anything else stays loudly approximate."""
    card, approx = adapter.resolve_card(
        {"id": "SOME_BASE_CARD_NOBODY_MAPPED", "name": "Whatever",
         "description": "Deal 4 damage."})
    assert approx is True
    assert card.id == "SOME_BASE_CARD_NOBODY_MAPPED"


def test_the_starter_the_klee_arm_actually_ships_is_covered():
    """The screen the soak met is the STARTER, so the map has to cover what the
    starter is made of -- read off the constant rather than retyped."""
    base = {cid for cid in C.KLEE_OVERHAUL_STARTER_IDS
            if not cid.startswith("proto_")}
    assert base <= set(adapter.BASE_CARD_IDS.values())


def test_the_smith_screen_is_a_decision_and_not_a_forced_default():
    decision = policy_v1.decide(_screen([STRIKE, DEFEND, JUMPY]))
    assert decision.available
    assert decision.action == {"action": "select_card", "index": 0}
    assert not (decision.notes or {}).get("forced_default")
    assert "no option resolves to a sim card row" not in decision.rationale


def test_the_same_screen_with_the_map_emptied_is_the_soaks_own_line(
        monkeypatch):
    """Seen to FAIL, and this is the failure: with no base ids resolvable the
    screen produces the soak's verbatim rationale and no action at all."""
    monkeypatch.setattr(adapter, "BASE_CARD_IDS", {})
    decision = policy_v1.decide(_screen([STRIKE, DEFEND]))
    assert decision.action is None
    assert "no option resolves to a sim card row" in decision.rationale

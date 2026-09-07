"""`EB-608`: Rosaria -- Ravaging Confession's rider reads the aura BEFORE the hit.

THE FIND (Klee r23 lane 1 (c) 4). "Deal 9 damage. If the enemy has an aura,
apply 1 Vulnerable" on a Cryo hit: the hit itself consumes the aura by Melt,
so a seat that Melted with her never saw Vulnerable land and could not tell
rule from bug. The rule, in both engines, is that the clause is read before
the hit -- tier0 snapshots `target_has_aura` at card start (`effects._cond`)
and the generated C# reads `targetHadAura` before `DamageCmd.Attack` -- so
the Melt hit is exactly the hit that pays the rider. The face now says so
("If the enemy had an aura before the hit"), and this pins the order the
face states, so a face that drifts from the engine is a red test.
"""

import yaml

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat
from tier0.tests.conftest import make_state

ROW = "proto_mc_rosaria_ravaging_confession"


def _rosaria():
    return next(c for c in loader.prototype_cards() if c.id == ROW)


def test_the_face_states_the_clause_order():
    # tier0 strips `description:` at load (it renders no face), so the pin
    # reads the sheet row the C# is generated from.
    rows = yaml.safe_load(loader.PROTOTYPE_SHEET.read_text(encoding="utf-8"))
    row = next(r for r in rows if r["id"] == ROW)
    assert "before the hit" in row["description"]


def test_rosaria_into_a_pyro_aura_melts_and_still_applies_vulnerable():
    st = make_state()
    e = st.enemies[0]
    e.aura, e.aura_turns_left = "pyro", C.AURA_DURATION_TURNS
    st.player.energy = 3
    card = _rosaria()
    st.player.hand = [card]
    combat.play_card(st, card)
    # The hit Melted (the aura was consumed and the number amplified) AND
    # the rider paid: the aura it read was the one the hit consumed.
    assert e.aura is None
    assert e.hp == 50 - int(9 * C.MELT_MULT)
    assert e.powers.get("vulnerable") == 1


def test_rosaria_into_a_bare_body_applies_nothing_and_leaves_cryo():
    st = make_state()
    e = st.enemies[0]
    st.player.energy = 3
    card = _rosaria()
    st.player.hand = [card]
    combat.play_card(st, card)
    assert e.hp == 50 - 9
    assert "vulnerable" not in e.powers
    assert e.aura == "cryo"          # her own element sticks as the new aura

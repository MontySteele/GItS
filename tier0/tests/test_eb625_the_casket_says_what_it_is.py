"""`EB-625`: Shell Guard named a relic, and something had to say what it is.

[USER]'s Kokomi act-1 run of 2026-09-07 read "whenever the Tamakushi Casket
strikes" and asked what the Casket is. The answer was a keyword tip on every
face that named the relic (`ArmKeywordTips.ForCasket`), re-read by the Casket
pass (2026-09-28) when the relic began to count Plans.

THE RE-FOUNDING (2026-10-12) RETIRED THE COUNT. The relic keeps its id, name
and art and now says one plain thing: "At the end of your turn, if a Plan is
waiting, gain 3 Block." No card names it, so there is no tip to attach, and
Shell Guard, Open the Casket and the count's readers are cut
(`review/active/kokomi-design-pass-2026-10-11.md`,
`review/active/kokomi-card-paper-2026-10-12.md`). What stays pinned here is
that the retired surfaces stay gone, and the panel clause that answers a
debuff-striking relic stays silent on the relic's face.
"""

from __future__ import annotations

from pathlib import Path

from tier0 import constants as C

REPO = Path(__file__).resolve().parents[2]

TIPS_CS = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
           / "ArmKeywordTips.cs")
MOD_CS = REPO / "klee-mod" / "KleeCode" / "KleeMod.cs"
RELIC_CS = REPO / "klee-mod" / "KleeCode" / "Relics" / "TamakushiCasket.cs"


def test_the_casket_tip_and_the_token_tip_are_retired():
    from tools import gen_klee_cards as gen

    assert not any(k.word in ("Tamakushi Casket", "Open the Casket")
                   for k in gen.ARM_KEYWORDS)
    assert "ArmKeywordTips.ForCasket" not in gen.arm_keyword_tip_calls(
        "Draw 1 card. The [gold]Casket[/gold] gains 2.")
    tips = TIPS_CS.read_text(encoding="utf-8")
    assert "ForCasket" not in tips
    assert "CasketKey" not in tips
    mod = MOD_CS.read_text(encoding="utf-8")
    assert "CasketKey" not in mod and "OpenTheCasketKey" not in mod


def test_the_relic_face_is_one_sentence_off_the_shared_number():
    """The number is read, never typed: `KokomiOverhaulLaw.CasketBlock`, held
    by value against `C.KOKOMI_OVERHAUL_CASKET_BLOCK` by
    `lint_constant_parity`."""
    relic = RELIC_CS.read_text(encoding="utf-8")
    assert "Face(KokomiOverhaulLaw.CasketBlock)" in relic
    assert ('"At the end of your turn, if a [gold]Plan[/gold] is waiting, '
            'gain "') in relic
    assert "Open the Casket" not in relic[relic.index('("description",'):]
    assert C.KOKOMI_OVERHAUL_CASKET_BLOCK == 3


def test_the_debuff_answer_clause_is_silent_on_the_relic():
    """`EB-433`'s panel clause is gated by matching the relic's sentence
    rather than its name, so it reads the relic a run holds: silent on the
    re-founded face, still answering the old strike spelling."""
    from understudy import blindplay_render

    rx = blindplay_render._DEBUFF_ANSWERING_HIT
    now = (f"At the end of your turn, if a [gold]Plan[/gold] is waiting, "
           f"gain {C.KOKOMI_OVERHAUL_CASKET_BLOCK} [gold]Block[/gold].")
    before = ("Start each combat with the [gold]Bake-Kurage[/gold]. Each debuff "
              "you apply lands a real [blue]2[/blue] [gold]Hydro[/gold] hit on "
              "that enemy.")
    assert not rx.search(now)
    assert rx.search(before)

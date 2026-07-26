"""A card that enters COMBAT must be created by the COMBAT scope.

Playtest 2026-07-26, Kokomi. Honor Guard transformed a hand card into Gorou,
General's War Banner; playing it soft locked the run:

    System.InvalidOperationException: KLEEMOD-GOROU_WAR_BANNER must be added
    to a CombatState before playing it.
      at MegaCrit.Sts2.Core.Commands.CardPileCmd.AddDuringManualCardPlay
      at MegaCrit.Sts2.Core.Models.CardModel.OnPlayWrapper
      at MegaCrit.Sts2.Core.GameActions.PlayCardAction.ExecuteAction

`KokomiConscript.RollRecruit` built the recruit with
`((ICardScope)owner.RunState).CreateCard(...)`, copied from `CompanionSlot`,
where run scope is CORRECT because that recruit is a reward headed for the
deck. A conscript recruit is combat-local -- the sim's `_op_conscript`
deepcopies into `state.player.hand` and never touches the deck, the discount is
`AddThisCombat`, the Exhaust is per-instance.

Why this needs a lint rather than a fix and a note. The failure is INVISIBLE
at the door it enters:

  * create mode threw at `AddGeneratedCardToCombat` -- loud, and the earlier
    playtest logs caught it on Inuzaka Charge / Daruma Gift / Blazing Barrier
  * transform mode threw at PLAY. The transform itself succeeded, the recruit
    sat in hand rendering correctly, and the throw landed inside
    PlayCardAction, where an unresolved GameAction leaves the queue stuck.
    That is a soft lock, not a crash: no dialog, no exit, the log is the only
    witness. Nothing in the mod's own surfaces reported it.

There is no C# test project (see the co-op/backstop note in DECISIONS.md), so
this is source text asserted from the Python side -- the same shape as
test_next_attack_up_series.py's C# half, and for the same reason: the defect
lives in a compiled Godot run where the simulator has nothing to execute.

The allowlist is checked in BOTH directions. An entry that no longer names a
real run-scope call site is a stale exemption, and a stale exemption is how the
next one of these gets waved through.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MOD_SRC = ROOT / "klee-mod" / "KleeCode"

# Run-scope card creation. `RunState` is the deck's scope: a card made there
# outlives combat and is never registered with the CombatState.
RUN_SCOPE_CREATE = re.compile(r"RunState\s*\)?\s*\.\s*CreateCard\b|RunState\.CreateCard\b")

# The ONE legitimate run-scope creation in the mod, with the reason it is
# legitimate. Anything else that reaches combat with a run-scoped card is the
# 2026-07-26 soft lock again.
RUN_SCOPE_ALLOWED = {
    "CompanionSlot.cs":
        "the 4th reward option -- a reward card is picked INTO THE DECK, so "
        "run scope is its real lifetime (CardFactory.CreateForReward ends in "
        "exactly this call)",
}


def _cs_files():
    return sorted(MOD_SRC.rglob("*.cs"))


def test_run_scope_creation_is_confined_to_the_allowlist():
    offenders = []
    for path in _cs_files():
        src = path.read_text(encoding="utf-8")
        for num, line in enumerate(src.splitlines(), 1):
            if line.lstrip().startswith(("//", "///", "*")):
                continue          # prose about the bug is not the bug
            if RUN_SCOPE_CREATE.search(line) and \
                    path.name not in RUN_SCOPE_ALLOWED:
                offenders.append(f"{path.relative_to(ROOT)}:{num}: {line.strip()}")

    assert not offenders, (
        "run-scope CreateCard outside the allowlist. A card built from "
        "RunState is never registered with the CombatState, and the base game "
        "rejects it at BOTH doors -- AddGeneratedCardToCombat throws on the "
        "way into a pile, AddDuringManualCardPlay throws on play and soft "
        "locks the action queue. Use CombatState.CreateCard for anything that "
        "enters combat.\n  " + "\n  ".join(offenders))


def test_every_allowlist_entry_still_names_a_real_call_site():
    """The other direction: no stale exemptions.

    If CompanionSlot stops creating run-scoped cards, its entry must go. An
    allowlist nobody prunes is an allowlist that eventually re-permits the
    defect it was written to fence off.
    """
    for name in RUN_SCOPE_ALLOWED:
        matches = [p for p in _cs_files() if p.name == name]
        assert matches, f"allowlist names {name}, which no longer exists"
        assert any(RUN_SCOPE_CREATE.search(p.read_text(encoding="utf-8"))
                   for p in matches), (
            f"{name} is exempted from the run-scope rule but no longer "
            "creates run-scoped cards -- drop the entry")


def test_the_conscript_recruit_is_combat_scoped():
    """The specific site the playtest burned, pinned by name.

    The general lint above would also catch a regression here, but only as one
    line in a list. This test says which card verb it is and what it broke, so
    the failure message carries the playtest with it.
    """
    src = (MOD_SRC / "Powers" / "KokomiConscript.cs").read_text(
        encoding="utf-8")
    body = src[src.index("private static CardModel? RollRecruit"):]
    # Code only. The fix comment quotes the line it replaced, and the whole
    # point of keeping that quote is that the next reader sees what was wrong.
    body = "\n".join(line for line in body.splitlines()
                     if not line.lstrip().startswith(("//", "///", "*")))

    assert "CombatState" in body and ".CreateCard(pick, owner)" in body, (
        "KokomiConscript.RollRecruit must build the recruit from the "
        "CombatState. Run scope produced a card the combat had never seen: "
        "Honor Guard -> Gorou, General's War Banner transformed fine, sat in "
        "hand, and soft locked PlayCardAction on play (2026-07-26 playtest)")
    assert "RunState" not in body, (
        "RollRecruit is reaching for RunState again -- that is the exact "
        "line that soft locked the 2026-07-26 Kokomi playtest")

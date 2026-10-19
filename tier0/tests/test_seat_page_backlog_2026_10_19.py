"""SEAT PAGE BACKLOG BURN (2026-10-19), the page half.

Five rows of `docs/current/BACKLOG.md`, each a thing that happened with
nothing on the page saying so:

- Furina suite 3 lane 3: a word tip for Charlotte on a screen with no
  Charlotte card. Furina's own event prose names her guests.
- The Tamakushi Casket's Block, Sango Pearl's spent discount, Ocean-Hued
  Clam's Mend and Everlasting Moonglow's skipped return: a `relic` page
  event under "Since last page" (`ResolutionLedger.NoteRelic`).
- Orb passives and evokes: an `orb` page event (`OrbNarration`).
- A full shrine names the Sakura a plant of another kind withers.
- Bottled Gale with no aura on the board says it would do nothing.

C# half: `klee-mod/KleeTests/SeatPageBacklog20261019Tests.cs`.
"""

from __future__ import annotations

from understudy import blindplay, blindplay_notes, blindplay_render
from tier0.tests.test_varka_payoff_seat_page import _ev, _row
from tier0.tests.test_varka_seat_page import varka_state


# ---- Charlotte on an event page -------------------------------------------

LETTER = ("She is still doing Charlotte's voice under her breath. A Melusine "
          "in a Palais courier's cap is waiting on the step.")


def _event(text: str, options: list[dict] | None = None) -> dict:
    return {"screen": "event", "text": text, "dialogue": [],
            "options": options or [], "character": "Furina",
            "stage_arm": True}


def _words(obs: dict) -> set[str]:
    return {row["name"] for row in blindplay_notes.keyword_notes(obs)}


def test_a_guest_named_in_event_prose_gets_no_word_tip():
    assert "Charlotte" not in _words(_event(LETTER))


def test_an_event_option_that_summons_her_still_gets_the_tip():
    obs = _event(LETTER, [{"name": "Take the stage",
                           "text": "Summon Charlotte."}])
    assert "Charlotte" in _words(obs)


def test_the_guest_on_a_combat_screen_is_unchanged():
    obs = {"screen": "card_reward", "character": "Furina", "stage_arm": True,
           "cards": [{"title": "Guest Star: Charlotte",
                      "text": "Summon Charlotte. Act: Repay 3."}]}
    assert "Charlotte" in _words(obs)


# ---- relics and orbs under "Since last page" --------------------------------

def _page(events) -> str:
    state = varka_state()
    state["player"]["resolutions"] = [_row("Strike", hits=True,
                                           events=events)]
    return blindplay.observe(state)


def _since(page: str) -> str:
    line = next(x for x in page.splitlines()
                if x.startswith(blindplay_render.EVENTS_HEAD))
    return line[len(blindplay_render.EVENTS_HEAD):]


def test_the_casket_block_prints_and_counts_its_repeats():
    page = _page([_ev("relic", 9401, card="Tamakushi Casket",
                      power="gained 1 Block"),
                  _ev("relic", 9402, card="Tamakushi Casket",
                      power="gained 1 Block")])
    assert "Tamakushi Casket: gained 1 Block x2" in _since(page)


def test_the_kokomi_relics_each_say_what_they_did():
    page = _page([
        _ev("relic", 9411, card="Sango Pearl",
            power="refunded 2 Energy, used this combat"),
        _ev("relic", 9412, card="Ocean-Hued Clam",
            power="Mend 1, healed 1 HP"),
        _ev("relic", 9413, card="Everlasting Moonglow",
            power="your hand was full, so Ward went to your Discard Pile")])
    since = _since(page)
    assert "Sango Pearl: refunded 2 Energy, used this combat" in since
    assert "Ocean-Hued Clam: Mend 1, healed 1 HP" in since
    assert ("Everlasting Moonglow: your hand was full, so Ward went to your "
            "Discard Pile") in since


def test_an_orb_passive_and_evoke_are_narrated():
    page = _page([_ev("orb", 9421, card="Lightning", power="passive"),
                  _ev("orb", 9422, card="Lightning", power="passive"),
                  _ev("orb", 9423, card="Frost", power="evoked")])
    since = _since(page)
    assert "Lightning orb: passive x2" in since
    assert "Frost orb: evoked" in since


def test_no_wire_word_reaches_the_page():
    page = _page([_ev("relic", 9431, card="Tamakushi Casket",
                      power="gained 1 Block"),
                  _ev("orb", 9432, card="Dark", power="evoked")])
    assert "relic" not in _since(page).split(":")[0]
    assert " orb\n" not in page


# ---- the full shrine names the Sakura a plant reaches -----------------------

def _sakura(slot, kind="thunder", turns=2, anns=()):
    return {"slot": slot, "level": 1, "kind": kind, "planted": 1,
            "strike": 3, "turns": turns, "annotations": list(anns),
            "annotation": anns[0] if anns else None}


def test_a_full_shrine_names_the_fewest_turns_left_oldest_first():
    rows = [_sakura(1, turns=2), _sakura(2, "kitsune", turns=1),
            _sakura(3, "foxfire", turns=1)]
    lines = blindplay_render._render_shrine({"sakura": rows, "cap": 3})
    assert ("- Next to act on a plant: Sakura 2 (Kitsune Sakura). A plant "
            "of another kind withers it.") in lines


def test_deadline_extension_goes_last():
    rows = [_sakura(1, turns=1, anns=("Deadline Extension",)),
            _sakura(2, turns=3)]
    assert blindplay_render.next_to_wither(rows)["slot"] == 2
    # Every one carries it: the fewest turns again.
    rows = [_sakura(1, turns=3, anns=("Deadline Extension",)),
            _sakura(2, turns=2, anns=("Red Ink", "Deadline Extension"))]
    assert blindplay_render.next_to_wither(rows)["slot"] == 2


def test_a_shrine_with_room_or_no_turns_names_none():
    rows = [_sakura(1), _sakura(2)]
    lines = blindplay_render._render_shrine({"sakura": rows, "cap": 3})
    assert not any(x.startswith("- Next to act") for x in lines)
    assert blindplay_render.next_to_wither([_sakura(1, turns=None)]) is None


# ---- Bottled Gale on a bare board -------------------------------------------

def _gale(auras) -> str:
    state = varka_state(auras=auras)
    state["player"]["potions"] = [
        {"id": "KLEEMOD-BOTTLED_GALE", "name": "Bottled Gale",
         "description": "Swirl every aura.", "keywords": []}]
    return blindplay.observe(state)


def test_bottled_gale_warns_on_a_board_with_no_aura():
    page = _gale((None, None))
    assert ("**Bottled Gale** — Swirl every aura."
            + blindplay_render.POTION_NO_AURA) in page


def test_bottled_gale_is_quiet_when_an_enemy_wears_one():
    from tier0.tests.test_varka_seat_page import FRESH_PYRO
    page = _gale(((FRESH_PYRO, "Pyro"), None))
    assert blindplay_render.POTION_NO_AURA not in page
    assert "**Bottled Gale** — Swirl every aura." in page


# ---- Claque's Ledger in the stage log ---------------------------------------

def test_claques_ledger_gain_is_its_own_stage_log_line():
    """The mod files the gain as its own beat, sourced
    (`StageDirector.Claque`); the wire's beat reaches the page as a line."""
    from understudy.blindplay_board import furina_stage as stage_block
    stage = stage_block({"furina_stage": {
        "live": True,
        "seats": [{"member": "wriothesley", "name": "Wriothesley",
                   "seat": 0}],
        "log": [{"event": "act", "member": "wriothesley", "seat": 0,
                 "fanfare": 3, "moved": 5},
                {"event": "gain", "member": "", "seat": -1, "fanfare": 4,
                 "moved": 1, "source": "Claque's Ledger"}]}})
    lines = blindplay_render._render_stage_log(stage)
    assert "  - You gained 1 Fanfare from Claque's Ledger: 3 → 4." in lines


def test_a_beat_no_performer_made_names_nobody():
    """The Charlotte word tip's other road (Furina suite 3, lane 3): an older
    mod's gain, spend, Drain, Repay and hit beats carried the enum's default
    performer, Charlotte, and her name raised her glossary row."""
    from understudy.blindplay_board import furina_stage as stage_block
    stage = stage_block({"furina_stage": {
        "live": True, "seats": [],
        "log": [{"event": event, "member": "charlotte", "name": "Charlotte",
                 "seat": -1, "fanfare": 2, "moved": 1}
                for event in ("gain", "spend", "drain", "repay", "hit")]}})
    assert all(row["name"] == "" and row["member"] == ""
               for row in stage["log"])
    obs = {"screen": "combat", "character": "Furina", "stage_arm": True,
           "combat": {"stage": stage}}
    assert "Charlotte" not in _words(obs)
    # A seated beat still names its performer.
    seated = stage_block({"furina_stage": {
        "live": True, "seats": [],
        "log": [{"event": "act", "member": "charlotte", "name": "Charlotte",
                 "seat": 0, "fanfare": 2, "moved": 3}]}})
    assert seated["log"][0]["name"] == "Charlotte"

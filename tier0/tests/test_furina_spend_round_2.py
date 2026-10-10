"""THE SPEND ROUND 2'S "CLAUDE SHIPS" CHANGES, sim and page side (2026-10-10).

`review/records/furina-spend-round-2-2026-10-10.md`, "What changes (Claude
ships)": High Stakes reads the HP drained this combat (gross, no Repay
lowers it); Gentle Current Repays on play with its Block floor; Charlotte's
line counts only a card's Repay; a Drain line of 0 explains itself on the
seat page; and the telemetry report reads the new keys (`past_lost`,
`high_stakes_bonus`, `block_card_turns`, `block_card_turns_no_block`). The
C# twin is `klee-mod/KleeTests/Prototype/FurinaSpendRound2Tests.cs`.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from tier0.content import loader
from tier0.engine import combat, furina_stage as FS, furina_tide as T
from tier0.tests.conftest import make_enemy, make_state
from tools import telemetry_report
from understudy import blindplay_board, blindplay_render

REPO = Path(__file__).resolve().parents[2]
GENERATED = REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "Generated"
PROTO = REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"


def _card(cid):
    return copy.deepcopy(loader.get_card(cid))


def _furina(hp=78, max_hp=78):
    st = make_state(enemies=[make_enemy(hp=300)], hp=max_hp)
    st.player.character_id = "furina"
    st.player.hp = hp
    st.in_player_turn = True
    st.turn = 1
    FS.reset_for_combat(st.player)
    st.player.energy = 9
    return st


def _play(st, card):
    st.player.hand.append(card)
    combat.play_card(st, card)


def _sheet_row(cid: str) -> dict:
    import yaml
    rows = yaml.safe_load((REPO / "docs" / "prototype-surface.yaml")
                          .read_text(encoding="utf-8"))
    rows = rows if isinstance(rows, list) else rows.get("cards", [])
    return next(r for r in rows if r.get("id") == cid)


# ---- 1. High Stakes reads a running total --------------------------------------

def test_high_stakes_face_says_drained_this_combat():
    row = _sheet_row("proto_fs_high_stakes")
    assert row["description"] == (
        "Your Attacks deal 1 additional damage for every 4 HP you have "
        "[gold]Drained[/gold] this combat.")
    src = (GENERATED / "ProtoFsHighStakes.cs").read_text(encoding="utf-8")
    assert "this combat." in src and "Repaid" not in src


def test_the_drained_count_is_gross_and_repay_never_lowers_it():
    st = _furina()
    FS.drain(st, 8)
    assert st.player.ftd.drained_this_combat == 8
    FS.repay(st, 5)
    assert st.player.ftd.drained == 3
    assert st.player.ftd.drained_this_combat == 8
    FS.drain(st, 3)
    assert st.player.ftd.drained_this_combat == 11


def test_high_stakes_keeps_its_bonus_through_a_repay():
    st = _furina()
    _play(st, _card("proto_fs_high_stakes"))
    FS.drain(st, 10)
    assert FS.high_stakes_bonus(st) == 2         # 10 // 4
    FS.repay(st, 10)
    assert st.player.ftd.drained == 0
    assert FS.high_stakes_bonus(st) == 2         # still 10 // 4
    _play(st, _card("proto_fs_high_stakes+"))
    assert FS.high_stakes_bonus(st) == 2 + 3     # 10 // 4 + 10 // 3


def test_the_end_of_turn_singer_no_longer_eats_the_bonus():
    """The record's diagnosis: net Drained sat near 0 because Salon
    Solitaire Repays every turn."""
    st = _furina()
    _play(st, _card("proto_fs_high_stakes"))
    FS.drain(st, 5)
    T.end_of_turn(st)                            # the Singer Repays 1
    assert st.player.ftd.drained == 4
    assert FS.high_stakes_bonus(st) == 1


# ---- 2. Gentle Current Repays now --------------------------------------------------

def test_gentle_current_is_hymns_shape_with_smaller_numbers():
    assert _sheet_row("proto_fs_gentle_current")["description"] == (
        "Gain 5 [gold]Block[/gold]. [gold]Repay[/gold] 3. Gain 1 "
        "[gold]Block[/gold] for any HP it could not [gold]Repay[/gold].")
    row = loader.get_card("proto_fs_gentle_current")
    assert row.effects == [{"op": "block", "amount": 5},
                           {"op": "stage_repay", "amount": 3,
                            "floor": "block"}]
    up = loader.get_card("proto_fs_gentle_current+")
    assert up.effects[0]["amount"] == 7 and up.effects[1]["amount"] == 4
    assert (row.cost, row.rarity, row.type) == (1, "common", "skill")


def test_gentle_current_repays_on_play_and_floors_the_rest():
    st = _furina()
    FS.drain(st, 2)
    st.player.block = 0
    _play(st, _card("proto_fs_gentle_current"))
    assert st.player.ftd.drained == 0
    assert st.player.block == 5 + 1              # 3 - 2 could not Repay
    st.player.block = 0
    T.turn_start(st)
    assert st.player.block == 0                  # nothing owed next turn


def test_the_next_turn_repay_is_gone_everywhere():
    assert "repay_next" not in FS.KINDS
    assert not hasattr(T.Ftd(), "repay_next")
    assert T.CARDS["ftd_gentle_current"].kind == "block_repay"
    assert T.CARDS["ftd_gentle_current"].n == (5, 3)
    for path in PROTO.glob("*.cs"):
        assert "RepayNextTurn" not in path.read_text(encoding="utf-8"), path
    src = (GENERATED / "ProtoFsGentleCurrent.cs").read_text(encoding="utf-8")
    assert "FurinaStageFacePreview.PayBlock" in src
    assert 'DynamicVars["RepayAmount"].IntValue, StageFloor.Block)' in src


# ---- 3. Charlotte's line reads a card's Repay ------------------------------------

def _charlotte(drained=8):
    st = _furina()
    st.player.ftd.stage = ["charlotte"]
    FS.drain(st, drained)
    st.player.draw_pile = [_card("strike") for _ in range(5)]
    return st


def test_charlottes_line_draws_on_a_cards_repay():
    st = _charlotte()
    _play(st, _card("proto_fs_soothing_waters"))
    assert st.player.ftd.charlotte_drew
    assert st.player.ftd.ledger["lines"]["charlotte"] == 1
    assert not st.player.ftd.in_card             # the play closed


def test_charlottes_line_ignores_her_act_and_salon_solitaire():
    st = _charlotte()
    T.end_of_turn(st)                            # her act, then the Singer
    assert st.player.ftd.drained == 8 - 2 - 1
    assert not st.player.ftd.charlotte_drew
    T.turn_start(st)
    assert not st.player.ftd.charlotte_drew


def test_inside_a_card_play_her_act_and_a_power_do_not_count():
    st = _charlotte(drained=12)
    st.player.ftd.in_card = True                 # a card is resolving
    T.act(st, "charlotte")                       # Encore!'s act
    assert not st.player.ftd.charlotte_drew
    with T.caused_by(st):                        # Grand Entrance
        T.repay_floor(st, 2, "block")
    assert not st.player.ftd.charlotte_drew
    T.repay(st, 1)                               # the card's own Repay
    assert st.player.ftd.charlotte_drew
    assert st.player.ftd.caused == 0


def test_grand_entrance_in_a_guest_star_play_is_not_a_cards_repay():
    st = _charlotte()
    st.player.powers[FS.GRAND_ENTRANCE] = 4
    _play(st, _card("proto_fs_guest_star_wriothesley"))
    assert st.player.ftd.drained == 8 - 4
    assert not st.player.ftd.charlotte_drew


def test_the_seat_glossary_says_one_of_your_cards():
    from understudy import blindplay_notes
    assert blindplay_notes.ARM_KEYWORDS["Charlotte"].startswith(
        "The first time one of your cards Repays each turn, draw 1 card.")


# ---- 4. A Drain line of 0 explains itself -------------------------------------------

def _drain_line(**extra) -> str:
    raw = {"live": True, "fanfare": 4, "drained": 6, "drain_line": 0,
           "drain_line_why": "the HP you started this fight with, minus 1/4 "
                             "of your Max HP",
           "entry_hp": 19, "entry_max_hp": 78, "seats": [], "log": []}
    raw.update(extra)
    stage = blindplay_board.furina_stage({"furina_stage": raw})
    lines = blindplay_render._render_stage(
        stage, {"block": 0, "hp": 13, "max_hp": 78})
    return next(ln for ln in lines if ln.startswith("- Drained "))


def test_a_line_of_zero_says_all_your_drain_returns():
    line = _drain_line()
    assert line == (
        "- Drained 6 HP. Drain line 0 HP (the HP you started this fight "
        "with, minus 1/4 of your Max HP): all your Drain returns after "
        "combat.")
    assert "lost unless" not in line
    # Any other line reads as before.
    other = _drain_line(drain_line=12)
    assert "lost unless you Repay" in other


def test_the_page_words_match_the_mods():
    law = (PROTO / "FurinaStageLaw.cs").read_text(encoding="utf-8")
    assert '"all your Drain returns after combat"' in law
    assert ("all your Drain returns after combat."
            in blindplay_render.STAGE_DRAIN_LINE_ZERO)


# ---- 5. Hygiene ----------------------------------------------------------------------

def test_the_salon_solitaire_comment_says_one_and_two():
    src = (PROTO / "FurinaStage.cs").read_text(encoding="utf-8")
    src = src.replace("\r\n", "\n")
    assert 'At the end of your turn, Repay\n///      1." (Upgraded: 2.' in src
    assert FS.SINGER_REPAY == 1


# ---- 6. The telemetry report --------------------------------------------------------

def _row(**extra) -> dict:
    row = {"record": "fight", "character": "Furina", "act": 1,
           "kind": "monster", "turns": 4, "hp_start": 60, "hp_end": 40,
           "hp_lost": 20, "max_hp": 80, "damage_dealt": 40, "seats": 1,
           "outcome": "won"}
    row.update(extra)
    return row


def test_the_report_reads_past_lost_and_high_stakes():
    rows = [_row(fanfare_peak=9, fanfare_end=3, fanfare_spends=[],
                 past_lost=6, high_stakes_bonus=12),
            _row(fanfare_peak=9, fanfare_end=3, fanfare_spends=[],
                 past_lost=0, high_stakes_bonus=0),
            _row()]
    s = telemetry_report.fanfare_summary("Furina", rows)
    assert s["fights_with_past_lost"] == 2
    assert s["past_lost"] == 3 and s["past_lost_total"] == 6
    assert s["high_stakes_total"] == 12 and s["high_stakes_fights"] == 1
    assert any(ln.startswith("Furina")
               for ln in telemetry_report.render_fanfare([s]))
    bare = telemetry_report.fanfare_summary("Furina", [_row()])
    assert bare["past_lost"] is None and bare["high_stakes_total"] is None


def test_the_report_reads_the_block_card_turns():
    rows = [_row(block_card_turns=4, block_card_turns_no_block=1),
            _row(character="Ironclad", block_card_turns=2,
                 block_card_turns_no_block=0),
            _row()]
    s = telemetry_report.block_gap_summary("all", rows)
    assert s["fights_with_keys"] == 2
    assert s["block_card_turns"] == 6 and s["no_block"] == 1
    assert abs(s["no_block_share"] - 1 / 6) < 1e-9
    assert s["fights_with_a_bare_turn"] == 1
    assert telemetry_report.block_gap_summary("x", [_row()])[
        "no_block_share"] is None


def test_the_report_cli_takes_block_gap(tmp_path, capsys):
    path = tmp_path / "play-1.jsonl"
    path.write_text(json.dumps(_row(block_card_turns=3,
                                    block_card_turns_no_block=2,
                                    ts=1.0)) + "\n", encoding="utf-8")
    assert telemetry_report.main(["--dir", str(tmp_path), "--block-gap",
                                  "--character", "Furina"]) == 0
    out = capsys.readouterr().out
    assert "BLOCK GAP" in out and "67%" in out


def test_the_schema_names_the_new_keys():
    readme = (REPO / "understudy" / "README.md").read_text(encoding="utf-8")
    for key in ("past_lost", "high_stakes_bonus", "block_card_turns",
                "block_card_turns_no_block", "(Thunderous Applause)"):
        assert key in readme, key

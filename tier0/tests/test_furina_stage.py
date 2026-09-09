"""FURINA, THE STAGE -- the sim engine's pins (`EB-724`).

The design is `review/active/furina-stage-brief-2026-09-08.md`, ruled R269. Its
sec.3 is the eleven rules and its sec.7 is the fight-one script this file
REPLAYS at the brief's own numbers, which is the acceptance the row asks for:
a brief that prints a turn-by-turn table and an engine that plays it are only
the same thing if something checks.

WHAT IS PINNED, in the order the rules are numbered:

  * the arm is OFF and the engine is byte-for-byte the shipped engine (first,
    because every other pin here is worthless without it);
  * the relic opens the stage at 3 and the lead regenerates from turn TWO;
  * a summon fills the back-most empty seat at 1, does NOT act on arrival
    (`EB-738`), and rotates the front out WITH ITS BAR on a full stage;
  * the damage order, per attack, and that it never runs on to the middle seat;
  * Spend fires in full off a short bar and the payer bows; a hit earns none;
  * the acts, the bows, and that Furina's own HP is touched by nothing;
  * the fight-one script, line A then the damage line on turn 3.

NOTHING MEASURED ON A PROTOTYPE IS QUOTABLE (R215 B): these are shape
assertions about an engine, not numbers about a game.
"""

import random

import pytest

from tier0.content import loader
from tier0.engine import combat, effects, furina_stage
from tier0.engine.state import Card, CombatState, Enemy, Player

FS = furina_stage


@pytest.fixture
def arm(monkeypatch):
    """ONE flag and no legs. The Stage is one rule set: a build that could run
    the damage order without the acts, or the acts without the bars, is a game
    no packet describes and no seat could be asked to grade."""
    monkeypatch.setattr(FS, "FURINA_STAGE", True)


def _furina(hp=200, max_hp=200, **kw):
    """A Furina with room to be hit. `fanfare_cap` is the marker the engine's
    shipped Furina telemetry gates on, kept here so this fixture is the same
    player the rest of the Furina suite builds -- the arm adds `stage` and
    takes nothing away."""
    return Player(hp=hp, max_hp=max_hp, fanfare_cap=99,
                  character_id="furina", **kw)


def _enemy(hp=99, intents=None, name="paper"):
    return Enemy(hp=hp, max_hp=hp, name=name,
                 intents=intents or [{"kind": "block", "amount": 0}])


def _state(player=None, enemies=None, turn=1, seed=0):
    st = CombatState(player=player or _furina(),
                     enemies=enemies or [_enemy()],
                     rng=random.Random(seed))
    st.turn = turn
    return st


def _sheet_rows(name):
    """One committed sheet's rows, read straight off disk."""
    import yaml
    rows = yaml.safe_load(
        (loader.DOCS_DIR / name).read_text(encoding="utf-8"))
    return rows["cards"] if isinstance(rows, dict) else rows


def _proto_rows():
    """Batch one, off the prototype surface."""
    return [r for r in _sheet_rows("prototype-surface.yaml")
            if r["id"].startswith("proto_fs_")]


def _card(cid="probe", type="skill", **kw):
    return Card(id=cid, name=cid, cost=1, type=type, rarity="common", **kw)


# ---------------------------------------------------------------------------
# 0. THE FLAG OFF. First, because it is the acceptance condition the whole
#    quarantine rests on.
# ---------------------------------------------------------------------------

def test_with_the_flag_off_the_stage_is_empty_and_every_verb_is_inert():
    st = _state()
    FS.open_combat(st)
    FS.summon(st, "usher")
    FS.raise_fanfare(st, 5)
    assert FS.stage(st.player) == []
    assert FS.lead(st.player) is None
    assert FS.can_spend(st.player) is False
    assert FS.spend(st, 3) == 0
    assert FS.absorb(st, 10) == 0
    assert FS.collect_all(st) == 0
    assert FS.final_bow(st) == 0
    assert st.log == []


def test_with_the_flag_off_no_other_character_grows_a_stage(monkeypatch):
    """CHARACTER-SCOPED, and checked with the flag ON: the Stage is one
    character's kit and a roster-wide branch would be a different change."""
    monkeypatch.setattr(FS, "FURINA_STAGE", True)
    st = _state(player=Player(hp=100, max_hp=100, character_id="klee"))
    FS.open_combat(st)
    FS.summon(st, "usher")
    assert FS.stage(st.player) == []


def test_the_arm_names_the_three_the_brief_names():
    assert FS.PERFORMERS == ("usher", "chevalmarin", "crabaletta")
    assert FS.SEATS == 3


# ---------------------------------------------------------------------------
# 1-4. THE SEATS, THE RELIC, THE SUMMON AND THE REGEN.
# ---------------------------------------------------------------------------

def test_the_relic_opens_the_front_seat_at_three_on_turn_one(arm):
    st = _state(turn=1)
    FS.open_combat(st)
    assert FS.stage(st.player) == [["usher", 3]]


def test_the_relic_fields_nobody_twice(arm):
    st = _state(turn=1)
    FS.open_combat(st)
    FS.open_combat(st)
    st.turn = 2
    FS.open_combat(st)
    assert FS.stage(st.player) == [["usher", 3]]


def test_the_first_hand_sees_three_and_the_second_turn_sees_four(arm):
    """Rule 4 as sec.3 rule 2 qualifies it: regen begins on her SECOND turn,
    so the opening hand is played against the 3 the relic granted."""
    st = _state(turn=1)
    FS.open_combat(st)
    FS.turn_start_regen(st)
    assert FS.lead_fanfare(st.player) == 3
    st.turn = 2
    FS.turn_start_regen(st)
    assert FS.lead_fanfare(st.player) == 4


def test_only_the_lead_regenerates(arm):
    st = _state(turn=2)
    st.player.stage = [["usher", 5], ["crabaletta", 1]]
    FS.turn_start_regen(st)
    assert st.player.stage == [["usher", 6], ["crabaletta", 1]]


def test_a_summon_fills_the_back_most_empty_seat_at_one(arm):
    st = _state()
    st.player.stage = [["usher", 5]]
    FS.summon(st, "crabaletta")
    assert [m for m, _f in st.player.stage] == ["usher", "crabaletta"]
    assert st.player.stage[-1][1] == FS.SUMMON_FANFARE


def test_a_newcomer_does_not_act_on_arrival(arm):
    """Sec.3 rule 3 as round one reworded it (`EB-738`, packet sec.5): "A
    newcomer performs with the others at the end of that turn, never on
    arrival." Summoning Usher changes no number on the board; the sweep is
    what pays his 3 Block, and it pays it once."""
    st = _state()
    before = st.player.block
    FS.summon(st, "usher")
    assert st.player.block == before
    assert not [e for e in st.log if e["event"] == "stage_act"]
    FS.end_of_turn_acts(st)
    assert st.player.block == before + FS.ACT_USHER_BLOCK


def test_a_summon_changes_no_enemy_number_on_play(arm):
    """`EB-738`'s acceptance, on the performer whose act is damage: three round-
    one seats watched every summon deal damage and apply Hydro with nothing on
    its face."""
    st = _state(enemies=[_enemy(hp=40)])
    FS.summon(st, "crabaletta")
    assert st.enemies[0].hp == 40
    assert st.enemies[0].aura is None


def test_a_full_stage_rotates_and_the_newcomer_inherits_the_leavers_bar(arm):
    """Rule 3: the front leaves WITHOUT A BOW, the other two step forward, and
    the newcomer takes the back seat with the leaver's Fanfare. "Pools are
    never lost to rotation"."""
    st = _state()
    st.player.stage = [["usher", 7], ["chevalmarin", 2], ["crabaletta", 1]]
    before = st.player.block
    FS.summon(st, "usher")
    assert [m for m, _f in st.player.stage] == [
        "chevalmarin", "crabaletta", "usher"]
    assert st.player.stage[-1][1] == 7          # the leaver's bar, carried
    assert sum(f for _m, f in st.player.stage) == 10   # nothing lost
    # No bow, and no arrival act either (`EB-738`): nothing lands on her Block
    # at all. The departing Usher's 4 is unearned (rule 7) and his
    # replacement's 3 waits for the end-of-turn sweep.
    assert st.player.block == before
    assert not [e for e in st.log if e["event"] == "stage_bow"]


def test_an_unknown_performer_is_a_loud_error(arm):
    st = _state()
    with pytest.raises(ValueError):
        FS.summon(st, "wriothesley")


# ---------------------------------------------------------------------------
# 5. RAISE.
# ---------------------------------------------------------------------------

def test_a_raise_lands_on_the_back_most_performer(arm):
    st = _state()
    st.player.stage = [["usher", 5], ["crabaletta", 1]]
    assert FS.raise_fanfare(st, 5) == 5
    assert st.player.stage == [["usher", 5], ["crabaletta", 6]]


def test_with_one_performer_the_back_seat_is_the_lead(arm):
    st = _state()
    st.player.stage = [["usher", 3]]
    FS.raise_fanfare(st, 5)
    assert st.player.stage == [["usher", 8]]


def test_a_raise_onto_an_empty_stage_says_so_rather_than_going_silent(arm):
    st = _state()
    assert FS.raise_fanfare(st, 5) == 0
    assert [e for e in st.log if e["event"] == "stage_raise_whiffed"]


# ---------------------------------------------------------------------------
# 6-7. THE DAMAGE ORDER.
# ---------------------------------------------------------------------------

def test_the_lead_absorbs_up_to_its_bar_and_the_rest_reaches_furina(arm):
    """Rule 6's big single hit: it rips through the lead and lands on her."""
    st = _state()
    st.player.stage = [["usher", 3], ["crabaletta", 9]]
    assert FS.absorb(st, 12) == 3
    # The lead emptied by a HIT just leaves (rule 7) -- no bow, no Block.
    assert [m for m, _f in st.player.stage] == ["crabaletta"]
    assert st.player.block == 0


def test_the_absorption_never_runs_on_to_the_middle_seat(arm):
    st = _state()
    st.player.stage = [["usher", 3], ["crabaletta", 9]]
    FS.absorb(st, 12)
    assert st.player.stage == [["crabaletta", 9]]


def test_a_flurry_kills_the_lead_and_leaves_furina_untouched(arm):
    """The other half of rule 6, and the reason the call site is per HIT: three
    hits of 2 into a lead at 3 and a reserve at 9 spend the lead and then the
    reserve, and none of it reaches her.

    THE THIRD HIT IS THE POINT. The first two empty Usher (2, then the 1 he has
    left), he leaves, and the seat behind him is the lead when the third
    arrives -- which is the difference rule 6 draws between a flurry and a big
    single hit, and it can only be true because the call site is per HIT."""
    st = _state()
    st.player.stage = [["usher", 3], ["crabaletta", 9]]
    through = sum(FS.absorb(st, 2) for _ in range(3))
    assert through == 5          # 2 + Usher's last 1 + 2 off the newcomer
    assert st.player.stage == [["crabaletta", 7]]


def test_a_hit_earns_no_bow(arm):
    st = _state()
    st.player.stage = [["usher", 2]]
    FS.absorb(st, 2)
    assert st.player.stage == []
    assert st.player.block == 0
    assert not [e for e in st.log if e["event"] == "stage_bow"]


def test_the_hit_loop_spends_block_then_the_lead_then_her(arm):
    """The wiring, at the real call site: `combat._enemy_action`'s per-hit
    loop, which is where rule 6's order is actually kept."""
    player = _furina(hp=78, max_hp=78, block=9)
    player.stage = [["usher", 3]]
    st = _state(player=player,
                enemies=[_enemy(hp=44, name="nibbit",
                                intents=[{"kind": "attack", "amount": 12}])])
    combat._enemy_turn(st, st.enemies[0])
    assert player.block == 0        # 9 of the 12 ate the Block
    assert player.stage == []       # the remaining 3 emptied Usher
    assert player.hp == 78          # and nothing reached her


# ---------------------------------------------------------------------------
# 8-9. SPEND AND THE BOW.
# ---------------------------------------------------------------------------

def test_a_spend_pays_from_the_lead(arm):
    st = _state()
    st.player.stage = [["usher", 8], ["crabaletta", 4]]
    assert FS.spend(st, 3) == 3
    assert st.player.stage == [["usher", 5], ["crabaletta", 4]]


def test_a_short_bar_pays_what_it_has_and_leaves_with_a_bow(arm):
    """Sec.10 default 4, [USER]'s own words: the rider still fires in full."""
    st = _state()
    st.player.stage = [["usher", 1]]
    assert FS.spend(st, 3) == 1
    assert st.player.stage == []
    assert st.player.block == FS.BOW_USHER_BLOCK


def test_a_performer_at_one_is_the_cheapest_spend_there_is(arm):
    """Sec.4, stated as a comparison because that is what the Expend deck is:
    the same rider costs one point off a bar of 1 and three off a bar of 8, and
    the small bar earns a bow the large one does not."""
    small = _state()
    small.player.stage = [["usher", 1]]
    large = _state()
    large.player.stage = [["usher", 8]]
    assert FS.spend(small, 3) == 1
    assert FS.spend(large, 3) == 3
    assert small.player.block == FS.BOW_USHER_BLOCK
    assert large.player.block == 0


def test_with_no_performer_the_rider_cannot_fire(arm):
    st = _state()
    assert FS.can_spend(st.player) is False
    assert FS.spend(st, 3) == 0


def test_each_bow_is_the_briefs_own(arm):
    usher = _state()
    usher.player.stage = [["usher", 1]]
    FS.spend(usher, 1)
    assert usher.player.block == FS.BOW_USHER_BLOCK

    crab = _state(enemies=[_enemy(hp=40)])
    crab.player.stage = [["crabaletta", 1]]
    FS.spend(crab, 1)
    assert crab.enemies[0].hp == 40 - FS.BOW_CRABALETTA_DAMAGE

    chev = _state(enemies=[_enemy(hp=40), _enemy(hp=40, name="paper2")])
    chev.player.stage = [["chevalmarin", 1]]
    FS.spend(chev, 1)
    assert all(e.aura == "hydro" for e in chev.enemies)
    assert all(e.hp == 40 for e in chev.enemies)   # the bow carries no damage


def test_final_bow_takes_the_bar_and_the_bow(arm):
    st = _state()
    st.player.stage = [["usher", 6]]
    assert FS.final_bow(st) == 6
    assert st.player.stage == []
    assert st.player.block == FS.BOW_USHER_BLOCK


def test_the_rare_spends_the_whole_stage_bows_and_returns_it_at_one(arm):
    st = _state(enemies=[_enemy(hp=60)])
    st.player.stage = [["usher", 5], ["chevalmarin", 3], ["crabaletta", 2]]
    assert FS.collect_all(st) == 10
    assert st.player.stage == []
    FS.bow_and_return(st)
    assert st.player.stage == [["usher", 1], ["chevalmarin", 1],
                               ["crabaletta", 1]]
    assert st.player.block == FS.BOW_USHER_BLOCK
    assert st.enemies[0].hp == 60 - FS.BOW_CRABALETTA_DAMAGE


def test_the_rare_is_worth_nothing_on_an_empty_stage(arm):
    st = _state()
    assert FS.collect_all(st) == 0
    FS.bow_and_return(st)
    assert st.player.stage == []


# ---------------------------------------------------------------------------
# 10-11. THE ACTS, AND HER OWN BAR.
# ---------------------------------------------------------------------------

def test_every_performer_acts_at_the_end_of_her_turn_from_any_seat(arm):
    st = _state(enemies=[_enemy(hp=60)])
    st.player.stage = [["crabaletta", 1], ["usher", 1], ["chevalmarin", 1]]
    FS.end_of_turn_acts(st)
    assert st.player.block == FS.ACT_USHER_BLOCK
    assert st.enemies[0].hp == (60 - FS.ACT_CRABALETTA_DAMAGE
                                - FS.ACT_CHEVALMARIN_DAMAGE)
    assert st.enemies[0].aura == "hydro"


def test_an_act_does_not_read_the_bar(arm):
    """Rule 10: flat. "Scaling on Fanfare lives in payoff cards, never in the
    performer"."""
    thin = _state()
    thin.player.stage = [["usher", 1]]
    fat = _state()
    fat.player.stage = [["usher", 40]]
    FS.end_of_turn_acts(thin)
    FS.end_of_turn_acts(fat)
    assert thin.player.block == fat.player.block == FS.ACT_USHER_BLOCK


def test_bis_performs_the_lead_and_nobody_else(arm):
    st = _state(enemies=[_enemy(hp=60)])
    st.player.stage = [["usher", 3], ["crabaletta", 3]]
    FS.perform_lead(st)
    assert st.player.block == FS.ACT_USHER_BLOCK
    assert st.enemies[0].hp == 60


def test_rotation_moves_the_front_to_the_back_with_its_bar_and_no_bow(arm):
    st = _state()
    st.player.stage = [["usher", 7], ["crabaletta", 1]]
    FS.rotate(st)
    assert st.player.stage == [["crabaletta", 1], ["usher", 7]]
    assert st.player.block == 0


def test_nothing_in_the_kit_touches_her_own_bar(arm):
    """Rule 11, swept over every verb rather than sampled: her HP is the one
    number the Stage may not move, and the whole promise of the kit
    ("her sustain is the cast") rests on it."""
    st = _state(enemies=[_enemy(hp=60)])
    FS.open_combat(st)
    FS.summon(st, "crabaletta")
    FS.raise_fanfare(st, 5)
    FS.turn_start_regen(st)
    FS.spend(st, 99)
    FS.rotate(st)
    FS.end_of_turn_acts(st)
    FS.collect_all(st)
    FS.bow_and_return(st)
    FS.final_bow(st)
    assert st.player.hp == st.player.max_hp


# ---------------------------------------------------------------------------
# THE OPS, as the seventeen faces spell them.
# ---------------------------------------------------------------------------

#: `EB-746`. THE SPEND FACE, as every Spend row on the surface is now written:
#: a `choose_one` with the base mode first and the Spend mode second, the
#: payment at the HEAD of the second body (which is what makes it the Spend
#: one, `furina_stage.spend_mode_amount`).
def _curtain_rise():
    return _card(type="attack", effects=[{"op": "choose_one", "modes": [
        {"label": "Deal 7 damage",
         "effects": [{"op": "damage", "amount": 7, "target": "enemy"}]},
        {"label": "Spend 3: deal 13 instead",
         "effects": [{"op": "stage_spend", "amount": 3},
                     {"op": "damage", "amount": 13, "target": "enemy"}]}]}])


def test_the_spend_face_is_a_choice_and_the_spend_mode_pays_and_hits(arm):
    """Sec.3 rule 8 as `EB-746` rewrote it: "Spend N is a CHOICE on her cards,
    made when the card is played". Taking the Spend mode pays the lead and
    deals the bigger number."""
    st = _state(enemies=[_enemy(hp=60)])
    st.player.stage = [["usher", 8]]
    effects.resolve_card(st, _curtain_rise())
    assert st.enemies[0].hp == 47
    assert st.player.stage == [["usher", 5]]
    assert [e for e in st.log
            if e["event"] == "mode_chosen" and e["index"] == 1]


def test_the_same_card_played_the_other_way_keeps_the_bar(arm, monkeypatch):
    """The verb four of six round-two seats asked for: the same board, the
    same card, the base number and a lead still standing at 8."""
    monkeypatch.setattr(FS, "spend_mode_index", lambda state, modes: 0)
    st = _state(enemies=[_enemy(hp=60)])
    st.player.stage = [["usher", 8]]
    effects.resolve_card(st, _curtain_rise())
    assert st.enemies[0].hp == 53
    assert st.player.stage == [["usher", 8]]


def test_the_same_card_on_an_empty_stage_plays_at_its_base_number(arm):
    """Rule 8's refusal, as a CHOICE: the Spend mode is not OFFERED at all on
    an empty stage, so the card plays at its base number and the refusal names
    the rule rather than a bank."""
    st = _state(enemies=[_enemy(hp=60)])
    card = _curtain_rise()
    modes = card.effects[0]["modes"]
    assert effects.offered_modes(st, modes) == [0]
    assert effects.mode_refusal(st, modes[0]) is None
    assert "needs a performer on stage" in effects.mode_refusal(st, modes[1])
    effects.resolve_card(st, card)
    assert st.enemies[0].hp == 53


def test_a_bar_of_any_size_is_still_offered_the_spend_mode(arm):
    """`can_spend`'s whole sentence, one layer up: the question is OCCUPANCY
    and never size, so a lead at 1 is offered a Spend asking for 3 and rule
    8's second clause resolves it -- which is the entire Expend deck."""
    st = _state(enemies=[_enemy(hp=60)])
    st.player.stage = [["usher", 1]]
    modes = _curtain_rise().effects[0]["modes"]
    assert effects.offered_modes(st, modes) == [0, 1]


# ---------------------------------------------------------------------------
# `EB-746`. THE PILOT'S SPEND POLICY, written out in
# `furina_stage.spend_mode_index`: spend when the lead survives the payment,
# or when the payment kills; otherwise keep.
# ---------------------------------------------------------------------------

def test_the_pilot_spends_when_the_lead_survives_the_payment(arm):
    st = _state(enemies=[_enemy(hp=60)])
    st.player.stage = [["usher", 8]]
    assert FS.spend_mode_index(st, _curtain_rise().effects[0]["modes"]) == 1


def test_the_pilot_keeps_when_the_payment_would_empty_the_lead(arm):
    """Brief sec.7's line A against line B: the whole turn-one wager is
    whether the Usher survives, and this pilot does not trade a body for a
    number."""
    st = _state(enemies=[_enemy(hp=60)])
    st.player.stage = [["usher", 3]]
    assert FS.spend_mode_index(st, _curtain_rise().effects[0]["modes"]) == 0


def test_the_pilot_spends_a_dying_bar_to_finish_the_fight(arm):
    """Sec.4: "every point unspent when the last enemy falls is gone", so a
    bar kept past the last body is worth nothing."""
    st = _state(enemies=[_enemy(hp=12)])
    st.player.stage = [["usher", 3]]
    assert FS.spend_mode_index(st, _curtain_rise().effects[0]["modes"]) == 1


def test_the_policy_answers_nothing_with_the_arm_off():
    """QUARANTINED: `POLICY_VERSION` is untouched because the chooser is not
    reached on any board the arm is off on."""
    st = _state(enemies=[_enemy(hp=60)])
    st.player.stage = [["usher", 8]]
    assert FS.spend_mode_index(st, _curtain_rise().effects[0]["modes"]) is None


def test_a_named_summon_raises_the_performer_it_finds_already_on_stage(arm):
    """Sec.10 default 2 (E): "so it is never a dead draw"."""
    st = _state()
    st.player.stage = [["usher", 4]]
    card = _card(effects=[{"op": "stage_summon", "member": "usher",
                           "if_present_raise": 3}])
    effects.resolve_card(st, card)
    assert st.player.stage == [["usher", 7]]


def test_a_random_summon_only_ever_fields_somebody_not_on_stage(arm):
    st = _state()
    st.player.stage = [["usher", 1], ["chevalmarin", 1]]
    card = _card(effects=[{"op": "stage_summon", "member": "random"}])
    effects.resolve_card(st, card)
    assert [m for m, _f in st.player.stage] == [
        "usher", "chevalmarin", "crabaletta"]


def test_the_readers_read_the_seat_they_name(arm):
    """*Ousia Surge* reads the LEAD, *Pneuma Refrain* the BACK, and neither
    spends what it reads."""
    st = _state(enemies=[_enemy(hp=60)])
    st.player.stage = [["usher", 9], ["crabaletta", 4]]
    effects.resolve_card(st, _card(type="attack", effects=[
        {"op": "damage", "target": "enemy",
         "amount_formula": {"base": 0, "per": 1,
                            "count": "stage_lead_fanfare"}}]))
    assert st.enemies[0].hp == 51
    effects.resolve_card(st, _card(effects=[
        {"op": "block",
         "amount_formula": {"base": 0, "per": 1,
                            "count": "stage_back_fanfare"}}]))
    assert st.player.block == 4
    assert st.player.stage == [["usher", 9], ["crabaletta", 4]]


def test_final_bows_block_is_the_bar_it_left_with(arm):
    st = _state()
    st.player.stage = [["chevalmarin", 6]]
    effects.resolve_card(st, _card(effects=[
        {"op": "stage_final_bow"},
        {"op": "block", "amount_formula": {"base": 0, "per": 1,
                                           "count": "stage_spent"}}]))
    assert st.player.block == 6
    assert st.player.stage == []


def test_the_rare_deals_what_it_spent_to_every_enemy(arm):
    st = _state(enemies=[_enemy(hp=60), _enemy(hp=60, name="paper2")])
    st.player.stage = [["usher", 5], ["crabaletta", 4]]
    effects.resolve_card(st, _card(type="attack", effects=[
        {"op": "stage_spend_all"},
        {"op": "damage", "target": "all_enemies",
         "amount_formula": {"base": 0, "per": 1, "count": "stage_spent"}},
        {"op": "stage_curtain_call"}]))
    # 9 to both, then Crabaletta's bow-8 to one of them.
    assert sorted(e.hp for e in st.enemies) == [
        60 - 9 - FS.BOW_CRABALETTA_DAMAGE, 60 - 9]
    assert st.player.stage == [["usher", 1], ["crabaletta", 1]]


# ---------------------------------------------------------------------------
# THE TWO LOADER SEAMS.
# ---------------------------------------------------------------------------

def test_the_starter_swaps_three_kit_cards_and_no_basic(arm):
    """Sec.7's opening ten. The seven basics do not move, and that is a
    standing rule rather than this arm's discretion."""
    ids = loader.starting_deck("furina")
    assert ids.count("soloists_solicitation") == 3
    assert ids.count("stage_presence") == 3
    assert ids.count("regal_bearing") == 1
    assert sorted(i for i in ids if i.startswith("proto_fs_")) == [
        "proto_fs_curtain_rise", "proto_fs_salon_debut",
        "proto_fs_standing_ovation"]
    assert len(ids) == 10


def test_with_the_flag_off_the_printed_starter_is_dealt():
    ids = loader.starting_deck("furina")
    assert not [i for i in ids if i.startswith("proto_fs_")]
    assert "aria_of_recompense" in ids and "salon_debut" in ids


def test_the_pool_seam_swaps_fourteen_rows_at_the_same_rarity(arm):
    """RARITY FOR RARITY, so the offer odds do not move -- which is the one
    thing `rewards.character_pool` refuses a substitution over.

    Read off the SHEETS rather than through `loader.get_card`, because the
    substituted-card index is `lru_cache`d at the flag's value and a fixture
    that flips a module constant cannot reach behind it. What is being asked
    here is a question about two committed files anyway."""
    subs = loader.pool_substitutions("furina")
    assert len(subs) == 14
    rarity = {r["id"]: r["rarity"] for r in _sheet_rows("furina-cards.yaml")}
    rarity.update({r["id"]: r["rarity"] for r in _proto_rows()})
    for shipped, proto in subs.items():
        assert rarity[shipped] == rarity[proto], shipped


def test_with_the_flag_off_the_pool_seam_is_empty():
    assert loader.pool_substitutions("furina") == {}


def test_every_batch_one_row_is_named_by_one_of_the_two_maps():
    """The sheet's `replaces:` key and the arm's maps, compared in BOTH
    directions, so a row nobody named is a red test rather than a card no
    surface ever deals."""
    on_sheet = {r["id"]: r.get("replaces") for r in _proto_rows()}
    named = {**FS.POOL_SUBS, **FS.STARTER_SUBS}
    assert set(named.values()) == set(on_sheet)
    assert {p: s for s, p in named.items()} == on_sheet
    assert len(on_sheet) == 17


# ---------------------------------------------------------------------------
# THE FIGHT-ONE SCRIPT (brief sec.7), replayed at the brief's numbers.
# ---------------------------------------------------------------------------

#: Nibbit's script for this fight, as sec.7 fixes it: Butt, Hiss, Slice, Butt.
#: The 44 HP is the brief's own figure, inside `tier05/content/act1_pool.yaml`'s
#: 42-46 band, and it is written out here because the script's arithmetic is
#: stated against it.
NIBBIT_HP = 44


def _nibbit():
    return Enemy(hp=NIBBIT_HP, max_hp=NIBBIT_HP, name="nibbit",
                 intents=[{"kind": "attack", "amount": 12},          # Butt
                          {"kind": "buff", "power": "strength",
                           "amount": 2},                             # Hiss
                          {"kind": "attack", "amount": 6},           # Slice
                          {"kind": "attack", "amount": 12}])         # Butt


def _open_fight_one():
    player = _furina(hp=78, max_hp=78)
    st = _state(player=player, enemies=[_nibbit()], turn=1)
    FS.open_combat(st)          # the relic: Usher, front, 3
    FS.turn_start_regen(st)     # turn 1: no regen (rule 4)
    return st


def test_fight_one_turn_one_line_a_is_the_briefs_row(arm):
    """Sec.7's line A, the BUILD: Presence, Rising Applause (Usher 3 to 8),
    Solicitation; Usher performs Block 3. Block 9, damage 6, Nibbit at 38,
    Usher takes the 3 that survives her Block and sits at 5, Furina at 78."""
    st = _open_fight_one()
    st.player.block += 6                                   # Stage Presence
    FS.raise_fanfare(st, FS.REFILL_AMOUNT)                 # Rising Applause
    effects.deal_damage_to_enemy(st, st.enemies[0], 6)     # Solicitation
    FS.end_of_turn_acts(st)                                # Usher: Block 3

    assert st.player.block == 9
    assert st.enemies[0].hp == 38
    assert FS.lead_fanfare(st.player) == 8

    combat._enemy_turn(st, st.enemies[0])                # Butt 12
    assert st.player.block == 0
    assert FS.stage(st.player) == [["usher", 5]]
    assert st.player.hp == 78


def test_fight_one_turn_one_line_b_is_the_wager(arm, monkeypatch):
    """Line B: Presence, Curtain Rise with Spend 3 (Usher 3 to 0, bows for
    Block 4), Solicitation. Block 10, damage 19, Nibbit at 25, the stage empty,
    Furina at 76 -- the 2 HP the wager costs.

    `EB-746`: THE CARD IS PLAYED AND THE MODE IS THE SCRIPT'S. Spend is a
    choice now, so a replay of the brief's own table has to make the brief's
    own choice: line B is the WAGER, which is the Spend mode, and the pilot's
    policy would keep here (the Usher does not survive the payment and 13 does
    not finish a 44-HP Nibbit) -- which is the finding sec.7 is describing, not
    a disagreement with it."""
    monkeypatch.setattr(FS, "spend_mode_index", lambda state, modes: 1)
    st = _open_fight_one()
    st.player.block += 6                                   # Stage Presence
    effects.resolve_card(st, _curtain_rise())              # Curtain Rise
    effects.deal_damage_to_enemy(st, st.enemies[0], 6)     # Solicitation

    assert st.player.block == 10                           # 6 + the bow's 4
    assert st.enemies[0].hp == 25
    assert FS.stage(st.player) == []

    combat._enemy_turn(st, st.enemies[0])                # Butt 12
    assert st.player.hp == 76


def test_fight_one_turn_one_line_c_loses_usher_for_nothing(arm):
    """Line C, the line sec.7 says a player takes who has not yet seen that
    Usher dies either way: Curtain Rise UNSPENT for 7, Usher performs, and the
    3 that survives her Block empties him with no bow to show for it.

    `EB-746` FIXED A NUMBER HERE, and it is a defect this row exposed rather
    than a rule it moved. While Spend was a rider the engine fired, the card
    had no unspent line to play at all -- so this pin dealt 13, the SPENT
    number, and asserted Nibbit at 25. The brief's own table (sec.7) says line
    C deals 13 for the TURN, which is Curtain Rise at 7 plus Solicitation at
    6, and leaves Nibbit at 31. Playing the card at its base mode is what the
    line is, and 31 is the brief's own figure.
    """
    st = _open_fight_one()
    st.player.block += 6
    # `EB-746`: line C is the BASE mode, chosen, which is what the pilot's own
    # policy takes on this board -- the Usher does not survive a Spend 3 from a
    # bar of 3, and 13 does not finish a 44-HP Nibbit.
    assert FS.spend_mode_index(st, _curtain_rise().effects[0]["modes"]) == 0
    effects.resolve_card(st, _curtain_rise())              # unspent
    effects.deal_damage_to_enemy(st, st.enemies[0], 6)
    FS.end_of_turn_acts(st)

    assert st.player.block == 9
    assert st.enemies[0].hp == 31
    combat._enemy_turn(st, st.enemies[0])
    assert FS.stage(st.player) == []
    assert st.player.hp == 78
    assert not [e for e in st.log if e["event"] == "stage_bow"]


def test_fight_one_runs_to_the_curtain_on_line_a_and_the_damage_line(arm):
    """The whole script the row asks for: sec.7's line A on turn one, then the
    DAMAGE line on turn three, which sec.7 says is the better of the two.

    Every number below is the brief's own. What this pins is that an engine
    playing the brief's plays reaches the brief's board -- not that the plays
    are good, which is the seats' question (sec.13).
    """
    st = _open_fight_one()

    # --- turn 1, line A -------------------------------------------------
    st.player.block += 6
    FS.raise_fanfare(st, FS.REFILL_AMOUNT)                 # Usher 3 -> 8
    effects.deal_damage_to_enemy(st, st.enemies[0], 6)
    FS.end_of_turn_acts(st)
    combat._enemy_turn(st, st.enemies[0])                # Butt 12
    assert st.enemies[0].hp == 38
    assert FS.stage(st.player) == [["usher", 5]]

    # --- turn 2: Salon Début fields Crabaletta, Solicitation, Regal Bearing --
    st.turn = 2
    st.player.block = 0
    FS.turn_start_regen(st)                                # Usher 5 -> 6
    assert FS.lead_fanfare(st.player) == 6
    st.player.block += 3                                   # Regal Bearing
    # `EB-738`: she arrives at 1 and does NOT act on arrival, so the board is
    # sec.7's own -- "Solicitation 6 (38 to 32) ... Performances: Usher Block 3
    # (wasted), Crabaletta 5 (32 to 27)".
    FS.summon(st, "crabaletta")
    assert st.enemies[0].hp == 38
    effects.deal_damage_to_enemy(st, st.enemies[0], 6)     # Solicitation
    assert st.enemies[0].hp == 32
    FS.end_of_turn_acts(st)                                # Usher 3, Crab 5
    assert st.enemies[0].hp == 27
    combat._enemy_turn(st, st.enemies[0])                # Hiss: +2 Strength
    assert st.enemies[0].powers.get("strength") == 2

    # --- turn 3, the DAMAGE line ---------------------------------------
    st.turn = 3
    st.player.block = 0
    FS.turn_start_regen(st)                                # Usher 6 -> 7
    st.player.block += 6                                   # Stage Presence
    # `EB-746`: the DAMAGE line takes the Spend mode, and here the pilot's own
    # policy takes it unprompted -- the Usher is at 7 and survives the 3.
    assert FS.spend_mode_index(st, _curtain_rise().effects[0]["modes"]) == 1
    effects.resolve_card(st, _curtain_rise())              # Curtain Rise
    effects.deal_damage_to_enemy(st, st.enemies[0], 6)     # Solicitation
    FS.end_of_turn_acts(st)                                # Usher 3, Crab 5
    assert st.player.block == 9
    # 27, less the turn's 19, less Crabaletta's 5: sec.7's damage line, "with
    # Crabaletta's 5, Nibbit is at 3", and sec.7's turn four kills it with two
    # Solicitations.
    assert st.enemies[0].hp == 3
    assert FS.lead_fanfare(st.player) == 4


def test_the_turn_census_is_emitted_even_at_zero(arm):
    """Sec.13's third report. A distribution that silently omits its zeros is
    not a distribution."""
    st = _state()
    FS.note_turn_census(st)
    st.player.stage = [["usher", 3], ["crabaletta", 1]]
    FS.note_turn_census(st)
    rows = [e for e in st.log if e["event"] == "stage_census"]
    assert [r["performers"] for r in rows] == [0, 2]

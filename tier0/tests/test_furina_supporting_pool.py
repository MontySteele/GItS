"""FURINA, THE STAGE -- THE SUPPORTING POOL (2026-09-26), the sim's pins.

The design is `review/active/furina-supporting-pool-2026-09-26.md`, ruled with
all four defaults and swept before the build: 28 of its 29 cards (Sold Out,
the fourth seat, is built beside them). The C# twin's pins are
`klee-mod/KleeTests/Prototype/FurinaSupportingPoolTests.cs`, which runs the
ledger's own moves on the same boards.

WHAT IS PINNED: the rows and the pool seam; each new mechanic, on a scripted
board, in the paper's family order.

NOTHING MEASURED ON A PROTOTYPE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

import random

import pytest
import yaml

from tier0.content import loader
from tier0.engine import effects, furina_stage, reactions
from tier0.engine.state import Card, CombatState, Enemy, Player

FS = furina_stage


@pytest.fixture
def arm(monkeypatch):
    monkeypatch.setattr(FS, "FURINA_STAGE", True)


def _furina(**kw):
    return Player(hp=200, max_hp=200, fanfare_cap=99, character_id="furina",
                  **kw)


def _enemy(hp=500, name="paper", aura=None):
    e = Enemy(hp=hp, max_hp=hp, name=name,
              intents=[{"kind": "block", "amount": 0}])
    e.aura = aura
    return e


def _state(stage=(), enemies=None, seed=0, deck=0):
    st = CombatState(player=_furina(), enemies=enemies or [_enemy()],
                     rng=random.Random(seed))
    st.turn = 2
    st.player.stage = [list(pair) for pair in stage]
    st.player.draw_pile = [_card([], cid=f"filler{i}") for i in range(deck)]
    return st


def _card(effects_, cid="probe", type_="skill"):
    return Card(id=cid, name=cid, cost=1, type=type_, rarity="common",
                effects=effects_)


def _rows():
    rows = yaml.safe_load(
        (loader.DOCS_DIR / "prototype-surface.yaml").read_text(
            encoding="utf-8"))
    return {r["id"]: r for r in rows}


def _row_card(rid, upgraded=False):
    """A sheet row as the sim plays it, its upgrade applied on request."""
    row = dict(_rows()[rid])
    card = Card(id=rid, name=row["name"], cost=row["cost"], type=row["type"],
                rarity=row["rarity"], effects=row["effects"])
    if upgraded:
        import copy
        card = copy.deepcopy(card)
        for key, delta in (row.get("upgrade") or {}).items():
            if key == "cost":
                card.cost += int(delta)
                continue
            _apply_delta(card, key, int(delta))
    return card


def _apply_delta(card, key, delta):
    """The few upgrade keys these pins read, bound as `upgrades` binds them."""
    top = card.effects
    if key in ("stage_whisper", "stage_intermission", "stage_guest"):
        next(fx for fx in top if fx.get("op") == key)["amount"] += delta
    elif key == "power_amount":
        next(fx for fx in top if fx.get("op") == "apply_power")["amount"] += delta
    elif key == "damage":
        next(fx for fx in top if fx.get("op") == "damage")["amount"] += delta
    else:
        raise AssertionError(key)


def _power(st, name, amount=1):
    st.player.powers[name] = st.player.powers.get(name, 0) + amount


def _events(st, name):
    return [e for e in st.log if e.get("event") == name]


# ---------------------------------------------------------------------------
# THE ROWS AND THE POOL.
# ---------------------------------------------------------------------------

#: id -> (name, rarity, cost, type), the paper's tables as swept, with the two
#: renames made for title clashes (Showstopper, Undertow).
TABLE = {
    "plot_twist": ("Plot Twist", "common", 1, "skill"),
    "revolving_stage": ("Revolving Stage", "uncommon", 1, "power"),
    "oratrices_verdict": ("Oratrice's Verdict", "uncommon", 0, "skill"),
    "guest_star_lyney": ("Guest Star: Lyney", "rare", 1, "skill"),
    "stage_whisper": ("Stage Whisper", "common", 0, "skill"),
    "cheered_on": ("Cheered On", "common", 1, "attack"),
    "season_tickets": ("Season Tickets", "uncommon", 1, "power"),
    "guest_star_escoffier": ("Guest Star: Escoffier", "rare", 2, "skill"),
    "star_billing": ("Star Billing", "uncommon", 1, "power"),
    "held_applause": ("Held Applause", "uncommon", 1, "skill"),
    "echoing_hall": ("Echoing Hall", "uncommon", 1, "power"),
    "eternal_applause": ("Eternal Applause", "rare", 1, "power"),
    "spirited_aria": ("Spirited Aria", "common", 1, "attack"),
    "intermission": ("Intermission", "uncommon", 1, "skill"),
    "counterclaim": ("Counterclaim", "uncommon", 1, "attack"),
    "bring_the_house_down": ("Bring the House Down", "rare", 2, "attack"),
    "da_capo": ("Da Capo", "uncommon", 1, "attack"),
    "grand_finale": ("Grand Finale", "rare", 1, "skill"),
    "gala_premiere": ("Gala Premiere", "rare", 2, "skill"),
    "bubble_aria": ("Bubble Aria", "common", 1, "attack"),
    "groundswell": ("Groundswell", "uncommon", 1, "attack"),
    "tide_of_applause": ("Tide of Applause", "uncommon", 1, "power"),
    "grand_deluge": ("Grand Deluge", "rare", 2, "attack"),
    "regina_of_all_waters": ("Regina of All Waters", "rare", 2, "power"),
    "solo_verse": ("Solo Verse", "common", 1, "attack"),
    "soliloquy": ("Soliloquy", "uncommon", 1, "power"),
    "one_woman_show": ("One-Woman Show", "rare", 2, "power"),
    "dual_nature": ("Dual Nature", "uncommon", 1, "skill"),
}


def test_the_twenty_eight_rows_are_the_papers_tables():
    rows = _rows()
    for key, (name, rarity, cost, type_) in TABLE.items():
        row = rows[f"proto_fs_{key}"]
        assert (row["name"], row["rarity"], row["cost"], row["type"]) == (
            name, rarity, cost, type_), key
        assert row["register"] == "salon"
        assert row["authored_by"] == ["claude"]
    # 6 Commons, 13 Uncommons, 9 Rares (Sold Out is the tenth Rare).
    by = [r for _n, r, _c, _t in TABLE.values()]
    assert (by.count("common"), by.count("uncommon"), by.count("rare")) == (
        6, 13, 9)


def test_every_row_but_solo_verse_replaces_a_row_the_filter_drops(arm):
    rows = _rows()
    subs = {p: s for s, p in FS.POOL_SUBS.items()}
    shipped = {r["id"]: r for r in yaml.safe_load(
        (loader.DOCS_DIR / "furina-cards.yaml").read_text(encoding="utf-8"))}
    for key in TABLE:
        rid = f"proto_fs_{key}"
        if rid in FS.POOL_ADDS:
            assert "replaces" not in rows[rid]
            continue
        assert rows[rid]["replaces"] == subs[rid]
        assert shipped[subs[rid]]["rarity"] == rows[rid]["rarity"]
    assert FS.POOL_ADDS == ("proto_fs_solo_verse",)
    # Sold Out's own row is built beside this batch and takes
    # `unheard_confession`; no row here may.
    assert "unheard_confession" not in [rows[f"proto_fs_{k}"].get("replaces")
                                        for k in TABLE]


def test_the_additions_reach_the_offer_and_the_flag_off_pool_does_not(arm):
    from tier05 import rewards
    assert loader.pool_additions("furina") == ("proto_fs_solo_verse",)
    # `character_pool` is lru-cached: a flag-off pool another test on this
    # worker built would answer here, and this test's arm-on pool would
    # answer the next one. Clear on both sides.
    rewards.character_pool.cache_clear()
    try:
        pool = rewards.character_pool("furina")
        assert "proto_fs_solo_verse" in [c.id for c in pool["common"]]
    finally:
        rewards.character_pool.cache_clear()


def test_with_the_flag_off_there_are_no_additions():
    assert loader.pool_additions("furina") == ()


# ---------------------------------------------------------------------------
# 1. ARRANGING THE STAGE.
# ---------------------------------------------------------------------------

def test_plot_twist_reverses_the_seats(arm):
    st = _state([["usher", 3], ["chevalmarin", 4], ["crabaletta", 5]])
    effects.resolve_card(st, _row_card("proto_fs_plot_twist"))
    assert st.player.stage == [["crabaletta", 5], ["chevalmarin", 4],
                               ["usher", 3]]
    assert st.player.block == 6
    st = _state([["usher", 3], ["crabaletta", 5]])
    effects.resolve_card(st, _row_card("proto_fs_plot_twist"))
    assert st.player.stage == [["crabaletta", 5], ["usher", 3]]


def test_revolving_stage_moves_the_back_forward_after_the_regen(arm):
    """The recommendation taken: AFTER rule 4's regen, so the regen went to
    the performer that led last turn."""
    st = _state([["usher", 3], ["chevalmarin", 4], ["crabaletta", 5]])
    _power(st, FS.REVOLVING_STAGE)
    FS.turn_start_regen(st)
    FS.turn_start_powers(st)
    assert st.player.stage == [["crabaletta", 5], ["usher", 4],
                               ["chevalmarin", 4]]


def test_oratrices_verdict_points_the_random_acts_this_turn(arm):
    weak = _enemy(hp=40, name="weak")
    strong = _enemy(hp=500, name="strong")
    st = _state([["crabaletta", 3]], enemies=[weak, strong], seed=3)
    effects.resolve_card(st, _row_card("proto_fs_oratrices_verdict"))
    assert st.player.stage_verdict is weak        # the bound aim
    for _ in range(3):
        FS.perform(st, "crabaletta", pair=st.player.stage[0])
    assert weak.hp == 40 - 3 * FS.ACT_CRABALETTA_DAMAGE
    assert strong.hp == 500
    # The sweep is its last use this turn.
    FS.end_of_turn_acts(st)
    assert st.player.stage_verdict is None


def test_a_dead_verdict_target_falls_back_to_random(arm):
    dead = _enemy(hp=0, name="dead")
    live = _enemy(hp=50, name="live")
    st = _state([["crabaletta", 3]], enemies=[dead, live])
    st.player.stage_verdict = dead
    FS.perform(st, "crabaletta", pair=st.player.stage[0])
    assert live.hp == 50 - FS.ACT_CRABALETTA_DAMAGE


def test_lyney_pays_two_hits_pyro_and_swaps_the_front_and_back(arm):
    enemy = _enemy()
    st = _state([["usher", 3], ["chevalmarin", 2], ["lyney", 5]],
                enemies=[enemy])
    FS.perform(st, "lyney", pair=st.player.stage[2])
    assert st.player.stage == [["lyney", 3], ["chevalmarin", 2],
                               ["usher", 3]]
    assert enemy.hp == 500 - FS.ACT_LYNEY_DAMAGE
    assert enemy.aura == "pyro"
    # One performer: nothing to swap.
    st = _state([["lyney", 5]])
    FS.perform(st, "lyney", pair=st.player.stage[0])
    assert st.player.stage == [["lyney", 3]]
    # Short of his price, he does not act.
    enemy = _enemy()
    st = _state([["usher", 3], ["lyney", 1]], enemies=[enemy])
    FS.perform(st, "lyney", pair=st.player.stage[1])
    assert st.player.stage == [["usher", 3], ["lyney", 1]]
    assert enemy.hp == 500
    assert _events(st, "stage_unpaid")


def test_lyneys_bow_is_free_and_swaps_the_stage_he_left(arm):
    st = _state([["usher", 3], ["chevalmarin", 2], ["lyney", 2]])
    FS.perform(st, "lyney", pair=st.player.stage[2])
    # He paid his last 2: the act swapped (Lyney to the front, then he
    # left), then his free Bow hit and swapped the stage he left.
    assert [m for m, _f in st.player.stage] == ["usher", "chevalmarin"]
    assert st.enemies[0].hp == 500 - 2 * FS.ACT_LYNEY_DAMAGE


def test_stage_whisper_moves_up_to_three_and_the_back_keeps_one(arm):
    st = _state([["usher", 2], ["crabaletta", 7]])
    effects.resolve_card(st, _row_card("proto_fs_stage_whisper"))
    assert st.player.stage == [["usher", 5], ["crabaletta", 4]]
    st = _state([["usher", 2], ["crabaletta", 3]])
    effects.resolve_card(st, _row_card("proto_fs_stage_whisper"))
    assert st.player.stage == [["usher", 4], ["crabaletta", 1]]
    # It never empties the back, so it never Bows it.
    st = _state([["usher", 2], ["crabaletta", 1]])
    effects.resolve_card(st, _row_card("proto_fs_stage_whisper"))
    assert st.player.stage == [["usher", 2], ["crabaletta", 1]]
    assert not _events(st, "stage_bow")
    # One performer: nothing.
    st = _state([["usher", 6]])
    effects.resolve_card(st, _row_card("proto_fs_stage_whisper"))
    assert st.player.stage == [["usher", 6]]
    # Upgraded: up to 5.
    st = _state([["usher", 2], ["crabaletta", 9]])
    effects.resolve_card(st, _row_card("proto_fs_stage_whisper", True))
    assert st.player.stage == [["usher", 7], ["crabaletta", 4]]


# ---------------------------------------------------------------------------
# 2. FEEDING.
# ---------------------------------------------------------------------------

def test_cheered_on_hits_and_feeds_the_back(arm):
    st = _state([["usher", 3], ["crabaletta", 1]])
    effects.resolve_card(st, _row_card("proto_fs_cheered_on"))
    assert st.enemies[0].hp == 500 - 7
    assert st.player.stage == [["usher", 3], ["crabaletta", 3]]


def test_season_tickets_raise_the_back_and_summon_on_an_empty_stage(arm):
    st = _state([["usher", 3], ["crabaletta", 1]])
    _power(st, FS.SEASON_TICKETS, 2)
    FS.turn_start_powers(st)
    assert st.player.stage[-1] == ["crabaletta", 3]
    st = _state([])
    _power(st, FS.SEASON_TICKETS, 3)
    FS.turn_start_powers(st)
    assert len(st.player.stage) == 1 and st.player.stage[0][1] == 3


def test_escoffier_pays_three_feeds_the_cast_and_hits_all_with_cryo(arm):
    a, b = _enemy(name="a"), _enemy(name="b")
    st = _state([["usher", 2], ["escoffier", 6], ["crabaletta", 1]],
                enemies=[a, b])
    FS.perform(st, "escoffier", pair=st.player.stage[1])
    assert st.player.stage == [["usher", 4], ["escoffier", 3],
                               ["crabaletta", 3]]
    assert (a.hp, b.hp) == (500 - 3, 500 - 3)
    assert a.aura == "cryo"


def test_escoffiers_bow_is_free_and_still_feeds(arm):
    st = _state([["usher", 2], ["escoffier", 3]])
    FS.perform(st, "escoffier", pair=st.player.stage[1])
    # She paid her last 3 and left; her act gave Usher 2, her Bow 2 more.
    assert st.player.stage == [["usher", 6]]


def test_star_billing_draws_whenever_a_guest_star_joins(arm):
    st = _state([["usher", 3]], deck=10)
    _power(st, FS.STAR_BILLING, 2)
    effects.resolve_card(st, _row_card("proto_fs_guest_star_lyney"))
    assert len(st.player.hand) == 2
    # A second copy's recast (Bow, then return) is a join too.
    effects.resolve_card(st, _row_card("proto_fs_guest_star_lyney"))
    assert len(st.player.hand) == 4


# ---------------------------------------------------------------------------
# 3. BENDING THE FADE.
# ---------------------------------------------------------------------------

def test_held_applause_skips_this_turns_fade_only(arm):
    st = _state([["usher", 3], ["crabaletta", 11]])
    effects.resolve_card(st, _row_card("proto_fs_held_applause"))
    assert st.player.block == 7
    FS.fade(st)
    assert st.player.stage[1][1] == 11
    FS.fade(st)
    assert st.player.stage[1][1] == 11 - FS.fade_loss(11)


def test_echoing_hall_sends_the_fades_loss_to_the_front(arm):
    st = _state([["usher", 3], ["chevalmarin", 9], ["crabaletta", 11]])
    _power(st, FS.ECHOING_HALL)
    _power(st, FS.ECHOING_HALL)       # a move: a second copy adds nothing
    FS.fade(st)
    lost = FS.fade_loss(9) + FS.fade_loss(11)
    assert st.player.stage == [["usher", 3 + lost],
                               ["chevalmarin", 9 - FS.fade_loss(9)],
                               ["crabaletta", 11 - FS.fade_loss(11)]]
    assert FS.total_fanfare(st.player) == 3 + 9 + 11


def test_eternal_applause_moves_the_line_to_ten(arm):
    assert FS.fade_loss(14, FS.ETERNAL_FADE_THRESHOLD) == 2
    st = _state([["usher", 3], ["chevalmarin", 9], ["crabaletta", 14]])
    _power(st, FS.ETERNAL_APPLAUSE)
    _power(st, FS.ETERNAL_APPLAUSE)   # copies do not stack further
    FS.fade(st)
    assert st.player.stage == [["usher", 3], ["chevalmarin", 9],
                               ["crabaletta", 12]]


# ---------------------------------------------------------------------------
# 4. CASHING OUT.
# ---------------------------------------------------------------------------

def test_spirited_arias_spend_mode_also_draws_two(arm):
    card = _row_card("proto_fs_spirited_aria")
    modes = card.effects[0]["modes"]
    assert [fx["op"] for fx in modes[1]["effects"]] == [
        "stage_spend", "damage", "draw"]
    assert modes[1]["effects"][0]["amount"] == 2
    assert modes[1]["effects"][2]["amount"] == 2
    st = _state([["usher", 3], ["crabaletta", 5]], deck=5)
    effects.resolve_card(st, card)
    # The arm's pilot spends when the payer survives.
    assert st.player.stage == [["usher", 3], ["crabaletta", 3]]
    assert len(st.player.hand) == 2
    assert st.enemies[0].hp == 500 - 8


@pytest.mark.parametrize("bar,upgraded,drawn", [
    (7, False, 2), (8, False, 2), (9, False, 3), (7, True, 3), (1, False, 0)])
def test_intermission_bows_the_back_and_draws_per_three(arm, bar, upgraded,
                                                       drawn):
    st = _state([["usher", 3], ["crabaletta", bar]], deck=10)
    effects.resolve_card(st, _row_card("proto_fs_intermission", upgraded))
    assert st.player.stage == [["usher", 3]]
    # A real Bow: Crabaletta's act, once more.
    assert _events(st, "stage_bow")
    assert st.enemies[0].hp == 500 - FS.ACT_CRABALETTA_DAMAGE
    assert len(st.player.hand) == drawn


def test_counterclaim_deals_the_second_seven_after_a_hit_on_the_front(arm):
    st = _state([["usher", 9], ["crabaletta", 1]])
    effects.resolve_card(st, _row_card("proto_fs_counterclaim"))
    assert st.enemies[0].hp == 500 - 7
    FS.absorb(st, 4)                  # an enemy's hit reaches the front
    effects.resolve_card(st, _row_card("proto_fs_counterclaim"))
    assert st.enemies[0].hp == 500 - 7 - 14
    # The window closes as her turn ends.
    FS.end_of_turn_acts(st)
    assert st.player.stage_front_hit is False


def test_bring_the_house_down_cashes_the_front_for_all(arm):
    a, b = _enemy(name="a"), _enemy(name="b")
    st = _state([["usher", 6], ["crabaletta", 2]], enemies=[a, b])
    effects.resolve_card(st, _row_card("proto_fs_bring_the_house_down"))
    # Usher's Bow (3 Block), then 2 per point to ALL.
    assert st.player.stage == [["crabaletta", 2]]
    assert st.player.block == FS.ACT_USHER_BLOCK
    assert (a.hp, b.hp) == (500 - 12, 500 - 12)
    st = _state([])
    effects.resolve_card(st, _row_card("proto_fs_bring_the_house_down"))
    assert st.enemies[0].hp == 500


# ---------------------------------------------------------------------------
# 5. BOWS AND ENCORES.
# ---------------------------------------------------------------------------

def test_da_capo_counts_every_bow_this_combat(arm):
    st = _state([["usher", 3]])
    effects.resolve_card(st, _row_card("proto_fs_da_capo"))
    assert st.enemies[0].hp == 500 - 5
    st.player.stage_bows = 3
    effects.resolve_card(st, _row_card("proto_fs_da_capo"))
    assert st.enemies[0].hp == 500 - 5 - (5 + 2 * 3)


def test_grand_finale_bows_everyone_in_place(arm):
    st = _state([["usher", 3], ["navia", 4], ["crabaletta", 2]], deck=10)
    _power(st, FS.THUNDEROUS_APPLAUSE, 2)
    st.player.stage_power_copies[FS.THUNDEROUS_APPLAUSE] = 1
    _power(st, FS.FIVE_CENTURY_ACT)
    effects.resolve_card(st, _row_card("proto_fs_grand_finale"))
    # Nobody left; each Bow fired its act and its reader (a draw and a Raise
    # of 2 on the back each).
    assert [m for m, _f in st.player.stage] == ["usher", "navia",
                                                "crabaletta"]
    assert st.player.stage[-1][1] == 2 + 3 * 2
    assert len(st.player.hand) == 3
    assert st.player.block == FS.ACT_USHER_BLOCK
    assert st.enemies[0].hp == 500 - 4 - FS.ACT_CRABALETTA_DAMAGE
    assert st.player.stage_bows == 3
    assert not _events(st, "stage_return")


def test_a_grand_finale_bow_gift_skips_the_giver(arm):
    st = _state([["usher", 2], ["charlotte", 4], ["sigewinne", 5]])
    FS.grand_finale(st)
    # Charlotte's Bow: each OTHER performer +1; Sigewinne's (at the back):
    # the front +3, free.
    assert st.player.stage == [["usher", 2 + 1 + 3], ["charlotte", 4],
                               ["sigewinne", 5 + 1]]


def test_gala_premiere_summons_the_trio_at_three_each(arm):
    st = _state([])
    effects.resolve_card(st, _row_card("proto_fs_gala_premiere"))
    assert st.player.stage == [["usher", 3], ["chevalmarin", 3],
                               ["crabaletta", 3]]
    # On a full stage each summon is a recast (rule 3): the front Bows and
    # leaves, and the newcomer adds its own 3 to the leaver's bar.
    st = _state([["navia", 4], ["neuvillette", 2], ["clorinde", 5]])
    effects.resolve_card(st, _row_card("proto_fs_gala_premiere"))
    assert st.player.stage == [["usher", 4 + 3], ["chevalmarin", 2 + 3],
                               ["crabaletta", 5 + 3]]


# ---------------------------------------------------------------------------
# 6. HYDRO AND REACTIONS.
# ---------------------------------------------------------------------------

def test_bubble_aria_hits_twice_and_applies_hydro(arm):
    st = _state([["usher", 3]])
    effects.resolve_card(st, _row_card("proto_fs_bubble_aria"))
    assert st.enemies[0].hp == 500 - 8
    assert st.enemies[0].aura == "hydro"


def test_groundswell_feeds_the_front_off_an_aura(arm):
    st = _state([["usher", 3], ["crabaletta", 1]])
    effects.resolve_card(st, _row_card("proto_fs_groundswell"))
    assert st.player.stage[0][1] == 3
    st = _state([["usher", 3], ["crabaletta", 1]],
                enemies=[_enemy(aura="pyro")])
    effects.resolve_card(st, _row_card("proto_fs_groundswell"))
    assert st.player.stage[0][1] == 6


def test_tide_of_applause_raises_the_back_per_reaction(arm):
    st = _state([["usher", 3], ["crabaletta", 1]],
                enemies=[_enemy(aura="pyro")])
    _power(st, FS.TIDE_OF_APPLAUSE, 2)
    reactions.resolve_hit(st, st.enemies[0], "hydro", 0, "probe")
    assert st.player.stage[-1][1] == 3


def test_grand_deluge_gives_each_performer_two_once_on_a_reaction(arm):
    a, b = _enemy(name="a", aura="pyro"), _enemy(name="b", aura="pyro")
    st = _state([["usher", 3], ["crabaletta", 1]], enemies=[a, b])
    effects.resolve_card(st, _row_card("proto_fs_grand_deluge"))
    # Two reactions, one gift: each performer +2 once.
    assert st.player.stage == [["usher", 5], ["crabaletta", 3]]
    st = _state([["usher", 3], ["crabaletta", 1]])
    effects.resolve_card(st, _row_card("proto_fs_grand_deluge"))
    assert st.player.stage == [["usher", 3], ["crabaletta", 1]]
    assert st.enemies[0].aura == "hydro"


def test_regina_soaks_all_enemies_at_turn_start(arm):
    a, b = _enemy(name="a"), _enemy(name="b", aura="pyro")
    st = _state([["usher", 3]], enemies=[a, b])
    _power(st, FS.REGINA)
    FS.turn_start_powers(st)
    assert a.aura == "hydro"
    assert b.aura is None             # Hydro on Pyro reacted


# ---------------------------------------------------------------------------
# 7. FURINA'S SIDE PATHS.
# ---------------------------------------------------------------------------

def test_solo_verse_doubles_on_an_empty_stage(arm):
    st = _state([["usher", 3]])
    effects.resolve_card(st, _row_card("proto_fs_solo_verse"))
    assert st.enemies[0].hp == 500 - 6
    st = _state([])
    effects.resolve_card(st, _row_card("proto_fs_solo_verse"))
    assert st.enemies[0].hp == 500 - 12


def test_soliloquy_adds_to_every_hit_while_the_stage_is_empty(arm):
    st = _state([])
    _power(st, FS.SOLILOQUY, 3)
    effects.resolve_card(st, _row_card("proto_fs_bubble_aria"))
    assert st.enemies[0].hp == 500 - 2 * (4 + 3)
    st = _state([["usher", 3]])
    _power(st, FS.SOLILOQUY, 3)
    effects.resolve_card(st, _row_card("proto_fs_bubble_aria"))
    assert st.enemies[0].hp == 500 - 8


def test_one_woman_show_pays_only_on_an_empty_stage_and_before_tickets(arm):
    st = _state([], deck=5)
    st.player.energy = 3
    _power(st, FS.ONE_WOMAN_SHOW)
    _power(st, FS.SEASON_TICKETS, 2)
    FS.turn_start_powers(st)
    assert st.player.energy == 4
    assert len(st.player.hand) == 1
    # Season Tickets then summoned onto the stage the show found empty.
    assert len(st.player.stage) == 1
    st = _state([["usher", 3]], deck=5)
    st.player.energy = 3
    _power(st, FS.ONE_WOMAN_SHOW)
    FS.turn_start_powers(st)
    assert st.player.energy == 3 and not st.player.hand


def test_dual_nature_sets_this_turns_half_without_stacking(arm):
    st = _state([["usher", 3], ["crabaletta", 1]])
    FS.dual_nature(st)
    # No enemy intends to attack: the pilot's pick is Ousia.
    assert st.player.stage_act_damage_mult == 2
    st.player.stage_act_damage_mult = 3       # Arkhe Alignment x2 copies
    FS.dual_nature(st)
    assert st.player.stage_act_damage_mult == 3

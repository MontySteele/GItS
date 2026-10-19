"""YAE REVIEW R3 (ruled 2026-10-14, both picks (a) as amended):
`review/active/yae-review-r3-2026-10-14.md`. The sim half; the C# half is
`klee-mod/KleeTests/Prototype/YaeReviewR3Tests.cs`.

  1. Sakura kinds: Sakura (Thunder), Foxfire Sakura (ALL, 1 + Level),
     Kitsune Sakura (the decoy, 2 + Level Block). A Sakura acts at the end
     of the turn, at Last Bloom and on Tenko. Tenko is one plain rule. A
     full-shrine plant: same kind levels the oldest, another kind withers it
     and takes its place.
  2. The Masterpiece: a permanent stack plus one temporary slot per card;
     stacked layers add up; Reprint's exact arithmetic.
  3. Second Printing, Author's Copy (never an Author's Copy: no
     energy-positive loop), Serial Novel.
  4. Fallen Petals, an active Skill.
"""

from __future__ import annotations

import random

import pytest

from tier0.content import loader
from tier0.engine import combat
from tier0.engine import yae_shrine as Y
from tier0.engine.state import CombatState, Enemy


@pytest.fixture(autouse=True)
def yae():
    loader.reset_arm_caches()
    Y.SCALING = "level"
    try:
        yield
    finally:
        Y.SCALING = "level"
        loader.reset_arm_caches()


def _enemy(name="e", hp=100):
    return Enemy(hp=hp, max_hp=hp, name=name,
                 intents=[{"kind": "block", "amount": 0}])


def _state(n=1):
    p = Y.build_player()
    p.draw_pile = []
    st = CombatState(player=p, enemies=[_enemy(f"e{i}") for i in range(n)],
                     rng=random.Random(0))
    st.turn = 1
    st.in_player_turn = True
    return st


def _ym(name):
    return "proto_ym_" + name


def _card(name):
    return loader.get_card(name if name in ("strike", "defend") else _ym(name))


def _published(name, stack):
    c = _card(name)
    Y.publish_to(c, stack)
    return c


def _play(st, card):
    if isinstance(card, str):
        card = _card(card)
    if card not in st.player.hand:
        st.player.hand.append(card)
    st.player.energy = max(st.player.energy, 10)
    combat.play_card(st, card)
    return card


def _led(st):
    return Y.ledger(st.player)


def _acts(st, reason=None):
    return [r for r in st.log if r["event"] == "yae_sakura_strike"
            and (reason is None or r["reason"] == reason)]


def _hp(st):
    return [e.hp for e in st.enemies]


# ===========================================================================
# 1. Sakura kinds
# ===========================================================================

def test_every_plain_planter_plants_a_plain_sakura():
    st = _state()
    # Twin Sakura left this list with the Yae block and Edit pass
    # (2026-10-19): a Sakura and a Kitsune Sakura (its own test).
    for name in ("yakan_evocation", "thunder_petal"):
        _play(st, name)
    assert {s.kind for s in _led(st).sakura} == {Y.THUNDER}


def test_twin_sakura_plants_a_sakura_then_a_kitsune_and_the_lantern_and_canopy_plant_kitsune():
    """The Yae block and Edit pass (2026-10-19): Kitsune at Defect's Frost
    access."""
    st = _state()
    _play(st, "twin_sakura")
    assert [s.kind for s in _led(st).sakura] == [Y.THUNDER, Y.KITSUNE]
    st = _state()
    _play(st, "cliffhanger")                     # Kitsune Lantern
    assert [s.kind for s in _led(st).sakura] == [Y.KITSUNE]
    assert st.enemies[0].hp == st.enemies[0].max_hp - 7
    st = _state()
    st.player.energy = 3
    _play(st, "sakura_canopy")
    assert [s.kind for s in _led(st).sakura] == [Y.KITSUNE, Y.KITSUNE]
    assert st.player.block == 6


def test_a_sakura_strikes_one_enemy_for_two_plus_level():
    st = _state(n=2)
    Y.plant(st, 1)          # the draft pass: Yakan Evocation strikes now
    Y.turn_end(st)
    assert sum(100 - h for h in _hp(st)) == 2 + 1


def test_foxfire_sweep_plants_a_foxfire_sakura_that_hits_all():
    st = _state(n=3)
    _play(st, "foxfire_sweep")                   # 4 to ALL, then the plant
    assert _led(st).sakura[0].kind == Y.FOXFIRE
    # Yae flat-value pass, 2026-10-17: "It strikes now." (1 + Level 1, each).
    assert _hp(st) == [94, 94, 94]
    Y.turn_end(st)
    assert _hp(st) == [92, 92, 92]               # 1 + Level 1, each


def test_the_guard_plants_a_kitsune_decoy_that_gives_block():
    st = _state()
    _play(st, "shrine_maidens_guard")
    assert st.player.block == 6
    assert _led(st).sakura[0].kind == Y.KITSUNE
    st.player.block = 0
    Y.turn_end(st)
    assert st.player.block == 2 + 1 and _hp(st) == [100]


def test_red_ink_adds_three_to_any_kind():
    st = _state(n=2)
    _play(st, "yakan_evocation")
    _play(st, "foxfire_sweep")
    _play(st, "shrine_maidens_guard")
    _play(st, "inked_branches")                  # Red Ink on every Sakura
    sizes = [Y.act_size(st, s) for s in _led(st).sakura]
    assert sizes == [2 + 1 + 3, 1 + 1 + 3, 2 + 1 + 3]


def test_edict_pays_on_damage_kinds_only():
    st = _state()
    _play(st, "edict_of_cleansing")
    _play(st, "shrine_maidens_guard")
    _play(st, "foxfire_sweep")
    st.enemies[0].powers["weak"] = 1
    hp = st.enemies[0].hp
    st.player.block = 0
    Y.turn_end(st)
    assert st.player.block == 3                  # no Edict on the Kitsune
    assert hp - st.enemies[0].hp == 2 + 3        # the Foxfire, Edict on top


def test_fox_fire_on_a_kitsune_fires_when_it_acts():
    st = _state()
    _play(st, "shrine_maidens_guard")
    _play(st, "fox_fire_draft")                  # the newest: the Kitsune
    hp = st.enemies[0].hp
    st.player.block = 0
    Y.turn_end(st)
    assert st.player.block == 3 and hp - st.enemies[0].hp == Y.FOX_FIRE_DAMAGE


def test_a_sakura_acts_at_turn_end_last_bloom_and_tenko():
    st = _state()
    _play(st, "shrine_maidens_guard")
    _play(st, "kitsune_guile")                   # Tenko
    for _ in range(3):
        Y.turn_end(st)
    reasons = [r["reason"] for r in _acts(st)]
    assert reasons == ["tenko", "turn_end", "turn_end", "turn_end", "bloom"]
    assert not _led(st).sakura


def test_tenko_is_one_action_per_sakura_and_refreshes_to_three():
    st = _state(n=2)
    _play(st, "yakan_evocation")
    _play(st, "foxfire_sweep")
    _play(st, "shrine_maidens_guard")
    for s in _led(st).sakura:
        s.turns_left = 1
    _led(st).sakura[0].turns_left = 5            # never shortened
    mark = len(_acts(st))
    _play(st, "thunder_rite")
    assert len(_acts(st)) - mark == 3            # one action each
    assert [s.turns_left for s in _led(st).sakura] == [5, 3, 3]


def test_kitsune_guile_tenkos_and_manuscript_pile_draws_then_edits():
    st = _state()
    Y.plant(st, 1)          # the draft pass: Yakan Evocation strikes now
    _play(st, "kitsune_guile")
    assert int(st.enemies[0].powers.get("weak", 0)) == 2
    assert _acts(st, "tenko")
    st.player.draw_pile = [_card("defend") for _ in range(3)]
    turns = _led(st).sakura[0].turns_left
    _play(st, "manuscript_pile")
    # Yae review r6 item 2: no Sakura extension; it draws, then Edits a
    # drawn card with Red Ink.
    assert _led(st).sakura[0].turns_left == turns
    assert len(_acts(st)) == 1                   # no Tenko on it any more
    assert [Y.temp(c) for c in st.player.hand].count(Y.RED_INK) == 1


# --- full shrine, by kind ----------------------------------------------------

def test_full_shrine_same_kind_levels_the_oldest_after_it_acts():
    st = _state()
    Y.plant(st, 3)
    _led(st).sakura[0].turns_left = 1
    Y.plant(st, 1)
    assert [s.kind for s in _led(st).sakura] == [Y.THUNDER] * 3
    assert [s.level for s in _led(st).sakura] == [2, 1, 1]
    assert _led(st).sakura[0].turns_left == Y.SAKURA_TURNS
    assert [r["reason"] for r in _acts(st)] == ["full_shrine"]


def test_full_shrine_another_kind_withers_the_oldest_and_takes_its_place():
    st = _state()
    Y.plant(st, 3)
    Y.level_up(st, 4)                            # an established shrine
    _play(st, "shrine_maidens_guard")
    assert [s.kind for s in _led(st).sakura] == [Y.THUNDER, Y.THUNDER,
                                                 Y.KITSUNE]
    # The Sakura Levels paper (2026-10-17, pick 1 (a)): the replaced
    # Sakura's Level 5 carries over to the Kitsune Sakura taking its place.
    assert [s.level for s in _led(st).sakura] == [5, 5, 5]
    assert _led(st).sakura[-1].planted_level == 5
    assert [r["reason"] for r in _acts(st)] == ["full_shrine"]
    assert any(r["event"] == "yae_wither" and r.get("reason") == "replaced"
               for r in st.log)


def test_a_replacement_honours_mooncall_and_red_ink():
    st = _state()
    _play(st, "foxs_mooncall")                   # planted 1 higher
    Y.plant(st, 3, kind=Y.KITSUNE)
    evo = _card("yakan_evocation")
    Y.annotate(st, evo, Y.RED_INK)
    _play(st, evo)
    new = _led(st).sakura[-1]
    assert new.kind == Y.THUNDER and new.level == 2
    assert new.annotations == [Y.RED_INK] and new.planted_level == 2


def test_a_planted_level_is_kept_so_the_display_can_say_the_rest():
    st = _state()
    Y.plant(st, 1, level=3)
    _play(st, "narukami_ray")
    s = _led(st).sakura[0]
    assert (s.planted_level, s.level) == (3, 4)


# ===========================================================================
# 2. The Masterpiece
# ===========================================================================

def test_stacked_red_ink_adds_three_each_and_a_temporary_layer_on_top():
    st = _state()
    strike = _published("strike", [Y.RED_INK, Y.RED_INK])
    assert strike.enchant_damage == 6
    _play(st, strike)
    assert st.enemies[0].hp == 100 - 12
    Y.annotate(st, strike, Y.RED_INK)            # the temporary slot: +3 more
    _play(st, strike)
    assert st.enemies[0].hp == 100 - 12 - 15


def test_stacked_riders_each_fire():
    st = _state(n=2)
    c = _published("strike", [Y.SAKURA_SEAL, Y.SAKURA_SEAL, Y.FOOTNOTE,
                              Y.ROYALTIES])
    Y.annotate(st, c, Y.ROYALTIES)
    st.player.draw_pile = [_card("defend") for _ in range(3)]
    st.player.hand.append(c)
    st.player.energy = 5
    combat.play_card(st, c)
    assert len(_led(st).sakura) == 2             # Sakura Seal x2
    assert sum(1 for x in st.player.hand if x.id == "defend") == 1
    assert st.player.energy == 5 - 1 + 2         # Royalties x2


def test_an_edit_fills_the_temporary_slot_and_a_later_one_replaces_it():
    st = _state()
    c = _published("strike", [Y.REPRINT])
    st.player.hand.append(c)
    Y.annotate(st, c, Y.DEADLINE)        # Cliffhanger's Edit went 2026-10-19
    assert Y.stack(c) == [Y.REPRINT] and Y.temp(c) == Y.DEADLINE and c.retain
    _play(st, "footnote")
    assert Y.stack(c) == [Y.REPRINT] and Y.temp(c) == Y.FOOTNOTE
    assert not c.retain


def test_repeated_proofreads_cannot_pile_up_reprints_in_one_fight():
    st = _state()
    c = _card("strike")
    st.player.hand.append(c)
    for _ in range(3):
        _play(st, "proofread")
    assert Y.count(c, Y.REPRINT) == 1


def test_publish_moves_the_temporary_layer_onto_the_stack_once():
    st = _state()
    c = _card("strike")
    c.ym_slot = 3
    st.player.hand.append(c)
    _play(st, "footnote")
    assert Y.publish_card(st, c) == Y.FOOTNOTE
    assert Y.stack(c) == [Y.FOOTNOTE] and Y.temp(c) is None
    assert Y.publish_card(st, c) is None         # nothing left to move
    assert 3 not in _led(st).drafts


def test_the_seven_glamours_adds_to_an_existing_stack():
    st = _state()
    c = _published("strike", [Y.RED_INK])
    st.player.hand.append(c)
    _play(st, "margin_note")                     # Red Ink, temporary
    st.enemies[0].hp = 1                         # its kill (2026-10-15)
    _play(st, "the_seven_glamours")
    assert Y.stack(c) == [Y.RED_INK, Y.RED_INK]


def test_the_after_elite_publish_stacks_on_a_published_card():
    published = {0: [Y.REPRINT]}
    out = Y.publish_after_fight("elite", {0: Y.REPRINT}, published)
    assert out == [(0, Y.REPRINT)] and published == {0: [Y.REPRINT, Y.REPRINT]}
    Y.publish_after_fight("boss", {0: Y.SAKURA_SEAL}, published)
    assert published == {0: [Y.REPRINT, Y.REPRINT, Y.SAKURA_SEAL]}


def test_a_draft_is_the_temporary_layer_only():
    st = _state()
    c = _published("strike", [Y.RED_INK])
    c.ym_slot = 4
    st.player.hand.append(c)
    Y.turn_end(st)
    assert 4 not in _led(st).drafts              # the stack is not evidence
    _play(st, "footnote")
    Y.turn_end(st)
    assert _led(st).drafts[4] == Y.FOOTNOTE


# --- Reprint, exactly ---------------------------------------------------------

def _dealt(st):
    return 100 - st.enemies[0].hp


def test_two_stacked_reprints_replay_twice_on_the_first_play_then_go_inert():
    st = _state()
    c = _published("strike", [Y.REPRINT, Y.REPRINT])
    _play(st, c)
    assert _dealt(st) == 3 * 6
    _play(st, c)
    assert _dealt(st) == 4 * 6


def test_a_temporary_reprint_on_the_first_play_adds_one_to_the_stacks():
    st = _state()
    c = _published("strike", [Y.REPRINT])
    Y.annotate(st, c, Y.REPRINT)
    _play(st, c)
    assert _dealt(st) == 3 * 6                   # once + stack 1 + temp 1


def test_a_new_temporary_reprint_arms_one_fresh_replay():
    st = _state()
    c = _published("strike", [Y.REPRINT, Y.REPRINT])
    _play(st, c)                                 # 3 plays
    Y.annotate(st, c, Y.REPRINT)
    _play(st, c)                                 # 2 plays, not 4
    assert _dealt(st) == 5 * 6
    _play(st, c)
    assert _dealt(st) == 6 * 6


def test_publishing_an_armed_reprint_before_the_first_play_counts_it_once():
    st = _state()
    c = _card("strike")
    st.player.hand.append(c)
    _play(st, "proofread")
    Y.publish_card(st, c)
    assert Y.stack(c) == [Y.REPRINT]
    _play(st, c)
    assert _dealt(st) == 2 * 6


def test_publishing_after_the_first_play_keeps_the_armed_replay():
    st = _state()
    c = _card("strike")
    _play(st, c)                                 # played once, plain
    Y.annotate(st, c, Y.REPRINT)
    Y.publish_card(st, c)
    _play(st, c)
    assert _dealt(st) == 6 + 2 * 6


def test_reprint_used_reads_spent():
    st = _state()
    c = _published("strike", [Y.REPRINT])
    assert not Y.reprint_used(st, c)
    _play(st, c)
    assert Y.reprint_used(st, c)
    Y.annotate(st, c, Y.REPRINT)
    assert not Y.reprint_used(st, c)


# --- the readers of an Annotation, with layers ---------------------------------

def test_bestseller_does_not_count_a_published_only_card():
    # Yae review r5, pick 1 (a) (ruled 2026-10-15): they count the cards
    # Edited this combat, and a Published card in hand is not an Edit.
    st = _state()
    st.player.hand.append(_published("strike", [Y.REPRINT]))
    _play(st, "bestseller")                      # 8 + 2 x 0
    assert st.enemies[0].hp == 100 - 8


def test_serialization_no_longer_pays_on_a_published_card_play():
    # Yae review r6 item 1: it pays per Edit; playing an Annotated card is
    # not an Edit.
    st = _state()
    _play(st, "serialization")
    st.player.block = 0
    _play(st, _published("strike", [Y.FOOTNOTE]))
    assert st.player.block == 0


def test_editor_in_chief_makes_the_highest_act_as_its_kind():
    st = _state()
    _play(st, "editor_in_chief")
    _play(st, "shrine_maidens_guard")
    Y.level_up(st, 2)
    st.player.block = 0
    c = _card("strike")
    Y.annotate(st, c, Y.FOOTNOTE)
    _play(st, c)
    assert st.player.block == 2 + 3              # the Kitsune acted


def test_the_dead_edit_filter_still_reads_the_card():
    st = _state()
    lure = _card("foxfire_lure")
    st.player.hand.append(lure)
    _play(st, "margin_note")
    assert not Y.is_annotated(lure)


def test_stacked_red_ink_passes_to_a_sakura_once():
    st = _state()
    _play(st, _published("yakan_evocation", [Y.RED_INK, Y.RED_INK]))
    s = _led(st).sakura[0]
    assert s.annotations == [Y.RED_INK] and Y.act_size(st, s) == 2 + 1 + 3


# ===========================================================================
# 3. The signature cards
# ===========================================================================

def test_second_printing_puts_an_annotated_card_from_the_discard_in_hand():
    st = _state()
    plain, pub = _card("strike"), _published("defend", [Y.FOOTNOTE])
    st.player.discard_pile += [plain, pub]
    _play(st, "second_printing")
    assert pub in st.player.hand and plain in st.player.discard_pile
    assert not pub.free_this_turn


def test_second_printing_plus_makes_it_cost_zero_this_turn():
    st = _state()
    pub = _card("defend")
    Y.annotate(st, pub, Y.REPRINT)
    st.player.discard_pile.append(pub)
    _play(st, loader.get_card(_ym("second_printing") + "+"))
    assert pub in st.player.hand and pub.free_this_turn


def test_second_printing_with_nothing_annotated_does_nothing():
    st = _state()
    st.player.discard_pile.append(_card("strike"))
    hand = len(st.player.hand)
    _play(st, "second_printing")
    assert len(st.player.hand) == hand


def test_authors_copy_keeps_every_layer_and_arms_its_reprints():
    st = _state()
    c = _published("strike", [Y.REPRINT, Y.RED_INK])
    c.ym_slot = 0
    _play(st, c)                                 # the original: spent
    st.player.hand.append(c)
    _play(st, "authors_copy")
    copies = [x for x in st.player.hand if x.id == "strike" and x is not c]
    assert len(copies) == 1
    copy = copies[0]
    assert Y.stack(copy) == [Y.REPRINT, Y.RED_INK] and copy.ym_slot is None
    hp = st.enemies[0].hp
    _play(st, copy)
    assert hp - st.enemies[0].hp == 2 * (6 + 3)  # a copy's Reprint is armed


def test_authors_copy_never_copies_an_authors_copy():
    st = _state()
    other = _card("authors_copy")
    Y.annotate(st, other, Y.ROYALTIES)
    st.player.hand.append(other)
    assert Y.copy_candidates(st, _card("authors_copy")) == []


def test_the_authors_copy_royalties_loop_is_impossible():
    """GPT's loop: an Author's Copy+ Annotated with Royalties, copied by
    another Author's Copy, made a 0-cost copy that copies the original
    again, for +1 Energy each time. LAW forbids energy-positive copy loops.
    With the ban each Author's Copy finds nothing to copy and Energy never
    rises."""
    st = _state()
    royal = loader.get_card(_ym("authors_copy") + "+")
    Y.annotate(st, royal, Y.ROYALTIES)
    st.player.hand.append(royal)
    st.player.energy = 3
    for _ in range(5):
        ac = loader.get_card(_ym("authors_copy") + "+")
        st.player.hand.append(ac)
        before = len(st.player.hand)
        combat.play_card(st, ac)
        assert len(st.player.hand) == before - 1   # it made nothing
    assert st.player.energy == 3
    assert [c for c in st.player.hand
            if c.id.startswith(Y.AUTHORS_COPY_ID)] == [royal]


def test_serial_novel_returns_a_random_annotated_card_each_turn_start():
    st = _state()
    _play(st, "serial_novel")
    a, plain = _card("strike"), _card("defend")
    Y.annotate(st, a, Y.FOOTNOTE)
    st.player.discard_pile += [a, plain]
    st.player.hand = []
    Y.turn_start(st)
    assert st.player.hand == [a] and plain in st.player.discard_pile
    Y.turn_start(st)                             # nothing Annotated left
    assert st.player.hand == [a]


# ===========================================================================
# 4. Fallen Petals
# ===========================================================================

def test_fallen_petals_withers_even_a_deadline_extension_sakura():
    st = _state()
    Y.plant(st, 1)          # the draft pass: Yakan Evocation strikes now
    _play(st, "evergreen_charm")                 # Deadline Extension
    st.player.energy = 0
    c = _card("fallen_petals")
    st.player.hand.append(c)
    combat.play_card(st, c)
    assert not _led(st).sakura and st.player.energy == 1
    assert [r["reason"] for r in _acts(st)] == ["bloom"]


def test_the_new_rows_load_with_their_paper_costs():
    sp, ac, sn, fp = (_card(n) for n in ("second_printing", "authors_copy",
                                          "serial_novel", "fallen_petals"))
    assert (sp.cost, sp.type, sp.rarity, sp.exhaust) == (0, "skill", "uncommon", True)
    assert (ac.cost, ac.type, ac.rarity, ac.exhaust) == (1, "skill", "uncommon", True)
    assert loader.get_card(_ym("authors_copy") + "+").cost == 0
    assert (sn.cost, sn.type, sn.rarity) == (2, "power", "rare")
    assert loader.get_card(_ym("serial_novel") + "+").cost == 1
    assert (fp.cost, fp.type, fp.rarity) == (0, "skill", "uncommon")

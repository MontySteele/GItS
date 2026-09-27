"""The second base-game control round of 2026-09-26: Ironclad, Silent, Defect
and Necrobinder played whole runs through the design-blind page again, and
these are the page's and the bridge's own defects they found.

Each test names the seat and the finding. Records: the main checkout's
`review/qa/seats-2026-09-26/control2-lane{1,2,3,4}.md` (gitignored).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from understudy import blindplay, blindplay_session, lanewatch

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _fresh_run_ledger():
    blindplay.forget_run()
    yield
    blindplay.forget_run()


def _combat(character="Ironclad", enemies=None, status=(), **player) -> dict:
    state = {"state_type": "monster",
             "player": {"character": character, "hp": 60, "max_hp": 80,
                        "block": 0, "energy": 3, "max_energy": 3, "hand": [],
                        "potions": [], "relics": [], "status": list(status),
                        "draw_pile_count": 5, "discard_pile_count": 0,
                        "exhaust_pile_count": 0},
             "battle": {"round": 2, "enemies": enemies or [
                 {"entity_id": "SEAPUNK", "combat_id": 1, "name": "Seapunk",
                  "hp": 30, "max_hp": 44, "block": 0,
                  "intents": [{"type": "Attack", "damage": 5}],
                  "status": []}]}}
    state["player"].update(player)
    return state


FOUL = {"id": "FOUL_POTION", "name": "Foul Potion", "slot": 0,
        "description": "Deal 12 damage to ALL players and enemies. Can be "
                       "thrown at the Merchant for 100 Gold instead.",
        "can_use_in_combat": True, "target_type": "TargetedNoCreature",
        "keywords": []}


def _shop(*potions) -> dict:
    return {"state_type": "shop",
            "player": {"character": "Ironclad", "hp": 51, "max_hp": 80,
                       "gold": 105, "potions": list(potions), "relics": []},
            "shop": {"can_proceed": True, "items": [
                {"index": 0, "category": "card_removal", "price": 100,
                 "is_stocked": True, "can_afford": True}]}}


# ------------------------------- Ironclad: Foul Potion at the Merchant --

def test_foul_potion_is_thrown_at_the_merchant_with_no_enemy_asked_for():
    """Ironclad (c): in the shop `use potion "Foul Potion"` was refused with
    "there is more than one enemy, so say which". Out of a fight the game
    aims it at the Merchant (`TargetedNoCreature`), so nothing is sent."""
    res = blindplay.act(_shop(FOUL), 'use potion "Foul Potion"')
    assert res["ok"], res["refusal"]
    assert res["post"] == {"action": "use_potion", "slot": 0}
    assert res["printed"]["target"] == "the Merchant"


def test_on_merchant_is_the_same_throw():
    """Ironclad (c): `on "Merchant"` was refused, "nothing here is called
    'Merchant'"."""
    res = blindplay.act(_shop(FOUL), 'use potion "Foul Potion" on "Merchant"')
    assert res["ok"], res["refusal"]
    assert "target" not in res["post"]


def test_aiming_foul_potion_at_anything_else_names_the_throw_that_works():
    res = blindplay.act(_shop(FOUL), 'use potion "Foul Potion" on "Nibbit"')
    assert not res["ok"]
    assert "thrown at the Merchant" in res["refusal"]
    assert 'use potion "Foul Potion"' in res["refusal"]


def test_the_bridge_closes_the_shelf_before_the_throw():
    """The game allows the throw only while the shelf is closed
    (`FoulPotion.GetFoulPotionMerchantTarget`), and the bridge opens it on
    every read. The use closes it first."""
    src = (REPO / "vendor" / "STS2_MCP" / "McpMod.Actions.cs").read_text(
        encoding="utf-8")
    use = src[src.index("ExecuteUsePotion(Player player"):]
    assert use.index("GitsCloseShelfForFoulPotion(player, potion);") < \
        use.index("PassesCustomUsabilityCheck")
    assert "NMerchantInventory.MethodName.Close" in src


# ---------------------------------- Ironclad, Silent: `use potion 1` --

def test_use_potion_takes_the_number_of_a_potion_on_the_belt():
    """Ironclad and Silent: `use potion 1` was refused with "no name given";
    only `drop potion` took a number."""
    block = {"id": "BLOCK_POTION", "name": "Block Potion", "slot": 1,
             "description": "Gain 12 Block.", "target_type": "Self"}
    state = _combat(potions=[FOUL, block])
    res = blindplay.act(state, "use potion 2")
    assert res["ok"], res["refusal"]
    assert res["post"]["slot"] == 1
    assert res["printed"]["potion"] == "Block Potion"


def test_use_potion_with_a_number_takes_its_enemy_too():
    fire = {"id": "FIRE_POTION", "name": "Fire Potion", "slot": 0,
            "description": "Deal 20 damage.", "target_type": "AnyEnemy"}
    res = blindplay.act(_combat(potions=[fire]),
                        'use potion 1 on "Seapunk"')
    assert res["ok"], res["refusal"]
    assert res["post"]["target"]


def test_a_number_past_the_belt_is_refused_with_the_count():
    res = blindplay.act(_combat(potions=[FOUL]), "use potion 3")
    assert not res["ok"]
    assert "no number 3 on your belt" in res["refusal"]


# ---------------------------------------- all four: the deck moved --

def _event(deck, gold=99, title="Reflections", **player) -> dict:
    blob = {"character": "Necrobinder", "hp": 80, "max_hp": 107, "gold": gold,
            "master_deck": [{"name": n, "description": t} for n, t in deck]}
    blob.update(player)
    return {"state_type": "event", "run": {"act": 3, "floor": 46},
            "player": blob,
            "event": {"event_id": "REFLECTIONS", "event_name": title,
                      "body": "Mirrors.", "options": [
                          {"index": 0, "title": "Proceed",
                           "is_proceed": True}]}}


def test_an_events_upgrades_and_downgrades_are_named():
    """Necrobinder: "Floor 46's Reflections event had silently downgraded
    Reap+ and Scourge+. I learned it only by diffing the deck list." One
    event screen, before and after the choice."""
    blindplay.observe(_event([("Reap+", ""), ("Scourge+", ""),
                              ("Strike", "")]))
    page = blindplay.observe(_event([("Reap", ""), ("Scourge", ""),
                                     ("Strike+", "")]))
    assert "- In your deck, **Reap+** became **Reap**." in page
    assert "- In your deck, **Scourge+** became **Scourge**." in page
    assert "- In your deck, **Strike** became **Strike+**." in page


def test_a_transform_names_what_left_and_what_joined():
    """Defect, Silent: New Leaf turned a Strike into Fusion and Doubt became
    Spore Mind, and no screen said so."""
    blindplay.observe(_event([("Strike", ""), ("Doubt", "")]))
    page = blindplay.observe(_event([("Fusion", "Channel 1 Plasma."),
                                     ("Spore Mind", "Unplayable.")]))
    assert "- Joined your deck: **Fusion** — Channel 1 Plasma." in page
    assert "- Joined your deck: **Spore Mind** — Unplayable." in page
    assert "- Left your deck: **Strike**, **Doubt**" in page


def test_a_screen_that_moves_nothing_says_nothing():
    blindplay.observe(_event([("Strike", "")]))
    page = blindplay.observe(_event([("Strike", "")]))
    assert "## Since the screen before this one" not in page


# ------------------------------- Defect: chest gold; the fairy fired --

def _treasure(gold: int) -> dict:
    return {"state_type": "treasure", "run": {"act": 1, "floor": 9},
            "player": {"character": "Defect", "hp": 40, "max_hp": 75,
                       "gold": gold, "potions": [], "relics": []},
            "treasure": {"message": "Opening chest...", "can_proceed": False}}


def test_chest_gold_is_said():
    """Defect (c): "Treasure chest gold was never itemized (55 -> 101)." The
    chest pays on the same screen it opens on."""
    blindplay.observe(_treasure(55))
    page = blindplay.observe(_treasure(101))
    assert "- Gold 55 → 101, up 46" in page


def test_a_potion_only_the_game_uses_is_said_when_it_goes():
    """Defect, fight 25 turn 8: "nothing printed that the Fairy had fired".
    The wire marks a potion the player cannot use (`can_use_in_combat`
    false: its use is automatic)."""
    fairy = {"id": "FAIRY_IN_A_BOTTLE", "name": "Fairy in a Bottle",
             "slot": 0, "description": "When your HP would be reduced to 0, "
                                       "heal to 30% of your Max HP.",
             "can_use_in_combat": False, "target_type": "Self"}
    before = _combat("Defect", potions=[fairy])
    blindplay.observe(before)
    after = _combat("Defect", potions=[], hp=3)
    after["battle"]["round"] = 3
    page = blindplay.observe(after)
    assert ("- **Fairy in a Bottle** left your belt. You never use it "
            "yourself: the game uses it when its text comes true.") in page


def test_a_potion_the_seat_drank_is_not_said():
    fire = {"id": "FIRE_POTION", "name": "Fire Potion", "slot": 0,
            "description": "Deal 20 damage.", "can_use_in_combat": True,
            "target_type": "AnyEnemy"}
    blindplay.observe(_combat(potions=[fire]))
    after = _combat(potions=[])
    after["battle"]["round"] = 3
    assert "left your belt" not in blindplay.observe(after)


# --------------------------------------- Necrobinder: Pen Nib at 9 --

PEN_NIB = {"id": "PEN_NIB", "name": "Pen Nib", "counter": 9,
           "description": "Every 10th Attack you play deals double damage."}
STRIKE = {"id": "STRIKE", "name": "Strike", "cost": "1", "type": "Attack",
          "description": "Deal 12 damage.", "target_type": "AnyEnemy",
          "can_play": True}


def test_pen_nib_at_nine_gets_the_one_card_note():
    """Necrobinder, fight 15: "the hand printed doubled numbers on every
    attack, though only the first one played would be doubled"."""
    page = blindplay.observe(_combat("Necrobinder", relics=[PEN_NIB],
                                     hand=[STRIKE]))
    assert ("**Pen Nib** pays for ONE card: its own words are \"every 10th "
            "Attack you play deals double damage\"") in page


def test_pen_nib_short_of_nine_says_nothing():
    page = blindplay.observe(_combat("Necrobinder",
                                     relics=[dict(PEN_NIB, counter=5)],
                                     hand=[STRIKE]))
    assert "pays for ONE card" not in page


# ------------------------------------ Ironclad: the target's Vulnerable --

def test_an_enemys_vulnerable_says_the_hand_does_not_count_it():
    """Ironclad, fight 3: "Deal 3 damage twice" landed 5 and 5. A card's face
    is worked out with no target, and the wire has no per-target figure."""
    vuln = {"id": "VULNERABLE_POWER", "name": "Vulnerable", "amount": 1,
            "type": "Debuff", "description": "Takes 50% more damage."}
    enemy = {"entity_id": "SHRINKER", "combat_id": 1,
             "name": "Shrinker Beetle", "hp": 20, "max_hp": 40, "block": 0,
             "intents": [{"type": "Attack", "damage": 7}], "status": [vuln]}
    page = blindplay.observe(_combat(enemies=[enemy], hand=[STRIKE]))
    assert ("Vulnerable 1 (debuff) — Takes 50% more damage. The damage "
            "printed on your cards does not count this; it is added when a "
            "hit lands here.") in page


# ------------------------------------------ Defect: orbs and Vulnerable --

def test_the_vulnerable_gloss_says_orbs_are_not_boosted():
    """Defect, fight 7: "Tesla's own hit went 3 to 4 on the Vulnerable
    target, but the Lightning triggers stayed at 3." Orbs deal
    `ValueProp.Unpowered`, which Vulnerable ignores."""
    assert "Orb damage is not boosted." in blindplay.BASE_KEYWORDS[
        "Vulnerable"]


# ------------------------- Silent: Energy with no number; used-up relic --

def test_a_lone_energy_pip_is_one_energy():
    """Silent: "Tactician, Sidestep, Automation and Cure All printed 'Gain
    Energy' with no number." The game draws one pip for 1 Energy."""
    tactician = dict(STRIKE, name="Tactician", type="Skill",
                     description="Sly. Gain [silent_energy_icon.png].")
    page = blindplay.observe(_combat("Silent", hand=[tactician]))
    assert "Sly. Gain 1 Energy." in page


def test_a_pip_after_a_number_stays_that_numbers_unit():
    cocoa = dict(STRIKE, name="Cocoa", type="Skill",
                 description="Gain 4[silent_energy_icon.png]. Costs 0 "
                             "[silent_energy_icon.png].")
    page = blindplay.observe(_combat("Silent", hand=[cocoa]))
    assert "Gain 4 Energy. Costs 0 Energy." in page


def test_a_used_up_relic_says_so():
    """Silent: "the Tea relic line kept saying 'next combat' after it had
    fired". The bridge sends `RelicModel.IsUsedUp`."""
    tea = {"id": "TEA_OF_DISCOURTESY", "name": "Tea of Discourtesy",
           "description": "At the start of the next combat, shuffle 2 Dazed "
                          "into your Draw Pile.", "used_up": True}
    page = blindplay.observe(_combat("Silent", relics=[tea]))
    assert ("- **Tea of Discourtesy** (used up: it has done its job and does "
            "nothing more) — At the start") in page
    fresh = blindplay.observe(_combat("Silent", relics=[
        dict(tea, used_up=False)]))
    assert "used up" not in fresh


# ---------------------- Silent, Defect: the tip a power hangs on itself --

def test_a_powers_own_card_tip_is_not_glossed():
    """Silent: "the glossary said Piercing Wail -- lose 6 while the + version
    applied 8". Defect: "the Words entry for Hotfix says Exhaust while
    Hotfix+ was in hand". Both are the power's origin card, unupgraded
    (`TemporaryStrengthPower.ExtraHoverTips`)."""
    wail = {"id": "PIERCING_WAIL_POWER", "name": "Piercing Wail",
            "amount": -8, "type": "Debuff",
            "description": "Loses 8 Strength this turn.",
            "keywords": [{"name": "Piercing Wail",
                          "description": "ALL enemies lose 6 Strength this "
                                         "turn. Exhaust."},
                         {"name": "Strength",
                          "description": "THE GAME'S STRENGTH."}]}
    enemy = {"entity_id": "SCROLL", "combat_id": 1, "name": "Scroll of Biting",
             "hp": 30, "max_hp": 35, "block": 0,
             "intents": [{"type": "Attack", "damage": 6}], "status": [wail]}
    page = blindplay.observe(_combat("Silent", enemies=[enemy]))
    assert "lose 6 Strength" not in page
    assert "- **Strength** — THE GAME'S STRENGTH." in page


# --------------------------- Silent, Ironclad: words defined when offered --

def test_an_offered_relic_and_potion_define_their_words():
    """Silent: Vigor (Akabeko), Regen, Thorns, Royally Approved and Buffer
    "were defined only once active in combat". The game's own tip rides on
    the reward row (bridge) and the page glosses it there."""
    state = {"state_type": "rewards",
             "player": {"character": "Silent", "hp": 43, "max_hp": 70,
                        "gold": 99, "potions": [], "max_potion_slots": 3},
             "rewards": {"can_proceed": True, "items": [
                 {"index": 0, "type": "relic", "description": "Akabeko",
                  "relic_name": "Akabeko",
                  "relic_description": "At the start of each combat, gain 8 "
                                       "Vigor.",
                  "keywords": [{"name": "Vigor",
                                "description": "Your next Attack deals "
                                               "additional damage."}]},
                 {"index": 1, "type": "potion", "description": "Regen Potion",
                  "potion_name": "Regen Potion",
                  "potion_description": "Gain 5 Regen.",
                  "keywords": [{"name": "Regen",
                                "description": "Regen heals HP at the end of "
                                               "your turn."}]}]}}
    page = blindplay.observe(state)
    assert "- **Vigor** — Your next Attack deals additional damage." in page
    assert "- **Regen** — Regen heals HP at the end of your turn." in page


def test_a_belt_potion_defines_its_word_in_a_fight():
    tonic = {"id": "LUCKY_TONIC", "name": "Lucky Tonic", "slot": 0,
             "description": "Gain 1 Buffer.", "target_type": "Self",
             "keywords": [{"name": "Buffer",
                           "description": "Prevent the next time you would "
                                          "lose HP."}]}
    page = blindplay.observe(_combat("Silent", potions=[tonic]))
    assert "- **Buffer** — Prevent the next time you would lose HP." in page


def test_the_bridge_sends_the_reward_rows_tips():
    src = (REPO / "vendor" / "STS2_MCP" / "McpMod.StateBuilder.cs"
           ).read_text(encoding="utf-8")
    assert 'item["keywords"] = BuildHoverTips(potionReward.Potion' in src
    assert 'item["keywords"] = BuildHoverTips(relicReward.Relic' in src
    assert '["used_up"] = relic.IsUsedUp' in src


# ------------------------------ Ironclad: the hit log keeps the number --

def _nibbits(ids, resolutions=None) -> dict:
    enemies = [{"entity_id": f"NIBBIT_{i}", "combat_id": cid,
                "name": "Nibbit", "hp": 20, "max_hp": 46, "block": 0,
                "intents": [{"type": "Attack", "damage": 6}], "status": []}
               for i, cid in enumerate(ids)]
    state = _combat(enemies=enemies)
    if resolutions is not None:
        state["player"]["resolutions"] = resolutions
    return state


def test_the_hit_log_keeps_the_survivors_number():
    """Ironclad, fights 5 and 6: "The hit log renamed the survivor 'Nibbit
    (2)' to 'Nibbit', even on lines where Nibbit (1) was still alive." """
    blindplay.observe(_nibbits([1, 2]))
    rows = [{"card_id": "TWIN_STRIKE", "card": "Twin Strike",
             "auto_played": False, "carried": False, "overflowed": False,
             "summoned": [], "hits": [
                 {"target": "Nibbit", "amount": 5, "blocked": 0,
                  "combat_id": "2"},
                 {"target": "Nibbit", "amount": 20, "blocked": 0,
                  "combat_id": "1", "killed": True}]}]
    page = blindplay.observe(_nibbits([2], rows))
    assert "**Nibbit (2)** -- 5" in page
    assert "**Nibbit (2)** [B]" in page


# ------------------------------------ all four: the rest site's room --

def test_act_rides_out_a_room_that_is_not_open(monkeypatch, capsys):
    """Four seats: "ok" and "Rest site room is not open", and the rest did
    nothing until a retry. `act` now re-posts on that one sentence, bounded
    by the settle budget, as the session always has."""
    state = {"state_type": "rest_site",
             "player": {"hp": 30, "max_hp": 70},
             "rest_site": {"can_proceed": False, "options": [
                 {"index": 0, "name": "Rest", "is_enabled": True,
                  "description": "Heal 30% of your max HP."}]}}
    answers = [{"status": "error", "error": "Rest site room is not open"},
               {"status": "ok", "message": "Resting"}]
    posted: list = []

    def post(action, **params):
        posted.append(action)
        return answers[min(len(posted), len(answers)) - 1]

    monkeypatch.setattr(lanewatch, "guard", lambda *a, **k: "")
    monkeypatch.setattr(blindplay, "_live_load", lambda _a: state)
    monkeypatch.setattr(blindplay, "budget_spent", lambda *a, **k: (0, 0))
    monkeypatch.setattr(blindplay.bridge, "post", post)
    monkeypatch.setattr(blindplay_session.time, "sleep", lambda _s: None)
    assert blindplay.main(["act", "rest"]) == 0
    out = capsys.readouterr().out
    assert posted == ["choose_rest_option", "choose_rest_option"]
    assert "Resting" in out and "not open" not in out


def test_the_prompt_says_a_numbered_enemy_keeps_its_number():
    text = blindplay.PROMPT_PATH.read_text(encoding="utf-8")
    assert "an enemy that was\nnumbered earlier in the fight" in text


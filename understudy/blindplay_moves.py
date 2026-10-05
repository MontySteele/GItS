"""What a base-game enemy's debuff move does, by the move's own id (seat
page 3, 2026-10-05).

THE FIND. A live seat round read "Malicious (CardDebuff)" (Thieving Hopper
stealing a card), "Strategic (Debuff)" (Weak) and "Debuff" on a Flyconid
(Frail): the intent's hover tip names the KIND of move and never the power it
applies. The move itself is code in the game (a closure per monster), so the
wire cannot say; the bridge now sends the move's state id
(`MoveState.StateId`, e.g. `FRAIL_SPORES_MOVE`, the GItS local edit in
`vendor/STS2_MCP/McpMod.StateBuilder.cs`) and this table says what that move
does to you.

READ OFF THE GAME, NOT RECALLED. Every row was read from the 0.111.0
`sts2.dll` move bodies: the `PowerCmd.Apply` calls aimed at the player and
the status cards added to a pile, for every move whose telegraph carries a
Debuff, CardDebuff or StatusCard part. Facts only, as short phrases; no
decompiled text. A figure that rises at a higher Ascension is left out rather
than guessed at (none in this table do).

KEYED BY (base monster id, move id): the wire's `entity_id` with its ordinal
off (`blindplay_enemies.brief_key`) and `move_id`. A move this table does
not know prints nothing extra.
"""
from __future__ import annotations

from understudy.blindplay_enemies import brief_key

#: (monster id, move id) -> what the move does to you.
MOVE_EFFECTS: dict[tuple[str, str], str] = {
    ("AEONGLASS", "INCREASING_INTENSITY_MOVE"):
        "adds 1 Wither to your discard pile",
    ("AXEBOT", "HAMMER_UPPERCUT_MOVE"):
        "applies Weak 2; applies Frail 2",
    ("BOWLBUG_SILK", "TOXIC_SPIT_MOVE"):
        "applies Weak 1",
    ("CEREMONIAL_BEAST", "BEAST_CRY_MOVE"):
        "applies Ringing 1",
    ("CHOMPER", "SCREECH_MOVE"):
        "adds 3 Dazed to your discard pile",
    ("CORPSE_SLUG", "GOOP_MOVE"):
        "applies Frail 2",
    ("CRUSHER", "BUG_STING_MOVE"):
        "applies Weak 2; applies Frail 2",
    ("DECIMILLIPEDE_SEGMENT_BACK", "CONSTRICT_MOVE"):
        "applies Weak 1",
    ("DECIMILLIPEDE_SEGMENT_FRONT", "CONSTRICT_MOVE"):
        "applies Weak 1",
    ("DECIMILLIPEDE_SEGMENT_MIDDLE", "CONSTRICT_MOVE"):
        "applies Weak 1",
    ("EYE_WITH_TEETH", "DISTRACT_MOVE"):
        "adds 3 Dazed to your discard pile",
    ("FAKE_MERCHANT_MONSTER", "THROW_RELIC_MOVE"):
        "applies Frail 1",
    ("FLYCONID", "FRAIL_SPORES_MOVE"):
        "applies Frail 2",
    ("FLYCONID", "VULNERABLE_SPORES_MOVE"):
        "applies Vulnerable 2",
    ("FOSSIL_STALKER", "TACKLE_MOVE"):
        "applies Frail 1",
    ("FROG_KNIGHT", "TONGUE_LASH"):
        "applies Frail 2",
    ("GLOBE_HEAD", "SHOCKING_SLAP"):
        "applies Frail 2",
    ("GREMLIN_MERC", "DOUBLE_SMASH_MOVE"):
        "applies Weak 2",
    ("HAUNTED_SHIP", "HAUNT_MOVE"):
        "applies Weak 3; adds 5 Dazed to your discard pile",
    ("HUNTER_KILLER", "TENDERIZING_GOOP_MOVE"):
        "applies Tender 1",
    ("KIN_PRIEST", "ORB_OF_FRAILTY_MOVE"):
        "applies Frail 1",
    ("KIN_PRIEST", "ORB_OF_WEAKNESS_MOVE"):
        "applies Weak 1",
    ("KNOWLEDGE_DEMON", "CURSE_OF_KNOWLEDGE_MOVE"):
        "makes you pick one of two harmful cards, which take effect at once",
    ("LAGAVULIN_MATRIARCH", "SOUL_SIPHON_MOVE"):
        "you lose 2 Strength; you lose 2 Dexterity",
    ("LEAF_SLIME_M", "STICKY_SHOT"):
        "adds 2 Slimed to your discard pile",
    ("LEAF_SLIME_S", "GOOP_MOVE"):
        "adds 1 Slimed to your discard pile",
    ("LIVING_FOG", "ADVANCED_GAS_MOVE"):
        "applies Smoggy 1",
    ("LOUSE_PROGENITOR", "WEB_CANNON_MOVE"):
        "applies Frail 2",
    ("MAGI_KNIGHT", "DAMPEN_MOVE"):
        "applies Dampen: your upgraded cards are downgraded until it dies",
    ("MAWLER", "ROAR_MOVE"):
        "applies Vulnerable 3",
    ("MECHA_KNIGHT", "FLAMETHROWER_MOVE"):
        "adds 4 Burn to your hand",
    ("MYTE", "TOXIC_MOVE"):
        "adds 2 Toxic to your hand",
    ("NOISEBOT", "NOISE_MOVE"):
        "adds a Dazed to your discard pile and one to your draw pile",
    ("OVICOPTER", "TENDERIZER_MOVE"):
        "applies Vulnerable 2",
    ("OWL_MAGISTRATE", "VERDICT"):
        "applies Vulnerable 4",
    ("PHROG_PARASITE", "INFECT_MOVE"):
        "adds 3 Infection to your discard pile",
    ("PUNCH_CONSTRUCT", "FAST_PUNCH_MOVE"):
        "applies Frail 1",
    ("QUEEN", "PUPPET_STRINGS_MOVE"):
        "applies Chains of Binding 3",
    ("QUEEN", "YOU_ARE_MINE_MOVE"):
        "applies Frail 99; applies Weak 99; applies Vulnerable 99",
    ("SHRINKER_BEETLE", "SHRINKER_MOVE"):
        "applies Shrink",
    ("SLIMED_BERSERKER", "LEECHING_HUG_MOVE"):
        "applies Weak 3",
    ("SLIMED_BERSERKER", "VOMIT_ICHOR_MOVE"):
        "adds 10 Slimed to your discard pile",
    ("SLITHERING_STRANGLER", "CONSTRICT"):
        "applies Constrict 3",
    ("SLUDGE_SPINNER", "OIL_SPRAY_MOVE"):
        "applies Weak 1",
    ("SOUL_FYSH", "BECKON_MOVE"):
        "adds a Beckon to your draw pile and one to your discard pile",
    ("SOUL_FYSH", "GAZE_MOVE"):
        "adds a Beckon to your discard pile",
    ("SOUL_FYSH", "SCREAM_MOVE"):
        "applies Vulnerable 3",
    ("SOUL_NEXUS", "DRAIN_LIFE_MOVE"):
        "applies Vulnerable 2; applies Weak 2",
    ("SPECTRAL_KNIGHT", "HEX"):
        "applies Hex 2",
    ("STABBOT", "STAB_MOVE"):
        "applies Frail 1",
    ("TERROR_EEL", "TERROR_MOVE"):
        "applies Vulnerable 99",
    ("TEST_SUBJECT", "BURNING_GROWL_MOVE"):
        "adds 3 Burn to your discard pile",
    ("TEST_SUBJECT", "SKULL_BASH_MOVE"):
        "applies Vulnerable 1",
    ("THE_FORGOTTEN", "MIASMA"):
        "you lose 2 Dexterity",
    ("THE_INSATIABLE", "LIQUIFY_GROUND_MOVE"):
        "applies Sandpit 4 and adds 6 Frantic Escape, 3 to your draw pile and 3 to your discard pile",
    ("THE_LOST", "DEBILITATING_SMOG"):
        "you lose 2 Strength",
    ("THIEVING_HOPPER", "THIEVERY_MOVE"):
        "steals a card from your draw or discard pile",
    ("TRACKER_RUBY_RAIDER", "TRACK_MOVE"):
        "applies Frail 2",
    ("TWIG_SLIME_M", "STICKY_SHOT_MOVE"):
        "adds 1 Slimed to your discard pile",
    ("TWO_TAILED_RAT", "SCREECH_MOVE"):
        "applies Frail 1",
    ("VANTOM", "DISMEMBER_MOVE"):
        "adds 3 Wound to your discard pile",
    ("VINE_SHAMBLER", "GRASPING_VINES_MOVE"):
        "applies Tangled 1",
    ("WATERFALL_GIANT", "STOMP_MOVE"):
        "applies Weak 1",
    ("WRIGGLER", "WRIGGLE_MOVE"):
        "adds 1 Infection to your discard pile",
}

#: The intent kinds a move effect is printed beside: the parts whose own
#: hover tip names no power.
EFFECT_KINDS = frozenset({"debuff", "debuffstrong", "carddebuff",
                          "statuscard"})


def move_effect(entity_id: str, move_id: str) -> str:
    """What this body's telegraphed move does to you, or `""`."""
    return MOVE_EFFECTS.get((brief_key(entity_id),
                             str(move_id or "").strip().upper()), "")

"""What a base-game enemy does, in a line or three, for the first page of a
fight (2026-10-05, the seat-page pass).

WHY A TABLE. The wire sends each body's CURRENT telegraph and its powers'
hover text, and nothing about the move set behind them: a seat met the Kaiser
Crab with no way to know that killing one arm enrages the other, or that a
Decimillipede segment comes back. A sighted player has the bestiary and a
thousand hours; the page has this. The move loops are code in the game (a
state machine per monster), not data, so there is nothing on the wire or in
`game_ref/` to read them from, and the table is curated by hand from the base
-game behaviour notes in `docs/current/dossiers/enemies/` (themselves
paraphrase, never decompiled text). The powers' own wording stays where it
already prints, under each body.

BLINDNESS. Base-game knowledge is fair game for a seat; nothing here names a
mod card, a kit or a design word, and every line passes `qa_packet`'s scrub
(`tier0/tests/test_blindplay_enemy_brief.py`). FACTS ONLY: a move order, a
trigger, a cap. Never a recommended play.

COVERAGE IS PINNED. `ELITE_AND_BOSS_IDS` is every body of every act-1/2/3
elite and boss encounter in the shipped game (the `*Elite` / `*Boss`
encounter classes in `sts2.dll` 0.111.0), and the test fails on one without
an entry. A normal enemy is here only where its rule is invisible on the page
(Exoskeleton's damage cap) or an elite summons it (Wriggler).

KEYED BY THE WIRE'S `entity_id` with the trailing `_<n>` off
(`DECIMILLIPEDE_SEGMENT_FRONT_0` -> `DECIMILLIPEDE_SEGMENT_FRONT`), which is
the base monster's `Id.Entry` and survives a Teyvat dressing of its name.
"""
from __future__ import annotations

import re

_KAISER_RAGE = ("Crab Rage: when one arm dies, the other gains 6 Strength "
                "and 99 Block.")
_DECIMILLIPEDE = (
    "Three segments, each looping Writhe (two hits), Constrict (hit, then "
    "Weak) and Bulk (hit, then Strength), offset so each turn brings one of "
    "each. Reattach: a segment at 0 HP is down and untargetable for two "
    "turns, then returns at 25 HP; the fight ends only when all three are "
    "down at once.")
_KNIGHTS = "One of three Knights (Flail, Spectral, Magi) fought together."

#: entity id (no `_<n>`) -> (the base name, the briefing).
ENEMY_BRIEFS: dict[str, tuple[str, str]] = {
    # --- act 1 elites ---------------------------------------------------
    "BYGONE_EFFIGY": (
        "Bygone Effigy",
        "Sleeps on its first turn, wakes on the second with a large Strength "
        "gain and no attack, then uses Slash every turn. Slow: each card you "
        "play in a turn makes it take 10% more attack damage, reset each "
        "turn."),
    "BYRDONIS": (
        "Byrdonis",
        "Alternates Swoop and Peck (three hits). Territorial: it gains 1 "
        "Strength at the end of every round, with no cap."),
    "PHROG_PARASITE": (
        "Phrog Parasite",
        "Alternates Infect (3 Infection cards into your discard pile) and "
        "Lash (four hits). Infested: killing it does not end the fight; four "
        "stunned Wrigglers take its place. An Infection still in hand at the "
        "end of your turn hurts you."),
    "WRIGGLER": (
        "Wriggler",
        "Alternates Nasty Bite and Wriggle (an Infection card into your "
        "discard pile, and it gains 2 Strength); a pack of four splits two "
        "and two."),
    "SKULKING_COLONY": (
        "Skulking Colony",
        "Fixed loop: Zoom, Zoom, Inertia (hit, then permanent Strength), "
        "Piercing Stabs (two hits). Hardened Shell: it loses at most 20 HP "
        "per turn; damage past that is wasted."),
    "TERROR_EEL": (
        "Terror Eel",
        "Alternates Crash and Thrash (three hits, then Vigor for its next "
        "attack). Once, when unblocked damage leaves it at half HP or less, "
        "Shriek stuns it and Terror gives you permanent Vulnerable."),
    "PHANTASMAL_GARDENER": (
        "Phantasmal Gardener",
        "Four Gardeners on one loop, offset so each turn brings one Bite, "
        "Lash, Flail (three hits) and Enlarge (Strength). Skittish: the first "
        "attack card to damage one in a turn gives it 6 Block."),
    # --- act 1 bosses ---------------------------------------------------
    "CEREMONIAL_BEAST": (
        "Ceremonial Beast",
        "Stamp, then Plow every turn (hit, +2 Strength). When unblocked "
        "damage takes it to 150 HP or less it loses all Strength and is "
        "stunned once; then it loops Beast Cry (Ringing: you may play only "
        "one card next turn), Stomp, Crush (Strength)."),
    "KIN_PRIEST": (
        "Kin Priest",
        "Fixed loop: Orb of Frailty (hit, Frail), Orb of Weakness (hit, "
        "Weak), Soul Beam (three hits), Ritual (+2 Strength). Its two Kin "
        "Followers die when it dies; killing them does nothing to it."),
    "KIN_FOLLOWER": (
        "Kin Follower",
        "Fixed loop: Quick Slash, Boomerang (two hits), Power Dance "
        "(Strength); the two start one move apart. Both die when the Kin "
        "Priest dies."),
    "VANTOM": (
        "Vantom",
        "Fixed loop: Ink Blot, Inky Lance (two hits), Dismember (big hit, 3 "
        "Wounds into your discard pile), Prepare (+2 Strength). Slippery 8: "
        "each of the first 8 hits it takes deals exactly 1."),
    "SOUL_FYSH": (
        "Soul Fysh",
        "Fixed loop: Beckon, De Gas, Gaze, Fade (Intangible 2), Scream "
        "(Vulnerable). Beckon and Gaze add Beckon cards; one still in hand at "
        "the end of your turn costs 6 HP that Block does not stop."),
    "WATERFALL_GIANT": (
        "Waterfall Giant",
        "Pressurize, then loops Stomp (Weak), Ram, Siphon (heals), Pressure "
        "Gun, Pressure Up; every move adds to Steam Eruption. At 0 HP it "
        "cannot be hit, waits a turn, then Explodes for the stored total and "
        "dies."),
    # --- act 2 elites ---------------------------------------------------
    "DECIMILLIPEDE_SEGMENT_FRONT": ("Decimillipede", _DECIMILLIPEDE),
    "DECIMILLIPEDE_SEGMENT_MIDDLE": ("Decimillipede", _DECIMILLIPEDE),
    "DECIMILLIPEDE_SEGMENT_BACK": ("Decimillipede", _DECIMILLIPEDE),
    "ENTOMANCER": (
        "Entomancer",
        "Fixed loop: Bees (many small hits), Spear, Pheromone Spit "
        "(Strength). Personal Hive: every hit of an attack that damages it "
        "shuffles Dazed into your draw pile."),
    "INFESTED_PRISM": (
        "Infested Prism",
        "Fixed loop: Jab, Radiate (hit, Block), Whirlwind (three hits), "
        "Pulsate (hit, large Block, raises Vital Spark). Vital Spark makes "
        "your Skills Tainted: each one you play adds damage to its hits this "
        "turn."),
    # --- act 2 bosses ---------------------------------------------------
    "CRUSHER": (
        "Crusher",
        "Left arm of the Kaiser Crab, beside Rocket. Loop: Thrash, Enlarging "
        "Strike, Bug Sting (two hits, Weak, Frail), Adapt (Strength), Guarded "
        "Strike (hit, Block). " + _KAISER_RAGE),
    "ROCKET": (
        "Rocket",
        "Right arm of the Kaiser Crab, beside Crusher. Loop: Targeting "
        "Reticle, Precision Beam, Charge Up (Strength), Laser (its big hit), "
        "Recharge (nothing). " + _KAISER_RAGE),
    "KNOWLEDGE_DEMON": (
        "Knowledge Demon",
        "Curse of Knowledge, Slap, Knowledge Overwhelming (three hits), "
        "Ponder (hit, heals, Strength); the Curse comes again on turns 5 and "
        "9 only. Each Curse makes you pick one of two harmful cards, which "
        "take effect at once."),
    "LAGAVULIN_MATRIARCH": (
        "Lagavulin Matriarch",
        "Asleep behind Plating, which refills its Block each turn; it wakes "
        "after 3 turns, or early (stunned once, Plating gone) when unblocked "
        "damage hits it. Then loops Slash, Disembowel (two hits), Slash with "
        "Block, Soul Siphon (you lose Strength and Dexterity, it gains "
        "Strength)."),
    "THE_INSATIABLE": (
        "The Insatiable",
        "Turn 1 Liquify Ground: Sandpit 4 on you and six Frantic Escape "
        "cards. Sandpit drops by 1 each enemy turn and kills you at 0; each "
        "Frantic Escape played adds 1 back and costs 1 more next time. Then "
        "loops Thrash, Lunging Bite, Salivate (Strength), Thrash."),
    # --- act 3 elites ---------------------------------------------------
    "FLAIL_KNIGHT": (
        "Flail Knight",
        _KNIGHTS + " Opens with Ram, then picks among Ram, Flail (two hits) "
        "and War Chant (3 Strength); War Chant never twice in a row."),
    "SPECTRAL_KNIGHT": (
        "Spectral Knight",
        _KNIGHTS + " Opens with Hex (your cards become Ethereal until it "
        "dies), then Soul Slash, then Soul Slash or Soul Flame (three "
        "hits)."),
    "MAGI_KNIGHT": (
        "Magi Knight",
        _KNIGHTS + " Power Shield (hit, Block), Dampen (your upgraded cards "
        "are downgraded until it dies), then loops Ram, Prep (Block), Magic "
        "Bomb (one very large hit)."),
    "MECHA_KNIGHT": (
        "Mecha Knight",
        "Charge, then loops Flamethrower (4 Burns into your hand), Windup "
        "(Block, 5 Strength), Heavy Cleave (large hit). Starts with 3 "
        "Artifact: its first three debuffs are negated."),
    "SOUL_NEXUS": (
        "Soul Nexus",
        "Soul Burn first, then each turn one of the two moves it did not "
        "just use: Soul Burn, Maelstrom (four hits), Drain Life (hit, "
        "Vulnerable and Weak on you). It never gains Block."),
    # --- act 3 bosses ---------------------------------------------------
    "QUEEN": (
        "Queen",
        "Puppet Strings (Chains of Binding), You're Mine (Frail, Weak, "
        "Vulnerable), then Burn Bright For Me (allies +1 Strength, she gains "
        "Block); no damage while the Torch Head Amalgam lives. After it dies: "
        "Off With Your Head (five hits), Execution, Enrage (Strength)."),
    "TORCH_HEAD_AMALGAM": (
        "Torch Head Amalgam",
        "Tackle, Tackle, then loops Soul Beam (three hits), Weak Tackle, Weak "
        "Tackle. Every Burn Bright For Me from the Queen gives it Strength."),
    "TEST_SUBJECT": (
        "Test Subject",
        "Revives twice (Adaptable), each time spending a turn on Respawn. "
        "Form 1: Bite, Skull Bash (Vulnerable). Form 2: Multi Claw, one more "
        "hit each use, Wounds per unblocked hit. Form 3: Lacerate, Big "
        "Pounce, Burning Growl (Burns, Strength). Enrage: every Skill you "
        "play gives it Strength."),
    "AEONGLASS": (
        "Aeonglass",
        "Fixed loop: Ebb (hit, Block), Eye Lasers (two hits), Increasing "
        "Intensity (Strength; Wither cards into your discard pile, and every "
        "Wither grows). Wither hurts you at the end of your turn while in "
        "hand. Starts with 3 Artifact."),
    # --- normals whose rule the page cannot show -----------------------
    "EXOSKELETON": (
        "Exoskeleton",
        "Hard To Kill 9: no single hit takes more than 9 HP off it. Skitter "
        "(three 1-damage hits) is followed by Mandibles, and Mandibles by "
        "Enrage (permanent Strength)."),
}

#: Every body of every act-1/2/3 elite and boss encounter in the shipped game.
#: The pin fails on one with no entry above.
ELITE_AND_BOSS_IDS = frozenset({
    # elites
    "BYGONE_EFFIGY", "BYRDONIS", "PHROG_PARASITE", "WRIGGLER",
    "SKULKING_COLONY", "TERROR_EEL", "PHANTASMAL_GARDENER",
    "DECIMILLIPEDE_SEGMENT_FRONT", "DECIMILLIPEDE_SEGMENT_MIDDLE",
    "DECIMILLIPEDE_SEGMENT_BACK", "ENTOMANCER", "INFESTED_PRISM",
    "FLAIL_KNIGHT", "SPECTRAL_KNIGHT", "MAGI_KNIGHT", "MECHA_KNIGHT",
    "SOUL_NEXUS",
    # bosses
    "CEREMONIAL_BEAST", "KIN_PRIEST", "KIN_FOLLOWER", "VANTOM", "SOUL_FYSH",
    "WATERFALL_GIANT", "CRUSHER", "ROCKET", "KNOWLEDGE_DEMON",
    "LAGAVULIN_MATRIARCH", "THE_INSATIABLE", "QUEEN", "TORCH_HEAD_AMALGAM",
    "TEST_SUBJECT", "AEONGLASS",
})

_ORDINAL = re.compile(r"_\d+$")


def brief_key(entity_id: str) -> str:
    """`ROCKET_1` -> `ROCKET`; an id with no ordinal is its own key."""
    return _ORDINAL.sub("", str(entity_id or "").strip().upper())


def enemy_brief(entity_id: str) -> str:
    """The briefing for a body, or `""` where the table has none."""
    found = ENEMY_BRIEFS.get(brief_key(entity_id))
    return found[1] if found else ""


def brief_by_name(name: str) -> tuple[str, str] | None:
    """`(base name, briefing)` for a printed base name, for `--define`."""
    want = re.sub(r"\s*\(\d+\)$", "", str(name or "")).strip().casefold()
    for base, text in ENEMY_BRIEFS.values():
        if base.casefold() == want:
            return base, text
    return None

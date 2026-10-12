"""THE PLAN (`C.KOKOMI_OVERHAUL`) -- the sim twin of
`klee-mod/KleeCode/Powers/Prototype/KokomiPlan.cs`.

DRAFT 6's ONE RULE. The Bake-Kurage is on her side of the field for the whole
combat; a card with a `plan:` line can be played ON the jellyfish instead of
where it would normally go, its cost paid now, and at the start of her next
turn the jellyfish carries that line out. Ruled brief
`review/active/kokomi-brief-2026-09-01.md` draft 6 (direction R240, brief
R241); slice `review/active/kokomi-overhaul-slice-1-2026-09-01.md` draft 6.

THE C# IS THE SPEC, and where its prose and its code disagree the CODE is what
this file mirrors. Three places that matters, all recorded at their sites
below: the resolution HOOK (the slice's prose says "before the draw", the mod
resolves at `AfterPlayerTurnStart` and its header says why), and the Casket's
DEALER (the pet, so no Strength rides the 2).

A SEPARATE MODULE, not a section of `effects.py`, for the reason
`furina_reframe.py` is one: this is a whole rule with a queue, a resolution
point, four listeners and a relic, and `effects.py` is already the largest file
in the engine. The dependency runs ONE WAY at import time -- this module
imports nothing from `effects` at module scope and reaches it late, inside the
functions -- which is the same arrangement `loader` and `relics` already make.

NOTHING HERE IS REACHABLE WITH THE FLAG OFF. Every entry point returns on
`live()` before touching anything, `loader._card_prototype` refuses a
`proto_kk_` id with the flag off, and `tier0/tests/test_kokomi_overhaul.py`
pins the OFF arm as a whole-log digest. NOTHING MEASURED ON A PROTOTYPE ROW IS
QUOTABLE (R215 B): this is a rule made runnable, not a number about a game.
"""

from __future__ import annotations

from typing import Optional, Sequence

from tier0 import constants as C
from tier0.engine import coop, powers
from tier0.engine.state import Card, CombatState, Enemy, PlanEntry

# ---------------------------------------------------------------------------
# THE VOCABULARY -- the twins of `KokomiPlan.Kind` and `KokomiPlan.Aim`
# ---------------------------------------------------------------------------

#: What a `plan:` clause may say. The twin of `KokomiPlan.Kind`, spelled in
#: this engine's op names because that is the vocabulary the sheet writes and
#: `tools/gen_klee_cards.PLAN_CLAUSE_KINDS` maps the same spellings to the same
#: enum members. A clause outside this table is a LOAD failure on both sides --
#: never an approximation.
#:
#: `apply_power` is one op and two Kinds (ApplyWeak / ApplyVulnerable), which
#: is why the debuff table below is separate and closed: the jellyfish carries
#: out what the card wrote, and "any power" would let a row schedule a BUFF
#: onto an enemy through a typo.
#:
#: `EB-643` (R265) ADDED the drain-positional clauses, about the QUEUE rather
#: than about a number: two RIDERS on the entry that follows this one in the
#: same drain (`next_plan_double_damage`, `next_plan_extra_carry_out`). Scout
#: Ahead's draw counts left with the card (the hygiene pass, 2026-10-11). Both
#: riders are PLAN-ONLY by construction -- each names a position in a drain,
#: and a now-line spelling would name a drain that is not running.
PLAN_KINDS = frozenset((
    "draw", "energy", "block", "mend", "damage", "damage_quarter_max_hp",
    "apply_power",
    "play_copy_of_companion",
    "next_plan_double_damage", "next_plan_extra_carry_out",
    # `EB-655` (pool pass three), BATTLE PLAN. See `NEXT_ATTACK_BONUS`.
    # R276 PICK 1, THE HALVES REWRITE. See `FIRST_ATTACK_TWICE` and the four
    # beside it.
    "first_attack_twice",
    "block_front_intent",
    # THE CO-OP SET: Joint Orders' "They draw 2 cards" and Coordinated
    # Strike's "each other player's Attacks deal 3 additional damage". Both
    # are about ANOTHER player, and tier 0 seats one (`engine/coop.py`).
    "ally_draw", "others_attack_damage_this_turn",
    # POOL COMPLETION (2026-10-01), Tactical Relay: "Each player gains 1
    # Energy [and draws 1 card]". See `EACH_PLAYER_ENERGY`.
    "each_player_energy", "each_player_draw",
    # THE STATUS BATCH (2026-10-01): clauses that read the hand just drawn.
    # See `BLOCK_PER_STATUS_IN_HAND`.
    "block_per_status_in_hand", "transform_statuses_in_draw_pile",
    # THE RE-FOUNDING (2026-10-12): Kurage's Wake's Stings and Gorou's two
    # Plan lines. See `ADD_STINGS` and the two beside it.
    "add_stings", "strength_this_turn", "juuga_guard",
))

#: The clauses that carry NO `amount`. Each is a whole rule rather than a
#: number: Sango Isshin's quarter of Max HP is derived at carry-out, Crystal
#: Collapse's copy is a CARD rather than a size, and `EB-643`'s two riders are
#: switches thrown on the next entry -- "double" and "once more" have no size
#: to print. Named once because `plan_shape_reason` asks it twice and
#: `gen_klee_cards.plan_reason` asks the same question from the other side.
PLAN_AMOUNTLESS_OPS = frozenset((
    "damage_quarter_max_hp", "play_copy_of_companion",
    "next_plan_double_damage", "next_plan_extra_carry_out",
    # `EB-655`. Battle Plan prints "deals 4 additional damage"; the number is the
    # RULE's (`C.KOKOMI_OVERHAUL_BATTLE_PLAN_BONUS`) and not the clause's,
    # exactly as Rally's is, so the clause carries no `amount` for a sheet to
    # move.
    # R276. A switch: "your first Attack" has no size to print.
    "first_attack_twice",
    # THE STATUS BATCH: "every status and curse".
    "transform_statuses_in_draw_pile",
))

#: The two debuffs a Plan may apply. `KokomiPlan.PLAN_APPLY_POWERS`' twin.
PLAN_APPLY_POWERS = frozenset(("weak", "vulnerable"))

#: Where a clause lands (the `Aim` enum). Rule 3: "A planned hit lands on the
#: front enemy (leftmost alive) unless the line says every enemy." A
#: self-facing clause (draw, energy, Block, Mend, the doubling) names no
#: target at all, which is `Aim.Self`.
#:
#: `enemies_intending_attack` (`EB-492`, Flank) is the one aim that looks BACK:
#: the set is fixed when the Plan is WRITTEN, off the intents the player was
#: reading, and the carry-out lands on those of them still alive. See
#: `schedule`, which does the capture, and `_aimed`, which resolves it.
PLAN_AIMS = frozenset(("front_enemy", "all_enemies",
                       "enemies_intending_attack"))

#: The clauses that take an aim. Everything else is self-facing.
PLAN_AIMED_OPS = frozenset((
    "damage", "damage_quarter_max_hp",
    "apply_power"))

#: R276. The clauses whose `amount` may be zero: Tide Wall's is a flat bonus on
#: top of the front enemy's intent, and the base card prints none. THE FEED
#: PASS (2026-09-29) adds the flat `block`: Current Read's upgrade ADDS "Gain 2
#: Block" to its Plan, and no key adds a Plan clause, so the clause is written
#: at 0 and a 0 flat Block is carried out as nothing (Dexterity does not feed a
#: clause the face does not print).
PLAN_ZERO_AMOUNT_OPS = frozenset(("block_front_intent", "block",
                                 # POOL COMPLETION: Tactical Relay's draw is
                                 # written at 0 and added by the upgrade.
                                 "each_player_draw"))

#: The clauses a `times:` may repeat: the FLAT hit, and nothing else
#: (`EB-492`, Pincer's "Plan: Deal 3 damage three times"). The two scaled
#: damage kinds already derive their size from a count, and a debuff applied
#: twice in one beat is two stacks -- an `amount` -- rather than two
#: applications. `gen_klee_cards.PLAN_TIMES_OPS` is the twin.
PLAN_TIMES_OPS = frozenset(("damage",))

#: Legal inside a `plan:` list and NOWHERE else. A top-level spelling would be
#: a different, unpriced card, and this module is the only resolver of either.
#: `effects.OPS` still registers them -- the loader validates a `plan:` list
#: through the same vocabulary check the body takes -- and the registered
#: handler refuses, which is what makes "plan-only" true rather than intended.
PLAN_ONLY_OPS = frozenset((
                           "play_copy_of_companion",
                           # `EB-643`. The drain-positional clauses. Each
                           # one names a place in a running drain -- "the next
                           # Plan", "after this one" -- so a now-line spelling
                           # would ask about a drain that is not running and
                           # answer nothing, every time.
                           "next_plan_double_damage",
                           "next_plan_extra_carry_out",
                           # `EB-655`, BATTLE PLAN. The rider is what the
                           # carry-out pays: a now-line spelling would be a
                           # different, unpriced card that buffed an Attack on
                           # the turn it was played.
                           # R276. Each names the carry-out turn ("this
                           # turn", "the first ...") or the writing ("since
                           # you wrote this"), so a now-line spelling would be
                           # a different, unpriced card.
                           "first_attack_twice",
                           "block_front_intent",
                           # Kokomi core pass: "next turn" is the carry-out.
                           # THE CO-OP SET: the player is the one captured
                           # when the Plan was written, and "next turn" is the
                           # carry-out turn.
                           "ally_draw", "others_attack_damage_this_turn",
                           # POOL COMPLETION: Tactical Relay's two clauses
                           # name the carry-out turn for every player.
                           "each_player_energy", "each_player_draw",
                           # THE STATUS BATCH: each reads the hand just
                           # drawn, which only a Plan can see.
                           "block_per_status_in_hand",
                           "transform_statuses_in_draw_pile",
                           # THE RE-FOUNDING: each names the carry-out turn.
                           "add_stings", "strength_this_turn",
                           "juuga_guard"))

#: THE STATUS BATCH (2026-10-01, review/active/kokomi-status-batch-2026-10-01.md).
#: Kelp Wall's "plus 3 for each status or curse in your hand when written" and
#: Sea Glass Harvest's transform. THE KOKOMI ROUND-1 FIXES (2026-10-12): both
#: used to read the hand at carry-out, which seats found empty of the
#: statuses they wrote the Plan for. Kelp Wall now counts the hand WHEN THE
#: PLAN IS WRITTEN (`schedule` stamps `written_count` on the clause, the
#: number the face's preview showed) and Sea Glass Harvest transforms the
#: DRAW PILE, so the dead draws still to come convert.
#: `KokomiPlan.Kind.BlockPerStatusInHand` and the one beside it are the twins;
#: the bodies are `KokomiStatusBatch`.
BLOCK_PER_STATUS_IN_HAND = "block_per_status_in_hand"
TRANSFORM_STATUSES_IN_DRAW_PILE = "transform_statuses_in_draw_pile"
#: Sea Glass Harvest's token, in no pool. `SeaGlass.cs` is the twin.
SEA_GLASS = "kk_sea_glass"

#: POOL COMPLETION (2026-10-01), TACTICAL RELAY: "Plan: Each player gains 1
#: Energy [and draws 1 card]." Every player in the fight, Kokomi included.
#: Tier 0 seats one (`coop.other_players` is empty), so here they land on her
#: alone. `KokomiPlan.Kind.EachPlayerEnergy` / `EachPlayerDraw` are the twins.
EACH_PLAYER_ENERGY = "each_player_energy"
EACH_PLAYER_DRAW = "each_player_draw"

#: THE RE-FOUNDING (2026-10-12, review/active/kokomi-card-paper-2026-10-12.md).
#: Kurage's Wake's "Plan: Add 2 Stings to your hand"; Gorou's War Banner
#: "Plan: Gain 3 Strength this turn" (Flex's `temp_strength`) and Juuga "Plan:
#: For 3 turns, at the end of your turn gain 6 Block" (`amount` is the turns,
#: the Block is `C.MI_JUUGA_GUARD_BLOCK`); and a written Companion, whose one
#: clause holds the card (`carry_out_companion`). `KokomiPlan.Kind.AddStings`,
#: `StrengthThisTurn`, `JuugaGuard`, `PlayCompanion` are the twins.
ADD_STINGS = "add_stings"
STRENGTH_THIS_TURN = "strength_this_turn"
JUUGA_GUARD = "juuga_guard"
PLAY_COMPANION = "play_companion"
#: Juuga's Plan line's power on her: stacks are TURNS REMAINING.
MI_JUUGA_GUARD = "mi_juuga_guard"
#: The two jellyfish cards (card paper sec.1 rule 4), off-pool sheet rows.
STING_ID = "proto_kk_sting"
WARD_ID = "proto_kk_ward"
#: The nation the Commander's generators draw from.
GENERATED_NATION = "inazuma"
#: Call the Generals' "1 of 3".
GENERALS_OFFERED = C.KOKOMI_GENERALS_OFFERED

#: `EB-643`, OPENING GAMBIT: "the next Plan deals double damage", and SECOND
#: WAVE: "the next Plan is carried out twice".
#:
#: THE NEXT PLAN IS THE ENTRY CARRIED OUT IMMEDIATELY AFTER THIS ONE IN THE
#: SAME DRAIN, and if none follows the rider does nothing. Both are written by
#: the entry that prints them and consumed by the entry that follows, which is
#: why they live on the DRAIN (`_drain`) rather than on the state: a rider that
#: outlived its drain would be a promise about a morning nobody wrote it in.
#: `Change of Plans` neither sets nor consumes one -- `resolve_front` carries a
#: single entry out and there is no "next" for it to name.
#:
#: A FLAG AND NOT A COUNTER, both of them, and it is the pin: an entry carried
#: out TWICE under Nereid's Ascension prints its rider twice, and "the next
#: Plan is carried out twice" said twice is still twice -- so Second Wave under
#: the Ascension hands the next entry `CarryOutTimes + 1` = 3 rather than 4.
NEXT_PLAN_DOUBLE_DAMAGE = "next_plan_double_damage"
NEXT_PLAN_EXTRA_CARRY_OUT = "next_plan_extra_carry_out"

#: The one clause the SHEET cannot spell, minted by Moon's Reflection when the
#: card it reaches has no Plan line of its own. It never appears in a `plan:`
#: list (`plan_shape_reason` refuses it there), so it is kept out of
#: `PLAN_KINDS` and handled beside them.
REPLAY_EXHAUSTED = "replay_exhausted"

#: Crystal Collapse's clause (R236, the Inazuma workshop's one Personal). The
#: SHEET spells it, unlike `replay_exhausted` above, because the card prints
#: it: "Plan: play a copy of the last other Companion card you played this
#: turn." What it holds is decided when the Plan is WRITTEN and carried out at
#: the morning, which is the whole shape of the card -- see `schedule`.
PLAY_COPY_OF_COMPANION = "play_copy_of_companion"

#: Sango Isshin's divisor. An inline literal on BOTH sides -- the C# writes
#: `(int)kokomi.MaxHp / 4` in `KokomiRules.QuarterOfMaxHp` and holds no named
#: constant for it -- so it is NOT a `lint_constant_parity` row: that lint
#: compares NAMED C# members by value, and minting a name here that the mod
#: does not have would be a parity claim about nothing.
QUARTER = 4

#: The player-side powers this arm reads. Named here rather than spelled at
#: each site so the sheet's `power:` values and the readers cannot drift.
#: Every one of them is applied by an ordinary `apply_power` op off a card row.
#: Kokomi core pass (review/active/kokomi-core-pass-2026-09-27.md). TREATISE
#: draws N, once a turn, when a card with a Plan line is played NORMALLY (not
#: written on the Bake-Kurage): `note_face_up_plan_card`. `TreatisePower` is
#: the twin.
TREATISE = "kk_treatise"
#: R276: her Ancient under the arm, "Whenever the Bake-Kurage carries out a
#: Plan, gain N Block and draw 1 card." EVERY Plan, uncapped -- the card prints
#: "Whenever" and is the Dusty Tome's single grant. Applied by the second effect
#: on `princess_of_watatsumi` (`content/cards/ancients.yaml`);
#: `PrincessOfWatatsumiPlanPower` is the twin.
PRINCESS_OF_WATATSUMI = "kk_princess_of_watatsumi"
PRINCESS_OF_WATATSUMI_DRAW = 1
#: THE EXPANSION, BATCH ONE (2026-09-29). Twins in `KokomiExpansion.cs`. (The
#: Casket's Powers -- Grand Design's old marker, Flood Tide, The Long Game,
#: Kurage Swarm -- left with the re-founding, 2026-10-12.)
AT_WATERS_EDGE = "kk_at_waters_edge"      # first Hydro hit a turn: Weak N + Vuln N
CEREMONIAL_GARMENT = "kk_ceremonial_garment"  # +N per Weak/Vuln stack, Attacks
WATATSUMIS_GRACE = "kk_watatsumis_grace"  # keep up to N Block at turn end
TIDAL_RIPOSTE = "kk_tidal_riposte"        # N to an attacker fully Blocked
#: THE PAYOFF PASS (2026-10-01): Kurage Canopy, "Whenever the Bake-Kurage
#: carries out a Plan, gain N Block." Per carry-out, on the plan bus.
#: `KurageCanopyPower` is the twin.
KURAGE_CANOPY = "kk_kurage_canopy"
#: POOL COMPLETION (2026-10-01, paper sec.4). Sea's Reproach: "Whenever you
#: apply Weak or Vulnerable to an enemy, deal N damage to it." Watatsumi
#: Resistance (since the re-founding): "Whenever you write a Companion card as
#: a Plan, add a Sting to your hand." `SeasReproachPower`,
#: `WatatsumiResistancePower`.
SEAS_REPROACH = "kk_seas_reproach"
WATATSUMI_RESISTANCE = "kk_watatsumi_resistance"
#: THE RE-FOUNDING (2026-10-12): seven Powers. Twins in
#: `Powers/Prototype/KokomiRefounding.cs`.
SANGONOMIYAS_ORDERS = "kk_sangonomiyas_orders"   # turn start: N Companions
KURAGE_BLOOM = "kk_kurage_bloom"                 # turn start: N Stings
WATCHFUL_SHOAL = "kk_watchful_shoal"             # Ethereal written: N Block
COORDINATED_TIDE = "kk_coordinated_tide"         # Ethereal carried out: N
GRAND_STRATEGIST = "kk_grand_strategist"         # a Plan's reaction: N to ALL
ENDLESS_SHOAL = "kk_endless_shoal"               # Sting/Ward carried out: copy
DAWN_TIDE = "kk_dawn_tide"                       # turn start: Hydro to ALL
#: Nereid's Ascension (`EB-492`). A MARKER AND NOT A WINDOW: the Rare is a
#: Power costing 2 that lasts the fight, so there is no duration to tick and
#: `carry_out_times` reads only whether it is worn. It replaced a `plan_twice`
#: CLAUSE, which spent the very morning it was meant to pay for -- and that op
#: is retired rather than left standing with no row to spell it.
#: `NereidsAscensionPower` is the twin.
NEREIDS_ASCENSION = "kk_nereids_ascension"
#: R276 PICK 1. PINCER's carry-out: "This turn, your first Attack is played
#: twice." A SWITCH on the player, consumed by the first Attack played
#: FACE-UP (`spend_first_attack_twice`) and dropped at her turn's end. A card
#: written on the Bake-Kurage is not a play of its face, so it neither takes
#: nor spends it -- Battle Plan's old rider's rule. `FirstAttackTwicePower`.
FIRST_ATTACK_TWICE = "kk_first_attack_twice"
#: What counts as a debuff ON AN ENEMY in this engine, for the Casket and for
#: Undertow's `target_has_debuff`.
#:
#: A NAMED SET, and it is a READING. The C# asks the game's own
#: `PowerType.Debuff` classification (`KokomiOverhaulKit.IsHerDebuffOnEnemy`),
#: which tier0 does not have: `Fighter.powers` is `name -> int` with no type
#: beside it. So the list is written out, and it is the enemy-side debuffs
#: this engine can actually apply -- the three duration debuffs plus the two
#: damage-over-time stacks. AN AURA IS NOT ON IT, matching the mod, where
#: `AuraPower` is filed as a Buff.
ENEMY_DEBUFFS = frozenset(("weak", "vulnerable", "frail", "poison", "dot"))

#: FROZEN, the one debuff in this engine that is not a power. `Enemy.frozen` is
#: an int FIELD (NC-7's stacks-are-turns timer) and the mod's is a real
#: `PowerModel`, so it reaches neither `powers.apply_power` nor `Fighter.powers`
#: -- which would have made it invisible to an answer hung off that funnel.
#: The C# names it as a feeder in as many words ("so do REACTIONS, since
#: Superconduct, Overloaded and Frozen each apply a debuff"), so
#: `reactions.resolve_hit` raises the event by hand and `has_debuff` reads the
#: field. Two lines instead of a gap.
FROZEN = "frozen"

#: What an APPLICATION may be named. The standing-state set plus Frozen.
DEBUFF_APPLICATIONS = ENEMY_DEBUFFS | {FROZEN}


# ---------------------------------------------------------------------------
# SHAPE -- the loader's half of `gen_klee_cards.plan_reason`
# ---------------------------------------------------------------------------

def plan_shape_reason(clauses: Sequence[dict]) -> Optional[str]:
    """Why this `plan:` list is not a legal Plan line, or None.

    THE SAME CHECKS THE EMITTER MAKES, from this side. `plan_reason` in
    `tools/gen_klee_cards.py` BLOCKS a row it cannot type; this refuses a row
    it could not resolve, and the two lists are the same list on purpose -- a
    clause one side would refuse and the other approximated is exactly the
    divergence the quarantine exists to stop.

    Returns a sentence, not a bool, because the loader puts it in the raise
    and a sheet author reads it.
    """
    if not isinstance(clauses, list) or not clauses:
        return "`plan:` must be a non-empty list of effects"
    for eff in clauses:
        if not isinstance(eff, dict):
            return "`plan:` entries must be effect maps"
        op = eff.get("op")
        if op not in PLAN_KINDS:
            return (f"plan clause {op!r} is not one of the planned clauses "
                    f"{sorted(PLAN_KINDS)}")
        allowed = {"op"}
        if op not in PLAN_AMOUNTLESS_OPS:
            allowed.add("amount")
        if op in PLAN_AIMED_OPS:
            allowed.add("target")
        if op == "apply_power":
            allowed.add("power")
        if op in PLAN_TIMES_OPS:
            allowed.add("times")
        # The big-Plan pass (2026-10-04): "Strength affects this Plan N
        # times", on the flat hit only.
        if op == "damage":
            allowed.add("strength_times")
        if op == TRANSFORM_STATUSES_IN_DRAW_PILE:
            allowed.add("upgraded")      # the `upgraded_grant` key's flag
        unknown = set(eff) - allowed
        if unknown:
            return (f"plan clause {op} field(s) {sorted(unknown)} "
                    "not understood")
        if op not in PLAN_AMOUNTLESS_OPS:
            amount = eff.get("amount")
            # A LITERAL POSITIVE INT, the `spend_spark_amount` /
            # `block_at_turn_start_turns` precedent: a Plan's amount is read a
            # turn after it was written, so a formula resolved against combat
            # state would be printed text that means something different every
            # time it is carried out.
            floor = 0 if op in PLAN_ZERO_AMOUNT_OPS else 1
            if not isinstance(amount, int) or isinstance(amount, bool) \
                    or amount < floor:
                return f"plan clause {op} amount must be a positive literal int"
        if "strength_times" in eff:
            strength_times = eff["strength_times"]
            if not isinstance(strength_times, int)                     or isinstance(strength_times, bool) or strength_times < 2:
                return (f"plan clause {op} strength_times must be a literal "
                        "int of 2 or more")
        if "times" in eff:
            times = eff["times"]
            # A LITERAL, for `amount`'s reason one branch up: a Plan's repeat
            # count is read a turn after it was written.
            if not isinstance(times, int) or isinstance(times, bool)                     or times < 2:
                return (f"plan clause {op} times must be a literal int of 2 "
                        "or more")
        if op in PLAN_AIMED_OPS and eff.get("target") not in PLAN_AIMS:
            return (f"plan clause {op} target {eff.get('target')!r} -- a "
                    f"planned clause lands {sorted(PLAN_AIMS)}")
        if op == "apply_power" and eff.get("power") not in PLAN_APPLY_POWERS:
            return (f"plan clause apply_power power {eff.get('power')!r} is "
                    f"not one of {sorted(PLAN_APPLY_POWERS)}")
    return None


# ---------------------------------------------------------------------------
# THE GATE
# ---------------------------------------------------------------------------

def live(state: CombatState) -> bool:
    """The one gate: the flag is on and the seat IS Kokomi.

    `KokomiOverhaul.LiveFor`'s twin, and the character test is not decoration
    -- `_kokomi_memory_live` states the same argument one arm over. The queue,
    the pet aim and the Casket answer are all hers by construction, and a
    debuff-applying Furina must not start writing Plans.
    """
    return state.player.character_id == "kokomi"


# ---------------------------------------------------------------------------
# THE AIM -- and THE PET, which is a CHOICE here and a creature in the mod
# ---------------------------------------------------------------------------

def front_enemy(state: CombatState) -> Optional[Enemy]:
    """The front enemy: LEFTMOST ALIVE, SKIPPING A MINION (`R250`, round-5
    sec.6 pick 1 at its default).

    `CombatState.living_enemies` preserves `enemies` order, which is encounter
    slot order, so "leftmost" is the first living one and needs no second
    definition -- the same sentence `KokomiPlan.FrontEnemy` writes about
    `HittableEnemies`. Two round-5 formations put a Minion-flagged decoy
    there on purpose (The Kin's Followers, Queen's Torch Head Amalgam), so
    this reads `is_minion` -- the sim's own mirror of the game's
    `MinionPower` (state.py, NC-7 alpha) -- rather than inventing a second
    "secondary enemy" concept. Falls back to the leftmost Minion when the
    board is Minions alone, because a Plan that lands on nothing is worse
    than one that lands on the decoy.
    """
    living = state.living_enemies
    if not living:
        return None
    return next((e for e in living if not e.is_minion), living[0])


def _aimed(state: CombatState, clause: dict,
           entry: Optional[PlanEntry] = None) -> list[Enemy]:
    """The bodies one clause lands on, resolved AT CARRY-OUT. A clause with no
    `target` (a self-facing one) is empty by construction -- it names no target
    at all.

    THE WHOLE CLAUSE AND NOT JUST ITS AIM (`EB-492`), because one aim reads
    something the clause carries: `enemies_intending_attack` resolves the set
    `schedule` captured, filtered to the bodies STILL ALIVE. An enemy whose
    intent changed overnight is still in the set -- the set was the point --
    and one that died drops out, which is the same "a Plan that lands on
    nothing lands on nothing" rule every other aim already keeps.
    `KokomiPlan.Aimed` is the twin; it holds combat IDS where this holds the
    `Enemy` objects, because the game tears a dead creature down and this
    engine never does (`Enemy.alive` is a read of `hp`).
    """
    aim = clause.get("target")
    if aim == "all_enemies":
        return list(state.living_enemies)
    if aim == "enemies_intending_attack":
        caught = clause.get("targets") or []
        return [e for e in caught if e.alive]
    if aim == "front_enemy":
        # `EB-643`, CONVERGING TIDE. The one aim a now-line may re-point:
        # "every queued Plan aims at this enemy instead of the front". The
        # override is read ONLY WHILE THAT BODY IS ALIVE and falls back to the
        # front otherwise, which is the same "a Plan that lands on nothing
        # lands on nothing" rule every other aim already keeps -- and it is
        # deliberately not extended to `all_enemies` or to Flank's captured
        # set: neither of those aims at the front, so there is nothing on
        # either for "instead of the front" to be about.
        if entry is not None and entry.aim_override is not None \
                and entry.aim_override.alive:
            return [entry.aim_override]
        front = front_enemy(state)
        return [front] if front is not None else []
    return []


def carry_out_only(card: Card) -> bool:
    """Does this row do NOTHING while the jellyfish holds no Plan? (`EB-455`.)

    `gen_klee_cards.card_is_carry_out_only`'s twin, clause for clause: true
    when every top-level effect that is not a cost is a `carry_out_front_plan`.
    Such a card pays its energy, exhausts itself and resolves to nothing --
    `klee_overhaul.set_off_only`'s shape one mechanic over, and its argument.

    A carry-out sitting BESIDE another effect is not covered: a card that also
    draws still does something on an empty jellyfish.
    """
    rest = [fx for fx in card.effects
            if fx.get("op") not in ("spend_spark", "spend_charge")]
    if not rest:
        return False
    return all(fx.get("op") == "carry_out_front_plan" for fx in rest)


def refuses_for_no_plan(state: CombatState, card: Card) -> bool:
    """`card_playable`'s Plan clause: a carry-out-only card is unplayable while
    the Bake-Kurage holds no Plan (`EB-455`).

    The mod refuses it at `CardModel.IsPlayable` and prints the reason through
    `IUnplayableReasonCard` ("no Plan is written"); this is that refusal at
    this engine's twin seam, exactly as `klee_overhaul.refuses_for_no_bomb` is.
    """
    return live(state) and carry_out_only(card) and not state.kk_plan_queue


def plan_aimed_at_pet(state: CombatState, card: Card) -> bool:
    """WAS THIS PLAY AIMED AT THE JELLYFISH? -- and this engine's whole answer
    to "the pet as a target the pilot can choose".

    THE PET IS A CHOICE HERE AND A CREATURE IN THE MOD, deliberately. The mod
    puts a real Bake-Kurage on the field because a player needs something to
    drag a card onto and because the strip is drawn on it; `PlayedOnPet` then
    reduces the whole question to one line, "was `CardPlay.Target` the pet".
    Nothing in draft 6's rules reads the pet as a BODY -- enemies cannot touch
    it, it has no HP, it deals damage as her and its Plans resolve on a power
    that lives on HER (`ProtoBakeKuragePower`'s own header says why). So tier0
    models the pet as the targeting decision it is, and models it at the one
    place a play's aim is decided.

    THE RULE IS THE SIM'S, NOT A DESIGN CLAIM. Nothing on any sheet, in the
    brief or in the slice says when to plan; a human player decides, and this
    engine has no human. What it has is a pilot, and a pilot that never
    planned would report a Plan arm that never used its one rule. So:

        plan when the card's now-line is EMPTY (there is nothing to give up),
        or when NO living enemy intends to attack this turn (the delay is
        free).

    Both halves are the crude, legible version of the same judgement -- a Plan
    trades this turn for next turn, so take the trade when this turn is cheap.
    It is an INSTRUMENT SURFACE in `_worst_card`'s sense: every number this arm
    ever produces rides this function, so a policy replaces ONE function rather
    than N call sites, and no measurement taken through it may be quoted as a
    statement about the DESIGN (R215 B).

    PURE, and it has to be: `pilot.policy._active_effects` calls it to decide
    which half of a card's face to score, and `effects._resolve_card_bound`
    calls it to decide which half to run. A read with a side effect would make
    the pilot's forecast and the play disagree.

    `EB-347`: AN AUTO-PLAY NEVER AIMS AT THE PET. Uproar's random Attack wrote
    Slack Water onto the jellyfish as a Plan instead of playing it at the enemy
    (Kokomi r4d act 1 fight 3, and three unreported act-2 plays); the identical
    card pulled by the identical Uproar had gone at the enemy one fight
    earlier, so the screen contradicted itself. The pet is a DELIBERATE target
    -- the mod draws it so a player has something to drag a card onto -- and a
    free play has nobody at the mouse. Both auto-play doors are read: the
    base game's forced-random plays (Havoc, Cascade, Uproar, the on-exhaust
    sweep) through `force_random_targeting`, and the jellyfish's own replay
    through `kurage_autoplaying`. The C# twin is `KokomiPlan.PlayedOnPet`,
    which asks `cardPlay.IsAutoPlay` for the same reason.
    """
    if not live(state) or not can_be_written(card):
        return False
    # THE RE-FOUNDING (2026-10-12): Grand Design's free write is the one
    # auto-play that writes, because the card it plays was CHOSEN to be
    # written (`write_free`). `KokomiRefounding.IsFreeWrite` is the twin.
    if state.kk_free_write is card:
        return True
    if state.force_random_targeting or state.kurage_autoplaying:
        return False
    if not card.effects:
        return True
    return not any(_intends_to_attack(e) for e in state.living_enemies)


def writable_companion(card: Optional[Card]) -> bool:
    """A Companion card with no Plan line of its own: written, it is carried
    out at its printed rate (design pass pick 4 (a), ruled 2026-10-12).
    `IWritableCompanion` is the twin (the codegen stamps every Companion row
    with no `plan:`)."""
    return card is not None and card.is_companion and not card.plan


def can_be_written(card: Optional[Card]) -> bool:
    """Can this card be written as a Plan? A Plan line, or a Companion card.
    `KokomiRefounding.CanBeWritten` is the twin."""
    return card is not None and (bool(card.plan) or writable_companion(card))


def _intends_to_attack(enemy: Enemy) -> bool:
    """Is this enemy's CURRENT intent an attack? An enemy with no script at
    all (a hand-built fixture) intends nothing, which is the honest answer
    rather than a crash.

    THE ARM'S ONE INTENT READ since `EB-492`: the pilot's plan-or-play
    judgement (`plan_aimed_at_pet`) and Flank's captured set both ask it, and
    the shipped predicate `enemy_intends_attack` spells the same two clauses
    -- "intent kind is attack AND `sleep_turns` is zero". The sleep half was
    missing here while the predicate beside it had it; the C# needs only the
    first clause and says why (`CurtainCallHooks.IntendsAttack`), because a
    sleeping creature telegraphs a SleepIntent and fails the intent test on
    its own.
    """
    if not enemy.intents:
        return False
    return (enemy.current_intent().get("kind") == "attack"
            and enemy.sleep_turns == 0)


# ---------------------------------------------------------------------------
# WRITING A PLAN
# ---------------------------------------------------------------------------

def last_other_companion(state: CombatState,
                         card: Card) -> Optional[Card]:
    """"The last other Companion card you played this turn" -- Crystal
    Collapse's whole reading, and the ONE place it is decided.

    BY IDENTITY, not by id, and it has to be here rather than "the last entry
    of the list": `combat._finish_play` records a play BEFORE the card's body
    resolves, so by the time this card's Plan is written the card ITSELF is
    already the last thing on the list. "Other" is the word the face prints
    and this is where it is honoured; a second copy of Crystal Collapse played
    earlier in the same turn IS other, which is why the test is identity.

    THE C# NEEDS NO SUCH GUARD and keeps one anyway: there `AfterCardPlayed`
    fires after `OnPlay`, so the ledger's last-Companion is still the previous
    card when the Plan is written -- the same answer by a different route, and
    the identity test is what makes the two engines say so for the same
    reason rather than by accident.
    """
    for played in reversed(state.kk_companions_this_turn):
        if played is not card:
            return played
    return None


def plan_label(card: Card, held: Optional[Card]) -> str:
    """What the strip prints for a Plan that HOLDS a card.

    `KokomiPlan.Entry.Label`'s twin. An ordinary Plan's strip line is the
    writing card's name; this one has to say WHICH card it caught, because the
    same face means a different thing every time it is written and a player who
    cannot see the answer cannot plan around it.

    THE SHORT NAME IS THE HALF AFTER THE EM DASH. A companion row is named
    "<Character> — <Card>", so the strip prints "Crystal Collapse: ..." rather
    than repeating Gorou twice in one line. The HELD card keeps its whole name,
    which is what the player will see resolve.
    """
    short = card.name.split("—")[-1].strip() or card.name
    return f"{short}: {held.name if held is not None else 'nothing'}"


def plan_aimed_label(card: Card, caught: Sequence[Enemy]) -> str:
    """What the strip prints for a Plan that CAUGHT A SET (`EB-492`).

    `plan_label`'s argument one aim over, and `KokomiPlan.AimedLabel`'s twin: a
    Plan whose targets were decided when it was written means a different thing
    every time it is written, and a player who cannot see which bodies it
    caught cannot plan around it. "Flank: nothing" is the honest line for a
    Plan written into a board of Defends -- it is queued, it will fire, and it
    will hit no one.
    """
    if not caught:
        return f"{card.name}: nothing"
    return f"{card.name}: " + ", ".join(e.name for e in caught)


def _enchanted(card: Optional[Card], amount: int) -> int:
    """`EB-580`. THE CARD'S OWN ENCHANTMENT, FOLDED INTO ITS PLAN LINE.

    THE FIND (Kokomi r21 lane 2 (c) 3). A Sharp 2 raised Riptide's now-line
    from 9 to 11 and left its Plan line printing 13, with nothing on screen
    saying which of the two lines the enchantment had bought: the seat read
    the pair as evidence that the Plan had become the worse half, and it
    "silently reversed the right play on my best card". Ruled at the r21
    packet's D default -- a card's own enchantment applies to BOTH its lines,
    since both are the card's.

    WHY IT WAS MISSING RATHER THAN REFUSED. The rider is folded where a CARD
    deals damage (`effects` reads `enchant_damage` inside the `type ==
    "attack"` branch), and a planned clause is not a card being played
    (`EB-538`) -- so nothing on the path from the queue to the board had the
    card in its hand to ask. It is asked here, once, at writing time.

    THE ADDITIVE THEN THE MULTIPLIER, which is the order the card's own damage
    takes one file over (Sharp lands with the flat riders, Corrupted's x1.5
    multiplies the sum). `enchant_first_play_damage` (Vigorous) is DELIBERATELY
    NOT HERE and it is the one rider a Plan cannot carry: "the first time this
    card is PLAYED" is spent by the play that wrote the Plan, and paying it
    again at the morning would pay one printed rider twice.

    C# twin: `KokomiPlan.Enchanted`, which asks the base game's
    `EnchantDamageAdditive` / `EnchantDamageMultiplicative` for the same two
    terms in the same order.
    """
    if card is None or amount <= 0:
        return amount
    folded = amount + card.enchant_damage
    if card.enchant_damage_mult != 1.0:
        folded = int(folded * card.enchant_damage_mult)
    return int(folded)


def hers(state: CombatState, card: Optional[Card], amount: int,
         strength_times: int = 1) -> int:
    """`EB-599`. HER SIDE OF A PLAN LINE, FOLDED AT WRITING TIME.

    THE FIND (Kokomi r22 lane 2). `Kurage's Oath` printed "Plan: Deal 10"
    under the target's Vulnerable, the seat paid for it, and the morning
    carried out 7 once the Vulnerable had expired -- "for a mechanic sold on
    committing a turn early, the committed number moving is the sharpest
    contradiction in the kit". Both lanes then read the two lines computing
    under two rules: her Strength moved the own line only and the target's
    Vulnerable moved the Plan line only.

    THE RULE (r22 packet sec.5, a D default): the Plan line folds HERS -- her
    Strength and her enchantment -- and NOTHING of the target's. Rule 3 says
    her Strength counts for a carry-out, and a Plan resolves next morning
    against whatever the target wears THEN, so the target's terms are exactly
    the ones no line written today can honestly print.

    HER STRENGTH AND NOT `powers.modify_damage_dealt`, which is the one
    argument here and is deliberate: that funnel also carries her Weak, and
    round four-c's finding is what took her Weak off a carry-out ("a Strategic
    enemy's Weak cut two banked Plans to x0.75 the next morning"). The default
    names her Strength and her enchantments; this folds those two and no more.

    THE ENCHANTMENT FIRST, THEN THE STRENGTH, which is the order a card's own
    damage takes one file over: `effects` reads `enchant_damage` and
    `modify_damage_dealt` adds Strength after it.

    `strength_times` (the big-Plan pass, 2026-10-04) is the clause's own
    "Strength affects this Plan N times": Masterstroke 3, Surging Shoal 2.
    Flat Strength per hit paid a 0-cost Nip as much as a 3-Energy Plan, so
    the big Plans count it more than once. The enchantment still counts once.

    C# twin: `KokomiPlan.Hers`.
    """
    folded = _enchanted(card, amount)
    if folded <= 0:
        return folded
    return folded + (int(state.player.powers.get("strength", 0))
                     * max(1, int(strength_times)))


def schedule(state: CombatState, card: Card,
             clauses: Optional[Sequence[dict]] = None,
             replay: Optional[Card] = None,
             enchanted_by: Optional[Card] = None) -> None:
    """Write one Plan down: rule 2's whole engine side.

    `clauses` defaults to the card's own printed line and is passed explicitly
    only by Moon's Reflection, which contributes the line of a card it found in
    the exhaust pile. `replay` is that screen's other shape -- a chosen card
    with NO Plan line of its own, replayed whole.

    `enchanted_by` (`EB-580`) is WHOSE ENCHANTMENT FOLDS INTO THE LINE, and it
    defaults to the writing card because on every ordinary Plan they are the
    same card. Moon's Reflection is the one caller that separates them: the
    line belongs to the card it FOUND, so that copy's Sharp is the one on it,
    which is also the card `KokomiPlan.ScheduleFromExhaust` hands its own
    `source` parameter.

    A COMPANION WITH NO PLAN LINE (the re-founding, 2026-10-12) is written as
    one `play_companion` clause holding the card itself, carried out next turn
    at its printed rate after the Bake-Kurage applies Hydro to its target
    (`carry_out_companion`). `KokomiCompanionPlan.Write` is the twin.

    A PLAN IS ONLY EVER QUEUED HERE (`EB-570`). The Moon Overlooks the Waters
    used to carry the entry out on the spot as well -- "Plans also happen now"
    -- and the Rare deleted the kit's one question rather than answering it:
    rule 2 is the delay, and Battle Plan's Plan line is double its play line,
    so any now-copy took the price off waiting. The row is withdrawn and this
    door is the writing alone; `resolve_all` and `resolve_front` are the two
    that carry a Plan out.
    """
    if not live(state):
        return
    # THE RE-FOUNDING (2026-10-12): a Companion with no Plan line of its own
    # is written as ONE clause holding the card (`KokomiCompanionPlan.Write`).
    companion = clauses is None and writable_companion(card)
    if companion:
        clauses = [{"op": PLAY_COMPANION, "target": "front_enemy"}]
        replay = card
    body = list(clauses if clauses is not None else card.plan)
    if not body:
        return
    # `EB-580` AND `EB-599`. HER SIDE OF THE LINE, FOLDED INTO THE NUMBER THAT
    # IS WRITTEN DOWN -- see `hers` for both findings and the rule. It is
    # folded HERE for the reason the two captures below are: her Strength and
    # this card's enchantment are what the player was looking at when they
    # decided to write the Plan, and both the card and the buff can be
    # anywhere by the morning. It runs FIRST, and each rewrite below copies
    # the clause it touches, so neither can un-fold it.
    #
    # MOON'S REFLECTION FOLDS THE CARD IT FOUND and not the card it is, which
    # is what `enchanted_by` is for: an enchantment is a fact about the copy
    # whose printed line this is. Her Strength is hers either way.
    owner = enchanted_by or card
    body = [dict(c, amount=hers(state, owner, int(c.get("amount", 0)),
                                int(c.get("strength_times", 1))))
            if c.get("op") == "damage" else c
            for c in body]
    # CRYSTAL COLLAPSE CAPTURES AT WRITING TIME, and that is the card. "The
    # last other Companion card you played THIS TURN" is a fact about the turn
    # the Plan was written on, and the Plan resolves on the next one -- so
    # asking at carry-out would read a turn the face never named and, on the
    # usual morning, find nothing at all. The captured card rides `entry.card`,
    # the one field a Plan already uses to hold an object (`replay_exhausted`),
    # and an EMPTY capture is written down rather than refused: the face says
    # what it does with nothing, and a Plan that silently declined to queue
    # would make the strip lie about the queue's depth.
    held = replay
    label: Optional[str] = None
    if replay is None and any(c.get("op") == PLAY_COPY_OF_COMPANION
                              for c in body):
        held = last_other_companion(state, card)
        label = plan_label(card, held)
    # `EB-492`, FLANK CAPTURES ITS SET AT WRITING TIME, and it is Crystal
    # Collapse's argument one aim over: "each enemy that intends to attack" is
    # a fact about the intents ON SCREEN NOW, which is what the player is
    # reading when they decide to write the Plan; asking again at carry-out
    # would answer about the NEXT turn's intents, a different question the face
    # never asked. An EMPTY set is written down rather than refused -- the Plan
    # is real, the strip shows it, and what it carries out is nothing.
    #
    # THE CLAUSE IS COPIED, never mutated: `body` is a shallow list of the
    # ROW's own dicts, and writing a capture into one of them would put this
    # turn's board on the printed card.
    if any(c.get("target") == "enemies_intending_attack" for c in body):
        caught = [e for e in state.living_enemies if _intends_to_attack(e)]
        body = [dict(c, targets=list(caught))
                if c.get("target") == "enemies_intending_attack" else c
                for c in body]
        label = plan_aimed_label(card, caught)
    # KELP WALL COUNTS AT WRITING TIME (Kokomi round-1 fixes, 2026-10-12):
    # "plus 3 for each status or curse in your hand when written" is the hand
    # on screen NOW, the number the face's preview printed. Copied, never
    # mutated, for Flank's reason above. `KokomiPlan.Schedule` is the twin.
    if any(c.get("op") == BLOCK_PER_STATUS_IN_HAND for c in body):
        held_now = len(statuses_in_hand(state))
        body = [dict(c, written_count=held_now)
                if c.get("op") == BLOCK_PER_STATUS_IN_HAND else c
                for c in body]
    # All Streams Flow to the Sea's pending gift, taken by the first Plan
    # written after it this turn (a count of 0 is still taken: "once, plus
    # once for each Plan cancelled" with none cancelled is once).
    extra = 0
    if state.kk_next_plan_extra is not None:
        extra = int(state.kk_next_plan_extra)
        state.kk_next_plan_extra = None
    # A PLAN STAYS OPEN (2026-10-01): the card whose now-line this Plan may
    # be carried out as. The LINE's owner (`owner`: Moon's Reflection's found
    # card, or the writing card itself), and only when this is that card's
    # own Plan line -- Moon's Reflection's replay shape writes a clause of its
    # own and is not two-line. A Dusk Plan is left as it is (paper sec.2).
    own_line = (clauses is None or enchanted_by is not None) and not companion
    now_card = (owner if own_line and owner.effects and owner.plan
                else None)
    entry = PlanEntry(card_id=card.id, clauses=body, card=held, label=label,
                      extra=extra, now_card=now_card, source=card)
    state.kk_plan_queue.append(entry)
    state.emit("plan_written", card=card.id, clauses=len(body),
               queued=len(state.kk_plan_queue),
               holds=None if held is None else held.id)
    # THE RE-FOUNDING (2026-10-12): the write payoffs, after the queue moved.
    # Moon's Reflection is the card that WROTE a found card's line.
    note_written(state, card)


def schedule_from_exhaust(state: CombatState, card: Card) -> None:
    """Moon's Reflection: "Choose a card in your exhaust pile: Plan: the
    jellyfish carries out its Plan line, or the card itself if it has none."

    TWO CLAUSE SHAPES OUT OF ONE SCREEN, split by the chosen card's own face,
    exactly as `KokomiPlan.ScheduleFromExhaust` splits them: a card that HAS a
    Plan line contributes that line verbatim, and one that has none becomes a
    single `replay_exhausted` clause holding the card itself.

    AN EMPTY EXHAUST PILE IS A NO-OP and not a screen -- a selection over
    nothing is a click the player cannot answer.

    THE CHOICE IS AN INSTRUMENT SURFACE, `_worst_card`'s convention: the mod
    asks the player and this engine cannot, so it takes a Plan line if one is
    there (that is the branch the card was printed for) and otherwise the
    `_best_card` ranking the recall screens already use. Replacing that body is
    the whole policy.
    """
    from tier0.engine import effects                # late import: cycle

    if not live(state):
        return
    pool = [c for c in state.player.exhaust_pile if c is not card]
    if not pool:
        state.emit("plan_from_exhaust_empty", card=card.id)
        return
    planned = [c for c in pool if c.plan]
    if planned:
        pick = effects._best_card(planned)
        state.emit("plan_from_exhaust", card=card.id, chose=pick.id,
                   line="own")
        # `EB-580`: the LINE is `pick`'s, so `pick`'s enchantment is the one on
        # it -- the same card `KokomiPlan.ScheduleFromExhaust` passes as its
        # `source`.
        schedule(state, card, clauses=pick.plan, enchanted_by=pick)
        return
    pick = effects._best_card(pool)
    state.emit("plan_from_exhaust", card=card.id, chose=pick.id, line="replay")
    schedule(state, card,
             clauses=[{"op": REPLAY_EXHAUSTED}], replay=pick)


# ---------------------------------------------------------------------------
# CARRYING PLANS OUT
# ---------------------------------------------------------------------------

def resolve_all(state: CombatState) -> None:
    """The start of her turn: every Plan she wrote resolves, in order, and the
    queue is empty afterwards.

    THE QUEUE IS DRAINED BEFORE THE FIRST CLAUSE RUNS -- `ResolveAll`'s own
    rule, and its reason: a Plan whose body schedules another Plan would
    otherwise resolve its own child in the same turn, which nothing printed
    says. Moon's Reflection's replay can reach a card that writes one, so this
    is not only a discipline.

    NEREID'S ASCENSION IS READ PER ENTRY, not once for the morning, and the C#
    records that as a reading: its own clause is what installs the doubling, so
    asking before each Plan means the Rare does not double itself and every
    Plan written after it in the same morning IS doubled.

    THE TWO-PLAN CAP IS READ HERE (`EB-643`, R265), and it is a LANE RULE
    BEHIND A RUNTIME TOGGLE rather than a rule of the arm: `C.KOKOMI_PLAN_CAP`
    is 0 by default and 0 is unlimited, so with it unset this method drains
    exactly what it drained before. At N the front N entries are carried out
    and THE REST STAY QUEUED IN ORDER -- they are not discarded and not
    re-sorted, because the whole trial is about whether queue ORDER becomes a
    decision. `KokomiPlan.PlanCap` is the twin, read out of the environment on
    that side for the reason its own header gives.

    """
    if not live(state) or not state.kk_plan_queue:
        return
    cap = int(getattr(C, "KOKOMI_PLAN_CAP", 0) or 0)
    if cap > 0:
        due = list(state.kk_plan_queue[:cap])
        held = list(state.kk_plan_queue[cap:])
    else:
        due = list(state.kk_plan_queue)
        held = []
    state.kk_plan_queue.clear()
    # `EB-335`. THE MORNING'S DEPTH, recorded on the same line the queue is
    # drained on and BEFORE the first clause runs -- Tide Wall's "for each Plan
    # the Bake-Kurage carries out this morning". Written here rather than
    # counted up inside the loop so the answer does not depend on where in the
    # queue the Tide Wall sits: on a three-Plan morning it is three whether it
    # was written first or last. `KokomiPlan.ResolveAll` records the same
    # number on the ledger, in the same place.
    # `EB-501`, R-less D default (Kokomi r17): the depth is CARRY-OUTS and not
    # entries. All three readers say "carried out this morning" on their own
    # faces -- Tide Wall, Well Laid, Tide Chart -- and under Nereid's
    # Ascension a one-Plan morning carries out twice, so a morning of one
    # written Plan pays for two. The seat wrote two Plans under the Ascension
    # and Well Laid paid +3.
    #
    # READ ONCE, AT THE DRAIN, which is the same discipline the paragraph
    # above states and for the same reason: the answer must not depend on
    # where in the queue the reader sits. The one state it cannot see is an
    # Ascension that ARRIVES mid-morning off a Plan of its own; the loop below
    # would then double the later entries and this number would not know. That
    # is the price of order-independence and it is deliberate.
    #
    # THE CAP MOVES THIS NUMBER AND IS MEANT TO (`EB-643`): the depth is what
    # the jellyfish CARRIES OUT this morning, so a capped morning is a shallow
    # morning and Tide Wall, Well Laid and Tide Chart all read the smaller
    # number. The entries that waited pay their reader on the morning they
    # actually land.
    # `EB-655`. ONE EXTRA CARRY-OUT AND NOT A DOUBLING, because Nereid's
    # Ascension now doubles the FIRST entry of the drain alone: a three-Plan
    # morning under the Rare is four carry-outs, not six.
    state.kk_plans_this_morning = len(due) + (
        1 if due and carry_out_times(state) > 1 else 0)
    state.emit("plan_resolve_all", plans=len(due))
    choose_lines(state, due)
    _drain(state, due, why="turn_start")
    # `EB-643`. WHAT THE CAP HELD BACK GOES BACK ON THE FRONT OF THE QUEUE, in
    # order, AFTER the drain -- not before it, because a Plan carried out this
    # morning can write another one (Moon's Reflection reaches a card that
    # does), and that new Plan waits for the NEXT morning like every other. It
    # is put in front of anything written during the drain for the same reason
    # it is kept in order at all: it was written first.
    if held:
        state.kk_plan_queue[:0] = held
        # `pending` IS THE TRUE DEPTH AFTER THE RE-INSERT (round 23, beside
        # `EB-650`), and it is the sim's half of the badge fix one file over:
        # `KokomiPlan.ResolveAll` syncs the pending badge at depth 0 before
        # the drain and left it there, so a capped morning ended with Plans
        # held and no badge saying so. This engine has no badge, and the
        # honest mirror is the number: a reader of the log sees what the
        # player is still holding rather than only what was put back.
        state.emit("plan_cap_held", plans=len(held), cap=cap,
                   pending=len(state.kk_plan_queue))


def _drain(state: CombatState, due: list[PlanEntry], why: str,
           mid_turn: bool = False) -> None:
    """CARRY A LIST OF PLANS OUT, IN ORDER -- the one loop both drains share
    (the morning's, and `EB-643`'s dusk).

    THE RIDERS LIVE HERE AND NOWHERE ELSE, which is the whole reason this is a
    function rather than two loops. "The next Plan" means the entry carried out
    immediately after this one IN THIS DRAIN: a rider is written by the entry
    that prints it, applies to the entry that follows, and is gone when this
    list runs out. A rider written by the last entry of a morning does not
    reach into the evening, and one written at dusk does not reach into the
    next morning -- both fall off the end of a local, which is the shape that
    cannot leak.

    `resolve_front` (Change of Plans) DOES NOT COME THROUGH HERE and so neither
    sets nor consumes a rider: it carries ONE entry out, and there is no "next"
    for the word to name. `KokomiPlan.Drain` is the twin, with the same two
    callers and the same non-caller.

    A RIDER THAT REACHED NOTHING SAYS SO (`EB-645`, round 23). The defence
    lane wrote Second Wave with no Plan behind it in the same morning, the
    rider fell off the end of this local exactly as designed, and the page
    said nothing at all -- the seat read "no enemy lost HP" off a Plan that
    had in fact done its whole job and found no follower. So the drain emits
    `plan_no_follower` carrying the finished sentence, `"<card>: no Plan
    followed"`, and the faces now print the window the rider lives in.
    `KokomiPlan.Drain` is the twin and records the same sentence on the
    carry-out log the seats read.

    ONLY ON A DRAIN THAT RAN OUT, and not on one the fight cut short: the
    two early returns below leave a fight that is over, where "no Plan
    followed" would be a receipt about a morning nobody is playing any more.
    """
    double_next = False
    extra_next = False
    #: `EB-645`. WHO WROTE THE PENDING RIDER, so the line can name the card.
    #: One slot for both riders: an entry printing both is one card, and two
    #: entries in a row each writing one leave only the later card pending.
    rider_source: Optional[str] = None
    # POOL COMPLETION (2026-10-01), SPRING TIDE: a MID-TURN drain is not the
    # start of a turn or a Dusk, so Nereid's Ascension does not double its
    # first entry (`resolve_front`'s reading, for the whole queue).
    first_times = 1 if mid_turn else carry_out_times(state)
    for index, entry in enumerate(due):
        if state.over or not state.player.alive:
            return
        # THE RIDERS THE ENTRY BEFORE THIS ONE WROTE, taken and cleared in the
        # same breath: a rider is spent by the entry it reaches, so two Plans
        # in a row that each double cannot both land on a third.
        double, extra = double_next, extra_next
        double_next = extra_next = False
        # `EB-655`. THE FIRST ENTRY OF THIS DRAIN IS THE ONE NEREID'S DOUBLES,
        # and "each turn" is read as "each DRAIN": a morning and a dusk are two
        # drains on one turn and each pays its own first entry. That is the
        # `_drain`-local reading every other positional rule in this arm takes
        # -- "the next Plan" already means "in this drain" -- and it is what
        # lets the Rare pay a one-Plan morning at all.
        #
        # `CarryOutTimes + 1` UNDER SECOND WAVE, which is the pin: the rider is
        # a FLAG and not a count, so a first entry under Nereid's Ascension
        # that Second Wave also reached is carried out three times, not four.
        times = ((first_times if index == 0 else 1)
                 + (1 if extra else 0) + int(entry.extra))
        for _ in range(times):
            if state.over or not state.player.alive:
                return
            wrote = _resolve_entry(state, entry, why=why,
                                   double_damage=double,
                                   drain_entries=len(due))
            # THE RIDERS THIS ENTRY WROTE, OR'd across its own carry-outs for
            # the reason above: an entry doubled by Nereid's prints its rider
            # twice and "the next Plan is carried out twice" said twice is
            # still twice.
            double_next = double_next or wrote[0]
            extra_next = extra_next or wrote[1]
        if double_next or extra_next:
            rider_source = entry.card_id
    # `EB-645`. THE DRAIN RAN OUT WITH A RIDER STILL IN HAND.
    if (double_next or extra_next) and rider_source:
        state.emit("plan_no_follower", card=rider_source, why=why,
                   line=f"{rider_source}: no Plan followed")


def resolve_front(state: CombatState) -> None:
    """Change of Plans: "The jellyfish carries out your front Plan now."

    IT LEAVES THE QUEUE, which is what "carries out" means everywhere else in
    the arm -- one resolution moved forward, not a copy. An empty queue is a
    printed no-op, the way a blocked Kurage memory is.

    NOT DOUBLED. `CarryOutTimes` is read inside `ResolveAll`'s drain loop and
    nowhere else, so Nereid's window pays the morning and not this card; that
    is the C#'s shape taken literally rather than a rule invented here.

    IT POPS THE FRONT ENTRY WHETHER OR NOT IT IS DUSK (`EB-643`), and that is
    a reading rather than an oversight: the card says "your front Plan", the
    queue is one queue, and a Dusk Plan sitting at the front of it is the front
    Plan. What Dusk changes is the drain that would otherwise have taken it.

    IT NEITHER SETS NOR CONSUMES A RIDER, for `_drain`'s reason: there is no
    "next Plan" in a drain of one.
    """
    if not live(state):
        return
    if not state.kk_plan_queue:
        state.emit("plan_front_empty")
        return
    entry = state.kk_plan_queue.pop(0)
    choose_lines(state, [entry])
    # THE EXPANSION: an All Streams gift rides the entry, so a hurried Plan
    # is carried out its full number of times too.
    for _ in range(1 + int(entry.extra)):
        if state.over or not state.player.alive:
            return
        _resolve_entry(state, entry, why="change_of_plans")


def resolve_all_now(state: CombatState) -> None:
    """SPRING TIDE (pool completion, 2026-10-01): "The Bake-Kurage carries out
    all your Plans now."

    THE WHOLE QUEUE, IN ORDER, Dusk Plans included: "all your Plans". It is a
    DRAIN (`_drain`), so "the Plan after this one" riders (Second Wave,
    Opening Gambit) reach the entry behind them, and each carry-out rings the
    plan bus and counts for the Casket and Kurage Canopy. MID-TURN, so
    Nereid's Ascension does not double the first entry (`resolve_front`'s
    reading, which this extends) and the morning's depth is not touched. Not
    capped: the cap is a rule about the morning.

    THE QUEUE IS EMPTIED BEFORE THE FIRST CLAUSE RUNS (`resolve_all`'s rule),
    so a Plan written afterwards -- by a carry-out or by the next card -- waits
    for the morning: "a volume turn can pay twice". `KokomiPlan.ResolveAllNow`
    is the twin.
    """
    if not live(state):
        return
    if not state.kk_plan_queue:
        state.emit("plan_front_empty")
        return
    due = list(state.kk_plan_queue)
    state.kk_plan_queue.clear()
    state.emit("plan_resolve_all_now", plans=len(due))
    choose_lines(state, due)
    _drain(state, due, why="spring_tide", mid_turn=True)


def carry_out_times(state: CombatState) -> int:
    """How many times THE FIRST Plan of a drain is carried out right now: two
    while Nereid's Ascension is on her, one otherwise.

    `EB-655` (pool pass three) NARROWED THE READER'S CALLER AND NOT THIS
    FUNCTION: the answer is still "is the Rare on her", and `_drain` asks it
    for the first entry of the drain only. The Rare used to double every Plan,
    which paid for writing MORE and made a deep morning its only line; the
    first entry of each drain pays a one-Plan morning too, and makes queue
    ORDER the decision the card is about. `KokomiPlan.CarryOutTimes` is the
    twin, narrowed at its own caller in the same way."""
    return 2 if state.player.powers.get(NEREIDS_ASCENSION, 0) else 1


# ---------------------------------------------------------------------------
# A PLAN STAYS OPEN (2026-10-01, ruled)
# ---------------------------------------------------------------------------
#
# review/active/kokomi-delay-pays-2026-10-01.md sec.2: "When the Bake-Kurage
# carries out a Plan, you choose which line it is: its Plan line, or its now
# line." Two-line cards only (a now-line and a Plan line); Plan-only cards and
# Dusk Plans are unchanged. The now-line is printed size. Every carry-out of
# an entry (Nereid's Ascension, Second Wave, All Streams) takes the line chosen
# for it, which is the paper's "the default is the line chosen for the first".
#
# PICK 5 (a) (sec.3, ruled 2026-10-01): "Plans carry out on their Plan line;
# click a waiting Plan to flip it." No screen. A waiting two-line Plan holds
# its `line`; during her turn the player flips it (`flip`, the click on the
# Plan strip in the mod) and flips it back the same way; at carry-out each
# Plan uses the line it holds (`choose_lines`). This engine's player is the
# pilot, which flips at the end of its turn by `line_policy` -- the Plan line
# by default. Twins: `KokomiPlan.Flip`, `KokomiPlan.ChooseLines`.


def two_line(entry: PlanEntry) -> bool:
    """Does this Plan offer the choice? A two-line card's own line."""
    return entry.now_card is not None


def flip(state: CombatState, index: int) -> bool:
    """The player clicks the waiting Plan at `index` (front = 0): a two-line
    Plan switches between its Plan line and its now-line. False, and nothing
    moves, outside her turn, past the queue, or on a Plan with one line.
    `KokomiPlan.Flip` is the twin."""
    if not live(state) or not state.in_player_turn:
        return False
    queue = state.kk_plan_queue
    if index < 0 or index >= len(queue) or not two_line(queue[index]):
        return False
    entry = queue[index]
    entry.line = "plan" if entry.line == "now" else "now"
    state.emit("plan_flipped", card=entry.card_id, line=entry.line)
    return True


def choose_lines(state: CombatState, due: Sequence[PlanEntry]) -> None:
    """Set each due entry's `line` before it is carried out: a two-line Plan
    keeps the line it was flipped to while it waited, and every other Plan is
    its Plan line. No screen, no latch (pick 5a). `KokomiPlan.ChooseLines`
    is the twin."""
    for entry in due:
        if not two_line(entry):
            entry.line = "plan"
            continue
        state.emit("plan_line_chosen", card=entry.card_id, line=entry.line)


def line_policy(state: CombatState, entry: PlanEntry) -> str:
    """THE PILOT'S FLIP -- an INSTRUMENT SURFACE in `_worst_card`'s sense
    (R215 B): the mod leaves it to the player, and nothing measured through
    this function is a statement about the design.

    THE PLAN LINE, by default (pick 5a: "Plans carry out on their Plan
    line"). The old heuristic read the carry-out turn's intents, which a
    player flipping during the turn before cannot see; it went with the
    turn-start screen."""
    return "plan"


def pilot_flips(state: CombatState) -> None:
    """The pilot's last act of its turn: each waiting two-line Plan's line,
    by `line_policy`, set through `flip` as a click would set it. Called by
    `combat._player_turn` at the end of her turn."""
    if not live(state):
        return
    for index, entry in enumerate(list(state.kk_plan_queue)):
        if two_line(entry) and line_policy(state, entry) != entry.line:
            flip(state, index)


#: The per-card context a now-line carry-out opens and then restores, on top
#: of `combat._FREE_PLAY_CONTEXT`: the bound aim, and the replay latch that
#: keeps a nested read from aiming at the pet.
_NOW_LINE_CONTEXT = ("card_aim", "card_aim_bound", "kurage_autoplaying")


def carry_out_now_line(state: CombatState, entry: PlanEntry) -> None:
    """THE NOW-LINE, CARRIED OUT BY THE BAKE-KURAGE: the card's printed
    effects, resolved as her own face-up line would resolve them (her Strength
    and Dexterity at carry-out, the printed numbers), without the card moving
    and without counting as a card played. `KokomiPlan.CarryOutNowLine`'s
    twin, which runs the generated card's `PlayNowLine`.

    THE AIM IS THE PLAN'S RETARGETING RULE: the front enemy, or Converging
    Tide's override while that body lives (`_aimed`). No living enemy and the
    line is skipped -- the fight is over.

    THE OUTER CONTEXT IS SAVED AND RESTORED (`combat.resolve_free_play`'s
    contract), because Change of Plans and Spring Tide carry Plans out inside
    a card's own play.
    """
    from tier0.engine import combat, effects        # late import: cycle
    _ABSENT = object()

    card = entry.now_card
    if card is None:
        return
    aim = _aimed(state, {"target": "front_enemy"}, entry)
    if not aim:
        state.emit("plan_now_line_skipped", card=card.id)
        return
    names = tuple(combat._FREE_PLAY_CONTEXT) + _NOW_LINE_CONTEXT
    saved = [(n, getattr(state, n, _ABSENT)) for n in names]
    try:
        state.card_aim = aim[0]
        state.card_aim_bound = True
        state.kurage_autoplaying = True
        state.current_card_companion = False
        state.reactions_this_card = 0
        state.kills_this_card = 0
        state.fatal_kills_this_card = 0
        state.exhausted_this_card = 0
        state.block_gains_this_card = 0
        state.block_gained_this_card = 0
        state.discards_this_card = 0
        state.repeat_requested = 0
        state.current_attack_bonus = 0
        state.mc_attack_element_override = None
        state.sparks_at_play = state.player.sparks
        state.current_card_cost = 0
        state.target_had_offelement_aura = bool(
            aim[0].aura and aim[0].aura != state.player.element)
        state.target_had_aura = bool(aim[0].aura)
        state.emit("plan_now_line", card=card.id,
                   target=getattr(aim[0], "name", None))
        try:
            effects._resolve_effects(state, card.effects, card)
        except effects.ChargeUnpaid:
            pass
    finally:
        for name, value in saved:
            if value is _ABSENT:
                state.__dict__.pop(name, None)
            else:
                setattr(state, name, value)


def _resolve_entry(state: CombatState, entry: PlanEntry, why: str,
                   double_damage: bool = False,
                   drain_entries: int = 1) -> tuple[bool, bool]:
    """ONE PLAN CARRIED OUT -- the unit Treatise and Song of Pearls are priced
    in. "Whenever the jellyfish carries out a Plan" is once per ENTRY, and the
    notify at the bottom is the only place it fires, so Change of Plans' early
    resolution pays them exactly as the morning's does.

    `double_damage` and `drain_entries` ARE THE DRAIN'S, and they are parameters
    rather than reads for `ResolveEntry`'s own reason one file over: nothing
    about the state this entry sits in says which entry ran before it or how
    deep the drain around it is, so the caller is the only thing that knows
    and the caller says. `resolve_front`'s defaults are the honest answer for
    a drain of one -- no rider was doubled and one Plan was carried out.

    IT RETURNS THE RIDERS THIS ENTRY WROTE, `(double, extra)`, because the clause that writes one is inside the
    loop below and the drain that spends it is outside: handing them back is
    what keeps "the next Plan" a fact about the DRAIN rather than a flag on the
    state that could outlive it.
    """
    state.emit("plan_carried_out", card=entry.card_id, why=why,
               clauses=len(entry.clauses))
    wrote = [False, False]
    if entry.line == "now" and entry.now_card is not None:
        # A PLAN STAYS OPEN (2026-10-01): the player chose the now-line. It
        # replaces the Plan line whole, so it writes no rider and Opening
        # Gambit's double does not reach it (printed size). It is still a
        # carry-out: the plan bus below pays either line.
        carry_out_now_line(state, entry)
    else:
        # THE RE-FOUNDING (2026-10-12): Grand Strategist's window -- a
        # reaction inside it was caused by this Plan. `KokomiPlan.IsCarryingOut`.
        was = state.kk_carrying_out
        state.kk_carrying_out = True
        try:
            for clause in entry.clauses:
                if state.over or not state.player.alive:
                    break
                _resolve_clause(state, entry, clause,
                                double_damage=double_damage, wrote=wrote,
                                drain_entries=drain_entries)
        finally:
            state.kk_carrying_out = was
    _note_plan_resolved(state, entry)
    note_carried_out(state, entry)
    return wrote[0], wrote[1]


def claim_once_per_turn(state: CombatState, key: str) -> bool:
    """THE ONE ONCE-PER-TURN GATE, and the three powers that cap a payoff at a
    turn all call it: True the FIRST time `key` is claimed in a turn and False
    for the rest of it. `KokomiOverhaulLedger.ClaimOncePerTurn`'s twin, cleared
    by `roll_turn` beside every other per-turn half of this arm.

    A CLAIM AND NOT A QUESTION: the caller that gets True has taken the turn's
    payout, so no second reader can see the latch open behind it.
    """
    if key in state.kk_once_per_turn:
        return False
    state.kk_once_per_turn.add(key)
    return True


def _note_plan_resolved(state: CombatState,
                        entry: Optional[PlanEntry] = None) -> None:
    """The plan bus: one Plan carried out.

    Treatise and Song of Pearls LEFT this bus in the Kokomi core pass
    (2026-09-27): Treatise now pays for a face-up play of a Plan card
    (`note_face_up_plan_card`) and Song of Pearls for an empty queue
    (`song_of_pearls`). Her Ancient under the arm still rides it.

    ONE PAYMENT PER PLAN, NOT PER CLAUSE: War Council prints two clauses and is
    one Plan. That is true because of WHERE this is called (the tail of
    `_resolve_entry`) rather than because of anything here.
    """
    p = state.player
    # Sango Isshin's condition, written here because this is the one place a
    # Plan is carried out -- dawn, Change of Plans and Moon all reach it.
    state.kk_plan_carried_out_this_turn = True
    # Sango Isshin's per-fight count ([USER]'s run, 2026-10-11), once per
    # CARRY-OUT, so a doubled one counts twice.
    state.kk_plans_carried_out_this_combat += 1
    # THE PAYOFF PASS, KURAGE CANOPY: "Whenever the Bake-Kurage carries out
    # a Plan, gain 2 Block." Per carry-out, so a doubled one pays twice.
    # POWERED, as her Ancient's Block below. `KurageCanopyPower` is the twin.
    canopy = int(p.powers.get(KURAGE_CANOPY, 0))
    if canopy:
        amount = powers.modify_block_gained(p, canopy)
        p.block += amount
        state.emit("block", amount=amount)
        state.emit("plan_kurage_canopy", amount=amount)
    n = p.powers.get(PRINCESS_OF_WATATSUMI, 0)
    if n:
        # Block first, then the card: `PrincessOfWatatsumiPlanPower`'s order.
        # POWERED (rule 3: her Dexterity counts on what a Plan pays).
        amount = powers.modify_block_gained(p, n)
        p.block += amount
        state.emit("block", amount=amount)
        state.draw(PRINCESS_OF_WATATSUMI_DRAW)
        state.emit("plan_princess_of_watatsumi", amount=amount)


def _resolve_clause(state: CombatState, entry: PlanEntry,
                    clause: dict, double_damage: bool = False,
                    wrote: Optional[list] = None,
                    drain_entries: int = 1) -> None:
    """One planned clause. `ResolveOne`'s switch, arm for arm.

    The last three arguments are `EB-643`'s and they are the drain's, not the
    clause's -- see `_resolve_entry`. `wrote` is written INTO rather than
    returned because one entry's clause list may print more than one rider and
    the switch below has no return value to carry them on."""
    from tier0.engine import effects                # late import: cycle

    p = state.player
    op = clause["op"]
    amount = int(clause.get("amount", 0))
    aim = clause.get("target")

    if op == "draw":
        state.draw(amount)
    elif op == "energy":
        p.energy += amount
        state.emit("energy", amount=amount)
    elif op == EACH_PLAYER_ENERGY:
        # POOL COMPLETION, TACTICAL RELAY. Every player: here, her.
        p.energy += amount
        state.emit("energy", amount=amount)
        state.emit("plan_each_player", op=op, amount=amount, players=1)
    elif op == EACH_PLAYER_DRAW:
        # Written at 0 on the base card: a 0 draws nothing.
        if amount > 0:
            state.draw(amount)
            state.emit("plan_each_player", op=op, amount=amount, players=1)
    elif op == "block":
        # POWERED (`ValueProp.Move`), rule 3, and the same funnel a card's own
        # printed Block goes through -- Frail bites it and Dexterity feeds it.
        # Draft 2's planned Block was `Unpowered`; draft 6 states the opposite
        # rule in the brief itself.
        if amount <= 0:
            # THE FEED PASS: an unprinted 0 clause (Current Read, unupgraded)
            # is nothing, not a Dexterity-sized Block. `PLAN_ZERO_AMOUNT_OPS`.
            return
        gained = powers.modify_block_gained(p, amount)
        p.block += gained
        state.emit("block", amount=gained)
    elif op == NEXT_PLAN_DOUBLE_DAMAGE:
        # OPENING GAMBIT's rider (`EB-643`). It DOES NOTHING HERE except say
        # so: the drain spends it on the entry that follows, and a rider
        # written by the last Plan of a drain falls off the end of a local
        # rather than waiting for a morning nobody promised it.
        if wrote is not None:
            wrote[0] = True
        state.emit("plan_rider", rider=NEXT_PLAN_DOUBLE_DAMAGE)
    elif op == NEXT_PLAN_EXTRA_CARRY_OUT:
        # SECOND WAVE's rider (`EB-643`). Same terms as the one above.
        if wrote is not None:
            wrote[1] = True
        state.emit("plan_rider", rider=NEXT_PLAN_EXTRA_CARRY_OUT)
    elif op == "first_attack_twice":
        # R276, PINCER: "This turn, your first Attack is played twice." One
        # switch however many are carried out -- "your first Attack" is one
        # Attack. Spent by `spend_first_attack_twice`, dropped at turn end.
        p.powers[FIRST_ATTACK_TWICE] = 1
        state.emit("plan_first_attack_twice")
    elif op == ADD_STINGS:
        # THE RE-FOUNDING, KURAGE'S WAKE: "Add 2 Stings to your hand."
        add_jellyfish(state, STING_ID, amount, upgraded=False)
    elif op == STRENGTH_THIS_TURN:
        # GOROU'S WAR BANNER: "Gain 3 Strength this turn." Flex's shape.
        powers.apply_power(state, p, "temp_strength", amount)
        state.emit("plan_strength_this_turn", amount=amount)
    elif op == JUUGA_GUARD:
        # GOROU'S JUUGA: "For 3 turns, at the end of your turn gain 6 Block."
        # Stacks are turns; `effects.inazuma_overhaul_turn_end` pays it.
        p.powers[MI_JUUGA_GUARD] = p.powers.get(MI_JUUGA_GUARD, 0) + amount
        state.emit("plan_juuga_guard", turns=amount)
    elif op == PLAY_COMPANION:
        carry_out_companion(state, entry.card)
    elif op in coop.PLAN_OPS:
        # THE CO-OP SET: Joint Orders' ally draws, Coordinated Strike's other
        # players hit harder. Nobody else is at a one-seat table, so the
        # clause is carried out and lands on no one -- the C# half,
        # `KokomiPlan.Kind.AllyDraw` / `OthersAttackDamageThisTurn`, is where
        # the rule lives.
        coop.no_other_player(state, op)
    elif op == "block_front_intent":
        # R276, TIDE WALL: "Gain Block equal to the damage the enemy intends
        # to deal" (+ the upgrade's flat bonus). The FRONT enemy's intent read
        # AT CARRY-OUT, which is after the coming enemy turn's intents are up;
        # a multi-hit intent counts every hit and a non-attack intent is 0.
        # POWERED, the flat planned Block's funnel.
        intended = front_intent_damage(state)
        gained = powers.modify_block_gained(p, intended + amount)
        if gained:
            p.block += gained
            state.emit("block", amount=gained)
        state.emit("plan_tide_wall", amount=gained, intended=intended)
    elif op == "mend":
        effects.mend(state, amount)
    elif op == "damage":
        _hit(state, clause, amount, entry=entry, double=double_damage)
    elif op == "damage_quarter_max_hp":
        _hit(state, clause, quarter_of_max_hp(state), entry=entry,
             double=double_damage)
    elif op == "apply_power":
        _debuff(state, clause, clause["power"], amount, entry=entry)
    elif op == REPLAY_EXHAUSTED:
        _replay(state, entry.card)
    elif op == PLAY_COPY_OF_COMPANION:
        _play_copy(state, entry.card)
    elif op == BLOCK_PER_STATUS_IN_HAND:
        block_per_status(state, amount, clause.get("written_count"))
    elif op == TRANSFORM_STATUSES_IN_DRAW_PILE:
        transform_statuses(state, bool(clause.get("upgraded")))
    else:                                   # unreachable: shape-checked at load
        raise ValueError(f"unknown plan clause {op!r}")


# ---------------------------------------------------------------------------
# THE STATUS BATCH (2026-10-01) -- the twins of `KokomiStatusBatch`
# ---------------------------------------------------------------------------

def is_status_or_curse(card: Optional[Card]) -> bool:
    """A status or a curse. `Card.is_junk` reads rarity, and an
    enemy-injected status is built at rarity "basic" with type "status"
    (`statuses.make_status`), so both are asked. `KokomiStatusBatch.
    IsStatusOrCurse` reads the card's type."""
    return card is not None and (card.type in ("status", "curse")
                                 or card.is_junk)


def statuses_in_hand(state: CombatState) -> list[Card]:
    return [c for c in state.player.hand if is_status_or_curse(c)]


def block_per_status(state: CombatState, rate: int,
                     written_count: Optional[int] = None) -> int:
    """KELP WALL: "plus 3 for each status or curse in your hand when
    written". Powered, the flat planned Block's funnel. `written_count` is
    the count `schedule` stamped when the Plan was written (Kokomi round-1
    fixes, 2026-10-12); None (a clause no writer stamped) reads the hand."""
    n = (len(statuses_in_hand(state)) if written_count is None
         else int(written_count))
    if n <= 0 or rate <= 0:
        state.emit("plan_kelp_wall", statuses=n, amount=0)
        return 0
    p = state.player
    gained = powers.modify_block_gained(p, rate * n)
    if gained:
        p.block += gained
        state.emit("block", amount=gained)
    state.emit("plan_kelp_wall", statuses=n, amount=gained)
    return gained


def exhaust_statuses(state: CombatState, cap: int) -> int:
    """TIDECLEANSE (its now-line since 2026-10-12): "Exhaust up to 2 [3]
    statuses or curses in your hand." Every one when she holds that many or
    fewer. When she holds more, the
    player chooses in the mod; this engine takes them in hand order (an
    INSTRUMENT SURFACE in `_worst_card`'s sense: every status is a clog)."""
    from tier0.engine import effects, refpowers     # late import: cycle
    victims = statuses_in_hand(state)[:max(0, cap)]
    for card in victims:
        if effects.remove_instance(state.player.hand, card):
            refpowers.exhaust_card(state, card)
    state.emit("plan_tidecleanse", exhausted=len(victims))
    return len(victims)


def sea_glass_card(upgraded: bool = False) -> Card:
    """Sea Glass: 0, "Gain 1 [2] Energy. Exhaust." In no pool."""
    return Card(id=SEA_GLASS + ("+" if upgraded else ""), name="Sea Glass",
                cost=0, type="skill", rarity="token", exhaust=True,
                effects=[{"op": "energy", "amount": 2 if upgraded else 1}])


def transform_statuses(state: CombatState, upgraded: bool) -> int:
    """SEA GLASS HARVEST: "Transform every status and curse in your draw
    pile into Sea Glass [Sea Glass+]." The DRAW PILE since the Kokomi round-1
    fixes (2026-10-12): the carry-out found the hand empty of what the Plan
    was written for, so it converts the dead draws still to come. In place,
    as `CardCmd.Transform` swaps a card where it stands."""
    pile = state.player.draw_pile
    n = 0
    for i, card in enumerate(list(pile)):
        if is_status_or_curse(card):
            pile[i] = sea_glass_card(upgraded)
            n += 1
    state.emit("plan_sea_glass", transformed=n, upgraded=upgraded)
    return n


def quarter_of_max_hp(state: CombatState) -> int:
    """Sango Isshin's "a quarter of your Max HP", rounded DOWN.

    ONE function, and it is public for the Furina legibility lesson the C#
    states at its own copy: a preview and an effect that compute separately
    will eventually disagree, and the player believes the preview. Both the
    now-line op and the planned all-enemies half read this.
    """
    return state.player.max_hp // QUARTER


def _hit(state: CombatState, clause: dict, amount: int,
         entry: Optional[PlanEntry] = None, double: bool = False) -> None:
    """A Plan's damage, and it is HYDRO, dealt BY THE BAKE-KURAGE.

    `EB-334`, RULED R246 pick 1 AT ITS DEFAULT: "the Bake-Kurage deals it. The
    enemy's debuffs apply, Kokomi's own Weak and her attack buffs do not."
    Round four-c found the arithmetic exactly the wrong way round -- a
    Strategic enemy's Weak cut two banked Plans to x0.75 the next morning (12
    to 9, 5 to 3) while the enemy's own Vulnerable multiplied nothing, so "her
    debuffs apply to the Kurage's hits and the enemy's do not"
    (`review/ruled/kokomi-overhaul-round-4c-2026-09-02.md` sec.2, sec.6).

    `powered=False` IS THAT SENTENCE IN THIS ENGINE, and it is the flag the
    Casket's strike already carries for the same reason: it drops the DEALER's
    Strength and Weak (`powers.modify_damage_dealt`, which is also where every
    flat attack buff in this engine lands) and NOTHING else -- the aura still
    lands, the reaction still fires, the target's Vulnerable still multiplies
    and its Block still absorbs. A pet carries no Strength, so a planned hit is
    its printed number against the enemy's current state.

    THE APPLIER IS STILL HER, which is a reading and is the C#'s: rule 3's
    "the plans are hers" is what makes a Plan-caused Freeze a debuff SHE
    applied. Draft 6 gives the jellyfish the arithmetic, not the authorship.

    `source="plan"` AND NOT `"attack"`, which is a reading and is the C#'s:
    `KokomiPlan.Hit` goes out through `ElementalHit.Deal`, the funnel this mod
    uses for every NON-Attack hit, not through `DamageCmd.Attack`. In tier0
    `source == "attack"` is the name for a hit from an Attack CARD and it is
    what gates Shatter, on-hit bomb detonation and Skittish; a planned clause
    is not a card being played, so it takes none of those. Everything that is
    still the jellyfish's business -- the aura, the reaction, Vulnerable,
    Block -- is outside that gate and applies.

    THE TARGET LIST IS SNAPSHOTTED before the first hit, so an enemy the volley
    kills does not change who is in it (`QuarterMaxHpAll`'s `.ToList()`).

    `times` IS A LOOP OF WHOLE HITS AND NOT A MULTIPLIER (`EB-492`, Pincer's
    "Deal 3 damage three times"). Three hits of 3 and one hit of 9 are
    different against Block, against an aura and against a body that dies
    partway, so every pass goes out through `deal_damage_to_enemy` on its own
    and THE AIM IS RE-READ between passes -- a front enemy killed by the first
    hit hands the next one to the enemy behind it, which is "leftmost alive"
    read twice rather than a second rule. `KokomiPlan.Hit` loops in the same
    order.

    `double` IS OPENING GAMBIT'S RIDER (`EB-643`), AND IT LANDS HERE -- the one
    funnel every damaging Plan clause goes through, so "the next Plan deals
    double damage" is true of the flat hit, of Sango Isshin's quarter and of
    Chain of Command's per-Companion total without three separate readings.

    AFTER THE FOLD AND BEFORE THE BOARD, which is what the printed order says:
    her Strength and her enchantment are already inside `amount` (they were
    folded at writing time, `hers`), the doubling is applied to that written
    number, and the target's Vulnerable and Block are read after it by
    `deal_damage_to_enemy` as they always are. It is a doubling of the SIZE and
    not of the number of hits, so Pincer's three passes stay three passes and
    each of them is twice as large -- which is the difference that matters
    against Block.
    """
    from tier0.engine import effects                # late import: cycle

    if amount <= 0:
        return
    if double:
        amount *= 2
    for _ in range(max(1, int(clause.get("times", 1)))):
        for enemy in _aimed(state, clause, entry):
            if not enemy.alive:
                continue
            effects.deal_damage_to_enemy(state, enemy, amount,
                                         element="hydro", source="plan",
                                         powered=False)


def _debuff(state: CombatState, clause: dict, power: str,
            amount: int, entry: Optional[PlanEntry] = None) -> None:
    """A planned Weak or Vulnerable, applied BY HER, exactly as a debuff off a
    card she played is.

    IT LANDS ON A CORPSE (R210 Q3): `PowerCmd.Apply` guards on
    `CanReceivePowers`, which does not test `IsDead`, and `_op_apply_power`
    already takes that reading for every aimed power in this engine. The aim
    itself is resolved over the LIVING, so the only corpse this can reach is
    one that died between the aim and the apply.

    IT TAKES THE ENTRY for `_hit`'s reason (`EB-643`): a single-target debuff
    aims at the front, and Converging Tide re-points exactly that aim.
    """
    for enemy in _aimed(state, clause, entry):
        powers.apply_power(state, enemy, power, amount,
                           applier=state.player)


def _replay(state: CombatState, card: Optional[Card]) -> None:
    """Moon's Reflection's second shape: replay a card that had no Plan line.

    THE CARD LEAVES THE EXHAUST PILE FIRST and is then free-played, in that
    order, and the argument is `KurageMemory.Fire`'s verbatim: a card resolving
    out of a pile it is still a member of is a class of bug this repo has
    already paid for once. `_free_play` routes it to its own result pile
    afterwards, so the play leaves the card wherever its printed keywords say.

    A card somebody else moved out of the pile in the meantime is simply not
    replayed -- `remove_instance` is by IDENTITY and its False is the answer.
    """
    from tier0.engine import effects                # late import: cycle
    from tier0.engine.state import remove_instance

    if card is None:
        return
    if not remove_instance(state.player.exhaust_pile, card):
        state.emit("plan_replay_gone", card=card.id)
        return
    state.emit("plan_replay", card=card.id)
    effects._free_play(state, card, force_exhaust=False)


def _play_copy(state: CombatState, card: Optional[Card]) -> None:
    """Crystal Collapse's morning: play a free COPY of the card it caught.

    A COPY, WHICH IS THE DIFFERENCE FROM `_replay` ABOVE. Moon's Reflection
    takes the chosen card OUT of the exhaust pile and plays that instance;
    this one leaves the original wherever it went (its discard pile, usually,
    where the deck can draw it again) and plays a clone. `copy.deepcopy` is the
    engine's own clone idiom -- Anger's `add_card: self` uses it at the one
    other site a card is duplicated mid-combat -- so the copy inherits the
    original's upgrade state, which is what "a copy of the card you played"
    says.

    EXHAUSTED AFTER, and it is `force_exhaust` rather than a keyword written
    onto the clone, so the copy leaves combat however its own printed keywords
    would have routed it and then goes to the exhaust pile regardless. A copy
    that returned to the discard pile would be a second permanent card in the
    deck for one Energy.

    A PLAN THAT CAUGHT NOTHING IS A PRINTED NO-OP, the shape a blocked Kurage
    memory and an empty `resolve_front` already have: the face says what it
    does when there was no other Companion, so this is the rule and not a
    failure.
    """
    import copy as _copy

    from tier0.engine import effects                # late import: cycle

    if card is None:
        state.emit("plan_copy_empty")
        return
    state.emit("plan_copy", card=card.id)
    effects._free_play(state, _copy.deepcopy(card), force_exhaust=True)


# ---------------------------------------------------------------------------
# THE TURN BOUNDARIES
# ---------------------------------------------------------------------------

def roll_turn(state: CombatState) -> None:
    """The Companion ledger's handover, at the ONE place the per-turn counter
    is cleared: this turn's count becomes last turn's.

    Called unconditionally (it is two integer moves and reads no flag), for the
    reason `KokomiOverhaulLedger.RollTo` rolls on read: a rule asked from a
    card body, a power and a relic must never see three different turns. With
    the flag off nothing reads the result.

    THE ARM'S ONE TURN BOUNDARY, and it carries four things rather than one:
    the Companion handover, the once-per-turn latches (Treatise, Song of Pearls
    and The General's Banner), Sango Isshin's "did a Plan happen this morning"
    and, since `EB-335`, Tide Wall's morning depth. One line for all of them,
    so no two can come to disagree about when a turn began --
    `KokomiOverhaulLedger.RollTo` clears the same set.

    """
    state.kk_once_per_turn.clear()
    state.kk_plan_carried_out_this_turn = False
    # `EB-335`. Tide Wall's morning count, cleared HERE and written a few lines
    # later by `resolve_all` -- which runs after this in `combat._player_turn`,
    # so a morning that drains nothing reads an honest zero rather than
    # yesterday's depth.
    state.kk_plans_this_morning = 0
    # THE EXPANSION: All Streams' gift says "this turn" and dies with it.
    state.kk_next_plan_extra = None
    # Crystal Collapse's "this turn". It is CLEARED rather than handed over:
    # the capture happens while the Plan is written, so what survives the
    # boundary is the captured card on the entry and never the list.
    state.kk_companions_this_turn.clear()


# ---------------------------------------------------------------------------
# THE HOOKS
# ---------------------------------------------------------------------------

def note_companion_played(state: CombatState, card: Card) -> None:
    """"You played a Companion card" -- the arm's one definition of it.

    It rides `combat._finish_play`, the one site a manual play and an auto-play
    both enter, beside the counter Chain of Command reads
    (`companion_plays_this_turn`, moved there for every play).
    """
    if not live(state) or not card.is_companion:
        return
    # CRYSTAL COLLAPSE'S MEMORY: this hook is the arm's one definition of
    # "she played a Companion card". (Watatsumi Resistance reads WRITES since
    # the re-founding, 2026-10-12: `note_written`.)
    state.kk_companions_this_turn.append(card)


def kurages_mercy(state: CombatState, amount: int) -> int:
    """KURAGE'S MERCY (pool completion, multiplayer): "Each player Mends 8."
    Every player in the fight, Kokomi included -- tier 0 seats one, so the
    Mend lands on her (`effects.mend`, the keyword's one spelling).
    `KokomiCards.KuragesMercy` is the twin."""
    if not live(state) or amount <= 0:
        return 0
    from tier0.engine import effects                # late import: cycle
    healed = effects.mend(state, amount)
    state.emit("plan_kurages_mercy", amount=amount, healed=healed, players=1)
    return healed


def watatsumi_resistance(state: CombatState) -> int:
    """WATATSUMI RESISTANCE (pool completion; the re-founding, 2026-10-12):
    "Whenever you write a Companion card as a Plan, add a Sting to your hand."
    One Sting per copy of the Power, from `note_written`.
    `WatatsumiResistancePower` (paid by `KokomiRefounding.OnWritten`) is the
    twin."""
    n = int(state.player.powers.get(WATATSUMI_RESISTANCE, 0))
    if not live(state) or n <= 0:
        return 0
    added = add_jellyfish(state, STING_ID, n, upgraded=False)
    state.emit("plan_watatsumi_resistance", stings=added)
    return added


def seas_reproach(state: CombatState, enemy, name: str, stacks: int) -> None:
    """SEA'S REPROACH (pool completion): "Whenever you apply Weak or
    Vulnerable to an enemy, deal 3 damage to it." Called from
    `refpowers.on_power_applied` (the twin of `AfterPowerAmountChanged`) for
    a POSITIVE application she made; once per enemy it lands on. Hydro and
    unpowered, Tidal Riposte's hit. `SeasReproachPower` is the twin."""
    if not live(state) or stacks <= 0 or name not in ("weak", "vulnerable"):
        return
    n = int(state.player.powers.get(SEAS_REPROACH, 0))
    if n <= 0 or enemy is None or enemy is state.player:
        return
    if not getattr(enemy, "alive", False):
        return
    from tier0.engine import effects                # late import: cycle
    state.emit("plan_seas_reproach", target=enemy.name, amount=n, power=name)
    effects.deal_damage_to_enemy(state, enemy, n, element="hydro",
                                 source="plan", powered=False)


# ---------------------------------------------------------------------------
# THE VERBS THAT BELONG TO NO RULE -- `KokomiOverhaulKit`'s half
# ---------------------------------------------------------------------------

def has_debuff(enemy: Optional[Enemy]) -> bool:
    """Undertow's "if the enemy has a debuff".

    `ENEMY_DEBUFFS` plus the Frozen FIELD, which is the whole reason this is a
    function and not a comprehension at the call site: Frozen is a debuff on
    both sides and a power on only one, and a reader that forgot the second
    limb would answer False on a frozen enemy.
    """
    if enemy is None:
        return False
    if enemy.frozen > 0:
        return True
    return any(enemy.powers.get(n, 0) > 0 for n in ENEMY_DEBUFFS)


def debuff_count(enemy: Optional[Enemy]) -> int:
    """Well Laid's "for each debuff on the enemy" (R276): DISTINCT debuffs,
    not stacks, with Frozen's field counted for `has_debuff`'s reason.
    `KokomiOverhaulKit.DebuffCount` is the twin."""
    if enemy is None:
        return 0
    count = sum(1 for n in ENEMY_DEBUFFS if enemy.powers.get(n, 0) > 0)
    return count + (1 if enemy.frozen > 0 else 0)


def weak_vuln_stacks(enemy: Optional[Enemy]) -> int:
    """The Kokomi card pass (2026-10-11, pick 1): "for each Weak and
    Vulnerable on the enemy" -- STACKS of Weak plus stacks of Vulnerable, so
    Weak 2 and Vulnerable 2 read 4. Drowning Pressure and Ceremonial Garment.
    `KokomiOverhaulKit.WeakVulnStacks` is the twin."""
    if enemy is None:
        return 0
    return (max(0, int(enemy.powers.get("weak", 0)))
            + max(0, int(enemy.powers.get("vulnerable", 0))))


def cancel_all_plans_cash(state: CombatState) -> None:
    """EBB TIDE (`EB-643`): "cancel every Plan you have queued; gain 1 Energy
    and draw 1 card for each."

    NO ROW SPELLS IT SINCE `EB-649` (round 23). Ebb Tide drew three times on
    the cap lane and was played none of them -- it is "only live in the
    situation you spent the previous turn trying to create" -- so the row left
    the sheet and both pools. THE OP STAYS REGISTERED, here and in
    `effects.OPS`: the rule is the one a re-issue would want, deleting a
    resolver to re-derive it later is how a reading is lost, and the pins
    below still drive it directly. `KokomiPlan.CancelAllForCash` is the twin
    and carries the same note.

    PER ENTRY AND NOT PER CARRY-OUT, which is the one reading here and it is
    the face's own word: "for each" counts the Plans she is holding, and what
    she is holding is entries -- the same quantity the pending badge shows and
    `PlansHeld` answers. Nereid's Ascension would have doubled them at the
    morning and did not, which is exactly the thing this card gives up.

    NO CARD COMES BACK, unlike Second Thoughts one row up, and that is the
    trade rather than an omission: this cancels a whole queue for a currency
    and that one buys a single Plan back at its own price.

    AN EMPTY QUEUE PAYS NOTHING and says so, the shape above.

    THE DRAW IS AFTER THE ENERGY, in one call, so a drawn card meets a hand
    that can already afford it.
    """
    if not live(state):
        return
    n = len(state.kk_plan_queue)
    if not n:
        state.emit("plan_cancel_all", plans=0, energy=0, cards=0)
        return
    state.kk_plan_queue.clear()
    state.player.energy += n
    state.emit("energy", amount=n)
    state.emit("plan_cancel_all", plans=n, energy=n, cards=n)
    state.draw(n)


def redirect_queued_plans(state: CombatState, target: Optional[Enemy]) -> None:
    """CONVERGING TIDE (`EB-643`): "every queued Plan aims at this enemy
    instead of the front."

    IT STAMPS THE ENTRIES THAT ARE ALREADY WRITTEN AND NOTHING ELSE. A Plan
    written after the redirect aims at the front as usual, because the card
    names the queue as it stands -- "every queued Plan" -- and a rule that
    kept re-aiming later writes would be a Power the row does not print.

    ONLY THE FRONT AIM MOVES, which is `_aimed`'s half of the same rule: "ALL
    enemies" does not aim at the front, so there is nothing on it for "instead
    of the front" to be about, and Flank's captured set was fixed when its Plan
    was written for reasons of its own (`EB-492`).

    A DEAD TARGET FALLS BACK TO THE FRONT rather than to nothing, read at
    carry-out (`_aimed`), which is the arm's standing rule for a body a Plan
    was pointed at and no longer finds.

    IT STAMPS DUSK ENTRIES TOO. They are in the queue, the face says every
    queued Plan, and the redirect happens on the turn they will land on.
    """
    if not live(state):
        return
    if target is None or not state.kk_plan_queue:
        state.emit("plan_redirect", plans=0,
                   target=None if target is None else target.name)
        return
    for entry in state.kk_plan_queue:
        entry.aim_override = target
    state.emit("plan_redirect", plans=len(state.kk_plan_queue),
               target=target.name)






def front_intent_damage(state: CombatState) -> int:
    """Tide Wall's read (R276): the total damage the FRONT enemy's current
    intent would deal her, every hit counted, through the same estimate the
    potions use (`potions._intent_damage`: its Strength and Weak, her
    Vulnerable). 0 for no front enemy or a non-attack intent. The C# twin is
    `KokomiOverhaulKit.IntendedDamage`, which asks the game's own
    `AttackIntent.GetTotalDamage` -- the number the intent badge shows."""
    from tier0.engine import potions               # late import: cycle
    front = front_enemy(state)
    if front is None or not _intends_to_attack(front):
        return 0
    return int(potions._intent_damage(state, front))


def spend_first_attack_twice(state: CombatState, card: Card) -> int:
    """PINCER's switch (R276), spent by the first Attack played FACE-UP: the
    extra play count it adds, 1 or 0. A card written on the Bake-Kurage is
    not a play of its face, so it neither takes nor spends it --
    `FirstAttackTwicePower`'s `ModifyCardPlayCount` asks the pet target the
    same way."""
    if not live(state) or card.type != "attack":
        return 0
    if plan_aimed_at_pet(state, card):
        return 0
    if state.player.powers.pop(FIRST_ATTACK_TWICE, 0):
        state.emit("plan_first_attack_twice_spent", card=card.id)
        return 1
    return 0


def note_face_up_plan_card(state: CombatState, card: Card) -> None:
    """TREATISE (core pass): "Once per turn, when you play a card with a Plan
    line normally, draw 1 card." Called by `effects._resolve_card_bound` after
    a card with a `plan:` line resolves its NOW-line; a write returns before
    it. `TreatisePower.AfterCardPlayed` is the twin. Copies add cards, still
    once a turn.

    KOKOMI ROUND 2 (2026-10-12): "a card you could have written as a Plan"
    -- `can_be_written`, so a Companion card counts too. A carry-out is not
    her play (`kk_carrying_out`): a written Companion's copy draws nothing."""
    if not live(state) or not can_be_written(card):
        return
    if state.kk_carrying_out:
        return
    n = int(state.player.powers.get(TREATISE, 0))
    if n and claim_once_per_turn(state, TREATISE):
        state.draw(n)
        state.emit("plan_treatise", amount=n, card=card.id)




def remove_one_debuff(state: CombatState) -> None:
    """Cleansing Wave: "Remove a debuff from yourself."

    A READING, recorded because the card says "a debuff" and not "the worst
    one": the FIRST debuff on her power list goes, which is the oldest one
    still standing, and the card gives the player no choice. `dict` preserves
    insertion order, so "first" here is the same "first" the C# gets from
    `kokomi.Powers.FirstOrDefault(p => p.Type == PowerType.Debuff)`.

    THE PLAYER-SIDE debuff list is `powers.DURATION_DEBUFFS` plus the two
    damage-over-time stacks -- the same set `ENEMY_DEBUFFS` names, read against
    her instead of against an enemy. An aura is not a debuff and lives on
    enemies anyway.
    """
    if not live(state):
        return
    for name in list(state.player.powers):
        if name in ENEMY_DEBUFFS and state.player.powers.get(name, 0) > 0:
            state.player.powers.pop(name, None)
            state.emit("plan_cleanse", power=name)
            return
    state.emit("plan_cleanse", power=None)


# ---------------------------------------------------------------------------
# THE EXPANSION, BATCH ONE (2026-09-29) -- `KokomiExpansion.cs`'s twin.
# Paper: review/active/kokomi-expansion-2026-09-29.md.
# ---------------------------------------------------------------------------

def note_hydro_damage(state: CombatState, enemy: Enemy) -> None:
    """AT WATER'S EDGE (the Kokomi card pass, 2026-10-11): "The first time
    each turn you deal Hydro damage to an enemy, apply 1 Weak and 1
    Vulnerable to it." Called from `effects.deal_damage_to_enemy` for every
    hit whose element is Hydro, once the hit has landed (fully blocked
    included). Once a turn on the shared latch, claimed by the first such
    hit on an enemy that survives it: a killing hit neither pays nor spends
    the turn's trigger. Copies stack the amount.
    `KokomiExpansion.OnHydroDamage` is the twin."""
    if not live(state) or enemy is None or not enemy.alive:
        return
    n = int(state.player.powers.get(AT_WATERS_EDGE, 0))
    if n <= 0 or not claim_once_per_turn(state, AT_WATERS_EDGE):
        return
    powers.apply_power(state, enemy, "weak", n, applier=state.player)
    powers.apply_power(state, enemy, "vulnerable", n, applier=state.player)
    state.emit("plan_at_waters_edge", target=enemy.name, amount=n)


def garment_bonus(state: CombatState, card: Card, enemy: Enemy) -> int:
    """CEREMONIAL GARMENT: "Your Attacks deal N more damage for each Weak and
    Vulnerable on their target." Per hit, read off the body the hit lands on,
    for an Attack card played face-up. The count is `weak_vuln_stacks`'s:
    stacks of Weak plus stacks of Vulnerable (the Kokomi card pass,
    2026-10-11). `ProtoCeremonialGarmentPower.ModifyDamageAdditive` is the
    twin."""
    if card is None or card.type != "attack" or not live(state):
        return 0
    n = int(state.player.powers.get(CEREMONIAL_GARMENT, 0))
    if n <= 0:
        return 0
    return n * weak_vuln_stacks(enemy)


def grace_keeps(state: CombatState) -> Optional[int]:
    """WATATSUMI'S GRACE: "At the end of your turn, keep up to N of your
    Block." The Block the clear leaves standing, or None when the Power is
    not on her. Read at the block clear, where Barricade and Blur are read
    (`refpowers.should_clear_block`), which is the base game's Sturdy Clamp
    shape: Block above the cap is lost, up to the cap is kept.
    `WatatsumisGracePower` is the twin."""
    if not live(state):
        return None
    n = int(state.player.powers.get(WATATSUMIS_GRACE, 0))
    if n <= 0:
        return None
    return min(int(state.player.block), n)


def tidal_riposte(state: CombatState, enemy: Enemy, blocked: int,
                  unblocked: int) -> None:
    """TIDAL RIPOSTE: "Whenever an enemy's attack is fully Blocked, deal N
    damage to it." One hit of an enemy's attack that Block absorbed whole
    (Block took some and nothing reached her HP), once per hit. Hydro, as
    every damaging card of hers is. `TidalRipostePower` is the twin."""
    from tier0.engine import effects                # late import: cycle
    if not live(state) or enemy is None or not enemy.alive:
        return
    if blocked <= 0 or unblocked > 0:
        return
    n = int(state.player.powers.get(TIDAL_RIPOSTE, 0))
    if n <= 0:
        return
    state.emit("plan_tidal_riposte", target=enemy.name, amount=n)
    effects.deal_damage_to_enemy(state, enemy, n, element="hydro",
                                 source="plan", powered=False)




def kind(state: CombatState, fx: dict, card: Card, target) -> None:
    """The `kokomi` op: one of the expansion's now-line verbs, by `kind:`.
    `KokomiCards.<Kind>` is the twin of each branch."""
    if not live(state):
        return
    k = fx.get("kind")
    p = state.player
    amount = int(fx.get("amount", 0))
    if k == "draw_if_no_plan":
        # MEASURED BREATH: "If no Plan is waiting, draw 2."
        if not state.kk_plan_queue:
            state.draw(amount)
    elif k == "double_weak_vulnerable":
        # SUFFOCATING DEEP: "Double each enemy's Weak and Vulnerable."
        for e in list(state.living_enemies):
            for name in ("weak", "vulnerable"):
                have = int(e.powers.get(name, 0))
                if have > 0:
                    powers.apply_power(state, e, name, have, applier=p)
    elif k == "spring_tide":
        # SPRING TIDE (pool completion): the whole queue, now.
        resolve_all_now(state)
    elif k == "kurages_mercy":
        # KURAGE'S MERCY (pool completion, multiplayer): each player Mends.
        kurages_mercy(state, amount)
    elif k == "shoal_call":
        # SHOAL CALL (the re-founding): "Add 2 [upgraded] Stings to your hand."
        add_jellyfish(state, STING_ID, amount,
                      upgraded=bool(fx.get("upgraded")))
    elif k == "add_sting":
        # Jellyfish Drift, Kurage Barrage: "Add a Sting to your hand."
        add_jellyfish(state, STING_ID, 1, upgraded=False)
    elif k == "add_ward":
        # Bubble Ward, Watatsumi Drill: "Add a Ward to your hand."
        add_jellyfish(state, WARD_ID, 1, upgraded=False)
    elif k == "add_companion":
        # Orders from the Shrine: "Add a random Common Inazuma Companion".
        add_companions(state, 1, upgraded=bool(fx.get("upgraded")))
    elif k == "add_companions":
        # Watatsumi Muster: "Add 2 random ...".
        add_companions(state, amount, upgraded=bool(fx.get("upgraded")))
    elif k == "call_the_generals":
        call_the_generals(state)
    elif k == "reserves":
        reserves(state)
    elif k == "grand_design":
        grand_design(state, card, amount)
    elif k == "block_per_attacker":
        # EVENING WATCH (Dusk retired): "Gain 4 Block for each enemy
        # intending to attack." The card's own Block: Dexterity and Frail.
        n = sum(1 for e in state.living_enemies if _intends_to_attack(e))
        gained = powers.modify_block_gained(p, amount * n) if n else 0
        if gained:
            p.block += gained
            state.emit("block", amount=gained)
        state.emit("plan_evening_watch", amount=gained, enemies=n)
    elif k == "double_block":
        # BRACE FOR THE TIDE (Dusk retired): "Double your Block." Entrench.
        gained = int(p.block)
        if gained > 0:
            p.block += gained
            state.emit("block", amount=gained)
        state.emit("plan_brace", amount=gained)
    elif k == "exhaust_statuses":
        # TIDECLEANSE (no Plan line since the re-founding).
        exhaust_statuses(state, amount)
    else:                                   # unreachable: validated at load
        raise ValueError(f"unknown kokomi kind {k!r}")


#: The `kokomi` op's kinds and the numeric field each prints. The codegen's
#: `KOKOMI_KINDS` / `KOKOMI_KIND_FIELDS` are the twin; `validate_op` is the
#: loader's check.
KINDS = {"draw_if_no_plan": ("amount",), "double_weak_vulnerable": (),
         # POOL COMPLETION (2026-10-01).
         "spring_tide": (),
         "kurages_mercy": ("amount",),
         # THE RE-FOUNDING (2026-10-12).
         "shoal_call": ("amount",), "add_sting": (), "add_ward": (),
         "add_companion": (), "add_companions": ("amount",),
         "call_the_generals": (), "reserves": (),
         "grand_design": ("amount",), "block_per_attacker": ("amount",),
         "double_block": (), "exhaust_statuses": ("amount",)}


def validate_op(card_id: str, fx: dict) -> None:
    """The loader's check of a `kokomi` op: a known kind, exactly its numeric
    fields, and no target (no kind aims)."""
    k = fx.get("kind")
    if k not in KINDS:
        raise ValueError(f"card {card_id!r}: unknown kokomi kind {k!r}")
    allowed = {"op", "kind", *KINDS[k]}
    if k in ("shoal_call", "add_companion", "add_companions"):
        allowed.add("upgraded")      # the `upgraded_grant` key's flag
    unknown = set(fx) - allowed
    if unknown:
        raise ValueError(f"card {card_id!r}: kokomi {k} field(s) "
                         f"{sorted(unknown)} not understood")
    for field in KINDS[k]:
        v = fx.get(field)
        if not isinstance(v, int) or isinstance(v, bool) or v <= 0:
            raise ValueError(f"card {card_id!r}: kokomi {k} {field} must be "
                             "a positive literal int")


# ---------------------------------------------------------------------------
# THE RE-FOUNDING (2026-10-12) -- `Powers/Prototype/KokomiRefounding.cs`'s twin.
# Direction review/active/kokomi-design-pass-2026-10-11.md (all five picks
# (a)); cards review/active/kokomi-card-paper-2026-10-12.md (ruled 2026-10-12).
# ---------------------------------------------------------------------------

def add_jellyfish(state: CombatState, card_id: str, amount: int,
                  upgraded: bool = False) -> int:
    """Add `amount` Stings or Wards to her hand: generated, Ethereal and
    Exhausting (their own rows print both), upgraded where the caller says
    so. A full hand stops them, this engine's `_add_token` rule. Returns how
    many arrived. `KokomiCards.AddJellyfish` is the twin."""
    if not live(state) or amount <= 0:
        return 0
    from tier0.content import loader, upgrades      # late import: cycle
    from tier0.engine import effects                # late import: cycle
    cid = card_id + (upgrades.SUFFIX if upgraded else "")
    added = 0
    for _ in range(int(amount)):
        if len(state.player.hand) >= C.MAX_HAND_SIZE:
            break
        effects._add_token(state, loader.get_card(cid), "hand")
        added += 1
    state.emit("kk_jellyfish_added", card=cid, amount=added)
    return added


def generated_companions(state: CombatState, rarity: str) -> list[Card]:
    """The Companions her generators may make: the run's companion roster,
    Inazuma's, of `rarity`, less someone else's Personals -- Klee's
    `random_companion_pool` narrowed to the nation and the rarity. Gorou's
    four are her own cards since the re-founding and are not in the roster.
    `KokomiCompanionPlan.Generated` is the twin."""
    from tier0.engine import klee_overhaul          # late import: cycle
    return [c for c in klee_overhaul.random_companion_pool(state)
            if c.rarity == rarity
            and getattr(c, "nation", None) == GENERATED_NATION]


def _generate(card: Card) -> Card:
    """A generated Companion is Ethereal and Exhausts when played or carried
    out (paper sec.1 rule 5). `KokomiCompanionPlan.Generate` is the twin."""
    import copy                                     # stdlib, local by habit
    made = copy.deepcopy(card)
    made.ethereal = True
    made.exhaust = True
    return made


def add_companions(state: CombatState, amount: int,
                   upgraded: bool = False) -> int:
    """ORDERS FROM THE SHRINE, WATATSUMI MUSTER: "Add N random Common Inazuma
    Companion cards to your hand. They are Ethereal." Distinct cards (Klee's
    Tag Along roll), upgraded on the upgraded card.
    `KokomiCards.AddCompanions` is the twin."""
    if not live(state) or amount <= 0:
        return 0
    from tier0.content import loader, upgrades      # late import: cycle
    pool = generated_companions(state, "common")
    if not pool:
        return 0
    picks = state.rng.sample(pool, min(int(amount), len(pool)))
    added = 0
    for pick in picks:
        if len(state.player.hand) >= C.MAX_HAND_SIZE:
            break
        source = (loader.get_card(pick.id + upgrades.SUFFIX)
                  if upgraded and upgrades.has_upgrade(pick.id) else pick)
        card = _generate(source)
        state.player.hand.append(card)
        state.emit("kk_companion_added", card=card.id)
        added += 1
    return added


def call_the_generals(state: CombatState) -> int:
    """CALL THE GENERALS: "Choose 1 of 3 random Rare Inazuma Companion cards.
    Add it to your hand. It is Ethereal. It costs 0 this turn." The pilot
    keeps the first offered (all three are Rare; a fixed rule, so a replay
    keeps what it kept). The cost-0 rider is Kokomi round 2's (2026-10-12),
    the base game's Discovery template (`free_this_turn`, swept at the turn
    boundary). `KokomiCards.CallTheGenerals` is the twin."""
    if not live(state):
        return 0
    pool = generated_companions(state, "rare")
    if not pool:
        return 0
    offered = state.rng.sample(pool, min(GENERALS_OFFERED, len(pool)))
    state.emit("kk_generals_offered", cards=[c.id for c in offered])
    if len(state.player.hand) >= C.MAX_HAND_SIZE:
        return 0
    card = _generate(offered[0])
    card.free_this_turn = True
    state.player.hand.append(card)
    state.emit("kk_companion_added", card=card.id)
    return 1


def reserves(state: CombatState) -> Optional[Card]:
    """RESERVES: "Put a card from your Exhaust Pile into your hand. It is
    Ethereal." The pick is the pilot's (`effects._best_card`, the recall
    screens' ranking, an INSTRUMENT SURFACE); an empty pile is a no-op.
    `KokomiCards.Reserves` is the twin."""
    from tier0.engine import effects                # late import: cycle
    from tier0.engine.state import remove_instance
    if not live(state):
        return None
    pool = list(state.player.exhaust_pile)
    if not pool or len(state.player.hand) >= C.MAX_HAND_SIZE:
        state.emit("kk_reserves", card=None)
        return None
    pick = effects._best_card(pool)
    remove_instance(state.player.exhaust_pile, pick)
    pick.ethereal = True
    state.player.hand.append(pick)
    state.emit("kk_reserves", card=pick.id)
    return pick


def write_free(state: CombatState, card: Card) -> bool:
    """GRAND DESIGN's write: the card is played on the Bake-Kurage for free
    -- out of her hand, through the one free-play door
    (`combat.resolve_free_play`), and its own Plan branch writes it, the path
    a drag onto the jellyfish takes. `KokomiRefounding.WriteFree` is the
    twin."""
    from tier0.engine import combat                 # late import: cycle
    from tier0.engine.state import remove_instance
    if not live(state) or not can_be_written(card):
        return False
    if not remove_instance(state.player.hand, card):
        return False
    was = state.kk_free_write
    state.kk_free_write = card
    try:
        combat.resolve_free_play(state, card)
    finally:
        state.kk_free_write = was
    return True


def grand_design(state: CombatState, card: Card, amount: int) -> int:
    """GRAND DESIGN (the re-founding's card under the old name): "Write up to
    3 cards from your hand as Plans. They cost 0." The pilot writes the
    writable cards in hand, most expensive first, up to `amount` (an
    INSTRUMENT SURFACE: the player chooses in the mod).
    `KokomiCards.GrandDesign` is the twin."""
    if not live(state) or amount <= 0:
        return 0
    from tier0.engine import combat                 # late import: cycle
    picks = [c for c in list(state.player.hand)
             if c is not card and can_be_written(c)]
    picks.sort(key=lambda c: -(combat.card_cost(state, c)
                               if c.cost != "X" else 0))
    written = 0
    for pick in picks[:int(amount)]:
        if write_free(state, pick):
            written += 1
    state.emit("kk_grand_design", written=written)
    return written


def carry_out_companion(state: CombatState, card: Optional[Card]) -> None:
    """A WRITTEN COMPANION, CARRIED OUT (design pass pick 4 (a)): the
    Bake-Kurage applies Hydro to the front enemy, then a free COPY of the
    Companion is played -- aimed at that enemy when it aims at one -- and
    Exhausts. Crystal Collapse's copy (`_play_copy`) with the Hydro first, so
    a Companion that hits reacts with it and one that only buffs or blocks
    carries the Hydro alone. No front enemy: no Hydro, and the copy plays at
    whoever its own aim finds. `KokomiCompanionPlan.CarryOut` is the twin."""
    import copy as _copy

    from tier0.engine import effects, reactions     # late import: cycle
    if card is None:
        state.emit("plan_companion_empty")
        return
    front = front_enemy(state)
    if front is not None:
        reactions.resolve_hit(state, front, "hydro", 0, "plan")
    state.emit("plan_companion", card=card.id,
               target=None if front is None else front.name)
    was = state.kurage_aim
    state.kurage_aim = front
    try:
        effects._free_play(state, _copy.deepcopy(card), force_exhaust=True)
    finally:
        state.kurage_aim = was


def note_written(state: CombatState, card: Card) -> None:
    """A Plan was just written by `card`. WATCHFUL SHOAL pays Block for an
    Ethereal card, WATATSUMI RESISTANCE a Sting for a Companion card.
    `KokomiRefounding.OnWritten` is the twin."""
    if not live(state) or card is None:
        return
    p = state.player
    if card.is_ethereal:
        n = int(p.powers.get(WATCHFUL_SHOAL, 0))
        if n:
            # RAW, like every power-sourced Block in the arm (NC-11).
            p.block += n
            state.emit("block", amount=n)
            state.emit("plan_watchful_shoal", amount=n)
    from tier0.engine import companion_hexerei      # late import: cycle
    if companion_hexerei.counts_as_companion(state, card):
        watatsumi_resistance(state)


def note_carried_out(state: CombatState, entry: PlanEntry) -> None:
    """A Plan was just carried out. COORDINATED TIDE hits the front enemy for
    an Ethereal card; ENDLESS SHOAL adds a copy of a Sting or Ward to her
    hand. Once per carry-out, either line.
    `KokomiRefounding.OnCarriedOut` is the twin."""
    import copy as _copy

    from tier0.engine import effects                # late import: cycle
    card = entry.source
    if not live(state) or card is None:
        return
    p = state.player
    if card.is_ethereal:
        n = int(p.powers.get(COORDINATED_TIDE, 0))
        front = front_enemy(state)
        if n and front is not None:
            state.emit("plan_coordinated_tide", target=front.name, amount=n)
            effects.deal_damage_to_enemy(state, front, n, element="hydro",
                                         source="plan", powered=False)
    base = card.id.rstrip("+")
    if base in (STING_ID, WARD_ID):
        n = int(p.powers.get(ENDLESS_SHOAL, 0))
        for _ in range(n):
            if len(p.hand) >= C.MAX_HAND_SIZE:
                break
            effects._add_token(state, _copy.deepcopy(card), "hand")
            state.emit("plan_endless_shoal", card=card.id)


def grand_strategist(state: CombatState) -> None:
    """GRAND STRATEGIST: "Whenever a Plan causes an Elemental Reaction, deal 5
    damage to ALL enemies." Called from `effects.companion_overhaul_reaction`,
    the one site a reaction resolves; a reaction inside a carry-out
    (`state.kk_carrying_out`) was caused by the Plan. Unelemented, power
    damage. `KokomiRefounding.OnReaction` is the twin."""
    if not live(state) or not state.kk_carrying_out:
        return
    n = int(state.player.powers.get(GRAND_STRATEGIST, 0))
    if n <= 0:
        return
    from tier0.engine import effects                # late import: cycle
    state.emit("plan_grand_strategist", amount=n)
    for enemy in list(state.living_enemies):
        effects.deal_damage_to_enemy(state, enemy, n, element=None,
                                     source="plan", powered=False)


def dawn_tide(state: CombatState) -> None:
    """DAWN TIDE: "At the start of your turn, the Bake-Kurage applies Hydro to
    ALL enemies." After the morning's Plans (`combat._player_turn`, after
    `resolve_all`), so the Hydro stands for her turn.
    `DawnTidePower.Signal` is the twin."""
    if not live(state) or not state.player.powers.get(DAWN_TIDE, 0):
        return
    from tier0.engine import reactions              # late import: cycle
    for enemy in list(state.living_enemies):
        if enemy.alive:
            reactions.resolve_hit(state, enemy, "hydro", 0, "dawn_tide")
    state.emit("plan_dawn_tide")


def turn_start_generators(state: CombatState) -> None:
    """KURAGE BLOOM ("At the start of your turn, add a Sting to your hand")
    and SANGONOMIYA'S ORDERS ("... add a random Common Inazuma Companion card
    to your hand. It is Ethereal."), copies adding one each, after the
    morning's Plans. `KurageBloomPower` and `SangonomiyasOrdersPower` are the
    twins."""
    if not live(state):
        return
    p = state.player
    bloom = int(p.powers.get(KURAGE_BLOOM, 0))
    if bloom:
        add_jellyfish(state, STING_ID, bloom, upgraded=False)
    orders = int(p.powers.get(SANGONOMIYAS_ORDERS, 0))
    if orders:
        add_companions(state, orders, upgraded=False)


def casket_block(state: CombatState) -> None:
    """THE TAMAKUSHI CASKET (the re-founding, 2026-10-12): "At the end of your
    turn, if a Plan is waiting, gain 3 Block." Its hook, at this engine's
    `BeforeSideTurnEnd` on her side; raw relic Block (Orichalcum's
    `ValueProp.Unpowered`). `TamakushiCasket.BeforeSideTurnEnd` is the
    twin."""
    from tier0.content import loader                # late import: cycle
    if not live(state):
        return
    if loader.OVERHAUL_CASKET_HOOK not in state.player.relic_hooks:
        return
    if not state.kk_plan_queue:
        return
    n = int(C.KOKOMI_OVERHAUL_CASKET_BLOCK)
    state.player.block += n
    state.emit("block", amount=n)
    state.emit("casket_block", amount=n, waiting=len(state.kk_plan_queue))

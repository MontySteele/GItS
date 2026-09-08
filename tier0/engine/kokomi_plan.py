"""THE PLAN (QUARANTINED, `C.KOKOMI_OVERHAUL`) -- the sim twin of
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
from tier0.engine import powers
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
#: `EB-643` (R265) ADDED THREE, and every one of them is about the QUEUE rather
#: than about a number: two RIDERS on the entry that follows this one in the
#: same drain (`next_plan_double_damage`, `next_plan_extra_carry_out`) and a
#: draw that counts the drain it is carried out in
#: (`draw_per_plan_this_turn`, `EB-679`). All three are PLAN-ONLY by
#: construction -- each names a drain, and a now-line spelling would name a
#: drain that is not running.
PLAN_KINDS = frozenset((
    "draw", "energy", "block", "mend", "damage", "damage_quarter_max_hp",
    "damage_per_companion_last_turn", "apply_power",
    "play_copy_of_companion", "block_per_plan_this_morning",
    "draw_per_plan_this_turn", "next_plan_double_damage",
    "next_plan_extra_carry_out",
    # `EB-655` (pool pass three), BATTLE PLAN. See `NEXT_ATTACK_BONUS`.
    "next_attack_damage",
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
    "next_attack_damage",
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
    "damage", "damage_quarter_max_hp", "damage_per_companion_last_turn",
    "apply_power"))

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
PLAN_ONLY_OPS = frozenset(("damage_per_companion_last_turn",
                           "play_copy_of_companion",
                           "block_per_plan_this_morning",
                           # `EB-643`. The three drain-positional clauses. Each
                           # one names a place in a running drain -- "the next
                           # Plan", "after this one" -- so a now-line spelling
                           # would ask about a drain that is not running and
                           # answer nothing, every time.
                           "draw_per_plan_this_turn",
                           "next_plan_double_damage",
                           "next_plan_extra_carry_out",
                           # `EB-655`, BATTLE PLAN. The rider is what the
                           # carry-out pays: a now-line spelling would be a
                           # different, unpriced card that buffed an Attack on
                           # the turn it was played.
                           "next_attack_damage"))

#: Tide Wall's clause (`EB-335`, R246 pick 2): "Gain N Block for each Plan the
#: Bake-Kurage carries out this morning." PLAN-ONLY by construction -- the
#: count it multiplies is a fact about a morning, and a now-line spelling would
#: read a number that is zero every time it is asked.
BLOCK_PER_PLAN = "block_per_plan_this_morning"

#: `EB-679` (pool pass four), SCOUT AHEAD: "draw 1 card for each Plan carried
#: out this turn", ITSELF INCLUDED. It used to count the carry-outs still to
#: come, which made the card's whole value its POSITION in the queue -- r26's
#: lane never wrote it, because a row worth 2 written first and 0 written last
#: competed for its slot with Plans that always paid. The count is now the
#: WHOLE DRAIN, so the card answers the same number wherever it sits: written
#: alone it draws 1, written with two others it draws 3.
#:
#: THE DRAIN AND NOT THE TURN, read literally: a morning and a dusk are two
#: drains and each counts its own, which is `_drain`'s reading of "the next
#: Plan" applied to a count. Change of Plans carries one entry out and pays 1.
#: `amount` is the RATE per carry-out, the shape `block_per_plan_this_morning`
#: above already has.
DRAW_PER_PLAN_THIS_TURN = "draw_per_plan_this_turn"

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
TREATISE = "kk_treatise"                     # draw N once a turn, on a Plan
SONG_OF_PEARLS = "kk_song_of_pearls"         # N Block once a turn, on a Plan
CLOUDS_LIKE_WAVES = "kk_clouds_like_waves"   # Block per debuff she applies
GENERALS_BANNER = "kk_generals_banner"       # Weak to the front, once a turn
#: Nereid's Ascension (`EB-492`). A MARKER AND NOT A WINDOW: the Rare is a
#: Power costing 2 that lasts the fight, so there is no duration to tick and
#: `carry_out_times` reads only whether it is worn. It replaced a `plan_twice`
#: CLAUSE, which spent the very morning it was meant to pay for -- and that op
#: is retired rather than left standing with no row to spell it.
#: `NereidsAscensionPower` is the twin.
NEREIDS_ASCENSION = "kk_nereids_ascension"
#: Rally's grant. ONE STACK, ALWAYS -- the card says "costs 1 less", not
#: "per Rally" -- and it is consumed by the next Companion play.
NEXT_COMPANION_DISCOUNT = "kk_next_companion_discount"
#: `EB-668` (`EB-655` reopened), BATTLE PLAN's carry-out: "the next Attack you
#: play face-up this turn deals 4 additional damage". Written by a PLAN, so it lands
#: on the morning the draw lands on -- and a card WRITTEN on the Bake-Kurage is
#: not a face-up play, so a write neither takes the bonus nor spends it. That
#: last clause is what stops the reward from paying for more writing, which is
#: the pass's thesis.
#:
#: A RIDER AND NOT A DISCOUNT, which is the whole of `EB-668`: the grant is now
#: read where the PLAY is known (`effects.flat_attack_bonus` here,
#: `ModifyDamageAdditive` there) instead of at a cost seam the mod cannot make
#: target-aware. `NextAttackDamagePower` is the twin.
NEXT_ATTACK_BONUS = "kk_battle_plan_rider"
#: Shell Guard's window (`EB-335`). THE AMOUNT IS THE BLOCK PER STRIKE, not a
#: number of turns: "until your next turn, whenever the Tamakushi Casket
#: strikes, gain 3 Block". `close_shell_guard` is the one place it ends, and
#: its header says which end of the turn that is and why.
SHELL_GUARD = "kk_shell_guard"

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
            if not isinstance(amount, int) or isinstance(amount, bool) \
                    or amount <= 0:
                return f"plan clause {op} amount must be a positive literal int"
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
    return bool(C.KOKOMI_OVERHAUL and state.player.character_id == "kokomi")


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
    """
    if not live(state) or not card.plan:
        return False
    if not card.effects:
        return True
    return not any(_intends_to_attack(e) for e in state.living_enemies)


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


def hers(state: CombatState, card: Optional[Card], amount: int) -> int:
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

    C# twin: `KokomiPlan.Hers`.
    """
    folded = _enchanted(card, amount)
    if folded <= 0:
        return folded
    return folded + int(state.player.powers.get("strength", 0))


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
    body = [dict(c, amount=hers(state, owner, int(c.get("amount", 0))))
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
    # `EB-643`, DUSK. A property of the WRITING CARD's printed face and not of
    # its clauses (`plan_dusk:` on the row), so it is read off the card here
    # and carried on the entry: the queue is one queue, and what a dusk entry
    # changes is WHEN it is drained (`resolve_dusk`, at the end of this turn,
    # before the enemies act) and nothing else about it. Moon's Reflection
    # contributes another card's LINE and not its face, so a replayed line is
    # never dusk -- the `clauses is not None` test is that sentence.
    dusk = bool(getattr(card, "plan_dusk", False)) and clauses is None
    entry = PlanEntry(card_id=card.id, clauses=body, card=held, label=label,
                      dusk=dusk)
    state.kk_plan_queue.append(entry)
    state.emit("plan_written", card=card.id, clauses=len(body),
               queued=len(state.kk_plan_queue),
               holds=None if held is None else held.id,
               dusk=dusk)


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

    DUSK ENTRIES CANNOT BE HERE. `resolve_dusk` drains them at the end of the
    turn they were written on, so by the next morning the queue holds only
    entries that waited for one -- which is what makes "dusk entries are not
    counted against the morning cap" true by construction rather than by a
    filter.
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


def _drain(state: CombatState, due: list[PlanEntry], why: str) -> None:
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
    # `EB-679`, SCOUT AHEAD's count: THE WHOLE DRAIN, itself included, read
    # ONCE before the first clause runs. Order-independence is the point of
    # the redesign -- a reader whose number depends on where in the queue it
    # sits is a card whose value is its position, which is what r26's lane
    # would not spend a slot on -- so this is computed here rather than per
    # entry, the discipline `resolve_all` already keeps for
    # `kk_plans_this_morning`.
    #
    # ONE EXTRA FOR NEREID'S ASCENSION, the same term `resolve_all` writes and
    # for the same reason: the Rare carries the FIRST entry of a drain out
    # twice, and every reader in this arm counts CARRY-OUTS (`EB-501`). It
    # deliberately does NOT fold in a `next_plan_extra_carry_out` written
    # inside this drain -- that rider is not on the board when the number is
    # asked, which is the reading the old per-entry term already took.
    drain_plans = len(due) + (
        1 if due and carry_out_times(state) > 1 else 0)
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
        times = (carry_out_times(state) if index == 0 else 1)             + (1 if extra else 0)
        for _ in range(times):
            if state.over or not state.player.alive:
                return
            wrote = _resolve_entry(state, entry, why=why,
                                   double_damage=double,
                                   drain_plans=drain_plans)
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


def promise_tide_chart(state: CombatState, per: int, flat: int) -> None:
    """Tide Chart is played: the draw is OWED, and paid next morning.

    NOTHING IS DRAWN HERE, which is the whole redesign (`EB-478`, R257). The
    old row read the queue at PLAY time and drew zero on three plays out of
    four, because a seat plays its cheap cards before it writes its Plans. The
    promise is written down instead and read after the carry-outs, when the
    number it multiplies is a fact rather than a guess.

    TWO NUMBERS ACCUMULATE. A second copy played the same turn adds its own
    `per` and its own flat, so two base copies pay twice the morning's depth
    and an upgraded copy beside a base one pays its extra 1 once.
    `KokomiPlan.PromiseDraw`'s twin.
    """
    if not live(state):
        return
    state.kk_tide_chart_per += int(per)
    state.kk_tide_chart_flat += int(flat)
    state.emit("tide_chart_promised", per=int(per), flat=int(flat))


def pay_tide_charts(state: CombatState) -> None:
    """THE MORNING AFTER: every Tide Chart promise is paid, in one draw.

    CALLED FROM `combat._player_turn` ONE LINE AFTER `resolve_all`, which is
    what the face says -- "after the Bake-Kurage carries out its Plans" -- and
    is where `ProtoBakeKuragePower.AfterPlayerTurnStart` calls
    `KokomiPlan.PayPromisedDraws`. Unconditional, because `resolve_all` returns
    early on an empty queue and a promise made on a turn that banked nothing
    still pays its flat: the upgraded row draws 1 on an empty morning and the
    base row draws 0, which is the ruled reading.

    THE COUNT IS THE MORNING'S DEPTH (`kk_plans_this_morning`), the same number
    Tide Wall reads and for the same reason -- it is written at the drain and
    cleared by `roll_turn`, so a morning with no Plans reads an honest zero
    rather than yesterday's.
    """
    if not live(state):
        return
    per, flat = state.kk_tide_chart_per, state.kk_tide_chart_flat
    if not per and not flat:
        return
    # CLEARED BEFORE THE DRAW, not after: a drawn card can be played by nothing
    # here, but a promise that survived its own payment would pay twice on the
    # next morning, and clearing first is the shape that cannot.
    state.kk_tide_chart_per = 0
    state.kk_tide_chart_flat = 0
    cards = flat + per * state.kk_plans_this_morning
    state.emit("tide_chart_paid", cards=cards,
               plans=state.kk_plans_this_morning)
    if cards > 0:
        state.draw(cards)


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
    _resolve_entry(state, entry, why="change_of_plans")


def resolve_dusk(state: CombatState) -> None:
    """`EB-643`, DUSK: "the Bake-Kurage carries this Plan out at the end of
    this turn, before enemies act."

    THE HOOK IS `combat._player_turn`'s TURN-END BLOCK, beside
    `klee_overhaul.turn_end` and after it -- this engine's twin of
    `BeforeSideTurnEnd` on the player side, which is where
    `ProtoBakeKuragePower.BeforeSideTurnEnd` runs the same drain. WHY THAT
    POINT and not one of the others, since a turn end has several:

      * AFTER the hand's own end-of-turn triggers (`player_turn_end_triggers`),
        so a Dusk Block is the LAST thing on her side of the boundary and
        nothing later in the turn recomputes it;
      * BEFORE `_settle_phases`, so a Dusk carry-out that kills settles the
        board it killed, exactly as Sparks 'n' Splash's turn-end burst does one
        arm over;
      * BEFORE the enemies act, which is the printed promise and the only
        clause of the sentence a card can tell apart -- a Dusk Block that
        landed after the swing would be a face that lies.

    A DUSK CARRY-OUT IS A CARRY-OUT. It goes through `_resolve_entry` like
    every other, so Treatise draws on it, Song of Pearls blocks on it, the
    `plan_carried_out` event fires and Sango Isshin's condition is met.

    IT DOES NOT TOUCH `kk_plans_this_morning`, and that is the one place the
    two drains differ on purpose: Tide Wall, Well Laid and Tide Chart all print
    "this morning", and an evening is not one.

    NOT CAPPED. `C.KOKOMI_PLAN_CAP` is a rule about the MORNING -- "at most N
    Plans a morning, the rest wait" -- and a Dusk Plan has already waited for
    nothing.
    """
    if not live(state):
        return
    due = [e for e in state.kk_plan_queue if e.dusk]
    if not due:
        return
    # THE DUSK ENTRIES LEAVE THE QUEUE AND THE OTHERS STAY, in order. Taken
    # before the first clause runs for `resolve_all`'s reason: a Dusk Plan
    # whose body writes another Plan must not carry its own child out on the
    # same boundary.
    state.kk_plan_queue[:] = [e for e in state.kk_plan_queue if not e.dusk]
    state.emit("plan_resolve_dusk", plans=len(due))
    _drain(state, due, why="dusk")


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


def _resolve_entry(state: CombatState, entry: PlanEntry, why: str,
                   double_damage: bool = False,
                   drain_plans: int = 1) -> tuple[bool, bool]:
    """ONE PLAN CARRIED OUT -- the unit Treatise and Song of Pearls are priced
    in. "Whenever the jellyfish carries out a Plan" is once per ENTRY, and the
    notify at the bottom is the only place it fires, so Change of Plans' early
    resolution pays them exactly as the morning's does.

    `double_damage` and `drain_plans` ARE THE DRAIN'S, and they are parameters
    rather than reads for `ResolveEntry`'s own reason one file over: nothing
    about the state this entry sits in says which entry ran before it or how
    deep the drain around it is, so the caller is the only thing that knows and
    the caller says. `resolve_front`'s defaults are the honest answer for a
    drain of one -- no rider was doubled, and one Plan was carried out.

    IT RETURNS THE RIDERS THIS ENTRY WROTE, `(double, extra)`, because the
    clause that writes one is inside the loop below and the drain that spends
    it is outside: handing them back is what keeps "the next Plan" a fact about
    the DRAIN rather than a flag on the state that could outlive it.
    """
    state.emit("plan_carried_out", card=entry.card_id, why=why,
               clauses=len(entry.clauses))
    wrote = [False, False]
    for clause in entry.clauses:
        if state.over or not state.player.alive:
            break
        _resolve_clause(state, entry, clause, double_damage=double_damage,
                        drain_plans=drain_plans, wrote=wrote)
    _note_plan_resolved(state)
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


def _note_plan_resolved(state: CombatState) -> None:
    """The plan bus: Treatise draws and Song of Pearls blocks, ONCE A TURN.

    ONCE A TURN SINCE 2026-09-02, [USER]'s own ruling off live play: "Treatise
    looks too good (one draw per turn if a Plan fired might be ok; one draw per
    Plan is too abuseable)", and "Likewise" of Song of Pearls, which is the
    same card in Block. The cards still ride the PLAN and not the turn -- a
    morning she planned nothing for pays nothing -- and the turn is only the
    cap.

    ONE PAYMENT PER PLAN, NOT PER CLAUSE, is unchanged underneath that cap:
    War Council prints two clauses and is one Plan. That is true because of
    WHERE this is called (the tail of `_resolve_entry`) rather than because of
    anything here.
    """
    p = state.player
    # Sango Isshin's condition, written here because this is the one place a
    # Plan is carried out -- dawn, Change of Plans and Moon all reach it.
    state.kk_plan_carried_out_this_turn = True
    n = p.powers.get(TREATISE, 0)
    if n and claim_once_per_turn(state, TREATISE):
        state.draw(n)
        state.emit("plan_treatise", amount=n)
    n = p.powers.get(SONG_OF_PEARLS, 0)
    if n and claim_once_per_turn(state, SONG_OF_PEARLS):
        # POWERED, and rule 3 is why: "your Strength and Dexterity count, since
        # the plans are hers". `SongOfPearlsPower` gains its Block at
        # `ValueProp.Move` and its header records the same argument -- the
        # alternative would make Read the Field's planned Block and this card's
        # Block from the same morning scale differently.
        amount = powers.modify_block_gained(p, n)
        p.block += amount
        state.emit("block", amount=amount)
        state.emit("plan_song_of_pearls", amount=amount)


def _resolve_clause(state: CombatState, entry: PlanEntry,
                    clause: dict, double_damage: bool = False,
                    drain_plans: int = 1,
                    wrote: Optional[list] = None) -> None:
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
    elif op == "block":
        # POWERED (`ValueProp.Move`), rule 3, and the same funnel a card's own
        # printed Block goes through -- Frail bites it and Dexterity feeds it.
        # Draft 2's planned Block was `Unpowered`; draft 6 states the opposite
        # rule in the brief itself.
        gained = powers.modify_block_gained(p, amount)
        p.block += gained
        state.emit("block", amount=gained)
    elif op == BLOCK_PER_PLAN:
        # TIDE WALL (`EB-335`, R246 pick 2): "Gain N Block for each Plan the
        # Bake-Kurage carries out this morning." The count is the morning's
        # whole depth, taken at the drain (`resolve_all`), so this card's Block
        # does not depend on where in the queue it was written -- and it lands
        # with the rest of the morning, which is what makes it guard the turn a
        # Defend would have guarded, one turn later and bigger for the wait.
        #
        # POWERED, the same funnel the printed `block` clause above takes:
        # rule 3 says her Dexterity counts and Frail bites, and two Block
        # clauses of one morning scaling differently is exactly what
        # `SongOfPearlsPower`'s header refuses.
        #
        # A MORNING THAT HELD NOTHING PAYS NOTHING, and it is a printed no-op
        # rather than a failure: `Change of Plans` can carry this Plan out on a
        # turn whose own morning was empty, and zero times three is the honest
        # answer to "for each Plan carried out this morning".
        gained = powers.modify_block_gained(
            p, amount * state.kk_plans_this_morning)
        if gained:
            p.block += gained
            state.emit("block", amount=gained)
        state.emit("plan_tide_wall", amount=gained,
                   plans=state.kk_plans_this_morning)
    elif op == DRAW_PER_PLAN_THIS_TURN:
        # SCOUT AHEAD (`EB-679`): "draw 1 card for each Plan carried out this
        # turn", itself included. `drain_plans` is the whole drain's count --
        # see `_drain`, which reads it once -- and the rate is the printed
        # amount, the shape Tide Wall's clause above already has. Change of
        # Plans carries ONE entry out and pays 1, which is the face read
        # literally: this Plan was carried out.
        cards = amount * int(drain_plans)
        state.emit("plan_scout_ahead", cards=cards, plans=int(drain_plans))
        if cards > 0:
            state.draw(cards)
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
    elif op == "next_attack_damage":
        # BATTLE PLAN's carry-out (`EB-655`, `EB-668`). One stack, always, and
        # the same switch-not-counter reading Rally's grant keeps: the face
        # says "deals 4 additional damage" and not "per Plan", so a morning that
        # carries out two Battle Plans still buffs one Attack. See
        # `next_attack_bonus`.
        next_attack_bonus(state)
    elif op == "mend":
        effects.mend(state, amount)
    elif op == "damage":
        _hit(state, clause, amount, entry=entry, double=double_damage)
    elif op == "damage_quarter_max_hp":
        _hit(state, clause, quarter_of_max_hp(state), entry=entry,
             double=double_damage)
    elif op == "damage_per_companion_last_turn":
        # Chain of Command. "LAST TURN" IS READ AT CARRY-OUT: the Plan was
        # written on turn N and resolves at the top of N+1, and
        # `combat._player_turn` has already rolled the counter by then -- so
        # what this reads is turn N, the turn the player was looking at when
        # they wrote it. `KokomiOverhaulLedger.RollTo` is the same handover.
        _hit(state, clause, amount * state.companion_plays_last_turn,
             entry=entry, double=double_damage)
    elif op == "apply_power":
        _debuff(state, clause, clause["power"], amount, entry=entry)
    elif op == REPLAY_EXHAUSTED:
        _replay(state, entry.card)
    elif op == PLAY_COPY_OF_COMPANION:
        _play_copy(state, entry.card)
    else:                                   # unreachable: shape-checked at load
        raise ValueError(f"unknown plan clause {op!r}")


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
    applied, so the Tamakushi Casket answers it and The Clouds Like Waves pays
    for it. Draft 6 gives the jellyfish the arithmetic, not the authorship.

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
    """A planned Weak or Vulnerable, applied BY HER -- so the Casket answers it
    and The Clouds Like Waves pays for it, exactly as they do for a debuff off
    a card she played.

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

    SHELL GUARD'S WINDOW IS NOT ON THIS LINE, deliberately: it has to survive
    the morning it is read in, so it is closed one step later
    (`close_shell_guard`, whose header carries the argument).
    """
    state.companion_plays_last_turn = state.companion_plays_this_turn
    state.kk_once_per_turn.clear()
    state.kk_plan_carried_out_this_turn = False
    # `EB-335`. Tide Wall's morning count, cleared HERE and written a few lines
    # later by `resolve_all` -- which runs after this in `combat._player_turn`,
    # so a morning that drains nothing reads an honest zero rather than
    # yesterday's depth.
    state.kk_plans_this_morning = 0
    # Crystal Collapse's "this turn". It is CLEARED rather than handed over:
    # the capture happens while the Plan is written, so what survives the
    # boundary is the captured card on the entry and never the list.
    state.kk_companions_this_turn.clear()


# ---------------------------------------------------------------------------
# THE HOOKS
# ---------------------------------------------------------------------------

def note_companion_played(state: CombatState, card: Card) -> None:
    """"You played a Companion card" -- The General's Banner's hook.

    ONCE A TURN SINCE 2026-09-02 ([USER], live: "The General's Banner applies
    a LOT of Weak. Probably too strong."). It used to pay per PLAY, so a hand
    full of Companions was a stack of Weak nothing else in the arm can match.

    THE COMPANION COUNTER IS NOT CAPPED WITH IT: `companion_plays_this_turn` is
    moved by `combat._finish_play` for every play, because that count is Chain
    of Command's. Only the Weak is capped here.

    It rides `combat._finish_play`, the one site a manual play and an auto-play
    both enter, beside the counter Chain of Command reads -- so "she played a
    Companion" has ONE definition in this engine and the Banner and the ledger
    cannot come to disagree about it.

    THE FRONT ENEMY IS `front_enemy`'s, the same reader a planned hit uses.
    """
    if not live(state) or not card.is_companion:
        return
    # CRYSTAL COLLAPSE'S MEMORY, recorded FIRST and unconditionally: this hook
    # is the arm's one definition of "she played a Companion card", and the
    # Banner's own `if not n` below is a fact about the Banner rather than
    # about the play. A recorder behind that return would remember nothing on
    # every board where the power is not out.
    state.kk_companions_this_turn.append(card)
    n = state.player.powers.get(GENERALS_BANNER, 0)
    if not n:
        return
    front = front_enemy(state)
    # The claim is taken AFTER the board question, so a Companion played on an
    # empty board does not spend the turn's Weak on nothing.
    if front is None:
        return
    if not claim_once_per_turn(state, GENERALS_BANNER):
        return
    state.emit("plan_banner", card=card.id, amount=n)
    powers.apply_power(state, front, "weak", n, applier=state.player)


#: Re-entrancy latch for the debuff answer. `KokomiOverhaulKit._answering`'s
#: twin, and it is not paranoia: the Casket's answer is a HYDRO hit, a Hydro
#: hit into a Cryo aura Freezes, and a boss-room Freeze applies Vulnerable --
#: a debuff she applied to an enemy. Without the latch the relic would answer
#: its own answer until the stack ran out. A plain module global because the
#: whole event is synchronous and this engine is single-threaded, cleared in a
#: `finally` so a throw inside a strike cannot leave the relic permanently
#: deaf. (`state` would be the tidier home; the C# uses a static and the two
#: are the same object here, since one fight is one call stack.)
_answering = False


def note_debuff_applied(state: CombatState, target, name: str, stacks: int,
                        applier) -> None:
    """"SHE APPLIED A DEBUFF TO AN ENEMY", once, for both things that read it.

    `KokomiOverhaulKit.IsHerDebuffOnEnemy` is the C#'s one predicate, shared by
    the relic and The Clouds Like Waves Rippling so the two can never come to
    disagree about the event they both answer; this is that predicate and both
    of its consumers, on this engine's own `AfterPowerAmountChanged` twin
    (`refpowers.on_power_applied`). A card, a Plan, a companion or a reaction
    all reach it, because they all reach `powers.apply_power`.

    FOUR CLAUSES, each earning its place, the C#'s list verbatim: a positive
    amount (a debuff ticking DOWN is not one being applied); a name in
    `ENEMY_DEBUFFS` (this engine's stand-in for `PowerType.Debuff`, and its
    limits are documented there); an ENEMY carrier (her own Weak is not a
    debuff she applied to an enemy); and HER as the applier.
    """
    global _answering

    if not live(state) or stacks <= 0:
        return
    if name not in DEBUFF_APPLICATIONS:
        return
    if not isinstance(target, Enemy) or not target.alive:
        return
    # HER, and STRICTLY her -- `if (applier != kokomi) return false;`. The
    # applier reaching this function has already been through
    # `refpowers.on_power_applied`'s inference, which fills in the player for
    # the unnamed player-turn cases and leaves an enemy intent's own applier
    # alone, so "unknown" never has to be read as "hers" here.
    if applier is not state.player:
        return

    # THE CLOUDS LIKE WAVES RIPPLING, PER APPLICATION AND NOT PER STACK: War
    # Council's "apply 1 Weak to each" over three enemies is three payouts and
    # one card applying 2 Weak to one enemy is one. It does NOT take the latch
    # -- the C# power does not either -- so Block gained off a Freeze the
    # Casket caused is intended rather than an oversight.
    n = state.player.powers.get(CLOUDS_LIKE_WAVES, 0)
    if n:
        gained = powers.modify_block_gained(state.player, n)
        state.player.block += gained
        state.emit("block", amount=gained)
        state.emit("plan_clouds_like_waves", amount=gained, power=name)

    if _answering or "kokomi_overhaul_casket" not in state.player.relic_hooks:
        return
    _answering = True
    try:
        casket_strike(state, target)
    finally:
        _answering = False


def casket_strike(state: CombatState, target: Enemy) -> None:
    """THE TAMAKUSHI CASKET's strike: "Whenever you apply a debuff to an enemy,
    the Bake-Kurage strikes that enemy for 2 Hydro damage."

    THE JELLYFISH IS THE DEALER, and the C# calls that a reading rather than a
    detail: the slice says "it strikes that enemy for 2", so the applier handed
    to the shared elemental pipeline is the PET. A pet carries no Strength, so
    the 2 is a flat 2 -- which is what keeps this the relic's number instead of
    the best Strength payoff in her pool, now that draft 6 gives her Strength
    back. `powered=False` is that sentence in this engine.

    THE HIT IS OTHERWISE REAL: Block applies, Vulnerable applies, the aura
    lands and its reaction fires, because it is the same funnel every other
    non-attack hit here goes through.

    THE NUMBER IS `C.KOKOMI_OVERHAUL_CASKET_STRIKE`, mirrored BY VALUE against
    `KokomiOverhaulLaw.CasketStrike` by `tools/lint_constant_parity.py`.
    """
    from tier0.engine import effects                # late import: cycle

    if not target.alive:
        return
    state.emit("casket_strike", target=target.name,
               amount=C.KOKOMI_OVERHAUL_CASKET_STRIKE)
    effects.deal_damage_to_enemy(
        state, target, C.KOKOMI_OVERHAUL_CASKET_STRIKE, element="hydro",
        source="casket", powered=False)
    _pay_shell_guard(state)


def _pay_shell_guard(state: CombatState) -> None:
    """SHELL GUARD (`EB-335`, R246 pick 2): "Until your next turn, whenever the
    Tamakushi Casket strikes, gain N Block."

    HUNG OFF THE STRIKE ITSELF and not off the debuff that caused it, which is
    the difference between this card and The Clouds Like Waves Rippling one row
    over: the Clouds pay per APPLICATION, this pays per STRIKE. They are the
    same count today, because the relic answers every application it is awake
    for -- but the relic is what the card names, so a run without the Casket
    pays nothing here and the two cards stay separable.

    AFTER THE HIT, so a strike that ends the fight has already happened. The
    Block is POWERED for the reason every other Block in this arm is (rule 3,
    `SongOfPearlsPower`'s header).
    """
    n = state.player.powers.get(SHELL_GUARD, 0)
    if not n:
        return
    gained = powers.modify_block_gained(state.player, n)
    state.player.block += gained
    state.emit("block", amount=gained)
    state.emit("plan_shell_guard", amount=gained)


def close_shell_guard(state: CombatState) -> None:
    """Shell Guard's window closes -- "until your next turn".

    THE END OF HER TURN-START RESOLUTION, and that is a reading with the
    packet's own sentence behind it: R246 pick 2 says "the morning's Plans that
    apply Weak strike it too, so the Block is there before the enemy swings"
    (`review/ruled/kokomi-overhaul-round-4c-2026-09-02.md` sec.6). The morning
    is the first thing that happens on her next turn, so a window closed by
    `roll_turn` -- which runs BEFORE the drain -- would make that sentence
    false. It is closed here instead, one line after the Plans are carried out,
    which is why `combat._player_turn` calls it there rather than beside the
    other per-turn clears.

    CALLED UNCONDITIONALLY inside the arm's turn-start block, because
    `resolve_all` returns early on an empty queue and a window that only closed
    on mornings with Plans in them would outlive its printed text.
    """
    if not live(state):
        return
    if state.player.powers.pop(SHELL_GUARD, 0):
        state.emit("plan_shell_guard_closed")


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


def cancel_last_plan(state: CombatState) -> None:
    """SECOND THOUGHTS (`EB-643`): "cancel your last Plan: its card returns to
    your hand and you regain its cost."

    THE LAST ENTRY AND NOT THE FRONT ONE, which is the whole card: Change of
    Plans hurries the OLDEST Plan and this takes back the NEWEST, so the two
    tempo cards operate on opposite ends of the same queue and a player who
    has just written the wrong Plan has a way back.

    THE CARD COMES OUT OF THE DISCARD PILE, and it is found BY ID rather than
    held on the entry. The entry keeps `card_id` for exactly this reason
    (`PlanEntry`'s own header: the writing card is kept for the log, and the
    C# keeps `Source` for the strip), and a play routes its card to the discard
    pile at the end of the play -- so the discard pile is where the card that
    wrote a queued Plan is, on the ordinary path.

    AND ON THE PATHS THAT ARE NOT ORDINARY, NOTHING RETURNS. A Plan written by
    Moon's Reflection off a card in the EXHAUST pile has a `card_id` that is
    not in the discard pile, and an Exhaust row's own card is not there either.
    The Plan is still cancelled and the Energy is still not paid, because what
    the face promises is the card and the card is not there to promise. It is
    a printed no-op of the kind this arm already has several of, not a search
    of every pile for something that looks similar.

    THE ENERGY IS THE RETURNED CARD'S CURRENT COST, read off the card that is
    coming back -- a smithed copy that cost 0 refunds 0, which is what "its
    cost" says. Nothing is refunded when no card returns, for the same reason:
    there is no "its" to read.

    AN EMPTY QUEUE IS A PRINTED NO-OP with a line on the ledger, the shape
    `resolve_front` already has.
    """
    from tier0.engine.state import remove_instance

    if not live(state):
        return
    if not state.kk_plan_queue:
        state.emit("plan_cancel_last_empty")
        return
    entry = state.kk_plan_queue.pop()
    card = next((c for c in state.player.discard_pile
                 if c.id == entry.card_id), None)
    if card is None:
        state.emit("plan_cancel_last", card=entry.card_id, returned=False,
                   energy=0)
        return
    remove_instance(state.player.discard_pile, card)
    state.player.hand.append(card)
    refund = max(0, int(card.cost))
    state.player.energy += refund
    if refund:
        state.emit("energy", amount=refund)
    state.emit("plan_cancel_last", card=entry.card_id, returned=True,
               energy=refund)


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


def next_attack_bonus(state: CombatState) -> None:
    """Battle Plan's carry-out: "the next Attack you play face-up this turn
    deals 4 additional damage".

    ONE STACK, ALWAYS, Rally's reading one card type over: the face says
    "deals 4 additional damage" and not "per Plan", so a morning carrying out two
    Battle Plans buffs one Attack.

    A RIDER ON EACH HIT, folded in by `effects.flat_attack_bonus` where every
    other flat attack rider is folded in, so a two-hit Attack collects it
    twice -- the same reading `next_attack_up` has always had, and the one
    `NextAttackDamagePower.ModifyDamageAdditive` gives on the other side.

    IT IS SPENT AT RESOLUTION (`spend_attack_bonus`), by a FACE-UP Attack: a
    card written on the Bake-Kurage is not a play of that card's face, so it
    neither takes the bonus nor spends it. `EB-668` is exactly that clause: a
    cost hook is handed no play and cannot ask, and damage at resolution can.
    """
    if not live(state):
        return
    if state.player.powers.get(NEXT_ATTACK_BONUS, 0):
        return
    state.player.powers[NEXT_ATTACK_BONUS] = 1
    state.emit("plan_battle_plan",
               bonus=C.KOKOMI_OVERHAUL_BATTLE_PLAN_BONUS)


def spend_attack_bonus(state: CombatState, card: Card) -> None:
    """The rider is consumed by the face-up Attack that takes it.

    CALLED FROM `effects._resolve_card_bound`, beside `next_attack_up`'s own
    consuming pop and AFTER `flat_attack_bonus` has read it -- which is the
    ordering the rider needs and the reason it is not spent at
    `combat._finish_play` the way the retired discount was.

    THE PET CHECK IS THE RULE AND NOT A GUARD. A card written on the jellyfish
    resolves none of its now-line, so it is not "an Attack you played" in the
    sense the face means -- the rider survives the write and pays the next
    Attack actually played. `NextAttackDamagePower.AfterCardPlayed` is the
    twin, gated on `KokomiPlan.PlayedOnPet` at the one site that can see the
    play's target.
    """
    if not live(state) or card.type != "attack":
        return
    if plan_aimed_at_pet(state, card):
        return
    if state.player.powers.pop(NEXT_ATTACK_BONUS, 0):
        state.emit("plan_battle_plan_spent", card=card.id)


def next_companion_discount(state: CombatState) -> None:
    """Rally: "The next Companion card you play this turn costs 1 less."

    ONE STACK, ALWAYS. The grant is a switch, not a counter -- two Rallies in
    one turn do not make the next Companion cost two less, because the card
    says "costs 1 less" and not "costs 1 less per Rally".

    A DISCOUNT, NOT A ZEROING (draft 6's change from draft 2's Vanguard):
    `combat.card_cost` SUBTRACTS it and floors at zero.
    """
    if not live(state):
        return
    if state.player.powers.get(NEXT_COMPANION_DISCOUNT, 0):
        return
    state.player.powers[NEXT_COMPANION_DISCOUNT] = 1
    state.emit("plan_rally", discount=C.KOKOMI_OVERHAUL_RALLY_DISCOUNT)


def spend_companion_discount(state: CombatState, card: Card) -> None:
    """The grant is consumed by the play that spends it -- the C#'s
    `AfterCardPlayed`/`IsLastInSeries` removal, at the one shared play site."""
    if not live(state) or not card.is_companion:
        return
    if state.player.powers.pop(NEXT_COMPANION_DISCOUNT, 0):
        state.emit("plan_rally_spent", card=card.id)


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

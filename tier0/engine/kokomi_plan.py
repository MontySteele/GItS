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
resolves at `AfterPlayerTurnStart` and its header says why), the Casket's
DEALER (the pet, so no Strength rides the 2), and "Plans ALSO happen now"
taken at its word (the Plan happens now AND is still queued).

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
PLAN_KINDS = frozenset((
    "draw", "energy", "block", "mend", "damage", "damage_quarter_max_hp",
    "damage_per_companion_last_turn", "apply_power", "plan_twice",
))

#: The two debuffs a Plan may apply. `KokomiPlan.PLAN_APPLY_POWERS`' twin.
PLAN_APPLY_POWERS = frozenset(("weak", "vulnerable"))

#: Where a clause lands (the `Aim` enum). Rule 3: "A planned hit lands on the
#: front enemy (leftmost alive) unless the line says every enemy." A
#: self-facing clause (draw, energy, Block, Mend, the doubling) names no
#: target at all, which is `Aim.Self`.
PLAN_AIMS = frozenset(("front_enemy", "all_enemies"))

#: The clauses that take an aim. Everything else is self-facing.
PLAN_AIMED_OPS = frozenset((
    "damage", "damage_quarter_max_hp", "damage_per_companion_last_turn",
    "apply_power"))

#: Legal inside a `plan:` list and NOWHERE else. A top-level spelling would be
#: a different, unpriced card, and this module is the only resolver of either.
#: `effects.OPS` still registers them -- the loader validates a `plan:` list
#: through the same vocabulary check the body takes -- and the registered
#: handler refuses, which is what makes "plan-only" true rather than intended.
PLAN_ONLY_OPS = frozenset(("plan_twice", "damage_per_companion_last_turn"))

#: The one clause the SHEET cannot spell, minted by Moon's Reflection when the
#: card it reaches has no Plan line of its own. It never appears in a `plan:`
#: list (`plan_shape_reason` refuses it there), so it is kept out of
#: `PLAN_KINDS` and handled beside them.
REPLAY_EXHAUSTED = "replay_exhausted"

#: Sango Isshin's divisor. An inline literal on BOTH sides -- the C# writes
#: `(int)kokomi.MaxHp / 4` in `KokomiRules.QuarterOfMaxHp` and holds no named
#: constant for it -- so it is NOT a `lint_constant_parity` row: that lint
#: compares NAMED C# members by value, and minting a name here that the mod
#: does not have would be a parity claim about nothing.
QUARTER = 4

#: The player-side powers this arm reads. Named here rather than spelled at
#: each site so the sheet's `power:` values and the readers cannot drift.
#: Every one of them is applied by an ordinary `apply_power` op off a card row.
TREATISE = "kk_treatise"                     # draw N per Plan carried out
SONG_OF_PEARLS = "kk_song_of_pearls"         # gain N Block per Plan
PLANS_ALSO_NOW = "kk_plans_also_now"         # Plans also happen now
CLOUDS_LIKE_WAVES = "kk_clouds_like_waves"   # Block per debuff she applies
GENERALS_BANNER = "kk_generals_banner"       # Weak to the front on a Companion
#: Nereid's Ascension's window. STACKS ARE TURNS, the engine's own grammar
#: (`kurage_summon`, `intangible`, `double_damage`), which is also the C#'s
#: (`PlanTwicePower.Amount` is turns remaining and ticks at her turn end).
PLAN_TWICE = "kk_plan_twice"
#: Rally's grant. ONE STACK, ALWAYS -- the card says "costs 1 less", not
#: "per Rally" -- and it is consumed by the next Companion play.
NEXT_COMPANION_DISCOUNT = "kk_next_companion_discount"

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
        if op != "damage_quarter_max_hp":
            allowed.add("amount")
        if op in PLAN_AIMED_OPS:
            allowed.add("target")
        if op == "apply_power":
            allowed.add("power")
        unknown = set(eff) - allowed
        if unknown:
            return (f"plan clause {op} field(s) {sorted(unknown)} "
                    "not understood")
        if op != "damage_quarter_max_hp":
            amount = eff.get("amount")
            # A LITERAL POSITIVE INT, the `spend_spark_amount` /
            # `block_at_turn_start_turns` precedent: a Plan's amount is read a
            # turn after it was written, so a formula resolved against combat
            # state would be printed text that means something different every
            # time it is carried out.
            if not isinstance(amount, int) or isinstance(amount, bool) \
                    or amount <= 0:
                return f"plan clause {op} amount must be a positive literal int"
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
    """The front enemy: LEFTMOST ALIVE.

    `CombatState.living_enemies` preserves `enemies` order, which is encounter
    slot order, so "leftmost" is the first living one and needs no second
    definition -- the same sentence `KokomiPlan.FrontEnemy` writes about
    `HittableEnemies`.
    """
    living = state.living_enemies
    return living[0] if living else None


def _aimed(state: CombatState, aim: Optional[str]) -> list[Enemy]:
    """The bodies one clause lands on. `None` (a self-facing clause) is
    empty by construction -- it names no target at all."""
    if aim == "all_enemies":
        return list(state.living_enemies)
    if aim == "front_enemy":
        front = front_enemy(state)
        return [front] if front is not None else []
    return []


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
    rather than a crash."""
    if not enemy.intents:
        return False
    return enemy.current_intent().get("kind") == "attack"


# ---------------------------------------------------------------------------
# WRITING A PLAN
# ---------------------------------------------------------------------------

def schedule(state: CombatState, card: Card,
             clauses: Optional[Sequence[dict]] = None,
             replay: Optional[Card] = None) -> None:
    """Write one Plan down: rule 2's whole engine side.

    `clauses` defaults to the card's own printed line and is passed explicitly
    only by Moon's Reflection, which contributes the line of a card it found in
    the exhaust pile. `replay` is that screen's other shape -- a chosen card
    with NO Plan line of its own, replayed whole.

    THE MOON OVERLOOKS THE WATERS IS RESOLVED HERE, and "also" is taken at its
    word (the C#'s reading, and its argument): the Rare's face is "Plans also
    happen now", so the Plan happens NOW and is STILL queued for the start of
    her next turn. Reading it as "instead" would delete rule 2 rather than
    break it.
    """
    if not live(state):
        return
    body = list(clauses if clauses is not None else card.plan)
    if not body:
        return
    entry = PlanEntry(card_id=card.id, clauses=body, card=replay)
    state.kk_plan_queue.append(entry)
    state.emit("plan_written", card=card.id, clauses=len(body),
               queued=len(state.kk_plan_queue))
    if state.player.powers.get(PLANS_ALSO_NOW, 0):
        _resolve_entry(state, entry, why="also_now")


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
        schedule(state, card, clauses=pick.plan)
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
    """
    if not live(state) or not state.kk_plan_queue:
        return
    due = list(state.kk_plan_queue)
    state.kk_plan_queue.clear()
    state.emit("plan_resolve_all", plans=len(due))
    for entry in due:
        for _ in range(carry_out_times(state)):
            if state.over or not state.player.alive:
                return
            _resolve_entry(state, entry, why="turn_start")


def resolve_front(state: CombatState) -> None:
    """Change of Plans: "The jellyfish carries out your front Plan now."

    IT LEAVES THE QUEUE, which is what "carries out" means everywhere else in
    the arm -- one resolution moved forward, not a copy. An empty queue is a
    printed no-op, the way a blocked Kurage memory is.

    NOT DOUBLED. `CarryOutTimes` is read inside `ResolveAll`'s drain loop and
    nowhere else, so Nereid's window pays the morning and not this card; that
    is the C#'s shape taken literally rather than a rule invented here.
    """
    if not live(state):
        return
    if not state.kk_plan_queue:
        state.emit("plan_front_empty")
        return
    entry = state.kk_plan_queue.pop(0)
    _resolve_entry(state, entry, why="change_of_plans")


def carry_out_times(state: CombatState) -> int:
    """How many times ONE Plan is carried out right now: two while Nereid's
    Ascension's window is up, one otherwise. A NAMED READ rather than an
    inline predicate, because WHERE it is asked is the rule."""
    return 2 if state.player.powers.get(PLAN_TWICE, 0) else 1


def _resolve_entry(state: CombatState, entry: PlanEntry, why: str) -> None:
    """ONE PLAN CARRIED OUT -- the unit Treatise and Song of Pearls are priced
    in. "Whenever the jellyfish carries out a Plan" is once per ENTRY, and the
    notify at the bottom is the only place it fires, so The Moon Overlooks the
    Waters' extra resolution pays them too."""
    state.emit("plan_carried_out", card=entry.card_id, why=why,
               clauses=len(entry.clauses))
    for clause in entry.clauses:
        if state.over or not state.player.alive:
            break
        _resolve_clause(state, entry, clause)
    _note_plan_resolved(state)


def _note_plan_resolved(state: CombatState) -> None:
    """The plan bus: Treatise draws and Song of Pearls blocks, once per Plan.

    ONE PAYMENT PER PLAN, NOT PER CLAUSE -- War Council prints two clauses and
    is one Plan, so it draws one. That is true because of WHERE this is called
    (the tail of `_resolve_entry`) rather than because of anything here.
    """
    p = state.player
    n = p.powers.get(TREATISE, 0)
    if n:
        state.draw(n)
        state.emit("plan_treatise", amount=n)
    n = p.powers.get(SONG_OF_PEARLS, 0)
    if n:
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
                    clause: dict) -> None:
    """One planned clause. `ResolveOne`'s switch, arm for arm."""
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
    elif op == "mend":
        effects.mend(state, amount)
    elif op == "damage":
        _hit(state, aim, amount)
    elif op == "damage_quarter_max_hp":
        _hit(state, aim, quarter_of_max_hp(state))
    elif op == "damage_per_companion_last_turn":
        # Chain of Command. "LAST TURN" IS READ AT CARRY-OUT: the Plan was
        # written on turn N and resolves at the top of N+1, and
        # `combat._player_turn` has already rolled the counter by then -- so
        # what this reads is turn N, the turn the player was looking at when
        # they wrote it. `KokomiOverhaulLedger.RollTo` is the same handover.
        _hit(state, aim, amount * state.companion_plays_last_turn)
    elif op == "apply_power":
        _debuff(state, aim, clause["power"], amount)
    elif op == "plan_twice":
        wear_plan_twice(state, amount)
    elif op == REPLAY_EXHAUSTED:
        _replay(state, entry.card)
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


def _hit(state: CombatState, aim: Optional[str], amount: int) -> None:
    """A Plan's damage, and it is HYDRO with KOKOMI as the dealer.

    Rule 3 settles both halves in one sentence: "Your Strength and Dexterity
    count, and planned damage from an Attack applies Hydro the way her Attacks
    do." `deal_damage_to_enemy` is this engine's funnel for exactly that -- the
    dealer's Strength and Weak, then the aura and its reaction, then the
    target's Vulnerable and Block -- so a planned hit and a played one differ
    in nothing but when they land.

    `source="plan"` AND NOT `"attack"`, which is a reading and is the C#'s:
    `KokomiPlan.Hit` goes out through `ElementalHit.Deal`, the funnel this mod
    uses for every NON-Attack hit, not through `DamageCmd.Attack`. In tier0
    `source == "attack"` is the name for a hit from an Attack CARD and it is
    what gates Shatter, on-hit bomb detonation and Skittish; a planned clause
    is not a card being played, so it takes none of those. Everything rule 3
    names -- Strength, Weak, the aura, the reaction, Vulnerable, Block -- is
    outside that gate and applies.

    THE TARGET LIST IS SNAPSHOTTED before the first hit, so an enemy the volley
    kills does not change who is in it (`QuarterMaxHpAll`'s `.ToList()`).
    """
    from tier0.engine import effects                # late import: cycle

    if amount <= 0:
        return
    for enemy in _aimed(state, aim):
        if not enemy.alive:
            continue
        effects.deal_damage_to_enemy(state, enemy, amount, element="hydro",
                                     source="plan")


def _debuff(state: CombatState, aim: Optional[str], power: str,
            amount: int) -> None:
    """A planned Weak or Vulnerable, applied BY HER -- so the Casket answers it
    and The Clouds Like Waves pays for it, exactly as they do for a debuff off
    a card she played.

    IT LANDS ON A CORPSE (R210 Q3): `PowerCmd.Apply` guards on
    `CanReceivePowers`, which does not test `IsDead`, and `_op_apply_power`
    already takes that reading for every aimed power in this engine. The aim
    itself is resolved over the LIVING, so the only corpse this can reach is
    one that died between the aim and the apply.
    """
    for enemy in _aimed(state, aim):
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


def wear_plan_twice(state: CombatState, turns: int) -> None:
    """Nereid's Ascension: "for 2 turns, the jellyfish carries out every Plan
    twice."

    THE DURATION IS THE AMOUNT, so a second Ascension EXTENDS the window and
    never doubles the doubling -- `PlanTwicePower.Wear`'s shape, and the
    `never_reduces` reading the engine already has a flag for.

    IT IS INSTALLED BY A PLAN, which is why the window starts one morning late
    and covers the NEXT two: the card is played on turn N, the clause is
    carried out at the top of N+1, and the tick runs at the end of N+1 and N+2.
    """
    standing = state.player.powers.get(PLAN_TWICE, 0)
    if standing >= turns:
        return
    # THE DELTA, not the amount: `PlanTwicePower.Wear` calls
    # `ModifyAmount(worn, turns - worn.Amount)`, which is a TOP-UP TO `turns`.
    # `apply_power` is additive, so handing it the whole 2 on top of a
    # standing 2 would make a second Ascension a four-turn window -- "doubles
    # the doubling", the exact thing the C# says this construction rules out.
    powers.apply_power(state, state.player, PLAN_TWICE, turns - standing)


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
    """
    state.companion_plays_last_turn = state.companion_plays_this_turn


def tick_windows(state: CombatState) -> None:
    """End of her turn: Nereid's window ticks down.

    `PlanTwicePower.AfterSideTurnEnd`'s twin, and the placement is the rule --
    a window installed by a Plan at the top of turn N+1 ticks at the END of
    N+1, so "for 2 turns" is N+1 and N+2.
    """
    if not live(state):
        return
    n = state.player.powers.get(PLAN_TWICE, 0)
    if not n:
        return
    if n <= 1:
        state.player.powers.pop(PLAN_TWICE, None)
    else:
        state.player.powers[PLAN_TWICE] = n - 1
    state.emit("plan_twice_tick", left=state.player.powers.get(PLAN_TWICE, 0))


# ---------------------------------------------------------------------------
# THE HOOKS
# ---------------------------------------------------------------------------

def note_companion_played(state: CombatState, card: Card) -> None:
    """"You played a Companion card" -- The General's Banner's hook.

    PER PLAY AND NOT PER CARD, the C#'s own sentence: a Companion played twice
    pays twice. It rides `combat._finish_play`, the one site a manual play and
    an auto-play both enter, beside the counter Chain of Command reads -- so
    "she played a Companion" has ONE definition in this engine and the Banner
    and the ledger cannot come to disagree about it.

    THE FRONT ENEMY IS `front_enemy`'s, the same reader a planned hit uses.
    """
    if not live(state) or not card.is_companion:
        return
    n = state.player.powers.get(GENERALS_BANNER, 0)
    if not n:
        return
    front = front_enemy(state)
    if front is None:
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

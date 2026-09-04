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
    "play_copy_of_companion", "block_per_plan_this_morning",
))

#: The clauses that carry NO `amount`. Both are whole rules rather than
#: numbers: Sango Isshin's quarter of Max HP is derived at carry-out, and
#: Crystal Collapse's copy is a CARD rather than a size. Named once because
#: `plan_shape_reason` asks it twice and `gen_klee_cards.plan_reason` asks the
#: same question from the other side.
PLAN_AMOUNTLESS_OPS = frozenset((
    "damage_quarter_max_hp", "play_copy_of_companion",
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
PLAN_ONLY_OPS = frozenset(("plan_twice", "damage_per_companion_last_turn",
                           "play_copy_of_companion",
                           "block_per_plan_this_morning"))

#: Tide Wall's clause (`EB-335`, R246 pick 2): "Gain N Block for each Plan the
#: Bake-Kurage carries out this morning." PLAN-ONLY by construction -- the
#: count it multiplies is a fact about a morning, and a now-line spelling would
#: read a number that is zero every time it is asked.
BLOCK_PER_PLAN = "block_per_plan_this_morning"

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
PLANS_ALSO_NOW = "kk_plans_also_now"         # Plans also happen now
CLOUDS_LIKE_WAVES = "kk_clouds_like_waves"   # Block per debuff she applies
GENERALS_BANNER = "kk_generals_banner"       # Weak to the front, once a turn
#: Nereid's Ascension's window. STACKS ARE TURNS, the engine's own grammar
#: (`kurage_summon`, `intangible`, `double_damage`), which is also the C#'s
#: (`PlanTwicePower.Amount` is turns remaining and ticks at her turn end).
PLAN_TWICE = "kk_plan_twice"
#: Rally's grant. ONE STACK, ALWAYS -- the card says "costs 1 less", not
#: "per Rally" -- and it is consumed by the next Companion play.
NEXT_COMPANION_DISCOUNT = "kk_next_companion_discount"
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


def _aimed(state: CombatState, aim: Optional[str]) -> list[Enemy]:
    """The bodies one clause lands on. `None` (a self-facing clause) is
    empty by construction -- it names no target at all."""
    if aim == "all_enemies":
        return list(state.living_enemies)
    if aim == "front_enemy":
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
    rather than a crash."""
    if not enemy.intents:
        return False
    return enemy.current_intent().get("kind") == "attack"


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
    entry = PlanEntry(card_id=card.id, clauses=body, card=held, label=label)
    state.kk_plan_queue.append(entry)
    state.emit("plan_written", card=card.id, clauses=len(body),
               queued=len(state.kk_plan_queue),
               holds=None if held is None else held.id)
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
    # `EB-335`. THE MORNING'S DEPTH, recorded on the same line the queue is
    # drained on and BEFORE the first clause runs -- Tide Wall's "for each Plan
    # the Bake-Kurage carries out this morning". Written here rather than
    # counted up inside the loop so the answer does not depend on where in the
    # queue the Tide Wall sits: on a three-Plan morning it is three whether it
    # was written first or last. `KokomiPlan.ResolveAll` records the same
    # number on the ledger, in the same place.
    state.kk_plans_this_morning = len(due)
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


def _hit(state: CombatState, aim: Optional[str], amount: int) -> None:
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
    """
    from tier0.engine import effects                # late import: cycle

    if amount <= 0:
        return
    for enemy in _aimed(state, aim):
        if not enemy.alive:
            continue
        effects.deal_damage_to_enemy(state, enemy, amount, element="hydro",
                                     source="plan", powered=False)


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

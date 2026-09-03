"""THE BOMB (QUARANTINED, `C.KLEE_OVERHAUL`) -- the sim twin of
`klee-mod/KleeCode/Powers/Prototype/ProtoBombPower.cs` and its neighbours.

THE RULED BRIEF'S SEVEN RULES (`review/active/klee-brief-2026-09-01.md` sec.3),
slice one (`review/active/klee-overhaul-slice-1-2026-09-01.md`):

  1. **Bomb.** A numbered charge on an enemy. Every Bomb grows by
     `C.KLEE_OVERHAUL_BOMB_GROWTH` at the start of Klee's turn, plus one per
     Explosives Workshop stack, the whole doubled by Alice's Recipe. A Bomb
     never goes off on its own.
  2. **Set off.** Only a card that says *Set off* makes Bombs go off. Every
     Bomb on the target goes off ONE AT A TIME, each a Pyro hit for its own
     size, BEFORE the rest of the card resolves.
  3. **Jump.** A Bomb whose enemy is already dead moves to a random living
     enemy at its current size instead of going off.
  4. **Spark.** Each explosion gives Klee `C.KLEE_OVERHAUL_SPARK_PER_EXPLOSION`
     Spark, and she starts every combat with `C.KLEE_OVERHAUL_OPENING_SPARK`.
     Cards that print a Spark price spend Sparks instead of energy.
  5. **Pyro.** An explosion is an ordinary Pyro hit -- Vulnerable and Weak on
     the enemy, Strength on Klee, and every reaction in the table.
  6. **Mine.** A Mine is a Bomb that ALSO goes off when its enemy attacks Klee,
     before the attack lands.
  7. **Nothing fires by itself.** No start-of-turn detonation, no automatic
     free attack, no "at 3 Sparks".

THE C# IS THE SPEC, and where its prose and its code disagree the CODE is what
this file mirrors. The places that matters are recorded at their sites below;
the ones a reader should know before reading anything else:

  * ALICE'S RECIPE MULTIPLIES, AND THE WORKSHOP IS ADDED FIRST. `GrowthFor`
    sums the base and the Workshop stacks and doubles the result -- "your Bombs
    grow twice each turn", the card's own face. See `growth_for`.
  * A SET OFF AIMED AT A CORPSE JUMPS the whole pile rather than fizzling;
    `SetOff` takes the charges first and its per-charge death test then sends
    every one of them to `JumpCharges`. See `set_off`.
  * THE MINE READS THE MULTIPLIER WITHOUT SPENDING IT (`PeekMultiplier`), so an
    enemy attack cannot eat the window The Big One armed for its own card.

A SEPARATE MODULE, not a section of `effects.py`, for the reason
`kokomi_plan.py` is one: this is a whole rule with a pile, four resolution
points, an explosion bus and a per-turn ledger, and `effects.py` is already the
largest file in the engine. The dependency runs ONE WAY at import time -- this
module imports nothing from `effects` at module scope and reaches it late,
inside the functions.

NOTHING HERE IS REACHABLE WITH THE FLAG OFF. Every entry point returns on
`live()` before touching anything, `loader._card_prototype` refuses a
`proto_ko_` id with the flag off, and `tier0/tests/test_klee_overhaul.py` pins
the OFF arm as a whole-log digest. NOTHING MEASURED ON A PROTOTYPE ROW IS
QUOTABLE (R215 B): this is a rule made runnable, not a number about a game.
"""

from __future__ import annotations

import contextlib
from typing import Iterator, Optional, Sequence

from tier0 import constants as C
from tier0.engine.state import Card, CombatState, Enemy, KleeCharge

# ---------------------------------------------------------------------------
# THE VOCABULARY
# ---------------------------------------------------------------------------

#: The arm's eight verbs. Registered in `effects.OPS`, priced in
#: `draft.STATIC_OP_PRICING`, and resolved by this module and nothing else.
OVERHAUL_OPS = frozenset((
    "set_off", "plant_bomb", "grow_bombs", "merge_bombs",
    "remove_bomb_for_block", "damage_set_off_total", "multiply_set_off",
    "draw_per_set_off"))

#: The player-side powers this arm reads, named here rather than spelled at
#: each site so the sheet's `power:` values and the readers cannot drift. Every
#: one is applied by an ordinary `apply_power` op off a card row, and every one
#: names its C# class in `tools/gen_klee_cards.POWER_CS`.
BOMB_GROWTH_UP = "ko_bomb_growth_up"          # Explosives Workshop: +1 growth
ALICES_RECIPE = "ko_alices_recipe"            # growth 4 INSTEAD of 3
CHAINED_REACTIONS = "ko_chained_reactions"    # re-Bomb per explosion
BOMB_ECHO = "ko_bomb_echo"                    # Sparks 'n' Splash's echo
BOMB_REACTION_SPARK = "ko_bomb_reaction_spark"   # Catalytic Converter
GROUNDED = "ko_grounded"                      # Block for the quiet turn

#: Pounding Surprise, in this engine's spelling. THE RELIC IS RULE 4 (the brief
#: sec.8), and tier 0 already carries the relic as a hook name on the player --
#: `content/characters/klee.yaml` ships `relic_hooks: [spark_on_detonation]`.
#: So the Spark rides the same hook the shipped detonation Spark rides, which
#: is the C#'s own arrangement: `PoundingSurprise` implements BOTH
#: `OnBombDetonated` and `OnBombExploded` with the same body.
SPARK_RELIC_HOOK = "spark_on_detonation"

#: `source=` for an explosion's hit, and it is NOT `"attack"`. In tier 0
#: `source == "attack"` is the name for a hit from an Attack CARD and is what
#: gates Shatter, the shipped on-hit bomb detonation and Skittish; an explosion
#: is not a card being played, so it takes none of those -- the same reading
#: `kokomi_plan._hit` records for a planned clause. The C# says it one layer
#: down: `Explode` goes out through `ElementalHit.Deal`, the funnel this mod
#: uses for every NON-Attack hit, not through `DamageCmd.Attack`. Everything
#: rule 5 names -- Strength, Weak, the aura, the reaction, Vulnerable, Block --
#: is outside that gate and applies.
#:
#: A NAME OF ITS OWN rather than the shipped `"bomb"`, because the two are
#: different rules and a log that spelled them the same could not be read.
EXPLOSION_SOURCE = "set_off"

#: `source=` for Sparks 'n' Splash's echo, and a THIRD name rather than
#: `EXPLOSION_SOURCE`, because the echo is not an explosion: it spends no
#: charge, mints no Spark and moves neither of rule 7's counters. A log that
#: called them the same thing would make "how many Bombs went off" unreadable.
#: Same non-Attack posture as an explosion, for the same reason.
ECHO_SOURCE = "bomb_echo"


# ---------------------------------------------------------------------------
# THE GATE
# ---------------------------------------------------------------------------

def live(state: CombatState) -> bool:
    """The one gate: the flag is on and the seat IS Klee.

    `KleeOverhaul.Enabled` plus the `IKleeCharacter` test every seam in the mod
    carries beside it (`KleeOverhaulOpening.GrantSpark`,
    `CatalystCadence.PrintedElement`, `SparkGauge.AppliesTo`), and the
    character half is not decoration: the flag is a build switch, the arm is
    Klee's rules, and a co-op Furina must not start growing Bombs.
    """
    return bool(C.KLEE_OVERHAUL and state.player.character_id == "klee")


# ---------------------------------------------------------------------------
# RULE 1 -- GROWTH
# ---------------------------------------------------------------------------

def growth_for(state: CombatState) -> int:
    """Rule 1's growth NUMBER for this Klee, right now. `GrowthFor`'s twin.

    ONE function, because the two modifiers compose in one printed way:
    Explosives Workshop ADDS `C.KLEE_OVERHAUL_WORKSHOP_GROWTH` per stack ("your
    Bombs grow by 1 more"), Alice's Recipe MULTIPLIES what is left by
    `C.KLEE_OVERHAUL_ALICE_MULTIPLIER` ("your Bombs grow twice each turn").

    ADD-THEN-MULTIPLY, and it is the only reading that leaves both faces true:
    "twice" is twice the growth the turn would otherwise have had, the
    Workshop's +1 included. At today's constants the Recipe alone grows 4 x 2 =
    8 and the Recipe with one Workshop grows (4 + 1) x 2 = 10. The other order
    would make the Rare read "twice the base and the Workshop once", which
    neither card says.

    A MULTIPLIER SINCE THE 2026-09-02 BALANCE PASS, replacing an earlier "grow
    by 4 instead of 3": the replacement reading made the Rare a strictly weaker
    Explosives Workshop, because a second Workshop reached 5 and a second
    Recipe still read 4.

    EVERY NUMBER IS READ, NEVER HARDCODED. Rule 1's growth is a placeholder the
    brief says is not a claim, and it has already moved once (3 to 4) inside
    this branch's own lifetime.
    """
    powers_ = state.player.powers
    growth = (int(C.KLEE_OVERHAUL_BOMB_GROWTH)
              + powers_.get(BOMB_GROWTH_UP, 0)
              * int(C.KLEE_OVERHAUL_WORKSHOP_GROWTH))
    if powers_.get(ALICES_RECIPE, 0):
        growth *= int(C.KLEE_OVERHAUL_ALICE_MULTIPLIER)
    return growth


def grow_pile(enemy: Enemy, amount: int) -> None:
    """Rule 1's growth, applied to one pile. PURE, `GrowBy`'s twin -- every
    charge grows by the same number, Mines included (rule 6: a Mine cooks like
    any Bomb)."""
    if amount == 0 or not enemy.ko_charges:
        return
    for charge in enemy.ko_charges:
        charge.size += amount


# ---------------------------------------------------------------------------
# THE PILE -- the pure reads and the pure mutations
# ---------------------------------------------------------------------------

def total_size(enemy: Enemy) -> int:
    """What a Set off here would deal, RAW: the sum of the charges.

    The raw sum every rule inside the arm is priced in (growth, jumps, Sorry
    Jean's Block). The mod also has a `PredictedSetOffDamage` -- the same sum
    run through the damage pipeline, for the badge and the tooltip -- and this
    engine has no badge, so that reader has no twin here (see the module's
    Not-done list in the PR).
    """
    return sum(c.size for c in enemy.ko_charges)


def mine_count(enemy: Enemy) -> int:
    """How many of this pile's charges are Mines -- the fuse mark."""
    return sum(1 for c in enemy.ko_charges if c.is_mine)


def holds_charge(enemy: Enemy) -> bool:
    """Does this enemy hold a live charge? `HoldsChargeFrom`'s twin."""
    return bool(enemy.ko_charges)


def any_bomb_placed(state: CombatState) -> bool:
    """Does ANY living enemy hold a charge? `AnyPlacedBy`'s twin, and the gate
    behind a card whose whole body is a Set off (`EB-261`).

    BOARD-WIDE, not per-target, because the mod asks it from `IsPlayable`,
    which is asked without a target -- "unplayable on a Bomb-less board,
    playable once any enemy holds one". Aiming at the wrong enemy stays the
    player's to get right.
    """
    return any(e.ko_charges for e in state.enemies if e.alive)


def take_all(enemy: Enemy) -> list[KleeCharge]:
    """Empty this pile and hand back what it carried. `TakeAll`'s twin.

    THE CHARGES ARE OFF THE PILE BEFORE ANYTHING THAT CAN KILL RUNS, which is
    the point rather than a tidiness: a kill mid-payload can neither re-enter
    the pile nor lose what is owed (the shipped Bomb's EB-138 discipline), and
    rule 3's jump needs the same guarantee for the same reason.
    """
    taken, enemy.ko_charges = enemy.ko_charges, []
    return taken


def take_mines(enemy: Enemy) -> list[KleeCharge]:
    """Empty only the MINES, leaving plain Bombs where they are (rule 6).
    `TakeMines`' twin."""
    mines = [c for c in enemy.ko_charges if c.is_mine]
    if mines:
        enemy.ko_charges = [c for c in enemy.ko_charges if not c.is_mine]
    return mines


def place(state: CombatState, enemy: Enemy, size: int, is_mine: bool = False,
          payload_mine_all: int = 0) -> None:
    """Plant one charge. `Place`'s twin, and the SINGLE entry point for every
    source: a card's `plant_bomb`, a jump's landing, a payload's Mines and
    Chained Reactions' re-Bomb all arrive here.

    IT LANDS ON A CORPSE, matching `PowerCmd.Apply`'s only guard
    (`CanReceivePowers`, which does not test `IsDead`) and this engine's own
    `CORPSE_TARGETABLE_OPS` reading for `place_bomb`. The sweep is what moves
    it off again.
    """
    enemy.ko_charges.append(
        KleeCharge(size=int(size), is_mine=bool(is_mine),
                   payload_mine_all=int(payload_mine_all)))
    state.emit("ko_bomb_placed", target=enemy.name, size=int(size),
               mine=bool(is_mine), payload=int(payload_mine_all),
               pile=total_size(enemy))


# ---------------------------------------------------------------------------
# THE LEDGER -- `KleeOverhaulLedger`'s twin
# ---------------------------------------------------------------------------

def roll_to(state: CombatState, round_: int) -> None:
    """Roll the per-turn counters to `round_`. `RollTo`'s twin, verbatim.

    THE STAMP IS THE RULE. `SetOffLastTurn` takes this turn's count only when
    the round moved by exactly one; any bigger jump means Klee had no turn in
    between and last turn's count is then honestly zero. tier 0's turns always
    advance by one, so that branch is unreachable from `combat._player_turn` --
    it is written anyway, because the C# reads the round STAMP and a twin that
    quietly assumed the increment would be a different function wearing the
    same name.

    Called unconditionally, the way `kokomi_plan.roll_turn` is: it is four
    integer moves and reads no flag, and with the arm off nothing reads the
    result.
    """
    if round_ == state.ko_round:
        return
    state.ko_set_off_last_turn = (state.ko_set_off_this_turn
                                  if round_ == state.ko_round + 1 else 0)
    state.ko_set_off_this_turn = 0
    state.ko_reacted_this_turn = 0
    state.ko_damage_set_off_this_play = 0
    state.ko_set_off_multiplier = 1
    state.ko_round = round_


def note_explosion(state: CombatState, reacted: bool,
                   damage_dealt: int) -> None:
    """One explosion landed. `NoteExplosion`'s twin, and THE ONE write site for
    both counters and the play memory, so the three can never disagree about
    what an explosion is."""
    state.ko_set_off_this_turn += 1
    state.ko_damage_set_off_this_play += int(damage_dealt)
    if reacted:
        state.ko_reacted_this_turn += 1


def begin_play(state: CombatState, card: Card) -> None:
    """A card play begins: the play-scoped damage memory starts empty.

    OPENED BY THE CARD THAT READS IT, exactly as the mod does it -- the
    emitter prepends `KleeOverhaulLedger.For(...).BeginPlay()` to the body of
    any row carrying `damage_set_off_total` and to no other row
    (`tools/gen_klee_cards.py`, the `BeginPlay` arm). Big Badda Boom is the
    only such row today.

    NOT the turn counters: Run Away! and Ammo Scavenging read the TURN, and
    Big Badda Boom reads the PLAY.
    """
    if not live(state):
        return
    if any(fx.get("op") == "damage_set_off_total" for fx in card.effects):
        state.ko_damage_set_off_this_play = 0


def arm_multiplier(state: CombatState, multiplier: int) -> None:
    """The Big One arms it; the next Set off spends it. `ArmMultiplier`.

    An INT rather than the flag it replaced. R243's Klee card audit ruling
    ([USER], 2026-09-02: "move The Big One to 4x with no flat number") made
    the number the card's own, so the row carries it
    (`multiply_set_off.multiplier`) and the engine multiplies by whatever
    the row says; unarmed is 1.
    """
    state.ko_set_off_multiplier = int(multiplier)


def take_multiplier(state: CombatState) -> int:
    """Read and clear (to 1). The Set off that consumes it is "this way"."""
    armed = state.ko_set_off_multiplier
    state.ko_set_off_multiplier = 1
    return armed


def peek_multiplier(state: CombatState) -> int:
    """Read WITHOUT clearing: a Mine answering an enemy attack must not eat the
    multiplier a card armed for its own Set off. `PeekMultiplier`."""
    return state.ko_set_off_multiplier


# ---------------------------------------------------------------------------
# RULE 2 -- SET OFF
# ---------------------------------------------------------------------------

def set_off(state: CombatState, enemy: Optional[Enemy]) -> int:
    """RULE 2. Every Bomb on `enemy` goes off, ONE AT A TIME, each a Pyro hit
    for its own size. Returns how many charges went off. `SetOff`'s twin.

    THE ORDER IS THE RULE, not an implementation detail: "one at a time" is
    what makes a three-Bomb pile three separate Pyro hits, so three separate
    reactions, three separate Sparks, and a kill on the second one leaves the
    third to JUMP rather than to fizzle (rule 3, the brief's worked example).

    TAKE-THEN-RESOLVE: the whole pile leaves the enemy first, so the loop below
    owns charges nothing else can reach.

    A CORPSE JUMPS THE WHOLE PILE. The death test is read per charge and BEFORE
    the charge resolves, so a Set off aimed at an enemy that is already dead --
    which R210's bind makes reachable, the aim being one creature for the whole
    play, dead or alive -- moves every charge instead of spending it on a body.
    """
    if enemy is None or not live(state):
        return 0
    taken = take_all(enemy)
    if not taken:
        return 0
    state.emit("ko_set_off", target=enemy.name, charges=len(taken),
               size=sum(c.size for c in taken))
    multiplier = take_multiplier(state)
    exploded = 0
    for index, charge in enumerate(taken):
        if not enemy.alive:
            jump_charges(state, enemy, taken[index:])
            break
        _explode(state, enemy, charge, multiplier)
        exploded += 1
        if state.over or not state.player.alive:
            break
    sweep_jumps(state)
    return exploded


def _explode(state: CombatState, enemy: Enemy, charge: KleeCharge,
             multiplier: int) -> None:
    """ONE explosion, which is the unit every other rule is priced in: one Pyro
    hit for the charge's size, one Spark, one payload, one entry in both of
    rule 7's counters. `Explode`'s twin.

    PYRO, THROUGH THE SHARED HIT FUNNEL, is rule 5 and it is why the reaction
    half needs no card text at all: `deal_damage_to_enemy` resolves the aura,
    the amplifier and the reaction, so a cooked Bomb Vaporizes exactly as one
    of Klee's Attacks would.

    THE REACTION IS DETECTED BY DIFFING `state.reactions_this_turn` across the
    hit, which is this engine's nearest thing to the C#'s
    `ReactionEffects.TotalResolved`: it is the one counter every reaction in
    the engine passes through, and no turn boundary can fall inside a single
    hit, so the diff is exact. `reactions_this_card` would have been wrong --
    a Mine answering an enemy attack is not inside a card.
    """
    from tier0.engine import effects                # late import: cycle

    size = charge.size * multiplier
    before = state.reactions_this_turn
    state.emit("ko_explosion", target=enemy.name, size=size,
               mine=charge.is_mine, multiplier=multiplier)
    dealt = effects.deal_damage_to_enemy(state, enemy, size, element="pyro",
                                         source=EXPLOSION_SOURCE)
    reacted = state.reactions_this_turn > before
    # `dealt` is the number the hit LANDED for, straight off the funnel that
    # computed it (`EB-270`): Big Badda Boom's face says "the damage the Bombs
    # dealt", and under Weak (or Strength, or Vulnerable) that is not `size`.
    note_explosion(state, reacted, int(dealt))
    # QUARANTINED (C.COMPANION_OVERHAUL). The stand-in seam's two this-turn
    # watchers (Diona's Bomb, Noelle's Mine), here rather than on
    # `_notify_explosion` below because that bus carries no Mine flag and
    # widening it for one card would put a stand-in's rule inside this arm's
    # own hook. A no-op with the companion arm off.
    from tier0.engine import companion_standins    # late import: cycle
    companion_standins.note_explosion(state, charge.is_mine)

    # THE BOMB PAYLOAD (Jumpy Dumpty). It rides the EXPLOSION rather than the
    # card, which is the whole of what makes the starter's promise legible: the
    # Mines arrive when the big Bomb finally goes off, not when it was planted.
    if charge.payload_mine_all > 0:
        for other in list(state.living_enemies):
            place(state, other, charge.payload_mine_all, is_mine=True)

    _notify_explosion(state, enemy, size, reacted)


def _notify_explosion(state: CombatState, enemy: Enemy, size: int,
                      reacted: bool) -> None:
    """The explosion bus, once PER EXPLOSION. `NotifyExplosionListeners`' twin,
    and the same shape for the same reason: rule 4's Spark, Chained Reactions
    and Catalytic Converter are all subscribers, so a three-Bomb Set off pays
    each of them three times.

    `reacted` is the half the React loop is built on -- whether THIS explosion
    consumed an off-element aura, which no listener could work out after the
    fact, because the aura it consumed is gone.
    """
    from tier0.engine import effects                # late import: cycle

    p = state.player
    # RULE 4, and the relic IS the rule (the brief sec.8). Gated on the hook
    # rather than on the character for the reason `relics.combat_start_spark`
    # is: the honest test for "this player runs the Spark economy" is the
    # starter's own hook, which the mod's upgrade keeps rather than removes.
    if SPARK_RELIC_HOOK in p.relic_hooks:
        effects.gain_sparks(state, int(C.KLEE_OVERHAUL_SPARK_PER_EXPLOSION))

    # Catalytic Converter: EXTRA, on top of the explosion's own Spark, and only
    # when the explosion REACTED.
    n = p.powers.get(BOMB_REACTION_SPARK, 0)
    if n and reacted:
        state.emit("ko_catalytic_converter", amount=n)
        effects.gain_sparks(state, n)

    # Chained Reactions: "Whenever one of your Bombs goes off, place a Bomb N
    # on a random enemy." Through the same `place` every other source uses, so
    # it can be set off and it can jump -- and, being a plain Bomb rather than
    # a Mine, it cannot answer an attack by itself (rule 7: this PLACES, it
    # does not detonate).
    n = p.powers.get(CHAINED_REACTIONS, 0)
    if n:
        living = list(state.living_enemies)
        if living:
            dest = state.rng.choice(living)
            state.emit("ko_chained_reactions", target=dest.name, size=n)
            place(state, dest, n)


# ---------------------------------------------------------------------------
# RULE 3 -- THE JUMP
# ---------------------------------------------------------------------------

def jump_charges(state: CombatState, from_enemy: Optional[Enemy],
                 charges: Sequence[KleeCharge]) -> None:
    """RULE 3 for charges already in hand: each moves to a random LIVING enemy
    at its current size. `JumpCharges`' twin.

    NOTHING IS LOST AND NOTHING GROWS -- a jump is a MOVE, so the size, the
    Mine flag and the payload all travel. Each charge rolls its own
    destination, so three jumping Bombs can land on three different enemies.
    With no living enemy left there is nowhere to go and the charges are
    dropped, which is the only answer available: the fight is over.
    """
    for charge in charges:
        candidates = [e for e in state.living_enemies if e is not from_enemy]
        if not candidates:
            return
        dest = state.rng.choice(candidates)
        state.emit("ko_bomb_jumped",
                   frm=from_enemy.name if from_enemy is not None else None,
                   to=dest.name, size=charge.size, mine=charge.is_mine)
        place(state, dest, charge.size, charge.is_mine,
              charge.payload_mine_all)


def sweep_jumps(state: CombatState) -> None:
    """RULE 3 for the death this arm did NOT cause: "A partner or a poison
    killed the enemy: all of them jump." `SweepJumps`' twin.

    NO REGISTER IS NEEDED HERE, and that is the one place this twin is simpler
    than the mod rather than different from it. `ProtoBombPower.Register`
    exists because the base game detaches a corpse and strips its powers inline
    inside the damage command, so by the time anything could look, the pile is
    gone. tier 0 tears nothing down -- a dead `Enemy` is an object whose `hp`
    is <= 0 and whose `ko_charges` list is exactly where it was -- so the board
    itself IS the register.

    WHEN IT RUNS is the C#'s list, moment for moment: at the start of Klee's
    turn (before growth, so a jumped Bomb grows on its new enemy this turn), at
    the end of every Set off, after a Mine fires, and after every card play
    (`KleeOverhaulSweepHooks.AfterCardPlayed`, the backstop `EB-279` added so
    the Bombs are on a living enemy before the next card is played).
    """
    if not live(state):
        return
    for enemy in state.enemies:
        if enemy.alive or not enemy.ko_charges:
            continue
        jump_charges(state, enemy, take_all(enemy))


# ---------------------------------------------------------------------------
# RULE 6 -- THE MINE
# ---------------------------------------------------------------------------

def mines_answer_attack(state: CombatState, enemy: Enemy) -> None:
    """RULE 6. This enemy's attack is about to land on Klee, so every Mine here
    goes off first; plain Bombs stay put. `BeforeDamageReceived`'s twin.

    THE SITE IS THE ONE THE MOD NAMES. `combat._enemy_turn` already carries a
    pre-hit hook at exactly this moment -- after the hit's number is settled
    and before Block is spent -- and its own comment says whose moment it is:
    "the moment the mod's `BeforeDamageReceived` gives Klee's Mine".

    NO PER-ACTION LATCH IS NEEDED, unlike the shipped Bomb's suppression: the
    Mines are CONSUMED, so the second hit of a multi-hit intent finds none. The
    rule is self-limiting.

    THE MULTIPLIER IS PEEKED, NOT TAKEN (`PeekMultiplier`): an enemy's attack
    must not eat the window The Big One armed for its own Set off.
    """
    if not live(state) or not enemy.alive:
        return
    mines = take_mines(enemy)
    if not mines:
        return
    state.emit("ko_mines_answer", target=enemy.name, count=len(mines))
    multiplier = peek_multiplier(state)
    for index, mine in enumerate(mines):
        if not enemy.alive:
            jump_charges(state, enemy, mines[index:])
            break
        _explode(state, enemy, mine, multiplier)
        if state.over or not state.player.alive:
            break
    sweep_jumps(state)


# ---------------------------------------------------------------------------
# THE TURN BOUNDARIES
# ---------------------------------------------------------------------------

def turn_start(state: CombatState) -> None:
    """The start of Klee's turn: jumps first, then rule 1's growth.

    `BeforeSideTurnStart`'s twin, at this engine's own name for that site
    (`refpowers.side_turn_start_early`, "StS2 site A ... BEFORE the block clear
    and BEFORE the draw").

    JUMPS FIRST, and the C# says why: a Bomb owed a jump is a Bomb that should
    GROW on its new enemy this turn, not next.

    AND RULE 7'S WHOLE POINT: this hook GROWS and does not detonate. The
    shipped Bomb's identical hook is what fires its start-of-turn payload;
    under this arm there is nothing to fire, because nothing fires by itself.
    """
    if not live(state):
        return
    sweep_jumps(state)
    amount = growth_for(state)
    grown = 0
    for enemy in state.enemies:
        if enemy.ko_charges:
            grow_pile(enemy, amount)
            grown += len(enemy.ko_charges)
    if grown:
        state.emit("ko_bombs_grew", amount=amount, charges=grown)


def turn_start_late(state: CombatState) -> None:
    """The two rules that read the turn AFTER it is set up -- rule 4's opening
    Spark and Grounded's Block.

    THE SITE IS `AfterPlayerTurnStart` on both sides, and both halves of the
    mod say why they need it rather than `BeforeCombatStart` or site A:
    `KleeOverhaulOpening` records that the sim fires its combat-start effects
    on TURN 1 after the block clear, the energy reset and the draw, and
    `GroundedPower` needs the ledger already rolled so `SetOffLastTurn` is the
    count that stood when the player last passed.
    """
    if not live(state):
        return
    from tier0.engine import effects                # late import: cycle

    # RULE 4's OPENING SPARK (R242 pick 1). A KIT rule and not a relic clause,
    # which is why it is gated on the arm alone: Touch of Orobas swaps the
    # relic at the act-2 reward and a relic clause would silently take the
    # opening Spark away from a player who upgraded.
    #
    # `== 1` rather than `<= 1` so an extra first turn cannot pay twice.
    if state.turn == 1 and C.KLEE_OVERHAUL_OPENING_SPARK > 0:
        state.emit("ko_opening_spark",
                   amount=int(C.KLEE_OVERHAUL_OPENING_SPARK))
        effects.gain_sparks(state, int(C.KLEE_OVERHAUL_OPENING_SPARK))

    # GROUNDED: "if none of your Bombs went off LAST turn, gain N Block." Last
    # turn and not this one is the whole design -- the decision it pays for was
    # made a turn ago, so the Block arrives before this turn's decision rather
    # than as a reward for one already taken.
    #
    # UNPOWERED (`ValueProp.Unpowered` in `CreatureCmd.GainBlock`), so no
    # Dexterity feeds it and no Frail bites it: it is a POWER's Block, not a
    # card's printed Block.
    # THE ONE READER OF KAEYA'S BLIND (QUARANTINED, C.COMPANION_OVERHAUL).
    # Cold-Blooded Strike's stand-in prints "This turn, Grounded counts nothing
    # as having gone off", and it names Grounded -- so the cover story is read
    # HERE and not by zeroing the counter, which Jean's stand-in also reads.
    # `grounded_blind` is False on every tree with the companion arm off.
    from tier0.engine import companion_standins    # late import: cycle

    n = state.player.powers.get(GROUNDED, 0)
    if n and (state.ko_set_off_last_turn == 0
              or companion_standins.grounded_blind(state)):
        state.player.block += n
        state.emit("block", amount=n)
        state.emit("ko_grounded", amount=n)


def turn_end(state: CombatState) -> None:
    """The end of Klee's turn: Sparks 'n' Splash's ECHO. `BombEchoPower
    .BeforeSideTurnEnd`'s twin.

    "At the end of your turn, deal Pyro damage to a random enemy equal to the
    Bombs on it." [USER]'s OWN DESIGN, 2026-09-02: "I think auto-detonation on
    Sparks n' Splash completely bricks the growth build. How about instead 'a
    random enemy takes damage equal to the amount of Bomb on them'?" The row
    printed an automatic Set off before that, and the Rare the growth deck most
    wants was the one card that cashed its pile without being asked.

    IT READS THE PILE AND DOES NOT SPEND IT, which is the whole card, and it is
    why rule 7 is untouched by it. Nothing is taken, so:
      * the Bombs stay and keep growing -- the echo pays again next turn, and
        bigger;
      * NO SPARK, because rule 4 pays one per EXPLOSION and nothing exploded;
      * no Mine answers, no explosion bus, and NEITHER of rule 7's counters
        moves -- the ledger is not touched at all. This is not a Set off.

    PYRO THROUGH THE SHARED HIT FUNNEL, so the echo reacts with an aura exactly
    as an explosion does and carries her Strength the same way; and NOT an
    Attack, because no card is being played.

    A RANDOM BOMBED ENEMY, unlike the auto-detonation it replaces: an echo of
    nothing is not a printed effect, so the roll is over the enemies that
    actually hold a charge, and a board with none does nothing at all.
    """
    from tier0.engine import effects                # late import: cycle

    if not live(state):
        return
    if not state.player.powers.get(BOMB_ECHO, 0):
        return
    candidates = [e for e in state.living_enemies if e.ko_charges]
    if not candidates:
        return
    target = state.rng.choice(candidates)
    size = total_size(target)
    if size <= 0:
        return
    state.emit("ko_bomb_echo", target=target.name, amount=size)
    effects.deal_damage_to_enemy(state, target, size, element="pyro",
                                 source=ECHO_SOURCE)


# ---------------------------------------------------------------------------
# THE CARD VERBS THAT ARE NOT A SET OFF
# ---------------------------------------------------------------------------

def merge_all_to(state: CombatState, dest: Optional[Enemy],
                 growth: int) -> None:
    """Careful Arrangement: move ALL your Bombs onto one enemy AS ONE Bomb,
    which then grows by `growth`. `MergeAllTo`'s twin.

    TWO THINGS THE CARD TEXT DOES NOT SAY, and both are the mod's reported
    defaults taken unchanged: the merged Bomb is a MINE if any merged charge
    was one (merging must not silently delete the defence the player set up),
    and it carries the payloads of every merged charge, summed. A merge is a
    move, and a move loses nothing.

    THE SOURCES ARE THE LIVING BOARD (`HittableEnemies`), so a corpse's pile is
    not gathered -- the sweep is what moves that one, and it moves it whole.
    """
    if dest is None or not live(state):
        return
    size = 0
    is_mine = False
    payload = 0
    merged = 0
    for enemy in list(state.living_enemies):
        for charge in take_all(enemy):
            size += charge.size
            is_mine |= charge.is_mine
            payload += charge.payload_mine_all
            merged += 1
    if size == 0:
        return
    state.emit("ko_bombs_merged", to=dest.name, charges=merged, size=size,
               growth=growth)
    place(state, dest, size + growth, is_mine, payload)


def remove_largest_for_block(state: CombatState) -> int:
    """Sorry, Jean...: remove ONE of your Bombs and gain Block equal to its
    size. Returns the size removed, 0 if there was nothing to remove.
    `RemoveLargestForBlockAndGain`'s twin.

    WHICH Bomb, the card does not say. THE LARGEST, the mod's reported default
    and the only deterministic answer a player can plan around: an emergency
    exit whose size is a coin flip is not an exit.

    ONE CALL, so the number removed and the number gained are the same number
    by construction and no printed value can drift from either. The Block is
    UNPOWERED, the mod's `ValueProp.Unpowered`.
    """
    if not live(state):
        return 0
    best_enemy: Optional[Enemy] = None
    best_index = -1
    best_size = 0
    for enemy in list(state.living_enemies):
        for index, charge in enumerate(enemy.ko_charges):
            if charge.size > best_size:
                best_enemy, best_index, best_size = enemy, index, charge.size
    if best_enemy is None:
        return 0
    removed = best_enemy.ko_charges.pop(best_index)
    state.player.block += removed.size
    state.emit("block", amount=removed.size)
    state.emit("ko_bomb_removed", target=best_enemy.name, size=removed.size)
    return removed.size


def draw_per_set_off(state: CombatState) -> None:
    """Ammo Scavenging: "Draw a card for each of your Bombs that went off this
    turn." Rule 7's first counter, spent. `DrawPerSetOff`'s twin."""
    if not live(state):
        return
    count = state.ko_set_off_this_turn
    if count <= 0:
        return
    state.emit("ko_draw_per_set_off", amount=count)
    state.draw(count)


# ---------------------------------------------------------------------------
# THE PLAYABILITY GATE -- `EB-261`
# ---------------------------------------------------------------------------

#: The two ops a Spark or Charge price is spelled with. `gen_klee_cards`'
#: `_COST_OPS`, and the reason it is a named pair on both sides: a cost is not
#: part of what the card DOES.
_COST_OPS = ("spend_spark", "spend_charge")


def set_off_only(card: Card) -> bool:
    """Does this row do NOTHING on a board with no Bomb on it? (`EB-261`.)

    `gen_klee_cards.card_is_set_off_only`'s twin, clause for clause. True when
    every top-level effect that is not a cost is a `set_off` that deals no
    damage of its own. Such a card pays its price and resolves to nothing,
    which is the same silent no-play the Spark cost line refuses one resource
    over -- so it takes the same gate, at the same extension point
    (`CardModel.IsPlayable` there, `combat.card_playable` here).

    DERIVED FROM THE ROW rather than declared per card, so a future Set-off row
    with the same shape cannot be given the gate by remembering to. A `set_off`
    carrying `damage` is NOT covered: Ka-pow! with no Bombs on the board is
    still an Attack, and refusing it would be a balance change rather than a
    legibility fix.

    A `grow_bombs` AHEAD OF A SET OFF ON THE SAME TARGET IS COVERED (round
    three's extension, Quick Fuse): growing a pile that is not there does
    exactly as little as setting off a pile that is not there. The clause is
    deliberately narrow -- the grow must feed a LATER `set_off` aimed at the
    SAME target. A `multiply_set_off` ahead of a Set off is covered the same
    way (The Big One since R243, "4x with no flat number": the card's whole
    body is the Set off, so a Bomb-less board makes it a 3-energy nothing).
    """
    rest = [fx for fx in card.effects if fx.get("op") not in _COST_OPS]
    if not rest:
        return False
    if not any(fx.get("op") == "set_off" for fx in rest):
        return False
    for index, fx in enumerate(rest):
        if fx.get("op") == "set_off":
            if int(fx.get("damage", 0) or 0):
                return False
            continue
        if fx.get("op") == "multiply_set_off":
            if not any(later.get("op") == "set_off"
                       for later in rest[index + 1:]):
                return False
            continue
        if fx.get("op") != "grow_bombs":
            return False
        if not any(later.get("op") == "set_off"
                   and later.get("target") == fx.get("target")
                   for later in rest[index + 1:]):
            return False
    return True


def refuses_for_no_bomb(state: CombatState, card: Card) -> bool:
    """`card_playable`'s arm clause: a Set-off-only card is unplayable while no
    living enemy holds a Bomb."""
    return live(state) and set_off_only(card) and not any_bomb_placed(state)


# ---------------------------------------------------------------------------
# THE AIM -- one helper, for the random-target Set off
# ---------------------------------------------------------------------------

@contextlib.contextmanager
def aimed_at(state: CombatState, enemy: Optional[Enemy]) -> Iterator[None]:
    """Bind the play's aim to `enemy` for the duration of the block.

    RULE 2'S LAST SENTENCE NEEDS IT: "For random-target Attacks, per target
    hit." `SetOffRandom` rolls an enemy and hands THAT creature to both the Set
    off and the card's own hit, so the effective `cardPlay.Target` for the
    iteration is the rolled body -- and `card_aim` is this engine's name for
    `cardPlay.Target`. `state.kurage_aim` is the standing precedent for an aim
    handed to a play for the duration of one resolution.

    Restored in a `finally`, so a throw inside a volley cannot leave the play
    aimed at a body it never chose.
    """
    previous, previously_bound = state.card_aim, state.card_aim_bound
    state.card_aim, state.card_aim_bound = enemy, True
    try:
        yield
    finally:
        state.card_aim, state.card_aim_bound = previous, previously_bound

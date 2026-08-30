"""All tunable numbers for the Tier 0 simulator live here.

Nothing in engine/ may hard-code a balance number. If you need a new knob,
add it here with a comment. These are starting points, not gospel
(tier0-simulator-spec.md §0) — calibrate per §7, then freeze.
"""

# --- Core turn economy (StS defaults; spec §10) ---
BASE_ENERGY_PER_TURN = 3
CARDS_DRAWN_PER_TURN = 5
MAX_HAND_SIZE = 10
# IntangiblePower.ModifyDamageCap / ModifyHpLostAfterOsty both return 1 for
# the owner. Named rather than inlined because it is a base-game parity
# number that no design ruling of ours may tune.
INTANGIBLE_DAMAGE_CAP = 1
# DoubleDamagePower.ModifyDamageMultiplicative returns a literal 2, NOT
# base.Amount -- its stacks count TURNS (one decrements at each of the
# owner's turn ends), so this is a parity constant and not a stack read.
DOUBLE_DAMAGE_MULT = 2
# OutbreakPower.poisonThreshold, a public const on the power itself.
OUTBREAK_POISON_THRESHOLD = 3

# --- Fight limits ---
MAX_TURNS = 30            # hard cap; hitting it counts as a loss (stall)
MAX_CARDS_PER_TURN = 25   # beyond this the infinite detector flags the fight

# --- Powers ---
WEAK_DEALT_MULT = 0.75        # Weak: -25% damage dealt
VULNERABLE_TAKEN_MULT = 1.50  # Vulnerable: +50% damage taken
FRAIL_BLOCK_MULT = 0.75       # Frail: -25% BLOCK GAINED by the affected
                              # creature (StS Frail). A real DECAYING debuff
                              # in its own right -- NOT mapped to Weak (which
                              # is -damage dealt). Run-model rework §4/§8.
                              # StS floors block*0.75; the affected creature's
                              # card block is what it bites.

# --- Base-game Ironclad parity powers (engine/refpowers.py) ---
# Structural rates from the decompiled sources, not balance dials: the
# per-card Amounts live in game_ref/ironclad.json (gitignored) and never here.
COLOSSUS_TAKEN_MULT = 0.5     # ColossusPower.ModifyDamageMultiplicative
JUGGLING_ATTACK_TRIGGER = 3   # JugglingPower fires on the ==3rd attack/turn

# --- Elemental auras & reactions (spec §4.4; validate in M4) ---
AURA_DURATION_TURNS = 2       # owner-turns an aura persists unconsumed
VAPORIZE_MULT = 1.5           # Pyro x Hydro, that hit only
MELT_MULT = 1.75              # Pyro x Cryo, that hit only
OVERLOAD_SPLASH = 6           # flat damage to ALL enemies
OVERLOAD_WEAK = 1             # stagger: reacted target's next attack is Weak
SUPERCONDUCT_VULN = 2         # Vulnerable stacks applied
ELECTROCHARGED_DOT = 4        # DoT amount
ELECTROCHARGED_DOT_TURNS = 2
CRYSTALLIZE_BLOCK = 4         # player Block gained
FROZEN_BOSS_VULN = 2          # bosses consume Frozen for Vulnerable 2
                              # (round-3 ruling; STANDS through the v1.5
                              # errata — the freeze-team control identity)
# Frozen v2 (principles v1.5 §2.2 errata): no skip/stun at base. The
# frozen enemy's next action deals -50% damage; while Frozen, the first
# Attack hit Shatters it (bonus damage, removes Frozen).
FROZEN_DAMAGE_MULT = 0.5      # frozen enemy's next action damage multiplier
SHATTER_DAMAGE = 6            # bonus damage on shattering hit (the knob —
                              # errata: if gauntlet floor dips, tune this)
CONTROL_UPTIME_CARRY = 0.40   # §2.2a detector: won fights with more than
                              # this fraction of enemy actions negated by
                              # companion-sourced control flag SUPPORT_CARRY
                              # (propose-and-tune value from the errata)

# --- Klee resources (spec §4.2; klee-character-design.md §3) ---
# RETIRED-UNDER-FLAG. `SPARKS_FOR_FREE_ATTACK` is the base rule's whole number
# and it is UNREAD whenever `SPARK_ALT_COST_ENABLED` is true: with the flag on
# there is no threshold, no zeroing and no automatic consume, so the constant
# describes a rule that is not running. It is not deleted, because the flag's
# entire purpose (PICK 6, option 1) is to let the two economies stand side by
# side and be measured against each other; deleting it would make the OFF arm
# unexpressible. `combat.spark_threshold` carries the same marking.
SPARKS_FOR_FREE_ATTACK = 3    # at 3 Sparks, next Attack costs 0
# =============================================================================
# SPARKS AS AN ALTERNATIVE COST -- R213 E2 PROTOTYPE ARM, QUARANTINED.
#
# [USER], 2026-08-29: "The old base rule ('At 3 Sparks, your Attacks cost 0.
# Playing one consumes 3') is being retired as the universal base mechanic;
# Sparks become an ALTERNATIVE card cost (some Klee cards cost Sparks instead
# of Energy); Bomb detonation stays the main source."
#
# THE NAME AND THE HOME are the repo's own convention, not a new one: a
# behaviour switch is a `*_ENABLED` boolean declared beside the code it gates
# (`PILOT_POLICIES_ENABLED`, `MODE_CHOOSER_ENABLED` in tier0/pilot/policy.py),
# and this one lives beside the constant it retires.
#
# WHAT THE FLAG BUYS, and it is the reason PICK 6 took option 1 rather than
# flipping the rule outright: with it OFF every Klee number ever measured
# stays comparable, and the two economies can be run as two arms of one
# question. FLAG OFF IS BYTE-IDENTICAL TO TODAY -- an acceptance condition
# pinned by tier0/tests/test_spark_alt_cost.py, not an intention.
#
# WHAT MOVES WHEN IT IS ON, exhaustively (every site names this constant):
#   * combat.card_cost      -- the Attack-zeroing branch does not run.
#   * combat.play_card      -- the automatic consume does not run.
#   * combat.spark_price    -- the strict Rare Power contributes a price.
#   * loader._starter_ids   -- two starter substitutions (PICK 1, opts 1+5).
#   * pilot/policy.py       -- a Spark stops being "a third of a free Attack"
#                              and becomes a share of the cheapest affordable
#                              sink.
#   * tier05/draft.py       -- the Spark dials are re-derived (PICK 7).
# Nothing else in either engine reads it.
SPARK_ALT_COST_ENABLED = False

# THE STRICT RARE POWER (PICK 5, wording (1), sub-pick (a)). While
# `spark_attack_cost` is on the player, an Attack that does NOT already print
# a Spark price costs 0 Energy and this many Sparks instead, and is unplayable
# below them. An Attack that already prints one is UNAFFECTED -- sub-pick (a),
# because (b) would raise the price of the very cards the archetype drafts.
#
# 3 IS LIFTED, NOT PICKED: it is [USER]'s own phrase ("converts all attacks
# into 3-spark-cost attacks") and it is the retired threshold's own number, so
# the Power charges exactly what the base rule used to hand out for free.
SPARK_ATTACK_POWER_PRICE = 3

# THE STARTER SUBSTITUTIONS (PICK 1, options 1 and 5 together -- the seat:
# "Options 1 and 5 together follow"). Both are proto rows on
# docs/prototype-surface.yaml and both enter through the ONE seam at
# `loader._starter_ids`; NO PRINTED SHEET MOVES. Regent's ten-card starter
# ships exactly one generator (Venerate) and exactly one sink (FallingStar),
# so exactly ONE COPY of each is substituted here -- see the seam for the
# decision that leaves for [USER].
SPARK_ALT_STARTER_SUBS: tuple[tuple[str, str], ...] = (
    ("pop", "proto_pop_spark"),          # opt 1: the Basic that MAKES
    ("kaboom", "proto_kaboom_sink"),     # opt 5: the Basic that SPENDS
)

# THE OFFERABLE-POOL SUBSTITUTIONS -- PICK 4's own one-for-one map, read at
# `loader._pool_substitutions` under this same flag and nowhere else.
#
# WHY IT EXISTS. `KLEESPARK-R1` sec.11.6 item 5 records the gap as a limitation
# of the round: "`loader._pool_substitutions` returns `{}` for Klee, so the
# tier 0.5 drafter structurally cannot be offered a prototype Spark row",
# which forced P5 and P6 to read a deck assembled BY ID rather than drafted.
# The Kokomi arm had a pool seam and this one did not; the asymmetry was an
# omission, not a decision, and this is the same seam Kokomi already uses.
#
# THE MAP IS NOT NEW AND NOTHING HERE IS PICKED: it is the surface's own
# header, the one-for-one conversion PICK 4 describes, in the order the packet
# prints it. Each prototype is filed at the SHIPPED row's rarity and
# `rewards.character_pool` REFUSES a substitution that would move a card
# between tiers, so the offer odds are untouched -- three commons, two
# uncommons, one rare, in and out.
#
# WITH THE FLAG OFF this constant is UNREAD: `_pool_substitutions` returns
# `{}` for Klee exactly as before, `_substituted_card_index` stays empty, and
# no pool, reward, shop, event or drafter can see a `proto_` id. That is the
# acceptance condition, pinned by test rather than intended.
SPARK_ALT_POOL_SUBS: dict[str, str] = {
    "sparkly_treasure": "proto_spark_strike",      # Fwoosh!,         common
    "spark_collection": "proto_spark_double_tap",  # Bang Bang!,      common
    "pocket_fireworks": "proto_spark_sweep",       # Tinder Toss,     common
    "sugar_rush": "proto_spark_blast",             # Dodoco Blast,    uncommon
    "cant_catch_me": "proto_spark_finisher",       # Firework Finale, uncommon
    "true_spark_knight": "proto_true_spark_knight",  # the Oath,      rare
    # THE THREE HYBRID SPENDERS, MIGRATED (R224 slate item 16, EB-218). These
    # three are NOT conversions in PICK 4's sense -- no body and no number
    # moves. Each shipped row is a HYBRID (1 Energy AND `spend_spark 2`), and
    # its twin here is the same card at 0 Energy, so the whole delta is that
    # the bank alone can now reach it. Same rarity in and out (three
    # Uncommons), so the offer odds are untouched here too, and with the flag
    # off none of this is read.
    "powder_charge": "proto_powder_charge_spark",        # Set It Off,   uncommon
    "hold_the_line": "proto_hold_the_line_spark",        # Dig In,       uncommon
    "smoke_and_sparks": "proto_smoke_and_sparks_spark",  # Powder Smoke, uncommon
}
BURST_PER_SKILL_TAG = 5       # burst energy per Skill-tagged card played
BURST_PER_REACTION = 5        # burst energy per reaction triggered

# =============================================================================
# KLEE'S PERSONAL-COMPANION SPARK TRIGGER -- "Little Hexenzirkul" (EB-219).
#
# LAW:145, countersigned R224 (2026-08-30): "Companion cards may not themselves
# grant signature resources. A character-owned engine may respond to a
# Companion play and generate its resource where that character's kit
# explicitly declares the trigger and bounds the amount generated per Companion
# play." THIS BLOCK IS THAT DECLARATION, and it is the only place either engine
# says what a Companion play is worth in Sparks.
#
# THE TRIGGER: Klee plays a card from her PERSONAL Companion pool
# (`personal_pool: klee`). Not a shared companion, not another character's.
# THE BOUND: at most MAX_PER_PLAY, once per CARD PLAY -- a Companion resolved a
# second time by a replay (Study Buddy) is one play, not two. A per-play bound a
# replay can double is not a bound.
#
# NOTHING HERE IS PICKED. All four numbers are lifted off `prune_witch_hunt`'s
# committed face so that the player's yield does not move (R212(6),
# derived-not-picked): her row printed `gain_spark 1` inside a
# `reaction_triggered_by_this` conditional AND `gain_spark 1` unconditionally at
# top level, with `{spark: +1}` on the upgrade bumping the unconditional one.
# So she paid 1 / 2 / 2 / 3 (base-no-reaction / base-reaction / upgraded-no-
# reaction / upgraded-reaction) and BASE + REACTION + UPGRADED reproduces all
# four. The cap is the arithmetic ceiling of the three, not a fifth number.
#
# REACH: general in form, Prune-only in fact -- exactly one row in the four
# committed companion sheets carries `personal_pool`. A second Personal
# Companion authored for Klee later falls under this declaration automatically,
# which is why the trigger is declared over the POOL and not over one card.
KLEE_COMPANION_SPARK_BASE = 1              # any Personal Companion play
KLEE_COMPANION_SPARK_REACTION_BONUS = 1    # ...that triggered a reaction
KLEE_COMPANION_SPARK_UPGRADED_BONUS = 1    # ...and/or is upgraded
KLEE_COMPANION_SPARK_MAX_PER_PLAY = 3      # the bound LAW:145 requires

# --- Klee power tunables (notes in klee-cards.yaml / companions sheet) ---
SPARKS_N_SPLASH_HITS = 4          # end of turn: N hits...
SPARKS_N_SPLASH_HIT_DMG = 5       # ...of this damage, each applies pyro
PLAYTIME_BOMB_DAMAGE = 5          # Playtime Forever's per-turn bomb
DETONATION_SPLASH_BURST = 3       # Blazing Delight: burst energy per detonation
DETONATION_SPLASH_PROC_CAP = 3     # max splash procs/turn. ARMED by the
                                   # errata/M5 triage (ruling 1): sanctioned
                                   # demolition ceiling knob for band
                                   # violations too. Sheet v0.4 codifies it
                                   # on blazing_delight (drift-guarded in
                                   # test_errata).
OZ_DMG = 3                        # Oz end-of-turn hit (applies electro)
WITCHS_FLAME_BURST = 3            # Durin: Burst Energy per consumed Pyro aura
SOLAR_ISOTOMA_BLOCK = 3           # block per attack hit vs aura'd enemy
CELESTIAL_GIFT_BLOCK = 4          # Nicole: block at start of turn
MASQUE_BOND_BLOCK = 5             # Arlecchino: Bond of Life, Block owed per turn
CATALYTIC_BURST_PER_REACTION = 5  # Catalytic Converter bonus burst/reaction

# --- Furina: Spotlight (kickoff §3) ---
SPOTLIGHT_BASE_MULT = 1.5     # RATIFIED (R71, 2026-07-26). The W0
                              # forced-arm sweep {1.25, 1.5} was the
                              # PRE-REGISTERED decision procedure -- this
                              # comment said "decides", and it did: pass 3
                              # returned dose evidence favouring 1.5
                              # (furina-pass3-rulings.md). R71 makes law of
                              # a result already committed to; the value
                              # does not move, so no number in the tree
                              # changes with this line.
                              # History, kept because it is why the
                              # PLACEHOLDER marking existed at all:
                              # the pass-2 "MEASURED 1.0" record is STRUCK
                              # (R33 veto, 2026-07-20). E1's identical
                              # cells were guaranteed by selector v2
                              # (companion branch unreachable at ~20 self
                              # cards vs 3-5 card kits) -- the constant was
                              # never READ in any cell (exercise-counter
                              # law, DECISIONS 87). E1 re-scoped to a valid
                              # MEDIAN-DEPTH null only; never summarize it
                              # as "the knob is dead". 1.5 restored the
                              # pass-1 companion geometry against the
                              # then-current self rate of 1.25. R40 later
                              # moved self aim to 1.0 without changing this
                              # outward-Spotlight value.
# SPOTLIGHT_SELF_MULT: DELETED by R67 (2026-07-26). It had zero readers --
# effects.spotlight_mult() hard-codes the 1.0 self-aim early return and never
# consulted the constant -- so exp_furina_sheetpass block C2 swept three
# guaranteed-identical cells. Those rows are STRUCK as instrument error, not
# read as "the self rate doesn't matter". The rule it encoded still holds and
# is now expressed only in code: Furina pays no hidden baseline tax, self aim
# drives Ovation/Fanfare, and numeric empowerment is reserved for companions.
SPOTLIGHT_GUEST_CAST = "__guest_cast__"  # all Companion cards share the light
# Selector heuristic history. The SPOTLIGHT_SELECTOR_VERSION stamp that used
# to sit at the end of this block was DELETED by R67 (2026-07-26): it was read
# by nothing, so it stamped no report and could not have stopped anyone from
# comparing selector versions unlabeled — the one job an instrument stamp has.
# The history it guarded is real and stays here as documentation; the shipped
# selector is v5, and "never compare selector versions unlabeled" survives as a
# house rule rather than as a constant that pretended to enforce it.
# v1 companions-always (sprint 1; measured harmful — 1-card guest
#    hijack halved Ovation throughput);
# v2 raw depth contest (passes 1-2; R33 found the companion branch
#    UNREACHABLE at ~20 self cards vs 3-5-card kits — every pass-2
#    number is a self-Spotlight world);
# v3 value-aware threshold (pass 3, derived from the W0 oracle arms):
#    designate the deepest companion iff its per-character depth
#    reaches SPOTLIGHT_COMPANION_DEPTH_MIN (4) AND the stage holds a
#    crowd (>= SPOTLIGHT_COMPANION_MIN_ENEMIES, 2, living enemies);
#    otherwise self. W0 evidence: forced-companion at full-kit depth
#    is +12.5pt on attrition and -10pt on tank_boss — outward aim is
#    encounter-contingent, so the selector reads the fight, not just
#    the deck.
#    RATIFIED (R71, 2026-07-26) — and ratified as a RECORD, not as live
#    law. v5 replaced character-depth targeting outright on 2026-07-23
#    (commit b4b4434) and deleted both constants along with the branch
#    that read them, three days before the ruling landed. The
#    ratification is honoured by writing down what it ratified; it is NOT
#    honoured by resurrecting two constants nothing reads, which is the
#    class R67 had just deleted nine of. If v3's geometry is ever wanted
#    back, 4 and 2 are the ratified numbers to restore it with.
# v4 keeps v3 for drafted companions, but a card created into hand by a
#    Guest Star generator is eligible at depth one.
# v5 replaces character-depth targeting with the explicit two-mode design:
#    Center Stage Spotlights Furina and generates Fanfare without a numeric
#    multiplier; Guest Cast Spotlights every Companion card at the outward
#    multiplier and generates no Fanfare from those plays. The selector picks
#    Guest Cast when a Companion is ready in hand, otherwise Center Stage.
SPOTLIGHT_CARDS_PER_TURN_CAP = None   # schematized but OFF (kickoff §3.2):
                              # turns on only if Tier 0 shows the rate
                              # asymmetry alone fails the §6 criterion.
                              # When set: empowered plays per turn beyond
                              # the cap resolve at printed numbers.

# --- Furina: Encore & Fanfare (kickoff §4) ---
# Encore is unbounded per-combat (v1.6) -- no cap constant by design.
FANFARE_CAP_FRACTION = 0.5    # Fanfare cap = fraction of maxHP.
                              # DEMOTED to a high safety rail by the Tide
                              # Turns sprint (F-A5, executor's call, logged
                              # in docs/archive/furina-fanfare-sprint-log.md): under
                              # decay the ceiling never binds -- the W2
                              # cap-1000 cells reported 0.0% at-cap -- and
                              # uncapping was worth +0.2pt to the archetype
                              # named after the stat. Kept, not deleted, so
                              # a degenerate floor-stack still has a stop.
                              # Prior life: RATIFIED (R17, 2026-07-20) as a
                              # first-order dial, sweep-bracketed (0.25
                              # cripples punisher at 2.4%, 0.75 overheats
                              # at 63%). Those numbers are ARCHIVE -- they
                              # were taken in the spendable-Fanfare world.
FANFARE_PER_HP_LOST = 1       # per point of true HP lost
FANFARE_PER_ENCORE_SPENT = 1  # per point of Encore deliberately spent
FANFARE_PER_ENCORE_ABSORBED = 1   # per point of Encore eaten by a hit
# FANFARE_PER_ENCORE_GAINED: DELETED by the Fanfare rework (2026-07-28, Track
# A, RULED). Fanfare now prints when Encore goes DOWN and never when it goes
# up. Encore used to mint on BOTH legs, so a card granting 3 Encore silently
# printed 6 Fanfare -- measured at 47% of generation under the greedy pilot
# and 62% under the stoker (pilot-gap P4), i.e. the better the loop was
# played, the more of its output came from the loop taxing itself twice.
#
# The third reduction path, ABSORPTION, was previously worth nothing and now
# pays: absorbed Encore is deferred Block that will never block a future hit,
# so cashing it is a real cost (RULED). That closes an asymmetry rather than
# opening one -- see resources.absorb_into_encore and the invariant test
# test_every_point_past_block_prints_exactly_one_fanfare: after this change
# EVERY point of damage that gets past Block prints exactly 1 Fanfare, via
# absorption if the buffer eats it and via hp_lost if HP does. Those three
# constants are therefore not independently tunable any more; the test is
# what says so out loud.
FANFARE_PER_SPOTLIGHT_CARD = 2    # the Ovation merge: per Spotlighted
                              # card played. NO passive per-turn accrual
                              # constant exists; do not add one (§4).

# --- Fanfare as a read-only momentum stat ("The Tide Turns", F-A1/F-A3;
# direction RATIFIED 2026-07-24, every NUMBER below PROPOSED pending
# red-pen). Fanfare is no longer spendable: it is generated by activity
# flux (above), DECAYS each turn, and is FLOORED by permanent constellation
# grants. Encore is Furina's only managed resource. ---
FANFARE_DECAY_FRACTION = 0.20 # PROPORTIONAL decay, as a fraction of the
                              # meter. This is the ONLY decay shape: R67
                              # (2026-07-26) deleted the flat fallback knob
                              # and its branch, so there is no longer an
                              # "instead of" to read this against.
                              # RULED 20% by [USER] 2026-07-24, REVERSING
                              # the plan's flat-over-proportional direction
                              # on measurement: a flat subtraction is one
                              # number for every meter level, so it barely
                              # dents a full meter while driving a low one
                              # to zero (flat-5 left 12.8% of Fanfare reads
                              # finding NOTHING). Proportional is asymptotic
                              # and never empties the pool, so it beats flat
                              # at BOTH tails at once -- 20% has a lower
                              # at-cap than flat-3 (0.1% vs 4.3%) AND a
                              # lower empty rate (8.3% vs 10.1%), at
                              # identical winrate. The tooltip argument that
                              # picked flat does not bite: "fades by 20%
                              # each turn" is the same one-line rule.
                              # Semantics: a fraction of the WHOLE meter,
                              # clamped at the floor (not a fraction of the
                              # amount above it) -- "Fanfare fades by 20%
                              # each turn" is the one-line rule, and the
                              # floor clamp already protects the baseline.
                              # Always removes at least 1 while above the
                              # floor, so the meter cannot stall out at a
                              # value too small to round down.
# FANFARE_DECAY_PER_TURN: DELETED by R67 (2026-07-26), together with the flat
# branch in resources._decay_amount and the resources.py assert that guarded
# it. It was reachable only when FANFARE_DECAY_FRACTION == 0, which the 20%
# ruling above made permanently false, so exp_furina_decay's magnitude sweep
# produced five identical rows that read as a null result about decay strength
# and were nothing of the kind. Those rows are STRUCK as instrument error.
# The historical flat-vs-proportional comparison that DECIDED the shape is
# preserved in the FANFARE_DECAY_FRACTION comment above; it is a record, and
# it is no longer reproducible in-tree because the flat shape no longer exists.
# A constellation grant is STATIC value, not accrual: it does not grow with
# time, so stalling still earns nothing and the no-passive-accrual law
# (kickoff §4) is intact, not amended.
#
# FANFARE_FLOOR_PER_POWER / _RARE: DELETED by the Fanfare rework (2026-07-28,
# Track B, RULED). They were the invisible rule -- every Power played raised
# floor, cap AND current by 5 (rares 8), printed on no card and explained in
# no tooltip. The value does not vanish; it MOVES ONTO THE CARDS, as two
# printed keywords:
#
#   "Fanfare Cap +X"  raise_fanfare_cap  -- the ceiling only
#   "Fanfare +X"      gain_fanfare_floor -- current, floor and cap together,
#                                           a RARE POWER payoff only
#
# Spelled "Fanfare Cap", never bare "Cap": bare "Cap" is ambiguous with the
# Salon's member cap, which is also a per-player stat since A12.
#
# The keyword convention is only safe while no card grants TRANSIENT Fanfare
# directly -- all remaining generation sources are indirect (hp_lost,
# encore_spent, encore_absorbed, center_stage), so "Fanfare +X" can mean the
# permanent grant without ambiguity. tools/lint_furina_registers.py L12 is
# the blocker that keeps it that way; the first direct transient grant would
# make the keyword ambiguous forever, so it fails the build rather than
# arriving quietly.
#
# WHAT THIS COSTS. The automatic was ~4% of her actual power by the 38d7769
# measurement (the visible Fanfare number moved ~22%, but most of that sat
# above what any reader consumed). It is deleted from non-Rares outright and
# is measured TOGETHER with Track A -- the two are never attributed
# separately without an ablation arm.

# --- Furina: Salon Members (kickoff §5; Salon v2 rework 2026-07-23,
# docs/archive/furina-salon-rework-plan.md) ---
# NUMBERS RATIFIED 2026-08-13 (R187, QUEUE M24). The rework plan's "every
# NUMBER below is PROPOSED pending red-pen" banner used to sit on this line
# and it was the last unsigned gate on the six member values; the derivation
# it was signed against is review/active/eb77-salon-summon-damage-derivation.md.
# The six values below are UNCHANGED by the countersign -- signing moved no
# number, so this is not a CONSTANTS_VERSION event. Recorded because the
# banner's absence is otherwise indistinguishable from nobody having written
# it: Crabaletta 6/14, Usher 3/9 Block and Chevalmarin 2/+3 Encore are signed
# as written, the Crabaletta/Usher gap is intended texture rather than a
# 1:1 damage-for-Block exchange, a pure Salon deck is NOT expected to reach
# Focus +2 on its own (cross-archetype Fanfare may earn the higher tiers),
# the directive's upward adjustment reads as satisfied holistically, and
# Chevalmarin's 2 -> 1 dry truncation is accepted. The paired signing surface
# is SalonConstants in klee-mod/KleeCode/Powers/SalonPowers.cs; the mod's
# displayed strings interpolate those constants since EB-86, so a future
# repricing moves the constants and the tooltip follows.
# v2 = the full Defect-orb grammar per user directive: members are TYPED
# (unique slot passive at start of player turn + unique final bow when
# displaced), the queue is FIFO (deploying into full slots bows the OLDEST
# member out), and Fanfare is the Focus analogue: every member NUMERIC
# amount gains +1 per SALON_FOCUS_PER held Fanfare at resolution (auras and
# the Encore bow rider do not scale -- numbers-only, §2.2a discipline).
# v1 (archive: uniform anonymous 4-damage ticks, overflow self-bows at x3)
# is the world of sheet passes 1-3 and every pre-rework Furina number.
SALON_MEMBERS = {
    # member: tick (slot passive) / bow (displaced payoff). "damage" ticks
    # are hydro to a random enemy; "block" is player Block; "aura" applies
    # hydro (chevalmarin's tick deals its damage AND applies; her bow
    # applies to ALL enemies and refunds Encore -- activity-gated, legal).
    "crabaletta":  {"tick": {"damage": 6},  "bow": {"damage": 14}},
    "usher":       {"tick": {"block": 3},   "bow": {"block": 9}},
    "chevalmarin": {"tick": {"damage": 2, "aura": True},
                    "bow": {"aura_all": True, "encore": 3}},
}
SALON_FOCUS_PER = 10          # +1 member numbers per this much held Fanfare
                              # (cap 30 -> +3; uncapped 45 -> +4)
SALON_MEMBER_SLOTS = 3        # Defect-orb shape: fixed active company
SALON_REPLACE_NUMERIC_MULT = 2  # deploy card's OTHER numerics on replacement
SALON_REPLACE_DAMAGE_MULT = 3   # deploy card's damage riders on replacement
SALON_TICK_ENCORE_COST = 1    # Encore drained per member tick
SALON_DRY_DAMAGE_MULT = 0.75  # no Encore: tick numerics at three-quarters;
                              # never true-HP loss (auras still apply)
SALON_TICK_BURST = 2          # burst energy per member tick AND bow (her
                              # particle economy leans on Salon, §1)
BURST_PER_ENCORE_SPENT = 1    # burst energy per point of Encore spent
                              # (the other half of her particle economy)

# --- Kokomi: Charge & the Pearl of Wisdom relic (kickoff v1 §2; ALL numbers
# PROPOSED — kickoff constants are [USER]-gated at battery freeze, none
# ratified). The relic carries only the two conversion laws (R16:
# bookkeeping in the relic, payoff magnitude in cards): exhaust→Charge and
# Strength→Charge. Charge is uncapped, never expended, card-event-driven
# only — no per-turn passive accrual constant exists here and none may be
# added (the Furina Fanfare precedent).
#
# NAMING (v0.4 lore overlay §3, [USER]-ruled): the relic is displayed as
# "PEARL OF WISDOM" — her signature catalyst, held-item fiction, and the
# community's own epithet for her. It used to wear "Tamakushi Casket",
# which is wrong: the wiki confirms Tamakushi Casket is her 1st Ascension
# PASSIVE, and what it actually does is refresh a fielded Bake-Kurage when
# she casts Nereid's Ascension. That name therefore moved to the mechanic
# that does that job — the Garment↔Kurage refresh in effects.py — where
# canon puts it. The hook IDENTIFIER stays `tamakushi_casket` on purpose:
# ids are stable across the lore overlay (only all_streams_flow renamed
# id-level), and the id now sits on the engine that powers the link it is
# named for. Relic MECHANICS are unchanged by the rename. ---
CHARGE_PER_EXHAUST = 1        # kickoff §2.1 base accrual (universal rule:
                              # every card through the exhaust funnel)
KOKOMI_BURST_PER_EXHAUST = 2  # her particle economy: burst energy per
                              # exhaust event (skill_tag 5 + reactions 5
                              # are the shared sources; this is her Salon-
                              # tick analogue). PROPOSED.
                              # THE DOUBLE WAGE, said out loud (addendum A9).
                              # One exhaust event pays TWICE on this sheet:
                              # CHARGE_PER_EXHAUST above AND this. That reads
                              # like a duplicated payout and it is not; it is
                              # her identity payment, and R79 is what makes it
                              # legitimate rather than greedy. LAW 5 hands the
                              # card/energy economy -- draw, energy, cycling,
                              # selection -- to the Discard/Sly lane as a
                              # MONOPOLY, so the exhaust verb has no economy
                              # rider to be paid in. What it has instead is
                              # these two meters. Strip either one and the
                              # exhaust lane is a lane that spends cards and
                              # buys nothing, because the law already gave
                              # away the thing it would otherwise buy.
                              # CONSEQUENCE FOR ANYONE TUNING THIS. These two
                              # constants are one wage in two currencies, so
                              # they move together or the reason moves with
                              # them; halving this alone is not "a small burst
                              # nerf", it is a partial repeal of the payment
                              # R79 obliges. The exhaust funnel splits its
                              # source (exhaust vs exhaust_muster) in
                              # refpowers.py precisely so the wage can be read
                              # per-source before anyone touches it -- see
                              # tier05/burst_telemetry.py, which is a trace
                              # and not an allowlist for the same reason.
CEREMONIAL_GARMENT_TURNS = 3  # Shape B state duration (stacks = turns,
                              # decays at player turn end). PROPOSED.
# v0.3 charge-curve pass (user-directed 2026-07-24, PROPOSED): 4 -> 2.
# The audit vs the Regent-common benchmark ("deal 7, Forge 7, 1 cost")
# found her meter read ~4x under the comparison power level; at /4 a
# node-4 bank of 8 Charge paid +2 per attack -- decoration, not a
# scaling identity. At /2 a priest-median 24-Charge Garment window is
# +12 per attack for 3 turns: Burst-tier, which is what a Burst is.
GARMENT_CHARGE_DIVISOR = 2    # while the state is active, attack cards
                              # gain +1 damage per this much Charge (the
                              # "scaled down per hit" read, §2.2 Shape B).
                              # KNOB_READS-instrumented. PROPOSED.
# --- v0.4 O4 salvage (plan §1, [USER]-ratified 2026-07-26; PROPOSED
# numbers, all five KNOB_READS-instrumented). The thesis: v0.3 bought its
# act-1 clear by making the BURST a metronome, which the ratio instrument
# correctly reads as frontload. O4 moves the periodic output to the summon,
# where canon keeps it, and lets the Burst go back to being a window. ---
KURAGE_DURATION = 1           # RETIRED UNDER THE KURAGE_MEMORY FLAG (v4 base
                              # kit): with KURAGE_ALWAYS_ON the jellyfish is
                              # installed at combat start and never expires,
                              # so nothing reads this while the flag is on --
                              # not the install, and not the Casket refresh,
                              # which maxes a 1 against a 1. The value below
                              # is the SHIPPED one and stays exact, because
                              # with the flag off this constant is still the
                              # whole of the summon.
                              # turns the jellyfish holds the field. Stacks
                              # = turns remaining (the oz_summon grammar);
                              # re-summoning REFRESHES, never adds — a
                              # second jellyfish is not a bigger jellyfish.
                              # v0.4 STARTER REWORK ([USER], 2026-07-26):
                              # 3 -> 1. At 3 the summon was effectively
                              # permanent; at 1 it is a delayed strike that
                              # must be re-bought every time. Upgrade goes
                              # to 2 (kurage_turns +1).
                              # KNOWN CONSEQUENCE, on the record: the
                              # Tamakushi Casket link (Garment cast
                              # refreshes a fielded Kurage) is near-dead at
                              # duration 1 — it only fires if the Burst goes
                              # off the same turn the Kurage was played. The
                              # canon loop survives in code, not in practice.
                              # COUPLING PIN (playtest sprint P1): this
                              # constant is also the pulse FREQUENCY, and
                              # Kurage's Oath pays its ward once per pulse.
                              # The Oath's 12 was measured here at 1. Raise
                              # the duration and you have repriced a Common
                              # power that already carries a [USER] "maybe
                              # too strong" flag, without editing its row.
                              # test_oath_ward_is_pinned_to_the_pulse_
                              # frequency_it_was_measured_at fails on that
                              # edit by design — re-measure the Oath, then
                              # move the pin and both notes together.
KURAGE_PULSE_BASE = 4         # flat damage per turn-end pulse, before the
                              # bank read (v0.4 starter rework: 2 -> 4).
KURAGE_PULSE_PER_CHARGE = 3   # pulse gains this much damage PER POINT of
                              # Charge. v0.4 starter rework ([USER]): the
                              # read flips from a DIVISOR (+1 per 4 Charge)
                              # to a MULTIPLIER (+N per Charge) — the design
                              # intent is "every Exhaust is worth about a
                              # Silent shiv toss", i.e. one banked point
                              # buys roughly one shiv of damage.
                              #
                              # R73 (Neap Tide v2.1, 2026-07-26): x4 -> x2,
                              # then x2 -> x3 when E1 graded P6 and the
                              # pre-committed weak-side fallback FIRED. The
                              # landed value is x3 — RATIFIED at the R130
                              # sitting, 2026-08-07, so the fallback's landing
                              # is the ruled number and not a pending read;
                              # x2 is measured, rejected, and kept on the
                              # record below because the rejection is the
                              # reason x3 is here.
                              # The x4 WATCH note this replaces was right and
                              # is kept as the reason: Charge is uncapped and
                              # never spent (R80), so this term only ever
                              # grows, and at x4 a BASIC out-read both
                              # rate-limited readers — at bank 10 the pulse
                              # was 44 vs nereids' (Rare) 17, at bank 25 it
                              # was 104 vs 24, inverting the §2.2 reader
                              # hierarchy. x2 halves the slope without
                              # touching the ACCRUAL side, which is the whole
                              # point of the knob-order commitment: the bank
                              # fills at the same rate, it just buys less.
                              # E1 GRADING OF P6 (600 runs, seed 11, C4,
                              # against same-world roster anchors). Act-1
                              # clear across the rest of the roster spans
                              # 57.5% (furina/fanfare) to 85.8% (klee/
                              # reaction), with ref_ironclad at 62.2%.
                              #   x2: her BEST plan cleared act 1 57.2% --
                              #       below the roster floor -- and three of
                              #       four plans sat far under it, with her
                              #       best full-run win 5.2% vs the reference
                              #       Ironclad's 6.3%. That is weak
                              #       EVERYWHERE, not "mortal in acts 2-3",
                              #       so P6's single pre-committed response
                              #       fired.
                              #   x3: priest 60.3 / commander 66.0 /
                              #       generic 55.7 act-1, i.e. inside the
                              #       band around ref_ironclad, and priest
                              #       8.7% / commander 6.7% win.
                              # assist stays weak at every value (2.0% win
                              # even at x4). That is a PLAN problem and must
                              # not be answered with this knob.
                              # Nothing else on the accrual side moves.
                              #
                              # WATCH (restored by addendum A1b, and it is
                              # MORE live at x3 than it was at x4, not less).
                              # The x4 watch was retired in the first draft of
                              # this comment on the reasoning that the cut had
                              # answered it. It had not. G2 ratified STACKING
                              # "Before Sun and Moon", which adds +1 (+2
                              # upgraded) to THIS coefficient and does not cap,
                              # so the cut lowered the FLOOR and left the
                              # ceiling to the drafter: one upgraded copy is
                              # x5, a pair is x5-x7, and 4-5 is the ordinary
                              # in-run read for a committed priest deck. The
                              # bank underneath is still uncapped and still
                              # never spent (R80), so this remains the only
                              # term in her kit that can only grow.
                              # WORKED EXAMPLE, at the LANDED x3 (update it
                              # when this number moves, or it becomes a lie
                              # that reads like a check):
                              #   bank 10, x3       pulse 4 + 30 =  34
                              #   bank 10, x5 (BSM) pulse 4 + 50 =  54
                              #   bank 25, x3       pulse 4 + 75 =  79
                              #   nereids' (Rare)   17 at bank 10, 24 at 25
                              # So the §2.2 reader hierarchy is upright at the
                              # BASELINE and inverts behind one Uncommon draft.
                              # That is the ratified design (sell the slope
                              # back for a card slot), and it is exactly why
                              # C4 reports stack counts. R14: the telemetry
                              # carries no threshold. The thing to look at
                              # first if the priest lane runs hot is the PAIR,
                              # not this constant.
KURAGE_PULSE_BLOCK = 0        # Block granted by each pulse. v0.4 starter
                              # rework ([USER]) turned this OFF (was 2): the
                              # pulse is damage now, not mending. NOTE this
                              # is where R51 had put the healer fantasy that
                              # feeds the stability band, and it is what
                              # retired the priest Garment-uptime watchlist
                              # in the first W2 pass — a one-constant
                              # restore if that reads as a loss.
GARMENT_ATTACK_BLOCK = 2      # while the Garment holds, her attack cards
                              # ALSO grant this much Block (Charlotte
                              # precedent). Canon: her burst's attacks
                              # damage AND restore the party. Feeds the
                              # stability band where R51 put the healer.
CONSCRIPT_COST_DELTA = -1     # kickoff §2.3: a conscripted card costs 1
                              # less (floor 0) and gains Exhaust.

# --- THE KURAGE'S MEMORY: a QUARANTINED rule prototype, VERSION 3
# (review/active/kokomi-kurage-memory-2026-08-29.md sec.11). NOT SHIPPED, NOT
# MEASURED, and no number taken off this arm is quotable anywhere -- the
# R213 B / R215 B principle applied to a RULE rather than to a card row:
# the quarantined surface exists to be PLAYED, not measured.
#
# THE ACCEPTANCE CONDITION ON THE FLAG ITSELF is that with KURAGE_MEMORY
# False not one byte of shipped behaviour changes. Every read of every
# constant below sits inside an `if C.KURAGE_MEMORY` branch, so the shipped
# engine cannot reach any of them; tier0/tests/test_kurage_memory.py holds
# the golden that says so out loud (the shipped pulse is 4 + 3 x Charge).
#
# VERSION 3 ([USER], 2026-08-29) REPLACED v2's entry rule and its price.
# v2 remembered every Companion she PLAYED and every memory cost one flat
# threshold. v3 has TWO INDEPENDENT ENTRY RULES and a per-card price:
#
#   RULE 1 -- MUSTER. The card SACRIFICED to a Muster enters the memory at
#   the moment of transformation, on its ORIGINAL face, with no stored
#   target. It does not matter what the Muster produced or what becomes of
#   it. ([USER]: "We would be adding the card that was sacrificed for the
#   Muster, not the new card - so the original face.")
#
#   RULE 2 -- EXHAUST. A Companion that did not originate from the memory
#   enters when it EXHAUSTS, however it came to exist -- drafted, Mustered
#   or created -- carrying the target it was played against. ([USER]: "so
#   cards with Exhaust get played twice, otherwise you have to manually
#   exhaust them".)
#
# The two rules never reference each other ([USER]: "Those should be
# independent mechanics"), so one Muster of a card whose recruit prints
# Exhaust yields TWO memories in order, and that is intended ([USER]: "No,
# if the Muster prints a card that Exhausts, then it gets added as well.").
#
# PRICE is per card: 3 x the remembered card's own face cost. FUEL is the
# shipped exhaust funnel at CHARGE_PER_EXHAUST, on every Exhaust of an
# ORIGINAL card of hers -- a memory copy pays nothing and is not an Exhaust
# event at all. FIRE is one card per turn at turn start, and an unaffordable
# front BLOCKS the queue.
KURAGE_MEMORY = False         # the master quarantine flag. False = today's
                              # engine, exactly. True = the redesign: the
                              # jellyfish is persistent, remembers what she
                              # burns, and spends Charge to replay it for 0
                              # energy.
KURAGE_ALWAYS_ON = True       # v4 BASE KIT ([USER], 2026-08-29): "I think
                              # that we will want to make Bake-Kurage part of
                              # the base kit (always on) rather than a
                              # separate card." READ ONLY WHEN KURAGE_MEMORY
                              # IS ON. True = the jellyfish is installed at
                              # the start of every one of Kokomi's combats and
                              # holds for the whole fight: no duration, no
                              # expiry, no summon needed, and the pulse fires
                              # at every turn end. False leaves the v3 arm
                              # reachable, where the jellyfish still had to be
                              # summoned by the card and then never expired.
                              # A separate constant so a revert to the v3
                              # shape is a flip and not a re-authoring, the
                              # same way KURAGE_THRESHOLD is for v2.
KURAGE_MEMORY_STARTER_DROP = "bake_kurage"
KURAGE_MEMORY_STARTER_ADD = "to_the_front"
                              # The base-kit starter swap, and the ONLY sheet
                              # fact the flag moves. READ ONLY WHEN
                              # KURAGE_MEMORY IS ON, at `loader._starter_ids`,
                              # so `docs/kokomi-cards.yaml` and
                              # `tier0/content/characters/kokomi.yaml` are
                              # UNTOUCHED and the shipped starter is still the
                              # printed one. Bake-Kurage leaves because it
                              # summons what is already there; ONE Muster card
                              # enters in its place so RULE 1 (a Muster
                              # remembers the card it ate, priced at 3x its
                              # cost) is PRINTED in fight 1 rather than
                              # drafted. The count is unchanged at twelve.
                              # "To the Front!" is the plain Muster -- 0-cost
                              # Skill, conscript 1, no rider -- and 0-cost
                              # means it is playable on any turn, so fight 1
                              # always shows the pattern. Rarity Common,
                              # which is Furina's `an_invitation` precedent (a
                              # Common already sits in a printed starter), so
                              # no Basic twin is owed. sec.12 lists the three
                              # alternatives that were not built.
KURAGE_MEMORY_POOL_DROP = "kurages_oath"
KURAGE_MEMORY_POOL_ADD = "proto_kurages_oath_memory"
                              # The OFFERABLE-POOL swap: the sec.12.4 twin of
                              # the starter swap above, read the same way --
                              # ONLY WHEN KURAGE_MEMORY IS ON, at
                              # `loader._pool_substitutions`, with both sheets
                              # UNTOUCHED. [USER] asked of the staged face,
                              # 2026-08-29: "Why does the power print 5
                              # instead of 3, exactly?" Because with the flag
                              # on the ward is paid on a MEMORY PLAY and its
                              # amount is read off whatever card applied it,
                              # so a run that DRAFTED the shipped Oath paid 5
                              # per memory play under a face that says per
                              # pulse. Text that cannot bind is a defect (D4)
                              # and the shipped row is frozen under R213, so
                              # the fix is on the OFFER side: under the flag
                              # the shipped Oath leaves Kokomi's offerable
                              # pool and the staged row takes its slot, at the
                              # SAME rarity, so a flagged run can only ever be
                              # offered the 3.
KURAGE_MEMORY_COST_PER_ENERGY = 3
                              # [USER], v3: "cards cost Charge equal to 3x
                              # their Cost". The whole price rule. A 0-cost
                              # card therefore costs 0 Charge and autoplays
                              # free (Gorou in the starter deck is the named
                              # example); a 2-cost card costs 6.
KURAGE_MEMORY_COST_BASIS = "remembered_face"
                              # The face the price is read off, and there is
                              # now only ONE reading of it: the printed cost
                              # of the CARD THAT ENTERED, as that instance
                              # reads it. Permanent upgrade changes count;
                              # a Muster's own -1 counts on the recruit's own
                              # entry (Rule 2) because the recruit IS the
                              # card that Exhausted; TEMPORARY combat
                              # discounts (cost_delta_this_turn, this_combat,
                              # free_this_turn, the companion cost mod) are
                              # ignored, because the price is read off the
                              # card and never off `combat.card_cost`.
                              # v2's "original_print" alternative is RETIRED
                              # by v3's Muster ruling: the sacrificed card
                              # enters on its own original face, so the two
                              # readings no longer differ.
KURAGE_MEMORY_TARGET_FALLBACK = "random"
                              # [USER], v3: "Cards must play against the same
                              # target the second time, unless that target no
                              # longer exists, in which case they play
                              # randomly against eligible targets." The
                              # stored target is used whenever it is alive;
                              # this constant is only the FALLBACK. "random"
                              # (v3 default) leaves the shipped forced-random
                              # roll in charge. "most_hp" (v2's PICK E1
                              # fallback) is implemented so the arm can be
                              # swept -- it is more forecastable and less
                              # what [USER] asked for.
KURAGE_FIRE_TIMING = "turn_start"
                              # [USER], v3: "At the start of Kokomi's turn".
                              # "turn_end" is still implemented so the arm
                              # can be swept; it is not what v3 asks for.
KURAGE_QUEUE_CAP = 0          # 0 = UNCAPPED. [USER], v3: "I don't think we
                              # need to cap this. If you load Memory with 20
                              # cards, they slow-play over 20 turns ... if you
                              # have the Charge." The queue is bounded by the
                              # ONE FIRE PER TURN clause and by the bank, not
                              # by a length.
KURAGE_MEMORY_KEYWORD_NEEDS_SUMMON = True
                              # RETIRED UNDER THE FLAG by v4's base kit: with
                              # KURAGE_ALWAYS_ON the jellyfish is on the field
                              # for every turn of every fight, so "is there a
                              # summon" is always yes and both settings of
                              # this constant read the same. It is kept, and
                              # kept True, so that turning KURAGE_ALWAYS_ON
                              # back off restores the v3 arm whole. The
                              # paragraph below is v3's and still describes
                              # what it does THERE.
                              # NOT A [USER] PICK -- a hole the build had to
                              # fill. The acceleration keyword's op
                              # (`play_front_memory`, provisional keyword name
                              # "Stir") fires the front outside the automatic
                              # rhythm. True: it still needs a jellyfish on
                              # the field, i.e. one rule for what may act on
                              # the memory. False (implemented): the keyword
                              # works with no summon, so a card printing it is
                              # never dead. sec.11 puts both to [USER].
KURAGE_FUEL_MODE = "exhaust_any"
                              # v3's fuel: "Charge now builds at a rate of
                              # '1 Exhaust = 1 Charge'", on every Exhaust of
                              # one of her ORIGINAL cards -- her own AND
                              # original Companions. That is the SHIPPED
                              # funnel, unnarrowed, so v3 RETIRES v2's PICK A1
                              # ("exhaust_own", where a Companion paid
                              # nothing). "play_or_exhaust" (v2's A2) is still
                              # implemented so the arm can be swept.
KURAGE_POWER_PULSE = "charge" # [USER], v3: the pulse when the last card she
                              # played was a POWER grants CHARGE, not Hydro --
                              # "Sacrificing a power seems like a bigger deal
                              # than sacrificing anything else." The AMOUNT is
                              # DERIVED, not picked (R212's derived-not-picked
                              # limb): it is CHARGE_PER_EXHAUST, the Exhaust
                              # rate, i.e. a Power pulse is worth exactly one
                              # burnt card. "hydro" (v2's PICK C1) stays
                              # implemented as the alternative.
KURAGE_MEMORY_PULSE_BLOCK = 5 # the SKILL branch of the pulse, RULED at 5 by
                              # [USER] on 2026-08-29 as a separate constant.
                              # NOT KURAGE_PULSE_BLOCK, which ships at 0 since
                              # the v0.4 starter rework and must stay reachable
                              # byte-for-byte with the flag off. The Oath's
                              # `kurage_ward` still stacks on top.
KURAGE_EMPTY_QUEUE = "hold"   # an EMPTY memory fires nothing and pays
                              # nothing; the bank keeps growing. Distinct from
                              # a BLOCKED memory, which is v3's own clause:
                              # [USER], "Sticking a card you can't afford into
                              # Memory blocks Memory until it's played" --
                              # nothing behind an unaffordable front fires and
                              # the bank holds.
KURAGE_TARGET_RULE = "follow_her_last_attack"
                              # v3 leaves this constant governing the PULSE's
                              # aim only. The REPLAY's aim is v3's stored
                              # target plus KURAGE_MEMORY_TARGET_FALLBACK
                              # above, which supersedes v2's PICK E for the
                              # replay and for the replay alone. "random" is
                              # implemented for the pulse.
# NOT READ under the flag: KURAGE_DURATION and KURAGE_PULSE_PER_CHARGE (the
# summon is persistent and the pulse carries no Charge term), and
# KURAGE_THRESHOLD, which v3's per-card price replaces outright.
# v4 adds two more to that list, both RETIRED-UNDER-FLAG rather than deleted:
# KURAGE_DURATION is now unread on BOTH of the jellyfish's doors (the base-kit
# install reads nothing, and the Casket refresh maxes a 1 against a 1), and
# KURAGE_MEMORY_KEYWORD_NEEDS_SUMMON is unread in effect because the summon
# check it gates can no longer fail. Both keep their shipped values so that a
# flip of KURAGE_ALWAYS_ON restores the v3 arm without a re-authoring.
KURAGE_THRESHOLD = 5          # RETIRED BY v3, kept only so a revert to the v2
                              # arm is a flag flip rather than a re-authoring.
                              # Nothing reads it.

# --- Reference relics ---
BURNING_BLOOD_HEAL = 6        # REF_IRONCLAD: heal after each won fight
                              # (ruling 1: gives A4 a nonzero anchor)

# --- Combat-side potions (engine/potions.py; potion pass) ---
# Payload amounts and the bounded-greedy use-policy thresholds. Inert on the
# frozen battery: battery players carry no potions, so every path below is a
# dead branch (Player.potions empty -> engine/potions.py fast-guards out).
POTION_SLOTS = 3                  # StS default held-potion capacity
POTION_BELT_BONUS_SLOTS = 2       # Potion Belt relic: +2 slots on pickup
POTION_BLOCK = 12                 # block_potion: gain Block
POTION_FIRE_DAMAGE = 20           # fire_potion: unpowered damage to ONE enemy
POTION_BLOOD_HEAL_FRACTION = 0.20 # blood_potion: heal this fraction of max HP
POTION_STRENGTH = 2               # strength_potion: +Strength this combat
POTION_SWIFT_DRAW = 3             # swift_potion: draw N
POTION_WEAK = 3                   # weak_potion: Weak stacks to one enemy
POTION_FEAR_VULN = 3              # fear_potion: Vulnerable stacks to one enemy
POTION_ENERGY = 2                 # energy_potion: +Energy
POTION_FAIRY_REVIVE_FRACTION = 0.30   # fairy_in_a_bottle: revive at this
                                      # fraction of max HP on lethal damage
# Use-policy thresholds (bounded greedy heuristic, NOT a solver).
POTION_DEFENSIVE_MARGIN = 0       # drink a defensive potion when predicted
                                  # end-of-turn HP would be <= this
POTION_BIG_HIT_FRACTION = 0.35    # a telegraphed enemy attack this large a
                                  # fraction of max HP is "big" (weak/fear/str)

# --- Pilot policy (spec §6) ---
BLOCK_PANIC_THRESHOLD = 0.40  # prioritize block when incoming >= 40% of HP
# EB-5. The combat pilot's scoring WEIGHT SET has its own version stamp, same
# archive discipline as CONSTANTS_VERSION and DRAFTER_VERSION: two pilot
# numbers taken under different weight sets are not the same measurement, and
# until now the set had no name to put in a row.
#
# WHAT IT LABELS: every `PILOT_*` weight in the block below, plus the `STOKE_*`
# block in `tier0/pilot/policy.py` (which stays out of this file for the reason
# written at its head -- constants.py is the surface the C# parity gate
# compares by value, and a pilot heuristic has no C# counterpart). The stamp
# lives HERE, with the bulk of the set, on the DRAFTER_VERSION idiom: that
# stamp also sits in constants.py while most of what it labels lives in
# tier05/draft.py.
#
# WHAT IT IS NOT: this stamp does NOT enter the RT/D/P/C run-cell stamp
# (tier05/cells.py). It is an instrument version on the A6_INSTRUMENT_VERSION
# pattern -- a label for the weight set, read by whoever is comparing two pilot
# readings, not a fourth axis of the run cell. Adding it moved no value.
#
# v1 = the set as it has stood since the 2026-07-29 sim-hygiene sprint moved
# the first sixteen weights here, plus the EB-5 completion of the same move
# (the damage-estimator, scaling and charge weights below). MOVED, NOT RETUNED
# at both steps: every value is byte-identical to the literal it replaced.
# Bump when a weight's VALUE changes; a pure rename or regrouping does not.
#
# v2 = POLICY 7 (EB-17p §13.8, R176, 2026-08-11): `PILOT_COMPANION_COPY_VALUE`
# = 1.5 joins the set, filed in the policy.py half. Read honestly, the "bump
# when a VALUE changes" rule covers this -- a weight ENTERING the labeled set
# changes the set, and a Klee reading taken while the pilot scored
# `copy_companion_in_hand` at zero is not comparable with one taken after.
#
# v3 = POLICY 8 (EB-118 Phase 2A, 2026-08-24): `PILOT_POLICIES_ENABLED` flips
# to True and the eleven `BOMB_*` / `EXHAUST_*` weights of the bomb-placement
# and exhaust-selection policies ENTER the labeled set -- the same v2 reading
# of the rule, applied to a whole block instead of one weight. While the switch
# was off no weight in that block was ever read, so the labeled set was
# arithmetically unchanged and the stamp could not move first; the moment the
# switch is on, a Klee or Kokomi reading taken before it is not comparable with
# one taken after. Filed in `tier0/pilot/policy.py` rather than here for the
# C#-parity reason written at that block's head -- where a weight LIVES is not
# what decides which readings are comparable. NO VALUE MOVED at this bump: the
# eleven are byte-identical to the hand-picked numbers they landed with. W4's
# sweep of them (`tier05/pilot_weight_sweep.py`) is a separate act carrying its
# own bump, and it RAN inside this same window and adopted nothing -- 78 points,
# every one INSEPARABLE, so no such bump was owed and the hand-picked vector is
# what v3 labels.
#
# v4 = POLICY 9 (EB-118 Phase 2C, 2026-08-24): `MODE_CHOOSER_ENABLED` flips to
# True and `MODE_OVERDRAW_HP_VALUE` ENTERS the labeled set. The v2/v3 reading
# of the rule again, and it is the FILE'S OWN IDIOM rather than a judgement
# made here: the mode-valuation block's head says a value moving there is its
# own `PILOT_WEIGHTS_VERSION` bump, and v3 already established that a weight
# which was never READ while its switch was off cannot have moved the stamp
# earlier -- so the entry IS the event. NO VALUE MOVED: 1.0 is byte-identical
# to the hand-picked number it landed with, and W4's sweep was NOT run over it
# (R205 re-bodied the card instead, on the finding that the dominance was
# structural and these two weights are shared policy).
# `MODE_TIE_EPSILON` rides along and is NOT the ground: 1e-9 is a float-noise
# guard on the tie-break, not a valuation weight, and it cannot change an
# argmax that any weight decides. Naming it here is a completeness note, not a
# second reason. A Furina reading taken with the chooser off is not comparable
# with one taken after -- for `deep_breath` and, today, nothing else.
#
# v5 = POLICY 10 (EB-118 Phase-3 Window 3, R211, 2026-08-25):
# `EXHAUST_FORMULA_PAYOUT_WEIGHT = 1.0` ENTERS the labeled set, filed in
# `tier0/pilot/policy.py` for the C#-parity reason at that block's head. This
# one is NOT the v2/v3/v4 shape -- those were weights that existed and were
# never read while a switch was off, and the entry WAS the event. This is a
# genuinely NEW weight arriving with the behaviour that reads it: the chosen-
# Exhaust chooser's default payout hook stops being `identity_blind_payout`
# and becomes `formula_aware_payout`, which pays a candidate the marginal
# contribution it would make to the exhausting card's OWN printed selection
# formula -- multiplied by the living-enemy count when that formula's damage
# targets `all_enemies`. The value 1.0 is hand-picked and unswept, on
# `BOMB_LANDED_DAMAGE_VALUE`'s and `MODE_OVERDRAW_HP_VALUE`'s reasoning: the
# chooser's scale is already points of damage, and a point of payout and a
# point of forgone future value trade one for one.
# WHAT IT MAKES INCOMPARABLE is narrower than usual and worth saying, because
# a reader will otherwise assume every Kokomi reading archives: the hook
# returns 0.0 for any card that prints no selection formula, so it is
# BYTE-IDENTICAL to the old default on every carrier except the two W3 rows
# that print one (`pearl_barrage`, `the_tide_remembers`). That is asserted
# directly over every chosen-Exhaust carrier on every sheet rather than
# argued -- `test_eb118_policies.test_no_existing_carriers_pick_moved` -- and
# it is what replaces a fourth scratch run that would have been provably null.
# THE RARE-ROTATION TRADE IS THE COST AND R211 ACCEPTED IT, paired with
# retrieval (C19 (c)'s "Salvage the Line" loans a rotated Rare back out of the
# Exhaust pile). Any later change to the value is its own bump, and the sweep
# grid's outcomes are [USER]'s call, not the integration's.
#
# v6 = POLICY 11 (the scorer-literacy window, 2026-08-26):
# `SPARK_HOLD_VALUE_WEIGHT = 1.0` ENTERS the labeled set, filed in
# `tier0/pilot/policy.py` beside the other policy-side weights. Same shape as
# v5 and not the v2/v3/v4 shape: a genuinely NEW weight arriving with the
# behaviour that reads it, with no switch in front of it. It is the ONLY new
# weight in a four-item window -- `EB-144` values both Salon verbs off the
# resolver's own `salon_tick_amount` and `EB-145` prices a selection payout
# off the card's own printed `base`/`per`, so neither mints a dial, and
# `EB-129` pays event card-adds the realized Book of Five Rings heal. The
# value 1.0 is hand-picked and unswept on `EXHAUST_FORMULA_PAYOUT_WEIGHT`'s
# reasoning: the scale is points of damage on both sides of the subtraction,
# so a point of banked-Spark value and a point of payoff trade one for one.
# WHAT IT MAKES INCOMPARABLE: any reading of a deck holding one of the three
# `C19` Spark sinks (`powder_charge`, `hold_the_line`, `smoke_and_sparks`) --
# the only rows on any sheet that print `spend_spark`, so the term is gated
# on a printed price that is 0 everywhere else and nothing else pays even the
# lookup. At 0.0 the pilot is byte-identical to `P10`, pinned as a test
# rather than argued. A PLACEHOLDER rides at the constant and is [USER]'s at
# the next sheet pass: leg 1's EXISTENCE, i.e. whether a Spark has hold value
# with no reader in hand and the free-Attack threshold untouched. Legs 2 and
# 3 stand either way.
PILOT_WEIGHTS_VERSION = 6
# Sim-hygiene sprint 2026-07-29 (task 4): the inline scoring weights that had
# been living as bare floats inside tier0/pilot/policy.py. MOVED, NOT RETUNED
# -- every value below is byte-identical to the literal it replaced, and the
# move was verified behaviour-identical by a seeded 12-arm roster comparison
# (identical table before/after). They live here because this file is what a
# version stamp labels: a pilot weight that is only reachable by reading the
# function body cannot be swept, cannot be diffed against a prior world, and
# cannot be cited in a ruling. Their CALIBRATION history is unchanged and is
# still recorded at the call sites.
#
# Reaction term (_reaction_value). "Preserve the calibrated strategic scale:
# seeding=2, one trigger=6" -- the comment that has guarded these two numbers
# since the reaction pilot was calibrated.
PILOT_REACTION_TRIGGER_VALUE = 6.0   # per EXPECTED reaction this card causes
PILOT_REACTION_SEED_VALUE = 2.0      # capable card that triggers nothing yet
# Tempo term (_tempo_value).
PILOT_DRAW_WHILE_VALUE = 2.0         # one matching card + the stopper
PILOT_SPARK_VALUE = 0.7              # sparks -> free attacks
PILOT_BURST_DIVISOR = 10.0           # burst_energy is priced per burst point
# Sustain term (_sustain_value): Encore is deferred HP economy, worth most of
# its face because it keeps until used, discounted for not stopping THIS
# turn's hits when drawn late.
PILOT_ENCORE_VALUE = 0.8
# Spotlight term (_spotlight_value). The designate ladder is a SEQUENCING
# priority, not a value estimate -- 20.0 exists to make the selector fire
# BEFORE the companion in hand is played, which is why it dwarfs everything
# else in the function.
PILOT_SPOTLIGHT_DESIGNATE_SEQUENCING = 20.0  # companion waiting: light first
PILOT_SPOTLIGHT_DESIGNATE_GENERATOR = 0.1    # invite first, then designate
PILOT_SPOTLIGHT_DESIGNATE_OPENING = 4.0      # no designation yet
PILOT_SPOTLIGHT_DESIGNATE_REDESIGNATE = 0.3  # already lit; not dead, not urgent
PILOT_SPOTLIGHT_BOOST_COMBAT = 3.0   # combat-scoped mult/ovation boosts
PILOT_SPOTLIGHT_BOOST_TURN = 1.5     # turn-window boosts
PILOT_SPOTLIGHT_BOOST_EARLY = 0.3    # no stage yet: not dead, just early
PILOT_GUEST_STAR_VALUE = 2.5         # a card in hand, roughly
PILOT_SPOTLIGHT_COPY_VALUE = 3.5     # dead without a target, and it knows it
# Scaling term (_scaling_value): setup is worth less as the fight winds down.
# The taper hits zero at this turn number.
PILOT_SETUP_TAPER_TURNS = 12.0
# --- EB-5 completion. The weights the 2026-07-29 move left inline, moved on
# the same terms: MOVED, NOT RETUNED, every value byte-identical to the
# literal it replaced, and their calibration notes stay at the call sites.
# Scaling term (_scaling_value), the rest of it. The self-buff cap and its
# per-stack price are the pair `test_pin_tier0_pilot` pins: percent-stack
# powers (Vermillion Pact 25, Durin 30) would otherwise dwarf everything.
PILOT_SELF_POWER_STACK_CAP = 6       # per-power stacks counted, at most
PILOT_SELF_POWER_VALUE = 3           # per counted stack of a SELF power
PILOT_ENEMY_DEBUFF_VALUE = 2         # per stack of an ENEMY debuff
# Damage-estimator terms (_expected_damage). Self-damage is a COST, and the
# two futurity discounts price damage that arrives over the coming turns
# (the Burst payoff and the Kurage's pulses) rather than this turn.
PILOT_SELF_DAMAGE_COST_WEIGHT = 0.5
PILOT_FUTURE_DAMAGE_DISCOUNT = 0.8
# Charge term (_charge_value), Kokomi's engine machinery. Values only the
# MACHINERY; the payoff damage already flows through _expected_damage.
PILOT_CHARGE_GAIN_VALUE = 0.6        # per point of banked Charge
PILOT_CONSCRIPT_CREATE_VALUE = 3.0   # create mode NETS a card
PILOT_CONSCRIPT_TRANSFORM_VALUE = 2.0    # transform mode pays one
PILOT_EXHAUST_ALL_ESTIMATE = 3       # "all" (Stoke grammar) is worth ~3 cards
PILOT_DELIBERATE_EXHAUST_VALUE = 0.8     # Charge + thinning, casket on
PILOT_SELF_MILL_VALUE = 0.5          # self-mill is fuel, not just loss
PILOT_GARMENT_CHARGE_VALUE = 1.2     # per turn per banked-Charge read
PILOT_GARMENT_BASE_VALUE = 2.0       # the garment itself
# PILOT_REGRET_SAMPLE_RATE: DELETED by R67 (2026-07-26). Zero readers, and
# actively misleading while it existed -- pilot/policy._log_regret fires on
# EVERY play, so every regret rate this repo has ever reported is a full
# census. Anyone who found the constant and rescaled a regret number by 0.01
# to "correct for sampling" would have been wrong by two orders of magnitude.

# --- Degeneracy detectors (spec §8) ---
RUNAWAY_SCALING_RATIO = 8.0   # DPT turn 10 > 8x DPT turn 3 -> SUPERLINEAR
AMP_STACK_LIMIT = 4.0         # single hit > 4x base damage -> log provenance

# --- Harness defaults ---
DEFAULT_FIGHTS_PER_ENCOUNTER = 1000
DEFAULT_SEED = 20260719
WINRATE_BAND_MIN_FIGHTS = 1000    # ratification process fix: winrate band
                                  # checks only run at >=1000 fights

# --- Tier 0.5 run model (tier05-draft-sim-spec.md §2; run-model rework) ---
# Fixed node template, no pathing choice (map design is theirs, not ours).
# RUNTEMPLATE_VERSION 3 (run-model rework §3.1, RATIFIED 2026-07-21): a
# realistic-ish Act 1 gauntlet. 11 nodes, 7 fights (4 normal + 2 elite +
# 1 boss), 2 rests, 1 treasure (T), 1 shop ($). The burst-check NODE is
# DROPPED (it was an A6 instrument, not a fight; the burst_check BATTERY
# encounter file stays frozen for test_klee). New node kinds T (treasure:
# gold + relic stub) and $ (shop: gold spend, stub this phase).
#
#   RATIFIED:  N N N R E T N $ E R B          (11 nodes, 7 fights)
#
# The first R sits BEFORE the first E (§3.1 red-pen): you never path to an
# early elite without a chance to heal/smith first. The second R guards the
# boss. Both elites and the boss are reachable off a rest.
#
# v4 (multi-act extension §10, RATIFIED 2026-07-23): the TEMPLATE STRING is
# unchanged, but the run is now the template repeated once PER REGISTERED ACT
# (RUN_ACTS below), with an act-boundary event between acts (forced-Rare
# companion slot + Ancient full-heal/relic pick) and the act BOSS drawn from
# a per-act boss POOL (>= 2, §10.0 ruling -- including Act 1). The boss-pool
# draw consumes a run-rng call, so v4 runs are NOT seed-comparable to v3
# EVEN at --acts 1. All v3 run-layer numbers are archived; never compare
# across template versions unlabeled.
# v5 (Ironclad-0.6% diagnosis, 2026-07-23): the act-boundary CARD offers are
#      forced Rare -- §10.1's ratified "choice-of-3 Rares" boss drop, which v4
#      shipped as a forced-Rare COMPANION slot only (a no-companion character
#      got plain commons at the boundary). Boundary screens skip the rarity
#      rolls, so v5 runs are not seed-comparable to v4 past the first boss.
# v4 = template repeated per registered act, boss pools, boundary event with
#      the forced-Rare companion slot only. §10.8's shipped sanity numbers
#      are v4; the boss-pool draw already broke v3 comparability at --acts 1.
# v3 = same "NNNRETN$ERB" string, single act, single fixed boss (Vantom):
#      the relic/potion-layer + calibration archive world.
# v2 = "NNNENRNNENRNRB" (11 fights, 3 rests incl. guaranteed pre-boss): the
#      archive world of the Furina sprint-1 and Klee pass-4 reports.
# v1 = "NNNENRNNENRNB"  (11 fights, 2 rests): the M5-M8 archive world.
# v6 (§11, 2026-07-24): THE TEMPLATE IS GONE. Each act generates a real
#      16-floor StS2 map (tier05/maps.py) and a route policy walks it, so node
#      composition is emergent and the run has agency. Unknown rooms resolve at
#      entry, 55% of them into events (tier05/events.py). Every archived
#      run-layer number is uncomparable across this boundary -- the same
#      discipline as v4->v5, but total rather than partial.
# v7 (§11.2, 2026-07-25): acts 2-3 get event pools (they shipped EMPTY in v6 --
#      an Unknown that rolled `event` in the Hive or Glory found nothing and
#      passed), and the event option valuation is corrected in two ways that
#      move act-1 runs too: GOLD_PER_HP was contradicting its own derivation by
#      ~2x, and escalating ladders are now valued THROUGH the escalation rather
#      than at face value (a myopic policy never climbed one, so every ladder
#      past its first rung was unreachable content). v6 event numbers do not
#      carry across.
# v8 (2026-08-07 sitting): two run-layer behaviour changes in one window.
#      (a) R125 widened the R121 tag shield to the run layer's two readers --
#      the rest-site smith and the event upgrade now read tags through
#      `draft.behavioural_archetypes`, so the reference anchor's
#      instrumentation tags no longer steer them (EB-46 measured the open
#      channels at +2.17 pp; the anchor returns to its untagged 11.13%
#      world). (b) R126 priced the Orobas hooks (each variant totals 13), so
#      the Ancient pick now takes the character's own upgraded starter --
#      acquisition that v7 realistic runs never had. DRAFTER_VERSION stays 14
#      on the R121 restores-not-redefines argument; the payoff-reach pin is
#      untouched.
# v9 (EB-30m): the Darv/Dusty Tome act-2 event -- the single Ancient
#      acquisition door, grants upgraded; act-2 event-pool odds move for
#      every character.
# v10 (R82 reopened, [USER] 2026-08-10, M7): the enchant events. Five events
#      built on Enchant join the pools -- Sapphire Seed (act 1), Field of
#      Man-Sized Holes / Stone of All Time / Symbiote (act 2; Symbiote also
#      act 3), Self-Help Book (all acts) -- so the event-pool odds move in
#      every act for every character, the same way the single act-2 addition
#      moved them at v9. Enchantments themselves are post-draft only: the
#      drafter is not taught about them, so DRAFTER_VERSION and
#      draft.POLICY_VERSION are both untouched and the payoff-reach pin
#      stands. v9 event numbers do not carry across.
# v11 (the coordinated 2026-08-13 window: EB-82 + EB-85). Two run-layer
#      changes, batched into ONE bump because both are RUNTEMPLATE content
#      and neither was quotable alone -- M14 enumerates this window and asked
#      for exactly one coordinated bump at the end of it.
#      (a) EB-82, the Grave of the Forgotten conversion. The event joins the
#      ACT-3 pool (2 own -> 3 own), so act-3 event odds move for every
#      character the same way v9's single act-2 addition moved act 2; its
#      Accept branch grants `forgotten_soul`, an EVENT relic no reward, Neow
#      or Ancient roll can reach, which arms the `damage_per_exhaust` hook
#      mid-run and puts damage into every later fight of that run.
#      (b) EB-85, five places where tier0 modelled an enchantment differently
#      from the class sts2.dll v0.107.1 ships, each re-verified against the
#      binary before it was touched. THREE move what an enchant event may
#      TARGET -- Nimble gates on GainsBlock rather than type == "skill", so
#      Block-granting Attacks are legal; Swift has no type override at all,
#      so Self-Help Book's third reading is live on Klee's printed starter
#      after being locked for all of v10; and Nimble never rides
#      block_next_turn, whose payout passes no card source. TWO move what one
#      PAYS -- the Nimble rider is collected on EVERY Block gain rather than
#      once per card play, and Perfect Fit refuses the opening shuffle
#      instead of acting as a free Innate.
#      Enchantments remain post-draft only and no drafter or pilot code
#      moved, so DRAFTER_VERSION and draft.POLICY_VERSION are both untouched
#      and the payoff-reach D14 pin stands. CONSTANTS_VERSION did not move
#      either: the window's other two branches (EB-70, EB-83) wrote no code.
#      No v10 enchant number and no v10 act-3 number carries across.
# v12 (window 2 of the 2026-08-13 correctness batch, EB-104). FIVE run-layer
#      behaviour changes, batched into ONE bump for the same reason v8 batched
#      two: they are all RUNTEMPLATE content, they landed in one window, and
#      none of them was quotable alone. Every one is a defect fix against a
#      named authority or against the run layer's own declared grammar -- none
#      is a tuning choice.
#      (a) EB-102, RunContext.resolve_shop now receives the run's Featured
#      Banner. The banner filter existed and the only production visit_shop
#      call never passed it, so the shop could offer a 5-star the banner had
#      excluded from every reward screen. It changes which card rng.choice
#      lands on, so every §4.7 shop-channel figure taken under C9 renumbers.
#      (b) EB-103, potion capacity is derived from held relics on read instead
#      of re-stamped at three sites, so a Potion Belt acquired since the last
#      refresh is visible to resolve_event and its grant is no longer dropped
#      unlogged.
#      (c) EB-110, the rest-site heal FLOORS where it rounded. The authority
#      lands the 30% through SetCurrentHpInternal, whose body truncates; Klee
#      healed 19 where the game heals 18. Measured at 2.39 HP/run of
#      one-directional sim-generous bias over 120 three-act runs.
#      (d) EB-111, Book of Five Rings counts event deck-adds. The relic's
#      sheet row is unconditional and only two of ~10 add sites were wired;
#      88 uncounted adds across 64 book-holding runs in 300, ~5 HP/run of
#      missing healing in the configuration the exp_* scripts run.
#      (e) EB-112, event card-reward screens roll rarity through RARITY_ODDS
#      like any other reward screen. The grammar declares card_reward as "an
#      ordinary reward screen" and it was drawing uniformly from the flattened
#      pool -- 20.0% Rare per offer against 5.0%, on three shipped options in
#      acts 1 and 2 for every character. RARITY_ODDS itself is UNMOVED; only
#      the site that failed to consult it moved.
#      No drafter or pilot code moved, so DRAFTER_VERSION and
#      draft.POLICY_VERSION are both untouched and the payoff-reach D14 pin
#      stands. CONSTANTS_VERSION moves in the SAME window on its own ground
#      (the tier0 engine half of EB-104) -- see the C10 entry below; the two
#      fields move once each, together, at the end of the window.
#      No v11 run-layer number carries across.
RUNTEMPLATE_VERSION = 12
# DEAD as of v6; kept as the name of the world every pre-§11 measurement was
# taken in, and still used by tests that pin a node sequence deliberately.
RUN_NODE_TEMPLATE = "NNNRETN$ERB"

# The act registry (§10.1): one spec per act -- pool file (tier05/content/)
# + how many N fights draw the easy pool (Act 1: 3, Acts 2-3: 2, the real
# StS2 rule). The run model spans ALL registered acts by default; acts 2-3
# land in §10 Passes 2-3 by appending specs here.
RUN_ACTS = (
    {"id": "act1", "pool": "act1_pool.yaml", "easy_fights": 3},
    {"id": "act2", "pool": "act2_pool.yaml", "easy_fights": 2},  # the Hive
    {"id": "act3", "pool": "act3_pool.yaml", "easy_fights": 2},  # Glory
)

# --- Act maps (§11, 2026-07-24): the real StS2 17-floor DAG --------------
# Research + sources: docs/archive/sts2-map-and-events-research.md §1. These replace
# RUN_NODE_TEMPLATE, which authored a fixed 11-node spine with 2 forced elites
# and zero Unknown rooms. WIKI-REAL at Ascension 0 unless marked OPEN.
# 16 walkable floors, 0-based. The wiki counts 17 because floor 17 is the
# boss CHEST, which is not on the map and is folded into the boss reward here
# rather than modeled as a room. So wiki floor N == index N-1 throughout.
MAP_FLOORS = 16
MAP_TREASURE_FLOOR = 8        # wiki floor 9: all rooms are Treasure
MAP_REST_FLOOR = 14           # wiki floor 15: all rooms are Rest Sites
MAP_BOSS_FLOOR = 15           # wiki floor 16: every route converges here
# That leaves 12 freely-typed floors (wiki 2-8 and 10-14), which is what the
# expected-composition arithmetic in the research doc is computed over.
MAP_MAX_EDGES = 3             # "1-3 paths exiting to the floor above"
# Room-type odds for every non-fixed room. WIKI-REAL. Elite frequency is NOT
# a tuning dial: the count a run FIGHTS is a routing outcome (target median
# ~2.5, range 1-4 -- §1.3), and moving 8% to hit a winrate would be exactly
# the difficulty-dial mistake this branch already made once.
MAP_ROOM_ODDS = (("N", 0.53), ("?", 0.22), ("R", 0.12), ("E", 0.08),
                 ("$", 0.05))
# The map is built by CARVING MAP_PATHS routes bottom-to-top (maps.generate);
# floor width and the 1-3 edge fan-out are emergent, not rolled. Six columns
# is the wiki's "up to six map locations on each floor"; MAP_PATHS is the
# OPEN NUMBER (§5.3) and it is what gets calibrated against the elite target
# (median ~2.5 fought, range 1-4 -- research §1.3), because path count sets
# how CONNECTED the map is and connectivity is what binds. Do not calibrate
# MAP_ROOM_ODDS against a winrate.
MAP_MAX_FLOOR_WIDTH = 6
MAP_PATHS = 6
# OPEN NUMBER (§5.1): Unknown rooms resolve at ENTRY with a pity table -- the
# chosen kind resets to baseline, the others increment. The RULE is wiki-real;
# the baselines and increments are not published anywhere and these are a
# defensible stand-in, stamped rather than smuggled. Event-dominant matches
# the play experience (most Unknowns are events); Treasure is the rare one.
MAP_UNKNOWN_BASE = {"event": 0.55, "N": 0.20, "$": 0.15, "T": 0.10}
MAP_UNKNOWN_STEP = {"event": 0.10, "N": 0.05, "$": 0.05, "T": 0.05}

# --- Tier 0.5 economy (run-model rework §5; defaults RATIFIED §8) ---
GOLD_START = 99                  # StS default starting gold
# Boss pays 100 (§10.1, RATIFIED 2026-07-23: the real StS2 act-transition
# drop -- resolves §5's open boss number; was 40). Only ever SPENDABLE on
# multi-act runs (a final boss ends the run), but it lands in the reported
# run gold at every act count.
GOLD_INCOME = {"N": 10, "E": 25, "B": 100}  # per WON fight, by node tier
TREASURE_GOLD = 40               # T node lump (relic slot is a stub)
# Shop ($): offers SHOP_CARD_OFFERS cards from the character's OWN draft pool
# (rewards.character_pool, ownership-required, companion-free) plus one card
# removal. Buy policy REUSES the draft policy's valuation (§5). Prices below
# are the ratified defaults (§8).
SHOP_CARD_PRICE = 60             # §5: card ~60
SHOP_REMOVAL_PRICE = 75          # §5: removal ~75 base
SHOP_REMOVAL_PRICE_STEP = 25     # §5: "rising per use" -- +25 each removal
#                                  bought across the run (StS-real). OPEN
#                                  NUMBER (§8 ratifies base ~75, not the step);
#                                  only bites once multi-act adds a 2nd shop.
SHOP_CARD_OFFERS = 3             # "a few cards" (§5). OPEN NUMBER -- §8 does
#                                  not fix a count; 3 mirrors REWARD_CARD_OFFERS.
# --- §4.7 companion channel (R59/R61, respecified by R116/NC-10, slot-2
# --- floor RESTORED by [USER] 2026-08-10) ---------------------------------
# The shop's TWO colorless slots carry companions.
#
# WHERE THE SLOTS STAND TODAY. Slot 1 = home region, Uncommon-or-higher.
# Slot 2 = any nation, Uncommon-or-higher. The NATION is what separates the
# slots; the RARITY FLOOR is common to both.
#
# HISTORY, kept because it is the reasoning that moved. R59 read the floor as
# covering both slots, on the argument that a wildcard at full reward odds
# (~60% Common) makes this shop worse than base's guaranteed-Rare slot 2.
# R116/NC-10 respecified slot 2 as "any companion card" -- no nation, no
# floor -- and Commons became drawable at the 50-gold band. [USER] closed
# that out on 2026-08-10 (S4-G10 agenda item "should slot 2 carry a rarity
# floor at all?") by RESTORING the floor per R59's original rationale: the
# paid premium channel is not a place to sell Commons. Slot 2 therefore reads
# SHOP_COMPANION_RARITY_ODDS again, exactly as it did before R116.
# This changes the shop world in both engines -> CONSTANTS_VERSION 8 -> 9.
SHOP_COMPANION_SLOTS = 2
# BOTH SLOTS' odds: RARITY_ODDS CONDITIONED on >= Uncommon, i.e. renormalized
# over the rarities that survive the floor -- 0.35/0.40 and 0.05/0.40. That
# is the only reading of "Uncommon or higher" that introduces no new number,
# and the values below are unchanged from when the floor covered both slots
# the first time.
#
# THE ALTERNATIVE READING, surfaced and NOT chosen (R116 required this
# explicitly: "a renormalization chosen by an implementer is a balance value
# chosen by an implementer"): the floor could instead carry its own STATED
# SPLIT, a fresh pair of odds designed for the premium slot rather than
# inherited from the reward table. That is a balance decision with a
# defensible case -- slot 1 is the "buy your dream support" slot and 12.5%
# Rare may be the wrong price for it -- and it is a [USER] call, not this
# one. Nothing below was tuned; conditioning was applied and the result is
# the identity on the existing values.
# RESOLVED BY Q16, 2026-08-06 (R117 rider, answered R118, verbatim
# "Condition."): [USER] chose the CONDITION reading -- the odds below ARE
# RARITY_ODDS renormalized over the >=Uncommon pool, exactly as shipped.
# The stated-split alternative above was declined; a fresh split would be
# its own row in its own window. No value changed by the ruling: the
# conditioning was already the identity on these numbers.
SHOP_COMPANION_RARITY_ODDS = {"uncommon": 0.875, "rare": 0.125}
# SLOT 2 reads THIS SAME TABLE ([USER] 2026-08-10). Between R116 and that
# ruling it read RARITY_ODDS itself, unconditioned, and could offer a Common
# at the Common band; the floor's restoration puts both slots back on one
# table. There is still no second constant -- the two slots differ by NATION
# only, and one table is what makes that visible.
# Priced by DRAWN RARITY (§4.7: gold is the balance governor, not a stat nerf).
# These are the REAL StS2 shop bands, read off MerchantCardEntry.GetCost, so
# the sim and the mod charge the same gold for the same companion. They are
# deliberately NOT the flat SHOP_CARD_PRICE above: a channel whose whole
# balance story is its price cannot be measured against a flat price.
#
# KNOWN DIVERGENCE, recorded not fixed: base GetCost multiplies by 1.15 when
# `card.Pool is ColorlessCardPool`, and companions do not resolve to that pool
# (see klee-mod CompanionPool), so neither side charges the colorless
# surcharge. Both sides agree; both are ~15% under base's premium channel.
#
# The COMMON band (50) joined the table under R116/NC-10, which opened slot 2
# to any companion card and therefore to Commons. It is READ OFF THE SAME
# METHOD as the other two, not invented: `MerchantCardEntry.GetCost`'s IL
# carries `ldc.i4 150`, `ldc.i4.s 75`, `ldc.i4.s 50` and the 1.15 colorless
# multiplier, in that order. Same provenance, same paragraph, no new number.
# INERT since the floor was restored ([USER] 2026-08-10): with both slots on
# SHOP_COMPANION_RARITY_ODDS no shop draw can be a Common, so nothing indexes
# this entry today. It is KEPT rather than deleted because it is a fact about
# `GetCost`, not a choice of ours -- deleting it would mean re-reading the IL
# to bring the band back, and both engines still price by drawn rarity.
SHOP_COMPANION_PRICE = {"common": 50, "uncommon": 75, "rare": 150}
# W2 relic granting cadence: shops stock 1-2 Common-pool relics for sale at
# this price. NEW economy number (relics were a stub before W2); auto-take-all
# policy buys an offered relic iff gold allows (relics are near-strictly-good).
SHOP_RELIC_PRICE = 150

# --- Tier 0.5 potion run-layer economy (potion pass; gated on grant_potions).
# Inert when grant_potions=False -- a run that never grants potions never reads
# these, so the pre-potion model is byte-identical. Drops land after WON
# normal/elite fights; the shop stocks 1-2 potions at POTION_PRICE.
POTION_DROP_CHANCE = 0.40        # chance of a potion drop after a won N/E fight
POTION_PRICE = 50                # shop price per potion ($ node auto-buy)

# NORMAL_ATTRITION_SCALE: DELETED by R67 (2026-07-26). It was written as the
# second knob of the R7 2D rest-economy sweep -- scale enemy ATTACK in plain
# normal-pool fights to test whether "95% of rest arrivals are under danger"
# was a template artifact -- but nothing ever applied it, so the second axis
# of that sweep was flat by construction. The finding it was meant to probe
# is untested, not disproved; re-opening it means wiring a scalar first.
REST_HEAL_FRACTION = 0.30         # rest option A: heal 30% of max HP
REST_HEAL_THRESHOLD = 0.65        # rest policy: heal below this HP
# M7: below DANGER always heal; between DANGER and HEAL_THRESHOLD an
# on-plan smith outranks the heal (the classic rest-vs-smith call). At
# 0.65 the heal branch swallowed every rest of a bruised run and the
# third option was dead by construction -- measured: 0 upgrades in 30
# demolition runs.
REST_SMITH_DANGER = 0.40
# DRAFTER_VERSION 5 (b): when the NEXT node is an Elite/Boss fight, the
# heal outranks the smith below this line -- the human "top up before the
# big fight" lookahead. Both template rests sit directly before E/B, so
# under v4 runs walked into guaranteed elites at ~48/80 HP (§10.8.1).
REST_PREFIGHT_HEAL_THRESHOLD = 0.90
# PUNISHER_LITE_SCALE / ATTRITION_LITE_HP / NORMAL_POOL_WEIGHTS: DELETED by
# R67 (2026-07-26). They described a weighted "lite" normal-encounter pool
# (a 70%-statline punisher and a single 45 HP attrition unit alongside swarm)
# that no code ever built -- tier05 draws its normal fights from the real
# battery statlines. The three read as a live encounter-pool spec while
# specifying nothing; rebuilding a lite pool means designing it again, not
# uncommenting these.

# PROGRESSION_GAP_COMPENSATOR: DELETED by R67 (2026-07-26). Applied by NOTHING
# since the real-statline roster swap -- tier05/model.py deliberately does not
# read it (see its note at :86), and its last reference died with
# tools/archive/roster_scale_gap.py. Historical record, since the constant was
# nominally FROZEN and is cited in DECISIONS §57 / triage ruling 3b: it was ONE
# number per node-tier standing in for the missing upgrades+relics power growth
# -- NOT a model of them -- grid-searched on the REF_IRONCLAD anchor only until
# anchor run completion hit 45%+-10, then frozen at {normal 1.0, elite 0.8,
# boss 0.7} on 2026-07-19 with anchor completion 47.9% at 1000 runs. The
# FROZEN status is preserved as a record; the object it froze is gone.

# --- Tier 0.5 rewards (spec §3 — the thing under test) ---
REWARD_CARD_OFFERS = 3
RARITY_ODDS = {"common": 0.60, "uncommon": 0.35, "rare": 0.05}
# The other half of the rarity vocabulary: every rarity that is REACHED
# rather than offered. Absence from RARITY_ODDS is what makes a card
# invisible to draft, reward and shop generation -- that absence is the
# mechanism, not a gap, and it is how `event`, `curse` and now `ancient`
# (R127 / EB-30m) all stay out of every pool without one filter naming them.
#
# The PAIR of tables is the point. Membership in NEITHER is a typo, and a
# typo'd rarity disappears from every pool silently with every gate green --
# so tier0/tests/test_eb30m_ancients.py asserts that every rarity in the card
# index is in one table or the other. This set gives the intentional half of
# that vocabulary somewhere to be declared, which is what turns a silent
# vanishing into a loud one.
ACQUISITION_ONLY_RARITIES = frozenset({"basic", "token", "status", "curse",
                                       "event", "ancient"})
# §4.1 made real (Furina kickoff §10, sprint 1): the companion reward slot
# concentrates SAME_NATION_REWARD_SHARE of its weight on the run
# character's own nation; the remainder spreads across ALL nations
# (relative cross-nation weights in NATION_WEIGHTS -- all 1.0 today).
# A single-nation world reduces exactly to the old uniform pick, so every
# archived pre-Fontaine number is unchanged by the mechanism itself; what
# changed the world is the Fontaine sheet loading (12 new 4-star cards).
SAME_NATION_REWARD_SHARE = 0.5
NATION_WEIGHTS = {"mondstadt": 1.0, "fontaine": 1.0, "inazuma": 1.0}

# principles v1.8 / draft-sim addendum: the Featured Banner. Each run rolls
# this many limited 5-stars per nation from the full designed roster, and only
# featured 5-stars appear in that run's companion offers. Rotation moves from
# authoring time (which someone must remember) to runtime (which the seed
# remembers), so the 5-star roster per nation can grow without a cap.
# DEGENERATE AT v0.1: Mondstadt has exactly 3 designed 5-stars, so the roll
# features all of them and current numbers are unaffected. This is plumbing.
BANNER_FEATURED_SLOTS = 3

# --- Tier 0.5 assigned draft policy (spec §4) ---
# CONSTANTS_VERSION 2 (morning-triage ruling 3.1). v1 measurements (M5/M6
# reports) were taken at DRAFT_SKIP_THRESHOLD = 1.0 and stay in those
# documents as the archived snapshot; every currently-load-bearing
# comparison is re-run under v2 in the M7 report. Do not compare a v1
# number against a v2 number without saying so.
# CONSTANTS_VERSION 3 ("The Tide Turns", F-A7): Fanfare stops being a
# spendable currency and becomes a read-only momentum stat -- decay, floors,
# no spend grammar, cap demoted to a safety rail. This changes a RESOURCE'S
# GRAMMAR, so every Furina number measured under v2 is archive: her decks
# generated a pool they could cash, and no v2 cell is comparable with v3
# output. Klee / Kokomi / ref_ironclad carry no Fanfare and do not move.
# CONSTANTS_VERSION 4 (R73, Neap Tide v2.1): KURAGE_PULSE_PER_CHARGE
# 4 -> 3 (ruled 2; E1 fired the pre-committed x3 fallback).
# Her pulse is read off an uncapped, never-spent bank (R80), so the multiplier
# is the whole slope of her damage curve -- every Kokomi number taken at x4 is
# archive, not a cheaper sample of the same world. Same rule the v2 bump
# applied to a single threshold: the size of the edit is not what decides,
# comparability is.
# WRITE THE LANDED VALUE, NOT THE RULED ONE (addendum A1c, 2026-07-26). This
# line read "4 -> 2" for the length of the sprint, because it was written when
# R73 was ruled and never revisited when E1 graded P6 and the fallback fired.
# x2 shipped in no build and no measurement cell; a version comment naming it
# files every current Kokomi number in a world that never existed, which is the
# exact failure the stamp exists to prevent. If a knob has a pre-committed
# fallback, this comment is not final until the fallback is graded.
# Klee / Furina / ref_ironclad carry no Charge and do not move.
# CONSTANTS_VERSION 5 (R110 / S-1, the X3 erratum; APPROVED by [USER]
# 2026-08-06 in reply to the Second Wind open one-liner (3)): Encore
# Performance loses its `{op: energy}` refund and its printed cost goes 1 -> 0
# (`docs/furina-cards.yaml`, regenerated `EncorePerformance.cs`).
# This is not a knob but it lands under the same comparability criterion the
# v2 bump wrote down, and the v4 note restated: the size of the edit is not
# what decides, comparability is. A Furina RARE changed cost AND stopped
# returning energy, so every drafted Furina deck that could ever have been
# offered the card prices its turns differently -- her whole energy curve, not
# one cell. **Every Furina tier-0.5 number measured under v4 or earlier is
# archive, not a cheaper sample of the same world.** The re-baseline is a
# COMPUTE decision for the next measurement sprint, not a debt this bump pays;
# archived numbers are bannered where they are published, never rewritten
# (R101b).
# Klee / Kokomi / ref_ironclad / real_ironclad / real_silent draft no Furina
# card and do not move. DRAFTER_VERSION and RUNTEMPLATE correctly do NOT bump:
# no offer-time price and no map/route shape changed.
# CONSTANTS_VERSION 6 (R117/Q14, verbatim "14) Yes"; wave 8, 2026-08-06):
# "Frozen unified + alpha boss-room scope + shop-slot spec" as ONE batch
# boundary. Contents: (a) NC-7 Frozen unified (Errata Batch 2, db3318e) --
# the sim adopted the mod's DURATION COUNTER (end-of-enemy-side tick,
# stacking extends, Shatter clears the counter); (b) the alpha boss-room
# scope (R117/Q13, verbatim "I'd say A") -- in a boss ROOM only
# minion-flagged creatures freeze, every other creature takes the
# Vulnerable substitution, which deliberately overrides R116's stated
# Kaiser-Crab-second-claw consequence; (c) the NC-10 shop-slot spec
# (Errata Batch 2, both engines) with Q16's CONDITION reading (R118,
# verbatim "Condition.") -- SHOP_COMPANION_RARITY_ODDS renormalizes over
# the >=Uncommon pool, a conditioning change with NO new values.
# Frozen appears across the roster's fights, so (a)+(b) archive EVERY
# pre-batch combat number for EVERY character -- not one kit's curve this
# time; (c) archives the tier-0.5 shop maths in both engines. Archive
# banners go where the numbers are published, nothing rewritten (R101b).
# DRAFTER_VERSION and RUNTEMPLATE correctly do NOT bump: no offer-time
# price and no map/route shape changed.
# CONSTANTS_VERSION 7 (R128, 2026-08-07 sitting: EB-29q ruled PROMOTE --
# "aim to make the sims realistic when possible - let's try to close the
# mechanics gaps"). Test Subject's three §10.9 approximations become the
# real mechanics: Enrage 2 at setup for the whole fight (every Skill played
# feeds permanent Strength, carried across revives), Painful Stabs 1 on the
# 200 bar (a Wound per unblocked HIT), and Nemesis on the 300 bar
# (Intangible 1 toggled per acting enemy turn, capping damage at
# INTANGIBLE_DAMAGE_CAP per hit -- now enforced at the direct-HP sites too:
# shatter, splashes, unpowered/unblockable helpers; unblockable was never
# uncappable). Multi-Claw's per-use growth becomes the real gains-a-hit
# shape (times_ramp_per_use). Every archived test_subject number -- 12.2%
# anchor, the EB-29q instrument set -- is C6-world archive; the C7 re-read
# lands with this bump. Other encounters do not carry these powers and do
# not move, EXCEPT any fight where a raw-damage site now caps -- no enemy
# outside Test Subject P3 ever holds Intangible, so none today.
# R131 (2026-08-07, closes EB-29s): the C7-world ~0% full-HP read on
# test_subject is an ACCEPTED OUTLIER -- working as intended, the pilot is
# worse than a real player; any quoted test_subject winrate carries this
# caveat. Ruling: `git show 41319eb`.
# CONSTANTS_VERSION 8 (EB-30m, R127): charge_per_turn / encore_per_turn
# income powers, income pinned before Salon upkeep (EB-2's parity target).
# Latent at the bump -- no encounter or ratified deck carries the powers;
# cells move only through the Ancient door.
# CONSTANTS_VERSION 9 ([USER] 2026-08-10, S4-G10 close-out): the shop's
# SLOT-2 RARITY FLOOR IS RESTORED -- slot 2 rolls SHOP_COMPANION_RARITY_ODDS
# (Uncommon-or-better) again instead of RARITY_ODDS, in BOTH engines
# (`tier05/shop.py`, `klee-mod/.../MerchantCompanionSlots.cs`), per R59's
# original rationale. Commons leave the paid channel entirely: the 50-gold
# band is now unreachable and the shop's cheapest companion is 75.
# Bumped on the CONSTANTS 5 criterion ("comparability decides, not edit
# size"): a shelf that stops offering ~60%-Common wildcards changes what a
# purse buys at every visit, so every §4.7 shop number measured under C6-C8
# -- the whole SHOP-P1/P2/P3 cell included -- is archive, not a cheaper
# sample of this world. Archive banners go where the numbers are published;
# nothing is rewritten (R101b).
# Landing WITH the bump, deliberately, so the re-run is one window and not
# two: the `exp_shop_companion_channel` instrument fixes (per-visit purchase
# attribution, true slot-2 purchase rarity, gold/affordability/crowd-out
# logging). An instrument fix moves no world, but it lands inside C9's
# boundary so the corrected cell has exactly one world to cite.
# FURTHER ERRATA MAY JOIN C9 while it is open: until a number is published
# under this stamp, an erratum that lands here widens this entry rather than
# opening C10.
#
# ERRATUM JOINED 2026-08-10 under exactly that clause -- no number has been
# published under C9, so this widens rather than opening C10. THE X7 + X8
# RARITY PROMOTIONS (R161, R162): `friendly_visit`, `chain_fuse` and
# `careful_arrangement` all move Common -> Uncommon in `docs/klee-cards.yaml`.
# Costs, amounts, tags and text are unchanged on all three; only the band
# they are drafted at moves. `skip_and_hop`, `sparkly_treasure` and `crackle`
# were ruled to STAY Common, and `lynette_box_trick` was deliberately left
# alone (watch item W5 in STATE) -- those are rulings, not deferrals.
# Why this belongs in the constants stamp at all: card-sheet rarity sits
# outside `RT/D/P/C`, so a rarity edit moves the drafted world with no
# version signal of its own (that gap is QUEUE M15, unratified). Batching it
# here gives it one. Two downstream effects follow mechanically and are NOT
# separate decisions: Klee's pool reads 29 Common / 28 Uncommon (was 32/25,
# total unchanged at 76), and `secret_stash`, whose add-pool is derived as
# "demolition Commons", stops offering `chain_fuse` and `careful_arrangement`.
# EB-17p supplies the measured warrant for the friendly_visit half: it graded
# PREDICTED-strong (+3.04 / +4.46) on the forced-first-copy sweep, 2026-08-10.
# DRAFTER_VERSION and RUNTEMPLATE correctly do NOT bump: no offer-time price
# and no map/route shape changed.
# CONSTANTS_VERSION 10 (window 2 of the 2026-08-13 correctness batch, EB-104).
# C9's "further errata may join" clause is SPENT: it holds only "until a
# number is published under this stamp", and the twelve-arm standing table of
# 2026-08-13 (`review/active/sitting-reads-2026-08-13.md`, commit 445b2ff) is
# published at RT11/D14/P7/C9. So this opens C10 rather than widening C9.
# Contents -- the tier0 ENGINE half of the EB-104 batch, seven combat-kernel
# behaviour fixes, each against a named authority and none of them a tuning
# choice. The bump criterion is CONSTANTS 5's ("comparability decides, not
# edit size") and the direct precedent is C6(a)/C7: a duration-tick clock and
# a set of enemy-turn mechanics are exactly what those bumps carried.
#   (a) EB-95, player-side duration debuffs tick at the ENEMY side-turn end,
#   not at the owner's turn end, and the first tick is skipped only when a
#   MONSTER applied the debuff -- the predicate is verbatim in the shipped
#   authority doc (PowerModel.SkipNextDurationTick). Enemy-OWNED
#   Vulnerable/Weak/Frail still tick at their own turn end, which bag_of_marbles
#   and fear_potion prose depends on. Incoming damage moves on three reachable
#   encounter rows (Test Subject, Soul Nexus, Hunter Killer).
#   (b) EB-96, a sleeping enemy is a side-turn PARTICIPANT: block clear,
#   turn-start and turn-end hooks all run, so its debuffs decay, its dot ticks
#   and its temp Strength reverts. advance_intent and the Nemesis Intangible
#   toggle stay suppressed, which is what the early return was load-bearing
#   for. This moves a FROZEN calibration-battery number (burst_check holds a
#   sleeper) plus two tier0.5 Act-1 bodies: measured 3.545 -> 3.653 mean turns,
#   79.70 -> 79.50 mean end HP over 400 seeded fights.
#   (c) EB-97, the Fanfare cap's base term is LIVE max HP in both engines and
#   is recomputed on gain_max_hp, per LAW's "Fanfare is capped at %maxHP"; the
#   C# side gains a named cap-fraction constant so lint_constant_parity can see
#   the term at all.
#   (d) EB-98, masque_red_death stops paying the flat-attack rider its
#   2026-07-25 redesign deleted. Any tier0/tier0.5 number measured with that
#   companion on board since then overstated damage.
#   (e) EB-99, Guest Star generation applies the personal_pool filter in BOTH
#   engines, restoring an already-ratified guardrail; the regression test that
#   passed vacuously is tightened onto personal_pool.
#   (f) EB-100, Encore Performance asks whether a card is LIT rather than who
#   is designated, so it copies under the Orobas both-modes relic as the C#
#   card does. Every tier0.5 Furina spotlight number taken with that relic in
#   the pool since R124 priced the Rare at zero.
#   (g) EB-101, Supporting Cast's first-play draw resolves AFTER the
#   triggering card, matching SpotlightSystem's BeforeCardPlayed/
#   AfterCardPlayed split, so a card that reads the hand during its own
#   resolution sees the same hand in both engines.
# NO CARD SHEET WAS EDITED in this window, so the R179/M15 card-sheet clause
# is not the ground for this bump and is recorded as checked, not invoked:
# no card was added, removed, repriced, renumbered or moved between rarities,
# and no display name or card id changed (so the strike_dummy substring
# question does not arise).
# Every pre-window combat number for every character is archive. Archive
# banners go where the numbers are published; nothing is rewritten (R101b).
# DRAFTER_VERSION correctly does NOT bump -- no offer-time price moved and the
# payoff-reach D14 pin stands; draft.POLICY_VERSION does not move either.
# RUNTEMPLATE moves in the SAME window on its own ground (11 -> 12, above).
# CONSTANTS_VERSION 11 ([USER] rulings 1-3, 2026-08-23). Built PROPOSED on
# branch `artifact-muster-sweep` per ruling 3 (the `S4-G13` staged-branch
# precedent), then PULLED BY [USER] the same day -- the sequencing choice
# ruling 3 reserved was made as "join the open window", so the number below
# is live and every branch that ships from here is C11.
# Ground: an engine BEHAVIOUR change that moves Kokomi combat numbers -- the
# rotation law ([USER] ruling 2, 2026-08-23). A Status or a Curse is never
# one of her cards: `_op_conscript` never transforms one, `_op_exhaust_from`
# drops them from the unfiltered pool under her relic hook (explicit
# `filter:` untouched -- Dodge Roll's opt-in shape), and
# `after_card_exhausted` pays no Charge and no Burst particle for one by any
# route (Ethereal, a played Dazed, the ward's random draw-pile pick). One
# predicate (`Card.is_junk`) at all three seams. Every pre-bump Kokomi
# number that saw a Status/Curse in hand or exhaust overstated her: junk was
# free curse removal that also paid the meter ("accepted quirk", kickoff v1
# §2.1 -- retired). The bump criterion is CONSTANTS 5's ("comparability
# decides, not edit size"); the direct precedent is C10's EB-95..101 shape.
# The SAME ruling's Artifact half (Auras/Bombs coexist with Artifact) is
# C#-only -- tier0 does not model Artifact ("unimplemented in sim:
# Artifact 3", candidates.md:512) -- so it is recorded here for the window's
# completeness but moves no sim number.
# NO CARD SHEET WAS EDITED: the R179/M15 clause is checked, not invoked --
# no card added, removed, repriced, renumbered or rarity-moved.
# DRAFTER_VERSION correctly does NOT move: no op was added and no
# offer-time price moved (`_static_power` never priced junk).
# draft.POLICY_VERSION does not move either. The `EB-69` collision note
# applies to this branch exactly as it does to
# `staged/eb74-lever2-b-alone`: whichever lands second re-baselines on the
# first -- this one landed first, so a later `eb74` pull re-baselines on
# C11 (its branch note's 9 -> 10 is stale and rebases to 11 -> 12).
# CONSTANTS_VERSION 12 -- the EB-118 PHASE-1 cleanup batch (2026-08-24), and
# the ground for this one is the clause the last two bumps recorded as checked
# and not invoked: R179/M15, "a material card-sheet edit is a world change and
# lands under a CONSTANTS_VERSION bump". Card sheets WERE edited here, twenty
# rows of them, and the edits are effect-level rather than cosmetic.
#   (a) sec.5.2 -- fifteen Furina cards lose an incidental `raise_fanfare_cap`
#   rider. The line was measured close to inert (the cap has not been a
#   binding number since F-A5), so what moves is small, but "small" is not the
#   test: it is a printed effect leaving twenty percent of a pool.
#   sec.5.2's sixteenth card, `lasting_impression`, did NOT land -- its ruled
#   upgrade delta binds to the op -- so the pool keeps exactly one carrier.
#   (b) sec.5.3 -- the Block-reader family. `suffering_for_art` and
#   `lasting_impression` lose ZERO-base Fanfare readers, `hearts_swelling`
#   keeps its printed Block 3 and loses its formula. `held_breath` (Common)
#   and `thunderous_ovation` (Rare) are preserved as the two readers that pay
#   something on a cold meter. Every Furina Block and Fanfare number taken
#   before this window is archive.
#   (c) sec.4.3 -- `blast_radius` gains a chosen discard and
#   `no_holding_back` gains Exhaust plus one `confiscated`. Two Klee cards
#   cost more than they did; base damage is untouched by design (sec.4.3 adds
#   the second price first and reprices in its own window).
#   (d) sec.4.6 -- `Burst +5` printed on fifteen `skill_tag` faces. TEXT ONLY,
#   and recorded here for the window's completeness rather than as ground: the
#   tag, its membership and the meter arithmetic do not move, and a card face
#   is not a number. On its own it would not have earned a bump.
# NO ENGINE RULE MOVED IN THIS WINDOW. No op, no power and no hook is part of
# C12: at this bump the three Phase-1 items that would have touched the engine
# were staged and unpulled, and C12 is a pure content window.
# THE SECOND HALF OF THAT SENTENCE HAS BEEN CORRECTED IN PLACE (2026-08-24, at
# the C13 bump below), because it was written in the present tense about a tree
# that has since moved: all three doors landed at PR #69 (`ddd96b7`) with
# CONSTANTS_VERSION still reading 12, and door (b) brought an engine power and
# a hook with it. C12's CONTENTS are unchanged and its archive claim stands;
# what is no longer true is "staged and not pulled" as a description of `main`.
# The landed items are enumerated and carried by C13.
# RT, D and P are all UNTOUCHED and each for its own reason: no run-layer
# content moved (RT), no offer-time price and no drafter code moved so the
# D15 spotlight-limb bump is undisturbed (D), and no pilot heuristic moved --
# `PILOT_POLICIES_ENABLED` is still False (P).
# THE RE-BASELINE IS OWED AND DELIBERATELY NOT TAKEN HERE. Two of the three
# staged Phase-1 items move Klee combat numbers again the moment [USER] pulls
# them, so re-taking the twelve-arm standing table now would buy a table that
# a same-day pull invalidates -- the EB-69/EB-74 collision argument, applied
# to this window. Every pre-window Furina and Klee combat number is archive
# from this bump regardless; the archive banner goes where the numbers are
# published and nothing is rewritten (R101b). THE DEFERRAL IS DISCHARGED AT
# C13 BELOW, which is what it bought: the staged items landed first, and one
# table is taken after them instead of one before and one after.
# CONSTANTS_VERSION 13 -- the EB-118 PHASE-2 INTEGRATION window (2026-08-24).
# ONE declared window covering EVERY material sheet and engine edit that
# reached `main` after C12 was stamped. It is not a fresh batch of work: all of
# it is already merged, each door and each PR named a CONSTANTS_VERSION move as
# OWED AT LANDING, and PRs #62, #64, #65 and #69 all landed with the integer
# still reading 12. This bump is that debt paid, enumerated the way C12
# enumerated its own so that the world a C13 number was taken in is readable
# from the stamp rather than from the merge log.
# The ground is the clause C12 rested on -- R179/M15, a material card-sheet
# edit is a world change -- plus an ENGINE half C12 explicitly did not have,
# which lands this bump on CONSTANTS 5's comparability criterion as well
# (C10's EB-95..101 shape is the direct precedent for that half).
#   (a) PHASE 2B -- `big_badda_boom`, BOTH PRs, one card. #64 (`baa8a97`) made
#   the row the pool's FIRST DRAFTABLE CARRIER of `ethereal:`, its old
#   `{damage: +4}` upgrade delta replaced by `{remove: ethereal}` under the
#   one-upgrade-axis rule. #65 (`b967be6`) then REPLACED that body rather than
#   amending it, on R201's Option A: "Deal 16. If this kills its target, deal 8
#   to a random other enemy." The rider is EXISTING grammar
#   (`conditional`/`killed_target`, already shipped on `sparkly_explosion` and
#   `showstopper` in both engines), so no op, no loader vocabulary, no codegen
#   entry and no predicate moved with it; the classifier re-derived the fight
#   band [mid] -> [mid, late] and landed it.
#   (b) DOOR (a) -- the Bomb-placement target cut (`1873c7e`, R204). TWELVE
#   `place_bomb` rows leave `target: random_enemy`: eight to the concentration
#   form (`target: enemy`), four to the distribution form, with the codegen and
#   TargetType work the latter needs. Klee's demolition board changes shape.
#   `klee/demolition_weighted` A2_scaling reads 4.937 and that number is
#   DESCRIPTIVE EVIDENCE with NO re-band, because R204 retired the live
#   per-axis deck-band system as acceptance law roster-wide.
#   (c) DOOR (b) -- the Explosives Workshop conversion (`5a51c1b`, R203), and
#   this is the half C12 could not have had. The flat `bomb_damage_up` install
#   becomes `bomb_damage_per_rotation`, A NEW ENGINE POWER with a once-per-turn
#   latch on discard-or-Exhaust: new code in `tier0/engine/effects.py` and
#   `tier0/engine/refpowers.py`, mirrored in `DemolitionPowers.cs`. It
#   increments the SAME bomb-damage stat the detonation reads, so a Bomb armed
#   three turns ago detonates at today's number, and the upgrade raises the
#   per-trigger increment (+1 -> +2) rather than adding a second trigger. The
#   frozen connectivity classifier learned the word under an authorized
#   `VOCAB_VERSION` v3 with both sides re-run.
#   (d) DOOR (c) -- `lasting_impression` (`ad36c41`, R203). The sixteenth card
#   of sec.5.2 sheds its `raise_fanfare_cap` line at last, and the broken
#   `{fanfare_cap: +2}` delta that BOUND to that op is replaced by
#   `{encore: +2}` (`gain_encore` 4 -> 6 on the upgraded face). An UNBLOCKER,
#   not a richness repair. Furina's pool now carries ZERO cap riders.
#   (e) PHASE 2C's LANDED CONTENT (`1d843ac`). `deep_breath` converts to
#   `choose_one` with R194's ratified pair, its upgrade delta moves
#   `remove: exhaust` -> `{cost: -1}`, a modal resolution path lands in
#   `tier0/engine/effects.py`, and `tools/role_tempo.py` re-derived and landed
#   the fight band early -> early/mid/late.
#   THIS ITEM IS IN THE WINDOW ON PURPOSE, AND THE REASON IS RECORDED RATHER
#   THAN ASSUMED. R191 names three Phase-2 windows and assigns stamps to two of
#   them -- "2B stamps = C + D, 2C chooser = its own window and its own P
#   bump" -- which leaves 2C's CONTENT unassigned, because R191 was written
#   before that content was on `main`; the 2C commit itself names "the required
#   C bump" as integration's. It is folded in here rather than held, because a
#   stamp integer labels a WORLD and not a subset of one: `main` today resolves
#   `deep_breath` from a modal body and upgrades it with a cost drop, and a C13
#   note that did not say so would misdescribe every number published at C13.
#   What is NOT here is 2C's ACTIVATION -- `MODE_CHOOSER_ENABLED` is still
#   False, no pilot heuristic moved, and the chooser keeps its own window and
#   its own `P` bump exactly as R191 orders.
#   AND THE LANDING IS NOT INERT, which is the other half of the reason. With
#   the chooser off the engine resolves mode 1, the body the card already
#   shipped, so the base face moves no number -- but the UPGRADE delta is live
#   either way, and an upgraded Deep Breath now costs 0 and KEEPS Exhaust where
#   it used to cost 1 and lose it.
#   (f) `EB-122` (`26af01d`) is recorded for completeness and is NOT ground:
#   the five blocked Kokomi cards get their C# grammar and the codegen that
#   emits it. No card sheet row and no tier0 module moved, so no sim number
#   moves and on its own it would not have earned a bump.
# EVERY PRE-WINDOW KLEE AND FURINA NUMBER IS ARCHIVE. Kokomi's sheet and her
# engine path are untouched by (a)-(f), so her three arms are this window's own
# control -- the re-baseline below REPORTS whether they reproduced rather than
# asserting that they would. Archive banners go where the numbers are
# published; nothing is rewritten (R101b).
# `RT` and `P` are UNTOUCHED, each on its own ground: no run-layer content
# moved (`RT`), and no pilot heuristic moved -- BOTH switches are still False
# (`PILOT_POLICIES_ENABLED` for the 2A pair, `MODE_CHOOSER_ENABLED` for 2C) --
# so `P` stays at 7 and both activation windows stay open (R191). `D` moves in
# the SAME window on its own ground (15 -> 16, below): each field once,
# together, at the end of the window, which is the shape RT11/C10 took.
# THE RE-BASELINE IS TAKEN AT THIS BUMP:
# `review/active/sitting-reads-2026-08-24-c13-d16.md`. It is TEN of the twelve
# arms, and the shortfall is an instrument loss disclosed there and filed as
# BACKLOG `EB-128`: the gitignored `game_ref/` tree was destroyed on this
# machine a fourth time, so `real_ironclad` and `real_silent` cannot be loaded
# at all and their two rows could not be run. `ref_ironclad` is unaffected and
# carries the anchor-identity check.
# CONSTANTS_VERSION 14 -- the `deep_breath` MODE-2 RE-BODY (R205, [USER]
# 2026-08-24), landed inside the EB-118 Phase-2C activation window. ONE window,
# ONE card, ONE mode body, enumerated the way C13 enumerated its own so that
# the world a C14 number was taken in is readable from the stamp.
#   (a) `deep_breath` mode 2: `spend_encore 2` + `draw 2` becomes
#   `spend_encore 3` + `draw 3`, label "Spend 2 Encore: draw 2" -> "Spend 3
#   Encore: draw 3". MODE 1 IS UNCHANGED, and so is every frame field -- cost,
#   type, rarity, register, Exhaust, tags, and the `{cost: -1}` upgrade delta.
#   Nothing else on any sheet moved.
# THE GROUND IS R179/M15, unamended and unstretched: this is an EFFECT-NUMBER
# CHANGE, which that rule names in its own text, and R202's role/archetype
# amendment is the same logic reaching a different field -- a sheet field that
# is mechanically read is material. The bump is owed by the re-body ALONE and
# would have been owed with the chooser still off, which is why it is declared
# here on its own ground and not folded into the `P` flip that shares the
# landing.
# WHY A SEPARATE WINDOW FROM C13 rather than an amendment to it: C13 CLOSED,
# and its re-baseline was published under it
# (`review/active/sitting-reads-2026-08-24-c13-d16.md`). A stamp integer labels
# a world, and a published number cannot be moved into a world it was not taken
# in -- so a sheet edit after the close is a new window, the way C13 itself was
# a new window over C12's landed debt rather than an edit to C12's note.
# WHAT IS ARCHIVE: every Furina tier-0.5 and combat number that DEPENDS ON
# WHICH MODE DEEP BREATH RESOLVES. With the chooser live that is a real set,
# and the honest bound is that it is the whole Furina column rather than a
# named subset -- the card is an Uncommon in the general pool, so any Furina
# arm can draft it. Klee's and Kokomi's numbers are untouched by (a): neither
# pool holds a modal card. Archive banners go where the numbers are published;
# nothing is rewritten (R101b).
# `RT` AND `D` ARE UNTOUCHED, and `D` was MEASURED rather than argued. No
# drafter code and no dial value moved, and the price this sheet edit feeds is
# unmoved on both faces: `deep_breath` prices 0.6000 -> 0.6000 and
# `deep_breath+` 0.6000 -> 0.6000, because `MAX(modes)` returns mode 1 and the
# edit deepened the LOSING mode (-0.6000 -> -0.9000). Had that max moved, the
# move would still have been C-ground and not D-ground -- a sheet consequence
# priced through live dials, the precedent D16 set when three `place_bomb`
# rows repriced off door (a) -- but it did not, so there is nothing to
# attribute. `P` moves in the SAME landing on its own ground (8 -> 9, the
# chooser flip), with `PILOT_WEIGHTS_VERSION` 3 -> 4 beside it: each field
# once, each on its own reason. The live cell at this landing is
# `RT12/D16/P9/C14`.
# THE RE-BASELINE OWED HERE IS NOT A SECOND TABLE. R202 step (iii) owes ONE
# Phase-2 post-read taken after both activation windows close, and this landing
# closes the second one -- so the read this bump re-baselines into is that
# post-read, which is now unblocked and owed, rather than a table taken twice
# in one day. That is the same argument the 2A flip recorded when it took no
# table of its own.
# CONSTANTS_VERSION 15 -- the EB-118 PHASE-3 WINDOW 1 LABEL PASS (R202, [USER]
# 2026-08-24: "The current phase 3 ledger is ratified."), landed 2026-08-25.
# ONE window, METADATA ONLY: sixteen `role` conversions and five `archetypes`
# changes across nineteen cards on the three character sheets, plus the three
# `tempo_band.run` values the classifier re-derives off `role` and the one
# generated C# file the `demolition_commons` pool feeds. NO card body, cost,
# rarity, keyword, `solve` or upgrade delta moves; no op is added; no drafter
# code and no pilot heuristic moves.
# THIS IS THE FIRST BUMP TAKEN UNDER R202's LAW AMENDMENT, and it is declared
# on that ground alone: "a change to a card's `role` or `archetypes` is a
# material card-sheet edit because both fields are mechanically read by
# drafting. It requires a `CONSTANTS_VERSION` bump, and drafted-world numbers
# are not comparable across it." R179/M15's own enumeration -- additions,
# removals, cost changes, effect-number changes, rarity moves -- reaches NONE
# of these edits, which is exactly why the amendment was ratified and why this
# window could not have been stamped without it.
#   (a) THE SIXTEEN ROLE CONVERSIONS. Twelve `payoff` -> `enabler` and four
#   `payoff` -> `glue`, by pool: furina/fanfare (`florid_cadenza`,
#   `the_sea_is_my_stage`, `reginas_mercy`), furina/spotlight (`leading_role`,
#   `supporting_cast`, `prima_donna`, `command_performance`, `rain_of_roses`),
#   furina/salon (`singer_of_many_waters`, `grand_gala`), kokomi/priest
#   (`sango_prayer`, `vigil_of_the_deep`, `prayer_to_the_moon`) and
#   klee/demolition (`explosive_frags`, `all_my_treasures`,
#   `playtime_forever`). Nineteen payoff tags leave five arms off eighteen
#   cards, and the measured supply is the ratified arithmetic exactly:
#   furina/fanfare 14 -> 10, kokomi/priest 14 -> 11, klee/demolition 10 -> 7,
#   furina/spotlight 10 -> 5, furina/salon 9 -> 5, klee/spark 7 -> 6,
#   furina/generic 9 -> 8, kokomi/generic 13 -> 10; klee/generic 3,
#   klee/reaction 8, kokomi/assist 5 and kokomi/commander 6 do not move.
#   (b) THE FIVE `archetypes` CHANGES. `showstopper` [fanfare] -> [generic],
#   `high_tide` [salon, fanfare] -> [fanfare], `rain_of_roses`
#   [salon, spotlight] -> [generic], `singer_of_many_waters` [generic, salon]
#   -> [generic], and `big_badda_boom` [demolition, generic] -> [generic]
#   (the W1 audit ruling, [USER] 2026-08-24 "Agreed on all of those rulings").
#   (c) THE ONE COMBAT CONSEQUENCE, and it is (b)'s alone. `demolition_commons`
#   is DERIVED at load as every non-kit Common carrying the tag, so Big Badda
#   Boom's drop takes `secret_stash`'s add-pool from EIGHT members to SEVEN and
#   that card can no longer arrive off it. That is an outcome-distribution
#   change inside a fight, not a drafting one, and it was accepted WITH the
#   ruling rather than discovered after it. The klee `demolition` sub-pool
#   reads 28 -> 27 and `generic` stays 19 (the card already carried it).
#   (d) THREE CLASSIFIER RE-DERIVATIONS, taken as the classifier ruled them.
#   `role_tempo.run_bands` reads `role`: an uncommon that is not a payoff also
#   bands `early`, so `florid_cadenza` [late] -> [early, late] and
#   `leading_role` / `supporting_cast` [late] -> [early]. No rare moved.
#   (e) THE ONE C# DELTA, which is the proof `archetypes` reaches emission:
#   `SecretStash.cs` drops `ModelDb.Card<BigBaddaBoom>()` from its stash list,
#   so both engines read seven. No other generated file moves and
#   `gen_roster_cards.py --check` is clean on all three sheets.
# WHAT IS ARCHIVE: EVERY tier-0.5 DRAFTED NUMBER FOR ALL THREE CHARACTERS.
# `is_on_plan_payoff` is literally `role == "payoff" and archetype in
# card.archetypes` and the adaptive scorer reads both fields a second time, so
# an offer scored before this window is not comparable with one scored after
# it -- which is the amendment's own sentence, applied. The combat archive is
# NARROW and named: Klee numbers that depend on what `secret_stash` produces,
# per (c). Nothing else in combat moves, because no body moved. Archive
# banners go where the numbers are published; nothing is rewritten (R101b).
# AND THE ATTRIBUTION CAVEAT IS PART OF THE WINDOW, pre-registered before it
# opened (`review/active/eb118-w1-preregistration-2026-08-24.md` §3): NO causal
# role-versus-tag claim may be read out of a tier-0.5 number taken after this
# bump, because both fields feed the same scorer. The window is ONE window by
# ruling (R202 call (7)), not a 1a/1b split, and the honest repair if such a
# claim ever matters is to split the window and re-run.
# `RT`, `D` and `P` ARE UNTOUCHED, each on its own ground. No run-layer content
# moved (`RT`). No drafter code and no dial value moved (`D`): the offer scorer
# reads these fields, but a sheet consequence priced through live dials is
# C-ground and not D-ground -- the precedent C14 set on `deep_breath` and D16
# set on the repriced `place_bomb` rows. No pilot heuristic moved (`P`); both
# activation switches keep the values Phase 2 left them at. The live cell at
# this landing is `RT12/D16/P9/C15`.
# NO STANDING BASELINE IS OWED AT THIS BUMP, and that is R207 rather than a
# deferral: a standing table is published at a meaningful product milestone or
# when a pending decision needs one, and no pending decision names one here.
# The registered read for this window is the PAIRED CONNECTIVITY re-read the
# pre-registration owed, taken against the Phase-2 post-read that R202 step
# (iv) made W1's pre-state.
# CONSTANTS_VERSION 16 -- the EB-118 PHASE-3 WINDOW 2 CARD-BODY PASS (R202,
# [USER] 2026-08-24: "Agreed on the per-card judgments for now." and "The
# current phase 3 ledger is ratified."), landed 2026-08-25. ONE window, THREE
# ratified Kokomi bodies and their upgrade deltas, plus one Furina upgrade
# delta that rides the landing on its own provenance. W1 was metadata only;
# this window moves PRINTED CARDS, so its ground is R179/M15 as written --
# effect-number changes -- with R202's role/archetype amendment reached once
# more by (c). Enumerated the way C13, C14 and C15 enumerate their own so that
# the world a C16 number was taken in is readable from the stamp.
#   (a) `moon_signal` (kokomi, Common, cost 0, Skill) -- the free cycle becomes
#   a free REORDER. Effects `discard 1` (random) + `draw 1` become
#   `discard 1 select: chosen` + `recall_to_draw 1`, and the draw moves onto a
#   new `sly: [{op: draw, amount: 1}]` rider, so the bell rings when the card
#   is THROWN rather than when it is played. UPGRADE `{draw: +1}` ->
#   `{retain: true}`: `add` appends unless `add_before` is given,
#   `recall_to_draw` inserts at draw-pile index 0 and `state.draw` pops index
#   0, so an appended draw would take back exactly the card the recall placed.
#   Retain sets a card FIELD and inserts nothing, so the printed order is
#   identical between the faces. `role`, `archetypes` and `tempo_band` do not
#   move (assist / enabler).
#   (b) `crane_wing` (kokomi, Uncommon, cost 1, Skill) -- printed `block`
#   6 -> 4, `cost_mod` rider untouched. The upgrade delta `{block: +2}` is
#   UNCHANGED and the base moved, so the upgraded face reads 8 -> 6 and lands
#   level with `jade_bulwark`'s printed Block instead of above it. No label
#   moves (commander / glue), so R199's third guardrail is untouched.
#   (c) `tighten_the_cords` (kokomi, Common, cost 1, Skill) -- BODY AND LABELS
#   TOGETHER. Printed `block` 3 -> 5, and the unconditional
#   `apply_power metallicize 1 target: self` becomes that same apply inside
#   `{op: conditional, if: exhaust_pile_at_least_3}`. UPGRADE
#   `{power_amount: +1}` -> `{block: +2}` per R58's always-live-half rule, so
#   the upgraded face reads block 7 with the bar where it is printed instead of
#   block 3 / metallicize 2. `archetypes` [generic] -> [priest] and `role`
#   glue -> payoff under Fork A (the label follows the body): reading the
#   Exhaust pile is priest's public state. This is the SECOND bump to reach
#   R202's LAW amendment, and the only card in this window that does.
#   (d) ONE CLASSIFIER RE-DERIVATION, taken as the classifier ruled it and
#   written by `suggest_role_tempo_tags.py --land` rather than by hand.
#   `tighten_the_cords` `tempo_band.fight` [early] -> [early, mid, late] and
#   `.run` [early] -> [early, late], off (c)'s `role`. No other row moved and
#   `--check` reports all three sheets matching the classifier.
#   (e) `encore_performance` (furina, Rare, cost 0, Skill) -- ex-`QUEUE` `M27`,
#   ruled R205, and ITS PROVENANCE IS NOT EB-118. It rides this window because
#   this was the open build and it shares an emitter door with (a). The BODY
#   does not move; the card gains the upgrade delta `{retain: true}` where it
#   had NONE. That is a material sheet edit on R179/M15 ground in its own
#   right: the delta answers target-dependence -- a 0-cost Rare that does
#   nothing unless a Spotlighted card is in hand -- so the upgrade buys TIMING,
#   not a bigger copy, and it sidesteps FLAG-2(ii) because `retain` binds to no
#   op. Three curated registers emptied with it, each by its own stated gate:
#   `lint_upgrade_coverage.SHEET_EXEMPT`, `lint_upgrade_coverage.CODEGEN_DEBT`
#   and `test_roster_codegen.FURINA_UPGRADE_GAP_PENDING_FB1`.
#   (f) THE C# DELTAS, all generated: `MoonSignal.cs`, `CraneWing.cs`,
#   `TightenTheCords.cs`, `EncorePerformance.cs`, and the Furina manifest's
#   `no_upgrade_path` emptied. `apply_power` joins the codegen's `BRANCH_OPS`
#   for the SELF target ONLY -- the enemy arms need the target guard or declare
#   locals and still block by name -- which is what (c) needed and the reason
#   Kokomi is 75/76 rather than 74/76. Furina stays 81/82 and
#   `gen_roster_cards.py --check` is clean on all three sheets.
# WHAT IS ARCHIVE. EVERY KOKOMI tier-0.5 AND COMBAT NUMBER: three drafted-pool
# bodies moved (two Commons and an Uncommon, so any Kokomi arm can draft them)
# and three upgrade deltas with them. EVERY FURINA tier-0.5 NUMBER, by (e) and
# on the run layer rather than in a fight: `model.rest_action` filters its
# smith candidates through `upgrades.has_upgrade`, so a Rare that had no
# upgrade path was never a candidate and now is -- the candidate SET moved even
# though the card's own price did not. Furina combat numbers are archive only
# for decks holding the upgraded face, which could not exist before this
# window. KLEE IS UNTOUCHED: no Klee sheet row, no Klee upgrade, no Klee
# generated file. Archive banners go where the numbers are published; nothing
# is rewritten (R101b).
# `RT`, `D` and `P` ARE UNTOUCHED, each on its own ground. No run-layer content
# moved (`RT`). No pilot heuristic and no weight value moved (`P`); both
# activation switches keep the values Phase 2 left them at. No drafter code and
# no dial value moved (`D`) -- and the prices these sheet edits feed WERE
# MEASURED rather than argued, because they move: `moon_signal` -0.5000 ->
# 1.0000 on both faces, `crane_wing` 6.0000 -> 4.0000 and its upgraded face
# 8.0000 -> 6.0000, `tighten_the_cords` 3.0000 -> 5.0000 and 3.0000 -> 7.0000,
# `encore_performance` 3.0000 -> 3.0000 with an upgraded face that now exists
# and prices 3.0000. A sheet consequence priced through LIVE dials is C-ground
# and not D-ground -- the precedent C14 set on `deep_breath` and C15 restated
# -- so the whole of that movement is declared here.
# THE SUPPLY MOVEMENT IS (c)'s AND IT IS NAMED, NOT INFERRED: kokomi/priest
# payoff supply 11 -> 12 over a sub-pool of 28 -> 29, and kokomi/generic loses
# the row from its sub-pool (36 -> 35) with its payoff count unchanged at 10.
# assist (5) and commander (6) do not move. The cost is the one the ruling
# already named: priest is the most over-supplied arm on the sheet and this
# adds a payoff to it. R199 ruled the bands DIRECTIONAL and Guardrail 1 forbids
# relabelling a card to keep a count tidy, so the number is disclosed rather
# than balanced against.
# THE WINDOW'S OWN GATE, MEASURED ON THIS WORLD: the `kokomi` `neardup` count
# reads 33 -> 29 against a limit of 30 pairs, so R200's TEMPORARY breach is
# CLEARED BY REDESIGN and not by a moved threshold -- the limit is untouched at
# 0.40. Beside it `uniq` 53% -> 54%, `decide%` 33% -> 36%, `hapax` 11 -> 10,
# `rider%` 36% -> 34%, and `maxclu` unmoved at 8 (still curated debt, with
# `uniq`). The `furina`, `klee` and `mondstadt-companions` pools are
# byte-identical across the window. `lint_strict_domination` is CLEAN over 264
# compared cards with all five EB-125 allowlist entries deleted, and
# `lint_role_tempo_coverage --gate` is green at 18 findings against 18 pins on
# both sides -- (c)'s relabel neither opened nor closed a coverage cell.
# NO STANDING BASELINE IS OWED AT THIS BUMP (R207): a standing table is
# published at a meaningful product milestone or when a pending decision needs
# one, and no pending decision names one here -- `S4-G13`'s pull condition
# reads a table when the lever is pulled, which is not this landing. NO
# CONNECTIVITY READ IS REGISTERED FOR THIS WINDOW EITHER: W1's read was owed by
# W1's own pre-registration §4, no W2 pre-registration exists, and R207 gives
# W3 the single public window with the single standing read. What was taken
# here is a BUILD-TIME FACT in W1 §5's sense, recorded in the landing commit so
# it cannot later be discovered and read as a finding, and it is NOT graded
# against §2.4's committed directional predictions.
# CONSTANTS_VERSION 17 -- the EB-118 PHASE-3 WINDOW 2b CARD-BODY PASS (R208,
# [USER] 2026-08-25: "Overall I agree as well; we can ratify the currely set."),
# landed 2026-08-25. ONE window, FIVE ratified bodies across ALL THREE
# characters -- the Exhaust-reader clone rewrites R205 ruled in as `W2b` plus
# the two Furina bodies and the one Klee body the same slate carried. W1 was
# metadata only and W2 moved three Kokomi cards; this window moves PRINTED
# CARDS ON EVERY SHEET, so its ground is R179/M15 as written -- effect-number
# changes -- with R202's role/archetype amendment reached twice more, by (a)
# and (b). Enumerated the way C13, C14, C15 and C16 enumerate their own so
# that the world a C17 number was taken in is readable from the stamp.
#   (a) `sparkly_explosion` (klee, Rare, cost 2, Attack) -- the kill-gated
#   splash becomes a DELIBERATE detonation. Effects `damage 18` +
#   `conditional if: killed_target then: [gain_spark 3, place_bomb 1
#   all_enemies bomb_damage 6]` become `move_bombs target: enemy` +
#   `detonate target: enemy bonus: 3` + `damage 14 target: enemy`, in that
#   order. UPGRADE `{damage: +5}` is UNCHANGED and the base moved, so the
#   upgraded face reads 14 -> 19 instead of 18 -> 23. `archetypes`
#   [demolition, spark] -> [demolition] -- R202's amendment, first of two
#   here, and the second of R202 call (8)'s two ruled steps on `klee/spark`.
#   `solve` [frontload, velocity] -> [frontload, utility], the classifier's
#   own derivation. WHY THE ORDER IS THE RULING: `_detonate_bombs_on_hit` is
#   guarded on `enemy.alive` and reached only when hp damage is nonzero, so an
#   implicit pop is discarded twice over -- once if the swing kills, once if
#   Block eats it. An explicit `detonate` before the damage line is immune to
#   both. Measured on the real resolver: on an empty board the card resolves
#   as a plain 14. BOTH VERBS ARE LIVE REGISTERED GRAMMAR -- three `detonate`
#   rows ship (`quick_fuse`, `remote_detonator`, `chained_reactions`) and one
#   `move_bombs` (`careful_arrangement`) -- so nothing was built in either
#   engine for it.
#   ITS SIMULATED NUMBER IS EXPLICITLY DIAGNOSTIC UNTIL `EB-136`'s SAME-TARGET
#   REPAIR LANDS, and that is declared here rather than discovered later.
#   tier0 re-resolves `target: enemy` INDEPENDENTLY PER OP to the lowest-HP
#   living enemy (`_pick_targets`), while C# holds one `cardPlay.Target` for
#   all three -- and this is the first shipped card where an earlier op on the
#   card routinely KILLS the aim, so the sim can scatter what the mod
#   concentrates. Any tier-0.5 number taken on this row systematically
#   UNDERSTATES it, and that sentence belongs beside any published number.
#   (b) `standing_room_only` "The House Rises" (furina, Uncommon, cost 1) --
#   BODY AND LABELS TOGETHER. `damage 5 target: all_enemies bonus_formula
#   1_per_4_fanfare` becomes `block 3` + `conditional if: encore_at_least_5
#   then: [block 3] else: [draw 1]`. Type attack -> SKILL, `role` payoff ->
#   glue (R202's amendment, second of two here), `solve` [frontload, scaling]
#   -> [block, velocity], `tempo_band.run` [late] -> [early, late].
#   `archetypes` [fanfare, generic] is UNCHANGED. UPGRADE `{damage: +2}` ->
#   `{block: +2}`: `_bump_first` matches `op == "block"` at TOP LEVEL only, so
#   the printed 3 -> 5 and both branch arms are untouched, which is R58's
#   always-live-half rule. THE ELSE-ARM IS `draw`, NOT `gain_encore`, and that
#   is the ruled half of the call: with Encore the card's usual face would
#   have read as `macaron_break` (Common: Encore 2 + Block 2) plus one Block
#   one rarity up -- the twin pattern this pass exists to kill, and one no
#   lint can see because `effect_maps` treats a conditional as opaque and the
#   distinctness report reads verbs rather than magnitudes. No Furina card at
#   any rarity prints Block and draw together.
#   (c) `dramatic_entrance` (furina, Uncommon, cost 1, Attack) -- candidate A
#   of the slate. `damage 6 target: enemy bonus_formula 1_per_4_fanfare`
#   becomes `damage 7 target: enemy` + `conditional if: fanfare_at_least_12
#   then: [damage 7 target: all_enemies]`. UPGRADE `{damage: +3}` is
#   UNCHANGED and the base moved, so the upgraded face reads 7 -> 10; under
#   R58 the bar of 12 may never be lowered on upgrade or by erratum. NO LABEL
#   MOVES on this card -- `role: payoff`, `archetypes: [fanfare]`, cost, type,
#   rarity and `tempo_band` all hold, and `solve` [frontload, scaling] HOLDS
#   TOO: the slate expected `scaling` to leave with the slope, and
#   `role_tempo` keeps it under R91/2c as countersigned, because a
#   `fanfare_at_least_` gate ON A DAMAGE LINE is a meter read. The card stops
#   being "a larger Applause Line" by changing SHAPE above a bar rather than
#   changing its number.
#   (d) `undertow` (kokomi, Uncommon, cost 1, Attack) -- the revision is
#   EXACTLY TWO CHANGES on a card that keeps its shape: `amount_formula.base`
#   4 -> 5, and a NEW `conditional if: exhaust_pile_at_least_3 then: [draw 1]`
#   appended. The slope, the `sly: [{op: energy, amount: 1}]` rider (a LAW-5
#   statement, not a number), the `{formula_base: +3}` upgrade delta, `solve`
#   and BOTH labels are untouched, so `kokomi/assist` payoff supply holds at
#   5. The U-A access rewrite the slate carried was REJECTED under R199's
#   guardrail -- no label-for-count -- and this row is what replaced it.
#   (e) `depths_judgment` "Sango Isshin" (kokomi, Rare, cost 2, Attack) --
#   `damage amount_formula {base: 10, per: 2, count: exhaust_pile}` becomes
#   `damage 14 target: enemy` + `conditional if: exhaust_pile_at_least_6
#   then: [block 8]`, the DIVIDEND job: the deep pile pays something other
#   than damage. UPGRADE `{formula_per: +1}` -> `{damage: +4}` (14 -> 18) --
#   the retired delta had no formula left to bump. `solve` [frontload,
#   scaling] -> [block, frontload]; `role: payoff` and `archetypes: [priest]`
#   do not move, so `kokomi/priest` payoff supply holds at 12. THE BAR IS 6,
#   NOT THE SLATE'S FIRST 8, AND IT WAS CHOSEN AT ~2x THE BAR-8 RATE: measured
#   on `kokomi/priest_weighted` attack plays, `exhaust_pile_at_least_6` fires
#   12.8% and `_at_least_8` fires 7.4% (mean pile 1.65, median 0, p90 6, p99
#   12). One consequence is named because a test now pins it: an Attack that
#   gains Block from a branch is a legal `nimble` enchant target, and the
#   generated class declares `GainsBlock => true` because BaseLib's
#   auto-detect cannot see a conditional Block row (`EB-84`).
#   (f) THREE CLASSIFIER RE-DERIVATIONS, taken as the classifier ruled them
#   and written by `suggest_role_tempo_tags.py --land` rather than by hand:
#   (a)'s `solve`, (b)'s `solve` + `tempo_band.run`, and (e)'s `solve`. The
#   fourth candidate move -- dropping `scaling` from (c) -- the classifier
#   REFUSED, per R91/2c, and the refusal was taken. `--check` reports all
#   three sheets matching.
#   (g) THE C# DELTAS, all generated: `SparklyExplosion.cs`,
#   `StandingRoomOnly.cs`, `DramaticEntrance.cs`, `Undertow.cs`,
#   `DepthsJudgment.cs`. No emitter vocabulary moved -- every op and every
#   predicate in the five bodies already shipped -- and
#   `gen_roster_cards.py --check` is clean on all three sheets. Coverage is
#   unchanged: furina 81/82, kokomi 75/76, klee fully generated. Sparkly's
#   emitted `OnPlay` was read against the ruled order and matches it:
#   `BombPower.MoveAllTo(..., cardPlay.Target, ...)`, then
#   `BombPower.DetonateOn(cardPlay.Target, 3)`, then `DamageCmd.Attack(14)
#   .Targeting(cardPlay.Target)` -- one target, three ops, which is exactly
#   the binding `EB-136` must give the sim.
# WHAT IS ARCHIVE. EVERY tier-0.5 NUMBER FOR ALL THREE CHARACTERS, and this
# window is the first since C13 where that is true of all three at once:
# drafted-pool bodies moved on the klee, furina and kokomi sheets, so an offer
# scored before this window is not comparable with one scored after it. EVERY
# KLEE, FURINA AND KOKOMI COMBAT NUMBER is archive as well, because all five
# moved bodies are draftable rows any arm of their character can hold -- there
# is no narrow carve-out to make here, unlike C15's. Archive banners go where
# the numbers are published; nothing is rewritten (R101b).
# `RT`, `D` and `P` ARE UNTOUCHED, each on its own ground. No run-layer content
# moved (`RT`). No pilot heuristic and no weight value moved (`P`); both
# activation switches keep the values Phase 2 left them at, and the one
# pilot-side test that moved is a POSITIVE CONTROL's run count, not a weight.
# No drafter code and no dial value moved (`D`) -- and the prices these sheet
# edits feed WERE MEASURED through `draft._static_power` rather than argued,
# because they move, C-ground per the precedent C14 set on `deep_breath` and
# C15 and C16 restated: `sparkly_explosion` 9.7500 -> 10.5000 and its upgraded
# face 12.2500 -> 13.0000; `standing_room_only` 10.0000 -> 3.0000 and 14.0000
# -> 5.0000 (the 10.00 it leaves was two-thirds `STATIC_AOE_MULT` on a number
# this body no longer prints -- a correction, and a large one);
# `dramatic_entrance` 6.0000 -> 7.0000 and 9.0000 -> 10.0000; `undertow`
# 5.0000 -> 6.0000 and 8.0000 -> 9.0000; `depths_judgment` 6.0000 -> 11.0000
# and 6.5000 -> 13.0000. Two of the five conditionals are credited at FULL
# FACE rather than zero, because `_static_condition` waves the
# `exhaust_pile_at_least_` prefix through: (d)'s draw credits nothing anyway
# under the v3 flat proxy, but (e)'s 8 Block is paid for against a 12.8% fire
# rate, an over-credit bounded at 4.0 and disclosed rather than tuned out.
# THE SUPPLY MOVEMENT IS (a)'s AND (b)'s, AND IT IS NAMED, NOT INFERRED:
# `klee/spark` payoff supply 6 -> 5 over a sub-pool of 22 -> 21, and
# `furina/fanfare` 10 -> 9 AND `furina/generic` 8 -> 7 off ONE edit, because
# `role` is one field and moving it removes the card from EVERY archetype's
# payoff count -- both of The House Rises' tags, not just the one the ruling
# discussed. Both Furina sub-pools are unchanged (30 and 34); the card kept
# its tags. `klee/demolition` (7), `kokomi/priest` (12), `kokomi/assist` (5)
# and every other arm do not move.
# THE WINDOW'S OWN MEASUREMENTS, TAKEN ON THE COMPOSED WORLD (main + W1 + W2 +
# W2b) AND NOT PROJECTED. Distinctness, pre -> post: `furina` `uniq` 73% ->
# 76% and `maxclu` 5 -> 4 -- (c) leaves the pool's ONLY five-member clone
# family (`damage@one~`, now four: `applause_line`, `high_tide`, `house_call`,
# `poised_riposte`) and (b) takes `damage@all~` from three to two, with
# `neardup` unmoved at 8. `kokomi` `uniq` 54% -> 57%, `top` 30% -> 32%,
# `rider` 34% -> 36%, `neardup` unmoved at 29 and `maxclu` unmoved at 8: (d)
# and (e) take `CLONES 5x damage@one~` to THREE (`all_streams_flow`,
# `pearl_barrage`, `what_the_tokoyo_took`). `klee` `hapax` 22 -> 21 and
# `decide` 22% -> 21%, everything else unmoved (`uniq` 62%, `maxclu` 5,
# `neardup` 21); `mondstadt-companions` byte-identical. THE THREE LAW
# THRESHOLDS ARE UNMOVED AND SO IS THE STANDING DEBT: `kokomi` `uniq` 57% < 70
# and `maxclu` 8 > 5, and `klee` `uniq` 62% < 70, are all PRE-EXISTING curated
# entries in `test_distinctness_gate`; this window opens no new breach and
# closes none of them (the eight-member cluster is flat BLOCK, which no body
# here touches). `lint_strict_domination` is CLEAN over 264 compared cards in
# 6 sheets. `lint_role_tempo_coverage --gate` is green at 18 findings against
# 18 pins on both sides -- (b)'s payoff -> glue neither opened nor closed a
# coverage cell. `lint_furina_registers` reports 0 violations and was NOT
# expanded: (c) keeps `_touches_fanfare` selecting `dramatic_entrance`,
# because the predicate matcher fires on an `if:` beginning
# `fanfare_at_least_`, so R2's fanfare-reader coverage is held by the lint and
# not only by the sheet.
# NO STANDING BASELINE IS OWED AT THIS BUMP (R207): a standing table is
# published at a meaningful product milestone or when a pending decision needs
# one, and no pending decision names one here. NO CONNECTIVITY READ IS
# REGISTERED FOR THIS WINDOW EITHER: no W2b pre-registration exists and R207
# gives W3 the single public window with the single standing read. The
# instrument movement recorded above is a BUILD-TIME FACT in W1 §5's sense,
# written down in the landing commit so it cannot later be discovered and read
# as a finding, and it is NOT graded against any committed prediction.
# (f) RULED LATE INTO THE WINDOW, [USER] 2026-08-25 (R209), PRE-MERGE:
#   `depths_judgment` (Sango Isshin) moves its bar `exhaust_pile_at_least_6`
#   -> `_at_least_8` on BOTH faces. (e) chose 6 against fire rates the two
#   corrections below expose as contaminated and then noisy-high; clean and
#   well-sampled, bar 6 fires 38.4% of priest attack plays (a regular
#   feature) and bar 8 fires 24.2% (roughly one attack play in four), which
#   is the earned-dividend shape (e)'s own rationale describes. The always-
#   live 14 and the `{damage: +4}` upgrade are untouched; the branch payload
#   stays 8 Block, so the drafter disclosure bound of 4.0 is unchanged (it
#   never read the rate). Under R58 the bar may rise again and may never
#   come down -- 6 is not recoverable. The window is still ONE window: this
#   item rides C17 because the chain has not reached main; nothing about it
#   re-opens (e)'s ratified body, which stands as recorded.
# ---------------------------------------------------------------------------
# FORWARD CORRECTION, 2026-08-25, to (e)'s FIRE RATES ONLY. R101b: the lines
# above stand as published and are NOT rewritten; this paragraph is appended
# beneath them, and it is the number a later reader should quote.
# WHAT WAS WRONG. (e) reports `exhaust_pile_at_least_6` firing 12.8% of
# `kokomi/priest_weighted` attack plays and `_at_least_8` firing 7.4% (mean
# pile 1.65, median 0, p90 6, p99 12). Those were taken through
# `harness/runner.score_config`, which ALWAYS runs
# `run_full_battery(*BASELINE, "generic", ...)` -- the `ref_ironclad`/`starter`
# ANCHOR BATTERY -- into the same process before it scores the target config.
# Ironclad attack plays carry an EMPTY exhaust pile, so every one of them
# entered the denominator as a zero. The pooled denominator was ~2.78x the
# Kokomi one, and the published rates are the Kokomi rates diluted by that
# factor. Nothing else in (e) is affected: the body, the bar, the upgrade
# delta and the drafter prices were never functions of these numbers.
# THE CLEAN MEASUREMENT, re-taken 2026-08-25 on the SAME instrument with the
# anchor battery removed -- `run_full_battery("kokomi", "priest_weighted",
# "priest", 40, seed)` and nothing else, sampling `len(player.exhaust_pile)`
# at every attack play, which is the exact expression the predicate reads.
# TWO SEEDS: seed 11, 2,494 attack plays -> `_at_least_6` 40.2%,
# `_at_least_8` 24.9%, mean 4.87, median 4, p90 10, p99 14. Seed 23, 2,491
# plays -> 42.2% / 27.3%, mean 5.02, median 4, p90 10, p99 15. POOLED over
# 4,985 plays: `_at_least_6` 41.2%, `_at_least_8` 26.1%, mean 4.95, MEDIAN 4.
# The contaminated path reproduces the published figures on demand -- the same
# spy through `score_config` reads 14.5% / 9.0% (mean 1.76, median 0) at seed
# 11 and 15.1% / 9.8% (mean 1.81, median 0) at seed 23 -- so the mechanism is
# demonstrated, not inferred.
# WHAT SURVIVES AND WHAT DOES NOT. THE RATIO SURVIVES: bar 6 fires about 1.6x
# as often as bar 8 clean (41.2 / 26.1), against 1.7x as published (12.8 /
# 7.4), so the comparison that actually drove the ruling -- 6 rather than the
# slate's first 8, chosen for the higher rate -- holds, and (e)'s "~2x" was a
# generous rounding on BOTH readings rather than an artefact of the
# contamination. THE ABSOLUTE LEVELS DO NOT: every one was understated by
# roughly 3x, and the two that read as near-never are the ones that mislead --
# "median 0" is really MEDIAN 4, and a mean of 1.65 is really 4.95. The Rare's
# second half is therefore a REGULAR occurrence, not the
# once-a-fight-when-you-have-really-burned moment (e) describes.
# ONE CONSEQUENCE IS [USER]'s AND HAS BEEN HANDED OVER, NOT SETTLED HERE:
# under R58 the bar of 6 is a one-way door, and it was set against a rate now
# known to be ~3x higher, so whether 6 is still the right bar is a design call
# and it is [USER]'s. Nothing in this correction moves the bar, the body or
# any stamp. The drafter disclosure above is affected the same way and by the
# same factor -- (e)'s 8 Block is credited at full face against what is really
# a 41.2% fire rate, not 12.8%, so the over-credit is LESS wrong than
# disclosed, and its bound of 4.0 is unchanged because that bound is
# 8 Block / cost 2 and never read the rate at all.
# `docs/kokomi-cards.yaml` carries the same two figures in the
# `depths_judgment` row's comment; it is pointed at this paragraph rather than
# rewritten, for the same R101b reason.
# SECOND FORWARD CORRECTION, 2026-08-25, SAME DAY, to the paragraph above --
# ITS DECIMALS ONLY. R101b again: the paragraph stands as published; this one
# is appended beneath it and carries the better-sampled figures.
# WHAT WAS IMPRECISE. The clean pooled rates above were taken at 40 fights
# per encounter over two seeds. At that setting the seed-to-seed spread is
# wide -- a six-seed sweep reads `_at_least_6` anywhere from 37.5% to 42.2% --
# because plays inside one fight share a pile trajectory, so ~2,500 attack
# plays carry the information of ~240 fights, not 2,500 independent
# observations. Seeds 11 and 23 are two of the higher draws, which put the
# pooled 41.2% / 26.1% at the top of the range rather than at its centre.
# THE BETTER-SAMPLED MEASUREMENT: the same instrument at `da33ec6`, 200
# fights per encounter over three seeds (11, 42, 23), 37,161 attack plays.
# `_at_least_6` 38.4%, `_at_least_8` 24.2%, mean 4.72, MEDIAN 4, p90 10,
# p99 14. The per-seed spread at bar 6 collapses to 38.2-38.5, which is why
# THESE are the decimals a later reader should quote.
# EVERYTHING ELSE ABOVE SURVIVES UNTOUCHED: the contamination diagnosis, the
# mechanism demonstration, median 4 not 0, the ~3x understatement, and the
# ratio (38.4 / 24.2 = 1.59 against the 1.58 above). Only the two headline
# decimals move, both down, by 2.8 and 1.9 points. The bar question handed
# to [USER] above is unchanged in kind and slightly softened in degree.
# ---------------------------------------------------------------------------
# CONSTANTS_VERSION 18 -- EB-136's SAME-TARGET BINDING (R210, [USER]
# 2026-08-25 -- full parity: Q1(b), `times` same-pass, corpse powers), landed
# 2026-08-25. NOT A SHEET WINDOW AND NOT A CARD-BODY PASS: no printed number,
# no label, no upgrade delta and no dial value moves here. What moves is HOW
# THE RESOLVER AIMS, and it moves under R179/M15's own logic -- a change that
# materially alters what a card does to a board is a `C` bump whether it is
# spelled in a sheet row or in the engine that reads one. C15/C16/C17 beneath
# it were the EB-118 Phase-3 label, Window-2 and Window-2b card-body passes.
# Enumerated the way those enumerate their own, so that the world a C18 number
# was taken in is readable from the stamp.
#   (a) THE BINDING. A card's `target: enemy` ops used to resolve
#   INDEPENDENTLY PER OP to whoever was lowest-HP at that moment
#   (`effects._pick_targets`); C# aims every one of them at the single
#   `cardPlay.Target` the play was constructed with. `CardPlay.Target` is
#   `public required Creature? Target { get; init; }` -- immutable for the life
#   of the play -- and on an autoplay `CardCmd.AutoPlay` fills it from
#   `HittableEnemies` BEFORE `OnPlayWrapper` is entered. So tier0 now takes the
#   pick ONCE, at the top of `effects.resolve_card`, holds it on
#   `CombatState.card_aim` / `card_aim_bound` for every aimed op of the card,
#   and clears it in a `finally` so the pilot's between-play estimates keep
#   reading live state. `combat._FREE_PLAY_CONTEXT` saves and restores the
#   pair, because a free play is a second `CardPlay` inside the first.
#   WHICH creature is NOT what moved and this bump does not re-open it: a
#   manual play's target is the human's mouse pick, which no engine rule
#   mirrors, so tier0 keeps its documented lowest-HP aim. Destination SCORING
#   stays severed as a later design question. `force_random_targeting` (the
#   free-play path) now rolls ONCE PER CARD rather than once per op, and only
#   for a card that actually aims -- `CardCmd.AutoPlay` rolls
#   `Rng.CombatTargets` only `if (card2.TargetType == TargetType.AnyEnemy)`.
#   (b) THE SAME BINDING INSIDE ONE OP (`times`). `_op_damage` and
#   `_op_apply_power` re-picked per hit. `AttackCommand.Execute` refilters its
#   one-element `GetPossibleTargets()` by `IsAlive` on EVERY hit and `break`s
#   on empty (`CombatState.IsLiveCombat()` returns literally `true`, so the
#   break is unconditional), so hits 2..N re-check the SAME `_singleTarget` and
#   stop when it dies. `_op_damage` now breaks on an empty target list, which
#   is that shape literally. The power side has no break to make: see (c).
#   `random_enemy` is UNTOUCHED and still re-rolls per pass -- BouncingFlask
#   throws three flasks at three separately rolled bodies, and that is a
#   different `TargetType`, not a bound aim.
#   (c) THE DEAD-TARGET RULE, AND IT IS NOT UNIFORM. Aimed DAMAGE fizzles:
#   `AttackCommand` breaks, with `CreatureCmd.Damage`'s `if
#   (originalTarget2.IsDead) continue;` behind it. Aimed POWERS LAND ON THE
#   CORPSE: `PowerCmd.Apply` guards only on `CanReceivePowers`, whose
#   first-party doc comment says in as many words that dead creatures can still
#   have powers applied to them, where `IsHittable` three lines above it does
#   test `IsDead`. Every other aimed op reaches that same corpse-accepting
#   door and is ruled with it -- `place_bomb` (`BombPower.Place` ->
#   `PowerCmd.Apply`), `move_bombs` (`BombPower.MoveAllTo` -> `PowerCmd.Apply`
#   on `dest`, while its SOURCES are `HittableEnemies` and so exclude the
#   dead), `apply_aura` / `swirl` (`ElementalHit.ApplyOnly` -> `AuraCmd.Apply`
#   -> `PowerCmd.Apply<XAuraPower>`). `detonate` lands there on its own
#   evidence: `BombPower.DetonateOn` reads `target.Powers.OfType<BombPower>()`
#   with no aliveness test at all, and the mod already NAMES the case
#   (`RecordDetonation(..., onCorpse: target is { IsDead: true })`, the EB-18
#   counter that reports and never grades). `strip_block` is deliberately left
#   on the fizzle default: it is not one of the emitter's `AIMING_OPS`, no C#
#   corpse behaviour is recorded for it, and a corpse's Block is 0, so the two
#   readings are observationally identical.
#   (d) THE DEAD-ENEMY POWER STATE, BUILT RATHER THAN ASSUMED (the audit's
#   sec.4/C3). tier0 had never applied a power to a corpse -- every picker
#   filtered `living_enemies` -- so standing it up meant examining the seams
#   the audit listed rather than discovering them later. What holds, each now
#   pinned in `tier0/tests/test_eb136_same_target_binding.py`: a corpse's
#   powers never tick and never act, because every duration tick, intent and
#   turn hook in the engine walks `living_enemies`; an aura banked on a corpse
#   is closed by `reactions.close_dead_auras` at the next settle, which is
#   EB-58's uptime rule doing its job rather than a divergence; a Bomb banked
#   on a corpse SURVIVES, because no tier0 site and no C# site removes it for
#   dying, which is what makes the corpse-detonation counter a real instrument.
#   THE PHASED-BOSS SEAM IS RECONCILED AND IT IS NOT A DEATH RULE:
#   `combat._settle_phases` rebuilds `powers` (keeping only Strength and
#   Enrage) and clears `bombs` at a REVIVE, so a debuff or a pile banked on a
#   body between its knockdown and the settle goes with the old bar. That is a
#   new body, not a corpse, and it leaves C#'s corpse-Bomb semantics untouched.
#   (e) ONE FUNNEL GUARD, and it repairs a case that PREDATES the binding.
#   `effects.deal_damage_to_enemy` now returns 0 for a dead target, which is
#   `CreatureCmd.Damage`'s guard at the level it actually sits at -- below
#   `AttackCommand`. Before it, charge 2 of a Bomb pile whose charge 1 had
#   killed the body still ran the whole reaction pipeline on the corpse, which
#   could consume an aura and splash off it. tier0's own overkill clamp meant
#   the DAMAGE was already 0; the reaction was not.
#   (f) THE CONSEQUENCE THAT IS NOT A CARD, AND IT IS NAMED RATHER THAN LEFT
#   TO BE FOUND: EB-118 (1)'s bomb-placement chooser is SUPERSEDED for
#   `target: enemy`. `place_bomb` is one of the emitter's `AIMING_OPS` -- All
#   of My Treasures emits six `BombPower.Place` calls on the ONE
#   `cardPlay.Target`, Trip Wire puts its bomb and its Weak on that same body
#   -- so a per-bomb chooser is three independently picked destinations where
#   the mod has one, which is the divergence restated rather than the cure, and
#   the row struck per-op aim hooks from its own scope for exactly that reason.
#   `_op_place_bomb` no longer calls `pilot.policy.bomb_placement_target`.
#   NOTHING IN `policy.py` IS EDITED: `bomb_placement_score`,
#   `bomb_placement_target` and all eight of their weights stand at their
#   shipped values, as the destination-scoring machinery the severed question
#   will need. `P` IS UNTOUCHED ON ITS OWN GROUND -- no pilot heuristic and no
#   weight value moved -- and the instrument movement that follows is declared
#   at the end of this block.
#   (g) NOTHING WAS BUILT IN THE MOD AND NOTHING NEEDED TO BE. C# already
#   binds; it is the reference. `klee-mod/` is byte-identical across this
#   landing and `gen_roster_cards.py --check` is unaffected -- no sheet row and
#   no emitter vocabulary moved.
# WHAT IS ARCHIVE. EVERY COMBAT NUMBER FOR EVERY CHARACTER, INCLUDING THE
# ANCHOR'S. The ruled scope is 28 live cards spanning `klee`, `furina`,
# `kokomi`, the `inazuma-companions` and `colorless_event` sheets,
# `ref_ironclad`'s STARTER (`bash`), `ref_silent` (`neutralize_like`), and both
# `real_*` pools (six `ic_*` rows and seven `si_*` rows); (b) reaches seven
# more (`matinee_performance`, `ic_twin_strike`, `ic_fight_me`, `ic_dismantle`,
# `ic_fiend_fire`, `ic_spite`, `si_skewer`). THE ANCHOR RENORMALISES TO 3.0 ON
# EVERY AXIS BY CONSTRUCTION and that is exactly why this has to be said out
# loud: `(ref_ironclad, starter)` under `generic` is the DIVISOR in
# `axes.normalize`, its combat behaviour moved -- `bash`'s Vulnerable now lands
# on the body the 8 killed instead of walking to a living bystander, which is a
# live debuff REMOVED and a real strength loss, not a rounding difference --
# and so every ratio taken against the old anchor is a C17-world ratio.
# tier-0.5 numbers are archive by the same reach. Archive banners go where the
# numbers are published; nothing is rewritten (R101b).
# `RT`, `D` and `P` ARE UNTOUCHED, each on its own ground. No run-layer content
# moved (`RT`). No drafter code and no dial value moved (`D`), and no drafter
# PRICE moves either -- `draft._static_power` reads printed rows, and no
# printed row changed; the binding is a resolution-time fact the offer scorer
# has never modelled. No pilot heuristic and no weight value moved (`P`); both
# EB-118 activation switches keep the values Phase 2 left them at.
# THE INSTRUMENT MOVEMENT IS (f)'s AND IT IS DISCLOSED, NOT BALANCED AGAINST.
# `tier05/pilot_weight_sweep.discover_scope` derives the 2A pair's sweepable
# surface from the ENGINE's own call sites, so with `_op_place_bomb` no longer
# asking, its entry points go from `("bomb_placement_target",
# "exhaust_victim")` to `("exhaust_victim",)` and the eight `BOMB_*` weights
# leave `pair_own`. THAT NARROWING IS R33 DOING ITS JOB rather than damage: a
# sweep that kept them would report a null on every cell and could not show
# the swept constant was READ even once, which is the exact failure R33's
# exercise counter exists to catch. The `bomb-primary` / `bomb-secondary`
# cells stop being carriers of a gated decision and now read like the Furina
# null control; `CELL_SPECS` still calls them `measure` and they are carriers
# again only if the severed destination-scoring question is answered by
# putting a chooser back at BIND time.
# `sparkly_explosion`'s DIAGNOSTIC CAVEAT IS CLEARED BY THIS LANDING. C17 (a)
# declared its simulated number DIAGNOSTIC until this repair landed, on the
# ground that tier0 could scatter what the mod concentrates and that the card
# is the first shipped body where an earlier op routinely KILLS the aim. That
# is now false: the gather, the detonation and the 14 resolve onto one
# creature, pinned by this row's first acceptance test. The C17 paragraph
# stands as published and is NOT rewritten (R101b) -- this is where the caveat
# is lifted. The two editable copies of it are updated in place:
# `docs/klee-cards.yaml`'s `sparkly_explosion` comment and `EB-118`'s item (d)
# in `BACKLOG.md`.
# ONE QUESTION IS LEFT OPEN ON PURPOSE AND IS NOT GUESSED AT. `_op_swirl`
# re-aims a single-target Swirl at whichever living body carries an aura when
# the bound aim carries none. That is an aim RE-TAKE, which Q1(b) forbids --
# and it is also a documented tier0 aim choice, which the same row says binding
# does not overturn. Five of the six `swirl target: enemy` rows carry no second
# aimed op, so deleting the branch would read them as blank whenever the aura
# sits off the lowest-HP body: a NEW divergence from a mod a human aims by
# hand. Moving it into the bind instead would bind `sayu_yoohoo_windwheel`'s
# DAMAGE to the aura'd body, which is card-shape-dependent aim policy nobody
# ruled. So it is left standing, ONE of the 28 in-scope cards is still
# scattering, and the state of the question is pinned by a strict xfail
# (`test_eb136_same_target_binding.py::test_swirl_aim_retake_is_unruled`).
# NO STANDING BASELINE IS OWED AT THIS BUMP, and that is R207 as agreed at the
# ruling rather than a deferral: `W3`'s single public window carries the single
# public standing read, this lands BEFORE that read so the read absorbs the
# movement, and the disclosure owed here is a commit-hash scratch before/after
# carried in PR text and published nowhere. NO CONNECTIVITY READ AND NO
# REGISTERED EXPERIMENT ATTACH TO THIS WINDOW EITHER: nothing here is graded
# against a committed prediction.
# ---------------------------------------------------------------------------
# CONSTANTS_VERSION 19 -- the EB-118 PHASE-3 WINDOW 3 CARD-BODY PASS (R211,
# [USER] 2026-08-25 -- the W3 ratification slate), landed 2026-08-25. ONE
# window, EIGHT sheet rows, ALL THREE characters: five NEW rows and three
# REWRITES THAT KEEP THEIR CARD IDS. Ground is R179/M15 as written -- printed
# effects and printed numbers move on every sheet -- with R202's role /
# archetype amendment reached once, on the row that leaves a clone cluster.
# Enumerated the way C13-C18 enumerate their own, so that the world a C19
# number was taken in is readable from the stamp.
#   (a) W3-KLEE, THREE NEW UNCOMMON SKILLS, and they are the first rows on any
#   sheet to print `spend_spark`. `powder_charge` (spend 2, `detonate
#   target: enemy bonus: 4`, upgrade `{bonus: +3}`), `hold_the_line` (spend 2,
#   Block 5, `conditional if: enemy_intends_attack then: [block 6]`, upgrade
#   `{conditional_block: +3}` raising BOTH halves), `smoke_and_sparks` (spend
#   2, Vulnerable 3, upgrade `{vulnerable: +1}`). The ratified floor of
#   three-or-four sinks is met AT THREE: a fourth candidate was cut at the
#   ruling. ALL THREE ARE `role: glue`, so NO PAYOFF COUNT MOVES ANYWHERE --
#   what moves is sub-pool size, and `klee/spark`'s payoff DENSITY falls 24%
#   -> 21% as three glue cards join and no payoff does. That is a DISCLOSURE,
#   not a breach: `klee/spark` is not on R199's ruled conversion priority
#   list. It is nevertheless the second consecutive window in which that arm
#   thins, and the sheet says so beside the rows.
#   THE SPARK PRICE IS AT TOP LEVEL ON ALL THREE and that is structural, not
#   stylistic: `combat.spark_cost` reads the top-level op and the playability
#   gate refuses the play below the bank, so a `spend_spark` nested in a
#   branch would let the payoff fire unpaid.
#   ALL THREE SIMULATED NUMBERS ARE DIAGNOSTIC and the reason is declared here
#   rather than discovered later: THE PILOT HAS NO HOLD-VERSUS-SPEND TERM for
#   Sparks -- there is no `spend_spark` branch anywhere in
#   `tier0/pilot/policy.py`, and `PILOT_SPARK_VALUE` is read only on GAIN -- so
#   the sim measures a pilot that spends the bank the moment a sink is legal
#   and never banks toward the free Attack. `powder_charge` carries a SECOND,
#   separate reason that C18 above does NOT clear: R210 took full parity on
#   which effects SHARE a target and explicitly severed which target is RIGHT,
#   so tier0 still aims at the lowest-HP living enemy -- and if that enemy
#   holds no Bombs this card silently does nothing having already spent the
#   Sparks, where a player aims at the pile. `smoke_and_sparks` takes a milder
#   form of the same (the sim debuffs the weakest where a player debuffs the
#   dangerous one) and is skewed rather than hollow; `hold_the_line` aims at
#   nothing and is clean on that axis.
#   (b) W3-FURINA, TWO NEW UNCOMMON SKILLS. `change_the_bill` (`salon_rotate`
#   + `salon_perform` + Block 3, upgrade `{block: +3}`) is the first sheet row
#   in the repo to print EITHER Salon verb -- both have been built and unused
#   since Phase 2 -- and its Block is load-bearing rather than decorative: at
#   cost 0 with the two verbs alone the card prices 1.5000 and its natural
#   upgrade (a draw) moves the price by ZERO, because draw is a dead dial.
#   `take_it_from_the_top` (Block 5 + `conditional if:
#   spotlight_moved_this_turn then: [damage 10 target: enemy]`, upgrade
#   `{conditional_damage: +4}`) is the route-(b) Spotlight reward. `role:
#   payoff` and `archetypes: [spotlight]`, so `furina/spotlight` payoff supply
#   goes 5 -> 6 over a sub-pool 17 -> 18 -- Spotlight is FOURTH in the ruled
#   priority order, so that is a disclosure item and not a breach. BOTH ROWS'
#   NUMBERS ARE FLOORS AND A NULL RESULT ON THEM IS NOT EVIDENCE: the pilot's
#   scorer reads neither the Salon state nor the Spotlight branch, so it
#   under-plays both.
#   (c) W3-KOKOMI, THREE REWRITES, AND THE POOL STAYS AT 76 ROWS AND AT THE
#   SAME 76 IDS. `pearl_barrage` stops reading the exhaust PILE and reads THE
#   CARD YOU CHOSE: `exhaust_from 1 chosen` + `damage amount_formula {base: 5,
#   per: 3, count: exhaust_selection_cost} target: enemy`, upgrade
#   `{formula_per: +1}` -> `{formula_base: +3}` (the retired delta had no pile
#   slope left to bump). Its ladder is 5 / 8 / 11 over the WHOLE live range,
#   because Kokomi's sheet has no card above cost 2.
#   `shell_of_sanctuary` KEEPS ITS ID and becomes "Salvage the Line" -- the
#   R69 pattern, the identifier frozen and the display string renamed, with
#   the retired string burned in `docs/reserved-card-names.txt`. Cost 2 -> 1,
#   `block 11` -> `draw 1` + `recall_to_draw 1 from: exhaust` + `gain_charge
#   2` + `block 4`, `exhaust: true`, `archetypes` [generic] -> [priest,
#   assist] (R202's amendment, the one label move in this window), `role:
#   glue` unchanged. ITS UPGRADE SHEET IS NOT EDITED AT ALL: the live delta
#   was already `{block: 4}`, which is exactly the ruled 4 -> 8.
#   THE EFFECT ORDER IS THE RULED CORRECTION AND IT IS LOAD-BEARING -- traced
#   on the real resolver, recall-then-draw puts the rescued card at draw-pile
#   index 0 and the draw pops index 0, so the rescued card lands STRAIGHT IN
#   HAND, defeating the rule that a retrieved card goes to the top of the draw
#   pile and never to hand. It is ALSO the repo's FIRST Exhaust-retrieving
#   row, so `lint_recall_exhaust`'s card-shape leg stops being vacuous; the
#   shape rules are met by construction (Uncommon, and it Exhausts itself).
#   `the_tide_remembers` KEEPS ITS ID and becomes "Tide of Names":
#   `exhaust_from 1 chosen` + `damage amount_formula {base: 5, per: 2, count:
#   exhaust_selection_cost} target: all_enemies`, upgrade `{damage: +3}` ->
#   `{formula_base: +2}` (the retired delta has no matching effect on the new
#   body). Tags `[priest, generic]` and `role: payoff` DO NOT MOVE, so
#   `kokomi/priest` payoff supply holds at 12 -- an earlier draft retagged it
#   `commander` and said in terms that it did so to keep the count down, which
#   R199 guardrail (1) forbids outright, and R211 refused that. Its ladder is
#   5 / 7 / 9, WIDE and SHALLOW where Pearl is AIMED and STEEP: two cards
#   reading the same count with the same shape would be a clone.
#   ITS NUMBER IS A FLOOR: the pilot cannot see this card's payout when it
#   decides whether to PLAY it, so it scores the row against an EMPTY
#   selection, base only.
#   TWO STANDING DEBTS MOVE, and both were measured rather than hoped. The
#   flat-Block clone cluster goes 8 -> 7 as `shell_of_sanctuary` leaves it --
#   the first movement on that curated debt this workstream has produced --
#   and the exhaust-pile reader family goes 5 -> 3 as both rewrites drop their
#   pile reads, which is what completes R208's `damage@one~` five-to-two.
#   `kokomi` near-duplicates hold at 29 against an untouched limit of 30.
#   (d) THE STANDING READ THIS WINDOW OWES IS DIAGNOSTIC-SCOPED AND IS NOT THE
#   PHASE-4 MILESTONE TABLE (R211 item 7). The three reasons are (a)'s
#   hold-versus-spend gap, (b)'s scorer blindness on both Furina rows, and
#   (c)'s scorer blindness on Tide of Names. The milestone read follows in a
#   later window, when those caveats clear. Per-character attribution for this
#   window is by commit-hash scratch comparison (R207) and is not citable the
#   way a stamped table is.
# ---------------------------------------------------------------------------
# CONSTANTS_VERSION 20 -- EB-139's SWIRL AURA-AWARE BIND (R211, [USER]
# 2026-08-25 -- semantics ratified there, implementation deferred to its own
# window), landed 2026-08-26. THE ONE QUESTION C18 LEFT OPEN, CLOSED. Not a
# sheet window and not a card-body pass: no printed number, no label, no
# upgrade delta and no dial value moves here either. What moves is HOW THE
# RESOLVER AIMS, which is C18's class exactly, and it takes C18's letter for
# C18's reason -- R179/M15, a change that materially alters what a card does to
# a board is a `C` bump whether it is spelled in a sheet row or in the engine
# that reads one. The reviewer's "`P` window" label on the row was a
# MIS-FILING and is corrected here: no pilot heuristic and no weight value is
# touched.
#   (a) THE RULED SEMANTICS, AND THE SEAM THEY LIVE AT. For MANUALLY-MODELLED
#   play, if ANY LIVING enemy carries an aura at card-play construction, the
#   WHOLE CARD binds to the LOWEST-HP AURA-BEARING enemy; otherwise the normal
#   lowest-HP bind. It is built in `effects.bind_card_aim` -- the C18 seam, the
#   first line of a play -- and NOT inside `_op_swirl`, which is the whole
#   content of the answer: an aim taken at the bind is one creature for the
#   whole play, where the re-take it replaces could hand a card's damage to one
#   body and its Swirl to another.
#   (b) WHY A SWIRL AND NOT THE BOARD. This is not a board-wide aim rule and
#   the negative pins hold it to that (`test_eb139_swirl_aura_bind
#   .test_a_card_with_no_swirl_ignores_the_auras_on_the_board`). A Swirl's
#   entire payload IS the aura it lands on -- aimed at an auraless body it does
#   nothing at all -- so an aimed Swirl is the one card shape where the mouse
#   pick a human makes is READABLE OFF THE BOARD rather than a matter of taste.
#   Every other card keeps the documented lowest-HP aim R210 declined to
#   re-open, and destination SCORING stays severed: nothing here scores a
#   destination, it reads one predicate off the board. The gate
#   (`_card_swirls_at_aim`) walks the whole effect tree the way
#   `_card_aims_at_enemy` does, and a `target: all_enemies` Swirl does NOT gate
#   it -- it hits the whole board and has no aim to correct.
#   (c) FORCED-RANDOM AUTOPLAY IS UNCHANGED AND RECEIVES NO CORRECTIVE RE-AIM.
#   The random branch is FIRST in `bind_card_aim` and that order is the ruling:
#   a free play has no human at the mouse, so modelling one there would hand
#   Havoc/Cascade a judgement the mod never gives them -- the same argument
#   that put the roll there in C18. The roll is still one draw per aiming card.
#   (d) WHAT IS ARCHIVE, AND IT IS NARROWER THAN THE STAMP SUGGESTS. Six live
#   rows carry an aimed Swirl, ALL of them companions -- no character sheet
#   prints one: `sayu_yoohoo_windwheel` (Inazuma), `lynette_enigmatic_feint`
#   and `lynette_astonishing_shift` (Fontaine), `sucrose_gust`,
#   `sucrose_astable` and `prune_witch_hunt` (Mondstadt, the last
#   `personal_pool: klee`). The list is DERIVED, never listed -- a seventh
#   aimed Swirl fails `test_the_live_sheets_carry_exactly_the_enumerated
#   _swirl_rows` and this paragraph gets corrected rather than silently
#   outgrown. The ARMS are every arm that draws companion rewards: all nine
#   character arms (`klee` demolition/spark/reaction, `furina`
#   salon/spotlight/fanfare, `kokomi` priest/commander/assist). FIVE OF THE SIX
#   ROWS MOVE NO NUMBER AT ALL, and that is demonstrated rather than hoped:
#   each of the five puts its Swirl FIRST and carries no second aimed op
#   (block, draw, burst energy, a Spark rider, an `all_enemies` damage row), so
#   the creature the bind now names is byte-for-byte the creature the old
#   re-take computed -- the same `min(bearers, key=hp)` on the same board -- and
#   no enchantment rider can widen that, the three shipped riders being
#   `damage target: self`, `draw` and `energy`. THE OBSERVABLE MOVEMENT IS ONE
#   CARD: `sayu_yoohoo_windwheel`'s `damage 4`, which C18's own block named as
#   the single row still scattering, now lands on the body its Swirl lands on.
#   THE ANCHOR DOES NOT MOVE, AND THAT IS THE DIFFERENCE FROM C18. C18 had to
#   declare the anchor archive because `bash` sits in `ref_ironclad`'s starter
#   and the anchor is the DIVISOR in `axes.normalize`. Nothing here reaches it:
#   `ref_ironclad`'s pool is starter+package (`rewards.character_pool`) and
#   prints no Swirl, and `ref_ironclad` / `real_ironclad` / `real_silent` draw
#   no companion REWARDS at all (`rewards.NO_COMPANION_CHARACTERS`). VERIFIED
#   RATHER THAN ASSERTED: the `ref_ironclad/starter` scorecard was run either
#   side of this change and is IDENTICAL -- all seven axes, all seven raws, all
#   six battery rows, the curve exponent, the pressure delta and the regret
#   rate. So every ratio taken against the C18 anchor is still good, and only
#   the numerator arms above are archive. The one door left open is the SHOP
#   companion channel, which is not gated by `NO_COMPANION_CHARACTERS`: an
#   anchor's tier-0.5 run can BUY a companion, so `ref_ironclad/generic` at
#   tier 0.5 is not immune BY CONSTRUCTION the way the tier-0 scorecard is. It
#   did not fire in the scratch below, and it is written down here rather than
#   left to be found.
# `RT`, `D` and `P` ARE UNTOUCHED, each on its own ground. No run-layer content
# moved (`RT`). No drafter code and no dial value moved (`D`), and no drafter
# PRICE moves either -- `draft._static_power` reads printed rows and no printed
# row changed; `STATIC_SWIRL_VALUE` is unmoved at 1.5, because what a Swirl is
# WORTH did not change, only which body it lands on. No pilot heuristic and no
# weight value moved (`P`): `policy.reaction_potential` already modelled a
# single-target Swirl as aura-aware, so the estimate the pilot makes and the
# resolution it gets have moved TOWARD each other rather than apart, and no
# weight was needed to do it.
# NO STANDING BASELINE IS OWED AT THIS BUMP (R207), on the same ground C18
# stood on and one step further: the movement is one companion row on nine
# arms, no pending decision is waiting on its size, and the anchor -- the thing
# a re-baseline exists to re-fix -- provably did not move. The disclosure owed
# here is a COMMIT-HASH SCRATCH before/after, carried in PR text and published
# nowhere, which is not citable the way a stamped table is. A SECOND C-CLASS
# CHANGE MAY JOIN THIS SAME WINDOW BEFORE ANY READ IS TAKEN -- the ruled
# "Sweet Dreams" (`elemental_ecstasy`) body, R189/R205 -- and R207 is what
# permits that: where nothing turns on attributing a movement to one edit,
# several may share a window and the stamp labels the world. NO CONNECTIVITY
# READ AND NO REGISTERED EXPERIMENT ATTACHES TO THIS WINDOW: nothing here is
# graded against a committed prediction.
# ---------------------------------------------------------------------------
# v21 (2026-08-30, EB-219). PRUNE'S SPARKS MOVED OFF HER FACE AND INTO KLEE'S
# KIT, at parity. `prune_witch_hunt` printed `gain_spark 1` inside a
# `reaction_triggered_by_this` conditional AND `gain_spark 1` unconditionally at
# top level; both ops are GONE from the sheet, and the grant is now the kit
# declaration LAW:145 requires (`KLEE_COMPANION_SPARK_*`,
# `effects.klee_personal_companion_spark`, C# `KleeCompanionSpark`).
#
# WHY A BUMP AT ALL, GIVEN THE PARITY. The four yields do not move -- 1 / 2 / 2
# / 3, asserted case by case in `tier0/tests/test_eb219_prune_kit_spark.py` --
# so on outcomes this is as close to a no-op as a sheet edit gets. It is stamped
# anyway for two reasons. (1) THE SHEET MOVED, and LAW's material-edit clause
# names "effect-number changes" without an exemption for edits that restore the
# number elsewhere; an unstamped world whose sheets differ is exactly the
# indistinguishability the clause exists to prevent, and `SHEET_DIGEST` below is
# re-pinned in this same commit. (2) ONE BEHAVIOUR REALLY DOES DIFFER, and it is
# written down rather than left to be found: a REPLAYED Prune (Study Buddy,
# `replay_next_companion`) used to resolve her face twice and mint twice, up to
# 4 Sparks base and 6 upgraded from one card play. The kit mints ONCE PER PLAY,
# so that combination now pays half. That is not an oversight -- LAW:145 bounds
# "the amount generated per Companion play", and a per-play bound a replay can
# double is not a bound -- but it is a world difference and it is what this
# integer labels.
#
# `RT`, `D` and `P` ARE UNTOUCHED, each on its own ground. No run-layer content
# moved (`RT`). NO DRAFTER PRICE MOVES (`D`), and this is arithmetic rather than
# hope: `draft.STATIC_SPARK_VALUE` is 0.0 -- a `gain_spark` has been priced at
# ZERO since the v3 flat-proxy sweep -- so deleting two of them from a printed
# row changes her offer score by exactly nothing, and the kit's mint is not a
# printed row for the drafter to read at all. No pilot weight moved (`P`).
# NO STANDING BASELINE IS OWED AT THIS BUMP (R207): the movement is one
# companion row, at parity on every case a measured arm can reach, no pending
# decision waits on its size, and no registered experiment attaches to this
# window.
# ---------------------------------------------------------------------------
CONSTANTS_VERSION = 21

# Correction D (2026-08-26). The content sheets carry no version integer of
# their own, and a sheet edit moves every measured arm: a pool that grows by
# three Uncommons renumbers the shelf, because `rng.choice` maps the same
# draw to a different card. This is one digest over `docs/*-cards.yaml` +
# `docs/*-companions.yaml`, gated by `tools/lint_sheet_stamp.py`, so a sheet
# edit that bumped no stamp FAILS instead of being noticed five re-stamps
# later. It is a fingerprint, not a version -- it says only that the sheets
# moved, and the bump the move earns is still a judgement. Re-pin with
# `python tools/lint_sheet_stamp.py --update`, in the SAME commit as the
# sheet edit.
#
# R226 (2026-08-30) re-pins it for a COMMENT-ONLY edit: the R80 standing-law
# header block in `docs/kokomi-cards.yaml` was rewritten to the amended Charge
# rule, marked PROSPECTIVE. No row, no number and no field moved, so
# `CONSTANTS_VERSION` does not bump -- the digest is a fingerprint over bytes
# and the bytes include comments (R225 precedent).
SHEET_DIGEST = "12531a9826dc794b09b9c9e97ab8019d3626979b75127ecb6072109c3962d7d7"
# Ruling R2.3: the drafter MODEL has its own version stamp, same archive
# discipline as CONSTANTS_VERSION. v1 = plan-committed scorer with no
# power awareness (M5-M7 reports are its archive). v2 = M7 ruling R2:
# assigned adopts the hybrid experiment's damage/Block term plus the reaction
# weights pass. v3 = conservative Bomb/debuff proxies and safe conditional
# Block. A measured flat draw/resource proxy was rejected rather than folded
# into the stamp. v4 (2026-07-23) = retroactive stamp for two world changes
# that shipped unstamped: the pilot's per_aura tempo valuation (b8891b2 --
# changes elemental_ecstasy's in-combat scoring) and the drafter's
# STATIC_STRENGTH_VALUE / witchs_flame persistent-proc terms in
# tier05/draft.py (bab07b2). Numbers measured Wed 2026-07-22 before 14:01
# are v3-world. Never compare measurements across drafter versions without
# labeling them. v5 (2026-07-23, red-pen: the Ironclad-0.6% diagnosis) =
# the run-layer discipline pass, two changes stamped together because they
# were measured together as the "discipline" arm (§10.8.1): (a) assigned's
# late-run lean gate (draft.DRAFT_LEAN_CAP/DRAFT_LEAN_BLOCK_CAP -- past 15
# cards only Powers/tempo/Block, past 20 Powers+tempo only; adaptive
# unchanged), and (b) the rest policy's pre-fight lookahead
# (REST_PREFIGHT_HEAL_THRESHOLD: heal-first below 90% when the next node
# is an Elite/Boss fight -- both template rests directly precede E/B, and
# v4 smithed at ~48/80 HP into them). v4-world 3-act numbers (real_IC
# 5.4%) are archived in §10.8.1. v6 (2026-07-23, Salon-v2 rework batch,
# ratified direction): (a) all_enemies damage in the static scorer counts
# STATIC_AOE_MULT bodies (the §10.8.2 AoE-blindness finding), and (b) the
# lean gate gains the rare strong-pick escape hatch (DRAFT_LEAN_RARE_BAR)
# the v5 arm promised but never implemented. v5-world numbers (Klee 6.2%,
# real_IC 3.0%) are archived in §10.8.1's lever-world table.
# v7 (2026-07-24, Kokomi v0.2 sheet pass): conservative static proxies for
# her three verbs -- conscript, gain_charge, and Sly riders -- which the v6
# scorer read as literal zero (the §10.8.2 AoE-blindness class: a plan
# whose core verb scores 0.0 drafts like the Furina 0% diagnosis). Structural
# constants in tier05.draft (STATIC_SLY_SHARE / STATIC_CONSCRIPT_VALUE /
# STATIC_CHARGE_VALUE), deliberately unswept: any v6-world act number is
# incomparable with v7 output for Kokomi; Klee/Furina/Ironclad decks carry
# none of these ops, so their numbers do not move.
# DRAFTER_VERSION 8 (v0.4 O4 salvage): `_static_power` learns the new
# `summon_kurage` op, priced like Durin at ONE pulse (flat damage + Block,
# STATIC_PERSISTENT_PROC_SHARE) because the bank read is invisible at offer
# time. Only Bake-Kurage carries the op, so only Kokomi numbers move; any
# v7-world Kokomi act number is incomparable with v8 output.
# DRAFTER_VERSION 9 ("The Tide Turns", F-A7 -- NOT bookkeeping): the two
# branches that valued the retired grammar are gone (`_is_fanfare_converter`
# read fanfare_cost; `_reads_fanfare` counted raise_fanfare_cap as a read),
# and floor grants are valued in their place. A drafter that cannot see a
# floor grant would under-draft the new identity outright, so this bump
# carries real work. Only Furina rows changed; other characters do not move.
# DRAFTER_VERSION 10 (G-E1, "Ship What We Know", 2026-07-25): the fanfare
# limb of `core_complete` now requires at least one card that READS the
# meter. It previously asked only for generation coverage and floor
# coverage -- neither of which is a payoff -- so it declared the archetype
# ONLINE while the deck held, on measurement, 1.87 readers in 20 cards. The
# fanfare sprint's close-out registered a standing instruction that nothing
# be measured against that predicate until it was fixed; this is the fix.
# NOT bookkeeping: `core_complete` and `_core_progress` both feed
# `score_offer`, so a fanfare deck now advances its core (and takes the
# +3.0 core-advance bonus) on a reader it previously ignored. Only Furina
# fanfare rows move; every other archetype takes a different branch. Any
# v9-world fanfare number is incomparable with v10 output.
# DRAFTER_VERSION 11 (R83/R84, 2026-07-27): the generic-anchor
# discrimination pass -- GENERIC_PLAN_BONUS_MULT 0.25 / GENERIC_SKIP_
# THRESHOLD 1.5 / GENERIC_REDUNDANCY_PENALTY 0.0 (dead dial), all scoped
# to archetype == "generic". Only the two real anchors move (silent 23.3%
# -> 28.8%, ironclad 26.9% -> 33.3% act-1 clear); house plans draft under
# their own archetypes. RATIFIED as R84. NOTE: this stamp line landed one
# session late -- the scorer changed on 2026-07-27 but the stamp still
# read 10 until the R84 pass caught it. No experiment script ran in the
# gap; the review doc's own tables carry their protocol inline.
# DRAFTER_VERSION 12 (R84, 2026-07-27): the power-aware static term.
# `_static_power` learns permanent self Dexterity (STATIC_DEXTERITY_VALUE
# 2.0, the Strength mirror; Footwork taken 21% -> 74% against its +23.6
# lift, real_silent 28.8% -> 29.1%) and carries a measured DEAD DIAL for
# flat engine credit (STATIC_POWER_ENGINE_VALUE 0.0 -- hurt at every
# swept value; a flat credit cannot discriminate engines). Universal term:
# the only committed cards affected are ref-vocabulary
# (metallicize_like, accuracy_like); no Klee/Furina/Kokomi card prints an
# unpriced self-power, so house numbers do not move. Any pre-v12 anchor
# reading is incomparable with v12 output.
# DRAFTER_VERSION 13 (sim-hygiene sprint, 2026-07-29): the op repricing.
# `_static_power` hand-enumerated 10 of the engine's 56 registered ops; the
# other 46 were priced at EXACTLY ZERO at offer time, so a card whose whole
# printed text was `detonate`, `salon_bow`, `add_card`, `apply_aura`,
# `block_next_turn` or `copy_companion_in_hand` read as blank cardboard to
# every drafting arm. This is the SAME defect class as v6 (AoE blindness),
# v7 (Kokomi's three verbs), v8 (summon_kurage) and v9 (floor grants) --
# found four times, fixed four times one character's verbs at a time. v13
# prices the whole registry at once and lands `tools/lint_op_parity.py`, so
# the next registered op cannot arrive unpriced and silent.
# NOT bookkeeping, and the bump is not optional: `_static_power` feeds
# `score_offer` on EVERY arm, so every character's decks move. Every pre-v13
# roster number in this repo is incomparable with v13 output -- the D12/D13
# side-by-side table (both stamps labeled) is in
# docs/sprint-sim-hygiene-log-2026-07-29.md. All v13 values are PROPOSED and
# await [USER] red pen; the deliberate ZEROS (draw/energy/spark/burst,
# raise_fanfare_cap, crash_fanfare, strip_block, transform_in_hand,
# remember_card) each carry their measurement or their reason at the
# constant, in tier05/draft.py.
# DRAFTER_VERSION 14 ("Last Call" track E, 2026-08-05): the generic limb of
# `core_complete`/`_core_progress` now requires at least one on-plan PAYOFF,
# not just DRAFT_CORE_SIZE on-plan enabler-or-payoff cards. This is the v10
# fanfare fix applied to the branch it was never applied to: the fanfare
# close-out's diagnosis -- "it measures when the RESOURCE assembles, not when
# the DECK does" -- was true of the generic limb too, where four enablers and
# zero payoffs read ONLINE.
# NOT bookkeeping, and the bump is not optional: `core_complete` gates
# `model.py`'s plan-live divergence check and `_core_progress` feeds
# `score_offer`'s +3.0 core-advance bonus, so every arm that resolves to the
# generic limb -- assist, commander, demolition, generic, priest, salon,
# spark -- drafts differently. reaction, spotlight and fanfare keep their own
# limbs untouched. Every pre-v14 number for those seven archetypes is
# incomparable with v14 output; nothing has been re-measured here.
# The spotlight limb was examined and deliberately NOT changed -- see the
# track E report: whether `_is_spotlight_machinery` (enabler OR payoff) is
# "a payoff" is a definitional question, not a mechanical one.
# NOT BUMPED by the R121 SHIELD (2026-08-06, `Q19`), and the non-bump is
# FLAGGED rather than settled -- read this before quoting a `ref_ironclad`
# number. The shield (`draft._core_advance_view`) makes the +3.0 core-advance
# bonus blind to the reference anchor's instrumentation tags, which moves how
# ONE arm drafts, and the stamp law would ordinarily call that a bump. Three
# reasons it is left at 14 for a ruling to settle rather than taken here:
# (a) the tags that caused the movement (R118's 10.2 rider) landed WITHOUT a
# bump, so the shield restores the scorer to the behaviour v14 was stamped
# for rather than defining a new one; (b) R121's own execution order says
# "the sprint runs under D14", and a bump here would move the world the
# countersigned re-registration is pinned to; (c) 15 is already claimed by
# the staged spotlight-limb change (`EB-43`, `staged/d15-spotlight-payoff`,
# unmerged), which R121 fixes as step (5) of an order in which no step
# reorders -- taking 15 here would collide with it. Every other arm is
# untouched by the shield (`_core_advance_view` returns its argument
# unchanged when no anchor card is present), so no non-anchor number is
# affected either way. The shielded `ref_ironclad` reading tripped R121's
# stop-and-surface rule (it overshot the archived ordering) and was released
# for publication anyway on [USER]'s option (a), verbatim "Yeah, I think A)
# is defensible here." -- it is the row that stands in the quotable table,
# and it is an untagged-under-CONSTANTS-6 baseline, not a restoration of the
# archived CONSTANTS 5 number. See R121's 2026-08-06 addendum.
# Reasons (b) and (c) above are SPENT as of 2026-08-24: the payoff-reach
# sprint ran under D14 and was graded blind, and 15 is now taken by the
# EB-43 landing below, which is what (c) was reserving it for. The non-bump
# stands on (a) alone -- restores-not-redefines -- which is the ground R125
# carried the widened shield on (it rode RUNTEMPLATE v8, not a D bump).
# DRAFTER_VERSION 15 (R120 / 10.3, verbatim "Yes"; authored 2026-08-06 on
# `staged/d15-spotlight-payoff`, LANDED 2026-08-24 as EB-43): payoff-presence
# extends to the SPOTLIGHT limb -- the one branch v14 deliberately left
# alone, because enabler-vs-payoff machinery was a definitional question.
# [USER] answered it. `core_complete` and `_core_progress` gain a
# machinery-PAYOFF limb (bar ONE, every limb's standard), so `limelight` --
# the only enabler-role machinery card, the measured blast radius -- alone
# stops satisfying the limb.
# NOT bookkeeping, and the bump is not optional: `_core_progress` feeds
# `score_offer`'s +3.0 core-advance bonus, so every spotlight arm drafts
# differently, and every pre-v15 spotlight number is incomparable with v15
# output. SEQUENCING RAIL (R120, recorded in full, now DISCHARGED): this
# change sat staged until R121's six-step order reached step (5) -- the
# payoff-reach pre-registration was pinned to a drafter version, and landing
# D15 before its blind grade could have invalidated it. Step (4), the blind
# grade, landed 2026-08-24; this is step (5). The re-baseline stamp law asks
# for lands WITH this bump, in the same window and no other change beside
# it: `review/active/sitting-reads-2026-08-24.md`, the twelve-arm table at
# `RT12/D15/P7/C11`.
# DRAFTER_VERSION 16 (EB-118 Phase 2, 2026-08-24) -- THE INERT TERMS GO LIVE.
# No drafter CODE moved and no dial VALUE moved in this window. What moved is
# which rows the existing dials REACH, and two of those dials were carrying an
# explicit no-bump licence that said, in the file, exactly when it would be
# spent. Both are spent now.
#   (a) `STATIC_ETHEREAL_SHARE` (`tier05/draft.py`). The licence read: the
#   term is provably inert because no committed sheet row prints `ethereal:`
#   and the only cards the tag spelling reaches are Statuses, Curses and the
#   Spotlight token, whose rarities sit outside `RARITY_ODDS`. It named the
#   row that would end that -- "Phase 2's big_badda_boom" -- and that row is
#   now on `main`. A Common Klee Attack is offerable by every reward, shop and
#   Neow channel, so the multiplier now moves a drafted price:
#   `big_badda_boom` prices **8.0000 -> 4.8000** on its base face.
#   (b) `choose_one`'s MAX arbitration -- the same shape with a weaker
#   consequence. It was registered PROPOSED with "no shipped card is modal"
#   as its stated reason; `deep_breath` is modal now (2C's landed content,
#   C13 above). It moves NO number -- `draw` and `energy` are static zeros, so
#   `MAX(modes)` returns mode 1, which IS the body the card already shipped --
#   and it is in the window anyway, because what this stamp labels is which
#   terms a drafted price may depend on, not whether one sheet happened to
#   exercise them.
# RECORDED HERE AND EXPLICITLY NOT GROUND, because a reader comparing offer
# prices across this boundary will find FOUR Klee rows moved and needs to know
# why only one of the four is this stamp's business. The other three are door
# (a)'s distribution form, priced through dials that were already live:
# `place_bomb` costs `bomb_damage * amount * STATIC_BOMB_DAMAGE_SHARE` and is
# blind to `target`, so a row that printed several random bombs and now prints
# ONE on all enemies prices lower by construction -- `mine_toss` 6.5000 ->
# 4.0000, `jumpy_dumpty_mk2` 11.7500 -> 10.2500, `cluster_charge` 8.2500 ->
# 7.0000. That is a SHEET consequence and it belongs to C13. Every other
# changed row in both sheets prices identically across the window, checked:
# `explosives_workshop` is 0.0000 on the old body and on the new one, and no
# Furina row moved at all.
# THE R193 REPRICING TRIGGER FIRED AT THIS BUMP AND WAS EXECUTED. Its terms
# and the read's full arithmetic live at the constant in `tier05/draft.py`,
# beside the number they are a read of. In one line: the card prices 4.8000
# base / 8.0000 upgraded -- exactly the two figures the trigger note predicted
# -- the ratio is 0.600000 to six places, and R201's kill rider prices at ZERO
# on both faces, so this is the one-variable read the trigger was written to
# get. THE SHARE IS NOT MOVED HERE. The note offers a re-derivation OR a
# deliberate re-ratification and defines no formula for the first, and 0.6 is
# on the record as "a JUDGEMENT, not a sweep"; the ratify-or-move call is
# [USER]'s and is filed as QUEUE `M41`.
# ONE WINDOW, and each field that moves in it moves on its own ground: `C`
# 12 -> 13 above (the sheet and engine content), `RT` and `P` untouched.
# The re-baseline this bump owes is the same table C13 owes, and it is taken
# ONCE for both: `review/active/sitting-reads-2026-08-24-c13-d16.md`.
# DRAFTER_VERSION 17 (EB-118 Phase-3 Window 3, R211, 2026-08-25) -- ONE NEW
# DIAL AND ONE NEW PRICED CONDITION, and this is the first bump in the series
# where the drafter learns a COST rather than a value.
#   (a) `STATIC_SPARK_SPEND_COST = 2.5` (`tier05/draft.py`). The `spend_spark`
#   branch of `_op_price` used to read the dead GAIN dial with the sign
#   flipped and therefore priced at 0.0; it now reads its own live dial. THE
#   BUMP IS UNCONDITIONAL AND IT WAS OWED IN WRITING: that branch carried an
#   explicit no-bump licence saying the bump came due "at Phase-2 landing,
#   with the first sink card that prints it", and `powder_charge` is that card
#   (C19 (a) above). The value is DERIVED, not picked -- three routes, two of
#   them converging on 2.50 from opposite directions (what a Spark buys, and
#   what Klee's own sheet charges to acquire two of them) -- and taken at the
#   TOP of the convergent range under R194's direction rule, which requires
#   the residual error to UNDER-value the sink rather than over-value it. The
#   derivation, its sensitivity and the two discounts deliberately declined
#   live at the constant. **THE VALUE IS [USER]-HELD:** 1.5 is the defensible
#   smaller number in the same method, and `hold_the_line` scoring 0.00 in a
#   demolition draft -- below `DRAFT_SKIP_THRESHOLD` -- is the offer-screen
#   consequence that would argue for it.
#   (b) `spotlight_moved_this_turn` joins `STATIC_STATE_CONDITIONS` with
#   `STATIC_SPOTLIGHT_MOVED_SHARE = 0.167`, the measured spotlight-arm rate.
#   R211 ratified the RIDER but not the SHARE, so the value is chosen under
#   R194 again: 0.5 (Klee's precedent for a branch the player can arrange and
#   the drafter cannot see) and 0.167 are both defensible and 0.167 is the
#   more conservative; anything at or above 1.0 is not defensible, because at
#   share 1.0 `take_it_from_the_top` would price 15.00 base off a branch that
#   fires on a sixth of plays in its own arm. **ALSO [USER]-HELD.**
#   THE ARCHIVE SCOPE OF THIS BUMP IS UNUSUALLY SMALL AND THAT IS WORTH
#   STATING, because the reflex is to assume a dial move archives the world.
#   It is FOUR ROWS, three of them new. `STATIC_SPARK_SPEND_COST` re-prices
#   the three new sinks AND NOTHING ELSE -- R211 kept `STATIC_SPARK_VALUE` at
#   0.0, so all eleven shipped Klee Spark rows and `prune_witch_hunt` are
#   unchanged to four decimals, verified card by card and pinned in
#   `test_eb118_w3_bodies.py`. The rider re-prices `take_it_from_the_top` and
#   `curtain_cue` (0.0000 -> 0.4000); `directors_cut` does NOT move at any
#   share, because BOTH its branches pay in dead dials (energy and draw), and
#   that corrects an expectation the `EB-118` register row carried.
#   ONE WINDOW, and each field moves on its own ground: `C` 18 -> 19 above
#   (the eight sheet rows), `P` 9 -> 10 below (the chooser), `RT` untouched.
#   THE READ THIS BUMP OWES IS W3's SINGLE DIAGNOSTIC-SCOPED STANDING READ,
#   taken once for the whole window -- see C19 (e).
# DRAFTER_VERSION 18 (EB-28, 2026-08-26) -- THE SALON DEPLOY STOPS PRICING AT
# ZERO. ONE NEW DIAL, `STATIC_SALON_MEMBER_VALUE = 1.5` (`tier05/draft.py`),
# and one new inline branch in `_static_power`. `apply_power` is priced
# INLINE, and none of the inline branches named `power: salon_member` -- so a
# printed company scored exactly 0.0 and Furina's members were invisible to
# every plan except salon, where the ARCHETYPE term (not the static scorer)
# was paying for them. That is the blindness EB-28 names, and the bump is
# owed because a priced-op set that grows IS a DRAFTER_VERSION bump.
#   THE VALUE IS DERIVED, NOT PICKED, and unlike D17 it is a VALUE, so the
#   conservative end of the band is the BOTTOM rather than the top. Three
#   routes: (1) PERFORM PARITY -- `salon_perform` already prices exactly one
#   member tick, on demand, at 1.5, and a deploy delivers at least that; (2)
#   TICK PLUS EVENTUAL BOW -- the perform dial's own note calls a tick "the
#   smaller half of a member" and FIFO displacement at SALON_MEMBER_SLOTS = 3
#   eventually pays the bow, 1.5 + 2.0 -> 3.5; (3) KURAGE PARITY -- the
#   repo's other persistent per-turn engine credits ONE pulse at FACE value
#   ((KURAGE_PULSE_BASE + KURAGE_PULSE_BLOCK) * STATIC_PERSISTENT_PROC_SHARE
#   = 4.0), and a salon tick's face averaged over the three types is 4.33
#   less the 1-Encore upkeep -> 4.03. (2) and (3) converge on 3.5-4.0 from
#   opposite directions; (1) is the hard floor and IS WHAT IS TAKEN. The gap
#   is declared rather than hidden: everything above one tick is stage
#   occupancy and combat length, which an offer screen cannot see -- the same
#   argument `STATIC_SALON_ROTATE_VALUE` makes for pricing at zero, applied
#   to a value that can at least be bounded. **THE VALUE IS [USER]-HELD** and
#   lives in exactly one constant; 3.5 is the defensible larger number in the
#   same method.
#   ARCHIVE SCOPE: NINE ROWS, ALL FURINA, ALL SALON, and nothing else on any
#   sheet moves to four decimals (322 cards dumped before and after; the diff
#   is these nine and no others). Base -> upgraded: `dress_rehearsal`
#   0.0000/0.0000 -> 1.5000/1.5000; `endless_waltz` 0.0000/0.0000 ->
#   1.5000/3.0000; `full_ensemble` 0.0000/0.0000 -> 2.2500/4.5000;
#   `gentilhomme_usher` 4.0000/6.0000 -> 5.5000/7.5000; `grand_gala`
#   0.6000/1.0500 -> 3.6000/4.0500; `mademoiselle_crabaletta` 0.0000/0.0000
#   -> 1.5000/3.0000; `overflowing_hospitality` 1.4500/1.7500 ->
#   2.2000/2.5000; `salon_debut` 0.0000/0.6000 -> 1.5000/2.1000;
#   `surintendante_chevalmarin` 0.9000/1.5000 -> 2.4000/3.0000. FIVE of the
#   nine priced 0.0000 on their base face before this bump and FOUR of those
#   on both faces, which is the row's claim measured. TWO INVISIBLE UPGRADES
#   BECOME VISIBLE: `endless_waltz`
#   and `mademoiselle_crabaletta` each read identically on both faces before
#   (0.0000/0.0000) and now separate, the same defect `take_it_from_the_top`
#   was taken for at D17.
#   `RT`, `P` and `C` are all untouched: no run-layer, policy or sheet edit
#   rides with this. NO STANDING BASELINE IS OWED (R207) -- the movement is
#   nine rows on one character's one register, no pending decision needs a
#   table for it, and the `EB-28` row's own next step (the `S4-G7` remedy,
#   rebalancing the weak Furina plans) is a [USER]-owned design pass that
#   this fix precedes rather than answers.
DRAFTER_VERSION = 18
DRAFT_BLOCK_DENSITY_MIN = 0.18    # defense quota: draft block below this
DRAFT_DECK_SOFT_CAP = 22          # deck-size penalty beyond this
# Retuned 1.0 -> 0.5 by a 6-point sweep at 1000 runs/cell (M7 report).
# 1.0 was pessimal: it starved assigned mode of ~4 cards of deck volume vs
# adaptive, and most of the "assigned loses by 14.5" finding was that
# missing volume, not drafting skill. 0.5 matches deck sizes (~18.3 both)
# and is measurement-identical to 0.0, so it is not knife-edge -- while
# keeping skip a real pick for negative-scoring screens.
DRAFT_SKIP_THRESHOLD = 0.5
DRAFT_CORE_SIZE = 4               # generic archetype core (reaction has its
                                  # own rule, v1.9: 2 appliers + amp payoff)

# --- Tier 0.5 M6: adaptive policy + divergence (spec §4-§5) ---
ADAPTIVE_COMMIT_THRESHOLD = 0.40  # share of tagged cards before a deck counts
                                  # as committed to a shape; below it the deck
                                  # is classified 'goodstuff', which is itself
                                  # the finding divergence looks for.
DIVERGENCE_DOMINANCE_ALARM = 0.55 # alarm if one shape exceeds this share
DIVERGENCE_STARVATION_ALARM = 0.10  # alarm if an archetype falls below this
# Morning-triage ruling: the enforced relevance acceptance. Strict
# advances-the-live-plan >=35% per archetype -- the anti-brick floor the
# original 60-70% claim was spiritually about. Loose "worth engaging" is
# reported alongside, unenforced.
RELEVANCE_FLOOR = 0.35
ACHIEVABILITY_ALARM_FIGHTS = 7    # alarm if median time-to-online exceeds this
DRAFT_REGRET_SAMPLE = 0.10        # fraction of decisions re-scored post-run
# Its route twin (EB-16w): the fraction of ROUTE decisions `run_metrics.
# route_regret` re-prices in the ACT's end state (per-act since 2026-08-08 --
# elites_taken/rests_taken are act-local, so the run's end state leaked a later
# act's elites into an earlier act's gate). 1.0, not the drafter's 0.10,
# and the asymmetry is deliberate -- the drafter re-scores whole card offers
# inside the run loop thousands of runs deep, while a route re-price is one
# backward-induction pass over a 16-floor DAG per forked floor. Sampling it
# down would buy no wall clock worth having and would cost the seeded A/B its
# stability. Overridable per call (the sampler takes `sample=`).
# NOT a balance knob and NOT a CONSTANTS_VERSION bump: it is measurement
# machinery on a dedicated rng stream (model.py, +5e9), read-only over a
# finished run, so no run, deck, encounter or cell moves. Same reading the R67
# sweep-instrumentation block below took, and the criterion the v2/v4/v5 notes
# above wrote down is comparability -- nothing measured under C8 becomes
# incomparable because a road not taken got priced afterwards.
ROUTE_REGRET_SAMPLE = 1.0

# Powers that AMPLIFY reactions rather than causing them. Lives here rather
# than in tier05.draft because the content loader also needs it, and tier0 must
# not import tier05.
AMP_PAYOFF_POWERS = {"amp_reaction_up"}


# =========================================================================
# Sweep instrumentation (R67, 2026-07-26). NOT a balance knob -- machinery.
#
# The audit found two live sweeps tuning constants the engine never reads
# (SPOTLIGHT_SELF_MULT, FANFARE_DECAY_PER_TURN), each printing a set of
# guaranteed-identical rows that read as a null result about the knob. R33
# had already found the same class once (selector circularity), so R67
# graduated the KNOB_READS counter from an opt-in courtesy to a gate.
#
# The mechanism has to survive the R33 exercise-counter law: "the gate may
# not be satisfied by adding artificial reads." So it does not count reads
# the engine was asked to self-report. When the sweep harness arms a knob it
# REMOVES the name from this module's namespace and parks the value in
# _SWEPT, which routes every subsequent `C.<KNOB>` through the hook below.
# What gets counted is therefore the real attribute access from real engine
# code on the real read path -- a knob nothing reads records zero, and no
# amount of instrumenting the knob can change that.
#
# Every consumer in this repo reads knobs as module attributes
# (`from tier0 import constants as C`), which is what makes this total; a
# `from tier0.constants import X` would bind at import time and slip the
# hook. Do not introduce one.
#
# Arm and disarm only through tier05.sweeps -- never poke _SWEPT directly.
# =========================================================================
_SWEPT: dict = {}


def __getattr__(name: str):
    """Serve armed sweep values, counting each read (PEP 562).

    Python only calls this when normal lookup fails, so it costs nothing
    outside a sweep: unarmed knobs are ordinary module globals.
    """
    if name in _SWEPT:
        from tier0.engine import effects
        effects.KNOB_READS[name] = effects.KNOB_READS.get(name, 0) + 1
        return _SWEPT[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def _arm_knob(name: str, value):
    """Park `value` for `name` behind the read hook. Returns the original.

    Raises if the knob does not exist -- a typo'd knob name would otherwise
    sweep nothing at all and report a clean null, which is the exact defect
    this machinery exists to catch.
    """
    if name in _SWEPT:
        raise RuntimeError(f"{name} is already armed; nested sweeps of one "
                           f"knob cannot be unwound in order")
    g = globals()
    if name not in g:
        raise AttributeError(f"no such constant: {name!r}")
    original = g.pop(name)
    _SWEPT[name] = value
    return original


def _disarm_knob(name: str, original) -> None:
    """Restore `name` to a plain module global holding `original`."""
    _SWEPT.pop(name, None)
    globals()[name] = original

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
SPARKS_FOR_FREE_ATTACK = 3    # at 3 Sparks, next Attack costs 0
BURST_PER_SKILL_TAG = 5       # burst energy per Skill-tagged card played
BURST_PER_REACTION = 5        # burst energy per reaction triggered

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
KURAGE_DURATION = 1           # turns the jellyfish holds the field. Stacks
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
PILOT_WEIGHTS_VERSION = 2
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
# NO ENGINE RULE MOVED. No op was added, no power was added, no hook changed
# -- the three Phase-1 items that would have touched the engine are STAGED and
# not pulled (see the BACKLOG EB-118 row). This is a pure content window.
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
# published and nothing is rewritten (R101b).
CONSTANTS_VERSION = 12
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
DRAFTER_VERSION = 15
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

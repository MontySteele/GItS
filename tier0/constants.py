"""All tunable numbers for the Tier 0 simulator live here.

Nothing in engine/ may hard-code a balance number. If you need a new knob,
add it here with a comment. These are starting points, not gospel
(tier0-simulator-spec.md §0) — calibrate per §7, then freeze.
"""

# --- Core turn economy (StS defaults; spec §10) ---
BASE_ENERGY_PER_TURN = 3
CARDS_DRAWN_PER_TURN = 5
MAX_HAND_SIZE = 10

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
CATALYTIC_BURST_PER_REACTION = 5  # Catalytic Conversion bonus burst/reaction

# --- Furina: Spotlight (kickoff §3) ---
SPOTLIGHT_BASE_MULT = 1.5     # PLACEHOLDER (R33 veto, 2026-07-20): the
                              # pass-2 "MEASURED 1.0" record is STRUCK.
                              # E1's identical cells were guaranteed by
                              # selector v2 (companion branch
                              # unreachable at ~20 self cards vs 3-5
                              # card kits) -- the constant was never
                              # READ in any cell (exercise-counter law,
                              # DECISIONS 87). E1 re-scoped to a valid
                              # MEDIAN-DEPTH null only; never summarize
                              # it as "the knob is dead". 1.5 restored
                              # the pass-1 companion geometry against the
                              # then-current self rate of 1.25. R40 later
                              # moved self aim to 1.0 without changing this
                              # outward-Spotlight value.
                              # Window-zero forced-arm sweep {1.25,
                              # 1.5} decides (furina-pass3-rulings.md).
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
#    reaches SPOTLIGHT_COMPANION_DEPTH_MIN AND the stage holds a
#    crowd (>= SPOTLIGHT_COMPANION_MIN_ENEMIES living enemies);
#    otherwise self. W0 evidence: forced-companion at full-kit depth
#    is +12.5pt on attrition and -10pt on tank_boss — outward aim is
#    encounter-contingent, so the selector reads the fight, not just
#    the deck.
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
FANFARE_PER_ENCORE_GAINED = 1 # per point of Encore gained
FANFARE_PER_ENCORE_SPENT = 1  # per point of Encore spent
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
# (kickoff §4) is intact, not amended. Powers grant by rarity; the
# gain_fanfare_floor op exists so non-power cards can grant too, which is
# REQUIRED rather than optional -- a power-only rule structurally excludes
# the power-light archetype the mechanic was designed for (measured: the
# fanfare plan saw 6.7 floors/run against salon's ~51).
FANFARE_FLOOR_PER_POWER = 5       # common/uncommon Power played
FANFARE_FLOOR_PER_POWER_RARE = 8  # rare Power played

# --- Furina: Salon Members (kickoff §5; Salon v2 rework 2026-07-23,
# docs/archive/furina-salon-rework-plan.md -- numbers PROPOSED pending red-pen) ---
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
KURAGE_PULSE_PER_CHARGE = 4   # pulse gains this much damage PER POINT of
                              # Charge. v0.4 starter rework ([USER]): the
                              # read flips from a DIVISOR (+1 per 4 Charge)
                              # to a MULTIPLIER (+4 per Charge) — the design
                              # intent is "every Exhaust is worth about a
                              # Silent shiv toss", i.e. one banked point
                              # buys roughly one shiv of damage.
                              # WATCH THIS ONE. Charge is uncapped and never
                              # spent, so this term only ever grows, and at
                              # x4 a BASIC out-reads both rate-limited
                              # readers: at bank 10 the pulse is 44 vs
                              # nereids' (Rare) 17; at bank 25 it is 104 vs
                              # 24. That inverts the §2.2 reader hierarchy.
                              # Bracketed x1/x2/x4 in the v0.4 report.
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
RUNTEMPLATE_VERSION = 7
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
# Research + sources: docs/sts2-map-and-events-research.md §1. These replace
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
# --- §4.7 companion channel (R59/R61) -------------------------------------
# The shop's TWO colorless slots carry companions. Slot 1 draws the run
# character's home nation; slot 2 is wildcard. Both floor at Uncommon (R59):
# base StS2's slot 2 is a guaranteed Rare, so a wildcard at full reward odds
# (~60% common) would make the mod's shop WORSE than base at the one slot
# whose entire argument is that it is the premium paid channel.
SHOP_COMPANION_SLOTS = 2
# RARITY_ODDS renormalized onto {uncommon, rare} -- the Uncommon floor is the
# ruling, this is just what the surviving odds weigh once commons are cut.
SHOP_COMPANION_RARITY_ODDS = {"uncommon": 0.875, "rare": 0.125}
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
SHOP_COMPANION_PRICE = {"uncommon": 75, "rare": 150}
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
                                  # fraction, otherwise remove a card
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
CONSTANTS_VERSION = 3
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
DRAFTER_VERSION = 10
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

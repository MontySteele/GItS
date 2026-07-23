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
SPOTLIGHT_SELF_MULT = 1.0     # Furina pays no hidden baseline tax: self aim
                              # still drives Ovation/Fanfare, while numeric
                              # empowerment is reserved for companions.
SPOTLIGHT_GUEST_CAST = "__guest_cast__"  # all Companion cards share the light
# Selector heuristic version (instrument stamp, the A6-v2 pattern —
# never compare selector versions unlabeled):
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
SPOTLIGHT_SELECTOR_VERSION = 5
SPOTLIGHT_CARDS_PER_TURN_CAP = None   # schematized but OFF (kickoff §3.2):
                              # turns on only if Tier 0 shows the rate
                              # asymmetry alone fails the §6 criterion.
                              # When set: empowered plays per turn beyond
                              # the cap resolve at printed numbers.

# --- Furina: Encore & Fanfare (kickoff §4) ---
# Encore is unbounded per-combat (v1.6) -- no cap constant by design.
FANFARE_CAP_FRACTION = 0.5    # Fanfare cap = fraction of maxHP.
                              # RATIFIED (R17, 2026-07-20): the sweep
                              # brackets it (0.25 cripples punisher at
                              # 2.4%, 0.75 overheats at 63%). First-order
                              # dial -- re-check under R16 at pass 2
                              # (Ovation economics shift with
                              # card-mediation).
FANFARE_PER_HP_LOST = 1       # per point of true HP lost
FANFARE_PER_ENCORE_GAINED = 1 # per point of Encore gained
FANFARE_PER_ENCORE_SPENT = 1  # per point of Encore spent
FANFARE_PER_SPOTLIGHT_CARD = 2    # the Ovation merge: per Spotlighted
                              # card played. NO passive per-turn accrual
                              # constant exists; do not add one (§4).

# --- Furina: Salon Members (kickoff §5; sheet pass 1) ---
# The oz_summon rails with Defect-style fixed slots: each active member is one
# start-of-turn Hydro tick. Overflowed deployments take an immediate stronger
# final bow. A tick that can pay Encore deals full damage; a dry tick never
# overdraws HP and instead deals three-quarter damage.
SALON_MEMBER_DMG = 4          # per-member tick damage (v0.2: 3->4 -- her
                              # signature engine may out-tick Oz's 3; the
                              # upkeep cost is what Oz doesn't pay)
SALON_MEMBER_SLOTS = 3        # Defect-orb shape: fixed active company
SALON_REPLACE_NUMERIC_MULT = 2  # draw/Encore/power/etc. on replacement
SALON_REPLACE_DAMAGE_MULT = 3   # final-bow damage and Block on replacement
SALON_TICK_ENCORE_COST = 1    # Encore drained per member tick
SALON_DRY_DAMAGE_MULT = 0.75  # no Encore: 3 vs the paid tick's 4 damage;
                              # never true-HP loss
SALON_TICK_BURST = 2          # burst energy per member tick (her particle
                              # economy leans on Salon application, §1)
BURST_PER_ENCORE_SPENT = 1    # burst energy per point of Encore spent
                              # (the other half of her particle economy)

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
PILOT_REGRET_SAMPLE_RATE = 0.01

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
# v3 DELIBERATELY BREAKS v2's "fight count (11) and screen count (10)
# UNCHANGED" promise -- the whole point of the rework is 11 fights -> 7 so
# per-fight effects (Burning Blood, future per-fight relics) read correctly.
# Draft-economy numbers are therefore NOT comparable across v2/v3.
# v2 = "NNNENRNNENRNRB" (11 fights, 3 rests incl. guaranteed pre-boss): the
#      archive world of the Furina sprint-1 and Klee pass-4 reports.
# v1 = "NNNENRNNENRNB"  (11 fights, 2 rests): the M5-M8 archive world.
RUNTEMPLATE_VERSION = 3
RUN_NODE_TEMPLATE = "NNNRETN$ERB"

# --- Tier 0.5 economy (run-model rework §5; defaults RATIFIED §8) ---
GOLD_START = 99                  # StS default starting gold
GOLD_INCOME = {"N": 10, "E": 25, "B": 40}  # per WON fight, by node tier
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

# R7 directive 2: the second knob of the 2D rest-economy sweep. Scales
# enemy ATTACK amounts in plain normal-pool fights only (not E/B/BC --
# those are calibrated checks) to probe whether the 95%-of-rest-arrivals-
# under-danger finding is a template attrition artifact. 1.0 = measured
# reality of the battery statlines; the sweep varies it, the stamped
# default does not move without a ruling.
NORMAL_ATTRITION_SCALE = 1.0
REST_HEAL_FRACTION = 0.30         # rest option A: heal 30% of max HP
REST_HEAL_THRESHOLD = 0.65        # rest policy: heal below this HP
# M7: below DANGER always heal; between DANGER and HEAL_THRESHOLD an
# on-plan smith outranks the heal (the classic rest-vs-smith call). At
# 0.65 the heal branch swallowed every rest of a bruised run and the
# third option was dead by construction -- measured: 0 upgrades in 30
# demolition runs.
REST_SMITH_DANGER = 0.40
                                  # fraction, otherwise remove a card
PUNISHER_LITE_SCALE = 0.70        # normal-pool punisher at 70% statline
ATTRITION_LITE_HP = 45            # normal-pool attrition: ONE 45 HP unit
NORMAL_POOL_WEIGHTS = {           # weighted normal-encounter pool
    "swarm": 1.0, "attrition_lite": 1.0, "punisher_lite": 1.0}

# Triage ruling 3b: ONE number per node-tier standing in for the missing
# upgrades+relics power growth — NOT a model of them. Grid-searched on the
# REF_IRONCLAD anchor only, until anchor run completion hit 45%+-10, then
# frozen (same behavioral-calibration method as the M2 battery). Applied
# to enemy hp + attack damage in tier05 node encounters ONLY; the Tier 0
# battery is untouched.
# FROZEN 2026-07-19: anchor completion 47.9% at 1000 runs. Normals kept
# at 1.0 — only the checks calibrated as full-HP solo gates (punisher,
# tank_boss) get compensated in run context.
PROGRESSION_GAP_COMPENSATOR = {"normal": 1.0, "elite": 0.8, "boss": 0.7}

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
NATION_WEIGHTS = {"mondstadt": 1.0, "fontaine": 1.0}

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
CONSTANTS_VERSION = 2
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
# labeling them.
DRAFTER_VERSION = 4
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

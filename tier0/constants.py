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

# --- Elemental auras & reactions (spec §4.4; validate in M4) ---
AURA_DURATION_TURNS = 2       # owner-turns an aura persists unconsumed
VAPORIZE_MULT = 1.5           # Pyro x Hydro, that hit only
MELT_MULT = 1.75              # Pyro x Cryo, that hit only
OVERLOAD_SPLASH = 6           # flat damage to ALL enemies
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
WITCHS_FLAME_DMG = 4              # Durin end-of-turn hit (applies pyro)
SOLAR_ISOTOMA_BLOCK = 3           # block per attack hit vs aura'd enemy
CELESTIAL_GIFT_BLOCK = 4          # Nicole: block at start of turn
CATALYTIC_BURST_PER_REACTION = 5  # Catalytic Conversion bonus burst/reaction

# --- Reference relics ---
BURNING_BLOOD_HEAL = 6        # REF_IRONCLAD: heal after each won fight
                              # (ruling 1: gives A4 a nonzero anchor)

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

# --- Tier 0.5 run model (tier05-draft-sim-spec.md §2) ---
# Fixed node template, no pathing choice (map design is theirs, not ours).
RUN_NODE_TEMPLATE = "NNNENRNNENRNB"
BURST_CHECK_NODE = 6              # this mid N is swapped to burst_check
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
NATION_WEIGHTS = {"mondstadt": 1.0}   # §4.1 mechanism; single-nation v0.1

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
# assigned adopts the hybrid experiment's raw-power term, plus the
# reaction weights pass (values + sweep in tier05/draft.py and the M8
# report). Never compare drafter-v1 and drafter-v2 numbers unlabeled.
DRAFTER_VERSION = 2
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
AMP_PAYOFF_POWERS = {"amp_reaction_up", "witchs_flame"}

# Furina Salon v2 + energy rebalance — pass plan (2026-07-23)

USER DIRECTIVE (2026-07-23, verbatim intent): the flat 4-damage member tick
"ain't it". Salon members should (a) do something UNIQUE while holding an
active slot, (b) be globally buffed by Fanfare "similar to Focus scaling on
Defect", (c) pay a LARGER payoff when kicked out of the slot, and (d) get
an upward numbers adjustment. Alongside: a common-rarity AoE effect (tied
to Fanfare) and an energy rebalancing. Ratified in the same message: the
drafter AoE valuation term and the lean-gate strong-pick escape hatch
(diagnosis §10.8.2 / §10.8.1 flags).

Direction is RATIFIED; every NUMBER below is PROPOSED pending red-pen
(house pattern: sheet passes ship measured proposals).

## 1. Salon v2 — the Defect-orb grammar

State: the anonymous `salon_member` counter becomes a typed FIFO queue
(`player.salon`, max `SALON_MEMBER_SLOTS` 3, duplicates legal — orb
semantics). `powers["salon_member"]` mirrors `len(queue)` so every
existing read (has_salon_members, pilot scoring, instruments) keeps
working.

Members (tick = start-of-player-turn slot passive; bow = the payoff when
DISPLACED — deploying into full slots bows the OLDEST member out, Defect
evoke geometry, replacing the old "excess deploys bow themselves" rule):

| member | tick (slot passive) | bow (kicked out) |
|---|---|---|
| **Mademoiselle Crabaletta** (the heavy) | 6 hydro dmg, random enemy | 14 hydro dmg, random enemy |
| **Gentilhomme Usher** (the shield) | 3 Block | 9 Block |
| **Surintendante Chevalmarin** (the applier) | 2 hydro dmg + hydro aura, random enemy | hydro aura on ALL enemies + gain 3 Encore |

- **Fanfare is the Focus analogue**: every member NUMERIC amount (tick and
  bow, damage and Block) gets `+ fanfare // SALON_FOCUS_PER` at
  resolution. SALON_FOCUS_PER 10 → +3 at the 30 cap, +4 under the
  uncapper. Auras and the Encore rider do not scale (numbers-only, §2.2a
  discipline; Chevalmarin's dmg does).
- Upkeep unchanged: each tick drains 1 Encore; a dry tick resolves at
  ×0.75 numerics (auras still apply). Bows cost no Encore. Ticks and bows
  still feed the Burst meter (SALON_TICK_BURST 2).
- `salon_damage_up` (Grand Salon) becomes "+N to member numeric effects"
  (ticks AND bows, Block included) — same hook id, description updated.
- Card-side replacement scaling stays: a deploy that causes a bow still
  doubles the card's OTHER numerics / triples its damage riders
  (SALON_REPLACE_NUMERIC_MULT / _DAMAGE_MULT — grand_gala's grammar).
- No passive-accrual law: intact. Chevalmarin's Encore is on the BOW — a
  player-triggered event, same legality as a card rider.

## 2. Sheet changes (docs/furina-cards.yaml)

Deploy cards go member-typed (`member:` rider on the salon_member op):

| card | change |
|---|---|
| salon_debut (basic) | deploys **Chevalmarin** (application from card one) |
| gentilhomme_usher | deploys **Usher**, keeps Block 4 rider |
| surintendante_chevalmarin | deploys **Chevalmarin**, keeps Encore 3 rider |
| mademoiselle_crabaletta | **cost 2→1**, deploys **Crabaletta** (was 2 anonymous) |
| full_ensemble | **cost 3→2**, deploys Usher + Chevalmarin + Crabaletta |
| overflowing_hospitality | deploys **Chevalmarin** (rest unchanged) |
| dress_rehearsal | deploys **Usher** (rehearsal = understudy; rest unchanged) |
| endless_waltz (rare) | **cost 3→2**, deploys Crabaletta + Usher, salon_damage_up 3 |
| grand_gala (rare) | **cost 3→2**, deploys Crabaletta, Crabaletta, Chevalmarin, Usher (guaranteed bows on a live Salon) + Encore 4 |

New common AoE (the Gardener-wall answer, Fanfare-tied per directive):

- `standing_room_only` — "Standing Room Only", cost 1, SKILL (skill-grade
  cadence → applies hydro to ALL), common, [fanfare, generic],
  `damage 4 all_enemies, bonus_formula 1_per_5_fanfare` (10-all at the 30
  cap). Joins the hydro mass-application WATCHLIST cell (redpen flag 8).

Energy rebalance (draftable rares avg 1.93 → **1.43**, vs Klee 1.38):
endless_waltz 3→2 · grand_gala 3→2 · the_final_verdict 3→2 ·
unheard_confession 2→1 · the_sea_is_my_stage 2→1 · star_of_the_show 2→1 ·
command_performance 2→1. Kept at 2: universal_revelry (fanfare_cost 20
carries it), prima_donna (double texture), rain_of_roses. Uncommon:
full_ensemble 3→2.

## 3. Drafter v6 (DRAFTER_VERSION 5→6)

- AoE term: `_static_power` multiplies `target: all_enemies` damage by
  STATIC_AOE_MULT 2.0 (conservative average body count; the diagnosis
  measured the drafter reading Undercurrent at half its table value
  against the 4-body elite).
- Lean-gate escape hatch (§10.8.1 flag): past DRAFT_LEAN_CAP, a RARE
  whose score clears DRAFT_LEAN_RARE_BAR 4.0 is always eligible — the
  measured arm's promised-but-unimplemented "genuinely strong picks"
  clause, scoped to rares.

## 4. Parity + fallout

- Codegen: `member` joins APPLY_POWER_FIELDS; the salon deploy emitter
  passes the typed member; SalonPowers.cs reworked to the same table
  (typed queue, focus term, bows). Regenerated roster on the next mod
  build; sim/codegen string contracts tested now.
- furina.yaml A2 deck bands WILL move (salon rework is the point) —
  re-measured this pass and updated with dated PROPOSED comments (R19
  small-n precedent; ratified-band law honored by flagging, not moving
  silently).
- Instruments: exp_furina_* keep running (salon pilot unchanged — the op
  shape survives; only its resolution changed).

## 5. Measurement plan

1. Full suite green (updated salon tests + new typed-member tests).
2. 3-act lever-world Furina funnel + died-given-faced per elite (the
   Gardener wall is the number this pass exists to move).
3. 4-char table (drafter v6 moves everyone — label DRAFTER_VERSION 6).
4. A2 band re-measure for the three archetype decks (1000 fights).

## 6. RESULTS (executed 2026-07-23; suite 593 green, anchor untouched,
## nothing committed — all numbers PROPOSED pending red-pen)

**Instrument correction found en route:** the session's earlier Furina
3-act rows (every §10.8.2 arm) were measured under the **fanfare**
assignment, but the CLI's `DEFAULT_PLAN` for her is **salon**. The
§10.8.2 within-arm attributions stand (same assignment both sides); the
headline "Furina 0%" rows carry the fanfare label. Both assignments were
measured post-rework (500 runs, seed 11, realistic):

| assignment | win | funnel | deck | salon/deck | rares/deck |
|---|---|---|---|---|---|
| fanfare | 0.0% | 37%/6.6%/0% | 17.5 | 0.04 | 0.43 |
| **salon (DEFAULT)** | **9.0%** | **57%/35%/9%** | 21.6 | 1.21 | 1.07 |

Died-given-faced, salon assignment (vs the pre-rework fanfare-assigned
54%/29%/8%): **Gardener 27%, Effigy 19%, Byrdonis 8%** — the Gardener
wall halved; act-1 clears 32%→57%. Deaths now spread across all three
acts (a3 is finally reachable: 79 a3N + 27 a3E + 22 a3B deaths).

4-character table, drafter-v6 world (500 runs; furina row = salon):

| character | v5-lever world | v6+rework world |
|---|---|---|
| furina | 0.0% | **9.0%** |
| klee | 6.2% | 6.0% (4.2–8.4%) |
| real_ironclad | 3.0% | **4.4%** (2.9–6.6%) — the rare hatch recovered him |
| ref_ironclad | 4.8% | 4.6% (3.1–6.8%) |

Red-pen items this section raises: (a) 9.0% makes her the roster top —
if that overshoots, the tune-down knobs are member numbers, the
SALON_FOCUS_PER divisor, and reprice depth; (b) the fanfare-assigned
plan is still 0% — the flux archetype needs its own pass; (c) A2 deck
bands in furina.yaml are flagged STALE, re-measure at ratification;
(d) the drafter still values deploy ops at ~0 static power — salon
assignment covers it via the core-progress term, but cross-plan the
members are invisible (same class as the fixed AoE blindness).

# S7 — divergence classification (Fable pass)

Date: 2026-08-05. Status: REVIEW — Surplus Dispatch 2, S7 touchpoint. Input:
`docs/s7-divergences.tsv` (1 635 rows) + `docs/s7-fidelity-audit.md` (the
worker pass, including its §2.1 confounders). This pass names families and
flags battery exposure. It adjudicates nothing that would need a probe the
corpus cannot supply, fixes nothing, and issues no rulings — every mechanism
below is a **hypothesis** unless marked otherwise, and the probes in §4 are
candidates for a [USER]-gated dispatch, not scheduled work.

Headline: **of 1 635 rows, none is yet a confirmed tier0 infidelity.** The
corpus splits into four families — instrument defects (A), replay
reconstruction gaps (B), two candidate genuine infidelities that survive the
confounders and carry real battery exposure (C), and channels the corpus
cannot inform (D). The two C candidates are the +2 block offset and the
Fanfare accounting residual; each has one cheap discriminating probe.

---

## Family A — instrument/writer defects (engine-side readings wrong, sim uninvolved)

| cluster | rows | mechanism | status |
|---|---|---|---|
| Encore engine=0 while mod-feed twin moves | 27 `l2.encore` + 221 `xfeed.meters.encore` | earlier soak build wrote `0` for "unseen" where the current writer uses `-1` — a sentinel collision with a legal meter value | **effectively confirmed** by the paired-feed control; the 27 sim-vs-engine rows are void, not divergences |
| `fight.cards_played` undercount, 139/139 fights | 244 `record.*` | the four missing names — Ethereal Spotlight (707), Soloist's Solicitation (52), Pers Deploy (10), Interdiction Fire (8) — are all **granted/token plays** (starter-relic cadence, companion cards), not deck-resident drafts; hypothesis: the record counter keys on deck residency while the posted stream counts what the bridge played | high confidence on the pattern (all four names are grants); the exact key is undiagnosed |
| `xfeed.outcome` + `n_cards_played` disagree on all 53 pairs | 106 | the documented R100/5 outcome-semantics change plus two different "played" definitions | expected; **confirms the feeds are not interchangeable for any count** — Track B must never mix them in one cell |

**Exposure:** none to the tier0 battery. Real exposure is to **Track B's B2
curves**, which read `cards_played`: any B2 cell involving Furina undercounts
her single most-played card by construction. B2's existing Act-1 tables
should carry a footnote until the writer is fixed; the fix itself is a
one-defect item, not a design question.

## Family B — replay reconstruction gaps (the wire doesn't carry what the replay would need; neither engine nor sim is impeached)

| cluster | rows | mechanism |
|---|---|---|
| Turn-1 Fanfare, sim 0 vs engine 1–11 | 51 of the 221 fanfare rows | Furina's starter relic grants an Ethereal Spotlight every turn and its Center Stage / Guest Cast **selector choice is never on the wire**; relics are invisible to the replay by declared confounder 2. The engine's turn-1 income flows through a channel the reconstruction structurally cannot see |
| High Tide+ sim 19 constant vs engine 34/39/43/51 | 4 headline + tail of `l1.damage` | tier0 spec is flat 22 (spend 15). 22 × 1.5 Vulnerable ≈ 33–34, plus within-turn Strength ramp reaches the 39–51 readings; L1 deliberately resolves from turn-opening meters (confounder 4), so target debuffs and same-turn ramp are unreconstructed. The *variance* across four plays of a flat-damage card is itself evidence for context, not spec |
| 9 negative HP brackets | 9 | enemy id reused across split/hatch (Corpse Slug / Toadpole / Wriggler) — harness bracketing artifact, correctly excluded |
| 35 skipped plays | — | base-game cards with no tier0 row; a coverage bound, not a divergence |

**Exposure:** none directly — but family B **caps the audit's power**. The
fanfare channel cannot be graded sim-vs-engine at all until the selector
choice and relic cadence are recorded (a bridge/telemetry item, P1.5-shaped),
and single-card damage rows can only be trusted where the target carried no
debuffs. The honest statement: this corpus can *refute* fidelity but mostly
cannot *confirm* it for Furina's kit machinery.

## Family C — candidate genuine sim infidelities (survive the confounders; battery exposure real)

**C1 — the +2 block offset.** 133/277 turns, median +2.0, and the four most
common pairs (7/5, 13/11, 6/4, 10/8) are all *exactly* sim-over-by-2 on
clean single-mechanism turns. No declared confounder produces a systematic
+2 in this direction: invisible relics/potions would make the sim read
*under*, not over. Something makes real block resolve 2 lower than tier0's
arithmetic, or samples it after a 2-point loss. This is the strongest
infidelity candidate in the corpus.
**Battery exposure: broad but shallow.** Tier0 over-blocking inflates
survivability in every arm symmetrically, so relative comparisons — the only
load-bearing use of battery numbers since D3 — largely survive; absolute
floor rulings (the 2% roster floor) are the exposed surface. Rank: fix-worthy
if confirmed, not result-invalidating.

**C2 — the Fanfare accounting residual.** After setting aside the 51
selector-blind turn-1 rows (family B), 170 divergent turns remain with the
sim under the engine (median −3), and the seam test cuts the wrong way:
applying tier0's own decay *widens* disagreement from 16% to 5%. If the
reconstruction gap explained everything, later-turn rows should tighten once
turn-1 income is written off — they don't obviously do so, and the decay
direction suggests tier0 may decay harder or generate later than the C#
engine.
**Battery exposure: narrow but deep — this is the ranked #1 flag.** Every
recent fanfare-archetype verdict leans on tier0 fanfare accounting: the
threshold-reach table (94.1%@10 / 80.8%@15 / 64.8%@20 / 40.8%@30), the
compensation STOP at 1.8%, the "prediction NOT SUPPORTED" early-half grade,
and the R91/2b revisit all move if tier0 under-models real income or
over-models decay. Direction of error: tier0 pessimistic about fanfare →
the fanfare archetype's below-floor verdicts would be *understated*, the
STOP potentially premature. Unconfirmed — but this is the one family where
a confirmed infidelity re-opens ratified conclusions.

## Family D — channels this corpus cannot inform

- `l2.enemy_pool_drop` (24% agreement): quadruple-confounded (targeting,
  enemy block, splits, AoE attribution). **Do not read this column**; it is
  an audit of the confounders, not the sim.
- `l2.salon_members` 262/262 agreement at universally zero: consistent with
  every salon-fill measurement to date, informative about nothing populated.
- All engine numbers are bot-floor (Guardrail 7) and nearly all-Furina —
  fidelity for Klee/Kokomi kits is untested by this corpus.

---

## 4. Discriminating probes (candidates for a gated pass — not scheduled)

1. **C1:** one scripted fight, no relics, single known enemy, play N block
   cards, read block at end via the bridge. One evening of harness time;
   separates a real −2 rule from a sampling artifact in one measurement.
2. **C2:** same shape for Fanfare — a no-relic (or relic-known) scripted turn
   sequence with recorded selector choices, engine meter read each turn
   opening vs tier0 trace. Requires the P1.5-shaped bridge item (record
   selector choices); that item now pays twice (family B *and* C2).
3. **A2 (cards_played):** read the writer with the four granted names in
   hand; it's a counter-key question, likely a one-line fix once seen.

## 5. What this audit does NOT license

No balance change, no constant edit, no re-grading of any ratified result,
and no claim that the battery is wrong — C1/C2 are *candidates* with declared
alternatives. The single immediate, no-authority-needed action item is the
B2 footnote (family A exposure), and even that is filed for the next Track B
pass rather than applied here.

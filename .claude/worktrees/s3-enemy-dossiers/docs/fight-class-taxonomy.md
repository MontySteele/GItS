# Fight-Class Taxonomy — S3 Synthesis

Date: 2026-08-05. Status: REVIEW — Surplus Week S3, Fable synthesis pass
(touchpoint 3 of 4). Inputs: the 111 enemy dossiers in `docs/enemy-dossiers/`
(one Opus agent per enemy, decompile-derived, behavioral notes only). This
document clusters those dossiers into the "per fight class" dimension Track
B's B1 demand curve needs, states the classification rules the labels imply,
and pre-labels every Act 1 encounter so bot-feed telemetry can be cut by
class now. **Zero design authority: no RESKIN/REDESIGN verdicts anywhere —
dossiers inform that ruling, [USER] makes it.**

Machine-readable companion: `docs/enemy-dossiers/fight-class-labels.yaml`
(per-enemy labels keyed by display name, joinable against telemetry's enemy
lists; encounter composition rules below).

---

## 1. The five classes, defined by per-turn demand

The dossier corpus converged on definitions sharper than the dispatch's
one-word labels. Stated here as the canonical reading:

| class | per-turn demand shape | what B1 sees | what B1 CANNOT see |
|---|---|---|---|
| **spike** | demand concentrated in scheduled peaks — a telegraphed big turn, or a ramp steep enough to be a deadline | high-variance incoming-damage series; required-output = kill-by-turn-N | which turn the peak lands (needs per-turn resolution, which the schema has) |
| **attrition** | flat or gently rising tax, every turn; fight length is the threat | steady mean incoming; demand ≈ sustained block+damage floor | the *slope* matters — see §2 |
| **swarm** | demand is *width*: N bodies must die before the board escalates | many small damage instances; required-output = bodies/turn | target-priority quality (same total damage, different allocation) |
| **gimmick** | demand is a binary rule: a threshold, a timer, a kill-order, a cap | often *nothing* — low or zero damage curves | the fight entirely; **gimmick fights are where curve-reading fails by construction** |
| **mixed** | rotating beats, each a different demand (boss-shaped) | multi-modal series | which beat killed the run |

**Consequence for Track B, stated now:** B1/B2 curves are a valid instrument
for spike/attrition/swarm and a *partial* instrument for mixed. For gimmick
fights (27 of 111 enemies; ~30% of Act 1 encounters below) the demand curve
under-describes the fight by design — a Bowlbug (Rock) room reads as "15
incoming/turn" while the actual demand is "exactly 15 block on one seat."
Gimmick cells in any curve table should carry a marker, the same discipline
as empty-cell labeling.

## 2. The slope rule (spike/attrition boundary, made explicit)

The dossiers apply a consistent implicit rule worth ratifying as the
taxonomy's edge-case law: **an uncapped ramp is attrition when its slope is
shallow (≲ +3 damage/turn) and spike when the curve goes effectively
vertical within block reach.** Worked pairs from the same families:
Calcified Cultist (Ritual 2 → +2/turn) = attrition, Damp Cultist (Ritual 5)
and Devoted Sculptor (Ritual 9) = spike; Byrdonis (+1/turn) = attrition,
Fuzzy Wurm Crawler (+7/Inhale) = spike. The corpus is consistent with this
rule everywhere I checked; no relabels needed on its account.

A second recurring fact rides on it: **determinism is near-universal.**
Almost every enemy runs a fixed or repeat-clamped loop; genuine RNG is rare
and small. Demand curves per fight class will therefore be *tight* — the
variance in B1 will come from encounter composition and seat count, not
enemy dice. This is good news for N=3-scale soaks: small N loses less than
it would against a stochastic roster.

Third fact, co-op: **HP scales by seat count (act-indexed ×1.1/×1.2/…) but
attacks hit every seat at full value, and party-wide debuffs multiply by
seats.** Per-seat demand is roughly flat while party demand grows
superlinearly — the Act 2 wall the playtest reported is visible in the
dossier scaling notes before any telemetry confirms it. B1 should therefore
always be cut by seat count, never pooled across it.

## 3. Distribution

111 dossiers: **mixed 32 · attrition 29 · gimmick 27 · swarm 12 · spike 11.**
Mixed concentrates in bosses/elites (as expected — multi-beat design IS boss
design). Gimmick density is the surprise: a quarter of the roster is
rule-shaped rather than number-shaped, which bounds how much of the game
Track B's curves can ever grade alone.

Excluded from Track B labeling (recorded in the YAML with `exclude` and a
reason): **The Architect** (epilogue victory room, not a fight), **The
Adversary Mk 1/2/3** (no encounter routes them — unrostered/unfinished
content), **Battle Friend V1/V2/V3** (event-selected DPS checks; labeled
gimmick but flagged `event_only` — they should not enter the normal-fight
demand pool).

## 4. Encounter composition rules

Telemetry records fights as enemy *sets*; the label must be composable from
member labels. Rules, in precedence order:

1. **Defining-gimmick precedence:** if any member's gimmick defines the
   room's win condition (heist timer, revive loop, kill-order lock), the
   encounter is **gimmick** — e.g. Corpse Slugs (a swarm-shaped pack whose
   Ravenous rule demands a simultaneous multi-kill) is gimmick, not swarm.
2. **Body-count:** ≥3 small bodies with no defining gimmick → **swarm**.
3. **Peak dominance:** any member whose scheduled peak or steep ramp sets
   the fight's deadline → **spike**.
4. **Beat rotation:** members (or a solo boss) rotating distinct demand
   types → **mixed**.
5. Otherwise → **attrition**.

## 5. Act 1 pre-labels (both branches), effective immediately

Derived by applying §4 to the dossier corpus. Telemetry keys on the enemy
set; encounter names are the decompile's where the dossiers state them.

**Overgrowth (act index 0):**

| encounter (enemy set) | label | via |
|---|---|---|
| Ruby Raiders band (Axe/Crossbow/Assassin/Tracker/Brute mix) | spike | rule 3 — Big Swing + Fire volleys set the peaks; Tracker/Brute are multipliers |
| Slime rooms (Leaf/Twig S+M, 3–4 bodies) | swarm | rule 2 |
| Inklets ×3 | swarm | rule 2 |
| Wrigglers ×4 (Dense Vegetation event fight) | swarm | rule 2 |
| Fogmog + Eye with Teeth | gimmick | rule 1 — revive loop is the fight |
| Corpse Slug pack | gimmick | rule 1 — Ravenous simultaneous-kill demand |
| Nibbits (pair or solo weak) | attrition | rule 5 |
| Mawler | attrition | rule 5 |
| Slithering Strangler | attrition | rule 5 |
| Haunted Ship | attrition | rule 5 |
| Flyconid + Snapping Jaxfruit | mixed | rule 4 — debuff rotation + ramp kill-priority |
| Fuzzy Wurm Crawler | spike | slope rule (+7/Inhale) |
| Cubex Construct | spike | rule 3 — uncapped Expel ramp, no wall |
| Shrinker Beetle | gimmick | rule 1 — 30% damage cut until it dies |
| **Elite:** Byrdonis | attrition | slope rule (+1/turn) |
| **Elite:** Bygone Effigy | attrition | flat 23/25 AoE; Slow ordering is texture, not the demand |
| **Elite:** Phrog Parasite (+ Wriggler phase 2) | mixed | rule 4 — deck-hygiene phase then swarm phase |
| **Boss:** Ceremonial Beast | mixed | threshold phase + rotation phase |
| **Boss:** Vantom | mixed | Slippery opener + scheduled Dismember |
| **Boss:** The Kin (Priest + 2 Followers) | swarm | rule 2 with decapitation hatch; dossier concurs |

**Underdocks (act index 0):**

| encounter (enemy set) | label | via |
|---|---|---|
| Cultists (Calcified + Damp) | spike | rule 3 — Ritual 5 sets the deadline |
| Gremlin Merc (→ Sneaky + Fat) | gimmick | rule 1 — two-turn heist timer |
| Living Fog + Gas Bombs | mixed | rule 4 — action-economy cap + recurring bomb tax |
| Two-Tailed Rats (3 + summons, cap 5) | swarm | rule 2 |
| Toadpoles ×2 | gimmick | rule 1 — spike-target alternation is the whole ask |
| Sewer Clam | attrition | Plating wall + shallow ramp |
| Seapunk | attrition | slope rule |
| Sludge Spinner (weak) | attrition | rule 5 |
| Fossil Stalker | gimmick | rule 1 — block-to-zero threshold |
| Punch Construct | mixed | rule 4 |
| **Elite:** Skulking Colony | gimmick | rule 1 — 20-damage/turn cap steps the demand |
| **Elite:** Terror Eel | gimmick | rule 1 — half-HP Shriek binary |
| **Elite:** Phantasmal Gardener ×4 | mixed | phase-offset ring + Skittish first-hit rule |
| **Boss:** Soul Fysh | gimmick | rule 1 — Beckon hygiene + Intangible lap |
| **Boss:** Waterfall Giant | mixed | attrition body + death-detonation rule |

Immediate Track B note: **Act 1's gimmick density (~30% of encounters) means
roughly a third of Act 1 bot-feed fights should be curve-marked per §1.**
The demand curve for those rooms is still worth plotting — it is the
*divergence* between curve-implied difficulty and observed HP loss that will
locate the gimmick tax empirically.

## 6. Flags for review (not relabels)

1. **Snapping Jaxfruit** is labeled gimmick by its dossier; by the slope
   rule its uncapped +2 Strength AoE reads closer to spike-adjacent
   kill-priority. Left as filed — the paired-encounter label (mixed) is what
   telemetry uses, so nothing downstream moves either way.
2. **Kin Priest** carries a dossier note (truncated in the ledger) about the
   A9 ramp; the swarm label is composition-correct regardless.
3. The **Adversary ladder** existing unrostered in the DLL is a base-game
   curiosity worth knowing (future content shape) — recorded, no action.

## 7. What this unlocks

- `tools/track_b_curves.py` can join `fight-class-labels.yaml` against the
  telemetry's enemy sets and emit B1 per class today, bot feed, Act 1.
- The human feed inherits the same labels — Act 2/3 encounter pre-labels are
  derivable from the same dossiers when Track B needs them (they exist in
  the corpus; only Act 1 was pre-labeled here per the dispatch).
- The gimmick marker (§1, §5) should ride any B1/B2 table the way feed
  labels already do (Guardrail 7 discipline, same shape).

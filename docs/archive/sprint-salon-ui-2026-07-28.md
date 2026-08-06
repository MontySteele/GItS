> **MOVED 2026-08-06 — Clear the Stage, Track R-B (charter R119, rail 1).**
> Old path: `docs/sprint-salon-ui-2026-07-28.md` — new path: `docs/archive/sprint-salon-ui-2026-07-28.md`.
> Verbatim move: everything below this banner is byte-identical to the
> pre-move file. Citers repointed in the move commit; see
> `review/stage-clear/rb-move-manifest.tsv`.

# Sprint brief — Salon UI legibility + measurement (Group 3 residue, 2026-07-28)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Delegated sprint. Parent doc: `docs/playtest2-triage-2026-07-28.md` (Group 3).
All design questions in scope are ANSWERED — this sprint is implementation and
measurement only. Anything marked PROPOSED or "report back" returns to [USER]
at review; do not invent balance numbers beyond what is written here.

Visual spec: `docs/mockups/salon-stage-d1-mockup-2026-07-28.html` — open it in
a browser; it embeds the real member sprites and the real tick constants.
**That file is deliberately UNTRACKED** (`.gitignore`, `docs/mockups/`): it
inlines three Tier F sprites as base64, and the repo is public, so committing
it would distribute exactly what §9 refuses to. It is handed over out-of-band
with the rest of the Tier F material; a checkout will not have it. The
mockup is the ruling for layout, hue, and chip shape, with the amendments in
Track 1 below (no bow marker) and Track 2 (ribbon becomes runway segments).

## Sequencing constraints (hard)

- **After B1–B5** (bug-fix sprint): Track 1's chip values must read the same
  scaled constants the tick actually uses, and B4 decides whether Grand Salon
  scaling reaches non-damage numbers. Building chips before B4 lands risks
  chips that lie.
- **Coordinate with A12** (adjustment sprint): slot count must come from the
  per-player salon cap stat A12 introduces, not the hardcoded 3. If A12 has
  not landed yet, build against the constant but through a single accessor so
  the swap is one line — do not duplicate the cap.

## Track 1 — Salon stage legibility (D1, RULED)

Scene: `klee-mod/pck-src/furina/ui/salon_stage.tscn`.
Bridge: `klee-mod/KleeCode/Vfx/SalonVisualsBridge.cs`.
Keep the sprint-2 skeleton: slot-index rendering, ghost slots, pop cascade,
dry tint, Displays registry. Everything below is additive.

1. **Accent hue per member**, carried by the underglow pool (and chip border),
   sprites untouched: Crabaletta rose, Usher gold, Chevalmarin aqua (exact
   values in the mockup CSS: #f0708c / #e8bb52 / #5fe0d2 — adapt for Godot
   modulate as needed). Duplicates render as duplicate hues; the slot-indexed
   Funnel Contract §1 is untouched.
2. **Live tick chip** under each occupied member: role glyph (sword / shield /
   droplet) + the member's CURRENT per-turn tick value, read from the same
   scaled path `SalonPowers` ticks with, so the chip can never disagree with
   the actual tick. When a buff (Grand Salon) raises the value above the base
   constant, render the number in the buffed-value color the game already
   uses for modified card text. Dry state greys the chips along with the
   existing tint.
3. **NO bow marker** (ruled 2026-07-28): members already display in summon
   order left→right (company appends, bow pops index 0 — SalonPowers.cs:221),
   so position IS the bows-next signal. Do not add marker chrome. Instead the
   Salon Member keyword text (shared with B5) gains one sentence: "The
   leftmost member bows first."
4. **Member tooltips on hover**: per-slot hover target showing tick line and
   bow line only, copy shared verbatim with B5's keyword tooltip source (one
   source of truth — do not fork the strings). Cap mechanics live on the
   Salon Member keyword, not per member. Verify the hover target does not
   fight targeting arrows or enemy intents.
5. **Dynamic slot count** from the per-player cap (see A12 constraint above).
   A cap raise appears as a new ghost slot; layout must stay inside Furina's
   240-wide bounds at cap 5 (tighten slot gap as count grows — mockup shows
   the cap-4 spacing).

## Track 2 — Encore ribbon becomes RUNWAY (D7, RULED)

Same scene/bridge. The current fill denominator `RibbonVisualSpan = 20`
(SalonVisualsBridge.cs:82) is a display-only lie — Encore is uncapped.
Replace fill-fraction with runway segments:

- Segment = one turn of upkeep at the CURRENT stage: member count × 1 Encore
  (`TickEncoreCost`). 12 Encore with 3 members = 4 segments.
- Render up to 5 segments; more shows as 5 segments + a "5+" overflow cue.
- Keep the raw Encore number label on the ribbon, and the existing dry
  flash/dim behavior.
- Zero members: no segmentation is meaningful — show the number on an
  unsegmented ribbon (pick the least-weird rendering, note it in the log).
- Deploying a member visibly shortens the runway with Encore unchanged —
  that is correct and is the point.

## Track 3 — Encore saturation telemetry, tier0 (D8 prerequisite, MEASURE ONLY)

Playtest read: Encore refills faster than the stage drains it and trends
toward a passively-full free-block bar. [USER] has ruled the DIRECTION only
(either more Encore sinks — pairs with the D6 on-demand-bow design space — or
faster drain + power bump). The lever pick is red-pen and OUT OF SCOPE.

This sprint ships the instrument and the baseline, same shape as the Fanfare
saturation telemetry from sheet pass 4:

- Per-combat: fraction of stage-active turns that are dry (< tick cost),
  fraction where every member ticked, Encore level at combat end, Encore
  gained vs spent totals.
- Report across the standard salon-assigned roster runs, version-stamped.
- Deliverable: numbers in the sprint log + a one-paragraph read, NO balance
  changes, NO new cards.

## Track 4 — Slip Backstage rider fire-rate, tier0 (D4, MEASURE ONLY)

`graceful_retreat` (Slip Backstage) has an `hp_lost_this_turn` conditional on
a block card, suspected near-dead (block resolves before the enemy turn).
Instrument how often the rider actually fires across the standard runs.
Deliverable: fire-rate number + a one-line read in the sprint log. Any
re-authoring of the condition is red-pen, out of scope.

## Gates (house standard)

- Full-repo pytest from root, green, before and after.
- Regen + build validate; `build_pck` before deploy; art lint clean.
- Harmony bite-check for the C# behavior touched (no Godot run available;
  co-op has no sim backstop — visual changes get verified at next playtest,
  say so in the log rather than claiming visual verification).
- Version stamps on any measurement tables; never quote old rows against new.
- Sprint log lists every PROPOSED item and every judgment call made without
  red-pen, for [USER] review.

## Explicitly out of scope

- D5 (Waltz/Gala watch pair — no change by design), D6 (on-demand bow —
  design + red-pen first), any Encore economy lever (Track 3 measures only),
  any card text or balance change not listed in the parent triage doc's
  Groups 1–2 (those belong to the other two sprints).

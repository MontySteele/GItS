# Sprint brief — the art gap and the A7 port (pre-playtest close-out, 2026-07-29)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Delegated sprint. Parent: the 2026-07-29 pool audit (clean verdict; this
brief is its two action items). Goal: after this sprint the pool is
playtest-ready — every card has art, and every card on the sheet exists in
the actual game.

## Track A — five card portraits

`art_coverage` reports exactly five missing, all from the last two sprints:

| card | rarity | register |
|---|---|---|
| applause_line | common | archon |
| held_breath | common | archon |
| breathless | common | private |
| casting_call | common | salon |
| take_your_bow | uncommon | salon |

Standing law, all of it applies:

- The scarcity ruling (hybrid §2): ~25 clean illos serve the pool — commons
  draw from the crop-reuse pool, strict-source treatment is reserved for
  basics and rares. All five of these are crop-eligible; none earns a
  strict slot.
- L9 family ban and the cover anchors are unchanged; L11 one-producer-per-
  out-path; declare encoding on every write; `build_pck` before deploy.
- **`art_fetch` takes NO arguments** — running it with `--help` runs a
  real fetch and churns SOURCES.tsv. Read the script header, not --help.
- Two cleared-but-orphaned assets sit on disk and MAY be re-crops if the
  fit is honest, not forced: `rising_tide.png` (water climbing the stage —
  plausibly casting_call or take_your_bow, both salon voice) and
  `swift_currents.png` (current motif). Both are already cleared through
  SOURCES.tsv, which is the entire reason they were kept. If used, the
  STALE ledger notes in art_coverage must be updated to say where they
  went; if not used, leave them and say why in the log — a judgment
  either way, logged either way.
- Register voice should inform the crop choice: archon reads as the
  Regina/public face, private as the woman, salon as the theatre. A
  private-register card wearing a coronation crop is a miss even if the
  art is pretty.

Deliverable: five portraits through the normal pipeline, art_lint clean,
art_coverage 271/271, pck rebuilt, deployed.

## Track B — the A7 port (Unheard Confession enters the game)

The last sheet card missing from C#. The manifest blocker is real: the C#
Fanfare mutators are synchronous and every block grant is
`await CreatureCmd.GainBlock`. The deferral was correct twice; now it is
the only card gap left before a playtest that includes fanfare decks, and
one of the three "Fanfare +8" rare-Power payoffs should not be absent from
the deck pool that needs it most.

Constraints on the idiom, non-negotiable:

- **Co-op safe.** No per-peer state mutated from preview/cost paths (the
  Vigil desync class), no fire-and-forget tasks racing the lockstep. If
  the settle must defer, it defers to a point both peers deterministically
  reach.
- **Parity exact.** tier0's `note_fanfare_change` fires on every mutation
  funnel (gain, decay, floor-raise, crash) at a FLAT amount per change
  event, either direction, inert at saturation (applied == 0 is not a
  change). The C# port must match all four sites and both edge cases; the
  parity test file is where that is pinned.
- **The sheet-ordering fact holds**: the card's own +8 grant is written
  before the power installs, so it must not pay itself for its own grant.
  Pin it — that is currently a sheet-ordering fact, not an engine
  guarantee, and the C# power's install order must reproduce it.
- Decay fires every turn from turn 2, so the power pays ~1 Block/turn
  passively once the meter moves — that is the DESIGN (the ruling's "pays
  on the way down"), not a bug to fix. Do not add an activity gate the
  sheet does not have.
- Verification: bite-check armed, the FURINA_DEFERRED_ASYNC assertion
  retired/re-scoped, manifest blocked count 2 → 1, and a red test built
  from the old blocked state.
- **If no co-op-safe idiom exists, report and stop** — a third deferral
  with a written reason beats an unverified sync hack. The bar is "would
  survive the Vigil postmortem," not "compiles."

## Out of scope

Card numbers (all PROPOSED items await red-pen), the X sweep, the
lasting_impression redesign (queued with red-pen — it also dissolves the
lasting_impression/reginas_mercy near-dup), the spotlight-arm conditional
telemetry, the +9 phantom hunt, the fanfare_weighted A2 band re-measure.

## Gates (house standard)

Full-repo pytest green before/after; regen clean; art_lint + art_coverage
clean; structural + register + parity lints; build_pck before deploy;
validate; bite-check; every judgment call in the log.

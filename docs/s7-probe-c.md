# S7 probe (c) — the `cards_played` counter key

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Date: 2026-08-05. Authority: R103 (probe order (c) → (a) → (b)). Input: the
S7 audit's family A cluster (`docs/s7-fidelity-audit.md` §4.1,
`docs/s7-classification.md` family A) plus `docs/s7-divergences.tsv`. This is a
**code read**, not a measurement: no game was launched and no run was taken.

## The answer

**The counter keyed on the AFTER-state, not on the play.** In
`understudy/soak.py`, `RunDriver._observe` wrote `fight.cards_played` (and
`fight.potions_used`) inside the arm guarded by
`if st_b in COMBAT and st_a in COMBAT:` — that is, a play was written down only
if the state read back *after* it was still a plain `monster`/`elite`/`boss`
screen. The classification's stated hypothesis — "the record counter keys on
deck residency" — is **wrong**: nothing in the writer or in
`understudy/naming.py` ever looks at the deck, and a granted card resolves its
name out of `player.hand` exactly like a drafted one. Grantedness was a
correlate, not the mechanism.

The correlate held because the two ways to leave `COMBAT` on your own play line
up almost exactly with the four names:

1. **The play opens a mid-fight overlay.** `st_a` becomes `card_select` (in
   `MID_FIGHT`), the arm is skipped, the play is lost. Furina's starter relic
   grants an Ethereal Spotlight every turn and playing it opens the Center
   Stage / Guest Cast choose screen — so *every* Spotlight play was lost. The
   divergence file agrees flatly: every Ethereal Spotlight row reads record `0`
   against a posted 1–9.
2. **The play ends the fight.** `st_a` becomes `rewards`, the arm is skipped,
   and the record is closed one statement later — so exactly **one** play per
   fight, whichever card landed the killing blow, was lost. Every non-Spotlight
   row in the divergence file is a delta of exactly 1: Soloist's Solicitation
   52, Freminet — Pers, Deploy! 10, Chevreuse — Interdiction Fire 8, then a
   tail of one-per-fight names (Crashing Waves+ 5, Matinée Performance 4, House
   Call 3, Applause Line+ 3, …) that the audit's headline did not enumerate.
   Those three companion attacks are simply the bot's most common finishers;
   their `OnPlay` opens no screen at all.

So the defect is one gate, seen from two sides, and the "granted plays" framing
in the signed package describes the biggest slice rather than the key. The
direction of the error is one-way undercount, and it is not uniform across
names — the Spotlight loses all of its plays, everything else loses at most one
per fight.

## The fix (R101/1b)

The play-recording block now hangs off `st_b in COMBAT` alone: a play is
recorded on the state it was decided against, which is also the state its round
number is read from. It sits before `_close_fight`, so a killing blow lands in
the record it belongs to. Pinned by four tests in
`tier0/tests/test_understudy_soak.py` (overlay play, killing blow, potion on
the way out, and a play whose *before* state is not a fight — still not a
play).

Historical rows are **not** regenerated. Every existing `record: fight` row
keeps its old counter and is annotated instead, per R101/1a — the Track B
banner in `docs/track-b-curves.md`.

## Two things deliberately NOT fixed here

- **`damage_by_source` shares the gate** and therefore drops the killing blow's
  damage and every Spotlight's. It stays inside the after-state arm on purpose:
  that attribution is a pool difference read across two states, and a pool
  cannot be differenced across a screen change. The writer's own comment
  already says the enemy pool by turn, not `damage_by_source`, is the honest
  damage curve. Flagged, not touched — fixing it is a different claim than
  counting a play.
- **`damage_taken`** has the same shape and the same reason.

## The C# writer does not share the defect

`klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs` counts from the game's own
`AfterCardPlayed` hook (`PlayTelemetry.CardPlayed`, one row per play via
`IsFirstInSeries`), gated only on the fight record still being open. No state
type is consulted, so neither an overlay nor a killing blow can hide a play
from it. This is consistent with the audit's observation that on all 53 paired
fights the mod feed's `n_cards_played` is the **higher** number. **Nothing to
rebuild or deploy for this item** — and the paired-feed gap it explains is
another reason the two feeds' counts are not interchangeable in one cell.

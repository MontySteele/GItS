# Sprint log — the art gap and the A7 port (2026-07-29)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Brief: `docs/sprint-art-and-a7-2026-07-29.md`. Both tracks SHIPPED.

**Headline: the pool is playtest-ready.** art_coverage 271/271, manifest
`blocked` 2 → 1 (the one remaining is the hand-written kit Burst, which is not
a gap). Every card on Furina's sheet now exists in the actual game.

**Two findings the brief did not anticipate, both reported rather than
tuned:**

1. **A7's decay half does not pay, in EITHER engine.** See §B.3.
2. **A live, shipped card is wearing a burnt-in wordmark.** `curtain_cue`
   carries "GENSHIN IMPACT" across the top of its portrait. Found by the new
   L9 family added this sprint, on a card outside the brief's five. See §A.4.

---

## Track A — five card portraits

### A.1 What shipped

| card | rarity | register | source | mode |
|---|---|---|---|---|
| casting_call | common | salon | Opera Epiclese - Furina's Seat.png | cover x0.45 |
| take_your_bow | uncommon | salon | Starlight Reverie Wallpaper Furina.png | cover center |
| held_breath | common | archon | Fragrant Fantasy Furina 3.png | cover_autocrop cover@0.06 |
| applause_line | common | archon | Furina Birthday 2024 - Shorts.png | cover center |
| breathless | common | private | Savoring the Breeze Furina.png | cover_autocrop contain@0.08 |

All five are `shortlist` rows with a rank-2 alternate, all in `furina_pool`
(hybrid §2 crop-reuse tier — none of these earns a strict slot). Rank 1 ships
as the provisional pick, so a red-pen session overrides any of them with one
line in `art/picks.tsv` and no code change.

**Register voice drove the pick, as the brief asked.** casting_call and
take_your_bow are the theatre (an empty seat, a lone figure downstage in a
spotlight); held_breath is the crowned Regina; breathless is the woman with no
crown on.

### A.2 The two strong ones, and why

**casting_call ← Furina's empty seat in the Opera Epiclese.** The card reads
"your Salon has room for one more Member". An empty throne IS that sentence.
The source carries a bottom-right GENSHIN watermark; `x0.45` walks the crop
left off it, and the shipped PNG was opened to confirm it is gone rather than
assumed from arithmetic.

**take_your_bow ← Furina alone downstage, head bowed, curtains drawn, in a
spotlight.** The best fit of the five by some distance. The source is
landscape at exactly the right aspect band, so a centred `cover` uses the full
source height and drops both the top-left wordmark and the bottom-right
copyright by construction.

### A.3 breathless is the weak one, and this is the flag

Register is right (no crown — the woman, not the Regina). **Mood is wrong**: a
card that spends her Encore buffer and pays the shortfall in her own HP is
wearing a contented chibi with her arms folded. Both its alternates are the
same art family. This is where the clean-illustration pool ran out, exactly as
the scarcity ruling predicted, and it is the first row a red-pen session
should look at.

Its first crop was worse and was fixed rather than shipped: `cover@0.06` on a
349x394 sticker zoomed into the face and cut the crown and everything below
the chin — the textbook L6 failure. Switched to `contain@0.08`, the documented
fallback. **applause_line** is the second-weakest: she is centre-frame and the
room is reacting to her, which is what an applause line is, but three other
characters share the frame.

### A.4 THE FINDING — a new lint caught an already-shipped defect

Four source families were opened this session, disqualified by eye, and
written into `art_lint`'s L9 ban with the reason:

- `Furina Introduction Card` — the banned Introduction BANNER's sibling. A
  title at 10% height and a full-width FURINA wordmark band at 80%; no crop
  tall enough to frame the figure clears both.
- `New Year's Advice from Teyvat` — a quote card. The only art is a chibi
  inset and cropping to it still includes the quote.
- `Ride the Waves to a Rendezvous` — a framed concept-art PAGE, not the
  concept art: a letterboxed panel with the wordmark above and ©COGNOSPHERE
  below, inside a decorative border.
- `Genshin Impact Commemorative Shikishi Set` — monochrome, with a copyright
  line burnt across the bottom. It would be the only colourless portrait in a
  pool of 82.

**The third one fired against `curtain_cue`, which shipped two sprints ago.**
Its portrait was opened and confirmed: the GENSHIN IMPACT wordmark sits across
the top of the card and the page's beige border runs down both sides.

It cannot be cropped out. The panel is letterboxed inside a 1920x1080 page, so
a 500x380 `cover` uses the full source height by construction and no focus
anchor changes it — only a different source or a manual crop fixes it.

**NOT re-picked here**, deliberately: it is outside the brief's five-card
scope, every honest replacement in the free pool is already claimed, and
picking a portrait is a taste call. Recorded in a new `PENDING_BANNED_FAMILY`
allowlist, following the existing `PENDING_UNDERSIZE` / `PENDING_RED_PEN`
pattern — reported on every run, does not fail the gate, and the entry must be
DELETED on resolution so the lint then guards it.

This is the whole argument for writing families down instead of remembering
them: the ban was added to protect future picks and immediately paid for
itself on a past one.

### A.5 The two orphaned assets — JUDGED, NOT USED

The brief offered both as possible re-crops. Both were opened. Both rejected,
and the STALE ledger notes in `art_coverage.py` were corrected either way, as
the brief required.

**`rising_tide.png` — and the ledger was describing a file it had not
looked at.** The note called it "water climbing the stage". The shipped bytes
are `A Wish For Smooth Sailing Quest Still 2`: a chibi resort-map panorama
with a dozen small figures and no Furina focus. The description was the
PLAN's intent, not the asset. Wrong voice for either salon card, and a
multi-figure scene besides. Note rewritten to say what the file actually is.

**`swift_currents.png`** is a KOKOMI chibi sticker on a `kokomi/` out-path — a
different character. No crop of it can serve a Furina card. The "current
motif" framing only ever applied to a future Kokomi row; the note now says so.

---

## Track B — the A7 port

### B.1 The idiom, and why the deferral's own gate was the wrong question

The deferral stood for two sprints and named its release gate as "make the
Furina resource surface async, or establish a verified sync block-grant
idiom". **Neither is what released it.** Both are still true: threading async
through the resource surface would drag GainEncore/SpendEncore and every
generated Encore card into a co-op-critical refactor, and
`Creature.GainBlockInternal` still has no precedent and no decompile evidence.

The third option was already shipping next door. `CurtainCallHooks.NoteEncoreSpent`
has, since R85, **noted synchronously and settled at the next awaited hook**,
on the same funnel, for the same reason. A7 copies it exactly:

- `FurinaResources.NoteFanfareChanged(creature, before, after)` — synchronous,
  called from all four mutation funnels, accumulates into a per-creature
  `PendingDeltaBlock` counter.
- `FurinaResources.FlushFanfareDeltaBlock(choiceContext, creature)` — awaits
  one `CreatureCmd.GainBlock`, `Unpowered`, `fast: true`, following
  `SalonBowBlockPower`. Idempotent: the counter is taken and cleared.

**Co-op exposure is not new.** The write happens at precisely the points a
vetted write already happens, and the settle happens at points both peers
reach deterministically in the lockstep. No per-peer state is touched from a
preview or cost path, and nothing is fire-and-forget.

Lesson worth keeping: *a deferral's stated gate is a hypothesis about the
solution.* Re-reading the neighbours beat waiting for the refactor.

### B.2 Parity, all four sites and both edge cases

| funnel | sim | mod |
|---|---|---|
| gain | `gain_fanfare` | `GainFanfare` |
| floor-raise | `gain_fanfare_floor` | `GainFanfareFloor` |
| decay | `decay_fanfare` | `DecayFanfare` |
| crash | `drop_fanfare_to_floor` | `DropFanfareToFloor` |

`raise_fanfare_cap` / `RaiseFanfareCap` is deliberately EXCLUDED in both and
pinned as an exclusion: it moves the ceiling and never the meter, so there is
no change to pay for. Wiring it would pay Block for every "Fanfare Cap +X"
Power in the pool — twelve cards' worth of value nobody printed.

Both edges hold: **flat per change event** regardless of how far the meter
moved, and **inert at saturation** (a gain landing entirely at the cap moved
nothing, so it is not a change). A meter already resting on its floor also
pays nothing for a decay that did nothing — `decay_fanfare` still emits in
that state, so "the event fired" and "the meter moved" are different
questions and only the second one pays.

Settle points: after a card play, at turn start (see below), at
`AfterPlayerTurnStart` for Salon upkeep's spend, at turn end, and — the one
that matters for a defensive power — `AfterDamageReceived`, which fires per
damage instance so the Block is on the board before the next hit of the same
turn.

### B.3 THE FINDING — the decay half pays into a bucket that is emptied

The brief states: *"Decay fires every turn from turn 2, so the power pays ~1
Block/turn passively once the meter moves — that is the DESIGN (the ruling's
'pays on the way down'), not a bug to fix."*

**The premise does not hold, and it does not hold in the SIM either.**
`combat._player_turn` calls `resources.decay_fanfare` at line 424 and clears
Block at line 430. Six lines. Decay is the only downward mover in the game, it
fires once per turn at the top of the turn, and its Block is destroyed
immediately afterward on every turn without Barricade.

So "pays on the way down as well as the way up" — the sheet comment's stated
reason this card is a fanfare engine rather than a second gain-rider — is
**not what the card does today**. It is a gain-rider.

**Ported faithfully rather than quietly improved.** The C# flush sits inside
`BeforeSideTurnStart`, the broadcast that `AfterBlockCleared` follows, so both
engines lose it identically. Moving the flush one broadcast later to
`AfterPlayerTurnStart` looks like a fix and is in fact a C#-only buff worth
~1 Block/turn that the sim never pays and no measurement has ever priced.

**This is a [USER] ruling, not a sprint judgment**, and it is a ruling about
the SIM's turn order first — the mod is downstream of it. The site is pinned
by a test asserting the ordering in both engines, and the C# comment says why,
so nobody "fixes" it by accident.

### B.4 The sheet-ordering fact, pinned on both sides

The card's own `Fanfare +8` is written before the power installs, so it does
not pay itself 8 Block for its own grant. Nothing in either engine prevents
the reverse — `note_fanfare_change` would happily pay it — so this is a
sheet-ordering fact, and the C# side only inherits it for as long as the
generator emits effects in sheet order. Both are now asserted: the sim
behaviour, and the textual order of `GainFanfareFloor` before
`PowerCmd.Apply<FanfareDeltaBlockPower>` in the generated card.

### B.5 Deferral released visibly

`FURINA_DEFERRED_ASYNC` is **deleted**, not emptied — the Curtain Call
precedent: a dormant escape hatch makes the next silent skip easy. In its
place, a positive assertion by name that `unheard_confession` generates, and
the manifest count moving 2 → 1.

---

## Judgment calls (every one, for the red pen)

1. **breathless's portrait is the weakest of the five** — right register,
   wrong mood. Flagged rather than forced; both alternates are the same
   family.
2. **applause_line is the second-weakest** — three other characters share the
   frame.
3. **curtain_cue was NOT re-picked**, only reported. Outside scope, and the
   replacement is a taste call.
4. **Four new L9 bans** added from this session's own eyes-on rejections.
   Adding a family is cheap and the alternative is losing the knowledge.
5. **`PENDING_BANNED_FAMILY` is a new allowlist**, modelled exactly on the two
   that already exist, so a real finding can be visible without failing a gate
   the sprint did not scope.
6. **Neither orphan asset was used**, and the rising_tide ledger note was
   found to be describing something other than the file it names.
7. **A7 settles as ONE GainBlock for the SUM** of the change events inside a
   hook window, not N calls. With `Unpowered` that is arithmetically identical
   to the sim's N adds; recorded because it stops being identical the day this
   payout gains a per-grant modifier.
8. **The power sigil is pathed ahead of its art** and registered in
   `validate.ps1`'s `$pckDeferred` — the same policy the six Curtain Call
   powers ship under. S12 caught the unregistered path on the first deploy
   attempt, which is the gate working.
9. **The C# half of the A7 tests asserts SOURCE TEXT, not behaviour.** There
   is no C# test project in this repo. Stated plainly in the test file's
   docstring: it proves the call sites exist where we reasoned about them, not
   that the game runs them. The bite-check is the run-verification half.

## Mutations run (a gate is only trusted once seen to FAIL)

All six via a copy-backup harness — **never `git checkout` on a dirty tree**,
the 2026-07-28 lesson.

| # | mutation | result |
|---|---|---|
| M1 | restore the `fanfare_delta_block` blocked_reason early-return | RED |
| M2 | drop `NoteFanfareChanged` from `DecayFanfare` | RED |
| M3 | drop `note_fanfare_change` from `drop_fanfare_to_floor` | RED |
| M4 | swap the card's effect order (it pays itself) | RED |
| M5 | move the decay flush out of `BeforeSideTurnStart` | RED |
| M6 | flush never clears the counter | RED |

## Gates

| gate | result |
|---|---|
| full-repo pytest | 1400 → **1416** |
| regen | clean; furina 81 generated / **1 blocked** |
| art_lint | plan OK (1 new pending, named) |
| art_coverage | **271 / 271** |
| register lint (R1–R7, L12) | OK |
| constant parity | OK |
| handwritten parity | OK |
| generated structure | OK |
| strict domination / pool membership / upgrade coverage | OK |
| sheet comments | OK |
| `dotnet build` | 0 errors |
| build_pck | 117 resources |
| validate | **OK** |
| deploy | done |
| bite-check | **14 patch classes armed** |

Two lints fail and **both failed identically at HEAD before this sprint**,
verified by re-running with the change stashed: `lint_text_encoding` (73
undeclared reads across 19 files, none in a file this sprint touched) and
`lint_unique_names` (needs sheet arguments; passes when given them — 219 card
+ 6 relic names unique). Neither is wired into `validate.ps1`. Recorded, not
fixed: out of scope.

## Still owed

- **The A7 decay ruling** (§B.3) — the biggest item, and it is [USER]'s.
- **curtain_cue's portrait** (§A.4) — a re-pick or a manual crop.
- **breathless's portrait** (§A.3) — the mood mismatch.
- Power sigil art for A7 and the six Curtain Call powers.
- Everything the previous sprint routed on: the fanfare arm at 1.8% under the
  2.0% floor, salon at 10.8% off its anchor, every X unswept, the
  `fanfare_weighted` A2 band, spotlight at 2.3%.

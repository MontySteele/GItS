# Sprint log — the C# bug-fix pass (2026-07-29)

Parent: the consolidated backlog (`82af10f`, `docs/backlog-2026-07-29.md`) and
the read-only sweep that produced it. Delegated IMPLEMENTATION pass: ten items
handed over as a verified list, plus four explicitly held back as design
rulings. No balance value, sheet, sim constant or piece of art was touched.

The end state is a **deployed build**, because a Furina playtest runs on it.

---

## What the verification is worth here

Three tiers, and the log says which tier every fix sits in, because they are
not the same claim.

1. **Bite-checked.** `klee-mod/build/bitecheck/` loads the built `klee.dll`
   outside Godot and runs the real Harmony bootstrap against the real
   `sts2.dll`. It proves the assembly loads and every patch class arms — it
   cannot construct a `CardPlay` or a `Creature`, so it reaches **no** behaviour
   in this sprint. Baseline and post-fix both: `14 patch class(es) armed`, no
   warning, no error.
2. **Pinned.** Three new source-level assertions in the Python suite, each
   bite-checked the house way — by reintroducing the defect and watching the
   pin fail. This is the only tier that will still be true next month.
3. **Compiled.** `dotnet build` clean, warning count unchanged from baseline
   (10 before, 10 after — one new CS8604 appeared mid-pass from a nullable-flow
   change and was fixed rather than accepted).

Nothing below is claimed as play-verified. There is no C# test project and the
sim models one seat (`docs/coop-no-sim-backstop.md`), so the co-op items in
particular are argued from the written contract, not measured.

---

## P1

### 1. The Salon counter could not go down

`SalonPowers.cs`, `SalonMemberPower.TryModifyPowerAmountReceived`.

The cap was enforced as a clamp on the **delta**:

```csharp
modifiedAmount = Math.Max(0m, Math.Min(amount, SlotsFor(target) - Amount));
```

That reads correctly for a deploy and silently destroys every bow. The company
list is authoritative and the counter mirrors it, so `BowLeftmost` applies an
always-negative delta — and `Math.Max(0m, ...)` turns every one of them into 0.
Take Your Bow (`Cards/Furina/Generated/TakeYourBow.cs`) is shipped and reaches
it. The list shrank, the counter did not, and for the rest of that combat the
badge, the stage and every per-member payer (Dinner Service, House Call) kept
counting performers who had already left.

Now clamped on the **resulting counter**, which is the invariant that was
actually meant: `[0, SlotsFor(target)]`.

```csharp
var clamped = Math.Max(0m, Math.Min(Amount + amount, SlotsFor(target)));
modifiedAmount = clamped - Amount;
```

Deploys are unaffected — for `Amount + amount <= SlotsFor` the two expressions
agree, and above it both truncate to the same headroom.

**Pinned:** `tier0/tests/test_salon_counter_clamp.py`, two rules (the clamp
must name `Amount + amount`; the old delta-clamp shape must not reappear).
Bite-checked by restoring the old expression — both rules failed, naming it.

### 2. Ownerless card plays, and the black screen

`FurinaResources.cs` (`FurinaResourceHooks.BeforeCardPlayed` /
`AfterCardPlayed`), `ElementalApplication.cs` (the Klee twins),
`SpotlightSystem.NotePlay`, `CompanionPowers.cs` (two sites).

`cardPlay.Card.Owner` is null on real paths — autoplay and token plays hand a
card to this broadcast with no `Player` attached — and these hooks fire for
**every card every player plays**. The NRE lands inside CombatManager's async
continuation, so the queue never completes: not a crash, not an error dialog, a
black screen and a dead run. The Furina file already took exactly this guard one
method away (`FurinaBurstResource.DrainOnPlay`), which is what makes it a slip
rather than a judgement call.

Seven derefs in the two Furina hooks, two in the Klee hooks. The list named
those nine; writing the pin surfaced three more of the identical class
(`SpotlightSystem.NotePlay`, `CompanionPowers` ×2), and they are fixed too
rather than curated as exceptions — a lint with a standing exception list for
its own defect class is a lint nobody believes.

Every site now binds the owner once and returns on null:

```csharp
if (card?.Owner?.Creature is not { } owner) return;
```

**Pinned:** `tier0/tests/test_card_play_hook_guards.py` — no `.Card.Owner.`
walk anywhere under `klee-mod/KleeCode` without a `?.` or a binding pattern.
Bite-checked by restoring one `CompanionPowers` deref; the pin failed and named
the file and line. The exception dict exists and is **empty**.

---

## P2

### 3. Courtroom Drama's window was the table's, not yours

`ReactionEffects.cs`. The once-per-turn gate read the **global**
`ReactionsThisTurn == 1`, so in co-op your partner's Overload consumed your
window. That directly contradicts the contract written on the function it
calls (`CurtainCallPowers.cs`, `NoteFirstReaction`): *"in co-op it means your
partner's reaction does not spend your once-per-turn window, which is the Best
Friends Forever lesson."* The code and its own doc comment disagreed; the doc
comment was right.

The distinction red-pen R1 drew is intact and deliberately untouched:
`TotalResolved` and `ReactionsThisTurn` stay **global**, because a Reaction is
a fact about the shared board. What changed is only the read Courtroom Drama
makes, because Courtroom Drama is a **power**, and a power belongs to somebody.
A new `DealerReactionsThisTurn` map counts per dealer and is cleared outright in
`MarkTurnStart` (every key is written and read inside one player turn, so there
is nothing to purge). Solo — the only configuration the sim models — this is
byte-for-byte `state.reactions_this_turn == 1`, so no sim parity moved.

`ReactionsThisTurn` is kept and re-documented rather than deleted: it is the
board-scoped reading the sim mirrors, and its doc now says in as many words
that it is *not* the Courtroom Drama gate.

### 4. `CompanionPlays` had no clearing path for a partner

`CurtainCallPowers.cs`. The map was added to the class and to `ResetTurn` but
never to `Purge`. It is also the one map a **non-Furina** player can key:
`NoteCardPlayed` records any owner's Companion play, while `ResetTurn` is only
ever invoked for Furina (`FurinaResourceHooks.BeforeSideTurnStart`). So a
partner's key had no clearing path at all — not per turn, not per combat, not
per run. Added to both halves of the sweep. The purge is the path that clears
partner keys, which is why it had to be the fix rather than an extra
`ResetTurn` call.

### 5. `SalonMemberPower.Company` never dropped a key

`SalonPowers.cs`. The comment at the stale-list check says entries are "reset",
and they are — the **list** is emptied. The `Creature` key and its `List`
object both survive, so a run left one dead entry per combat behind forever,
each one pinning a whole combat's `Creature`. Added `PurgeCompany()` in the
idiom of `FurinaResources.PurgeDeltaBlock` and `CurtainCallHooks.Purge`, wired
to the same lifecycle site those use: the top-of-player-turn sweep in
`FurinaResourceHooks.BeforeSideTurnStart`, one line above the `ResetTurn` call
whose `Purge` it now sits beside.

---

## P3

### 6. "Maximum 3" outlived the per-player cap

`SalonPowers.cs`. A12 (2026-07-28) promoted the cap from a constant to a
per-player stat (`SlotsFor`; Casting Call takes it to 5) and the tooltip kept
saying a flat "Maximum 3" — so a player who had **paid** for the bigger stage
was told, by the power itself, that the card did nothing.

Fixed with the `DynamicVar` idiom `BombPower` already uses for `{Damage}`: a
`{Slots}` var on `CanonicalVars`, a new `smartDescription` that reads it, and
`SyncSlotsDisplay(owner)` called from the three sites that already refresh the
salon — `Deploy`, `BowLeftmost`, and `FurinaResources.SyncMeters` (which runs
after every card play, so a Casting Call raise is visible the instant the card
resolves).

The plain `description` still prints the base 3, deliberately: it renders with
no instance and therefore no owner to ask. That split is the same one
`BombPower` makes and it is written into the comment so the next reader does
not "fix" it.

### 7. `CombatState.HittableEnemies` unguarded

`DemolitionPowers.cs`, `OnBombDetonated`. Neighbouring files all use
`CombatState?.`; this one did not, on a path reached from an async continuation
where a power can outlive its combat by a frame. Guarded, with the null and
empty cases collapsed into one `is { Count: > 0 }`.

### 8. One dangling anchor per Setup/Refresh cycle

`Vfx/TrackedDisplayBridge.cs`. `Track` adds a fresh `RemoteTransform2D` child
of the creature node every call; `Registry.Discard` frees the display and never
the anchor. Both bridges run `Discard -> Spawn -> Track`, so every refresh cycle
added one and freed none for the length of the combat.

Swept in `Track` rather than in `Discard`, because `Discard` is keyed and knows
no creature — it cannot reach the node the anchors hang from. Anchors are now
**named** (`KleeTrackAnchor`), and `Track` frees only its own, only when the
display they point at is gone, queued for deletion, or is the display being
re-tracked. Naming them is what makes it safe: a `RemoteTransform2D` the game
itself put on the creature node can never be touched. `IsQueuedForDeletion()`
is in the test because `QueueFree` is deferred — the just-discarded display is
still `IsInstanceValid` for the rest of the frame, which is exactly the frame
`Track` runs in.

### 9. The shop's last rung priced off the wrong rarity

`Patches/MerchantCompanionSlots.cs`. The base-colorless fallback constructed its
`MerchantCardEntry` with `rarity` while every other rung uses `chosenRarity`.

**This is a correctness repair, not a behaviour change, and the log should say
so.** Reaching that branch means no rung found candidates, and `chosenRarity`
only moves on a rung that *did* — so today the two are provably equal there. The
value of the fix is that it stops being a trap: add one more rung above that
downgrades and partially succeeds, and the old line silently prices a
downgraded card at the original rarity.

### 10. Fanfare's two mint halves rounded differently

`FurinaResources.cs`, `AfterCurrentHpChanged`. The stated rule is *"every point
of damage past Block prints exactly 1 Fanfare, through absorption if the buffer
eats it and through HP loss if HP does."* The absorption half used
`Math.Ceiling`; the HP-loss half used a truncating `(int)` cast. A fractional
HP loss therefore printed nothing through one half while the other paid for it
— the invariant held only for integers.

Now `(int)Math.Ceiling(-delta)`, computed into one local that both the mint and
Slip Backstage's `NoteHpLost` predicate read, so "how much did she lose" cannot
become two different numbers. (`NoteHpLost` shared the truncating cast; folding
both onto one local is why it moved too.)

---

## Verification

| | evidence |
|---|---|
| C# build | `dotnet build KleeCode.csproj --no-incremental`: **0 errors, 10 warnings** — identical to the pre-sprint baseline |
| bite-check | `harmony-bitecheck.exe`: `[klee] harmony: 14 patch class(es) armed.` — baseline and post-fix, silent both times |
| pins | 3 new assertions across 2 files, all 3 bite-checked by reintroducing their defect |
| suite | `python -m pytest -q` **from repo root**: **1410 passed, 1 skipped** (1407 before + the 3 new pins) |
| deploy | `tools/build_pck.ps1` then `klee-mod/build/deploy.ps1 -Configuration Release`: `validate: OK` (full local `game_ref`, S7 suite included), deployed to the game's `mods\klee` |

The deployed artefact is **0.2-247**, built from commit `29f5ce6` — a clean
tree, so no `+dirty` stamp and it is safe to hand to a co-op partner. The pck
carries build id `20260729-125659+29f5ce6`, the same commit. Only this file
moved after that build; the playtest binary is not affected by it.

---

## Still owed

Four items came in on the brief as **document, do not touch** — each is a
design ruling wearing a bug's clothes — plus what this pass could not reach.

### A. The same-broadcast ordering race: Salon upkeep vs All the World's a Stage

`SalonPowers.cs` `SalonMemberPower.AfterPlayerTurnStart` (the upkeep that
**spends** 1 Encore per member) and `FurinaResources.cs`
`EncorePerTurnPower.AfterPlayerTurnStart` (All the World's a Stage, which
**grants** `Amount` Encore) are both `AfterPlayerTurnStart` hooks on powers held
by the same creature. They run in the **same broadcast**, and their relative
order is whatever order the host happens to walk the power list in — which is
application order, i.e. the order the player happened to acquire them in that
run.

The race is not cosmetic. With 3 members and 2 Encore banked:

- **grant first**: 2 + N Encore available; up to 3 members pay and act at full
  value.
- **upkeep first**: 2 Encore available; two members act at full, the third goes
  **dry** (three-quarters), and *then* the grant lands — banked, useful next
  turn, useless this one.

So the same board produces a different turn depending on acquisition order, and
the dry/wet split is exactly the axis the member payoff is tuned on.

**Why this pass did not pick an order.** Both orders are defensible design.
"Your stage draws its salary before your patron pays you" and "the house pays
before the performers are due" are both sentences a card could print. The sim
has an order, but the sim models one seat and one acquisition sequence, so
matching it would be picking the sim's accident rather than a ruling. This
needs [USER]: name the order, and the fix is then a two-line move to distinct
broadcasts (`BeforeSideTurnStart` for whichever goes first), not an
intra-broadcast tiebreak — the mod already uses that technique twice for
exactly this reason.

### B. Standing Ovation's boost expiry

`SpotlightSystem.cs`, `ResetTurn` zeroes `SpotlightSpendBoostResource` alongside
the other per-turn spotlight state. Whether the boost the card grants is
supposed to die at the top of the next turn or persist is a card-text-vs-intent
question. Not a code defect until the intent is named; **do not** treat the
current behaviour as ratified.

### C. Salon member RNG ordering, sim vs C#

The sim and the mod draw the entering member at different points relative to
the replacement check. Balance-neutral — the distribution is identical, only
the stream position differs — so it costs nothing today. It costs something the
day a co-op desync is being bisected against sim traces. Documented, not
changed.

### D. The unlintable hand-written literals

`Cards/Furina/LetThePeopleRejoice.cs` and `AllTheWorldsAStage.cs` carry numbers
the constant-parity gate cannot see. That is parity-gate work and belongs to a
sim sprint, not to a C# bug pass.

### E. Out of scope by ruling

`unheard_confession` and the A7 Fanfare-decay/Block ordering were left exactly
as they are — the card is queued for a full design rework. Nothing in this
sprint touched the decay path.

### F. What no tier of verification here reaches

Every fix in this log is compiled, and the two P1s and the shop item are
pinned. **None is play-verified.** In particular:

- items 1, 3, 4, 5 and 6 change behaviour a player can see, and the first play
  session on this build is the first time any of them is observed;
- item 8's anchor sweep is the one to watch in the playtest — if a gauge or the
  Salon stage ever stops tracking the creature, that sweep is the first
  suspect, and reverting `Track` to its old unconditional-add shape is a
  one-line rollback that restores the leak but not the bug;
- co-op items (3, 4) cannot be exercised at all without a second seat.

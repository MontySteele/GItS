# Track A sprint log — Axis-Validity, 2026-08-04

Charter: `docs/axis-validity-session-charter.md` (RATIFIED, AV-G2 countersigned).
Brief: `docs/track-a-kickoff-brief.md`. Worktree-per-session (G4).

---

## §0. THE GRADES, RECORDED BEFORE ANYTHING ELSE WAS READ INTO THE RUN

The brief's instruction is explicit — *record grades in the sprint log before
reading anything else into the results* — so this section was written from the
first run's raw output and nothing below it was allowed to edit it afterwards.

Instrument: `tools/lint_role_tempo_coverage.py`, first run, against
`docs/role-tempo-floors.yaml` (min-of-canon, five DLL-extracted pools) and the
provisional tags in `docs/role-tempo-review.tsv`.

### P1 — **NULL. THE BINDING NULL HAS FIRED. TRACK A STOPS HERE.**

> *P1: first run fails Furina on (fanfare × frontload × fight-early) and
> (fanfare × scaling × fight-late). **Binding null:** if these cells pass as
> currently authored, the taxonomy is mis-specified and Track A returns to
> design.*

Verbatim, from the run:

```
  furina/fanfare  (31 cards)
      ok     block|early         64.5%  floor 10.2%
      ok     block|late          64.5%  floor 10.2%
      ok     block|mid           64.5%  floor  5.7%
      ok     frontload|early     80.6%  floor 21.6%
      ok     frontload|late      87.1%  floor 21.6%
      ok     frontload|mid       87.1%  floor 15.9%
      ok     scaling|late        58.1%  floor 21.6%
      ok     scaling|mid         45.2%  floor  4.5%
      ok     velocity|early      61.3%  floor  4.6%
      ok     velocity|late       61.3%  floor  6.8%
      ok     velocity|mid        61.3%  floor 10.2%
```

Both named cells **PASS**, and not narrowly: `frontload|early` clears its floor
by 59 percentage points and `scaling|late` by 36. **Furina fails nothing at
all** — all four of her declared archetypes clear all eleven mandatory cells.

Per the brief this is a STOP. No floor was adjusted, no cell was re-derived,
and no attempt was made to reach the predicted result. §3 below is diagnosis of
the null, not a repair of it.

### P2 — **CONFIRMED.**

> *P2: at least one Klee bomb cell and one Kokomi cell fail.*

Klee's bomb archetype is `demolition`, and it fails **seven** cells:

```
    klee/demolition block|early          3.6%  <  floor 10.2%
    klee/demolition block|late           0.0%  <  floor 10.2%
    klee/demolition block|mid            0.0%  <  floor  5.7%
    klee/demolition frontload|early      3.6%  <  floor 21.6%
    klee/demolition scaling|late        14.3%  <  floor 21.6%
    klee/demolition scaling|mid          0.0%  <  floor  4.5%
    klee/demolition velocity|mid         7.1%  <  floor 10.2%
```

Kokomi fails **eight** across all four declared archetypes:

```
    kokomi/assist     block|late           0.0%  <  floor 10.2%
    kokomi/assist     block|mid            0.0%  <  floor  5.7%
    kokomi/assist     scaling|mid          0.0%  <  floor  4.5%
    kokomi/commander  scaling|mid          0.0%  <  floor  4.5%
    kokomi/generic    velocity|late        0.0%  <  floor  6.8%
    kokomi/generic    velocity|mid         0.0%  <  floor 10.2%
    kokomi/priest     velocity|late        4.0%  <  floor  6.8%
    kokomi/priest     velocity|mid         4.0%  <  floor 10.2%
```

Total: **30 (character, archetype, cell) findings across Klee and Kokomi, and
zero on Furina.**

### P3 — metric reading, not a gate

> *P3: Klee multi-solve rises toward the canon floor in her rework — currently
> 9% vs canon range 29% (Regent) to 51% (Ironclad).*

The rework has not run, so this is a baseline reading only. Two numbers, and
they are not the same measurement:

| pool | AUTHORED multi-solve % | multi-solve % under this taxonomy |
|---|---|---|
| Klee | 9.2 | 44.7 |
| Furina | 40.2 | 64.6 |
| Kokomi | 55.7 | 57.4 |
| canon: Regent | — | 27.3 |
| canon: Silent | — | 37.5 |
| canon: Ironclad | — | 46.0 |
| canon: Necrobinder | — | 48.9 |
| canon: Defect | — | 51.1 |

The authored column reproduces the charter's figure exactly (Klee 9.2 ≈ 9%),
which confirms both routes are counting the same sheets. The right-hand column
is the one the lint uses, and it applies tag-through to both sides, so it is
the apples-to-apples comparison.

**On that comparison Klee reads 44.7% and is INSIDE the canon range, above
Regent (27.3) and Silent (37.5).** P3's premise — Klee sitting below the canon
floor and needing to rise toward it — does not survive the taxonomy it was
registered against. It is not graded as failed, because P3 is a metric and not
a gate, and because the rework it refers to has not happened: it is graded as
**re-based**, and the number a future rework should be read against is 44.7,
not 9. The gap the charter saw is a gap between authored tags and what the
cards actually do — which is itself a finding about the sheets, not about Klee.

---

## §1. What shipped

| item | artifact |
|---|---|
| T1 — canon baseline, DLL-verified | `tools/extract_base_game_pool.py --characters`, `tools/canon_role_tempo.py`, `game_ref/role_tempo_canon.json` (local) |
| T2 — classifier + REVIEW column | `tools/role_tempo.py`, `tools/suggest_role_tempo_tags.py`, `docs/role-tempo-review.tsv`, `docs/role-tempo-tagthrough.md` |
| T3 — baseline + floors | `docs/role-tempo-baseline.md`, `docs/role-tempo-floors.yaml` |
| T4 — coverage lint | `tools/lint_role_tempo_coverage.py`, `docs/role-tempo-debt.tsv` |

Non-goals held: no balance value moved, no card authored/reworked/re-rarity'd,
no new keyword/op/subsystem, no `combat_role` field (`solve` was extended), no
drafter read, no canon card text committed. `game_ref/` outputs stayed local.

## §2. Wiki-vs-DLL reconciliation (counts only)

Full table in `docs/role-tempo-baseline.md` §0. Headline: DLL prints
87/88/88/88/88 against the charter's wiki route's 91/92/91/91/91 — **flat 3–4
high per pool**, exactly as predicted, and flat rather than concentrated, which
is the signature of "the wiki lists a few extra" and not of "we are reading a
different pool". Every canon pool ships the identical rarity mix (20 common /
36 uncommon / 26 rare / 2 ancient), so rarity split is not an identity lever in
canon at all.

One charter figure does not reconcile with anything: the header's "402 canon
cards total", against its own per-pool wiki figures summing to 456, a DLL sum
of 439, and a draftable subtotal of 410. Carried forward flagged rather than
silently replaced. No percentage in the charter is affected — all of them are
within-pool.

## §3. Diagnosing the null — WHY Furina passes

Written after §0 was fixed, and it changes nothing in it. Four candidate
mis-specifications, in the order they should be argued about:

**(a) Tag-through unions across bands, so a carrier is credited everywhere.**
A card that deploys a Salon member inherits the member's roles at `mid` and
`late` *and* keeps its own direct roles at `early`. Furina's pool is almost
entirely carriers, so nearly every card lands in nearly every cell. Her lowest
passing cell is 34.4%; the highest canon floor is 21.6%. The taxonomy cannot
fail a pool built the way hers is, whatever the pool's real shape.

**(b) There is no magnitude gate, and the charter's own mechanism is a**
**magnitude claim.** §1.2 grades Fanfare as "a flat adder — too slow to
generate early, underwhelming damage late". Both halves are about SIZE. A
coverage lint counts cards; it cannot see that `applause_line` deals 3 or that
`1 per 4 Fanfare` pays nothing on turn one. Refusing a magnitude gate was a
deliberate non-goal (it would be authoring balance numbers), so the instrument
was built unable to test the hypothesis it was pre-registered against. That is
a specification error upstream of the code.

**(c) The floors are whole-pool canon percentages applied to an archetype's**
**sub-pool.** A canon character spreads 88 cards across everything it does; a
GItS archetype is 11–32 cards all pointed at one plan, so its per-cell density
is structurally higher. The comparison is generous to us by construction, and
the baseline doc says so — but the size of the effect (Furina clearing floors
by 40–60 points) was not anticipated.

**(d) Fanfare's derived cash-out is not actually empty, and that is real.**
The tag-through table (`docs/role-tempo-tagthrough.md`) has Fanfare cashing
into `block`, `frontload`, `velocity` at every band and `scaling` at late. The
charter's §2 diagnosis says a carrier with nothing to inherit is the disease;
by this derivation Fanfare has plenty to inherit. If (a)–(c) are repaired and
this survives, the CONSTRUCTION half of §1's verdict needs re-examining, not
the tagging.

One asymmetry worth holding onto: Klee and Kokomi fail 30 cells on the same
instrument. The taxonomy is not vacuous — it discriminates. It just does not
discriminate on the axis P1 aimed it at.

## §4. Stop-and-surface items

1. **P1's binding null (above).** Track A returns to design per the charter.
2. **The tag-through table is the arguable artifact.** Three claims in
   `tools/role_tempo.py::TOKEN_PAYOFF_POWERS` decide whether a Power *improves*
   a resource (carrier — inherits) or *is a payoff of* it (defines the
   cash-out). Get one wrong and a meter's whole column moves.
3. **`salon_member` is two tokens wearing one name.** The typed member (what
   that member does on stage) and the stage COUNTER (what `2_per_salon_member`
   and `has_salon_members` read) are different payoffs of the same deploy. Both
   are credited. If [USER] rules that double-crediting wrong, Furina's numbers
   move materially.
4. **`support` is structurally invisible on our three sheets — 0% everywhere.**
   Canon carries 2.3% in all five pools. No GItS row has an ally target, an
   ally op, or a co-op constraint, so there is nothing for a classifier to
   find. It is never linted (one-seat sim, D4), so this is a finding for the
   Kokomi rework rather than a gate.
5. **`sustain` is nearly absent from canon under a structural reading**
   (0.0–2.3%), against the charter's wiki-route claim of 1% (Silent) to 15%
   (Ironclad). The structural rule counts heals, max-HP and prevention; the
   wiki route evidently counted more. Consequence: every `sustain` cell landed
   in the identity-only list and none is linted. If sustain floors matter, that
   definition needs a ruling.
6. **`tools/extract_base_game_pool.py::_solve` contradicts charter A0.** It
   tags AoE damage as `utility`; A0 retires `aoe` as a role. NOT CHANGED — it
   feeds the reference anchors' seven-axis scores and re-tagging them would
   move measurements this track is a non-goal for. Recorded so the divergence
   is known rather than discovered.
7. **Shared schema, cross-session note.** `tempo_band:` does not exist on any
   sheet and nothing was added to one. When A-G1 closes and the field lands, it
   touches the sheet schema that `tier0/content/loader.py` and the C# codegen
   both read. That is a cross-session change and needs its note before it
   lands, not after.

## §5. The debt list, and why the suite is green

The lint exits 1 on its own. Suite-green at the track boundary is a standing
rule, and the house pattern for a gate whose findings are real but not yet
actionable is the one the Silent-anchor sprint set: **pin the known findings as
a debt list and fail only on NEW ones.** `docs/role-tempo-debt.tsv` holds the
30 findings above; `--gate` passes while the findings are a subset of it and
fails the moment a thirty-first appears or a pinned one silently disappears.

This is NOT a floors adjustment and no floor moved. It is the difference
between "we know about these thirty" and "nobody is watching". The debt list is
worthless the day P1's null is resolved and should be deleted with it.

## §6. What A-G1 most needs to look at

Ranked, from `docs/role-tempo-review.tsv` (219 rows, 135 diverging from the
authored `solve`):

1. `ENTITY_PAYOFFS` — the three typed Salon members, the bomb, the Bake-Kurage,
   the spark, the Spotlight, the aura. Seven design claims, one provenance line
   each.
2. `TOKEN_PAYOFF_POWERS` — the improver/payoff split named in §4.2.
3. The double-credit in §4.3.
4. Whether a damage card that reads a meter is `frontload`, `scaling`, or both.
   The sheets currently say all three in different places; the suggester picks
   one and 135 divergences ride partly on that choice.

---

# §7. THE REPAIR RUN — R90/R91/R92 executed (2026-08-04)

Written after the countersign package landed
(`docs/axis-validity-countersign-2026-08-04.md`). **§0 above is not edited and
must never be**: it is the grade the first run earned, and the whole point of
recording grades before reading anything into them is that a later repair
cannot go back and improve them.

## §7.1 What the repair changed, in order

| ruling | what moved |
|---|---|
| R90/1a | lint stays a counting tool; its banner now says so on every run |
| R90/1b | P1 leaves Track A for Track B; ledger line quoted below |
| R90/1c | floors re-derived from canon PACKAGES, not whole pools |
| R91/2a | seven `ENTITY_PAYOFFS` confirmed as proposed — **no code moved** |
| R91/2b | double-credit kept; every meter gains bounded/unbounded + cap |
| R91/2c | meter-reading damage = `scaling`, `frontload` iff it pays at zero |
| R91/2d | sustain bounded to your own HP ledger; joins the never-linted list |
| R92/3a | charter's "402 canon cards" corrected to 439 DLL / 410 draftable |
| R92/3b | cross-session note filed, THEN `tempo_band` landed |
| R92/3c | support gap filed to `docs/brief-kokomi-pool-fill.md`, not linted |

## §7.2 The new floors' shape

Five canon packages, membership structural off the decompiled body and
counting **both sides** of a mechanic (the card that applies Poison and the
card that reads the stack are both poison cards — the first extraction only
recorded the generate side, which is why the packages had to be rebuilt rather
than filtered out of the existing JSON):

| package | character | cards |
|---|---|---|
| `silent_poison` | Silent | 12 |
| `defect_orbs` | Defect | 41 |
| `necro_summons` | Necrobinder | 22 |
| `ironclad_strength` | Ironclad | 8 |
| `regent_forge` | Regent | 19 |

8–41 cards against archetypes at 11–32. **That is the repair**: §3(c)'s
diagnosis of the null named the population mismatch and this is it closed.

Eight archetypes are anchored to the package shaped like them; four are not,
and the four absences are stated in `ARCHETYPE_ANCHORS` rather than left to be
discovered, because an unanchored archetype gets the four lax default cells
and that SILENCES findings. Necrobinder's summon-payoff shape **stays Furina's
designated anchor**, exactly as charter A1 named it; only the population under
it narrowed from the whole pool to the package.

The default floor set is four cells — `frontload` at all three bands and
`scaling|late`. That is a finding, not a weakness: across five canon packages
the only universally-covered jobs are *deal damage at every band* and *scale
late*. Everything else is identity.

## §7.3 The lint re-run

**19 findings**, down from 30, across three characters.

| character | findings | archetypes |
|---|---|---|
| Furina | 2 | salon 1, spotlight 1 |
| Klee | 11 | demolition 6, reaction 3, spark 2 |
| Kokomi | 6 | priest 6 |

### Furina's fanfare cells under package floors — REPORTING, NOT A PREDICTION

Quoted verbatim, and quoted because the first run's fanfare reading is the
thing this whole repair was ordered against:

```
  furina/fanfare  (31 cards)  -- anchor silent_poison (n=12)
      ok     block|late          64.5%  floor  8.3%
      ok     frontload|early     80.6%  floor  8.3%
      ok     frontload|late      83.9%  floor 16.7%
      ok     frontload|mid       83.9%  floor  8.3%
      ok     scaling|late        80.6%  floor 41.7%
      ok     scaling|mid         80.6%  floor  8.3%
```

**The fanfare archetype still fails nothing**, on repaired floors, against the
canon package whose shape it actually resembles — a counter that accrues off
other plays and is cashed by readers. `scaling|late` reads 80.6% against a
41.7% floor: the bar is nearly double what it was (21.6 → 41.7) and the
coverage went UP too, because R91/2c gave nineteen meter-reading damage cards
their `scaling` tag.

**This is a REPORT and it re-registers nothing.** Per R90/1b the Fanfare
size-and-timing question now lives in Track B, and P1's ledger line reads:
*"aimed at the wrong instrument; withdrawn and re-registered, not failed."*
The correct reading of the table above is **"the payoff cards exist"** — which
was never in dispute after the first run, and which is precisely why the
question moved. A coverage lint cannot see that `applause_line` deals 3, and
under R90/1a it never will.

Furina's two real findings are elsewhere and both are new:

```
    furina/salon      frontload|late      67.9%  <  floor 68.2%
    furina/spotlight  scaling|late        61.1%  <  floor 75.0%
```

The salon miss is **0.3 points** — one card in twenty-eight — and is reported
at that precision rather than rounded into comfort or out of existence. The
spotlight miss is real: 61.1 against an Ironclad-strength package that spends
75% of itself on late scaling, which is what a pure multiplier package looks
like.

## §7.4 The debt list: 30 → 19, and NOT ONE GAP WAS FIXED

The single most misreadable diff in this branch. **Seventeen pins dropped and
six appeared, and no card changed to cause any of it.** The instrument changed
subject.

**Dropped because the archetype stopped being measured** (unanchored → four
lax default cells): all seven `klee/generic`, both `kokomi/generic`, all three
`kokomi/assist`, and two of the five `klee/reaction`.

**Dropped because the floor itself moved down** under the package population:
`klee/demolition scaling|late` (floor 21.6 → 4.5), `klee/spark scaling|late`
(21.6 → 10.5), `kokomi/commander scaling|mid` (4.5 → not mandatory for the
Forge/Stars package, which sits at zero there itself).

**Added because the floor moved UP**, i.e. the archetype is now measured
against something genuinely shaped like it: `furina/salon frontload|late`,
`furina/spotlight scaling|late`, and four `kokomi/priest` cells (`block|late`,
`block|mid`, `frontload|late`, `scaling|late`) — the orb package is 41 cards
and dense, and the Bake-Kurage archetype is being asked to look like it.

Per R90/1a the pinned gaps are real and stay pinned; the gate fails only on a
NEW finding or a stale pin. The debt file's own header now carries the
"30 → 19 was not eleven wins" sentence, and a test pins that sentence, because
a comment nobody is forced to keep is a comment that gets deleted.

## §7.5 Tag landing

219 rows, all three sheets, both fields, machine-written by
`suggest_role_tempo_tags.py --land`. **135 divergences resolved to zero** — not
by argument, by landing: the sheets and the classifier are now the same
statement, `diverges` reads empty on every row, and `--check` fails on any
hand edit that forks them again.

**No hand-rulings remain.** Every one of the 135 was settled by a rule:

- **19 by R91/2c directly** — the meter-reading damage question. 15 gained
  `scaling` beside `frontload`; 4 lost `frontload` outright
  (`the_final_verdict`, `pearl_barrage`, `undertow`, `depths_judgment`)
  because they deal nothing on an empty meter.
- **The rest by tag-through**, which was never a divergence in the first
  place: no sheet row had ever been tagged with what its token cashes into, so
  every carrier diverged by construction and that IS A0.1 doing its job.

## §7.6 Answers to §4's stop-and-surface list

1. **P1's null** — discharged by R90. Not repaired, *redirected*.
2. **The tag-through table** — reviewed and confirmed at A-G1 (R91/2a).
3. **`salon_member` double-credit** — KEPT (R91/2b), with the
   bounded/unbounded property as the amendment and a Track B fill-time
   measurement pre-registered against it.
4. **`support` 0% everywhere** — R92/3c, filed to the Kokomi brief as
   not-linted rework input.
5. **`sustain` nearly absent from canon** — this was the item that asked for a
   ruling and got one: R91/2d. Never linted; zero sustain is a legal identity.
6. **`extract_base_game_pool::_solve` disagrees with A0** — STILL OPEN,
   deliberately. It feeds the reference anchors' seven-axis scores and
   re-tagging them would move measurements this track is a non-goal for. The
   two classifiers coexist and the divergence stays recorded.
7. **Shared schema note** — filed before the field landed (§8 below), mirrored
   in `docs/roster-codegen.md`.

## §7.7 New this run

**`disrupt` has no `solve` value of its own.** R91/2d names disrupt as where
enemy-output reduction lives, and in this implementation Weak and Frail are
the sheets' `utility` voice — protected free space, never linted. The ruling's
load-bearing half (*they are not sustain*) therefore already holds without a
sixth role. Minting one would be a new vocabulary value on three ratified
sheets, outside this repair's scope. Recorded here and beside `NEVER_LINTED`
rather than silently collapsed; the question a sixth role would have answered
is Track B's HP trajectory.

## §7.8 Track B pre-registrations from this pass

Not measurements, not predictions — conditions filed where Track B will meet
them.

1. **Salon fill-time** (R91/2b): the turn the Salon first fills, and the
   fraction of fight-turns it sits full. Revisit condition: if bounded-meter
   readers plateau early on the output curves, the `scaling` tag for those
   readers is re-argued WITH DATA. Not before.
2. **Fanfare size and timing** (R90/1b): re-registered in the playtest's own
   words — *too slow to generate early, underwhelming damage late*. Instrument:
   produced damage and block per turn against demanded per turn.
---

# §8. CROSS-SESSION NOTE — the card-sheet schema gains `tempo_band` (2026-08-04)

Filed BEFORE landing, per R92/3b and the standing rule that a change to a
shared loader takes its note first (`tier0/DECISIONS.md`:431, and the house
pattern in `docs/animation-sprint-2-log.md`). The mirror of this note is in
`docs/roster-codegen.md`.

**Who reads the surface.** The three card sheets are read by TWO independent
consumers, and both of them hard-fail on a field they do not know:

1. `tier0/content/loader.py` → `Card.from_dict`, which raises
   `unknown fields [...]` for anything not declared on the `Card` dataclass in
   `tier0/engine/state.py`. That refusal is deliberate (a sheet row declaring a
   field that does nothing is a card whose author believes it does something).
2. The C# codegen, `tools/gen_klee_cards.py::CARD_FIELDS` → `card_level_reason`,
   which returns `card field(s) [...] not understood` and BLOCKS the card. Two
   fields have already been caught by exactly this gate — `innate` (A9) and
   `retain` (Fanfare rework Track C.1) — and in both cases the block was the
   design working.

So adding a field to a sheet without touching both is not a cosmetic change:
it is a hard loader failure on one side and a blocked card on the other.

**What is changing.** `tempo_band:` lands on all 219 rows of
`docs/klee-cards.yaml`, `docs/furina-cards.yaml` and `docs/kokomi-cards.yaml`.
It carries two orthogonal scales, per charter A0:

```yaml
tempo_band: {fight: [early, mid], run: [early]}
```

`fight` ∈ {early, mid, late} — when in a FIGHT the card is worth playing.
`run` ∈ {early, late} — when in a RUN it is draftable and functional.
Multi-band is legal and normal; a scaling Power is fight-late and must be
run-early-draftable to be assembled by Act 2, and saying both is the point of
the axis.

**What is NOT changing, and this is the reason the note is short.** The field
is **inert on both readers**:

- `Card.tempo_band` is a plain declared field with an empty-dict default. No
  engine code reads it. It is descriptive metadata of exactly the kind
  `register` and `solve` already are.
- `CARD_FIELDS` gains `"tempo_band"` in the descriptive/draft-metadata block
  beside `register`. Nothing is emitted from it, so no generated C# changes and
  no manifest number moves.

No op is added, no keyword is added, no subsystem is added. Every value is
machine-derived by `tools/role_tempo.py::fight_bands` / `run_bands` and written
by `tools/suggest_role_tempo_tags.py --land`; `--check` fails if a hand edit
moves one away from the rule that produced it, so the field cannot rot into
prose.

**Who is affected right now.** The Understudy Phase-0 sprint is live in a
parallel worktree on `understudy/`, a vendored STS2MCP bridge, and a C# speed
patch. None of those surfaces is touched here. If that stream regenerates card
C# it will pick up an unchanged manifest; if it loads the sim it will pick up
one more inert field. Neither needs action.

**Verification owed by the landing commit** (and paid): the suite proves BOTH
readers handle the field — the sim loads all three sheets, and the codegen
`--check` reports the same manifest counts as before the field existed.

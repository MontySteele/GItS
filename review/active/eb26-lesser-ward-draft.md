# EB-26 / P4 — the Kokomi lesser ward, DRAFT candidate

> **DRAFT ONLY. NOTHING HERE IS RATIFIED AND NOTHING HERE IS IN THE MEASURED
> POOL.** No row was added to `docs/kokomi-cards.yaml`, no delta to
> `docs/kokomi-upgrades.yaml`, no C# was generated, no art was claimed. An
> unratified card in the sheet enters every drafting arm and moves every
> Kokomi number in the repo, which is the opposite of what a candidate is for
> — the same posture `brief-kokomi-pool-fill.md` took for its 15 proposals.
>
> Drafted under BACKLOG `EB-55`. The ratify / revise / drop call is QUEUE
> `EB-26`, and it is [USER]'s.

---

## 1. What P4 is

`P4` is the fourth ruling ask of the **Kokomi v0.2 sheet pass**, §4
(`git show pre-simplification-2026-08-06:docs/archive/kokomi-sheetpass-v0.2-report.md`,
§4). Verbatim:

> **P4 — prevention on curve (stability band).** An uncommon lesser ward
> (e.g., 3, same latch) so the stability identity exists before a Rare shows.
> The probe says defense alone fixes nothing — this is for the band's sake
> AFTER P1/P2 land, not the wall's.

Its status is recorded in the recap audit
(`docs/archive/missed-requirements.md` §3.2): **P1 / P2 / P5 landed in v0.3;
P4 did not.** The audit's evidence of absence, re-verified against HEAD this
pass:

| claim | HEAD today |
| --- | --- |
| the only `prevent_exhaust_ward` in her pool is `vigil_of_the_deep`, **rare** | still true — one row, `docs/kokomi-cards.yaml:556`, `rarity: rare`, `cost: 2` |
| the R58 +20-card fill added none | still true |
| `kurages_oath` is Block-per-pulse, a different mechanic | still true (`power: kurage_ward`) |

And a stronger form of the same finding, computed over the sheet this pass:
**`vigil_of_the_deep` is the only card in the entire 61-row Kokomi pool
carrying `solve: [sustain]`.** Her whole declared sustain identity — LAW 2's
substitute for the healing she is forbidden ("her sustain fantasy is
prevention (the ward) + the stability band", sheet header) — hangs off one
Rare. A player who never sees that Rare never meets the identity.

"On curve" therefore means two things at once, and the candidate has to do
both: **available at a rarity that shows up in act 1** (uncommon, not rare),
and **cheap enough to be online while act-1 bills are being paid** (a cost
step under the Rare).

---

## 2. The candidate (paste-ready)

Insert into `docs/kokomi-cards.yaml` in the uncommon **`# Generic (2)`**
block, immediately after `pearl_current` and before `the_tide_remembers`:

```yaml
# --- EB-26 / P4 candidate: the lesser ward (DRAFT, unratified) ---
- {id: watch_of_the_shallows, name: "Watch of the Shallows", cost: 1, type: power, rarity: uncommon, solve: [sustain], tempo_band: {fight: [mid, late], run: [early, late]}, archetypes: [generic], role: payoff,
   effects: [{op: apply_power, power: prevent_exhaust_ward, amount: 3, target: self, max_stacks: 6, note: "first unblocked hit each turn: prevent up to 3, Exhaust a random draw-pile card"}]}
   # P4, the LESSER WARD (kickoff §2.4 band; sheetpass v0.2 §4 P4 asked for "an uncommon lesser ward, e.g. 3,
   # same latch" so the stability identity exists before a Rare shows). Same power, same once-per-turn latch,
   # same price in future draws — half the magnitude of vigil_of_the_deep and a cost step under it, so the Rare
   # keeps the premium read and this is the on-curve one. The proc is still an Exhaust -> Charge: getting
   # attacked fuels the finisher from act 1, not from whenever a Rare shows.
   # max_stacks 6 is the POOL'S ward ceiling, not this row's amount. apply_power clamps the TOTAL, so a lower
   # cap here would make this card LOWER a standing Vigil when played after it; at 6 it can only ever top up,
   # and a doubled-up ward stops exactly where the Rare already prints.
```

And into `docs/kokomi-upgrades.yaml`, in the `# ---- UNCOMMONS ----` block
(after `tidal_lure`):

```yaml
watch_of_the_shallows: {power_amount: +2}   # ward 3->5. max_stacks does NOT ride along here (the applier only
                                         # carries the cap when cap == amount, and this row's cap is the pool's
                                         # ward ceiling, not its magnitude) — so the upgrade buys magnitude and
                                         # the ceiling stays exactly where the Rare put it.
```

**Card face, as the player reads it:** *Watch of the Shallows* — Power, 1
energy, Uncommon. "The first time each turn an attack would deal unblocked
damage, prevent up to 3 of it and Exhaust a random card from your draw pile."
Upgraded: 5.

**Partial upgrades are forbidden** (`docs/roster-codegen.md`, "Honesty
rules"), so the candidate ships with its complete ruled delta rather than
landing on `upgrades.no_upgrade_path`. `power_amount` is the same delta key
`vigil_of_the_deep` and `mercy_of_the_deep` already use, and it is machine-
verified to apply in §4 below.

---

## 3. Why this row, and not another

### 3.1 It is the ask, executed literally

`3`, uncommon, same latch, same power. P4 named a magnitude and a rarity; the
only things the draft added are a cost, a lane, a name, a cap and an upgrade —
each of which is called out as a sub-decision in §5.

### 3.2 It is on-idiom, and it is not a second Vigil

Same `prevent_exhaust_ward`, same once-per-player-turn latch
(`prevention_used_this_turn`), same price in future draws. That is deliberate:
P4 says *"same latch"*, and a lesser ward built out of a different verb would
have taught a second rule for the same fantasy. What differs is magnitude
(3 vs 6) and cost (1 vs 2), which is the rarity ladder doing its job — the
Rare keeps the premium read.

Both structural guards the sheet cites for the ward class still hold at
uncommon:

- **LAW 4 breaks the invincibility loop at Common.** This is uncommon, so
  LAW 4 is not the binding guard here — but the candidate creates no cards at
  all, so it is trivially inside it either way (machine-checked, §4).
- **The once-per-turn latch breaks it at the power.** Unchanged, and now
  doing more of the work than it did when the only ward was Rare-gated. This
  is the real reason the magnitude is 3 and not 6: the latch caps *frequency*,
  so the only dial left for the rarity step is *size*.

The proc is still an Exhaust routed through the relic funnel, so it is still
Charge — the kickoff §2.4 identity ("getting attacked fuels the finisher")
now reaches the player in act 1 instead of only after a Rare.

### 3.3 It respects the pool's standing laws

| law | candidate |
| --- | --- |
| **LAW 1** no self-damage | no damage op at all |
| **LAW 2** no heals, ever | prevention, not healing; the HP bar does not move up |
| **LAW 3** no Strength | none |
| **LAW 4** commons net card delta <= 0 | uncommon, and net delta 0 regardless |
| **LAW 5** economy riders are Sly/discard's monopoly | no rider of any kind — one line, one power |
| **R51** Weak/Vulnerable only as exhaust/Sly riders | applies neither |
| **R80** Charge is never spent | reads nothing, spends nothing |
| **Voice law** Exhaust is rotation, not sacrifice | the note is `vigil_of_the_deep`'s wording verbatim, which is already voice-cleared |
| **No Furina / no Klee grammar** | no `salon_*`, no `copy_*`, no bombs, no Sparks |

### 3.4 Neighbours in the pool

Every power Kokomi owns, for the comparison [USER] is being asked to make:

| card | rarity | cost | effect | lane |
| --- | --- | --- | --- | --- |
| `kurages_oath` | common | 1 | `kurage_ward` 5 (Block per Kurage pulse) | priest, generic |
| `before_sun_and_moon` | uncommon | 1 | `kurage_amp` +1 (pulse multiplier) | priest, generic |
| `mercy_of_the_deep` | uncommon | 1 | `feel_no_pain` 3 (Block per exhaust) | priest |
| `pearl_current` | uncommon | 1 | `metallicize` 3 (Block each turn) | generic |
| **`watch_of_the_shallows`** | **uncommon** | **1** | **`prevent_exhaust_ward` 3** | **generic** |
| `vigil_of_the_deep` | rare | 2 | `prevent_exhaust_ward` 6 | priest, generic |
| `epiphany_of_the_deep` | rare | 2 | draw engine | priest, assist |

The nearest neighbour is `pearl_current`: same rarity, same cost, same lane,
and a comparable magnitude. They are **not** the same card and neither
dominates the other:

- `metallicize` 3 is unconditional and stacks with Block; the ward only fires
  on damage that got *past* Block. As raw mitigation `pearl_current` is the
  more reliable card, and it should stay so — it is the generic lane's
  do-nothing floor by design.
- The ward pays where `metallicize` cannot: it is *sized to the hit*, it feeds
  Charge every time it fires, and it is the only card in the pool that
  converts being attacked into engine. That is the identity `pearl_current`
  does not carry and cannot be asked to.

`vigil_of_the_deep` at cost 2 sits in a different cost group, so the pair is
structurally incomparable to the domination lint and — more importantly — is a
real draft question rather than a strictly-better answer: half the ward for
half the energy, and they stack toward one ceiling (§5, D2).

### 3.5 Where it puts the pool

61 rows (5 basic / 27 common / 19 uncommon / 10 rare) -> **62** (5 / 27 / **20**
/ 10). The pool-fill brief's target shape is 76 (5 / 31 / 25 / 15), so this is
one row of a gap that stays open; EB-26 is a *requirement* being discharged,
not a fill pass.

---

## 4. Machine-check evidence

The candidate was spliced into a **shadow `docs/` tree** in the scratchpad —
the repo's own sheets were never modified — and every gate that reads a card
sheet was pointed at the shadow. Harness:
`scratchpad/check_eb55.py` + `scratchpad/probe_runtime.py` (temp artifacts,
not committed, per the norm that raw check output is PR text).

```
[PASS] YAML parses; candidate row present
[PASS] loader builds the Card (effect vocabulary + unique ids)
        id=watch_of_the_shallows cost=1 type=power rarity=uncommon character=kokomi archetypes=['generic']
[PASS] pool size after fill              kokomi rows: 62
[PASS] upgrade delta is applicable and lands
        has_upgrade=True  upgraded amount=5  max_stacks=6
[PASS] engine op registered for the row's power
[PASS] solve: tag matches role_tempo's classifier   classifier=('sustain',) sheet=['sustain']
[PASS] tempo bands are in vocabulary     {'fight': ['mid','late'], 'run': ['early','late']}
[PASS] lint_strict_domination (shadow sheets, cross-sheet pass ON)
        CLEAN over 250 compared card(s) in 6 sheet(s)
        kokomi-cards.yaml  56/62 compared
[PASS] lint_sheet_comments (shadow kokomi sheet)     CLEAN
[PASS] lint_kokomi_decksize (shadow kokomi sheet)    no findings
[PASS] lint_unique_names (shadow sheets + relics)
        OK: 271 card + 6 relic names unique across 6 sheet(s), reserved list honored
[PASS] lint_upgrade_comment_arithmetic (shadow upgrades sheet)
        64 pair(s) recomputed, 0 findings

SUMMARY: ALL CHECKS PASS
```

Notes on what each of those actually buys:

- **`lint_unique_names`** covers the reserved list
  (`docs/reserved-card-names.txt`, 131 entries incl. the Silent's full base-game
  pool) and the C# relic display names, not just the card sheets — so
  "Watch of the Shallows" is clear of the *player-facing* namespace, which is
  the R69 scope. It is still not naming-audited; that is [USER]'s (§5, D1).
- **`lint_strict_domination`** ran with the cross-sheet pass on, i.e. the
  candidate was compared against Klee, Furina and all three companion sheets,
  not only its own.
- **`role_tempo`** already maps `prevent_exhaust_ward -> ("sustain",)`, so the
  `solve:` tag is the classifier's own answer rather than an authored guess.
  `sustain` is in `NEVER_LINTED` (R91/2d), so the coverage gate has and will
  have no opinion about this row either way.

### 4.1 Runtime probe — the card actually works, and the cap matters

Played through `combat.play_card` on a real Kokomi state:

```
after play: ward stacks = 3
hit 8 with ward 3: hp 70 -> 65 (prevented 3), draw pile 5 -> 4, exhaust pile 1
vigil alone: 6
vigil then candidate (max_stacks 6): 6      <- must not drop below 6
vigil then a max_stacks-3 variant: 3        <- the downgrade trap
three copies of the candidate: 6            <- capped at the Rare's 6
```

The third line is the load-bearing one and it is why `max_stacks: 6` is on a
card whose amount is 3. `powers.apply_power` clamps the **running total**, not
the increment (`tier0/engine/powers.py:183`). A lesser ward carrying its own
magnitude as its cap would therefore **reduce a standing Vigil from 6 to 3
when played after it** — a card that is a downgrade to play, discoverable only
by a player who drafts both. At 6 the cap is the *pool's ward ceiling*: the
lesser ward can only ever top up, and no number of copies exceeds what the
Rare already prints.

### 4.2 What was NOT checked, because a draft cannot be

These are ratification work, listed so the gap is explicit rather than
discovered later:

- **Codegen.** `tools/gen_roster_cards.py --check` compares committed C#
  against the sheet; a card that is not in the sheet has no C# and cannot be
  checked. Ratification means generating `WatchOfTheShallows.cs`, the
  `KokomiCardRoster` entry and the `manifest.json` row, then re-running the
  parity + `lint_generated_structure` + `lint_pool_membership` +
  `lint_upgrade_coverage` layer-2/3 gates against the emitted C#.
- **Art.** No `art/plan.tsv` row, no `art/SOURCES.tsv` claim, so
  `tools/art_coverage.py` would report the card uncovered. Kokomi's art
  scarcity is a known standing constraint.
- **Measurement.** No DRAFTER number is quoted anywhere in this packet, on
  purpose: the card is not in the pool, so no arm has been re-measured, and
  any winrate claim here would be invented. Whether ratification triggers a
  re-baseline is [USER]'s call (§5, D7).

---

## 5. Open sub-decisions for [USER]

Each of these is a place the draft had to choose something P4 did not specify.
None is settled here.

**D1 — the name.** `Watch of the Shallows`, deliberately built as the lesser
twin of `Vigil of the Deep` (shallows/deep, watch/vigil). It is authored
flavor, not wiki-verified canon; the naming audit is [USER]-only. It is clear
of the internal + reserved namespaces (§4).

**D2 — `max_stacks: 6` on an amount-3 card.** Recommended, with the §4.1
evidence: it is the only value at which the card cannot be a downgrade to
play. The cost is that copy count now matters up to the ceiling — two Watches
equal one Vigil's magnitude for the same total energy across two cards and two
draft picks. `vigil_of_the_deep`'s own comment says "the magnitude is the
knob, not the copy count", and this bends that (bounded by 6, never past it).
Alternative: `max_stacks: 3`, which honours the no-stacking line strictly and
accepts the trap. **A third option exists and is not drafted:** re-read
`max_stacks` as a per-application cap in the engine, which would fix the class
rather than this card — that is engine surgery on a shipped power and belongs
in BACKLOG if it is wanted, not smuggled in under a card ratification.

**D3 — magnitude and cost: 3 at 1 energy.** P4 said "e.g., 3". Against
`pearl_current` (`metallicize` 3, same rarity, same cost) the ward is the less
reliable mitigation, so 3-at-1 may read a touch shy. The dials: amount 3 -> 4,
or cost 1 -> 2. **Cost 2 is not neutral** — it would put the candidate in
`vigil_of_the_deep`'s cost group and make the pair comparable to the
domination lint, and it would cost the card its "on curve" claim.

**D4 — lane: `archetypes: [generic]`.** Drafted generic-only so the stability
band belongs to *any* Kokomi deck, and because the pool-fill brief's census
calls priest "the finished lane" (25 cards, 7 rares) and proposes no
priest-exclusive card. The alternative is `[priest, generic]`, mirroring
`vigil_of_the_deep` exactly, on the argument that the ward's exhaust proc is
priest fuel. Either passes the gates.

**D5 — `tempo_band: {fight: [mid, late], run: [early, late]}`.** `run: early`
is P4's whole point and is not really optional. `fight: [mid, late]` is the
debatable half: *every other* Kokomi power is tagged `fight: [late]`, and this
row claims the earlier band on the strength of one energy less than the Rare.
Cosmetic today — `sustain` is never linted — but it is an authored claim about
when the card pays, and it will be read as one.

**D6 — upgrade `power_amount: +2` (ward 3 -> 5).** Matches
`vigil_of_the_deep`'s +2 slope; `mercy_of_the_deep`'s comparable power delta
is +1. At +2 the upgraded lesser ward (5) sits just under the unupgraded Rare
(6), which is the intended shape. Resource-curve law is not engaged (no Charge
line to move).

**D7 — scope of the ratification.** Two questions the drafting could not
answer: (a) does ratifying this trigger a Kokomi re-baseline, or does the card
land and wait for the next scheduled measurement? (b) `missed-requirements.md`
§3.2 names **P3** in the same finding — "a ticking body for the commander", no
persistent recruit above the basic `bake_kurage`, *and neither P3 option was
ever explicitly chosen*. P3 is out of `EB-26`'s scope as written; it is still
open, and it is still nobody's.

---

## 6. If ratified — the execution checklist

Recorded so the ratify call knows what it is buying:

1. Paste the two blocks in §2 into `docs/kokomi-cards.yaml` and
   `docs/kokomi-upgrades.yaml` (encoding declared, no BOM).
2. `tools/gen_roster_cards.py` for Kokomi -> `WatchOfTheShallows.cs`,
   `KokomiCardRoster`, `manifest.json`; then `--check`.
3. Roster registry / pool-membership rows so the card is reachable from
   `KokomiCardPool` (`lint_pool_membership` is a shipped-crash gate, not a
   style check).
4. `art/plan.tsv` row + a claimed source, or an explicit art debt entry.
5. Full gate wall: `python -m pytest tier0/tests tier05/tests -q`.
6. Whatever D7 rules about re-measurement.

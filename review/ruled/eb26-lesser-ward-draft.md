Status: RULED (see RULINGS.md)

# EB-26 / P4 — the Kokomi lesser ward, LANDED

> **STATUS 2026-08-10: D2 RESOLVED and the candidate LANDED.** [USER] ruled
> D2 as **option (d)**, the floor-not-clamp apply mode (§7.2(d)), and
> `watch_of_the_shallows` is now a real row in `docs/kokomi-cards.yaml` with
> its upgrade in `docs/kokomi-upgrades.yaml`, its generated C#
> (`WatchOfTheShallows.cs`), and the engine + mod support the mode needed. §8
> is the landing record; §1–§7 are kept as written, as the drafting record
> that the ruling answers.
>
> **Still open after this landing** — D1 (the name, an eye-read only [USER]
> can do), D7(b) (P3 is unowned), and the re-baseline, which QUEUES BEHIND
> EB-22 (§8.5). Drafted under BACKLOG `EB-55`; the ratify call was QUEUE
> `EB-26`.

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

**This probe used the UNUPGRADED Rare only. The upgraded Rare is ward 8 / cap
8, and against it the conclusion below does not hold — see §7.**

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

---

## 7. D2 addendum (2026-08-10): the upgraded Vigil

§4.1 probed the wrong Vigil. It only played the **unupgraded** Rare — ward 6,
cap 6 — and concluded that `max_stacks: 6` on the candidate "can only ever top
up". That conclusion is false as soon as the Rare is upgraded.

`vigil_of_the_deep+` is ward **8**, cap **8** (`docs/kokomi-upgrades.yaml:147`;
the applier carries the cap along because this row encodes cap == amount,
`tier0/content/upgrades.py:509-511`). The engine clamps the **running total**,
not the increment (`tier0/engine/powers.py:182-184`: `new = min(existing +
stacks, max_stacks)`). So a candidate whose cap is 6, played on top of a
standing 8, sets the ward **down to 6**. The player loses 2 prevention by
playing a card.

Re-probed with the real applier and real `combat.play_card` on a
loader-built Kokomi (scratchpad harness, not committed).

### 7.1 The full interaction matrix

Printed statlines, as the applier produces them:

| card | ward amount | `max_stacks` |
| --- | --- | --- |
| `vigil_of_the_deep` | 6 | 6 |
| `vigil_of_the_deep+` | 8 | 8 |
| candidate (as drafted) | 3 | 6 |
| candidate+ (as drafted) | 5 | 6 |

Ward stack after the first card, then after the second. Both orders, all four
pairs:

| order | after 1st | after 2nd | |
| --- | --- | --- | --- |
| `vigil` -> candidate | 6 | **6** | no change (3 would overflow the cap) |
| candidate -> `vigil` | 3 | 6 | top-up, as intended |
| `vigil` -> candidate+ | 6 | **6** | no change |
| candidate+ -> `vigil` | 5 | 6 | top-up |
| **`vigil+` -> candidate** | 8 | **6** | **DROP of 2** |
| candidate -> `vigil+` | 3 | 8 | top-up |
| **`vigil+` -> candidate+** | 8 | **6** | **DROP of 2** |
| candidate+ -> `vigil+` | 5 | 8 | top-up |

Copies of one card, played four times in a row:

| card | stacks after each play |
| --- | --- |
| candidate (cap 6) | 3, 6, 6, 6 |
| candidate+ (cap 6) | 5, 6, 6, 6 |
| `vigil` | 6, 6, 6, 6 |
| `vigil+` | 8, 8, 8, 8 |

So the defect is exactly two cells wide, and it is order-dependent: it fires
only when the **upgraded** Rare is standing and the candidate is played after
it. Nothing else in the table moves.

**One more thing the matrix does not show, and D2 has to know it:** the C#
side does not implement the sim's rule at all. `PreventExhaustWardPower`
(`klee-mod/KleeCode/Powers/KuragePowers.cs:566-596`) derives the cap from the
incoming application — it subtracts the standing amount from the incoming one,
so the power always **becomes** whatever the last card printed. In the mod,
`vigil+` (8) then the candidate (3) would leave **3**, not 6, and three copies
of the candidate would leave 3, not 6. That class also carries the Rare's own
title and text in its tooltip ("Vigil of the Deep"), so a second card applying
the same power shows the Rare's name in the power display. Whichever of the
options below is picked, the C# power is part of the work.

### 7.2 The four options, re-costed against cap 8

#### (a) Raise the candidate's `max_stacks` to 8

Probed: with the candidate at cap 8, every drop disappears. `vigil+` ->
candidate is 8 -> 8; `vigil` -> candidate is 6 -> 8 (a real top-up from the
lesser card). But the ceiling moves for the lesser card **alone**, and it now
climbs there on copy count:

| card, played repeatedly | stacks after each play |
| --- | --- |
| candidate at cap 8 | 3, 6, **8**, 8 |
| candidate+ at cap 8 | 5, **8**, 8, 8 |

So yes: the lesser uncommon alone banks the upgraded Rare's number — **three
copies unupgraded, two copies upgraded**. That is the thing `vigil_of_the_deep`'s
own sheet comment refuses ("the magnitude is the knob, not the copy count"),
now reaching the Rare's *upgraded* magnitude off uncommons.

There is also a hard blocker in the toolchain. The codegen registry stores
**one cap per power id** and cross-checks every sheet row against it
(`tools/gen_klee_cards.py:470` registers `prevent_exhaust_ward` at 6;
`:1183-1189` raises `SystemExit` when a row disagrees). Two rows of the same
power with different caps cannot both pass. Option (a) therefore also requires
a decision about what the registry cap becomes, and a matching change to the
C# power.

#### (b) Keep `max_stacks: 6`, accept the trap, document it

Nothing changes in code or sheets. Two cells of the matrix stay wrong: a
player holding an upgraded Vigil loses 2 ward by playing the lesser card.
It is silent — no message, no preview — and it is only reachable by a player
who drafted both cards and upgraded the Rare.

#### (c) Re-read `max_stacks` as a per-application cap (engine surgery)

D2's "third option". Instead of clamping the running total, clamp only the
incoming amount, then add — or, in the shape the C# already uses, let the cap
mean "one application may not exceed this". The one-line site is
`tier0/engine/powers.py:182-184`.

The blast radius, enumerated honestly. **Code that would change or need a
ruling:**

1. `tier0/engine/powers.py:182-184` — the clamp itself. The only place the
   running total is bounded.
2. `tier0/engine/effects.py:881, 927-928, 948-949` — `_op_apply_power`, the
   **only** caller that ever passes `max_stacks` (self branch and enemy
   branch). Every other `apply_power` caller — relics, potions, companions,
   intents, `refpowers` — passes nothing and is unaffected.
3. `tier0/content/upgrades.py:506-511` — the "cap rides along when cap ==
   amount" branch. Its whole justification is the running-total reading; under
   a per-application reading, cap == amount means something different and the
   branch needs re-ruling.

**Content that relies on the current reading:**

4. `docs/kokomi-cards.yaml:557` — `vigil_of_the_deep` is the **only live row in
   all six sheets** carrying `max_stacks`. Furina's caps were dropped by the
   2026-07-24 ruling and survive only as comments
   (`docs/furina-cards.yaml:773-775`). So the content blast radius is one row,
   plus this candidate if ratified.
5. `docs/kokomi-upgrades.yaml:147` — the cap-rides-along delta for that row.

**Tests that pin the current reading (all would fail, each needs a re-rule,
not a re-baseline):**

6. `tier0/tests/test_pin_engine_powers.py:59-70` —
   `test_capped_power_stops_at_max_stacks_across_applications`, which asserts
   the running-total meaning in its name.
7. `tier0/tests/test_pin_engine_powers.py:72-80` —
   `test_single_application_over_the_cap_lands_exactly_on_the_cap`. This one
   survives a per-application reading; it is listed because it is the other
   half of the pinned pair and should be re-read with it.
8. `tier0/tests/test_kokomi.py:692-698` —
   `test_vigil_upgrade_moves_the_cap_with_the_amount`.
9. `tier0/tests/test_furina_sheet.py:815-886` — the pass-2 errata tests, whose
   prose states "max_stacks is in POWER UNITS (engine caps the total)" as the
   settled reading and records that the applier branch is otherwise unexercised
   by live content.

**Tooling that encodes the current semantics:**

10. `tools/gen_klee_cards.py:422-426` (registry docstring: "stack cap"),
    `:470` (the cap 6 entry), `:1183-1189` (the sheet-vs-registry cross-check).
11. `tools/lint_upgrade_comment_arithmetic.py:108` — `max_stacks` is in
    `CAP_FIELDS`, so upgrade-comment arithmetic is recomputed against it.
12. `tools/lint_handwritten_parity.py:180-184` — `max_stacks` is excluded from
    the card-side parity key set on the grounds that it carries no card-side
    meaning.
13. `tools/lint_sheet_comments.py:10` — `max_stacks` is on the list of things a
    sheet comment must explain.

**C# mirror:**

14. `klee-mod/KleeCode/Powers/KuragePowers.cs:566-596` — as noted, this already
    implements a third rule (set-to-incoming). Any ruling here has to say what
    the mod does, and `SalonPowers.cs:468` /
    `KokomiResources.cs:395` use the same `TryModifyPowerAmountReceived`
    chokepoint, so the pattern is shared even though the numbers are not.

Not implemented, per the ask.

#### (d) A "never lower it" apply mode — the engine's existing idiom

The engine already owns this exact shape, at a different site. When the
Ceremonial Garment refreshes a fielded Bake-Kurage, `effects.py:915-925` takes
`max(standing, new)` rather than assigning — added by the 2026-07-26 audit
(EPOCH 1) precisely because the assignment version pulled an upgraded summon's
duration *down* and deleted the turn the upgrade had paid for. That is the same
defect as this one, in the same file, already ruled once.

The equivalent here is a floor, not a clamp: an application never lowers a
standing stack. There is **no such mode in the apply vocabulary today** —
`_op_apply_power` understands `amount`, `amount_formula`, `target`, `times`,
`max_stacks`, `guard`, `payload`, `member`, `target_all_if_power`, and nothing
else. So this is still engine work, but it is narrower than (c): a new opt-in
field on the row, `max_stacks` untouched, no existing pin re-ruled. Its blast
radius is items 1, 2, 10 and 14 from the (c) list — the apply site, the op, the
codegen field allowlist (`APPLY_POWER_FIELDS`, `gen_klee_cards.py:610`, which
rejects unknown fields loudly by design), and the C# power.

### 7.3 What each option costs, in plain English

**(a) Cap 8.** The player never gets punished for playing a card, ever, in any
order — that is the whole win. What they get instead is a lesser ward that
reaches the big number on its own if they draft enough copies: three of the
plain one, or two upgraded. Engineering side it is one number in the sheet plus
a decision about the codegen registry, which today stores one cap per power and
will refuse two rows that disagree, plus the C# power that hardcodes the same
6. Re-measurement: the card's power level changes at multi-copy densities, so
the drafting arms would want a fresh Kokomi read rather than the single-copy
read a ratification usually implies.

**(b) Cap 6, trap documented.** Zero engineering. Zero re-measurement. The cost
is entirely on the player: someone who owns an upgraded Vigil and plays the
lesser ward after it quietly loses 2 prevention, with nothing on screen saying
so. It is rare — it needs both cards, the upgrade, and that play order — and it
is exactly the kind of thing a playtest report describes as "the card did
nothing" rather than "the card hurt me".

**(c) Per-application cap.** Nothing about this card changes on the surface;
what changes is what the word "cap" means everywhere. It fixes the whole class
at once, including any future ward. It is surgery on a shipped power: one
engine line, one op, one upgrade branch, four tests that state the old meaning
in their names and prose, four tools, and a C# power that currently implements
neither reading. Re-measurement: the only live capped row is the Vigil, so the
sim numbers that could move are Kokomi's, and only where two ward applications
meet — but the pinned tests are *rulings*, so they need [USER] to re-rule, not
a re-run.

**(d) Floor mode.** The player experience is the same as (a) — no card ever
lowers your ward — but the lesser ward keeps its own ceiling of 6, so copies of
it never reach 8. Engineering is a new optional field on the card row, one
branch at the apply site, one entry in the codegen field allowlist, and the C#
power. No existing pin is re-ruled, because `max_stacks` keeps meaning what it
means. Re-measurement: nothing moves that a single-copy read would not already
cover; the card is strictly the drafted card, minus the trap.

No recommendation is made here. The pick is [USER]'s.

### 7.4 The ask-list, restated in full

A GPT review of this packet answered D2–D6 and skipped two items. Both are
still open, and the list below is the complete ask.

- **D1 — the name (STILL OPEN).** "Watch of the Shallows" is **authored
  flavor, not wiki-verified canon**. It was built as the lesser twin of
  "Vigil of the Deep" (shallows/deep, watch/vigil). The machine checks in §4
  only prove it is unique against the internal and reserved namespaces; they
  say nothing about whether it reads right. `S4-G11` — read card names and
  lore text by eye before they ship — applies to this row, and `S4-G11` is
  ruled to have no substitute. So this needs an eye-read, and the eye is
  [USER]'s.
- **D2 — the stack cap. RESOLVED 2026-08-10 by [USER]: option (d), the
  floor-not-clamp apply mode.** Built and landed; §8 is the record. `max_stacks`
  keeps its running-total meaning for every existing row, and the card carries
  the new opt-in field.
- **D3 — magnitude and cost: 3 at 1 energy.** Unchanged (§5).
- **D4 — lane: `archetypes: [generic]`.** Unchanged (§5).
- **D5 — `tempo_band`.** Unchanged (§5).
- **D6 — upgrade `power_amount: +2` (ward 3 -> 5).** Unchanged (§5).
- **D7(a) — does ratifying trigger a Kokomi re-baseline**, or does the card
  land and wait for the next scheduled measurement? Note that the D2 pick
  feeds this: option (a) changes the card's multi-copy power level, and the
  others do not.
- **D7(b) — P3 is still unowned (STILL OPEN).** `missed-requirements.md` §3.2
  names **P3** — "a ticking body for the commander", i.e. no persistent
  recruit above the basic `bake_kurage` — in the same finding that produced
  P4, and **neither P3 option was ever explicitly chosen**. P3 is outside
  `EB-26`'s scope as written. It is open, and it belongs to nobody. Naming an
  owner is the ask; it is not answered by ratifying this card.

---

## 8. Landing record (2026-08-10)

D2 was ruled **(d), the floor-not-clamp apply mode**, and this section is what
was built against that ruling. §1-§7 are unedited: they are the drafting record
the ruling answers, and the two cells §7.1 called wrong are now closed by code
rather than by prose.

### 8.1 The field: `never_reduces: true`

An **opt-in boolean on the `apply_power` effect**, absent everywhere else, and
absent means exactly today's behaviour. The name was chosen over an enum
(`apply_mode: floor`) on the sheet's own conventions: effect-level opt-in flags
here are booleans (`consumes_aura: true`, `applies_element: true`), while the
enum-valued fields (`guard`, `scope`, `member`) exist to pick among several
named values and this mode has exactly one. `never_reduces` also states the
rule in the words the ruling used — an application never reduces a standing
stack — so the row reads as a sentence rather than as a term needing a
glossary.

**`max_stacks` is untouched.** It still bounds the running total for every row
in every sheet; the new flag only says the application may not push a HIGHER
standing stack down to reach that bound. No pinned test was re-ruled.

| site | change |
| --- | --- |
| `tier0/engine/powers.py` | `apply_power(..., never_reduces=False)`; after the clamp, `new = max(new, standing)` |
| `tier0/engine/effects.py` | `_op_apply_power` reads the field and passes it on both the self and the enemy branch |
| `tools/gen_klee_cards.py` | field in `APPLY_POWER_FIELDS`; new `NEVER_REDUCES_POWERS` allowlist; a row is refused by name if the power has no C# floor implementation, or if it asks for the mode with no `max_stacks` to raise toward |

The engine precedent the ruling named is the same shape: `effects.py:915-925`
takes `max(standing, new)` on the Ceremonial Garment refresh, added by the
2026-07-26 audit because assigning pulled an upgraded summon's duration down.

### 8.2 The matrix, re-run against the shipped row

`tier0/tests/test_kokomi.py` (real cards through `combat.play_card` on a
loader-built Kokomi) and `tier0/tests/test_pin_engine_powers.py` (the engine
chokepoint direct). Every cell of §7.1, both orders, both upgrade states:

| order | after 1st | after 2nd | was, before the ruling |
| --- | --- | --- | --- |
| `vigil` -> candidate | 6 | **6** | 6 |
| `vigil` -> candidate+ | 6 | **6** | 6 |
| `vigil+` -> candidate | 8 | **8** | 6 (the DROP) |
| `vigil+` -> candidate+ | 8 | **8** | 6 (the DROP) |
| candidate -> `vigil` | 3 | 6 | 6 |
| candidate+ -> `vigil` | 5 | 6 | 6 |
| candidate -> `vigil+` | 3 | 8 | 8 |
| candidate+ -> `vigil+` | 5 | 8 | 8 |

Copies of one card, four plays: candidate `3, 6, 6, 6`; candidate+
`5, 6, 6, 6`. The floor raises a stack, it does not remove the cap, so the
lesser ward still never reaches the Rare's number on copy count — which is
exactly what separates (d) from (a).

**Regression, and it is the point of "default off":** a row WITHOUT the field
is the old behaviour byte for byte, including the part that looks like the same
defect — plain `vigil` played on top of `vigil+` still clamps 8 down to 6,
because that is what `max_stacks` means and the ruling did not move it. Pinned
in both files.

### 8.3 C# parity — the live defect in `PreventExhaustWardPower`

§7.1 recorded that the mod implemented NEITHER reading (the power became
whatever the last card printed) and showed the Rare's tooltip on any applier.
Both are fixed in `klee-mod/KleeCode/Powers/KuragePowers.cs`.

The obstacle, and the answer. `TryModifyPowerAmountReceived` is handed the
applier CREATURE and no card, so the power could not know which ROW was
applying — and both the mode and the cap are properties of the row, not of the
power. Decompiling `PowerCmd` settles where the row's identity is available:
`Hook.ModifyPowerAmountReceived` takes no `cardSource`, but
`Hook.BeforePowerAmountChanged` does, and it is awaited immediately before the
modify hooks on **both** application paths (`Apply` and `ModifyAmount`). So:

- the generated card declares the mode — `INeverReducingApplier`, carrying the
  row's cap as `NeverReducingCap`
  (`klee-mod/KleeCode/Cards/INeverReducingApplier.cs`, emitted by the generator
  only for rows carrying the field);
- the power captures the applying card in `BeforePowerAmountChanged`, and in
  `BeforeApplied`, which covers the FIRST application — the instance is not in
  the combat yet, so it does not receive the broadcast hook;
- `TryModifyPowerAmountReceived` then computes
  `max(Amount, min(Amount + amount, card cap))` for a floor applier, and the
  running-total clamp otherwise.

The default branch is unchanged in *behaviour*: under the single-application
encoding every non-floor row of this power has cap == amount, so
`min(Amount + amount, amount)` is `amount` — the set-to-incoming line that was
already there. It is now documented as the clamp it implements rather than as a
rule of its own.

**Tooltip.** The power overrides `Title` with the applying card's own
`TitleLocString`, captured on the same two hooks, so the power bar names the
card the player actually played. The class's registered loc entry stays as the
fallback for an application with no card behind it (there is none today).

**How the C# was verified, and what is still owed.** `dotnet build` on
`klee-mod/KleeCode` is green against the real game assembly (0 errors), and the
hook contract above is decompile-verified against `sts2.dll` — the ordering and
the missing `cardSource` are read off the decompiled `PowerCmd.Apply` /
`PowerCmd.ModifyAmount`, not assumed. The Harmony bite-check covers patch
ARMING, not power behaviour, so it has nothing to say about this change.
**A live in-game check of the two fixed behaviours — ward composition and the
tooltip title — is OWED**, and can only run on the art-bearing main checkout
with the game installed.

### 8.4 What landed, and what the gates said

- `docs/kokomi-cards.yaml` — the row, in the uncommon Generic block (now 3),
  with `never_reduces: true`. Pool 61 -> **62** (5 / 27 / **20** / 10).
- `docs/kokomi-upgrades.yaml` — `power_amount: +2` (ward 3 -> 5). The cap does
  not ride along, so the ceiling stays where the Rare put it.
- Generated: `WatchOfTheShallows.cs`, the `KokomiCardRoster` entry,
  `manifest.json`; `gen_roster_cards.py --check` clean.
- Full suite `tier0/tests tier05/tests` green; the softlock lints (handwritten
  / constant / op parity, pool membership, ancient coverage, role-tempo
  `--check` and `--gate`, roster registry, vendor pin, art coverage) green.
- One lint fix rode along as hygiene: `lint_sheet_comments` read the docket id
  `EB-26` in a sheet comment as a cited card number. Docket ids now skip with
  the other ruling refs.
- **D5 could not land as drafted.** `tempo_band` is a MACHINE-LANDED tag (R91)
  and the drift gate requires it to equal the classifier's output, which reads
  this row `fight: [late] / run: [late]`, as it reads every other Kokomi power.
  The sheet carries the classifier's bands and says so beside the row. The
  drafted `run: early` claim needs the classifier RULE to move, which is a
  design call and is not smuggled in under a card landing.
- **Art is an open debt:** `art_coverage` now carries
  `uncommon 1 watch_of_the_shallows` on its bill. No `art/plan.tsv` row, no
  claimed source; Kokomi's art scarcity is the standing constraint.

### 8.5 Re-measurement — D7(a), and why nothing was run

**No rebaseline was run, deliberately.** EXPERIMENTS D4 is one variable per
measurement window, and `EB-22`'s Kokomi pool fill has not landed yet. Two
card-pool changes inside one window make neither readable, so **EB-26's
rebaseline queues behind EB-22's**: EB-22 lands and takes its window, and the
Kokomi read that follows carries both rows. Under option (d) that is a cheap
deferral — the card's power level is the single-copy card minus the trap, so
nothing about it wants a window of its own.

### 8.6 Still owed

1. **D1, the name.** `Watch of the Shallows` is authored flavor, not
   wiki-verified canon. It is unique against the internal and reserved
   namespaces; S4-G11 says a name is read by eye before it ships and has no
   substitute. The eye is [USER]'s, and the sheet row carries the flag.
2. **D7(b), P3.** Still unowned. Naming an owner is the ask, and landing this
   card did not answer it.
3. **The rebaseline**, behind EB-22 (§8.5).
4. **The live in-game check** of the C# ward composition and tooltip (§8.3),
   and the art bill (§8.4).

# EB-77 — Furina summon damage: the derivation, for countersign

> **DRAFT. Nothing here is ratified and nothing here moved a number.** This
> packet exists because `EB-53` has cited "the R89 countersign" as the gate on
> the Furina leg of the N1 attribution pass since the playtest-4 triage, and
> there was no draft in HEAD to countersign. This is that draft.
>
> **It is arithmetic, not a measurement.** Every number below is computed from
> constants and card rows that are already in the tree. No simulation was run,
> no `Cell` was opened, and nothing here carries an `RT/D/P/C` stamp — because
> nothing here is a measured quantity. Nothing in this packet is citable as a
> winrate or an axis reading.
>
> **It takes no position.** §7 lists the decision-shaped questions the
> arithmetic surfaces. Each is written as a question with its arithmetic
> attached, and none carries a recommendation. Those are [USER]'s.

---

## 1. What "Furina summon damage" actually names

The playtest-4 triage asked for four things under N1, and the first row of its
table is *"Furina summon damage numbers"*
(`git show pre-simplification-2026-08-06:docs/archive/playtest4-triage-2026-08-04.md`
§N1). Two clarifications are needed before any arithmetic, because the phrase
does not point where a reader would guess.

**Furina owns none of the four end-of-turn sources.** The end-of-turn docket
built for N1 (`klee-mod/KleeCode/Powers/TurnEndAttribution.cs:144-255`) carries
exactly four: the Masque's Bond of Life, Klee's Sparks 'n' Splash, Oz, and
Kokomi's Bake-Kurage. None is Furina's. Her "summons" are the **Salon
members**, and they act at the **start** of her turn, not the end
(`tier0/engine/effects.py:2555` and `:2686-2716`;
`klee-mod/KleeCode/Powers/SalonPowers.cs:413`, `AfterPlayerTurnStart`). They
were never inside the widget the attribution pass shipped, which is why the leg
stayed open after the other two closed.

**So "Furina summon damage numbers" means these six values**, and nothing else:

| member | tick (start of turn, while on stage) | bow (when displaced) |
|---|---|---|
| Mademoiselle Crabaletta | **6** Hydro damage, random enemy | **14** Hydro damage, random enemy |
| Gentilhomme Usher | **3** Block | **9** Block |
| Surintendante Chevalmarin | **2** Hydro damage, random enemy | Hydro to ALL enemies, **3** Encore |

Source of truth: `tier0/constants.py:285-294` (`SALON_MEMBERS`). Mirrored by
value in `klee-mod/KleeCode/Powers/SalonPowers.cs:41-46`, and the mirror is
enforced — all six are named in the constant-parity gate
(`tools/lint_constant_parity.py:178-183`).

**All six are marked PROPOSED, in both engines, and have been since they were
written.** `tier0/constants.py:275-276` says "numbers PROPOSED pending
red-pen"; `SalonPowers.cs:39-40` repeats it. They came in with the Salon v2
rework of 2026-07-23
(`git show pre-simplification-2026-08-06:docs/archive/furina-salon-rework-plan.md`
§1), whose header states the position exactly: *"Direction is RATIFIED; every
NUMBER below is PROPOSED pending red-pen."* The direction was a [USER]
directive — members should be unique, Fanfare-scaled, pay a larger payoff on
displacement, and get an upward numbers adjustment. The six numbers were the
drafter's answer to that directive and no one has ever signed them.

---

## 2. The resolution arithmetic, exactly as both engines compute it

A member number is not the printed number. Three terms sit on top of it, and
they apply in this order.

**Step 1 — the printed base.** From the table in §1.

**Step 2 — the Focus term and Grand Salon, added.**

```
scaled = base + (readable Fanfare // 10) + salon_damage_up
```

`tier0/engine/effects.py:816-830` (`_salon_amount`), and
`klee-mod/KleeCode/Powers/SalonPowers.cs:171-174` (`Scaled`). `10` is
`SALON_FOCUS_PER` (`tier0/constants.py:295`) / `SalonConstants.FocusPerFanfare`
(`SalonPowers.cs:31`). `salon_damage_up` is Grand Salon's stack count
(`docs/furina-cards.yaml:446`, +1 per copy) and is **0 in every table below** —
these are the unaugmented numbers.

**Step 3 — the dry reduction, if the member could not pay.** Each member pays
`SALON_TICK_ENCORE_COST` = 1 Encore for its tick
(`tier0/constants.py:300`). A member that cannot pay still acts, at
three-quarters, truncated:

```
tick = paid ? scaled : int(scaled * 0.75)
```

`tier0/engine/effects.py:2699-2701`; `SalonPowers.cs:193-197` (`TickValue`).
`0.75` is `SALON_DRY_DAMAGE_MULT` (`tier0/constants.py:301`) /
`SalonConstants.DryDamageMultiplier` (`SalonPowers.cs:37`). A dry tick never
overdraws HP — the upkeep calls `spend_encore`, not `spend_encore_or_hp`
(`tier0/engine/effects.py:2696`).

**Bows skip step 3 entirely.** A bow costs no Encore and is never dry
(`tier0/engine/effects.py:832-857`, `_salon_bow`; `SalonPowers.cs:200-247`,
`Bow`). Chevalmarin's 3 Encore and both aura effects do **not** take the Focus
term — the term is numbers-only by the rework's §2.2a discipline, and the code
matches (`effects.py:846-852` applies `aura_all` and `encore` without passing
through `_salon_amount`).

**Both engines read Fanfare AFTER the turn's decay.** In the sim, decay runs at
the top of the player turn (`tier0/engine/combat.py:533`) and the Salon upkeep
runs later in the same turn (`combat.py:568`, inside
`player_turn_start_triggers`). In C#, decay is in `BeforeSideTurnStart`
(`klee-mod/KleeCode/Powers/FurinaResources.cs:913`) and the upkeep is in
`AfterPlayerTurnStart` (`SalonPowers.cs:413`), which is a strictly later
broadcast. So the Focus term is read off the **post-decay** meter in both. This
matters to §4 and is the reason the steady state there is what it is.

---

## 3. What the six numbers are worth, at each Fanfare level

Furina's Fanfare cap is `FANFARE_CAP_FRACTION` × maxHP = 0.5 × 60 = **30**
(`tier0/constants.py:166`; `tier0/content/characters/furina.yaml:9`), so the
Focus term runs +0 to +3 unless a cap-raiser is in play. `Casting Call` and
`Grand Salon` each add +5 to the cap (`docs/furina-cards.yaml` — the
`raise_fanfare_cap` riders), which is where the rework plan's "uncapped 45 →
+4" came from.

Grand Salon at 0 stacks. All values computed by evaluating the code in §2.

| Fanfare | Focus | Crab tick | Usher tick | Chev tick | Crab bow | Usher bow |
|---|---|---|---|---|---|---|
| 0 | +0 | 6 | 3 | 2 | 14 | 9 |
| 10 | +1 | 7 | 4 | 3 | 15 | 10 |
| 20 | +2 | 8 | 5 | 4 | 16 | 11 |
| 30 (cap) | +3 | 9 | 6 | 5 | 17 | 12 |
| 45 (raised cap) | +4 | 10 | 7 | 6 | 18 | 13 |

The same ticks, **dry** (no Encore to pay with):

| Fanfare | Crab | Usher | Chev |
|---|---|---|---|
| 0 | 4 | 2 | 1 |
| 10 | 5 | 3 | 2 |
| 20 | 6 | 3 | 3 |
| 30 | 6 | 4 | 3 |

**A flat term does not scale flatly.** Because the Focus term is +1 to every
number regardless of that number's size, it is worth a different fraction to
each member. From 0 Fanfare to the 30 cap:

| number | 0 → cap | as a fraction |
|---|---|---|
| Chevalmarin tick | 2 → 5 | **+150%** |
| Usher tick | 3 → 6 | **+100%** |
| Crabaletta tick | 6 → 9 | **+50%** |
| Usher bow | 9 → 12 | **+33%** |
| Crabaletta bow | 14 → 17 | **+21%** |

So a full meter compresses the stage: the Crabaletta-to-Usher tick ratio falls
from 2.00 at empty to 1.50 at cap, and the tick-to-bow ratio moves against the
bows. This is a property of the +1-per-10 shape, not of any of the six numbers,
and it is worth stating because the rework's stated intent was that bows are
the larger payoff.

**Truncation makes the dry penalty uneven.** The dry cut is nominally 25%, but
after truncation it is 33% for a 6, 33% for a 3, and **50% for a 2**. The
smallest member is hit hardest by the dry rule, in both engines, at Fanfare 0.
The effect fades as Focus raises the operand.

---

## 4. The stage feeds its own Focus term, and it converges at +1

This is the derivation with the largest consequence, and it falls straight out
of two constants that were never set against each other.

Each paid tick spends 1 Encore. Every point of Encore spent prints exactly 1
Fanfare (`FANFARE_PER_ENCORE_SPENT` = 1, `tier0/constants.py:181`; applied in
`tier0/engine/resources.py:320`). So a full three-member stage generates **3
Fanfare per turn from its own upkeep**, before any card is played.

Fanfare decays 20% of the whole meter each turn, minimum 1, from turn 2
(`FANFARE_DECAY_FRACTION` = 0.20, `tier0/constants.py:208`; the rounding is
`max(1, round(fanfare * 0.20))`, `tier0/engine/resources.py:114`).

Iterating decay-then-income from an empty meter, with the stage as the only
Fanfare source:

| turn | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10+ |
|---|---|---|---|---|---|---|---|---|---|
| Fanfare after upkeep | 3 | 5 | 7 | 9 | 10 | 11 | 12 | 13 | **13** |
| Focus term | +0 | +0 | +0 | +0 | +1 | +1 | +1 | +1 | **+1** |

**The stage's self-feed converges at Fanfare 13 — Focus +1 — on turn 6, and
never reaches +2.** The general rule is simple: a steady meter of `10k` needs
income of `2k` per turn to hold, so holding +1 costs 2 Fanfare per turn,
holding +2 costs 4, and holding the +3 at cap costs **6 Fanfare per turn,
every turn**. The stage supplies 3. The other 3 must come from the other live
legs — HP lost, Encore absorbed, Spotlighted cards played
(`tier0/constants.py:180-199`).

So the cap-row of the §3 table (Crabaletta at 9, Chevalmarin at 5) describes a
board state the Salon plan cannot reach on its own upkeep, and the +1 row is
what a stage that does nothing else settles at from turn 6.

---

## 5. Pricing the six numbers against the sheet's own anchors

There is no damage-per-energy law in `LAW.md` to derive against, so the anchor
has to come from the sheet. Furina's basics give a clean one, and it has to be
stated as an assumption rather than smuggled in:

> **Anchor A (stated, not proven).** One energy of a Furina *basic* card buys
> 6 damage or 6 Block: `soloists_solicitation` is cost 1 / 6 damage
> (`docs/furina-cards.yaml:53`) and `stage_presence` is cost 1 / 6 Block
> (`docs/furina-cards.yaml:63`). Damage and Block are therefore treated as
> 1:1 "units" below. **This anchor cannot price auras or applications at all**,
> so Chevalmarin's identity — she is the applier — is systematically
> undercounted everywhere in this section. Every Chevalmarin comparison below
> is a floor, not a value.

> **Anchor B (stated, not proven).** One energy of a basic card buys 5 Encore:
> `aria_of_recompense` is cost 1 / 5 Encore (`docs/furina-cards.yaml:69`). So
> 1 Encore ≈ 0.2 energy ≈ **1.2 units** at Anchor A.

### 5a. What a tick converts

At Fanfare 0, one paid tick spends 1 Encore (1.2 units by Anchor B) and returns:

| member | returns | net units | return on the Encore |
|---|---|---|---|
| Crabaletta | 6 damage | +4.8 | **5.0×** |
| Usher | 3 Block | +1.8 | **2.5×** |
| Chevalmarin | 2 damage + Hydro | +0.8 + aura | ≥1.7× |

At the self-feeding steady state (Focus +1, §4) those become 7 / 4 / 3, i.e.
5.8× / 3.3× / ≥2.5×. At the cap they are 9 / 6 / 5.

A full stage at Fanfare 0 therefore turns **3 Encore per turn (3.6 units) into
8 damage + 3 Block (11 units)**, a 3.1× conversion; at the steady state it is
10 damage + 4 Block (14 units), 3.9×; at cap 14 + 6 (20 units), 5.6×.

### 5b. The three cost-1 common deploy cards, side by side

All three deploy one member, all three are cost 1 common, and two carry a rider
that the third does not:

| card | line | deploys | rider |
|---|---|---|---|
| `mademoiselle_crabaletta` | `docs/furina-cards.yaml:138` | Crabaletta | **none** |
| `gentilhomme_usher` | `docs/furina-cards.yaml:131` | Usher | 4 Block |
| `surintendante_chevalmarin` | `docs/furina-cards.yaml:134` | Chevalmarin | 3 Encore |

Let `T` be the number of turns a member stays on stage before being displaced.
At Fanfare 0, in Anchor-A units, ignoring the Encore upkeep (identical for all
three) and ignoring auras (unpriceable):

```
crabaletta card  =  6T + 14
usher card       =  3T +  9 + 4   =  3T + 13
chevalmarin card =  2T +  0 + 3.6 + auras   (3 Encore at Anchor B)
```

`crabaletta − usher = 3T + 1`. **This is positive at every residency,
including T = 0.** The rider that was presumably meant to compensate the weaker
member pays 4 units once; the tick gap it is compensating for is 3 units *per
turn*, and there is a further 5-unit gap in the bows (14 vs 9). The two cards
break even at no value of T.

This is **not** a strict-domination finding under R26/R77 — the effects are
different in kind (damage vs Block vs application), and the law scopes
domination to strictly-better supersets. It is an arithmetic gap under a stated
anchor, and it is exactly the kind of thing a countersign should either accept
(Block is worth more than damage per point, in which case the anchor is wrong)
or move.

### 5c. Against the world these numbers replaced

Salon v1 was a uniform anonymous **4 damage** tick with overflow members
self-bowing at ×3 = 12 damage (`tier0/constants.py:283-284`, the archive note).
The [USER] directive that opened the rework asked, as its point (d), for "an
upward numbers adjustment"
(`furina-salon-rework-plan.md`, USER DIRECTIVE paragraph).

Comparing a full three-member stage, in Anchor-A units:

| world | per-turn output | units |
|---|---|---|
| v1 | 12 damage | **12** |
| v2 at Fanfare 0 | 8 damage + 3 Block | **11** |
| v2 at the self-feed steady state (+1) | 10 damage + 4 Block | **14** |
| v2 at the 30 cap (+3) | 14 damage + 6 Block | **20** |

And per *randomly deployed* member — `salon_debut`, the basic, deploys
`member: random` (`docs/furina-cards.yaml:80`), so the uniform-thirds average is
the honest comparison for an opening hand:

| world | expected tick | expected bow |
|---|---|---|
| v1 | 4.00 | 12.00 |
| v2 at Fanfare 0 | **3.67** | **7.67** (Chevalmarin's bow scores 0 units) |
| v2 at Focus +1 | 4.67 | 8.67 |

**So the directive's "upward" holds from turn 6 onward and does not hold on
turns 1–5**, and the average bow is below v1's at every Fanfare level up to the
cap. The unpriced half is real — v2's bows include an all-enemy Hydro
application and 3 Encore that v1 had no analogue for — but it is unpriced, and
the countersign is where it gets priced.

### 5d. The burst side, for completeness

Each paid tick pays `SALON_TICK_BURST` = 2 (`tier0/constants.py:303`) plus
`BURST_PER_ENCORE_SPENT` = 1 for the Encore it spent (`tier0/constants.py:305`;
pinned at `tier0/tests/test_furina_sheet.py:430-432`) — **3 burst per paid
tick**, 9 per turn for a full stage. A dry tick pays 2 only, since it spends
nothing. Against `burst_max: 70`
(`tier0/content/characters/furina.yaml:14`), a full paid stage fills the Burst
meter from empty in **7.8 turns** on upkeep alone; a full dry stage takes 11.7.
Bows pay 2 as well (`tier0/engine/effects.py:855`).

---

## 6. What the derivation does NOT establish

Stated plainly, because a countersign should know the shape of what it is
signing.

- **No measurement was run.** Nothing here is a winrate, an axis reading, or a
  survival number. Whether these numbers land Furina's Salon arm on or off its
  anchor is a question for the instrument, not for this packet, and the salon
  arm's standing STOP (R87 item 1, and the C2 escrow) is untouched by anything
  here.
- **Auras and applications are unpriced.** Anchor A has no term for them.
  Chevalmarin is the member most affected and every number attached to her in
  §5 is a floor.
- **Residency `T` is not derived.** It depends on draft contents and play
  patterns. §5b avoids it by holding at every `T`, but §5a's per-card totals do
  not.
- **Enemy-side terms are absent.** The ticks pick random targets and resolve
  through the element pipeline, so Vulnerable, Weak and enemy Block all move
  the real number. The same caveat the docket's hover copy already makes
  (`TurnEndAttribution.cs:54-60`).

---

## 7. What is being asked of [USER]

Five questions. Each carries its arithmetic and none carries a recommendation.

**Q1 — Sign the six numbers as they stand, or move them.** The six values in
§1 have been live and PROPOSED in both engines since 2026-07-23. A countersign
here converts them from proposed to ratified and discharges the PROPOSED
banners at `tier0/constants.py:275-276` and `SalonPowers.cs:39-40`. Nothing in
this packet moves them.

**Q2 — Is the Crabaletta/Usher gap in §5b intended?** Under Anchor A the
Crabaletta deploy beats the Usher deploy by `3T + 1` units at identical cost and
rarity, at every residency. Either the anchor is wrong (a point of Block is
worth more than a point of damage on this character, in which case say by how
much and the arithmetic re-runs), or the gap is intended texture, or a number
moves. All three are decisions.

**Q3 — Is the Focus term supposed to reach +2?** §4 shows the stage's own
upkeep converging at Fanfare 13 / Focus +1, and holding +3 costing 6 Fanfare per
turn forever. The §3 cap row describes a state the Salon plan does not reach on
its own. Accepting that means the printed "+1 per 10 Fanfare" is, for a pure
Salon deck, "+1, from turn 6".

**Q4 — Does the directive's "upward numbers adjustment" read as satisfied?**
§5c: the full stage is 11 units at Fanfare 0 against v1's 12, crosses at the
+1 steady state, and the average bow is below v1's at every level up to the cap.
The uncounted half is the application and Encore that v1 did not have. Whether
that trade is the upward adjustment asked for is a taste call.

**Q5 — Is the 50% dry cut on Chevalmarin acceptable?** §3: truncation makes the
nominal 25% dry reduction land as 33% / 33% / 50% at Fanfare 0. This is
identical in both engines, so it is a shape question and not a parity defect.

---

## 8. Findings for the register (not decisions)

These are engineering observations surfaced by the derivation. They are
reported, not fixed, and none of them changed a number.

**F1 — the `EB-53` gate citation is stale in two ways.** `EB-53` and the
playtest-4 triage both name "the R89 countersign" as the gate on this leg. R89
is *Furina legibility: the preview-truth fix* and it was **countersigned on
2026-08-06** as an audit-trail reconstruction (commit `894502e`;
`git show 894502e:tier0/DECISIONS.md`, the R89 banner). It contains no member
numbers of any kind — its subject is the split value path between
`PreviewValue` and `PrintedDamage`. So the named gate is (a) already
discharged and (b) never carried the numbers. The real unsigned gate is the
Salon v2 rework plan's "every NUMBER below is PROPOSED pending red-pen", which
this packet is the draft for. `EB-77`'s premise — "no draft exists in HEAD" —
is correct; its citation route is not.

**F2 — `SalonMemberPower.Localization` hardcodes all six numbers as string
literals.** `klee-mod/KleeCode/Powers/SalonPowers.cs:70-93` writes "deals 6
Hydro damage", "gains 3 Block", "deals 2 Hydro damage", "deals 14", "gains 9
Block", "grants 3 Encore" — and the same six again in the `smartDescription`
directly below. The values are correct today. But
`klee-mod/KleeCode/Cards/SalonMemberTips.cs:99-114` deliberately interpolates
`SalonConstants.*` for exactly this text, with the comment *"Numbers come from
SalonConstants, so a repricing cannot leave the tooltip telling the player a
retired number."* The power's own description does not follow its own rule. If
Q1 moves any of the six, these two strings are the drift site, and the
constant-parity gate cannot see them — it compares constants, not prose.
**Consequence for the countersign: a repricing is a two-file edit, not a
one-file edit.**

**F3 — `"aura": True` on Chevalmarin's tick is inert.**
`tier0/constants.py:292` carries an `aura` key on her tick spec. No engine code
reads it: the tick loop reads only `damage` and `block`
(`tier0/engine/effects.py:2702-2713`), and grep finds no `"aura"` read anywhere
under `tier0/engine/`. **There is no behaviour gap** — her tick deals Hydro
damage, and a Hydro hit applies Hydro through the element pipeline, so the
intent lands anyway. The key is documentation that looks like a switch. Worth
noting because Crabaletta's tick is also Hydro damage and so applies exactly
the same aura, which means the two members' *application* profiles are
identical and only the numbers differ — Chevalmarin's applier identity lives
entirely in her **bow**, not her tick.

**F4 — a stale line citation in the C# decay comment.**
`klee-mod/KleeCode/Powers/FurinaResources.cs:915-918` cites "combat.\_player\_turn
calls decay_fanfare at line 424 and clears Block at line 430, six lines later".
In HEAD those are `tier0/engine/combat.py:533` and `:539`. The *claim* is still
exactly true (still six lines, still the same order), only the absolute numbers
drifted. Cosmetic.

---

## 9. Provenance

- Ask: `git show pre-simplification-2026-08-06:docs/archive/playtest4-triage-2026-08-04.md` §N1, row 1.
- Register row: `docs/current/BACKLOG.md` `EB-77`; parent `EB-53`.
- Numbers under derivation: `tier0/constants.py:285-305`,
  `klee-mod/KleeCode/Powers/SalonPowers.cs:26-46`.
- Resolution paths: `tier0/engine/effects.py:816-857` and `:2555`, `:2686-2716`;
  `klee-mod/KleeCode/Powers/SalonPowers.cs:171-247` and `:413-453`.
- Parity gate over all six: `tools/lint_constant_parity.py:178-183`.
- Direction that authored them:
  `git show pre-simplification-2026-08-06:docs/archive/furina-salon-rework-plan.md` §1.
- The gate `EB-53` names: `git show 894502e:tier0/DECISIONS.md`, entry R89.
- Anchors: `docs/furina-cards.yaml:53`, `:63`, `:69`, `:131`, `:134`, `:138`,
  `:80`, `:446`; `tier0/content/characters/furina.yaml:9`, `:14`.

**Owed live checks: none.** Nothing in this packet needs the game launched —
every value is computed from source, and the C#/sim agreement it relies on is
already asserted by the parity gate on every suite run.

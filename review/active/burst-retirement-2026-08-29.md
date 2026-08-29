# Retiring the shared Burst meter — a roster-wide concept packet

**Date:** 2026-08-29 · **Branch:** `burst-retirement` · **Docs only.**
**Status:** DRAFT for [USER]'s countersign. Nothing here is built, nothing is
merged, and no register row is edited by this branch — §7 lists the register
changes this packet *owes* so they land in one slate under one ruling (R206 as
amended by R212).

Everything in §3 and §4 is **prospective**. The R213 freeze is untouched: no
lever moves, no window opens, and no character's kit changes on this branch.

---

## §1 — [USER]'s words

### 1.1 [USER], 2026-08-29 (a)

> "I think the Burst Meter thing might be overdone, honestly. It was a day 1
> idea that frankly feels like it adds complexity without payoff. So folding it
> into Furina's already-existing Fanfare concept feels fine. Klee's Burst feels
> basically redundant, and I want to make Kokomi's more useful as part of the
> current rework as well."

### 1.2 Claude's recommendation, 2026-08-29 — the thing (b) agrees to

Attributed to Claude, reproduced here so the "agreed" below has a referent:

> Retire the shared Burst meter as a concept. Each character's signature
> resource becomes the gauge — Klee's Sparks, Furina's Fanfare, Kokomi's Charge
> — and each "Burst" becomes a drain or overdrive of that resource rather than
> a second bar filled by a second economy.
>
> - **Furina:** Let the People Rejoice drains Fanfare, and it becomes rare loot
>   rather than kit.
> - **Klee:** Sparks 'n' Splash keeps its name and becomes a Spark drain —
>   "spend all Sparks: shoot that many 5-damage sparks."
> - **Kokomi:** Ceremonial Garment becomes a Charge-drain state, folded into
>   the Kurage rework.
>
> And a timing pick for Kokomi: (1) run the sealed Kurage run as staged, then
> fold Burst in the NEXT Kokomi slice; or (2) fold first, re-seal, then run.

### 1.3 [USER], 2026-08-29 (b)

> "Yeah, agreed on the Burst changes. And let's go with 1) The Regent-equivalent
> is an Uncommon card, by the way; we could either let Klee's go to Uncommon or
> make it stronger as a Rare payoff."

**What that settles.** The concept is agreed. Kokomi's timing is **pick 1** —
the sealed Kurage run goes as staged, and the Burst fold is the *next* Kokomi
slice's work. Klee's rarity is left open as a two-way pick, which §4.2 answers
with a recommendation and a pick list.

---

## §2 — What is actually there, with citations

Everything in this section was read on `origin/main` at the head of this branch.
Line numbers are that read.

### 2.1 The three Burst cards

| character | id | file:line | shape |
|---|---|---|---|
| Furina | `let_the_people_rejoice` | `docs/furina-cards.yaml:837` | cost 0 attack, rare, `kit_card: true`, `tags: [burst]`, `requires: burst_energy_full` |
| Klee | `sparks_n_splash` | `docs/klee-cards.yaml:374` | cost 0 power, rare, `kit_card: true`, `tags: [burst]`, `requires: burst_energy_full` |
| Kokomi | `ceremonial_garment` | `docs/kokomi-cards.yaml:669` | cost 0 skill, rare, `kit_card: true`, `tags: [burst]`, `requires: burst_energy_full` |

**Furina** (`docs/furina-cards.yaml:837–839`): `{op: damage, amount: 8, target:
all_enemies, bonus_formula: 1_per_4_fanfare}` then `{op: gain_encore, amount:
6}`. The row calls it "mass hydro (burst-tag cadence) scaling with the crowd's
roar" and records the cost-0 ruling: *"the charged meter IS the cost — it empties
on cast."* It already reads Fanfare; what it does not do is *pay* Fanfare.

**Klee** (`docs/klee-cards.yaml:374–376`): `{op: apply_power, power:
sparks_n_splash, amount: 3, ...}` — three turns of "end of turn, 4 sparks × 5
damage to random enemies, each applies Pyro," marked *"v0.5: NOT in draftable
pool; granted to hand when Burst meter first fills (innate-on-charge)."* C# arm:
`Powers/KitBurst.cs:57` (`SparksNSplashPower`), `VolleyHits` / `VolleyHitDamage`
at `:86, 100`.

**Kokomi** (`docs/kokomi-cards.yaml:669–671`): `{op: apply_power, power:
ceremonial_garment, amount: 3, target: self}` — pure state entry for
`CEREMONIAL_GARMENT_TURNS` = 3, during which her attacks read Charge at +1
damage per `GARMENT_CHARGE_DIVISOR` = 2 Charge per play. **R74 removed its entry
splash** (`docs/kokomi-cards.yaml:673–678`): *"THE ENTRY SPLASH IS GONE. Pure
state-entry now… the splash was a second, unrelated payment stapled to the front
of it, and it let the Burst read as a damage button rather than as a state."*
That ruling is the closest precedent in the repo to what §3 proposes — R74
already decided this card is a *window on a resource*, not a nuke. Making the
window cost Charge is the natural completion of R74, not a reversal of it.

### 2.2 The three meters

| character | file:line | `burst_max` |
|---|---|---|
| Furina | `tier0/content/characters/furina.yaml:25` | **70** — the row cites R17 (2026-07-20) |
| Klee | `tier0/content/characters/klee.yaml:11` | **40** |
| Kokomi | `tier0/content/characters/kokomi.yaml:35` | **20** — "v0.4 O4 salvage (PROPOSED, plan §1.2): 10 → 20" |

C# mirrors: `BurstConstants.KleeMax` (`Powers/BurstResource.cs`, referenced at
`Vfx/GaugeBridge.cs:150`), `FurinaResourceConstants.BurstMax = 70`
(`Powers/FurinaResources.cs:117`), `KokomiConstants.BurstMax = 20`
(`Powers/KokomiResources.cs:118`).

### 2.3 The feeds — where Burst energy comes from

All in `tier0/constants.py`:

| constant | line | value | scope |
|---|---|---|---|
| `BURST_PER_SKILL_TAG` | 129 | 5 | **roster-wide** — every skill-tagged card, any character with a meter |
| `BURST_PER_REACTION` | 130 | 5 | **roster-wide** — every reaction |
| `DETONATION_SPLASH_BURST` | 136 | 3 | Klee — Blazing Delight (`docs/klee-cards.yaml:377`) |
| `WITCHS_FLAME_BURST` | 144 | 3 | Klee — Durin, per consumed Pyro aura |
| `CATALYTIC_BURST_PER_REACTION` | 148 | 5 | Klee — Catalytic Converter (`docs/klee-cards.yaml:333`) bonus |
| `SALON_TICK_BURST` | 379 | 2 | Furina — per member tick and bow |
| `BURST_PER_ENCORE_SPENT` | 381 | 1 | Furina — per point of Encore spent |
| `KOKOMI_BURST_PER_EXHAUST` | 405 | 2 | Kokomi — per Exhaust event |

Engine sites: `tier0/engine/reactions.py:208` (reaction), `:215` (catalytic
bonus); `tier0/engine/effects.py:901` (detonation splash), `:4736` (Durin's
flame); the skill-tag grant is inline in `tier0/engine/combat.py` beside the
Burst-cast drain. Every gain funnels through `resources.gain_burst`
(`tier0/engine/resources.py:503`), which records a source string — that funnel
is what makes a retirement auditable rather than a grep.

**The "one wage in two currencies."** `CHARGE_PER_EXHAUST` = 1
(`tier0/constants.py:403`) and `KOKOMI_BURST_PER_EXHAUST` = 2 (`:405`) are paid
by the *same* event. The Kurage packet says so explicitly
(`review/active/kokomi-kurage-memory-2026-08-29.md:645–649`):

> "**Only the Charge funnel narrows; the Burst wage does not.** `CHARGE_PER_
> EXHAUST` and `KOKOMI_BURST_PER_EXHAUST` are documented as one wage in two
> currencies, and §4 removes the Muster *Charge* subsidy without mentioning
> Burst. A Mustered Companion's Exhaust therefore still pays her burst
> particles and pays no Charge."

That asymmetry is a live inconsistency today and it disappears entirely under
§3 — which is one of the stronger arguments for the retirement.

### 2.4 Shared machinery

- `tier0/engine/combat.py:116` — `grant_charged_kit`: at a full meter the kit
  card is granted to hand; a full hand *defers* the grant so the meter is never
  lost.
- `tier0/engine/combat.py:213` — playability gate: `if card.requires ==
  "burst_energy_full": if state.player.burst_energy < state.player.burst_max:
  return False`.
- `tier0/engine/combat.py:471` — the drain: `p.burst_energy = 0  # playing the
  Burst empties it`, then `state.emit("burst_cast", …)`; the skill-tag grant
  sits immediately below it.
- `tier0/engine/effects.py:1677` — `_op_burst_energy`, the card-text source op,
  gated on `if state.player.burst_max`.
- `tier0/engine/resources.py:503` — `gain_burst(state, n, source)`, the single
  funnel with source attribution.

**The pilot prices Burst points.** `tier0/constants.py:953`:
`PILOT_BURST_DIVISOR = 10.0  # burst_energy is priced per burst point`. This is
the load-bearing engineering consequence of the whole packet: *the pilot's
valuation function reads the meter*. Retiring the meter changes what the pilot
values, which is a `POLICY_VERSION` bump and a re-baseline — see §5.

### 2.5 C# — the three pools and the indicator

| site | what is there |
|---|---|
| `Powers/BurstResource.cs:19–25` | `BurstConstants.PerSkillTag = 5`, `PerReaction = 5` — mirrored from `tier0/constants.py`, "never re-derived" |
| `Powers/KitBurst.cs:108–135` | `KitGrant`, the port of `grant_charged_kit`, with its four invariants (grant only at full; never a duplicate; a full hand defers; the copy is fresh) |
| `KleeCardPool.cs:38, 68, 101` + `KleeOffPoolCards.cs:12, 76` | the kit Burst card held out of the draftable pool |
| `KokomiCardPool.cs:22, 86–110` | the same for `ceremonial_garment` — *"granted-not-drafted is the v1.9 kit invariant"* |
| `KleeMod.cs:148` | printed rider: *"Playing this card grants {BurstConstants.PerSkillTag} Burst Energy."* |
| `KleeMod.cs:271–278` | the cross-character **Burst KEYWORD** loc entry, `"Burst Energy"` |
| `Cards/KleeCardTooltips.cs:104–128` | the `BurstMeter` record and `MeterOf(Creature?)`, three branches |

**The indicator** (`klee-mod/KleeCode/Vfx/GaugeBridge.cs`): `:42–51`
`OverheadBurstAnchor = new(0f, -300f)`, with the C1 ruling in the comment —
*"this anchor is a CONVENTION, not a per-character choice — the overhead slot
means 'Burst' for everybody."* `:55–63` `SecondRowAnchor = new(0f, -340f)`, *"a
resource that is not Burst. Kokomi's Charge is the first tenant."* Then the three
entries: `:137–157` Klee, key `"burst"`, fuse-and-bomb skin; `:158–178` Furina,
`"furina_burst"`, hydro ribbon; `:180–202` Kokomi, `"kokomi_burst"`, pearl. And
`:203+` Kokomi's Charge, *"THE ONE GAUGE WITH NO BAR"*, on the second row.

This is the piece of the retirement that costs the least and is worth flagging
early: **the overhead slot survives unchanged.** The gauge entries keep their
anchor, their skins and their flash predicates; only `ReadValue`, `VisualSpan`
and `LabelMax` re-point from the Burst resource to the signature resource. Under
§3, Kokomi's Charge stops being a second-row tenant and moves up into the slot
it should have had all along.

### 2.6 Rulings this packet touches

| ruling | `docs/current/RULINGS.md` | what it says |
|---|---|---|
| R17 | line 30, 2026-07-20 | the knob ratification pass that fixed Furina's `burst_max` at 70 |
| R47 | line 59, 2026-07-23 | "Klee second-playtest card and Burst pass" |
| R74 | line 86 | "Ceremonial Garment loses its entry splash; pure state-entry." |
| v1.9 | `docs/current/LAW.md:176` | "The Burst (Sparks 'n' Splash) is **kit, not loot**" |

### 2.7 The LAW clauses

Found by `grep -i burst docs/current/LAW.md` — eight hits, seven of them
substantive:

| line | clause |
|---|---|
| 64 | reaction credit — damage attribution **and Burst energy** — goes to the triggering player |
| 72 | application cadence: catalyst-grade vs. **"only Skill/Burst-tagged cards apply"** |
| 145 | **"Burst-meter (`burst_energy`) generation stays character-kit-scoped"** and never cheaply repeatable from companions |
| 176 | v1.9: the Burst is **kit, not loot** — never draftable, granted on fill, casting empties the meter, re-granted on refill, Retain |
| 248 | rotation law: no Charge **(or Burst particle)** accrues from a Status/Curse exhaust |
| 266 | the §3 character template: talent-relic + **kit-Burst** + character relics/potions |
| 481 | every meter carries a bounded/unbounded property; **`burst`** is listed as unbounded |
| 508 | the centered-overhead creature-space slot is the **cross-character Burst indicator**; gauge skins unique per character |

### 2.8 The Regent card [USER] means

`docs/current/research/regent-stars-economy.md:322`, in the §3.5 table of all 23
Star spenders:

> | `Stardust` | Uncommon | 0 | **X** | Attack | 5 damage to a random enemy, X times |

Its localised text, `:476`:

> `"STARDUST.description": "Deal X times {Damage:diff()} damage to a random enemy."`

And the resolution rule, `:335–337`:

> "`Stardust` is the X case (`HasStarCostX => true`), resolved by
> `CardModel.ResolveStarXValue()` — **it spends the whole bank and hits that
> many times**."

So the base game's spend-all-your-resource card is **Uncommon, 0 energy, X
Stars, Attack, 5 damage per Star to a random enemy**. That is a near-exact
structural twin of the seed body in §4.2 — same rarity question, same "5 damage
× bank" payout, same random aim. It is the right anchor and [USER] is right
about its rarity.

Two notes that bear on how much weight the anchor carries:

- The Regent's Star pool is **spender-heavy**: 4 Basic / 20 Common / 38 Uncommon
  / 27 Rare / 2 Ancient, and by rarity the generator-to-spender ratio at Uncommon
  is **1 : 2.5** (`:191–195`). Sparks, under the shipped Klee sheet, are the
  opposite — see §4.2. Stardust is Uncommon in an economy where Stars are *hard
  to keep*.
- `EB-192` (`docs/current/BACKLOG.md:103`) has the `regent_forge` canon package
  under an open [USER] measurement call, and `EB-193` (`:104`) records that
  `game_ref/regent.json` carries no Star amounts at all. Every Star number quoted
  above was re-decompiled by hand into the research doc. **Cite it as a design
  anchor, not as a measured baseline.**

---

## §3 — DRAFT ruling text, for countersign

### 3.1 The architecture paragraph

> The shared Burst meter is retired as a roster concept. Each character's
> signature resource is her gauge — Klee: Sparks; Furina: Fanfare; Kokomi:
> Charge — and the centered-overhead indicator keeps showing it, skinned per
> character; that display rule stands unchanged. Each former Burst becomes a
> drain or an overdrive of that resource, authored inside the character's own
> kit rather than granted by a second economy. The roster-wide feeds — the skill
> tag and the reaction — retire with the meter; the reaction-credit clause
> narrows to damage attribution alone; "kit-Burst" leaves the character
> template. v1.9's "kit, not loot" stops being a roster law and becomes a
> per-character call: Furina's drain and Klee's drain are LOOT by [USER]'s word,
> and Kokomi's is the next slice's call. Everything here is PROSPECTIVE under
> the R213 quarantine, and the shared retirement lands LAST — after all three
> folds are in — so that no character is ever left holding a dead gauge.

### 3.2 The LAW replacements, clause by clause (C2-style block, PROSPECTIVE)

Each block below is the exact replacement sentence(s) for the cited line. None
of them is applied on this branch.

**LAW:64 — reaction credit.** Narrows to damage attribution.

*Current:*

> - **Reaction credit — damage attribution and Burst energy — goes to the
>   triggering player;** auras live on shared enemies so cross-player reactions
>   need no special-casing. (principles §2.5)

*PROSPECTIVE replacement:*

> - **Reaction credit — damage attribution — goes to the triggering player;**
>   auras live on shared enemies so cross-player reactions need no
>   special-casing. Where a character's signature resource pays out on a
>   reaction, that payment follows the same attribution rule and is declared in
>   her own kit, never roster-wide. (principles §2.5; Burst retirement 2026-08-29)

**LAW:72 — application cadence.** The tag name survives the meter's death only
if a card still carries it; it does not.

*Current fragment:*

> …catalyst-grade (every attack applies, low base numbers) vs. skill-grade (only
> Skill/Burst-tagged cards apply, higher base numbers).

*PROSPECTIVE replacement fragment:*

> …catalyst-grade (every attack applies, low base numbers) vs. skill-grade (only
> Skill-tagged cards apply, higher base numbers).

*Note:* the `burst` **card tag** is a separate thing from `burst_energy` and it
is what the three kit rows carry today (`tags: [burst]`). §5 books the decision
of whether the tag is renamed (`signature`?) or dropped; it is a naming call
inside a countersigned block and, if lint proves it cosmetic, R179 lets Claude
settle it.

**LAW:145 — companion-scoped Burst generation.** The clause exists to stop the
colorless pool from cheaply printing a character's meter. That danger does not
retire with the meter; it re-points at the signature resources.

*Current second sentence:*

> **Burst-meter (`burst_energy`) generation stays character-kit-scoped** and must
> never be cheaply repeatable from companions.

*PROSPECTIVE replacement:*

> **A character's signature-resource generation (Sparks, Fanfare, Charge) stays
> character-kit-scoped** and must never be cheaply repeatable from companions.

This is the clause with the widest silent reach: it is the reason the companion
pool is safe today, and re-pointing it is not optional bookkeeping.

**LAW:176 — v1.9 "kit, not loot."** Becomes per-character.

*Current:*

> - **The Burst (Sparks 'n' Splash) is kit, not loot:** never draftable, granted
>   to hand on meter fill, casting empties the whole meter (overflow lost at
>   cast), re-granted on refill, carries Retain. (principles §2.4, v1.9)

*PROSPECTIVE replacement:*

> - **Whether a character's signature payoff is kit or loot is a per-character
>   call, declared on her sheet.** Furina's *Let the People Rejoice* and Klee's
>   *Sparks 'n' Splash* are LOOT — draftable, priced at their rarity, paid for
>   out of the signature resource ([USER] 2026-08-29). Kokomi's *Ceremonial
>   Garment* is unruled and belongs to the next Kokomi slice. Where a payoff
>   remains kit, the v1.9 grant machinery is what it uses: never draftable,
>   granted on threshold, re-granted after a spend, carries Retain.
>   (principles §2.4; Burst retirement 2026-08-29)

**LAW:248 — rotation law.** Drops the parenthetical.

*Current fragment:*

> …and no Charge (or Burst particle) accrues from a Status/Curse exhaust by any
> route.

*PROSPECTIVE replacement fragment:*

> …and no Charge accrues from a Status/Curse exhaust by any route.

This one has a bonus: it makes the rotation law *simpler* and removes the exact
double-currency the Kurage packet flagged at its line 645.

**LAW:266 — the character template.**

*Current fragment:*

> …~75-card pool; talent-relic + kit-Burst + character relics/potions.

*PROSPECTIVE replacement fragment:*

> …~75-card pool; talent-relic + a signature-resource payoff (kit or loot, her
> call) + character relics/potions.

**LAW:481 — the meter property list.**

*Current fragment:*

> (bounded: salon_member 3, spark 3, fanfare; unbounded: encore, charge, burst,
> exhaust_pile)

*PROSPECTIVE replacement fragment:*

> (bounded: salon_member 3, spark 3, fanfare; unbounded: encore, charge,
> exhaust_pile)

*Caveat, and it is a real one:* `spark` is listed as **bounded at 3**. A
spend-all Sparks card only makes sense against an unbounded or a much larger
bank, and the Klee Sparks packet's smoke measured a *net accumulating* bank
(§4.2). Whether Sparks are bounded is already live inside the Klee Sparks work
(M51) and this packet does not settle it — but the retirement **depends** on the
answer, so §4.2's pick is written to be legible either way and §6 flags the
dependency.

**LAW:508 — the indicator.** The display rule stands; only the noun changes.

*Current first sentence:*

> - **The centered-overhead creature-space slot is the cross-character Burst
>   indicator;** gauge skins are unique per character.

*PROSPECTIVE replacement:*

> - **The centered-overhead creature-space slot is the cross-character
>   signature-resource indicator;** gauge skins are unique per character. The
>   anchor is a CONVENTION, not a per-character choice — the overhead slot means
>   "this character's resource" for everybody.

The rest of the clause (mirror above the animated node, never write
`Visuals.Scale`, boot check on the node) is untouched.

### 3.3 Sequencing — why the shared retirement lands LAST

R213 sequences the roster Kokomi → Klee → Furina. The retirement inverts that
for the *shared* half, because the shared half is the only piece that can leave
a character with a dead bar:

1. Kokomi's fold ships (next Kokomi slice) — her Garment reads Charge, but
   `burst_max` 20 still exists.
2. Klee's fold ships (the Sparks arm's next round) — Sparks 'n' Splash becomes a
   Spark drain behind `SPARK_ALT_COST_ENABLED`.
3. Furina's fold ships (the reframe) — Rejoice drains Fanfare.
4. **Then and only then** the shared retirement lands: the meter, the two
   roster-wide feeds, the `requires` gate, the kit-grant machinery, the LAW
   clauses, the pilot term, and the gauge re-point.

Between (1) and (4) each character carries a Burst meter that fills and does
nothing, which is ugly but *safe* — it is a display and a dead constant, not a
broken kit. The reverse order would brick three characters' payoffs at once.

---

## §4 — Per character

### 4.1 Furina — pointer only

Her fold is being drafted in `review/active/furina-reframe-2026-08-29.md` on
branch `furina-reframe`. **This packet decides nothing for her beyond the
concept**: Fanfare is her gauge, *Let the People Rejoice* drains it, and it is
LOOT by [USER]'s word at §1.3. Everything else — the drain amount, whether the
`1_per_4_fanfare` formula survives contact with a card that *spends* Fanfare,
what happens to `SALON_TICK_BURST` and `BURST_PER_ENCORE_SPENT`, and her rarity
— belongs to the reframe packet.

*One fact worth handing across:* `let_the_people_rejoice` already reads Fanfare
(`bonus_formula: 1_per_4_fanfare`) but never pays it, so the reframe is turning
a read into a read-and-spend on a card whose text barely moves. That is the
cheapest of the three folds.

*Unverified:* branch `furina-reframe` is not on `origin` as of this read, and
`review/active/furina-reframe-2026-08-29.md` is not on `main`. The pointer is
recorded as given.

**No pick list. Nothing returns to [USER] from 4.1.**

---

### 4.2 Klee — Sparks 'n' Splash becomes a Spark drain

**The seed body** (numbers are seeds, not derived — no sim has been run on
them):

> **Sparks 'n' Splash** — *Attack.* Spend all Sparks: shoot that many sparks at
> random enemies, each dealing **5** damage and applying **Pyro**.

The name is kept — that was in the recommendation [USER] agreed to, and it is
her canon Burst's name. What changes is that the card stops being a three-turn
Power fed by a hidden meter and becomes a single spend of the resource the
player has been watching all fight.

**The Regent anchor, beside it:**

> **Stardust** — Uncommon, 0 energy, **X Stars**, Attack. *"Deal X times 5
> damage to a random enemy."* Spends the whole bank and hits that many times.
> (`docs/current/research/regent-stars-economy.md:322, 335–337, 476`)

They are the same card. Which is exactly why the rarity question is real.

**What each rarity does to the Sparks arm's in/out ratio.** The Klee Sparks
packet's smoke (`review/active/klee-sparks-2026-08-29.md:863–873`) measured,
over 25 player turns: **33 Sparks gained (1.32/turn), 11 spent (0.44/turn), net
+22**, against a modelled expectation of +1.0 / −1.0. Zero automatic consumes,
zero refused spends. The arm is **income-heavy and sink-starved** — the exact
mirror image of the Regent's 1 : 2.5 generator-to-spender ratio at Uncommon.

The shipped spenders are all `Spend 2` (`:114` — `powder_charge`,
`hold_the_line`, `smoke_and_sparks`) and the proto rows top out at **Firework
Finale, Uncommon, Spend 3, Exhaust, 18 damage** (`:263`).

- **At Uncommon.** The card enters decks at Uncommon frequency against
  1.32 Sparks/turn income and the arm's "insane generation is fine" posture. A
  bank growing +22 over a fight, cashed at 5 damage a Spark, is a repeatable nuke
  *cheaper to reach* than the current three-turn Power — and it fixes the sink
  problem in the wrong direction: one card absorbs the whole surplus, every other
  spender stops competing, and the arm's in/out ratio becomes one card's ratio.
- **At Rare.** It is the archetype's finale: Rare draw frequency, the kit name
  kept, and room left for the `Spend 2`/`Spend 3` band to do the per-turn sink
  work the smoke says is missing. The ratio still needs repair, but by *many
  small sinks* the packet is already building rather than by one card.

**Claude's lean is Rare with a stronger body.** The Regent anchor is Uncommon,
but the anchor's economy is spender-heavy and ours is income-heavy; copying the
rarity across that gap copies the wrong half of the card.

#### PICK K1 — Sparks 'n' Splash rarity

1. **Rare, with a stronger body** — *Claude's recommendation.* Keeps the kit
   name as the archetype's finale; the spend-ALL verb is priced at the rarity
   where a bank-cashing card belongs; the `Spend 2` band keeps its job. The
   "stronger body" is the seed's 5 damage plus one of: a floor (minimum 3
   sparks), an all-enemies split, or a Pyro-aura guarantee — a sub-pick for the
   round that builds it, not for now.
2. **Uncommon, matching Stardust** — the base game's precedent read literally:
   0 energy, spend-all, 5 per point, random aim, Uncommon. Simpler to defend as
   "we ship what the game ships," and if Sparks stay bounded at 3
   (`docs/current/LAW.md:481`) the ceiling is small and the Uncommon price is
   correct. Choose this if the bounded-Sparks reading is the one that holds.

#### The five Klee-side feeds — re-author to Sparks, or retire, per card

| feed | file:line | value | recommendation |
|---|---|---|---|
| `BURST_PER_SKILL_TAG` | `constants.py:129` | 5 | **RETIRE.** Roster-wide by construction; a skill tag paying Sparks would give Klee a second, invisible generator on top of a bank already running +1.32/turn. The printed rider at `KleeMod.cs:148` retires with it. |
| `BURST_PER_REACTION` | `constants.py:130` | 5 | **RETIRE as a roster feed.** If Klee is to be paid for reactions, that payment is authored on her sheet as a Spark rider on named cards, not as an engine-wide rule — which is precisely what LAW:64's narrowing says. |
| `CATALYTIC_BURST_PER_REACTION` | `constants.py:148` | 5 | **RE-AUTHOR to Sparks**, at a derived rate, not at 5. Catalytic Converter (`docs/klee-cards.yaml:333`) is an Uncommon Power whose whole job is "reactions pay you"; it survives the retirement intact with Sparks as the currency. This is the one feed where the *card* is the point. |
| `DETONATION_SPLASH_BURST` | `constants.py:136` | 3 | **RE-AUTHOR to Sparks.** Blazing Delight (`docs/klee-cards.yaml:377`) already carries a per-turn proc cap of 3, so it is rate-limited at source — the safest of the three card feeds to convert. Rate derived, not carried over. |
| `WITCHS_FLAME_BURST` | `constants.py:144` | 3 | **RETIRE.** Durin is a companion, and LAW:145 (as replaced in §3.2) says signature-resource generation stays kit-scoped and never cheaply repeatable from companions. Converting this feed would write the new law's violation into the new law's first day. |

That is: two roster feeds retire, two Klee cards convert, one companion feed
retires on the strength of the replacement clause itself.

#### PICK K2 — the feed dispositions

1. **The table as written** — *Claude's recommendation.* Two retire, Catalytic
   Converter and Blazing Delight convert to Sparks at derived rates, Durin
   retires under LAW:145.
2. **The table, but Durin converts too** — accept a companion paying Sparks, and
   carve an explicit exception into the replacement clause for a Rare
   Klee-flavoured companion.
3. **All five retire** — the cleanest possible retirement; Catalytic Converter
   and Blazing Delight lose their resource rider and are re-authored as
   damage/utility cards in the Sparks round.

**Timing.** This rides the unsigned **M51** pick list
(`docs/current/QUEUE.md:76`) or the Sparks arm's next round, and everything ships
behind **`SPARK_ALT_COST_ENABLED`** (`review/active/klee-sparks-2026-08-29.md:453,
459, 631`), which is `False` in `tier0/constants.py` today. Nothing here opens a
window.

---

### 4.3 Kokomi — Ceremonial Garment becomes a Charge-drain state

**Timing is settled by [USER] at §1.3: pick 1.** The sealed Kurage run goes as
staged. The pinned seeds `KURAGEMEM001` / `002` / `003`
(`review/active/kokomi-kurage-memory-2026-08-29.md:1796–1798`) are unused and
remain sealed (`:2051`); the Burst fold is the **next** Kokomi slice's work and
does not touch that registration.

R74's reasoning is the whole design brief here. The Garment is *a window on
Charge*, not a damage button. Today it is a window bought with a second
currency. Under the fold it is a window bought with the currency it reads.

#### Options for the fold

**(a) State length paid from Charge.** Spend N Charge, get N/k turns of Garment
(floor 1). The player chooses how long the window is. The only option where both
numbers the card already has (`CEREMONIAL_GARMENT_TURNS` 3,
`GARMENT_CHARGE_DIVISOR` 2) stay meaningful.

**(b) Pulse count paid from Charge.** Spend all Charge, the jellyfish pulses that
many extra times. Closest to the Klee shape and to Stardust, and it folds PICK 3
for free — but it turns her state card into a damage card, the exact thing R74
removed.

**(c) The memory replays under the state.** Entering the Garment replays the
Kurage's memory, paid from Charge. Deepest fit with the rework; also the most
machinery, and it depends on the memory's final shape, which the sealed run has
not graded.

**(d) Garment as-is, fed by Charge instead of a second meter.** A Charge
*threshold* replaces `requires: burst_energy_full`; entry drains it; everything
else is byte-identical. Smallest diff, no design risk — and it delivers the
retirement without delivering "more useful," which is half of what [USER] asked
for at §1.1.

**The Tamakushi Casket link folds in here.** PICK 3 of the Kurage packet
(`:1388–1396`) is the Garment's Casket refresh, which under the v3 persistent
summon "now pays nothing — refreshing something that never expires is nothing.
This is her canon E-into-Q loop, and under the base kit it is silent." Its three
options were: leave it silent / re-key the refresh to an immediate extra pulse /
retire the link. **Option (b) above absorbs option 2 of PICK 3 exactly** — if
the Garment's own body pulses the jellyfish, the Casket's refresh has a live
referent again. Under (a), (c) or (d), PICK 3 still needs its own answer.

#### What the retirement does to her income

`KOKOMI_BURST_PER_EXHAUST` = 2 (`tier0/constants.py:405`) retires with the
meter. Her Exhaust event stops paying two currencies and pays one:
`CHARGE_PER_EXHAUST` = 1 (`:403`).

Three consequences, and they are not all in the same direction:

1. **The Kurage packet's line-645 asymmetry vanishes.** A Mustered Companion's
   Exhaust currently pays Burst but not Charge. After the retirement it pays
   whatever the Charge funnel says it pays, and there is no second wage to
   forget about. This is a clean win and it removes a documented inconsistency
   rather than papering over it.
2. **Her Burst becomes strictly slower to reach, then instantly reachable.**
   Today four bake plays fill a 20-point meter
   (`docs/kokomi-cards.yaml:687`). After the fold there is no meter — there is a
   threshold on a bank she was already growing at 1 Charge per Exhaust. Whether
   that is faster or slower depends entirely on which fold option and which
   threshold, so **it must be derived, not carried over**.
3. **`EB-74` is touched.** The staged lever (`docs/current/BACKLOG.md:66`,
   `staged/eb74-lever2-b-alone` at `5f09864`) is `CHARGE_PER_EXHAUST` 1→2 with
   `KOKOMI_BURST_PER_EXHAUST` **untouched**. That "untouched" is the whole point
   of the `B-alone` arm, and the retirement deletes the constant the arm holds
   still. The lever is not invalidated, but its *description* stops being true.
   Booked in §7 as owed.

#### PICK KO1 — the Kokomi fold shape

1. **(a) State length paid from Charge** — *Claude's recommendation.* It keeps
   R74's ruling intact (the card is still a state, not a nuke), it makes the
   player's banked Charge buy something the player chooses, and it is the option
   where "more useful" (§1.1) is delivered by *agency* rather than by numbers.
   Both existing constants survive with meaning.
2. **(b) Pulse count paid from Charge** — folds Kurage PICK 3 for free and gives
   her the same legible verb as Klee's, at the cost of re-opening what R74
   closed.
3. **(c) The memory replays under the state** — the deepest fold and the best
   fit with the rework's own subject matter; blocked until the sealed run is
   graded, so it cannot be the *next* slice's opener without a wait.
4. **(d) Garment as-is, Charge-fed** — the minimum-risk retirement. Choose it if
   the priority is landing the concept and re-opening her payoff later.

#### PICK KO2 — the Tamakushi Casket link (Kurage PICK 3, re-homed)

1. **Fold it into the answer to KO1** — *Claude's recommendation.* If KO1
   resolves to (b), the link is live and PICK 3 answers itself as its option 2.
   Under (a), (c) or (d), re-key the refresh to an immediate extra pulse so her
   canon E-into-Q loop still visibly fires.
2. **Leave it silent** — Kurage PICK 3 option 1, unchanged.
3. **Retire the link and say so on the relic's face** — Kurage PICK 3 option 3.

---

## §5 — Engineering blast radius and sequence

### 5.1 Sim (`tier0/`)

| surface | site | change |
|---|---|---|
| player field | `burst_energy`, `burst_max` on the player state | removed after step 4 of §3.3 |
| character sheets | `furina.yaml:25`, `klee.yaml:11`, `kokomi.yaml:35` | `burst_max` rows deleted |
| kit grant | `combat.py:116` `grant_charged_kit` | deleted, or retained for whichever payoff stays kit (Kokomi's, pending KO1) |
| playability gate | `combat.py:213` `requires == "burst_energy_full"` | the whole `requires` value retires; `draw_pile_empty` is unaffected |
| the drain | `combat.py:471` | deleted with the skill-tag grant beside it |
| card op | `effects.py:1677` `_op_burst_energy` | retires; any surviving card rider re-points to `gain_spark` / Fanfare / `gain_charge` |
| funnel | `resources.py:503` `gain_burst` | retires; its source-attribution shape is the template the replacement riders should copy |
| reaction feeds | `reactions.py:208, 215` | `:208` retires; `:215` converts under PICK K2 |
| card feeds | `effects.py:901, 4736` | `:901` converts, `:4736` retires under PICK K2 |
| constants | `constants.py:129, 130, 136, 144, 148, 379, 381, 405` | eight constants; retirement or conversion per PICK K2 and the Furina reframe |
| card tag | `tags: [burst]` on three rows | rename or drop — R179 lets lint settle it if cosmetic |

### 5.2 The pilot — the expensive part

`PILOT_BURST_DIVISOR = 10.0` (`tier0/constants.py:953`) means the drafter and the
policy **price burst points** when they score a card. Removing the term changes
what every Klee/Furina/Kokomi deck drafts and plays. That is a `POLICY_VERSION`
bump — `P` is **11** today (`docs/current/STATE.md:25`) — and a `POLICY_VERSION`
bump carries a re-baseline.

**Merge it with the HP re-baseline.** `review/active/roster-hp-scalers-2026-08-29.md`
already owes a twelve-arm re-run: its §7 books the cost, `:172` names *"the
standing twelve-arm baseline"*, and `:206` says explicitly *"The twelve-arm table
should be re-run in one pass **after** the merge, not before."* The Burst
retirement and the HP change are both whole-table movers with no interaction
worth isolating, and re-baselining twice would burn the compute twice for one
answer. **One combined twelve-arm re-baseline discharges both**, taken after the
last fold lands.

> *Register note:* **EB-194 through EB-197 are already minted on the unmerged
> `kokomi-blind-run` branch** — EB-194 the `+proto` boot regression, **EB-195 the
> twelve-arm re-baseline owed after the HP change**, EB-196/197 the Kurage memory
> and buff-text defects. `main` still shows EB-193 as the ceiling only because
> that branch has not merged. §7 therefore numbers this packet's rows from
> EB-198 and merges the pilot bump into the existing EB-195.

### 5.3 C# (`klee-mod/KleeCode/`)

- `Powers/BurstResource.cs` — `BurstConstants`, `KleeBurstResource`,
  `BurstMeterPower` (already a retired display kept for save-compat, `:248–251`);
  that save-compat pattern is the precedent for retiring these types without
  breaking loads. `Powers/KitBurst.cs` — under PICK K1 `SparksNSplashPower`
  becomes a card effect and `KitGrant` loses its Klee caller.
  `Powers/FurinaResources.cs:113–117, 257–298, 610, 635` — five constants, the
  resource, `DrainOnPlay` (read its "infinite-Burst bug, 2026-07-24" comment
  before touching it), `GainBurst`. `Powers/KokomiResources.cs:43–68, 118,
  415–424` — the mirror table, `BurstMax`, `FindBurst`.
- **The three pools** (`KleeCardPool.cs:38, 68, 101` / `KleeOffPoolCards.cs:12,
  76` / `KokomiCardPool.cs:22, 86–110`): under the LOOT ruling at §3.2 Klee's and
  Furina's cards move **into** the draftable pool — a pool-composition change
  with its own rarity-coverage lint.
- **Loc and text:** `KleeMod.cs:148` (the skill-tag rider) retires;
  `KleeMod.cs:271–278` is the `Burst Energy` keyword. **An id is an API** (LAW,
  klee-mod findings 7/15/23) — changing `KleeCardTooltips.BurstKey` requires a
  consumer sweep over loc keys and asset paths.
  `Cards/KleeCardTooltips.cs:104–128` is its three-branch reader.
- **`Vfx/GaugeBridge.cs:42–51, 137–202+` — the cheapest surface.** The anchor,
  the three skins and the flash predicates all survive; only `ReadValue` /
  `VisualSpan` / `LabelMax` re-point. Kokomi's Charge (`:203+`) graduates from
  `SecondRowAnchor` to `OverheadBurstAnchor`, and its "no bar because Charge is
  uncapped" comment becomes a live design question the moment Charge is
  spendable. `Powers/KleePowerIcons.cs:30, 152, 167` is the retired-display
  registry — `FurinaBurstMeterPower` already sits there as *"retired display
  (sprint 2 E1); save-compat only"*, which is the treatment for the rest.

### 5.4 Tests that assert Burst behaviour

`grep -rn "burst_energy\|burst_max" tier0/tests/` — **30 files** carry the string
`burst`; the direct assertions live in:

| file | what it pins |
|---|---|
| `test_klee.py:277, 290, 417, 427–436, 447–459, 472–473` | the meter, the grant, "casting empties the meter", refill re-grants |
| `test_furina_sheet.py:340, 438, 441, 484, 1048, 1058, 1066` | `burst_max == 70`, Salon-tick income, the cast drain |
| `test_kokomi.py:38, 71` | `burst_max == 20`, `KOKOMI_BURST_PER_EXHAUST` |
| `test_kokomi_rotation_law.py:149, 154` | no particle from a Status/Curse exhaust — the LAW:248 red test |
| `test_orobas_upgraded_starters.py:109, 114, 145, 197` | the exhaust wage, including an explicit "additive would read 6" |
| `test_ethereal_base_field.py:109` | the exhaust wage on the ethereal path |
| `test_kurage_memory.py:441–445` | that the memory pays no burst |
| `test_eb118_salon_verbs.py:99, 172, 224, 231` | Salon income, with `assert st.player.burst_max, "the fixture must have a burst meter"` |
| `test_eb118_connectivity.py:139` | `"burst": _row(requires="burst_energy_full")` — a connectivity row keyed on the gate |
| `test_eb118_phase1.py:271`, `test_errata.py:49`, `test_furina_fanfare_parity.py:147` | fixtures and the `burst_energy` op |

Every one of these is a **rewrite, not a delete** — each becomes the same
assertion against the signature resource. `test_kokomi_rotation_law.py` in
particular is the red test for a LAW clause being amended, so its rewrite is
part of the LAW change, not cleanup after it.

### 5.5 Order

Per §3.3: **Kokomi's fold (next slice) → Klee's round → Furina's reframe → the
shared retirement, last.** Each of the first three lands behind its own flag and
its own slice's grading. The fourth is one branch that touches the engine, the
three sheets, the pilot, the C# and the LAW at once, and it lands with the
combined re-baseline.

---

## §6 — What returns to [USER]

Three things, and only three.

1. **The concept countersign and the LAW text** — §3.1's architecture paragraph
   and the eight replacement blocks in §3.2. This is a LAW amendment, which the
   delegation ladder keeps with [USER] regardless of anything else here.
2. **PICK K1** — Sparks 'n' Splash at Rare with a stronger body (recommended) or
   Uncommon matching Stardust. **Plus PICK K2**, the five feed dispositions.
3. **PICK KO1** — the Kokomi fold shape, four options, (a) recommended. **Plus
   PICK KO2**, the Tamakushi Casket link re-homed from Kurage PICK 3.

**One dependency to flag before answering K1:** `docs/current/LAW.md:481` lists
`spark` as **bounded at 3**. If that holds, a spend-all Sparks card has a
three-point ceiling and the Uncommon reading (K1 option 2) is the correct one; if
Sparks become unbounded — which the measured +22 net bank
(`klee-sparks-2026-08-29.md:863`) suggests they effectively already are in play —
the Rare reading (option 1) is. That question lives in the Klee Sparks work
(M51), not here, and K1 should be answered with it in view.

---

## §7 — Register changes OWED (not made on this branch)

> **LANDED AS `M60`, `EB-199` AND `EB-200` BY R220** (2026-08-29). Every id
> this section reserved had collided by the time the slate opened: `M52` was
> already Furina's countersign row and `M54`–`M58` were minted by the blind run
> and the tester seat, so the four picks are `M60`; `EB-198` was minted by the
> blind run for the memory-strip diagnosis, so the shared retirement is
> `EB-199` and its C# arm is `EB-200`. `M51`'s re-pointing was overtaken too —
> the row is COUNTERSIGNED (R220 F) and `LAW.md:481` moved `spark` to the
> unbounded meters with it, which discharges the K1 dependency this packet
> flags at §6. Pointer only — the text below stands as written.

Nothing below is edited by this branch. All of it lands in one slate under one
ruling.

**Ruling.** Next free id is **R220** (`docs/current/RULINGS.md` runs to R219).
The slate carries: §1's verbatim words in the commit message; §3.1's
architecture paragraph; §3.2's eight LAW replacement blocks, marked PROSPECTIVE;
and the answers to K1 / K2 / KO1 / KO2.

**QUEUE — one M row.** Next free id is **M52** (`docs/current/QUEUE.md` runs to
M51). One row carrying all four picks, per R206/R212's one-batch rule — not four
transient rows.

**QUEUE — re-pointing.**
- **M51** (`QUEUE.md:76`, the Klee Sparks countersign) gains a line: the Sparks
  re-author now also carries the Burst fold, and PICK K1's rarity call is a
  Sparks-arm decision.
- **M50** (`QUEUE.md:75`, the four unruled Kurage rows) — its **PICK 3** (the
  Casket refresh link) is answered by **KO2** and should point here rather than
  be answered twice.

**BACKLOG — EB rows.** Next free id is **EB-198** (EB-194–197 are minted on
`kokomi-blind-run`, unmerged; `main` runs to EB-193 until it lands).
- **EB-198** — the shared retirement itself: engine fields, ops, the `requires`
  gate, the kit-grant machinery, the eight constants, the three sheets'
  `burst_max`, and the ~30 test files. Gate: all three folds landed. Acceptance:
  `grep -i burst_energy tier0/` returns nothing outside retired-display comments.
- **EB-195** (exists, on `kokomi-blind-run`) — gains the `POLICY_VERSION` bump
  for `PILOT_BURST_DIVISOR`'s removal, **explicitly merged** with its twelve-arm
  re-baseline into one run. Not minted here; its row text is amended when the
  ruling lands.
- **EB-199** — the C# arm: the three pools' off-pool carve-outs, the keyword loc
  id and its consumer sweep, the retired-display registry entries, and the
  `GaugeBridge` re-point including Kokomi's Charge graduating to the overhead
  anchor.
- **EB-74's description is stale** (`BACKLOG.md:66`): the `B-alone` arm is
  defined as "`KOKOMI_BURST_PER_EXHAUST` untouched", and the retirement deletes
  that constant. The lever is not invalidated; the row needs a line saying the
  arm's control disappears with the meter. Hygiene once the ruling lands.
- **EB-192 / EB-193** (`:103–104`) are unchanged by this packet but are the
  reason §2.8's Regent numbers are cited as a design anchor rather than a
  measured baseline.

**STATE.md.** The R213 sequence paragraph (`:286–300`) gains the retirement's
inverted tail — Kokomi → Klee → Furina for the folds, shared retirement last.
`P` at `:25` moves when EB-195 runs.

**No YAML, no LAW, no code, no `tools/lint_register_ids.py` edit is owed by this
branch.** All of it is owed by the slate.

---

## §8 — Grading roles

Per R213 as amended by R217, and R212's ladder:

- **[USER]** authored the direction (§1.1, §1.3) and owns the countersign, the
  LAW text and the three picks in §6. Briefs and final signoff are his.
- **Claude** authored this packet: the recommendation at §1.2, every citation in
  §2, the LAW replacement drafting in §3, the analysis and the pick lists in §4,
  and the blast radius in §5. Recommendations are marked as such and every pick
  is a numbered list, never a blank.
- **The Codex seat** (`understudy/seat.py`, independence by model family)
  **doctrine-gates** this packet: it RETURNS or ADVANCES against LAW and the D1–D9
  charter with no [USER] form. A seat RETURN on any clause in §3.2 sends that
  clause back before it reaches the countersign. SURVIVES is never ship approval.
- **No GPT-authored rows appear in this packet**, so there is nothing here for a
  fresh-Claude read to grade — the fresh-read step is not owed.
- No experiment is registered by this packet and no seed is drawn. The sealed
  Kurage seeds `KURAGEMEM001/002/003` are untouched and stay sealed.

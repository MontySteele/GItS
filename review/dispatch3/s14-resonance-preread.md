# S14 — Elemental Resonance pre-read

> **SURPLUS-ONLY. Decides nothing.** This file is a census and a question list.
> It is **not** evidence that Elemental Resonance belongs in public v1, it
> outranks nothing in the morning read, and it proposes no mechanic, no number,
> and no scope. Read it last (charter §6, morning read order item 7).
>
> **Retrieval date for every mutable-canon claim below: 2026-08-26.**
> Genshin Impact canon is live-service and changes on patch cadence; each row
> is pinned to the exact source revision that was read, and two of the sources
> read tonight **disagree with each other** (see §1.4).

---

## 1. Dated canon census

### 1.1 Sources actually read (all retrieved 2026-08-26)

| # | Source | Kind | Pin |
|---|---|---|---|
| S1 | HoYoWiki (official HoYoverse), "Elemental Resonance", entry 5559 | **Primary / official** | `https://wiki.hoyolab.com/pc/genshin/entry/5559?lang=en-us`, read via `https://sg-wiki-api-static.hoyolab.com/hoyowiki/genshin/wapi/entry_page?entry_page_id=5559`; JSON field `data.page.version = 1755050563` (Unix seconds → 2025-08-13). Menu: `Tutorial`. |
| S2 | Fandom Genshin Impact Wiki, page **"Team Bonus"** | **Secondary**, revision-pinned | revid **2128871**, timestamp `2026-07-13T03:39:21Z` |
| S3 | Fandom Genshin Impact Wiki, page **"Genius Invokation TCG"** | Secondary, revision-pinned | revid **2071511**, `2026-04-03T00:48:58Z` |
| S4 | Fandom, 14 × `Elemental Resonance: <name>` TCG Event Card pages | Secondary, revision-pinned | revids listed per row in §1.5 |

Charter §3.6 requires official pages first and permits a wiki only as a
secondary with its own revision pinned. That is what was done. **S1 is the only
HoYoverse-authored text quoted here**; S2–S4 are community text and are labelled
as such at every use.

**Search boundary.** Only the four sources above were read. The in-game Party
Setup screen was **not** read (charter forbids launching the game tonight —
[USER] is playtesting on `0.2-1155`). No HoYoverse patch-notes page was
successfully retrieved: the announcement URL cited by S2
(`https://genshin.hoyoverse.com/en/news/detail/159216`, "The Blessing of
Moonlight") returned only the site shell to the fetcher, so **the Moonsign /
Lunar-reaction material in §1.3 rests on S2 alone and is UNVERIFIED against an
official source.**

### 1.2 The party-composition resonance table (official wording, S1)

Quoted from S1 (official HoYoverse), retrieved 2026-08-26, page version stamp
2025-08-13. Requirement column is S1's own.

| Resonance | Requirement | Effect (S1 wording) |
|---|---|---|
| Fervent Flames | Pyro + Pyro | "Affected by Cryo for 40% less time. Increases ATK by 25%." |
| Soothing Water | Hydro + Hydro | "Affected by Pyro for 40% less time. Increases Max HP by 25%" |
| Impetuous Winds | Anemo + Anemo | "Decreases Stamina Consumption by 15%. Increases Movement SPD by 10%. Shortens Skill CD by 5%." |
| High Voltage | Electro + Electro | "Affected by Hydro for 40% less time. Superconduct, Overloaded, Electro-Charged, Quicken, Aggravate, or Hyperbloom have a 100% chance to generate an Electro Elemental Particle (CD: 5s)" |
| Sprawling Greenery | Dendro + Dendro | "Elemental Mastery increased by 50. After triggering Burning, Quicken, or Bloom reactions, all nearby party members gain 30 Elemental Mastery for 6s. After triggering Aggravate, Spread, Hyperbloom, or Burgeon reactions, all nearby party members gain 20 Elemental Mastery for 6s. The duration of the aforementioned effects will be counted independently." |
| Shattering Ice | Cryo + Cryo | "Affected by Electro for 40% less time. Increases CRIT Rate against opponents that are Frozen or affected by Cryo by 15%." |
| Enduring Rock | Geo + Geo | "Increases shield strength by 15%. Additionally, characters protected by a shield will have the following special characteristics: DMG dealt increased by 15%, dealing DMG to enemies will decrease their Geo RES by 20% for 15s." |
| Protective Canopy | **Any 4 Unique Elements** | "All Elemental RES +15%, Physical RES +15%." |

**Eight effects total. Seven are same-element pairs; one (Protective Canopy) is
the four-unique-element case.**

Activation rules, quoted/paraphrased from S1:

- "When the party contains at least 4 characters, Elemental Resonance Effects
  corresponding to the Elemental Types present in the party will be provided."
- "To activate any Elemental Resonance except Protective Canopy, 2+ characters
  of the specific Element are needed."
- "The maximum number of Elemental Resonance present in the part[y] is 2."
- Available in any Party Setup — Overworld, Abyss, Domain (S1).
- Trial characters count. With more than four characters in the party, only the
  **first four** are considered (S1).
- Inside domains, only characters present in the party benefit (S1).
- "Elemental Resonance will activate in Co-op mode as long as the requirements
  are met." (S1)
- S2 adds two rules S1 does not state: effects **"do not require all party
  members to be alive"**, and in Co-Op, if part of the party is inside a Domain,
  "the resonance will only be determined by the characters that are in the
  Domain, and only characters in the Domain will benefit." (S2, secondary.)

### 1.3 Single-element parties, and the wider "Team Bonus" frame

**There is no single-element (mono-element / 3-of-a-kind / 4-of-a-kind)
resonance.** Both sources state the pair threshold does not scale: S1 caps the
party at two simultaneous resonances and requires "2+"; S2 states "Having more
than two characters of the same element does not further enhance the
corresponding Resonance." A four-Pyro party therefore receives exactly Fervent
Flames and nothing further. **This is a NON-FINDING against the charter's
"incl. single-element" phrasing, not an omission.** The only non-pair
composition effect in the whole system is Protective Canopy (four unique
elements).

**However, "Elemental Resonance" is now one of at least three siblings under a
containing system.** S2 (revid 2128871, 2026-07-13) titles the page **"Team
Bonus"** and documents, alongside Elemental Resonance:

| Sibling | Keyed from | Threshold (S2) | UNVERIFIED against official source |
|---|---|---|---|
| **Moonsign** | count of "Moonsign characters" in party | 1 → "Nascent Gleam"; 2 → "Ascendant Gleam" | yes — S2 only |
| **Hexerei** | count of "Hexerei characters" in party | 2 → "Hexerei: Secret Rite" | yes — S2 only. S2 also says Hexerei status is *earned per character* by completing "Witch's Homework", i.e. it is an account-progress flag, not an intrinsic character property |
| **Nightsoul Burst** (region-based) | count of Natlanese characters | 1 / 2 / 3+ → interval 18s / 12s / 9s | yes — S2 only. S2 notes it is **not** shown on the Party Setup menu, unlike the three above |

S2 also records that Ascendant Gleam's party buff **keys off the element of the
non-Moonsign character that cast a skill/burst**, converting one of that
character's own stats into Lunar-Reaction DMG for the party — i.e. a
composition effect whose magnitude is read from a teammate's build, not from a
flat table.

### 1.4 Source disagreement found tonight — read this before citing anything

1. **S1 (official) is behind S2 (community) on wording.** S2's High Voltage,
   Enduring Rock and Sprawling Greenery rows name **Stellar-Conduct,
   Lunar-Charged, Lunar-Bloom, Lunar-Crystallize** and **Moondrifts**; none of
   those terms appear in S1. S1's page stamp is 2025-08-13; S2's revision is
   2026-07-13. Direction of the discrepancy is consistent with S1 being stale,
   but **that is an inference, not a citation.** Anything that must be exact
   should be re-read from the live game or a HoYoverse patch note.
2. **A widely-mirrored third-party summary contradicts both.** A search result
   surfaced tonight rendered Soothing Water as "increases incoming healing by
   30%". **Both** S1 and S2 say "Increases Max HP by 25%". The healing wording
   is stale canon and is recorded here only so nobody re-imports it.
3. Two ancillary claims in S2's own header are marked `{{Stub|Verify}}` by the
   wiki itself — Co-Op behaviour when players are on different maps, and
   Moonsign coverage. S2 does not consider its own co-op section settled.

### 1.5 Special / event variant: the Genius Invokation TCG resonance cards

This is the one place HoYoverse has already re-expressed Resonance **as a card
game**, which is why it is in this census rather than in §3.

Gating rule (S3, revid 2071511, 2026-04-03): "Elemental Resonance Cards provide
effects based on having two Character Cards of the same element in the deck."
So the composition check moved from *party slots* to *deck contents*, and the
payoff moved from a passive aura to a **playable Event Card**.

Fourteen cards, two per element (a cheap "Woven" die-fixer and a themed
payoff). Effects quoted from S4; each row carries its own Fandom revid.

| Card | Element | Effect (S4) | revid / timestamp |
|---|---|---|---|
| Woven Flames | Pyro | "Create 1 Pyro Die." | 2128923 / 2026-07-13 |
| Woven Waters | Hydro | "Create 1 Hydro Die." | 2085637 / 2026-04-29 |
| Woven Thunder | Electro | "Create 1 Electro Die." | 1567344 / 2024-07-13 |
| Woven Ice | Cryo | "Create 1 Cryo Die." | 2128922 / 2026-07-13 |
| Woven Winds | Anemo | "Create 1 Anemo Die." | 1567338 / 2024-07-13 |
| Woven Stone | Geo | "Create 1 Geo Die." | 1567341 / 2024-07-13 |
| Woven Weeds | Dendro | "Create 1 Dendro Die." | 1567339 / 2024-07-13 |
| Fervent Flames | Pyro | "During this round, the next instance of Pyro-Related Reactions your current active character triggers deals +3 DMG." | 1567346 / 2024-07-13 |
| Soothing Water | Hydro | "Heal your active character for 2 HP and all your characters on standby for 1 HP." | 2085636 / 2026-04-29 |
| High Voltage | Electro | "Your active character and your next character without maximum Energy gain 1 Energy." | 1729409 / 2025-03-24 |
| Shattering Ice | Cryo | "During this Round, your current active character will deal +2 DMG for the next instance." | 1567348 / 2024-07-13 |
| Impetuous Winds | Anemo | "The next time you perform \"Switch Character\": This action will be considered a Fast Action instead of a Combat Action. It will also cost 1 less Elemental Die.<br>The next Swirl Reaction you trigger deals +1 DMG to all opposing characters except the target." | 1729412 / 2025-03-24 |
| Enduring Rock | Geo | "Grants 3 Shield points to your active character." | 1729416 / 2025-03-24 |
| Sprawling Greenery | Dendro | "If you have Burning Flame/Dendro Core or Bountiful Core/Catalyzing Field on the field, deal 1 Pyro DMG/Hydro DMG/Electro DMG to the opposing active character." | 1749503 / 2025-05-08 |

Structural note, not a proposal: **there is no TCG analogue of Protective
Canopy** in the fourteen, and the TCG versions share only the *names* with the
overworld effects — every payoff was rewritten into card-game currency (dice,
Energy, Shield, one-shot DMG riders), and the two-of-an-element requirement is
the only thing carried across intact.

---

## 2. Structural read — what each effect keys from, fixed vs dynamic

"Keys from" = the input the game reads to decide the effect exists or how big it
is. "Fixed" = decided once at party assembly and constant thereafter.
"Dynamic" = re-evaluated during play.

### 2.1 Activation layer (uniform across all eight)

| Property | Value | Source |
|---|---|---|
| Input | multiset of Elemental Types over the **first four party slots** | S1 |
| Predicate | `count(element) >= 2`, or `distinct(elements) == 4` for Protective Canopy | S1 |
| Saturation | none — 3 or 4 of an element is identical to 2 | S2 |
| Simultaneity cap | 2 resonances maximum | S1 |
| Liveness | not gated on party members being alive | S2 (secondary) |
| Re-evaluation | at party assembly / domain entry, **not** on active-character swap | S1 ("Elemental Resonance can be found in any Party Setup"; effects are party-wide, not active-character-scoped) |

So the **activation** half is **FIXED** for the duration of a party
configuration, with one documented exception: domain entry in co-op recomputes
the membership set (S2).

### 2.2 Payoff layer — this is where fixed and dynamic separate

| Resonance | Payoff shape | Fixed or dynamic | What the payoff keys from (beyond composition) |
|---|---|---|---|
| Fervent Flames | flat stat multiplier + status-duration modifier | **fixed** | nothing; always-on |
| Soothing Water | flat stat multiplier + status-duration modifier | **fixed** | nothing; always-on |
| Impetuous Winds | flat modifiers to stamina, move speed, skill cooldown | **fixed** | nothing; always-on |
| Shattering Ice | conditional stat — CRIT Rate **only vs. targets that are Frozen or Cryo-affected** | **dynamic** | live **enemy aura state** |
| Protective Canopy | flat resistance | **fixed** | nothing; always-on |
| Enduring Rock | shield-strength multiplier is fixed; the +15% DMG and the Geo-RES shred are **gated on the character currently being shielded** (S2 adds: or near a Lunar-Crystallize Moondrift) | **hybrid** | live **self/ally buff state** |
| High Voltage | duration modifier is fixed; the particle generation is an **event trigger with its own 5s cooldown**, fired by a named reaction list | **dynamic** | live **reaction events** + an internal cooldown |
| Sprawling Greenery | +50 EM is fixed; two stacking-independent 6s EM buffs are **event-triggered by two disjoint reaction lists** | **hybrid** | live **reaction events**, with two independent duration timers |

**Three structural families fall out of that table, and they are not
interchangeable:**

1. **Always-on stat riders** (Fervent Flames, Soothing Water, Impetuous Winds,
   Protective Canopy) — composition is the *only* input.
2. **State-conditional riders** (Shattering Ice, Enduring Rock) — composition
   opens the effect; a second live predicate decides whether it applies on a
   given hit.
3. **Reaction-event triggers** (High Voltage, Sprawling Greenery) — composition
   subscribes the party to an event stream; the payoff is emitted per reaction,
   with an internal governor (a cooldown for High Voltage, independent buff
   timers for Sprawling Greenery).

Family 3 is the only one that **reads the reaction layer**, and both of its
members carry an anti-spam governor in canon.

### 2.3 The sibling systems, same axes (all UNVERIFIED / S2 only)

| System | Input | Fixed or dynamic |
|---|---|---|
| Moonsign Nascent Gleam | count of a **tagged character class** in party | fixed |
| Moonsign Ascendant Gleam | same count, **plus** the element and a *stat value* of whichever non-Moonsign character last cast a skill/burst, capped, non-stacking, 20s window | **dynamic and build-dependent** |
| Hexerei: Secret Rite | count of Hexerei characters, where "is Hexerei" is itself an **account-progression flag** earned per character | fixed at party assembly; the underlying flag is account state |
| Nightsoul Burst | count of characters with a **region** tag | fixed threshold, dynamic firing (interval timer) |

Two structural facts worth carrying forward regardless of any design view:
composition effects in current canon key off **tags that are not elements**
(Moonsign, Hexerei, region), and at least one of those tags is **mutable
account progress rather than an intrinsic character property**.

---

## 3. Prior-art scan — composition passives in deckbuilders / co-op mods

**Scope searched:** the pinned Downfall clone (`lamali292/Downfall`, verified
locally at `git rev-parse HEAD` = `32e61132052ae58e32cd33342d24136ffe18be12`,
1,858 `.cs` files) and the BaseLib artifact it depends on. Reference-reading
only, charter §3.7. No code, text or asset was copied.

### 3.1 NON-FINDING — no composition passive exists in Downfall

| Probe | Command shape | Result |
|---|---|---|
| Any resonance-like concept | `grep -ril "resonance"` over `*.cs`, `*.json`, `*.md` | **zero hits** |
| Deck-composition counting (a passive that reads the whole deck) | `grep -rn -iE "MasterDeck\|CardsInDeck\|CountCards\|deck\.Count\|GetCards\("` | 4 hits, **all local pile queries** — `CollectorCode/Cards/Uncommon/SeverSoul.cs:25,33`; `HermitCode/Cards/Rare/FromBeyond.cs:18,24` (counts the exhaust pile); `HexaghostCode/Cards/Uncommon/HauntedHand.cs:25` (hand size). None reads party/seat composition. |

**Conclusion: Downfall implements no party- or deck-composition passive of any
kind.** That is a genuine NON-FINDING, not a gap in the search: the search
boundary is the whole pinned tree.

### 3.2 What Downfall *does* have that is adjacent (and what it isn't)

These are the nearest structural neighbours. **None of them is a composition
passive** — each is recorded so the distinction is not blurred later.

| Mechanism | Pointer (Downfall@32e6113) | What it actually is |
|---|---|---|
| `CardMultiplayerConstraint.MultiplayerOnly` | 35 occurrences across `*/Cards/Multiplayer/*.cs`, e.g. `ChampCode/Cards/Multiplayer/GroupEffort.cs:20` | A **base-engine card-availability gate keyed on seat count**. It changes whether a card exists in the pool, not what a passive does. This is the closest StS2-native primitive to "composition changes the rules", and it is binary (multiplayer yes/no), not element- or identity-keyed. |
| `AffectsAllPlayers => true` | `ChampCode/Cards/Multiplayer/GroupEffort.cs:26` | Play-time targeting breadth, per card. Not a passive and not composition-conditional. |
| Character-identity check on a seat | `AutomatonCode/Core/AutomatonModel.cs:20` — `if (player.Character is Automaton)` inside `AfterRoomEntered` | Proof that **a mod can enumerate `state.Players` and branch on each seat's `Character`**. Used here only to attach that character's own UI display. It is the mechanical prerequisite a composition passive would need, and it is the only place in the tree that uses it. |
| Cross-seat card delivery | `SneckoCode/Powers/DiceCasePower.cs:32-34` (`TargetCreature?.Player`, `GiveCards<SoulRoll>(otherPlayer, ...)`) | Directed effect at another seat. Composition-blind. |
| Seven per-character `Cards/Multiplayer/` directories, 5 cards each (35 total) | `Automaton`, `Awakened`, `Champ`, `Guardian`, `Hermit`, `Hexaghost`, `Snecko` | Downfall's whole co-op answer is **per-character co-op-only cards**, i.e. content that appears when a second seat exists — never a passive that reads *which* characters are seated. |

### 3.3 Search boundary and what was not searched

- **BaseLib was not decompiled tonight.** The artifact is present at
  `C:\Program Files (x86)\Steam\steamapps\workshop\content\2868840\3737335127\BaseLib\BaseLib.dll`
  (1,090,560 bytes, mtime 2025-08-13), pinned in
  `klee-mod/local.props:4`. It was located, not read; a resonance-shaped
  abstraction there would have been found by S13's socket probe, not by this
  surplus stream. **UNKNOWN, not NON-FINDING.**
- The StS2 base game decompile was **not** searched for composition bonuses.
  Same reason. **UNKNOWN.**
- No non-StS2 deckbuilder (Monster Train, Griftlands, Wildfrost, StS1
  Downfall-for-StS1, etc.) was examined. Charter §3.6 requires primary sources
  — repository, release, or official documentation — and no such source was
  fetched tonight. **UNKNOWN, and deliberately left so rather than filled from
  memory.**

### 3.4 The only shipped card-game realisation found

The strongest prior art located tonight is HoYoverse's own: the fourteen Genius
Invokation TCG resonance Event Cards in §1.5. It is the single existing example
of this exact translation — party-composition passive → deckbuilder — and it was
resolved by making the effect a **playable card gated on deck composition**
rather than a passive. Recorded as a fact about canon. **No inference is drawn
from it here.**

---

## 4. Interaction surface — QUESTIONS ONLY

Every entry below is a question with a governing repo pointer. **No numbers, no
recommendations, no declarative design, no implied answer.** Nothing in this
section is a proposal, and a "yes" to any of them would still be [USER]'s call
under CLAUDE.md's delegation ladder.

### 4.1 Against the reactions layer

| # | Question | Governing pointer |
|---|---|---|
| Q1 | Our aura model is one aura per enemy, 2 player-turns, with Anemo/Geo trigger-only — canon resonance families 2 and 3 (§2.2) read live aura and reaction state. Which of those states, if any, is even *readable* at the point a party-wide passive would have to be evaluated? | `docs/current/LAW.md:46-47`; `tier0/engine/reactions.py:22` (`AURA_ELEMENTS`), `:51` `apply_aura`, `:100` `tick_auras`, `:115` `resolve_hit` |
| Q2 | LAW's iron rule forbids any reaction producing a persistent or compounding damage multiplier. Does a composition-keyed rider that *modifies* a reaction's output count against that rule, or is the rule scoped only to reaction-produced effects? | `docs/current/LAW.md:42-45`; `tier0/engine/reactions.py:24-28` (`_AMPLIFY`), `:30-36` (`_amp_mult`) |
| Q3 | Canon's two reaction-event resonances both carry an internal governor (a 5s particle cooldown; independent 6s timers). Our engine is turn-based with no wall-clock. What is the turn-based referent for "governor" here, and does one already exist to key from? | `tier0/engine/reactions.py:138` `_react`; `docs/current/LAW.md:67-70` (Overload/Electro-Charged bypass Block, pipeline-free) |
| Q4 | Reaction credit currently goes to the triggering player, with auras living on shared enemies. If a party-wide effect were keyed on reactions, who would be the subject of the effect — the triggerer, or every seat? | `docs/current/LAW.md:64-66`; `klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs:261-263` |
| Q5 | "Reactions are earned, not given" — off-element access comes only from companions or a co-op partner. Does a composition-keyed effect count as *giving* access, or is it downstream of access already earned? | `docs/current/LAW.md:39-41` |
| Q6 | Application cadence is a per-character dial (catalyst-grade vs skill-grade). Does that dial belong in a composition predicate at all, or is composition strictly about identity/element? | `docs/current/LAW.md:71-73`; `tier0/roster.py:112-127` |

### 4.2 Against co-op seats

| # | Question | Governing pointer |
|---|---|---|
| Q7 | Canon resonance keys off **four party slots**. We have 1–3 human seats, each driving one character. What is the repo's definition of the composition set — seats, or seats plus companions? | `docs/current/LAW.md:64-66`; `klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs:944-945` (`seats`, `seat_index`); charter §4 `S20` (1/2/3-player split) |
| Q8 | In single-player, is the composition set of size one — and if so, is a composition effect defined at all in that case, or absent? | `klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs:583-584` (seat enumeration); `docs/current/STATE.md` "Live cell" (tier 0.5 models one seat) |
| Q9 | Downfall's only composition-shaped primitive is a binary `MultiplayerOnly` availability gate on *cards*. Is card availability a candidate site for anything composition-keyed in our mod, or is availability out of scope for this question entirely? | `klee-mod/KleeCode/Cards/ModalChoice.cs:28` (seat sync); Downfall@32e6113 `ChampCode/Cards/Multiplayer/GroupEffort.cs:20` (reference-read only) |
| Q10 | S2 records that canon recomputes resonance membership on domain entry in co-op, and its own wiki flags co-op behaviour as unverified. What is our equivalent boundary event — combat entry, room entry, run start — and is there a single place that already fires there for all seats? | Downfall@32e6113 `AutomatonCode/Core/AutomatonModel.cs:14-23` (`AfterRoomEntered` enumerating `state.Players`) — reference pattern; ours: `klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs:169` (one record per seat) |
| Q11 | Co-op has only a partial automated backstop — per-seat ownership is testable, anything needing a live `CombatState` is play-only. Is a composition effect testable at all before it is played, and does that change whether the question can be answered from evidence? | `klee-mod/KleeTests/README.md`; `docs/current/STATE.md` §Systems (klee-mod bullet) |

### 4.3 Against companion nations

| # | Question | Governing pointer |
|---|---|---|
| Q12 | Companions are the mod's sole colorless content and route power through your character, never around them. Do companions belong in a composition set, given that including them would make the set drafted rather than chosen? | `docs/current/LAW.md:79-103`; `tier0/roster.py:53` (`nation:` = companion-pool home nation) |
| Q13 | Canon's newest composition tags are **regional** (Nightsoul Burst keys off Natlanese characters) and **progression-based** (Hexerei). Our roster already carries a `nation` field and ships companion pools per nation. Is nation a composition axis in this repo, or purely a pool-partitioning key? | `tier0/roster.py:53,112-127`; `docs/mondstadt-companions.yaml`, `docs/fontaine-companions.yaml`, `docs/inazuma-companions.yaml` |
| Q14 | The delete-test says removing a character's own cards from a winning deck must gut it. If a composition effect were sourced from companions, which side of the delete-test does the effect sit on? | `docs/current/LAW.md:87-97` (`SUPPORT_CARRY`) |
| Q15 | Hard CC is payoff-tier only and companions never source hard CC, enforced by the `control_uptime` / `SUPPORT_CARRY` detector. Would a composition-keyed effect be visible to that detector at all, or would it be structurally invisible to it? | `docs/current/LAW.md:59-63`; project norm on structurally invisible defects (`CLAUDE.md` §Norms; memory `structurally-invisible-defects`) |

### 4.4 Against banner limits

| # | Question | Governing pointer |
|---|---|---|
| Q16 | The Featured Banner gates 5-stars to `BANNER_FEATURED_SLOTS` per nation per run, and is explicitly a **runtime** governor rather than an authoring cap. Does a composition predicate interact with availability gating, or are the two orthogonal? | `tier0/constants.py:1090`; `docs/current/LAW.md:98-103`; `tier05/rewards.py:144,166-170` |
| Q17 | The banner is per-**player**, not per-run — in co-op each seat rolls its own lineup, and divergent lineups are stated to be the point. If composition were ever read across seats, whose banner state defines it? | `klee-mod/KleeCode/CompanionBanner.cs:35-39` ("PER PLAYER, NOT PER RUN"), `:49` (`FeaturedSlots = 3`) |
| Q18 | Sim/mod banner parity is explicitly **structural, not numeric** — the two engines pick different members for the same nominal seed. Does that parity standard survive a predicate that reads *which* members were picked? | `klee-mod/KleeCode/CompanionBanner.cs:40-44`; `tier05/tests/test_v18_banner.py:8-14` |

### 4.5 Against UI

| # | Question | Governing pointer |
|---|---|---|
| Q19 | Canon shows resonance as a persistent party-setup panel with met/unmet states (S1's gallery names exactly "Active Elemental Resonance" and "Inactive Elemental Resonance"). Does our mod have any surface that displays an unmet condition, as opposed to only active effects? | `klee-mod/KleeCode/Powers/KleePowerIcons.cs:149-160` (icon registry, incl. retired display entries) |
| Q20 | Aura and Bomb are `Buff`-typed so they coexist with Artifact; Frozen and reaction-applied debuffs stay real Debuffs. If a composition effect existed, would it be a Power at all — and if so, which side of that typing does it land on? | `docs/current/STATE.md` §Systems (tier0 bullet, Artifact coexistence); `docs/current/LAW.md:53-58`; `klee-mod/KleeCode/Powers/AuraPower.cs:208` |
| Q21 | Reaction telemetry currently lands **both** seats' reactions in every seat's row, and the file itself warns a reader who does not know that will misread it. Would a party-wide effect make that ambiguity worse, and is there an existing per-seat disambiguation to reuse? | `klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs:261-263,293-296` |
| Q22 | Eyes-on taste — including any badge or panel styling — is [USER]'s and is not delegated. Is there any part of this surface that is *not* an eyes-on call? | `CLAUDE.md` §Norms, delegation ladder R212 ("Still [USER]'s: eyes-on taste…") |

### 4.6 Against save identity

| # | Question | Governing pointer |
|---|---|---|
| Q23 | `CompanionBanner` deliberately hooks **no** save system: it is a pure function of the player's rng seed and is recomputed rather than stored, which is stated to be what makes it survive save/load for free. Is a composition effect derivable the same way — recomputed from party state — or would it need stored state? | `klee-mod/KleeCode/CompanionBanner.cs:29-33` |
| Q24 | This repo keeps retired Power classes registered purely so mid-combat saves written before a retirement still load. What is the save-compat obligation created by a Power that only exists under certain compositions — i.e. one that may be absent on load? | `klee-mod/KleeCode/Powers/BurstResource.cs:247`; `klee-mod/KleeCode/Powers/FurinaResources.cs:735,1087,1136`; `klee-mod/KleeCode/Powers/KleePowerIcons.cs:149,159-160` |
| Q25 | Starting companions are seeded so peers and save replays stay deterministic **without consuming native RNG**. Does a composition predicate read anything that could perturb that determinism? | `klee-mod/KleeCode/KleeStartingCompanions.cs:23` |
| Q26 | Canon's Hexerei tag is account progress, not an intrinsic character property (§2.3). Does this repo have any per-account or per-save flag that a composition predicate could legitimately read, or is all identity intrinsic to the roster registry? | `tier0/roster.py:53,112-127`; `docs/current/STATE.md` §Roster (pre-slot-4 gate is the roster registry) |
| Q27 | S20 (release readiness) owns save/update/removal as a separate census. Is any of Q23–Q26 already inside S20's scope, and therefore not a new question at all? | charter §4 `S20`; `review/dispatch3/s20-release-readiness/` (this dispatch) |

---

## 5. NON-FINDINGS and UNKNOWNS, collected

**NON-FINDINGS (searched, genuinely absent):**

- No single-element / mono-element resonance exists in Genshin canon. The pair
  threshold does not scale past two, and Protective Canopy is the only
  non-pair composition effect. (§1.3, S1 + S2)
- No composition passive of any kind exists in Downfall@32e6113 — zero hits for
  "resonance", and every deck/pile-counting call site is a local pile query.
  (§3.1)
- No TCG analogue of Protective Canopy exists among the fourteen resonance
  Event Cards. (§1.5)

**UNKNOWNS (not searched, or unresolvable tonight):**

- BaseLib 3.3.7.0 was located but not decompiled. Whether it exposes any
  composition-shaped abstraction is UNKNOWN. (§3.3)
- The StS2 base game decompile was not searched for composition bonuses.
  UNKNOWN. (§3.3)
- No non-StS2 deckbuilder was examined from a primary source. UNKNOWN. (§3.3)
- The Moonsign / Hexerei / Nightsoul Burst material (§1.3, §2.3) rests on S2
  alone; the official announcement page did not return article text to the
  fetcher. UNVERIFIED against an official source. (§1.1)
- Whether S1's 2025-08-13 page stamp means S1's effect wording is stale is an
  inference from the term mismatch in §1.4, not a citation. The live game was
  not read (playtest in progress).
- S2 flags its own co-op section as unverified for cross-map and cross-domain
  cases. (§1.4 item 3)

---

## 6. What this does NOT establish

This file does not establish that Elemental Resonance should exist in this mod,
in public v1, or at all; it proposes no mechanic, no number, no threshold, no
UI, and no scope. It does not rank Resonance against any other workstream — the
charter places it last in the morning read. Section 4 contains questions only
and no recommendation, and none of its 27 entries should be read as implying its
own answer. Section 3 is a NON-FINDING about one pinned mod tree plus three
explicit UNKNOWNs, not a claim that composition passives are unprecedented. The
canon census is a snapshot dated 2026-08-26 of a live-service game whose own
official page and community wiki already disagree (§1.4); nothing here is safe
to quote as current canon without a re-read.

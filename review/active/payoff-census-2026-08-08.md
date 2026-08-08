# The canonical payoff census — rubric + census + candidate bands

**R137 step (2a).** BACKLOG `EB-56`, closed by this packet.
**For [USER] ratification.** Nothing here is ratified, and nothing here aims
anything.

> **Lifecycle: REVIEW.** Two things are asked of the red pen and they are
> asked in order: **(1) ratify the rubric** (§2), because a census over an
> unratified rubric decides nothing — R137's own words — and **(2) read the
> bands** (§5) as the space that R137 step (2c) aims inside.
>
> **What this packet does NOT do, deliberately.** It does not aim any GItS
> archetype high / medium / low; that aim IS the Q-C answer and it is
> [USER]'s (`docs/current/QUEUE.md` row `Q-C`, R137 2c). It states no
> direction and no threshold for Q-A or Q-B. It contains no GItS roster
> number of any kind. It reads canonical CONTENT only — the extracted pools
> under `game_ref/` — and never the sprint's instrument, so the blind
> discipline of R121's steps (3)–(6) is intact and the `DRAFTER_VERSION = 14`
> pin is untouched (R137 contamination statement, honoured as written).

---

## 0. What was measured, and the IP line it stops at

The five base-game pools as extracted to the primary checkout's gitignored
`game_ref/` (extraction leg of `EB-56`, 2026-08-08):

| pool | cards | basic | common | uncommon | rare | ancient | draftable |
|---|---|---|---|---|---|---|---|
| Ironclad | 87 | 3 | 20 | 36 | 26 | 2 | 82 |
| Silent | 88 | 4 | 20 | 36 | 26 | 2 | 82 |
| Defect | 88 | 4 | 20 | 36 | 26 | 2 | 82 |
| Necrobinder | 88 | 4 | 20 | 36 | 26 | 2 | 82 |
| Regent | 88 | 4 | 20 | 36 | 26 | 2 | 82 |

Identical to the counts `docs/role-tempo-baseline.md` §0 already publishes,
which is the join check as much as the header: the two extractions agree card
for card by name in all five pools (the census refuses to run otherwise —
`build()` raises rather than joining across worlds).

**Where the per-card sheet lives, and why not here.** `.gitignore` says the
reason plainly for its neighbour `.sentinel/`: a file whose *content* is
"relic names, rarities, printed numbers" is base-game material and stays a
local artifact even when the tool that writes it is committed (§0.3,
"Extracted / decompiled base-game material is REFERENCE ONLY"). A full
five-pool table of *card × rarity × classification* is that file. So it is
written to **`game_ref/payoff_census.json`** — gitignored, regenerable, never
committed — exactly as `tools/canon_role_tempo.py` already does with
`game_ref/role_tempo_canon.json`, and this packet carries the committed-safe
half: counts, shapes, bands, and the handful of card names the judgment calls
cannot be argued without. That last is the line `docs/reserved-card-names.txt`
and `docs/current/atlas/tier0-pilot-roster.md` already stand on — naming a
base-game card in prose is established; reproducing the pool is not. No card
text and no number off any card face appears anywhere below.

**Regenerate:**

```
python tools/payoff_census.py --game-ref <checkout>/game_ref
python tools/payoff_census.py --game-ref <checkout>/game_ref --strict-p2
```

(A worktree has no `game_ref/` and must never be given one, so the path is an
argument. `--strict-p2` is the one open rubric choice — §2.5.)

---

## 1. The problem the rubric has to solve

Canon **declares no archetypes**. A GItS card carries `archetype:` and
`role: payoff` as authored sheet fields; `tier05/draft.py` just reads them.
Nothing in the five base-game pools carries either. So a canonical payoff
census cannot be a lookup — the classification has to be *derived* from what
the cards structurally do, and the derivation is the thing that needs
ratifying, because a derivation chosen after seeing the answer is not a
census.

Two house precedents constrain it, and the rubric is built on them rather
than beside them:

1. **What an archetype is, structurally.** R90/1c already settled the canon
   stand-in: the **package** — "the subset of a canon pool whose card bodies
   name one mechanic layer, on either side of the mechanic; the card that
   applies Poison and the card that reads the stack are both poison cards"
   (`docs/role-tempo-baseline.md` §5). §2 generalises that from five
   hand-named packages to every layer the pools carry, so no archetype enters
   or leaves by hand.
2. **What a payoff is.** `DRAFTER_VERSION` 10 fixed the fanfare limb of
   `core_complete` by requiring "at least one card that **READS** the meter",
   having found generation coverage and floor coverage are "neither of which
   is a payoff" (`tier0/constants.py`, v10 stamp); v14 applied the same fix to
   the generic limb. **A payoff reads.** The rubric adopts that verbatim
   rather than minting a fresh definition.

The same stamp also records the honest edge: whether enabler-*or*-payoff
machinery counts as "a payoff" is "a definitional question, not a mechanical
one" (v14 stamp, on the spotlight limb). §2 answers it for canon — **no** —
and §6 lists every card that answer moves.

---

## 2. THE RUBRIC (this is the part being ratified)

The rubric is **`tools/payoff_census.py`**, and the section below is a reading
of that file rather than a parallel description of it. Every rule is one named
predicate over fields that came off the decompiled body, so a second
classifier reproduces the census by running the file, not by re-interpreting a
paragraph.

### R0 — Population
The five pools above, whole. **Basic** and **Ancient** cards are classified
and counted but carry no offer weight in §5: neither is in the normal
card-reward stream. Draftable = common + uncommon + rare = 82 per pool.

### R1 — A *layer* is the unit an archetype is made of
A layer is a mechanic token a card's body names. Three sources:
- every `<XPower>` type the body names (`powers`);
- every `<XOrb>` type (`orbs`);
- six **markers** for layers that have no type name of their own and would
  otherwise be invisible: `Osty` (summons), `Stars` (the Forge economy),
  `OrbLayer` (the orb board itself, as distinct from any one orb),
  `Exhaust`, `Discard`, `GeneratedCard`.

### R2 — MENTIONS vs GENERATES, the hinge
- **MENTIONS(c)** = every layer above that the card names, either side.
- **GENERATES(c)** = the *make it bigger* half only: `PowerCmd.Apply<X>`,
  `OrbCmd.Channel<X>` (both taken from `canon_role_tempo.classify_canon`'s own
  `tokens` field, so the two classifiers share one generate-side definition),
  plus each marker's own creation call.

`OrbCmd.Evoke` *touches* the orb layer and **shrinks** it, so it is
deliberately not generation — a rule that read every `OrbCmd.` call as
generation would classify the Defect's cash-in cards as their own enablers.

### R3 — Which layers are *archetypes*
**(a) BREADTH, and breadth is the only admission rule.** A layer is an
archetype of its pool when **≥ 6 cards** of that pool mention it. Below that
it is a card, not a plan. The smallest package R90/1c ratified is 8 cards
(`ironclad_strength`); 6 is one notch more permissive on purpose, so a
real-but-small canon archetype is not erased by the threshold. Sensitivity at
5 / 6 / 8 is reported in §4 rather than asserted away.

> **A first draft of this rubric also required "≥ 1 payoff" to admit a layer,
> and that was wrong twice over.** It would have made every admitted archetype
> carry ≥ 1 payoff *by construction* — the floor of §5's band would then be a
> definition wearing a measurement's clothes — and it silently deleted the
> Necrobinder **summon** layer, whose cards all generate and whose cashers
> read a board state the extraction cannot see. **A zero is a finding here,
> not an exclusion criterion.** The zeros are listed in §5.3.

**(b) IDENTITY vs GENERIC, reported and never enforced.** A layer broad in
**≥ 3 of the 5 pools** is something the *game* does (Exhaust, Vulnerable,
Weak, Strength, GeneratedCard); a layer broad in ≤ 2 is something a
*character is* (Poison, Doom, Orbs, Focus, Stars, Osty). Both are censused.
Bands in §5 are derived over **identity** layers only: a band computed over
Exhaust would be a band about Slay the Spire, not about an archetype.

### R4 — Which cards are *payoffs*
Card `c` is a payoff of layer `L` when `L ∈ MENTIONS(c)` and any of:

- **P1 — reads, does not make (strict).** `L ∉ GENERATES(c)` **and `c`
  generates nothing at all** — so the mention can only be a read.
- **P2 — computed magnitude.** The card's printed number is *absent* because
  it is computed at play time (`CalculationBase` in its vars, i.e. a
  `CalculatedDamageVar`/`CalculatedBlockVar` rather than a literal). A card
  whose own output is a function of combat state is a payoff of that state by
  construction.
- **P3 — consumption.** The card spends the layer's accumulated bodies
  (`OrbCmd.Evoke*`).

**SECOND-HAND MENTION — the deliberate exclusion, and the sharp edge of the
rubric.** A card that names `L`, does not generate `L`, but *does* generate
something else is **not** a payoff. The usual reason a body names a power it
never applies is that it is hover-tipping the power its own power grants
downstream. Counting those as payoffs turns the plainest enablers in canon
into payoffs of their own layer — the summon-form power that grants Strength
every turn would read as a Strength payoff. Every second-hand card is counted
and the class is sized in §6.1.

### R5 — Unresolved payoffs
P2/P3 say *"this number is computed from state"* but not *from which state*.
A P2/P3 card that mentions **no** layer is a payoff of something the
extraction cannot see — a card-**name** subset, a pile size, a board count.
It is counted in a separate row and **never** assigned to an archetype. This
is the census's largest limitation and it is quantified in §6.3, not buried.

### R6 — Rarity
Off the card's own `CardRarity`. Counted; never printed per-card in committed
prose (§0).

### R7 — Census → candidate bands
Two axes, and they answer different questions:
- **SUPPLY** — how many draftable payoff cards the pool prints for the layer.
  The **ceiling** a perfect drafter could reach.
- **OFFER** — `Σ_r RARITY_ODDS[r] × payoffs_at_r / pool_size_at_r`
  (`RARITY_ODDS` quoted from `tier0/constants.py:800`, not re-derived).
  P(one offered card is a payoff of the layer) — the **blind-draft floor**.

**Curtain Call's prediction 4 is a statement about the OFFER axis and not the
supply axis**, which is exactly why it came out counterintuitive: "promoting
payoffs OUT of common cuts their offer frequency, so rarity-shape correction
REDUCED reach". Supply went up and reach went down. Keeping the two axes
separate is the point of the rubric having them.

The band is the **bracket** between them, never a point prediction: a
committed drafter picks on-plan, that selection model is ratified nowhere, and
inventing one here would be the retro-fit the registration's own authority
forbids.

### 2.5 — THE ONE OPEN RUBRIC CHOICE, put to the pen rather than settled
P2/P3 identify a state-reading card but not *which* layer it reads, so the
attribution needs a rule, and exactly two are defensible:

| | rule | what it gets wrong |
|---|---|---|
| **LOOSE** *(shipped default)* | attribute to every layer the card mentions | over-attributes — a card carrying the Exhaust keyword whose magnitude is really computed off HP loss reads as an Exhaust payoff |
| **STRICT** (`--strict-p2`) | attribute only to layers the card does **not** generate, so read and make stay disjoint for P2 as they already are for P1 | under-attributes — a card that channels an orb *and* scales off the orb count stops counting as an orb payoff at all |

Neither is obviously right, and picking one silently would be precisely the
self-serving rubric R137 refuses. **Both are computed. §5 reports both. The
ratification names one.** The good news is in §5.4: the bands barely move.

---

## 3. THE CENSUS — per pool

`ment` = cards mentioning the layer · `gen` = generators · `pay` = payoffs ·
`C/U/R` = payoffs by rarity · `2nd` = second-hand mentions (R4) ·
`reach` = P(one offered card is a payoff). Rows sorted generic first, then by
reach. **LOOSE attribution** (the strict deltas are §5.4).

### Ironclad — 87 cards · 3 archetypes · 3 unresolved-layer payoffs

| archetype | kind | ment | gen | pay | C/U/R | 2nd | reach |
|---|---|---|---|---|---|---|---|
| `Exhaust` | generic | 26 | 24 | 2 | 0/2/0 | 0 | 0.0194 |
| `VulnerablePower` | identity | 13 | 8 | 2 | 0/2/0 | 3 | 0.0194 |
| `StrengthPower` | identity | 8 | 4 | **0** | 0/0/0 | 4 | 0.0000 |

### Silent — 88 cards · 4 archetypes · 6 unresolved-layer payoffs

| archetype | kind | ment | gen | pay | C/U/R | 2nd | reach |
|---|---|---|---|---|---|---|---|
| `Exhaust` | generic | 12 | 11 | 1 | 0/1/0 | 0 | 0.0097 |
| `PoisonPower` | identity | 12 | 6 | 1 | 0/1/0 | 5 | 0.0097 |
| `Discard` | identity | 8 | 8 | **0** | 0/0/0 | 0 | 0.0000 |
| `WeakPower` | identity | 7 | 6 | **0** | 0/0/0 | 1 | 0.0000 |

### Defect — 88 cards · 6 archetypes · 3 unresolved-layer payoffs

| archetype | kind | ment | gen | pay | C/U/R | 2nd | reach |
|---|---|---|---|---|---|---|---|
| `Exhaust` | generic | 18 | 15 | 3 | 0/1/2 | 0 | 0.0136 |
| `GeneratedCard` | generic | 7 | 7 | **0** | 0/0/0 | 0 | 0.0000 |
| `FocusPower` | identity | 6 | 3 | 1 | 0/1/0 | 2 | 0.0097 |
| `OrbLayer` | identity | 29 | 22 | 5 | 0/0/3 | 2 | 0.0058 |
| `LightningOrb` | identity | 9 | 8 | 1 | 0/0/1 | 0 | 0.0019 |
| `FrostOrb` | identity | 7 | 7 | **0** | 0/0/0 | 0 | 0.0000 |

### Necrobinder — 88 cards · 4 archetypes · 8 unresolved-layer payoffs

| archetype | kind | ment | gen | pay | C/U/R | 2nd | reach |
|---|---|---|---|---|---|---|---|
| `Exhaust` | generic | 15 | 14 | 1 | 0/0/1 | 0 | 0.0019 |
| `GeneratedCard` | generic | 7 | 7 | **0** | 0/0/0 | 0 | 0.0000 |
| `DoomPower` | identity | 13 | 5 | 3 | 0/2/1 | 5 | 0.0214 |
| `Osty` | identity | 9 | 9 | **0** | 0/0/0 | 0 | 0.0000 |

### Regent — 88 cards · 4 archetypes · 4 unresolved-layer payoffs

| archetype | kind | ment | gen | pay | C/U/R | 2nd | reach |
|---|---|---|---|---|---|---|---|
| `Exhaust` | generic | 9 | 9 | **0** | 0/0/0 | 0 | 0.0000 |
| `GeneratedCard` | generic | 7 | 7 | **0** | 0/0/0 | 0 | 0.0000 |
| `Stars` | identity | 18 | 17 | 1 | 0/0/1 | 0 | 0.0019 |
| `StrengthPower` | identity | 6 | 1 | **0** | 0/0/0 | 5 | 0.0000 |

### 3.1 Three things worth saying out loud about that table

- **Not one payoff in any pool is COMMON.** Every payoff the census resolves
  is uncommon, rare or ancient, in all five pools, across 21 archetypes. That
  is not a rounding artefact — it is the strongest single regularity in the
  census, and it is the exact shape Curtain Call's prediction 4 ran into from
  the other direction.
- **The generate side is enormous and the read side is thin.** Layers run
  6–29 cards wide and cash out through 0–5 of them. Canon builds meters far
  more than it reads them.
- **`StrengthPower` behaves identically in the two pools that carry it** — 8
  and 6 mentions, 0 resolved payoffs, 4 and 5 second-hand mentions. Two
  independent pools producing the same signature is a property of the
  *rubric*, not of the character, and §6.1 is where that is argued.

---

## 4. Threshold sensitivity (R3(a))

Archetypes admitted per pool, at three settings of the breadth threshold:

| `min_layer` | Ironclad | Silent | Defect | Necrobinder | Regent |
|---|---|---|---|---|---|
| 5 | 3 | 4 | 7 | 4 | 6 |
| **6** *(shipped)* | **3** | **4** | **6** | **4** | **4** |
| 8 | 3 | 3 | 3 | 3 | 2 |

6 is the stable middle: dropping to 5 adds only marginal layers to the two
widest pools; raising to 8 halves Regent. No band in §5 changes sign at any
of the three, because the layers 5 and 8 disagree about all carry zero
resolved payoffs and are outside the band population either way.

---

## 5. THE CANDIDATE BANDS (R137 step 2b)

Derived over **identity archetypes carrying ≥ 1 payoff** — n = 7 under LOOSE,
n = 5 under STRICT. Generic layers excluded (R3(b)); zero-payoff identity
layers are a blind-spot finding (§5.3), not a data point.

### 5.1 The two axes

| | min | p25 | median | p75 | max |
|---|---|---|---|---|---|
| **SUPPLY** — draftable payoff cards | 1 | 1 | 1 | 2 | 3 |
| **OFFER** — P(an offered card is a payoff) | 0.0019 | 0.0058 | 0.0097 | 0.0097 | 0.0214 |
| **OFFER**, as P(a 3-card reward screen shows ≥ 1) | 0.6% | — | 2.9% | — | 6.3% |

### 5.2 The bands

Each band is a **bracket**: blind-draft floor (offer × cards drafted) on the
left, supply ceiling on the right. A committed drafter lives between them.

| band | offer | ceiling | N=15 | N=20 | N=25 |
|---|---|---|---|---|---|
| **LOW** (p25) | 0.0058 | 1 | 0.09 – 1 | 0.12 – 1 | 0.14 – 1 |
| **MEDIUM** (median) | 0.0097 | 1 | 0.15 – 1 | 0.19 – 1 | 0.24 – 1 |
| **HIGH** (p75) | 0.0097 | 2 | 0.15 – 2 | 0.19 – 2 | 0.24 – 2 |
| **TOP** (max) | 0.0214 | 3 | 0.32 – 3 | 0.43 – 3 | 0.53 – 3 |

**Read in one sentence:** a canonical archetype prints **1–3 draftable payoff
cards**, all of them above common, and its offer stream shows one on roughly
**1–6% of 3-card reward screens**.

### 5.3 The zeros — identity layers the census resolves no payoff for

`Ironclad/StrengthPower` · `Silent/Discard` · `Silent/WeakPower` ·
`Defect/FrostOrb` · `Necrobinder/Osty` · `Regent/StrengthPower`
(STRICT adds `Defect/LightningOrb` and `Regent/Stars`.)

These are **blind spots, not zeros**, and `Necrobinder/Osty` is the proof:
nine cards summon, the pool is visibly built around how many bodies are out,
and the cards that cash that count read a board state no field in the
extraction carries. They are excluded from the band population and named here
so the exclusion is visible rather than silent.

### 5.4 LOOSE vs STRICT — the ratification barely moves the answer

| | LOOSE (default) | STRICT (`--strict-p2`) |
|---|---|---|
| identity archetypes in band population | 7 | 5 |
| SUPPLY min / median / max | 1 / 1 / 3 | 1 / 2 / 2 |
| OFFER min / median / max | 0.0019 / 0.0097 / 0.0214 | 0.0039 / 0.0097 / 0.0194 |
| P(3-card screen shows ≥ 1) min / median / max | 0.6% / 2.9% / 6.3% | 1.2% / 2.9% / 5.7% |

The median is **identical** on both axes; the spread narrows because STRICT
drops the two most-attributed cards. **The band survives the open rubric
choice**, which is the one thing that most needed checking before anything is
aimed inside it.

---

## 6. Every judgment call, named

### 6.1 Second-hand mentions — 33 cards, the largest class the rubric excludes

Per pool: Ironclad 7 · Silent 10 · Defect 4 · Necrobinder 7 · Regent 5. The
consequential ones, by layer:

| layer | second-hand cards | the call |
|---|---|---|
| `Silent/PoisonPower` | Noxious Fumes, Envenom, Outbreak, Corrosive Wave, Accelerant | **NOT payoffs.** Each applies its own power and hover-tips Poison downstream. These are the poison archetype's *enablers*; counting them would make the archetype's own engine its own reward. Confident. |
| `Necrobinder/DoomPower` | Countdown, Neurosurge, Oblivion, Reaper Form, Shroud | **NOT payoffs**, same shape as above. Confident. |
| `Ironclad/VulnerablePower` | Colossus, Cruelty, Vicious | **NOT payoffs** — each applies its own power and tips Vulnerable. Confident. |
| `Ironclad/StrengthPower` | Demon Form, Mangle, Rupture, Setup Strike | **NOT payoffs, and this is the least comfortable call in the packet.** Demon Form is canon's archetypal strength *enabler* and P1 would have read it as a strength payoff, which is what forced the strict form of P1 in the first place. But it also means the strength layer resolves to **zero** payoffs in both pools that carry it, and a strength archetype with no reader is not obviously a true statement about the game — see §6.3. **Flagged for the pen.** |
| `Regent/StrengthPower` | 5 cards, same signature | Same call, same discomfort. |

### 6.2 Multi-layer P2 attributions — 4 cards

Mirage (Silent, uncommon → Exhaust + Poison), Synchronize (Defect, uncommon →
Exhaust + Focus + its own power), Voltaic (Defect, rare → Exhaust + Lightning
+ OrbLayer), Time's Up (Necrobinder, rare → Doom + Exhaust). Each has a
computed magnitude and names more than one layer, so LOOSE credits it to all
of them and STRICT credits it to the ones it does not generate. **These four
cards ARE the LOOSE/STRICT delta** — §2.5 and §5.4 are about exactly them.
The Exhaust legs are the weakest: a card that carries the Exhaust keyword and
computes its number off something else entirely still reads as an Exhaust
payoff under LOOSE. Exhaust is generic and excluded from the bands, so the
error is contained; it is stated anyway.

### 6.3 Unresolved-layer payoffs — 24 cards, and the honest headline

Ironclad 3 · Silent 6 · Defect 3 · Necrobinder 8 · Regent 4. Every one has a
computed magnitude (P2) or spends a resource (P3) but names **no** layer the
extraction can see.

**The census resolves 16 payoff cards and leaves 24 unattributed — 60% of the
payoff-shaped cards in the five pools have no archetype in this table.** Both
axes in §5 are therefore **lower bounds**, and the supply ceilings especially
so.

The pattern is legible even though the layer is not: Silent's six cluster
around a generated-token count, Necrobinder's eight around a summoned-body
count, Ironclad's three around card-**name** subsets and pile sizes. None of
those is a field `tools/extract_base_game_pool.py` currently emits — the
`TOKEN_CREATE` regex exists in that file but `parse_card` does not surface it,
and a `CalculatedVar`'s *arguments* (which name the state it reads) are
dropped entirely. Filed as `EB-63`: one extraction change would attribute most
of these and tighten both axes. **The bands in §5 should be read as a floor on
canon's payoff density, not as its measured value**, and if that gap matters
to the aim, `EB-63` lands before step (2c) rather than after.

### 6.4 Two known inherited limitations

- **`HoverTipFactory.FromOrb<X>` counts as generation.** The `tokens` field
  the rubric borrows for its generate side folds hover-tips of orbs in with
  actual channels, so an orb layer can read as generated by a card that only
  points at it. Costs the census orb-side P1 payoffs in the Defect pool and
  nowhere else. Not patched here: changing it would fork the generate-side
  definition the two classifiers currently share, which is worth more than the
  handful of cards. Stated per the standing "the divergence is known" rule
  `docs/role-tempo-baseline.md` §7 already uses for its own classifier split.
- **No magnitude, anywhere.** A payoff that doubles a meter and one that adds
  one damage per stack count the same. Same non-goal, same reason, as
  `docs/role-tempo-baseline.md` §7.

---

## 7. What ratification is being asked for

1. **The rubric (§2)** — RATIFY / AMEND / REJECT, and with it the one open
   choice: **LOOSE or STRICT** P2/P3 attribution (§2.5). §5.4 is the evidence
   that the choice is not load-bearing for the bands.
2. **The exclusion in §6.1** — second-hand mentions are not payoffs. This is
   the v14 stamp's "definitional question, not a mechanical one" answered for
   canon, and the strength layer's double zero is the price. CONFIRM or
   OVERRULE.
3. **Whether `EB-63` gates step (2c)** (§6.3) — the bands are a floor while
   60% of payoff-shaped cards sit unattributed. Aim inside a floor, or resolve
   first.

Then R137 step (2c) — the aim, the direction, the threshold — which is
[USER]'s and appears nowhere in this document.

— `EB-56`, 2026-08-08, branch `overnight-eb56`. Zero design authority
exercised. No measurement was run against the sprint's instrument, and no GItS
roster number was read to produce this document.

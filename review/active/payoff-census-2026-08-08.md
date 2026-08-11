<!--
lifecycle: active
owner: Q-C
exit_when: the rubric is ratified and the aims + predictions are committed
-->
# The canonical payoff census — rubric + census + candidate bands

**R137 step (2a).** BACKLOG `EB-56`, closed by this packet.
**AMENDED 2026-08-10 by [USER]'s ruling.** The census below is the re-issued
one. Nothing here aims anything.

> **What [USER] ruled on 2026-08-10.** Three things, and all three are already
> applied to the numbers in this packet:
>
> 1. **The rubric is AMENDED to carry a token-creation layer.** A character
>    whose plan is to conjure a card that is not in her own pool had no layer
>    at all, so the census could not see one card of that plan. §2 R1 now has
>    the new layer family and §2.6 says what it changed.
> 2. **`EB-63` runs before any aim is taken.** It has run. The extraction now
>    records which card makes which token, and what a computed number counts.
>    §6.3 reports what that bought and what it did not.
> 3. **LOOSE attribution is the ruled rule**, and the §6.1 exclusion of
>    second-hand mentions is CONFIRMED. Both were open questions in the first
>    issue of this packet. They are closed.
>
> **What is still open, and it is the whole of §7.** [USER] ratifies the
> amended rubric TEXT, and then places the aims. The tentative aims are
> written down in §7 so they are on the record; they are **not** the Q-C
> predictions commit.
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

**Regenerate.** Two steps now, and the order matters:

```
python tools/extract_base_game_pool.py --characters Ironclad,Silent,Defect,Necrobinder,Regent
python tools/payoff_census.py --game-ref <checkout>/game_ref
python tools/payoff_census.py --game-ref <checkout>/game_ref --strict-p2
```

The extraction step is new. The amended rubric reads three fields that
`EB-63` added to the extract, so a census run against an older extract would
quietly reproduce the OLD numbers under the NEW rubric's name. The census
refuses to run in that case rather than allow it.

(A worktree has no `game_ref/` and must never be given one, so the path is an
argument. `--strict-p2` is the variant of the attribution rule — §2.5. LOOSE
is now the ruled rule; the variant is kept because §5.4 is the evidence that
the ruling did not move the bands.)

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
A layer is a mechanic token a card's body names. Four sources:
- every `<XPower>` type the body names (`powers`);
- every `<XOrb>` type (`orbs`);
- six **markers** for layers that have no type name of their own and would
  otherwise be invisible: `Osty` (summons), `Stars` (the Forge economy),
  `OrbLayer` (the orb board itself, as distinct from any one orb),
  `Exhaust`, `Discard`, `GeneratedCard`;
- **the token-creation family** (AMENDED 2026-08-10). One layer per token
  card type a pool creates, written `Token:<name>`.

**The token family, in full.** Some characters play a card that is not in
their own pool. The card is conjured during the fight, so it is never
drafted, never offered, and never appears in the pool listing. The first
issue of this packet had no way to see that at all. A whole plan — build the
token, then cash it in — was invisible.

The family is **derived, never listed**. `tools/payoff_census.py` contains no
token name, and it must not: a committed tool may not carry a table of
base-game card names. Instead the census reads each pool's own extract and
opens one layer per token type that pool's cards create. Whatever the five
pools create gets a layer by the same rule, and each layer then faces the
same breadth threshold as every other layer (R3(a), unchanged at 6). Nothing
is special-cased.

The two sides of the new layer, in the same shape as R2 below:

- **MENTIONS the token** — the card makes one, *or* it hover-tips the token's
  card (canon's way of printing "this is about that card" without making
  one), *or* its computed number counts cards carrying the token's own tag.
  That third spelling is the one that finds payoffs, and it is only readable
  because `EB-63` landed first.
- **GENERATES the token** — the card makes one. Naming it is not making it.

**What the family deliberately cannot see, stated because it bounds the
result.** The extraction recognises two creation spellings. A pool that makes
its token some third way therefore shows token *mentions* and no token
*creations*. Admitting such a layer would be the worst available error: with
the generate side blind, every enabler of the layer would read as a payoff of
it — exactly what R4's strict P1 exists to prevent. So the family is keyed on
creation, and a mention-only token is a named blind spot instead of a bad
archetype. One occurs, and §6.5 names it.

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

### 2.5 — THE ATTRIBUTION RULE — **RULED LOOSE, 2026-08-10**
P2/P3 identify a state-reading card but not *which* layer it reads, so the
attribution needs a rule, and exactly two are defensible:

| | rule | what it gets wrong |
|---|---|---|
| **LOOSE** — **RULED** | attribute to every layer the card mentions | over-attributes — a card carrying the Exhaust keyword whose magnitude is really computed off HP loss reads as an Exhaust payoff |
| **STRICT** (`--strict-p2`) | attribute only to layers the card does **not** generate, so read and make stay disjoint for P2 as they already are for P1 | under-attributes — a card that channels an orb *and* scales off the orb count stops counting as an orb payoff at all |

Neither is obviously right, and picking one silently would have been the
self-serving rubric R137 refuses. So both were computed and both were
reported. [USER] ruled **LOOSE** on 2026-08-10. Every number in §3 and §5 is
the LOOSE number; STRICT is still computed and still reported in §5.4,
because that side-by-side is the evidence that the ruling did not decide the
bands.

### 2.6 — What the amendment changed, in one place

The re-run is a small, legible change and nothing about it is subtle.

| | before | after |
|---|---|---|
| archetypes admitted, all five pools | 21 | 22 |
| payoff cards the census attributes | 16 | 17 |
| payoff-shaped cards left unattributed | 24 | **23** |
| identity archetypes in the band population | 7 | 8 |
| second-hand mentions (R4's exclusion) | 33 | 36 |

**One new archetype, in one pool.** The Silent pool admits `Token:Shiv`: 12
cards name the token, 8 of them make one, and exactly **1** card reads the
count. That reader is **Knife Trap**, a rare.

**No other pool gains a layer, and that is the threshold doing its job.** The
other four pools create tokens too — one type in the Ironclad pool, six in
the Defect pool, three in the Regent pool, none in the Necrobinder pool — but
each of those types is named by one or two cards, far under the 6-card
breadth threshold. They are cards, not plans, which is exactly what R3(a)
says. The amendment did not have to be told to ignore them.

**One card left the unattributed list.** Knife Trap was in the 24. It is now
a payoff of a named archetype. The other five Silent cards in that list stay
there, and §6.3 says why — the honest answer is not the one the first issue
of this packet guessed.

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

### Silent — 88 cards · 5 archetypes · 5 unresolved-layer payoffs

| archetype | kind | ment | gen | pay | C/U/R | 2nd | reach |
|---|---|---|---|---|---|---|---|
| `Exhaust` | generic | 12 | 11 | 1 | 0/1/0 | 0 | 0.0097 |
| `PoisonPower` | identity | 12 | 6 | 1 | 0/1/0 | 5 | 0.0097 |
| **`Token:Shiv`** *(new)* | identity | 12 | 8 | 1 | 0/0/1 | 3 | 0.0019 |
| `Discard` | identity | 8 | 8 | **0** | 0/0/0 | 0 | 0.0000 |
| `WeakPower` | identity | 7 | 6 | **0** | 0/0/0 | 1 | 0.0000 |

`Token:Shiv` is the only row the amendment adds anywhere in the census. It is
as broad as the poison layer in the same pool — 12 cards each — and it cashes
out through one rare, which is the same thin shape every other archetype
here has.

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
  is uncommon, rare or ancient, in all five pools, across 22 archetypes. That
  is not a rounding artefact — it is the strongest single regularity in the
  census, and it is the exact shape Curtain Call's prediction 4 ran into from
  the other direction. The new token archetype obeys it too: 8 cards make the
  token, three of them common, and the one card that reads the count is rare.
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
| 5 | 3 | 5 | 7 | 4 | 6 |
| **6** *(shipped)* | **3** | **5** | **6** | **4** | **4** |
| 8 | 3 | 4 | 3 | 3 | 2 |

6 is the stable middle: dropping to 5 adds only marginal layers to the two
widest pools; raising to 8 halves Regent. No band in §5 changes sign at any
of the three, because the layers 5 and 8 disagree about all carry zero
resolved payoffs and are outside the band population either way.

The Silent column is one higher than in the first issue, at all three
settings. That is the new token layer, and the fact that it survives the
strictest setting (8) is worth saying: at 12 mentions it is not a threshold
artefact. It would be an archetype under any threshold this packet
considered.

---

## 5. THE CANDIDATE BANDS (R137 step 2b)

Derived over **identity archetypes carrying ≥ 1 payoff** — n = 8 under the
ruled LOOSE rule, n = 6 under STRICT. Generic layers excluded (R3(b));
zero-payoff identity layers are a blind-spot finding (§5.3), not a data
point.

### 5.1 The two axes

| | min | p25 | median | p75 | max |
|---|---|---|---|---|---|
| **SUPPLY** — draftable payoff cards | 1 | 1 | 1 | 2 | 3 |
| **OFFER** — P(an offered card is a payoff) | 0.0019 | 0.0019 | 0.0097 | 0.0097 | 0.0214 |
| **OFFER**, as P(a 3-card reward screen shows ≥ 1) | 0.6% | — | 2.9% | — | 6.3% |

### 5.2 The bands

Each band is a **bracket**: blind-draft floor (offer × cards drafted) on the
left, supply ceiling on the right. A committed drafter lives between them.

| band | offer | ceiling | N=15 | N=20 | N=25 |
|---|---|---|---|---|---|
| **LOW** (p25) | 0.0019 | 1 | 0.03 – 1 | 0.04 – 1 | 0.05 – 1 |
| **MEDIUM** (median) | 0.0097 | 1 | 0.15 – 1 | 0.19 – 1 | 0.24 – 1 |
| **HIGH** (p75) | 0.0097 | 2 | 0.15 – 2 | 0.19 – 2 | 0.24 – 2 |
| **TOP** (max) | 0.0214 | 3 | 0.32 – 3 | 0.43 – 3 | 0.53 – 3 |

**Read in one sentence:** a canonical archetype prints **1–3 draftable payoff
cards**, all of them above common, and its offer stream shows one on roughly
**0.6–6% of 3-card reward screens**.

### 5.2a What the amendment did to the bands

**Three of the four bands did not move at all.** MEDIUM, HIGH and TOP are
byte-for-byte what they were before the amendment, on both axes.

**LOW moved down.** Its offer figure went from 0.0058 to 0.0019, so the
blind-draft floor of a LOW archetype fell by about two thirds. Its ceiling is
unchanged at 1 card.

**Why it moved is arithmetic, not a discovery.** LOW is the 25th percentile.
The band population went from 7 archetypes to 8, which moves where the
quarter mark falls. The new member's offer figure is 0.0019 — the joint
lowest in the set, because its one payoff is rare and rares are shown least
often. So the bottom quarter of the distribution got heavier. Nothing about
any other archetype changed.

**The practical reading.** The gap between LOW and MEDIUM is now wider than
it was, and LOW is now a genuinely low bar: a blind drafter taking 20 cards
expects 0.04 payoffs of a LOW archetype. That is a statement about how rarely
canon shows you the reader, not about how weak the plan is.

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

| | LOOSE (RULED) | STRICT (`--strict-p2`) |
|---|---|---|
| identity archetypes in band population | 8 | 6 |
| SUPPLY min / median / max | 1 / 1 / 3 | 1 / 1 / 2 |
| OFFER min / median / max | 0.0019 / 0.0097 / 0.0214 | 0.0019 / 0.0097 / 0.0194 |
| P(3-card screen shows ≥ 1) min / median / max | 0.6% / 2.9% / 6.3% | 0.6% / 2.9% / 5.7% |

The median is **identical** on both axes; the spread narrows because STRICT
drops the two most-attributed cards. **The band survives the attribution
rule**, which is the one thing that most needed checking before anything is
aimed inside it — and it is why [USER] could rule LOOSE without the ruling
deciding the answer.

The new token archetype is in the band population under **both** rules. Its
one payoff reads the token count without making a token, so STRICT keeps it
for the same reason LOOSE does. The amendment is not a LOOSE-only effect.

---

## 6. Every judgment call, named

### 6.1 Second-hand mentions — 36 cards, the largest class the rubric excludes

**CONFIRMED by [USER], 2026-08-10: a second-hand mention is not a payoff.**
This was question 2 of the first issue. It is closed, and the strength
layer's double zero (below) is the accepted price.

Per pool: Ironclad 7 · Silent 13 · Defect 4 · Necrobinder 7 · Regent 5. The
consequential ones, by layer:

| layer | second-hand cards | the call |
|---|---|---|
| `Silent/PoisonPower` | Noxious Fumes, Envenom, Outbreak, Corrosive Wave, Accelerant | **NOT payoffs.** Each applies its own power and hover-tips Poison downstream. These are the poison archetype's *enablers*; counting them would make the archetype's own engine its own reward. Confident. |
| `Necrobinder/DoomPower` | Countdown, Neurosurge, Oblivion, Reaper Form, Shroud | **NOT payoffs**, same shape as above. Confident. |
| `Ironclad/VulnerablePower` | Colossus, Cruelty, Vicious | **NOT payoffs** — each applies its own power and tips Vulnerable. Confident. |
| `Ironclad/StrengthPower` | Demon Form, Mangle, Rupture, Setup Strike | **NOT payoffs, and this is the least comfortable call in the packet.** Demon Form is canon's archetypal strength *enabler* and P1 would have read it as a strength payoff, which is what forced the strict form of P1 in the first place. But it also means the strength layer resolves to **zero** payoffs in both pools that carry it, and a strength archetype with no reader is not obviously a true statement about the game — see §6.3. **Flagged for the pen.** |
| `Regent/StrengthPower` | 5 cards, same signature | Same call, same discomfort. |
| `Silent/Token:Shiv` *(new)* | Accuracy, Infinite Blades, Phantom Blades | **NOT payoffs**, and the amendment produced this class rather than being spoiled by it. Each applies its own power and hover-tips the token, and it is that power — not the card — that makes or buffs tokens later. The same shape as the poison row above. Confident. |

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

### 6.3 Unresolved-layer payoffs — 23 cards, and what `EB-63` actually found

Ironclad 3 · Silent 5 · Defect 3 · Necrobinder 8 · Regent 4. Every one has a
computed magnitude (P2) or spends a resource (P3) but names **no** layer the
amended rubric admits.

**The census resolves 17 payoff cards and leaves 23 unattributed — 57% of the
payoff-shaped cards in the five pools still have no archetype in this table.**
Both axes in §5 are therefore still **lower bounds**, and the supply ceilings
especially so.

**`EB-63` has landed, and this is the honest account of it.** The extraction
now records, for every card, which token cards it makes, which it names, and
what each computed number counts. Three results, and the second one is not
what the first issue of this packet predicted.

**(1) It bought exactly one attribution.** Knife Trap, and only Knife Trap.
It left the 24 because its damage counts cards carrying the token's own tag,
which the extract can now see.

**(2) The other five Silent cards are not token payoffs, and the first issue
of this packet was wrong to imply they might be.** The extract now says what
each of them counts, and none of them counts tokens:

| card | what its number actually counts |
|---|---|
| Finisher | attacks played this turn |
| Flechettes | skills in hand |
| Memento Mori | cards discarded this turn |
| Murder | cards drawn this combat |
| Precise Cut | hand size, negated |

They correlate with a token plan — the token is a free attack, so playing
several raises the attack count — but correlation is not what R4 classifies.
**A mechanical rubric that attributed these to the token layer would be
reading the designer's intent off a card name.** They stay unattributed, and
that is the rubric working.

**(3) What it did buy is a map of the remaining 23.** Sixteen of them now
name the state they read. The states cluster into four families that the
amended rubric has no layer for:

| family | cards | example of what is counted |
|---|---|---|
| combat-history events | 9 | cards drawn, cards discarded, damage taken, energy spent, stars modified |
| a pile or a card type | 4 | skills in hand, hand size, attacks played |
| a card **tag** | 2 | cards carrying a named tag |
| a card **class** | 1 | cards of one type sitting in the exhaust pile |

The remaining **7** name nothing the extraction can reach: their number comes
off a property path — the player's own block, the orb queue's length, a
summoned body's current or maximum HP — with no tag, type or pile name in it.

**This is now a rubric question and no longer an extraction one.** Attributing
those 16 would mean opening three more layer families (history events, piles,
tags). That is a much bigger amendment than the token layer, it is [USER]'s
call and not this packet's, and it is asked in §7.

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

### 6.5 The one token layer the amendment deliberately does not open

The Necrobinder pool names a token card in **ten** of its cards — well over
the breadth threshold — and the census opens no layer for it. This is the
blind spot §2 R1 warned about, and it has exactly one instance.

**Why.** The extraction recognises two spellings of "make a token". That pool
uses a third. So the extract sees ten cards naming the token and **zero**
cards making it.

**Why that is a refusal and not an oversight.** With the generate side blind,
every card of the layer would look like a card that reads without making —
which is R4's P1, the payoff test. The census would report a ten-card
archetype in which nearly every card is a payoff. That is the single most
wrong answer available, and it is the failure that made P1 strict in the
first place (§6.1, the strength row). A named blind spot is better than a
confident wrong archetype.

**What it would take.** Teaching the extraction the third creation spelling.
It is a small change and it is **not** made here, because widening a shared
regex changes what the other tools that use it see, and this packet's job was
the ruling, not a second unruled amendment. It is [USER]'s call in §7.

**What is being given up is not nothing.** The extract now shows that this
pool prints a *reader* of that token too: one rare counts token cards sitting
in the exhaust pile. So the layer would very likely have a payoff, not a
zero, if the creation side were visible. That is the strongest single reason
to make the small extraction change — and the strongest reason not to guess
at it in the same pass that carried a ruling.

**One related fact, since it is now visible.** Four Necrobinder cards compute
their number off the summoned body: three read its current or maximum HP, one
counts cards carrying its tag. That is the `Necrobinder/Osty` zero in §5.3.
The extract can now see that those readers exist. The rubric still cannot
attribute them, for the same reason as the rest of §6.3 — the state three of
them read is a property path, not a layer this rubric has.

---

## 7. What is still asked of [USER]

Three of the first issue's questions are answered. LOOSE is ruled, §6.1 is
confirmed, and `EB-63` has run before any aim. Two things remain, and they
are in order.

### 7.1 Ratify the amended rubric TEXT

§2 is the rubric, and §2's R1 is now longer than it was. What is being
ratified is the wording of the token-creation family: that a layer is opened
per token type a pool **creates**, that naming a token is a mention and not a
generation, and that a token whose creation the extraction cannot see gets a
named blind spot instead of an archetype (§6.5).

RATIFY / AMEND / REJECT. One sub-question rides along, and it is small:

- **Should the extraction learn the third creation spelling (§6.5)?** Yes
  opens a ten-card layer in the Necrobinder pool, probably with a payoff, and
  probably widens the band population by one. No leaves a named blind spot.
  Either answer is defensible; neither changes any band that exists today.

### 7.2 Place the aims — R137 step (2c)

This is the Q-C answer. It is [USER]'s, it has never been in this packet, and
it is not in this packet now.

The bands in §5 are the space. There are four of them — LOW, MEDIUM, HIGH,
TOP — and each is a bracket, not a number.

**Tentative aims, recorded so they are on the record.** These are what [USER]
has said out loud so far. They are **TENTATIVE**. Writing them here is not
the Q-C predictions commit, does not register anything, and does not bind
anything:

| character | archetype | tentative band |
|---|---|---|
| Klee | Demolition | MEDIUM |
| Klee | Reaction | HIGH |
| Klee | Spark | LOW |
| Furina | Salon | MEDIUM |
| Furina | Spotlight | HIGH |
| Furina | Fanfare | LOW |
| Kokomi | Priest | MEDIUM |
| Kokomi | Commander | HIGH |
| Kokomi | Assist | LOW |

**One thing to know before they are made final.** LOW moved at the amendment
and the other three bands did not (§5.2a). LOW's blind-draft floor is now
0.04 payoffs over a 20-card draft. Three of the nine aims above are LOW, so
that is the band the amendment touched hardest, and it is the one worth a
second look before the aims are committed.

**And the standing caveat.** Both axes remain lower bounds while 23
payoff-shaped cards sit unattributed (§6.3). The bands are a floor on canon's
payoff density, not its measured value. That was true at the first issue and
it is still true; `EB-63` narrowed it by one card and mapped the rest.

— `EB-56`, first issued 2026-08-08; AMENDED and re-issued 2026-08-10 per
[USER]'s ruling, branch `sitting-prep-2026-08-08`. Zero design authority
exercised. No measurement was run against the sprint's instrument, and no
GItS roster number was read to produce this document.

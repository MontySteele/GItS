# Companion cards — the opening design packet

**Drafted 2026-08-30, and RULED the same day — see §5, R234.** §1 to §4 are the
evidence the packet was drafted on and are unchanged by the ruling. §6 keeps the
pick bodies exactly as they were put to [USER], each now carrying a one-line
answer, because a ruling is only readable against the options it chose between.

Still true of this file after the ruling: **no shipped number moves, no card
sheet is edited, no code is written, and no register row is minted here.** The
picks are numbered P1 to P9, plus one sub-pick P5a, **inside this document
only** — those labels are local handles for a conversation, not identifiers, and
they do not reserve or consume anything in any register. The engineering the
ruling creates is named as owed in §5.3 and its rows mint on the
register-reconcile branch, not from this packet.

Written 2026-08-30 on branch `companion-slice-1`, based on main `4c50cbf1`.

---

## 1. The intent, and what follows from it

### 1.1 [USER]'s written intent, verbatim (2026-08-30)

These four answers are the design authority for everything below. Where this
packet and these sentences disagree, these sentences win.

> **1.** "I think we go one nation at a time to prove the concept, then work
> outward."

> **2.** Shapes are **"per-nation"** — each nation's companion pool has its own
> shape identity, rather than one global grammar.

> **3.** "Companion cards are supposed to take two flavors - Personal Companions
> (like Prune for Klee) which are a subset of a character's draftable pool and
> can directly interact with their unique mechanics and engine, and the rest,
> which are designed as a replacement for the native StS2 colorless pool - the
> cards belonging to a character's home nation (which the pool is weighted to
> show more often) should be balanced around them, but the rest should be
> balanced globally; thus, Personal Companions should interact with the engine
> and kit of a character, while the universal Companions should not so that they
> aren't a brick in someone else's deck."

> **4.** "Personal Companion cards should match the power level of others in
> that character's deck at equivalent rarity; otherwise they follow the
> following convention: Common cards are largely 'reaction fodder' or niche
> picks that might be exploitable if they plug a kit gap (like a bad Exhaust
> card in a deck with no other exhaust); Uncommon and Rare cards can be slightly
> better than native cards of equal rarity as they are intended to be unlikely
> finds, just like native StS2 Colorless cards."

### 1.2 The derived contract

One sentence follows from answer 3 and is the spine of this whole packet:

> **Personal Companions print engine interactions on their faces. Universal
> Companions never do — the engines reach out to them instead.**

That is not a new invention. It is the direction the codebase has already been
moving, in three independent places, all of which were verified in the repo
before this packet was written.

**Klee.** Prune used to grant Sparks off her own face — one `gain_spark` at top
level and a second inside a `reaction_triggered_by_this` conditional. Both ops
are gone from the sheet, and the grant now lives in Klee's own kit as a declared
engine response. The declaration is
`tier0/constants.py:201-204` (`KLEE_COMPANION_SPARK_BASE` /
`_REACTION_BONUS` / `_UPGRADED_BONUS` / `_MAX_PER_PLAY` = 1 / 1 / 1 / 3); the
engine site is `tier0/engine/effects.py:920-969`
(`klee_personal_companion_spark`), called from
`tier0/engine/combat.py:626`; the C# twin is
`klee-mod/KleeCode/Powers/KleeCompanionSpark.cs`. Prune's own face now says so
in a comment (`docs/mondstadt-companions.yaml:109-126`), and
`docs/current/STATE.md:26` records the move at `CONSTANTS_VERSION` 21. The
engine function even scopes itself to the character who declared it: a Personal
Companion that reached another character's deck mints nothing
(`effects.py:952-957`).

**Kokomi.** Her kit reaches out to Companions rather than the other way round.
Charge accrues at one per Exhaust of one of her own cards, **Companions
included**, declared in LAW itself
(`docs/current/LAW.md:237-241`) rather than printed on any Companion face; the
tests pin it for an ordinary Companion and for a Mustered one
(`tier0/tests/test_kurage_memory.py:540-553`). The Bake-Kurage's memory,
symmetrically, holds one of her own **non-Companion** cards — "every
Companion-only reading of the memory is wrong"
(`docs/current/LAW.md:251-252`). One correction worth stating plainly, because
this packet was commissioned with a slightly stronger claim: **there is no
shipped Kurage-memory discount on Mustered Companions.** R216 D deferred that
subsidy rather than settling it, and it lives today only as a quarantined
prototype on the R213 surface
(`tier0/tests/test_eb183_muster_subsidy_funnel.py:1-28`,
`review/active/eb183-muster-funnel-2026-08-30.md`). The shipped fact is the
Charge funnel, which is still an engine reaching outward, and is enough for the
contract.

**Furina.** Under the reframe, a Companion play triggers one Salon member — the
mechanism is a hook on Companion play, fired as the pair `salon_perform` then
`salon_rotate`, and it is expressly "fired by a hook on Companion play rather
than by a card"
(`review/active/furina-reframe-2026-08-29.md:884-889`, §4.3). Nothing is printed
on any Companion. `docs/current/STATE.md:617-625` records the slice as built in
the sim behind five flags that all ship OFF.

So the contract already describes the code. What this packet adds is naming it,
stating what it forbids, and asking where the pool goes next.

### 1.3 Where the contract already exists in LAW, and where it does not

The clause everyone cites as **LAW:145** is *not* the text at line 145 of
`docs/current/LAW.md` today. Line 145 currently reads:

> "**Burst-meter (`burst_energy`) generation stays character-kit-scoped** and
> must never be cheaply repeatable from companions."
> (`docs/current/LAW.md:143-146`)

The tightened rewrite — the sentence the Prune work, the constants block and the
C# power all quote — is **countersigned but PROSPECTIVE** under R213, and no
`LAW.md` line has moved:

> "**Companion cards may not themselves grant signature resources. A
> character-owned engine may respond to a Companion play and generate its
> resource where that character's kit explicitly declares the trigger and bounds
> the amount generated per Companion play.**"
> (`review/active/burst-retirement-2026-08-29.md:335-340`, countersigned R224 at
> `:371-374`; `docs/current/STATE.md:609-613` and `:863-869` record the
> prospective standing.)

This matters to the packet in a practical way. **The derived contract is already
half-written in LAW, prospectively, and this slice should be designed to land
inside it rather than beside it.** It also means one word in the countersigned
clause is deliberately absent — "only" — precisely so that Kokomi's engine-level
Exhaust-to-Charge, declared in LAW rather than on her sheet, stays legal
(`burst-retirement-2026-08-29.md:342-345`). The Universal side of the contract
must not accidentally re-introduce that "only".

---

## 2. What exists today

### 2.1 The three pools, counted

Counted directly from the sheets:

| Nation | Rows | Common | Uncommon | Rare | Draftable rows | Personal-pool rows | Guest-star rows |
|---|---|---|---|---|---|---|---|
| Mondstadt (Klee) | 17 | 6 | 8 | 3 | 17 | **1** (`prune_witch_hunt`) | 0 |
| Fontaine (Furina) | 19 | 10 | 5 | 4 | 16 | 0 | **3** (Neuvillette cameos) |
| Inazuma (Kokomi) | 15 | 8 | 5 | 2 | 15 | 0 | 0 |
| **Total** | **51** | **24** | **18** | **9** | **48** | **1** | **3** |

The 51 matches the EB-148 audit's independent count
(`review/active/eb148-companion-audit-2026-08-27.md:16-19`: 17 Mondstadt, 19
Fontaine including 3 cameos, 15 Inazuma).

**The headline: under the new taxonomy, exactly one draftable card in fifty-one
is a Personal Companion.** Prune, flagged `personal_pool: klee`
(`docs/mondstadt-companions.yaml:102`). The three Neuvillette cameos are
Furina-personal but are `guest_star: true` — generated mid-combat, never
drafted, never banner-governed
(`docs/fontaine-companions.yaml:206-226`; LAW at
`docs/current/LAW.md:104-120`). Everything else is Universal by default, because
nothing ever asked it to be anything.

### 2.2 Which Universal cards violate the contract

Reading every effect list for a printed signature resource, the violations are
narrow and they are all in one nation and one family: **`burst_energy` printed
on a Universal Mondstadt face.**

- `barbara_melody` — `{op: burst_energy, amount: 4}` (`docs/mondstadt-companions.yaml:31`)
- `sucrose_astable` — `{op: burst_energy, amount: 8}` (`:49`)
- `bennett_passion` — `{op: burst_energy, amount: 5}` (`:70`)
- `durin_witchs_flame` — the power's note grants "3 Burst Energy" per consumed
  aura (`:86`)

Three of the four are 4-star commons or uncommons, and one (`sucrose_astable`)
carries an Exhaust guard whose retained purpose is written on the card
(`:50-57`). Durin's feed is already ruled: the burst-retirement packet marks
`WITCHS_FLAME_BURST` **RETIRE**, on the reasoning that "Durin is a companion,
and LAW:145 ... says signature-resource generation stays kit-scoped and never
cheaply repeatable from companions"
(`review/active/burst-retirement-2026-08-29.md:638`), and R224 ruled the retire
holds "under either LAW:145 reading" (`:647-648`). The other three have not been
dispositioned.

Two cards look like violations and are not, and it is worth saying why, because
they are the model the Universal flavor should copy:

- **`sara_tengu_stormcall`** grants plain `strength 2`. In Kokomi's hands that
  Strength converts to 2 Charge — but at *her* `apply_power` chokepoint, not on
  the card. The sheet says so explicitly: "the conversion is the design, not a
  leak; any other drafter keeps the Strength"
  (`docs/inazuma-companions.yaml:82-86`).
- **`arlecchino_masque_red_death`** pays Strength and a Bond of Life, and the
  same chokepoint pays Kokomi in Charge instead — "deliberately NOT
  special-cased: routing through the standard chokepoint is what makes that fall
  out on its own" (`docs/fontaine-companions.yaml:169-173`).

That is the contract working: a globally-legible card, and a kit that reaches
out to it.

One card is a genuine borderline and needs a ruling rather than a verdict.
**`navia_cannon_fire_support`** triggers on "whenever you play a Companion card,
gain 3 Block" (`docs/fontaine-companions.yaml:98-101`). It touches no
character's engine, so it is not a contract violation as written. But it is a
Universal card whose whole payoff is *the Companion pool itself*, which makes
its power level a function of how many Companions the deck holds — and it is the
exact loop the playtest complained about
(`review/active/eb148-companion-audit-2026-08-27.md:40-47`, which classes it a
"subsidy engine" alongside Albedo's Solar Isotoma). **It is the only card in the
pool of this kind:** Albedo shares the audit's subsidy-engine label but triggers
on attacking an aura-bearing enemy, which is element synergy rather than
Companion density — P6 separates them and explains why.

### 2.3 The defence audit, which is the same problem seen from another angle

EB-148 read all 51 cards and found: 30 grant no defence; 14 buy defence
outright; **7 get defence as a free rider on a card bought for something else**,
and of those seven, **five carry no price at all**
(`eb148-companion-audit-2026-08-27.md:20-28`). Per nation, the share of cards
granting Block is 41% Mondstadt, 26% Fontaine, **60% Inazuma** (`:32-38`).
Exactly one card in the whole set — Prune — makes the Block and the engine
payoff mutually exclusive (`:26-28`).

This is a Universal-flavor problem in taxonomy terms. A card that hands out
unpriced Block is never a brick in anyone's deck — which is the goal — but it is
also never a decision, which is the complaint. §3 states the test that separates
those two.

### 2.4 The colorless-pool reference — **NOT VERIFIABLE FROM THIS REPO**

The task asked for the native StS2 colorless pool's size, rarity split and power
conventions, read out of `game_ref/`. **That data is not in `game_ref/`.** The
tree (read read-only from the main checkout at
`C:\Users\Monty\Documents\GitHub\GItS\game_ref\`) is flat, 29 files, and holds
only Ironclad, Silent, Defect, Regent and Necrobinder character material plus
`role_tempo_canon.json`. A case-insensitive grep for "colorless" across the
whole tree returns nothing.

What the repo *does* have, and what this packet is therefore limited to:

- **The two completed official character anchors** — Ironclad 76 cards, Silent
  87 (`docs/current/STATE.md:99-101`). These are character pools, not the
  colorless pool, and they anchor distinctness and power, not colorless
  convention.
- **The extractor that would produce it**, `tools/extract_base_game_pool.py`,
  which `card_distinctness_report.py --gate` already wants run first and which
  is why that gate stands red in the local-only lane
  (`docs/current/OPERATIONS.md:164-170`).
- **One prose datum** that is the closest thing to a stated colorless
  convention in HEAD: watchlist `W5` keeps `lynette_box_trick` at its rarity
  because "as a companion card it is close to *what if I high-roll a colorless
  option*" (`docs/current/STATE.md:893-895`). That is a taste anchor, not a
  number.

**So this packet does not quote a colorless size or rarity split, and no design
below is priced against one.** P8 asks whether producing that reference is part
of this slice.

### 2.5 Home-nation weighting: implemented, not aspirational

It is real, and it is one constant.

```
SAME_NATION_REWARD_SHARE = 0.5
NATION_WEIGHTS = {"mondstadt": 1.0, "fontaine": 1.0, "inazuma": 1.0}
```
(`tier0/constants.py:1420-1421`, with the mechanism described at `:1413-1419`.)

Half the companion reward slot's weight concentrates on the run character's own
nation; the remainder spreads across all nations at equal relative weight. The
comment records the property that makes it safe: "a single-nation world reduces
exactly to the old uniform pick", so no archived pre-Fontaine number moved when
the mechanism landed. The mod side keys off the same idea — every generated
companion card carries a `Nation` whose docstring says "Nation drives
`SAME_NATION_REWARD_SHARE` weighting"
(e.g. `klee-mod/KleeCode/Cards/Generated/AlbedoSolarIsotoma.cs:37`).

The shop is the other channel and works differently: two colorless slots, both
Uncommon-or-higher, slot 1 home-region and slot 2 wildcard-nation, with "the
nation filter the only difference between the slots"
(`docs/current/LAW.md:122-128`). Companions are exempt from the ×1.15 colorless
surcharge (`:134-136`). And the governor is explicitly not price alone — price,
shelf composition and shelf order jointly govern
(`docs/current/LAW.md:137-142`, [USER] 2026-08-10 / S4-G10), which amended the
older "price is the governor" thesis rather than replacing it.

So answer 3's parenthetical — "which the pool is weighted to show more often" —
is already true in code, at 50%. **Nothing in this slice needs to build it. What
it may need is to decide whether 50% is the right number once the Universal /
home-nation balance split has real content behind it** (P7).

### 2.6 The distinctness floor, and a lint gap

`tools/card_distinctness_report.py` sets `GATE_MIN_POOL = 30` (`:263`) and skips
any pool under it, printing what it skipped (`:409`, `:506`). Its own docstring
says the exemption applies to "pools of 30+ cards (companion sheets exempt by
size)" (`:168`).

All three companion pools are exempt today: 17, 19, 15. **A pool that reaches 30
stops being exempt, and the gate that has never evaluated a companion sheet
starts evaluating it.** The tool's own history is the warning — the exemption
"swallowed OFFICIAL:silent whole while she was under 30", and for two days the
anchor added to ratify the gate was never evaluated by it (`:168-170`).

**A separate defect, found while verifying the above and not fixed here. It is
two-fold, and the second half only becomes visible once the taxonomy in §3
exists.**

*(a) Input coverage.* The tool's `SHEETS` list globs `docs/*-cards.yaml` and
then appends **`mondstadt-companions.yaml` only**
(`tools/card_distinctness_report.py:195-198`). Fontaine's and Inazuma's
companion sheets are not in the instrument's input at all — not exempt-by-size,
but absent.

*(b) No taxonomy filter.* If the missing sheets were simply added today, the
instrument would count **Personal and guest-star rows inside a pool metric that
should be measuring the draftable Universal pool.** Fontaine is the case that
proves it: three of its nineteen rows are `guest_star` cameos that no player can
draft (§2.1), and under §3.1 a Personal Companion is balanced against its
owner's character sheet rather than against the companion pool — so neither kind
belongs in a distinctness reading of the Universal pool. Fixing (a) without (b)
would produce numbers that look like coverage and are not.

Under the current sizes neither half changes anything, since all three pools are
under 30 and exempt. Both would bite the moment a pool grew (P4). This is
engineering debt rather than a design question: it becomes a row on the
register-reconcile branch **after tonight's runs land**, and it is deliberately
**not** filed by this packet, which mints nothing.

---

## 3. The taxonomy, written as the law it wants to become

Nothing in this section is countersigned. It is drafted in the shape LAW would
take, so that a ruling can adopt or amend sentences rather than paragraphs.

### 3.1 The two flavors

**A Personal Companion** is a Companion card flagged to exactly one character's
pool. It is a subset of that character's draftable pool, it is drafted normally
(rewards, shop, a possible randomized starter), and **it may print interactions
with that character's unique mechanics and engine on its own face.** It is
balanced against the other cards in *that character's* deck at equal rarity.
This is the existing personal-pool clause
(`docs/current/LAW.md:104-120`) with answer 3's face-printing permission made
explicit.

**A Universal Companion** is every other Companion card. It is the mod's
replacement for the native StS2 colorless pool. **It never prints a named
character's engine, resource, or kit vocabulary on its face.** A character's own
kit may reach out and respond to it — that is the prospective LAW:145 clause,
and the response is declared and bounded on the character's side, never the
card's. A Universal Companion belonging to a character's home nation is balanced
*around* that character; the rest is balanced globally.

**The brick test, which is the whole point of the split.** A Universal Companion
must be a card any current or future character can draft without it being dead.
Answer 3 names the failure mode — "so that they aren't a brick in someone else's
deck" — and the existing pool already states the same instinct twice
independently: Chevreuse's Valor was generalized to *any* reaction because it
"must never be a dead draw in an off-Pyro/Electro deck"
(`docs/fontaine-companions.yaml:16`), and Sucrose's Catalyst Conversion exists
because "the pool must cover gaps for any character present or future, so 'a
current character self-provides energy' was the wrong test"
(`docs/mondstadt-companions.yaml:60-65`).

### 3.2 Answer 4, restated as things you can test

Answer 4 gives three balance statements. Each is written below as a test, so
that a card either passes or does not.

**Personal Companions — "match the power level of others in that character's
deck at equivalent rarity."** *Test:* place the card in that character's own
sheet at its rarity and ask whether it would be an unremarkable member of that
band. This is a comparison against one sheet, not against the companion pools,
and it is the only balance statement in answer 4 that points at a character's
own cards. It is also the statement that the existing personal-pool LAW clause
already carries as "power tracks rarity" plus the exemption from
enabler-not-carry (`docs/current/LAW.md:104-113`), so no new law is needed for
it — only the naming.

**Universal Commons — "reaction fodder or niche picks that might be exploitable
if they plug a kit gap."** *Test, in two halves, and a card must pass at least
one:*
1. **Reaction fodder.** The card's honest use is to put an element on the board
   or to eat one, and its body would be unremarkable stripped of that. Most of
   the existing commons already read this way — `dahlia_sacramental_shower`,
   `fischl_nightrider`, `kaeya_frostgnaw`, `freminet_pers_deploy`,
   `chevreuse_interdiction_fire` are all "small damage, applies an element".
2. **Kit-gap plug.** The card is weak in the average deck and specifically good
   in a deck missing one thing — [USER]'s own example is a bad Exhaust card in a
   deck with no other Exhaust. The pool has exactly one card authored on this
   logic today (`sucrose_catalyst_conversion`, the neutral energy fixer,
   `docs/mondstadt-companions.yaml:58-68`).

The half that is *not* a licence: a common that is simply strong in every deck
fails both halves. That is the strongest reading of "niche".

**Universal Uncommons and Rares — "slightly better than native cards of equal
rarity as they are intended to be unlikely finds."** *Test:* a Universal
Uncommon or Rare may sit above the equivalent-rarity band of a character sheet,
by a margin justified by its access rate and nothing else. The existing pool
already prices Rares this way in [USER]'s own words on Raiden — "Rares in
general tend to be undertuned, so I think this is fine for a front-loaded rare"
(`docs/inazuma-companions.yaml:103-106`) — and `W5` keeps Lynette's draw common
where it is on the "high-roll a colorless option" reading
(`docs/current/STATE.md:893-895`).

**What "slightly better" cannot be measured against today.** See §2.4: the
native colorless reference does not exist in this repo. Until it does, "slightly
better than native cards of equal rarity" has to be read against the character
sheets, which are a different band by construction. **P8 is the pick that
settles whether this slice produces the missing anchor or proceeds without it.**
This packet does not assign a number to "slightly", and any number offered
before the anchor exists would be taste dressed as measurement.

### 3.3 What the 30-card floor implies per pool

If each nation's pool is meant to eventually stand on its own as a shape family
(answer 2), then 30 is the number at which the distinctness instrument starts
having an opinion about it. Today all three are exempt (17 / 19 / 15).

Two readings, and they are a genuine fork rather than a fact (P4):

- **30 is a target.** Crossing it means the pool is dense enough that the
  instrument can tell you whether its cards are distinguishable from one
  another — which is exactly the question "does this nation have a shape
  identity" is asking. Under this reading the floor is the slice's success
  condition.
- **30 is a hazard.** Crossing it turns a green gate red without any card having
  got worse, and the instrument's own record is that pools measured under 30
  were measuring the extractor, not the pool
  (`card_distinctness_report.py:163-167`). Under this reading the pool should be
  grown deliberately and past 30 in one step, with the gate's baseline re-taken,
  rather than drifting across the line mid-slice.

---

## 4. Per-nation shape identity

Answer 2 says shapes are per-nation. Here is what each nation's existing cards
plus its character's engine already suggest. These are readings of shipped
content, not proposals.

### 4.1 Mondstadt (Klee) — *element delivery, and the fixers*

The existing 17 lean hard on plain elemental appliers at one energy — Dahlia,
Fischl, Kaeya, Diona all read "small body, applies an element". Anemo (Sucrose,
and Prune) is the pool's Swirl engine. Its distinctive contributions are the two
**fixers**: `sucrose_catalyst_conversion`, the neutral energy/draw patch
authored explicitly for any character present or future
(`docs/mondstadt-companions.yaml:58-68`), and `sucrose_gust`, the free
self-replacing Swirl that had to be bumped to Uncommon under the cycling-engine
clause (`:41-47`). Its three Rares are all Powers.

Klee's engine reaches out to it in the cleanest way in the game: a Personal
Companion play mints Sparks through her kit, bounded per play
(§1.2). **Mondstadt's shape family reads: apply an element, or fix a gap.**

### 4.2 Fontaine (Furina) — *the reaction economy, deliberately incomplete*

Fontaine is the most consciously *composed* pool. Its header states convergence
levers by construction: exactly one Cryo-applying card each for Charlotte and
Freminet, Chevreuse authored as the Overload/Vaporize counterweight, and **no
Fontaine Electro at all** — "Furina's Electro-Charged scarcity is BY
CONSTRUCTION — do not 'fix'" (`docs/fontaine-companions.yaml:5-7`). Freminet is
a three-card mini-engine that must produce its own Shatter (`:56-71`). It is the
only pool with a full Rare set (four), and it is the set that turned the
Featured Banner on (`:73-79`).

Furina's engine reaches out via the Companion-play → member-performs hook
(§1.2). **Fontaine's shape family reads: a managed reaction economy, where what
is absent is as designed as what is present.**

### 4.3 Inazuma (Kokomi) — *the muster, and the Block problem* — **PENDING WF**

Inazuma's cards are the most defensive in the game: 60% grant Block, the highest
of the three (`eb148-companion-audit-2026-08-27.md:32-38`). Its lore framing is
the peace answering a call, and its display family is Muster / Enlist / Rally
with the exhaust voice as ROTATION, never sacrifice
(`docs/inazuma-companions.yaml:18-25`). Kokomi's kit reaches out by paying
Charge on any Companion Exhaust (§1.2), which makes Companion density itself an
income stream.

**Everything about Inazuma's shape identity in this packet is pending
`KOKOMI-SLICE1-WF`, which is running tonight.** That read is precisely about
these shapes: six of slice 1's seven arms ADVANCED across four rounds, and the
arms are the exclusive-modes ("choose one: damage | Block") and cost-line-price
("the shipped effects to the digit, and one more energy") re-authorings of three
Inazuma Companions — Shinobu, Thoma and Itto
(`review/active/kokomi-slice-1-2026-08-27.md:66-92`; tally at `:780-782`;
registration and R227 countersign at `:791-812`). The registration exists
because those six ADVANCE results currently feed *nothing registered*, and the
accept-to-sheet step is a one-way door (`:815-825`). The slice packet records
`EB-184` as preceding the Itto exclusive-mode arm (`:806-810`), but **that block
is gone: `EB-184` CLOSED on 2026-08-30 on its live replay**
(`docs/current/STATE.md:345-347`, `:726`), in the wave merge that is this
branch's own base commit, and BACKLOG no longer carries the row. All arms are
unblocked. **The read itself is still ungraded.**

**So: whether Inazuma's shape family is "priced defence" or "exclusive-mode
defence" — or neither — is not a question this packet answers. It is the
question tonight's read is asking.** Every design sentence in this packet that
would depend on that answer is marked pending-WF, and P2's Inazuma option is
argued on the evidence's timing rather than on a shape conclusion.

---

## 5. The ruling — R234 (2026-08-30)

**Provenance.** A GPT review relayed by [USER] on 2026-08-30, plus this session's
verified fact-check of it, plus [USER]'s own convergence with both. Signed under
the standing both-agreed authorization. Every pick below is answered; the pick
bodies in §6 are left exactly as drafted so that each answer can be read against
the options it chose between.

### 5.1 The answers

**P1 — which nation first. MONDSTADT.** [USER] directly. The first slice is
Mondstadt's, and the arguments made against it in §6 are the risks that slice
now carries rather than reasons to revisit.

**P2 — what slice 1 delivers. THE TAXONOMY PLUS TWO NEW KLEE PERSONAL CARDS** —
three in total with Prune. **No Universal expansion in slice 1.** This is the
drafted option B, sized: it proves the half of the concept that is new, because
Personal Companions are currently n=1, and it deliberately leaves the
colorless-replacement half alone until the anchor P8 orders exists.

**P3 — the three undispositioned `burst_energy` faces. RESOLVED INSIDE THE
SHARED BURST-RETIREMENT FOLD.** Barbara, Sucrose's Astable and Bennett's Passion
are either rewritten as generic Universal effects or their riders retired, and
that work happens **in the fold, not in this slice**. Three things are ruled out
by name: **no grandfathering**, so the drafted option B is rejected; **none of
the three becomes a Klee-specific hook**, so the Prune manoeuvre is not the
template here — these are Universal cards and they stay Universal; and none is
re-authored as its own errand ahead of the fold. Durin's feed is already ruled
RETIRE in that same fold, so all four now travel together.

**P4 — the 30-card floor. DECOUPLE.** It is an instrument threshold, not a
content target. Pool size is set by what a nation's shape family needs. The
drafted option C.

**P5 — how many Personal Companions per character. A LONG-TERM RANGE OF THREE TO
FIVE, STARTING AT THREE.** The drafted option B, with the entry point named.

**P5a — the Rare Personal tier. DEFERRED, and the sub-pick STAYS OPEN.** None of
options (a) through (d) is taken. The open sub-pick **gates any Rare Personal
design**: no Rare Personal Companion may be authored until it is answered, and
**slice 1 promises none** — its three Klee Personals sit at 4-star, where the
acquisition chain in §6 shows the channels already work. This is the one place
the ruling deliberately leaves a fork standing, and it is left standing because
authoring an unreachable card is the outcome all four options exist to prevent.

**P6 — density payoff. SPLIT, AS AMENDED, AND RULED PER CARD.**
**Navia takes option C — Universal, but bounded or costed.** **Albedo returns to
ordinary Universal balancing**, since his trigger is element synergy rather than
Companion density. **No third taxonomy is created**, so the drafted option B is
rejected outright.

**P7 — the home-nation weight. `SAME_NATION_REWARD_SHARE` HOLDS AT 0.5.** The
drafted option A, with a condition attached: **re-measure the actual home-nation
and Personal appearance rates after the Personal set lands, and before any
tuning.** The constant is not defended on principle — it is held because nothing
has measured it since the taxonomy existed, and the measurement now has a
trigger.

**P8 — the missing colorless anchor. PRODUCED IN PARALLEL, AND IT IS A
PRECONDITION.** The anchor is not sequenced ahead of the Personal work and does
not block it, but it **must exist before any Universal Uncommon or Rare is added
or repriced.** This is stronger than the drafted option C: banking the question
becomes an actual gate on the Universal half rather than a re-check.

**P9 — per-nation shape. AN AUTHORING CONSTRAINT, SCOPED TO UNIVERSALS.** The
drafted option B, with the scope stated: **Personal cards follow character
identity, not nation shape**, and where a nation's shape family and the global
brick test disagree, **the brick test takes precedence over home-nation
synergy.** That last clause is the one that keeps §3.1's Universal definition
load-bearing: a card is not allowed to become a brick elsewhere because it fit
its nation's family well.

### 5.2 The sequencing program, as ruled

Parallel, not serial. The order below is a dependency order, not a queue.

1. **Now, in parallel:** Mondstadt taxonomy and the two Klee Personal drafts on
   one side; the colorless anchor's production and the companion-instrument
   repair (§2.6) on the other. Neither waits on the other.
2. **Gated on the Burst fold:** the sheet changes, and P3's three rewrites. They
   land in the fold, so nothing here sets their date.
3. **Then:** whole-fight proof of the Mondstadt slice → Inazuma → Fontaine.

This is what "one nation at a time, then work outward" (answer 1) looks like once
the work that is *not* nation-shaped — an anchor, an instrument — is allowed to
run beside it rather than in front of it.

### 5.3 What the ruling owes, and mints nowhere

The slate creates engineering. It is named here so it is not rediscovered, and
**no identifier is minted for any of it** — the rows mint on the
register-reconcile branch after tonight's runs land.

- **Produce the colorless anchor** (P8): the reference §2.4 could not find, and
  now a precondition on the Universal half.
- **Repair the companion instrument** (§2.6): both halves — the missing sheets,
  and the taxonomy filter that keeps Personal and guest-star rows out of a
  Universal-pool metric.
- **Draft the two new Klee Personal cards** (P2, P5): 4-star, under P5a's
  standing bar against a Rare.

Three things the ruling explicitly does *not* owe: a Rare Personal design (P5a
gates it), any Universal card (P2 excludes it from slice 1), and any change to
`SAME_NATION_REWARD_SHARE` (P7 holds it pending a measurement).

---

## 6. The picks

Numbered P1 to P9 plus the sub-pick P5a, this document only. **All are ANSWERED
by R234 (§5), except P5a, which R234 deliberately leaves OPEN.** The bodies below
are kept exactly as they were put to [USER] — each is a real fork, defaults are
marked where one was defensible, and where the material genuinely did not choose,
no default was marked and that is stated. Nothing here has been rewritten to
agree with the answer it got; the one-line RULED pointer at the head of each pick
is the whole of the ruling's footprint in this section.

---

### P1 — Which nation goes first

**RULED (R234): Mondstadt.** See §5.1.

Answer 1 says one nation at a time. This is the pick that starts the clock, and
[USER] took option A directly on 2026-08-30. The three options are kept below
unedited, because the arguments against A are the risks the Mondstadt slice now
has to carry.

**Option A — Mondstadt (Klee).** *Claude's recommendation.*
- Klee is the compatibility baseline character (`docs/current/STATE.md:83`), so
  anything proved here is proved on the least exotic engine in the roster.
- The Personal/Universal contract **already physically exists here**, and only
  here: Prune is the one `personal_pool` card in the game, and her engine
  interaction has already been through the full move from card face to kit
  declaration with parity tests
  (`tier0/tests/test_eb219_prune_kit_spark.py`). The exemplar is not
  hypothetical; it shipped this week.
- The prospective LAW:145 clause was written *about* this exact card
  (`burst-retirement-2026-08-29.md:350-358`), so a Mondstadt-first slice lands
  inside law that is already drafted rather than beside it.
- It also owns three of the four contract violations (§2.2), so first-nation
  work and cleanup are the same work.
- *Cost:* Mondstadt has no evidence in flight tonight; the slice starts from
  argument rather than from a read. And it is the pool most likely to want new
  cards rather than re-authored ones, which is slower.

**Option B — Inazuma (Kokomi).**
- Tonight's `KOKOMI-SLICE1-WF` is directly about Inazuma Companion shapes, and
  it is the only companion-shape evidence anywhere in the project. Starting here
  means the first nation's shape family is settled by a measurement rather than
  by taste.
- Kokomi's fold is upcoming, so the sheet is going to be opened anyway.
- *Cost:* the WF has not been graded — starting a slice on an ungraded read
  invites reading results early, which measurement law forbids. (The arm that
  was blocked on `EB-184` is no longer blocked: that row CLOSED 2026-08-30,
  §4.3.) It is also
  the pool with the heaviest existing defensive load (60% Block), so the taxonomy
  work and the Block work would arrive tangled.

**Option C — Fontaine (Furina).**
- Largest pool (19), the only complete Rare set, the only pool with a stated
  construction logic, and its Rares are **freshly closed** — R231 closed `M10`
  with the Fontaine Rares approved and Neuvillette shipping as-is
  (`docs/current/QUEUE.md:69-73`, `docs/current/STATE.md:836-837`). A closed
  section is a stable base.
- *Cost:* that same closure is the argument against. Fontaine is the pool most
  recently ruled on, so it is the pool where a fresh slice most risks looking
  like a reopening — and §7 forbids that. It also has the most in flight: the
  reframe's own whole-fight read is pending
  (`docs/current/STATE.md:600-603`), and its Companion hook is the most
  entangled engine of the three.

**Recommendation: A (Mondstadt).** The deciding argument is not pool size or
evidence timing; it is that the contract's only working exemplar, its only
declared kit hook with parity tests, and its only drafted law all sit in
Mondstadt already. Proving a concept on the nation where two of the three parts
are built is the shortest honest proof. Inazuma's WF evidence does not go stale
— it lands tonight and is still there when the second nation comes up, and under
answer 1's "work outward" it makes a strong *second*.

---

### P2 — What "first nation" actually means as a deliverable

**RULED (R234): option B, sized — taxonomy plus two new Klee Personal cards, three with Prune, no Universal expansion in slice 1.** See §5.1.

A. **Taxonomy only.** Flag every existing Mondstadt row Personal or Universal,
   fix the contract violations, ship no new cards. *Cheapest; proves the
   contract, proves nothing about pool depth.*
B. **Taxonomy plus Personal set.** The above, plus authoring Klee's Personal
   Companion set beyond Prune. *Proves the half of the concept that is new —
   Personal Companions are currently n=1.* **Claude's default.**
C. **Taxonomy plus Universal depth.** The above, plus growing Mondstadt's
   Universal count toward the 30-card floor. *Proves the colorless-replacement
   half, which is the half with no anchor to measure against (§2.4).*
D. **All three.** *Largest one-way door in the packet.*

*Cost of B over A:* new art, new codegen, new C# classes, and a rarity-band
argument per card. *Cost of C:* it is the option that trips the distinctness
gate (§2.6, P4), and it is the option that most wants the missing colorless
anchor (P8).

---

### P3 — The existing contract violations: re-author or grandfather

**RULED (R234): none of the drafted options as written — the three riders are resolved inside the shared Burst-retirement fold, no grandfathering, and none becomes a Klee-specific hook.** See §5.1.

The three undispositioned `burst_energy` faces (§2.2 — Barbara, Sucrose's
Astable, Bennett's Passion; Durin is already ruled RETIRE).

A. **Re-author all three now,** moving the meter feed into the character kit
   that wants it, exactly as Prune's Sparks moved. *Consistent, and the
   machinery exists. Costs a sheet edit, a stamp, and parity work in both
   engines for cards nobody has complained about.*
B. **Grandfather all three** as a priced, named v1 condition, the way R60
   phase 2's colorless leak is graded ACCEPTABLE and not scheduled
   (`docs/current/LAW.md:83-86`). *Cheapest; leaves the pool's first-day law
   with three visible exceptions.*
C. **Re-author on contact** — each is fixed the next time its card is opened for
   any other reason. **Claude's default:** it matches how Durin's feed is
   already being handled (retired inside the burst fold, not as its own errand),
   and the prospective clause does not bind until the folds land, so there is no
   date by which these must be legal.

*A caveat that belongs with this pick:* the Burst meter itself is mid-retirement
(`review/active/burst-retirement-2026-08-29.md`, eight LAW blocks countersigned
prospective). Re-authoring a `burst_energy` feed now may be work that the fold
deletes.

---

### P4 — The 30-card floor: target or hazard

**RULED (R234): option C — decouple.** See §5.1.

Stated as the fork in §3.3.

A. **Target.** Each nation's pool is grown to 30+ draftable cards, and passing
   distinctness at 30+ is the slice's success condition.
B. **Hazard.** Pools stay deliberately under 30 until a nation is grown past it
   in one deliberate step, with a fresh baseline taken.
C. **Neither — decouple.** The floor is an instrument threshold, not a design
   target; pool size is set by what the nation's shape family needs, and the
   gate is re-baselined whenever it starts applying. **Claude's default**, on
   the tool's own evidence that pools measured near the floor were measuring the
   extractor (`card_distinctness_report.py:163-167`) and that no pool it has
   ever measured — including the completed official anchors — passes all three
   thresholds (`:118-122`).

*Whatever is picked, the lint gap in §2.6 (Fontaine and Inazuma absent from the
instrument's input) becomes load-bearing under A and B and does not under C.*

---

### P5 — How many Personal Companions per character

**RULED (R234): option B — three to five long-term, starting at three.** See §5.1.

Personal Companions are currently n=1 across the whole roster.

A. **One per character.** Prune is the model; the Personal flavor is a signature
   card, not a set.
B. **A small set, 3–5 per character,** spanning rarities so the flavor exists at
   common as well as rare. **Claude's default** — answer 3 calls Personal
   Companions "a subset of a character's draftable pool", which reads as a set,
   and answer 4 gives *separate* balance guidance for Personal cards at
   equivalent rarity, which only bites if Personal cards exist at more than one
   rarity.
C. **Unbounded, governed by rarity only** — as many as the character's engine
   has interesting hooks for.

*Cost of B and C:* every Personal Companion is exempt from enabler-not-carry
(`docs/current/LAW.md:104-113`) and may be deck-warping by design, so each one
enlarges the surface the delete-test has to be re-run against.

#### P5a — How a Rare Personal Companion would ever be acquired

**RULED (R234): DEFERRED — this sub-pick stays OPEN and gates any Rare Personal design; slice 1 promises none.** See §5.1.

**This sub-pick exists because the answer today is "it could not be."** A Rare
Personal Companion is **unreachable through every live channel**, and that is a
structural fact rather than an oversight anyone has ruled on. The chain,
verified end to end:

1. **Rare means 5-star.** The sheet law is "4-star = common/uncommon
   (multi-card kits allowed). 5-star = rare, ONE card each, max 3"
   (`docs/mondstadt-companions.yaml:4`), and LAW carries the same grade
   (`docs/current/LAW.md:98-103`).
2. **Personal cards are excluded from every banner roster.**
   `five_star_roster` gathers a nation's banner-eligible 5-stars and filters
   `c.personal_pool is None and not c.guest_star`
   (`tier05/rewards.py:130-141`). A Personal 5-star is therefore never on any
   banner, in any run, by construction.
3. **Off-banner 5-stars are dropped from every offer pool.** `_banner_filtered`
   keeps a card only if `c.star != 5 or c.id in banner`
   (`tier05/rewards.py:199-204`).
4. **Both live channels run through that filter.** Rewards apply it before the
   `personal_pool in (None, character_id)` check
   (`tier05/rewards.py:339-342`), and the shop's `eligible` calls
   `rewards._banner_filtered` before its own personal-pool check
   (`tier05/shop.py:150-157`).

So a Personal 5-star can never be *on* a banner (step 2) and is filtered out
everywhere *off* banner (steps 3–4). The two conditions are exhaustive.

**The contrast that shows this is specific to Rares:** 4-star Personals are
perfectly reachable for their owner. Both channels admit
`personal_pool in (None, character)`, and 4-stars are never banner-gated —
`_banner_filtered`'s docstring says so in as many words. Prune is Uncommon, so
the one Personal Companion that exists has never met this wall.

**Options.**

a. **Owner-only banner bypass.** The banner filter stops applying to a Personal
   5-star in its owner's run; it stays filtered for everyone else. *Smallest
   change, and it preserves the banner as the availability governor for the
   shared pool while letting a character's own Rare behave like the rest of her
   kit.*
b. **Personal 5-stars participate in the owner's banner.** They enter
   `five_star_roster` when the run character owns them, and compete for the
   featured slots like any other Rare. *Keeps one governor for all 5-stars, but
   a character's own signature Rare can then be rolled out of her own run —
   and with `BANNER_FEATURED_SLOTS = 3`, adding Personal cards to a nation's
   roster also makes the shared Rares scarcer for their owner.*
c. **Run-start access only.** No draft channel at all; a Personal Rare arrives,
   if at all, through the declinable run-start offer LAW already permits — the
   R160 amendment's "optional, visible run-start offer ... the
   randomized-starter family, not new Neow machinery"
   (`docs/current/LAW.md:114-120`), whose mechanism exists and is nation- and
   role-locked (`tier0/content/loader.py:1140`;
   `tier05/tests/test_m5.py:55-101`). *Uses machinery that is already built and
   already lawful. Makes a Personal Rare a run-shaping opening choice rather
   than a mid-run find, which is a different card design.*
d. **No Personal Rares at all.** The Personal flavor caps at Uncommon, and the
   current unreachability becomes the rule rather than a defect. *Costs
   nothing, and is honest about where the code already is.*

**No default marked.** The written intent does not choose: answer 4 gives
Personal Companions a balance rule "at equivalent rarity" without naming which
rarities exist, and answer 3 calls them "a subset of a character's draftable
pool" — which argues they should be *draftable*, and so argues against (d), but
does not pick between (a), (b) and (c). That is a design fork, and §6's rule is
that a fork is a pick.

*Note on scope:* if P5 lands on option A (one Personal per character, Prune the
model) this sub-pick can stay unanswered indefinitely, since nothing would be
authored at Rare. Under B or C it has to be answered before the first Rare
Personal is authored, not after — authoring an unreachable card is the one
outcome none of the four options wants.

---

### P6 — Density payoff: is a Universal card allowed to pay out on Companion plays

**RULED (R234): split, per card — Navia takes option C (bounded or costed); Albedo returns to ordinary Universal balancing; no third taxonomy.** See §5.1.

**This pick has been narrowed. It previously bundled Navia and Albedo together,
and they are two different mechanisms** — EB-148 grouped them as "subsidy
engines" because both hand out free Block after one purchase
(`review/active/eb148-companion-audit-2026-08-27.md:40-47`), which is a true
statement about *defence economy* and not about what they trigger on.

- **`navia_cannon_fire_support`** triggers on **"whenever you play a Companion
  card"** (`docs/fontaine-companions.yaml:98-101`) — literally the pool paying
  the pool. Its power is a function of Companion *density*, and Companion
  density is exactly what Kokomi's Charge funnel and Furina's member trigger
  already reward, so the same card is quietly stronger in two specific decks
  while naming neither.
- **`albedo_solar_isotoma`** triggers on **attacking an enemy that bears an
  aura** (`docs/mondstadt-companions.yaml:83-84`). That is element synergy. Any
  deck that applies elements turns it on, which is every deck in the game, and
  its strength does not scale with how many Companions are drafted.

**So Albedo is not this pick's subject at all.** He returns to ordinary Universal
balancing under §3.2 — an aura-conditional Rare Power, judged against the
Universal Rare band like any other, with no taxonomy question attached. The
Navia/Albedo overlap the Fontaine sheet flags as "FLAGGED, NOT RESOLVED"
(`docs/fontaine-companions.yaml:106-109`) remains a real balance overlap between
two Geo block engines; it is a power-level question for whoever prices them, not
a taxonomy one, and this packet does not settle it.

**What is left, and it is only Navia and any future density-payoff design:**

A. **Universal, unchanged.** It names no character engine, so it passes the
   contract as written. *Accepts that a Universal card's power varies with a
   deck property two shipped engines are built to maximise.*
B. **A named third category** — pool-payoff Companions, a taxonomy of their own,
   balanced globally but priced against Companion density rather than a rarity
   band.
C. **Universal, but bounded or costed** — no new taxonomy. The contract gains
   one sentence about what a Universal card may pay out on a Companion play, and
   the affected card is re-authored to fit: a cap, a cost, or a different
   trigger.

**No default marked.** This is a design-direction fork, not a hygiene call: A
and C are opposite readings of whether "the pool paying the pool" is a feature
or the loop the playtest complained about.

*On the external review's suggestion, for the record:* "Universal but
bounded/costed, no third taxonomy" is **option C applied per-card once the split
above is made** — it is not a fourth option, and reading it as one would
double-count the position. What the split changes is its scope: before the split C
would have re-authored Albedo too, and after it, C touches Navia and leaves
Albedo alone.

---

### P7 — Whether the 50% home-nation weight is the right number

**RULED (R234): option A — 0.5 holds, with a re-measurement owed after the Personal set lands.** See §5.1.

`SAME_NATION_REWARD_SHARE = 0.5` (`tier0/constants.py:1420`) predates the
Personal/Universal split and was set when the home-nation pool was the only pool
with a balance story.

A. **Leave it at 0.5** and revisit only if a read moves. **Claude's default** —
   nothing measured has complained about it, and it is a one-constant change at
   any later date.
B. **Raise it,** on the argument that answer 3 makes home-nation cards the ones
   balanced *around* the character, so seeing them more often is now
   load-bearing rather than flavorful.
C. **Lower it,** on the argument that the Universal flavor is the colorless
   replacement and a colorless pool that is half one nation is not really a
   colorless pool.

*Note for whoever rules this:* the constant governs the **reward** slot. The
shop's home-nation concentration is structural instead — slot 1 is home-region
by construction (`docs/current/LAW.md:122-128`) — so B and C move one of the two
channels, not both.

---

### P8 — Whether this slice produces the missing colorless anchor

**RULED (R234): produced in parallel, and a precondition on any Universal Uncommon or Rare.** See §5.1.

§2.4: `game_ref/` contains no colorless pool data, so "slightly better than
native cards of equal rarity" (answer 4) currently has no referent.

A. **Produce it first.** Run `tools/extract_base_game_pool.py` for the colorless
   pool, record size, rarity split and a power read, and design against it.
   *Also clears the standing red on `card_distinctness_report.py --gate`
   (`docs/current/OPERATIONS.md:164-170`). Costs time on the art-bearing main
   checkout, and this branch cannot do it.*
B. **Proceed without it,** reading "slightly better" against the character
   sheets and [USER]'s stated Rare instinct
   (`docs/inazuma-companions.yaml:103-106`). *Fastest; leaves the one balance
   sentence in answer 4 that names an external reference unanchored.*
C. **Proceed, but bank the question** — design to the character-sheet reading
   now, and re-check the Universal Uncommons and Rares once the anchor exists.
   **Claude's default**, because it is the only option that neither blocks the
   slice on an errand nor quietly redefines [USER]'s words.

---

### P9 — Whether "per-nation shapes" is a constraint or an observation

**RULED (R234): option B, scoped to Universals — Personal cards follow character identity, and the brick test outranks home-nation synergy.** See §5.1.

Answer 2 says shapes are per-nation. Two readings:

A. **Observation.** Each nation happens to have a character and a lore frame, so
   its cards cluster; nothing enforces it. *Costs nothing, guarantees nothing.*
B. **Constraint.** Each nation declares a shape family in its sheet header, and
   new cards are authored to it — with the distinctness instrument as the check
   once pools clear 30. *Makes answer 2 testable. Costs an authoring rule and,
   under P4-A/B, a gate that starts biting.* **Claude's default**, weakly:
   Fontaine already does this voluntarily (its header declares convergence
   levers and a deliberate Electro absence, `docs/fontaine-companions.yaml:5-8`)
   and it is the pool that reads most deliberately of the three.

*Pending WF:* if Inazuma's shape family turns out to be settled by tonight's
read, B gets cheaper for that nation — the declaration writes itself from the
result.

---

## 7. What this slice does not touch

- **The Fontaine Rares are CLOSED and stay closed.** R231 closed `M10` with the
  close approved, the v1.7 lore/naming audit riding on it, and **Neuvillette
  shipping as-is** carrying its later redesign
  (`docs/current/QUEUE.md:69-73`; `docs/current/STATE.md:836-837`). Nothing in
  this packet reopens a Fontaine Rare, re-prices one, or reads the closure as
  provisional. Fontaine appears in P1 only as a first-nation candidate, and §4.2
  describes its shape family without proposing a change to any card.
- **The shipped kits.** Klee's Spark declaration, Kokomi's Charge funnel and
  Furina's Salon hook are the contract's evidence, not its subject matter. This
  slice names what they already do; it does not modify them.
- **Everything mid-flight tonight.** `KOKOMI-SLICE1-WF` is running and ungraded
  — nothing here reads it, anticipates it, or is written to be consistent with a
  guessed outcome. The Furina reframe's own whole-fight read is likewise pending
  (`docs/current/STATE.md:600-603`), the Burst retirement's LAW blocks are
  countersigned prospective with no `LAW.md` line moved
  (`docs/current/STATE.md:863-869`), and the Kokomi Charge slate is prospective
  under R213 (`docs/current/LAW.md:243-249`).
- **`LAW.md` itself.** §3 is drafted in law's shape as a convenience for a
  ruling. No line of `LAW.md` moves in this branch, and the prospective LAW:145
  rewrite stays exactly as R224 countersigned it.
- **Any register.** No QUEUE, BACKLOG, EXPERIMENTS or STATE edit; no id of any
  kind is minted. The two audit findings this packet turned up — the three
  undispositioned `burst_energy` faces (§2.2) and the distinctness tool's
  missing sheets (§2.6) — are named here and filed nowhere.

---

## 8. Sequencing — the constraints the ruled program was built on

**§5.2 is the ruled program and this section is its reasoning.** Where the two
differ in shape, §5.2 governs: R234 made the program **parallel**, so the anchor
and the instrument repair run beside the Mondstadt work rather than behind it,
and the serial reading at the end of this section is superseded on that point.
The dependencies below are unchanged by the ruling and are why the parallel form
is safe.

**Tonight.** `KOKOMI-SLICE1-WF` runs. It is the only companion-shape evidence in
the project, it is about Inazuma, and it is why §4.3 concludes nothing. When it
grades, §4.3's shape reading becomes answerable — which matters for the *second*
nation now that P1 is settled on Mondstadt, not for the first.

**Relative to the Klee arc.** P1 is settled on Mondstadt, so this slice and the Klee
arc share a sheet. The Spark redesign is pending (`M48` pick 6), and Klee's
`PICK 1` reopens only if the income reads short
(`docs/current/STATE.md:823-825`). A Mondstadt companion slice should sit
*after* whatever moves Klee's Spark economy, because Personal Companions are the
things that mint Sparks and their power level is a function of what a Spark is
worth.

**Relative to the Kokomi fold.** The fold opens Kokomi's sheet. `S4-G6`'s band
is explicitly sequenced "after the Kokomi fold"
(`docs/current/STATE.md:825-826`). An Inazuma companion slice most naturally
rides that opening rather than preceding it — which is a second, independent
argument for Inazuma being the *second* nation rather than the first.

**Relative to the Furina C# window (R213).** Furina's reframe slice 1 is built
in the sim behind five flags that all ship OFF
(`docs/current/STATE.md:617-625`), and the Companion-play trigger is one of the
things behind those flags. A Fontaine companion slice cannot settle Fontaine's
shape family while the hook that reads Companion plays is unflipped, because the
value of every Fontaine Companion in Furina's hands changes when it flips.

**The nation order these three constraints imply** — and the half of the drafted
sequence R234 kept: Mondstadt now (contract proved on the baseline character with
the built exemplar) → Inazuma after the fold and with the WF graded → Fontaine
after the reframe's flags flip. That is answer 1's "one nation at a time, then
work outward", with the outward order chosen by which evidence lands when rather
than by pool size.

**What R234 changed about it:** the drafted version read this as one serial
queue, which would have put the colorless anchor and the instrument repair behind
a nation. Neither is nation-shaped, and neither blocks the Personal drafting, so
§5.2 runs them in parallel and gates only what genuinely depends on something —
the Universal half on the anchor (P8), and the sheet rewrites on the Burst fold
(P3).

---

*End of packet. DRAFT — nothing countersigned, no shipped number moved, no code
written, no identifier minted.*

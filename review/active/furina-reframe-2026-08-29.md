# Furina reframe — the design packet

> **Lifecycle: ACTIVE.** A design packet, not law. §3 is a DRAFT ruling
> awaiting [USER]'s countersign; §9 is what returns to him. Nothing here has
> moved a shipped number, a sheet row, a constant, a register entry or a line
> of `LAW.md`. No code was written for it.
>
> **This packet SUPERSEDES `review/active/furina-e4-2026-08-29.md` on paper**
> — specifically its §3 ruling text, its §4 architecture, its §7.1 reader
> triage and its §12 build contract. E4's §2 evidence and §2.10 sheet census
> are still true and are CITED here rather than copied. E4 stays in
> `review/active/` as the record of how the direction was reached; it is not
> struck, and three of its §13 findings are inherited below.
>
> **Why a new packet and not a revision.** E4 answered a question [USER] has
> since replaced. Revising it in place would have meant editing the text a
> countersign (`M52`) is pending on. A superseding packet is the honest
> shape: the old text stands as what was proposed, and the signature moves.

**Date:** 2026-08-29. **Branch:** `furina-reframe`, cut from `origin/main` at
`77eea5f`. **World:** `RT12 / D18 / P11 / C20`, `PILOT_WEIGHTS_VERSION` 6.
**Authority:** R213 E4 as amended by R217; the delegation ladder is R212; the
design charter is LAW's D1–D9 (R217).

Every `file:line` below was verified in this tree at `77eea5f`. Where a figure
differs from the one E4 quotes, the difference is called out — E4's census was
taken on 2026-08-12 and the sheet has moved since.

---

## 1. The inputs

### 1.1 [USER], verbatim

The framing message, first:

> "We're trying to juggle three things at once: 1) What does the Salon do?
> What cards make it useful? 2) How does Furina play with Companions? Is this
> an archetype in itself? If not, what kit gaps is Furina looking for from
> them, and how does she get them? 3) What does Furina's own kit do, besides
> set up Salon and Companions? AKA what are her archetypes, or is Furina
> 'Salon and/or Companions and also some utility stuff?' … I think the basic
> concept of the Salon as a rotating set of effects is fine, mimicking the
> style of Defect orbs, but if so then they need to be able to scale, you
> need to adjust the size of them, they need to be able to provide damage /
> block / scaling / (at high rarity) energy, etc, just like Defect does. And
> this needs to be obviously legible to the player. And it makes sense to
> integrate companion cards with the stage as well, but it needs to be in
> some sort of complementary way so that you don't end up with cards
> competing for space that brick the other side."

Then the brief:

> "Let's aim for the following:
> Encore is both Furina's deferred block as well as a resource that is spent
> down to direct the Stage via Evoke-style plays.
> Salon members are the equivalent to orbs. They need a general redrafting to
> account for a range of possible effects. Unlike Defect orbs they do NOT
> auto-play.
> Fanfare is the focus-equivalent, which scales the Salon members but decays
> over time.
> Companion card plays trigger a single Salon member's effect (rotating)
> without evoking them.
> Furina's own cards can Evoke the Salon members, expending them, but with
> much stronger Fanfare scaling or alternative effects, as well as read the
> Fanfare meter for direct effects. She also has cards that add companion
> cards to her deck (Existing functionality).
> When Fanfare reaches a threshold, it prints the burst card, which puts
> Furina into a strong overdrive at the cost of reducing Fanfare by a large
> amount (my initial idea - for some number of turns, a temporary Fanfare
> bonus larger than what was expended, and scaling that applies to companion
> cards). One viable playstyle is to just not use the Burst and keep Fanfare
> juiced at all times."

And the critique that ended E4:

> "this makes Fanfare a meaningless form of generation. What is the payoff
> for Featured?"

### 1.1a [USER]'s answers to the four open items — RULED, 2026-08-29

Claude returned four open items with the read at §1.2. [USER] answered all
four the same day, verbatim below. **These are RULED, not picks.** They shape
§3 and §4 directly, and where they overturn a sentence in the brief above —
item 3 does — the answer governs.

**1. What generates Fanfare.**

> "Agreed"

— to Claude's recommendation: a member PERFORMING mints Fanfare, a trigger
minting the small amount and an Evoke the larger; deliberate Encore spend
mints nothing by itself.

**2. Deploy tempo and the empty stage.**

> "I think that most Deploy cards should come with a trigger clause, so
> deployment cards do actually do something useful, and overcrowding the
> stage still forces out an Evoke. If your Salon is empty, then companions do
> nothing extra."

Three rules: most deploy cards deploy **and** make that member perform;
deploying onto a full stage **Evokes** the front member (Defect's
channel-when-full); a Companion played with an empty Salon does nothing extra.

**3. The Burst — the brief's own last paragraph is withdrawn.**

> "Actually, maybe we're overcomplicating this. If fanfare IS the burst, then
> maxing the meter is its own payoff. 'Drain Fanfare for a giant effect'
> could be a Rare-level payoff card separate from the base character kit.
> Furina's Burst doesn't need to be a card in itself."

And, settling the LAW question this packet raised against it:

> "I think the Burst Meter thing might be overdone, honestly. It was a day 1
> idea that frankly feels like it adds complexity without payoff. So folding
> it into Furina's already-existing Fanfare concept feels fine. Klee's Burst
> feels basically redundant, and I want to make Kokomi's more useful as part
> of the current rework as well."

And, ruling the roster-wide consequence:

> "Yeah, agreed on the Burst changes"

— the shared Burst meter is retired as a concept, each character's signature
resource becomes her gauge, and each former Burst becomes a drain or overdrive
of that resource. That change is packeted separately on branch
`burst-retirement`; **Furina's fold below is the last of its three** (R220 B
sequences the folds Kokomi → Klee → Furina, with the shared retirement last).

So, for Furina: no Burst card printed at a threshold, no overdrive loan, no
temporary Fanfare bonus and no entitlements. A full meter is a maximally scaled Salon,
and that fill state **is** the reward. "Drain it all for a giant effect"
becomes an optional **Rare payoff card**, drafted, not base kit.

**4. Co-op.**

> "Agreed"

— to Claude's recommendation: an ally's Companion play triggers Furina's
stage, one member performs and rotates, with the same empty-stage no-op.

### 1.2 Claude's read, as given to [USER]

*(Claude's, not a ruling. Recorded because the design rests on it and because
§1.1a's four answers are answers to its four questions. The four are now
RULED and are not picks in §4.)*

The strong points of the brief are these. Making the members not auto-play
dissolves the seat's "repeatable 14-damage engine" objection at its root, and
it makes the stage legible in a way the current one is not: the stage performs
when you play, so a player who does nothing sees nothing happen, and a player
who plays a Companion sees exactly one thing happen. Trigger-versus-Evoke is
complementary rather than competitive, which is the thing [USER] asked for —
Companions live in your hand and the Salon lives on the board, so the two
never fight for the same card slot; one is a body you draft and the other is a
board you build. Change the Bill's existing rotate becomes the aiming verb for
both halves. Fanfare-as-Focus-with-decay gives the meter two uses that pull
against each other, which is what a resource needs in order to be a decision:
hold it high and every member hits harder, or cash it and start climbing
again. And the machinery for both already exists — `FANFARE_DECAY_FRACTION`
and the Focus term `SALON_FOCUS_PER` are both live and shipped, and E4 was
retiring the first and orphaning the second.

The four open items were: what mints Fanfare (the brief never says); deploy
tempo without a passive tick; the Burst loan's numbers and the Focus cap that
has to be set alongside them; and co-op, where "an ally's Companion play
triggers your stage" would return the ally-coupled mechanic E4 lost. **All
four are answered at §1.1a**, and the third was answered by removing the loan
rather than by numbering it.

### 1.3 What E4 was, and why it is superseded

E4 was the packet R213 asked for: prove the four mechanics function as parts
of one loop, or cut or merge them. It merged aggressively. It folded Fanfare
into the Burst meter outright, retired Fanfare's decay, floor and cap
machinery, retired the +50% Spotlight multiplier, retired Center Stage as a
mode, and made a *Featured performance* the meter's single cause. Salon
members kept their automatic turn-start tick, and the Featured act was an
extra act laid on top of it.

Three things ended it, all on the record.

**[USER]'s critique.** "this makes Fanfare a meaningless form of generation.
What is the payoff for Featured?" — E4's meter had exactly one consumer, the
Burst, and Fanfare's only job was to count to it. Under this packet the meter
scales the whole board continuously, so holding it *is* the payoff.

**E4's own §13 fresh read.** A fresh-Claude session graded the GPT-authored
rows and returned four `REQUIRES_MODIFICATION` and one `CONFLICTS`
(`review/active/furina-e4-2026-08-29.md:2146-2163`); revision 4 closed all
five in place. Three of those findings are facts about the shipped engine
rather than about E4's prose, so they survive E4's supersession and are
carried into §2.7.

**The direction changed under it.** E4 is B1 — the fold R177 declined. This
packet is not B1: three named mechanics survive with distinct jobs. R177's
*measured* finding, that the stage outruns its fuel, is untouched by either
packet and constrains §4.2 here exactly as it constrained E4's §4.3.

**What E4 leaves behind that this packet keeps.** Its §2 evidence, entire —
the three-plan winrate structure, the selector heuristic as the collapse rule,
the 0.167 move share, the relic upgrade that deletes the choice, the two
meters observing one activity, the Encore-has-no-denominator finding, the
starter that does not teach the plan, and the §2.10 sheet census. All cited
below, none copied. **And one of its retirement items, carried over verbatim
in substance:** E4 §3 item 7 named the four constants that feed the Burst
meter without being performances — `BURST_PER_REACTION`,
`BURST_PER_SKILL_TAG`, `SALON_TICK_BURST` and `BURST_PER_ENCORE_SPENT`. This
packet retires all four for Furina too, and for a simpler reason: under §1.1a
item 3 she has no separate Burst meter for them to feed.

**What E4 leaves behind that this packet drops.** The merge direction is
reversed — E4 folded Fanfare into Burst; this packet folds Burst into Fanfare.
With it go: the retirement of `FANFARE_DECAY_FRACTION` and
`FANFARE_CAP_FRACTION`; the orphaning of `SALON_FOCUS_PER`; the single-cause
"only a Featured performance creates Fanfare" rule; the Featured-entitlement
tokens; the two-lane persistent Spotlight; and the per-character narrowing of
LAW's reaction-credit clause. That last one is worth naming: **E4 needed a
carve-out of a roster-wide clause because it gave Furina a merged meter that a
teammate's reaction would have fed. Here she has no Burst meter at all, so
`LAW.md:64-66` is untouched and the carve-out is unnecessary.**

---

## 2. Evidence

### 2.1 The Salon engine as it ships

`tier0/constants.py:361-370`, the member table, ratified R187 / `M24`
2026-08-13:

| member | tick (automatic slot passive) | bow (on displacement) |
|---|---|---|
| `crabaletta` | 6 damage (Hydro, random enemy) | 14 damage |
| `usher` | 3 Block | 9 Block |
| `chevalmarin` | 2 damage **and** applies Hydro | Hydro to ALL enemies, +3 Encore |

Three members, three effect kinds, and exactly one printed numeric each — a
fact the engine leans on: `salon_tick_amount` reads `spec.get("damage", 0) or
spec.get("block", 0)` and its docstring says "each member prints exactly one
numeric, so one reader answers for all three"
(`tier0/engine/effects.py:4505-4522`). **There is no `encore_cost` field
inside `SALON_MEMBERS`** — upkeep is uniform through `SALON_TICK_ENCORE_COST`
— and there is no "evoke" entry: the `bow` entry **is** the Defect-evoke
analogue.

The dials:

| constant | value | line | what it does |
|---|---|---|---|
| `SALON_FOCUS_PER` | 10 | `tier0/constants.py:371` | +1 to every member numeric per this much held Fanfare |
| `SALON_MEMBER_SLOTS` | 3 | `:373` | "Defect-orb shape: fixed active company" |
| `SALON_REPLACE_NUMERIC_MULT` | 2 | `:374` | deploy card's other numerics, on replacement |
| `SALON_REPLACE_DAMAGE_MULT` | 3 | `:375` | deploy card's damage riders, on replacement |
| `SALON_TICK_ENCORE_COST` | 1 | `:376` | Encore drained per member per tick |
| `SALON_DRY_DAMAGE_MULT` | 0.75 | `:377-378` | with no Encore the tick pays three-quarters — the comment reads **"never true-HP loss (auras still apply)"** |
| `SALON_TICK_BURST` | 2 | `:379` | Burst particles per tick **and** per bow |
| `BURST_PER_ENCORE_SPENT` | 1 | `:381` | Burst particles per point of Encore spent |
| `FANFARE_DECAY_FRACTION` | 0.20 | `:268` | proportional decay of held Fanfare |
| `FANFARE_CAP_FRACTION` | 0.5 | `:226` | Fanfare cap as a fraction of max HP |
| `FANFARE_PER_HP_LOST` | 1 | `:240` | |
| `FANFARE_PER_ENCORE_SPENT` | 1 | `:241` | |
| `FANFARE_PER_ENCORE_ABSORBED` | 1 | `:242` | |
| `FANFARE_PER_SPOTLIGHT_CARD` | 2 | `:259` | |
| `SPOTLIGHT_BASE_MULT` | 1.5 | `:151` | ratified R71 |
| `BURST_PER_SKILL_TAG` | 5 | `:129` | |
| `BURST_PER_REACTION` | 5 | `:130` | |

**One correction to a figure this packet nearly quoted wrongly, and it
matters.** `SALON_FOCUS_PER`'s comment at `:372` reads "cap 30 -> +3;
uncapped 45 -> +4". **That is a comment, not a constant.** There is no
`SALON_FOCUS_CAP` anywhere in the tree; the only ceiling on the Focus term is
the Fanfare cap itself, `FANFARE_CAP_FRACTION × maxHP`. At Furina's shipped 78
HP (`tier0/content/characters/furina.yaml:9`, raised from 60 by the R219 F
slate) that cap is **39**, so the Focus term tops out at **+3** and the
comment's "+4 at 45" is unreachable. Anyone reading the comment as a dial will
look for a constant that does not exist. §4.5 owns this.

Her Burst meter is `burst_max: 70`
(`tier0/content/characters/furina.yaml:25`, ratified R17 2026-07-20), whose
own comment names its four income sources — skill tags 5, reactions 5, Salon
ticks 2 per member per turn, Encore spend 1 per point. The Burst card is
`let_the_people_rejoice` (`docs/furina-cards.yaml:836-838`): rare, cost 0,
archetype `generic`, tags `[burst]`, `kit_card: true`, `requires:
burst_energy_full`, and its body is 8 AoE damage with a `1_per_4_fanfare`
bonus plus 6 Encore. It is listed as her kit at `furina.yaml:29` with the
comment "v1.9: Burst is kit, not loot", and it is the one Furina row codegen
cannot generate (STATE: 83 of 84 generated, 1 blocked).

### 2.2 The three Salon verbs already exist — and so does the full-stage Evoke

All three verbs are shipped and built; two of them are used by exactly one
card.

- **`_op_salon_bow`** (`tier0/engine/effects.py:1908-1932`) — the LEFTMOST
  member takes its final bow and leaves, `salon.pop(0)`. Its docstring calls
  itself the "**Defect-evoke analogue**". Inert on an empty stage, silently
  and deliberately. Registered at `:4129`.
- **`_op_salon_rotate`** (`:1935-1956`) — a pure reorder, leftmost to the
  back. No tick, no Encore drain, no bow. It buys "exactly one thing — which
  performer the FIFO end offers next". Emits `salon_rotate_whiffed` at `:1952`
  when empty. Registered at `:4130`.
- **`_op_salon_perform`** (`:1959-1979`) — the leftmost member performs NOW,
  at the standard price, and **stays on stage**. It resolves through
  `salon_member_act`, "the same function the turn-start upkeep calls", so the
  Encore cost, the dry three-quarters, the Focus scaling, the Burst particle
  and the telemetry are inherited rather than restated. Emits
  `salon_perform_whiffed` at `:1975`. Registered at `:4131`. Its docstring
  already names the brief's pattern: "pair it with `salon_rotate` to spread
  the acts across the company."

**[USER]'s "overcrowding the stage still forces out an Evoke" is already the
shipped behaviour.** `salon_slots(player)` returns `SALON_MEMBER_SLOTS +
powers["salon_cap_up"]` (`:1406-1415`), and its only consumer is the
displacement check at `:1436`: deploying into a full stage calls
`_salon_bow(state, p.salon.pop(0))` at `:1438` — the front member's bow,
which is the Evoke. The rule §1.1a item 2 asks for is a rename of a rule that
ships, not a new mechanism.

The Focus term is read at `:1365`, inside `_salon_amount` (`:1343-1366`):
`focus = resources.readable(p) // C.SALON_FOCUS_PER`, added to the member's
base along with `salon_damage_up`, filing a `fanfare_read` census row unless
the caller is the forecasting pilot.

**The automatic tick is real, it is at TURN START, and it is the thing this
packet removes.** `salon_tick(state)` is called at `:4469` inside
`player_turn_start_triggers` (`:4365`), deliberately placed after the Encore
income block. `salon_tick` (`:4568`) emits `salon_upkeep` then loops
`salon_member_act` (`:4525`) per member, which checks `p.encore >=
SALON_TICK_ENCORE_COST`, spends the upkeep, and grants `SALON_TICK_BURST`.
There is **no end-of-turn Salon path**, so removing the turn-start call
removes the automatic engine entirely.

### 2.3 The Defect-orb comparison, term by term

| Defect | Furina, today | Furina, under this packet |
|---|---|---|
| **Channel an orb** | deploy a member — `apply_power salon_member … member: <named>` | deploy **and** perform that member once (§1.1a item 2) |
| **Passive (every orb acts at end of turn, free)** | the turn-start tick, `SALON_TICK_ENCORE_COST = 1` each | **REMOVED.** Members do not auto-play. The single biggest change. |
| **Channel into a full slot set evokes the oldest orb** | the displacement bow at `effects.py:1436-1438` | unchanged in mechanism, renamed: a deploy onto a full stage Evokes the front member |
| **Evoke (front orb acts big, then leaves)** | `_op_salon_bow`, "the Defect-evoke analogue"; one card uses it (`take_your_bow`, `docs/furina-cards.yaml:491`) | Evoke is Furina's own verb, expends the member, and pays either much stronger Fanfare scaling or an alternative effect |
| **Focus (+1 to every orb's number)** | `SALON_FOCUS_PER = 10`, live at `effects.py:1365` | unchanged in shape; Fanfare **is** Focus, and it decays |
| **Orb slots (3, raised by Capacitor)** | `SALON_MEMBER_SLOTS = 3`, raised by `salon_cap_up` — one card, `casting_call` (`docs/furina-cards.yaml:104-105`) | unchanged; the cap lever stays a drafted card |
| **Lightning / Frost / Dark / Plasma** — damage / block / scaling / energy | Crabaletta (damage), Usher (Block), Chevalmarin (aura + Encore). **No scaling member. No energy member.** | the roster gap — §4.2 |
| **(no analogue)** | — | **the Companion trigger**: a Companion play makes one member perform and rotates. Defect has nothing like it; it is the complementary hook [USER] asked for. |

The two blanks are exactly the two [USER] named ("damage / block / scaling /
(at high rarity) energy"). The Salon has the first two and neither of the last
two.

### 2.4 The sheet, as it stands today

`docs/furina-cards.yaml` holds **84 rows** (STATE: 82 + the two `Win3`
Salon/Spotlight rows). Overall rarity: 5 basic / 23 common / 37 uncommon / 19
rare. By archetype tag and rarity, counted live:

| archetype | basic | common | uncommon | rare | total |
|---|---|---|---|---|---|
| `salon` | 1 | 8 | 15 | 2 | **26** |
| `spotlight` | 0 | 4 | 10 | 4 | **18** |
| `fanfare` | 1 | 8 | 12 | 9 | **30** |
| `generic` | 4 | 10 | 13 | 7 | **34** |

*(Rows carry more than one archetype, so the column sums exceed 84.)*

**Two rare tiers are nearly empty, and one of them is where §4.6 puts its
payoff card.** `salon` has **2 rare rows** against 15 uncommon — the thinnest
rare tier of the four archetypes. That is the hole the Rare drain card fills.

**This does not match E4's §2.10 census, and the difference is the sheet
moving, not an error in either.** E4 quotes
`review/active/eb81-furina-remedy-options-2026-08-12.md:117-131` — salon 28
touching / 15 exclusive, fanfare 31 / 14, spotlight 18 / 15 — taken before
`Win3`. Two facts from it still hold and are worth carrying: fanfare's
exclusives are rare-heavy, so a change confined to them is a change most decks
never draw; and twelve cards are tagged `[fanfare, generic]`, i.e. fanfare
cards the drafter also offers to salon decks. Cited, not restated.

**Eleven rows read the Fanfare meter in their body** — a `bonus_formula:
N_per_M_fanfare` or an `if: fanfare_at_least_N` gate: `applause_line` (`:321`),
`held_breath` (`:336`), `crescendo` (`:553`), `florid_cadenza` (`:559`),
`dramatic_entrance` (`:746`), `let_the_people_rejoice` (`:836`),
`universal_revelry` (`:907`), `high_tide` (`:930`), `the_final_verdict`
(`:951`), `thunderous_ovation` (`:991`), `flood_of_emotion` (`:997`). That is
the population §7 is about, and it is smaller than E4's "~31 readers" because
31 counts every row *tagged* fanfare and 11 counts every row that *reads the
number*.

Three further sheet facts the design depends on:

- **`gain_fanfare_floor` appears on 3 rows** (`unheard_confession` `:859`,
  `the_sea_is_my_stage` `:899`, `rapturous_applause` `:1011`), and
  **`raise_fanfare_cap` appears on ZERO rows** despite the op existing at
  `effects.py:1863`. STATE says the same thing from the other direction: the
  pool carries zero `raise_fanfare_cap` riders and lint `R7` retired with
  them. So the Fanfare **cap** is today a constant nothing can move, which is
  a pick in §4.5.
- **`encore_cost` appears on exactly 2 rows** — `ebb_and_flow` (`:299`, cost
  1) and `dress_rehearsal` (`:539`, cost 2). The field exists and the gate
  works; the family does not. That is `F3`/`Win11`, frozen.
- The sheet's own header comment at `:13` claims 78 cards against a real 84.
  A stale hand-maintained count of exactly the kind the sheet's other comments
  warn about — hygiene, noted at §10.

The specific rows this packet touches or leans on:

| row | line | why |
|---|---|---|
| `salon_debut` | `:83-84` | the basic; `member: random`, ruled random by A11 on 2026-07-28 |
| `casting_call` | `:104-105` | the ONLY `salon_cap_up` card — the whole Capacitor analogue is one common |
| `gentilhomme_usher` | `:128-129` | deploy Usher + 4 Block, common |
| `surintendante_chevalmarin` | `:131-132` | deploy Chevalmarin + 3 Encore, common |
| `mademoiselle_crabaletta` | `:135-136` | deploy Crabaletta, bare, common |
| `change_the_bill` | `:472-473` | `salon_rotate` + `salon_perform` + 3 Block — the only user of either verb, and the comment at `:467` says both "have been built and unused since Phase 2" |
| `take_your_bow` | `:491-492` | the only on-demand `salon_bow`, cost 0 uncommon |
| `full_ensemble` | `:518` | deploys all three members |
| `let_the_people_rejoice` | `:836-838` | the kit Burst — §4.6 |

Companion sources: `docs/fontaine-companions.yaml` **19 rows**,
`docs/mondstadt-companions.yaml` **17**, `docs/inazuma-companions.yaml` **15**
— 51 in a nation-weighted reward channel, with the Featured Banner governing
5-star availability (LAW, Economy).

### 2.5 What E4's evidence established, cited not copied

Load-bearing here and not restated:

- The three plans are not one system: salon 4.70% / spotlight 1.50% /
  fanfare 1.30% at `RT9/D14/P6/C8`, Salon's interval disjoint from both, the
  other two indistinguishable from each other and from the `real_silent`
  floor (E4 §2.1). Structure only; three stamp boundaries stale.
- The Spotlight selector heuristic at `effects.py:1810` *is* the collapse
  rule, not a collapse toward one (E4 §2.2).
- `STATIC_SPOTLIGHT_MOVED_SHARE = 0.167` — the drafter prices every "if you
  moved the Spotlight" payoff against one turn in six (E4 §2.3).
- The upgraded starting relic deletes the mode choice outright (E4 §2.4).
- Encore is unbounded with no cap constant by design, so a fill bar has no
  denominator; the ribbon renders a runway (E4 §2.7).
- The Encore-spender family `F3` does not exist and is frozen in `Win11`
  behind the pilot's Encore opportunity-cost repair (E4 §2.8, STATE).
- The starter does not teach the default plan: one Salon card, random member
  (E4 §2.9).
- Blast radius, measured: 37 test files reference salon, 32 fanfare, 18
  spotlight across a 190-file suite; 16 / 10 / 6 pin the plan name as a quoted
  string literal. Any landed step re-baselines the whole twelve-arm table
  (E4 §2.11, §7).
- R177's finding that the stage outruns its fuel — half of all upkeeps arrive
  unable to fund a member — stands and constrains §4.2 (E4 §2.12).

### 2.6 The design charter clauses this packet is graded against

D2 (player-controlled leverage; "watch it rise until the number is large" is
not a decision; the control must be reachable early), D3 (benefits carry
binding prices; the counterfactual test), D4 (visible and live effects;
invisible feeds are defects), D8 (archetypes differ in how turns unfold, not
in the label on a bigger number) and D9 (the starting relic and starter deck
introduce the central verbs and one recurring tension from fight one, with no
invisible feed). `docs/current/LAW.md:389-439`.

**D2 deserves a note against §1.1a item 3.** "Maxing the meter is its own
payoff" is one sentence away from "watch it rise until the number is large",
which D2 names as not-a-decision. It escapes because the meter *decays*: the
number does not rise while you watch it, it falls, and holding it high demands
that the stage keep performing. The decision D2 requires is "do I spend this
turn making the stage perform, or doing something else", and it recurs every
turn. That is the whole load-bearing argument for the design, and §4.5's decay
rule is what makes it true or false.

### 2.7 Three defects E4's fresh read found that survive into this packet

Engine facts, not E4 prose, so superseding E4 does not close them.

**(a) `SALON_FOCUS_PER` is a live reader with no owner under E4.** E4 §3 item
2 retired "Spotlight means +50%" and §3.1's replacement text forbade a
designation carrying a numeric multiplier; E4 §4.1 alternative (b) then names
the Focus bonus as "a numeric multiplier, exactly what §3.1 retires". But
`_salon_amount` reads `SALON_FOCUS_PER` on every member act
(`effects.py:1365`) and E4 retired neither the constant nor the reader — it
retired the *meter the reader reads* and replaced it with a Burst meter that
empties on cast. A Focus term reading a meter that zeroes every Burst is a
different mechanic wearing the same constant. **Under this packet it closes by
construction**: Fanfare is Focus, so `SALON_FOCUS_PER` is the term's home and
its owner is §4.5.

**(b) The tick-versus-Featured ambiguity in E4 §4.1.** E4 asserted the
Featured act "costs the front slot", and the fresh read showed that price is a
function of stage size and is **zero at size one** — the state a Furina deck
spends its early turns in, and the state the starter boards would stage (E4
§13.3). The general form carries: **any positional price on a rotating queue
is worth nothing on a one-member stage**, and a one-member stage is the
default. Inherited here as a hard constraint on §4.3 and §4.4 and as a
required test board in §6.

**(c) The kickoff and LAW describe a Salon overdraw the engine does not
implement.** `docs/current/characters/furina-kickoff-v0.1.md` §4 says "**Salon
overdraw drains true HP when Encore is empty** — greed is legal and priced",
and LAW's Encore bullet carries "overdraw drains true HP". The shipped rule is
`SALON_DRY_DAMAGE_MULT = 0.75` with the constant's own comment reading
"**never true-HP loss (auras still apply)**" (`tier0/constants.py:377-378`),
applied at `effects.py:4522`. LAW's sentence is true of *Encore absorption*
overdraw and false of *Salon* overdraw; the kickoff's is about the Salon and
is stale. **A documentation defect, not a design question** — hygiene under
the norms, owed as a one-line kickoff correction on whichever branch next
touches that file. Recorded rather than fixed here because this branch is
docs-only for `review/active/`.

---

## 3. Ruling text — DRAFT for [USER]'s countersign

> **R2xx — Furina: the Salon is an orb board, Fanfare is its Focus and its
> Burst, and Encore aims it.**
>
> **The architecture.** Encore is two things at once and they are in tension:
> it is Furina's deferred Block, absorbing after Block and before HP, and it
> is the currency she spends to direct the Stage. The Salon is a board of
> members in the Defect-orb shape — a fixed company of slots, deployed by her
> cards, offering a range of effects across damage, Block, scaling and, at
> high rarity, energy. **Members do not auto-play.** They perform when
> something makes them perform, and there are three things that do. **A
> Companion card play triggers one member's effect, rotating** — the front
> member performs, then goes to the back, so a run of Companion plays walks
> the company; if the Salon is empty, a Companion play does nothing extra.
> **Most deploy cards make the member they deploy perform once immediately**,
> and **deploying onto a full stage Evokes the front member** to make room.
> **Furina's own cards Evoke**, which expends the member and pays either much
> stronger Fanfare scaling or an alternative effect the trigger never gives;
> her cards also read the Fanfare meter directly, and she keeps her existing
> cards that add Companion cards to her deck.
>
> **Fanfare is the Focus analogue and it is also her Burst.** It scales every
> member numeric, it is minted only by a member performing — a trigger mints
> the small amount, an Evoke the larger — and it decays every turn. **A full
> meter is its own payoff: a maximally scaled Salon.** There is no Burst card
> printed at a threshold, no overdrive, and no temporary bonus. Decay applies
> at every value including the cap, so a juiced meter has to be kept juiced by
> performing, and that is the intended tension. **"Drain the meter for a giant
> effect" is a Rare payoff card, drafted, not base kit** — Furina's Burst does
> not need to be a card in itself.
>
> **The separate Burst meter is retired for Furina.** `burst_max: 70`
> (`tier0/content/characters/furina.yaml:25`, R17) goes, and with it every
> Furina-side feed of it: `BURST_PER_SKILL_TAG = 5`
> (`tier0/constants.py:129`), `BURST_PER_REACTION = 5` (`:130`),
> `SALON_TICK_BURST = 2` (`:379`) and `BURST_PER_ENCORE_SPENT = 1` (`:381`).
> E4 §3 retirement item 7 named the same four constants for the same reason
> and that list is carried over here. The centered-overhead creature-space
> slot — the cross-character Burst indicator (`LAW.md:508-510`) — renders
> Fanfare for Furina, which is one gauge where there were two.
> `let_the_people_rejoice` is disposed of by pick **F11**.
>
> **One clause this does NOT narrow.** `LAW.md:64-66` — "Reaction credit —
> damage attribution and Burst energy — goes to the triggering player" — is
> **untouched**. E4 had to narrow it per-character because its merged meter
> would have been fed by a teammate's reaction; here Furina has no Burst meter
> for a reaction to feed, so the roster-wide clause stands as ratified.
>
> **Scope, stated so it is not over-read.** The roster-wide retirement of the
> shared Burst meter is **RULED** ([USER], 2026-08-29: "Yeah, agreed on the
> Burst changes") and is **packeted separately** on branch `burst-retirement`
> (`review/active/burst-retirement-2026-08-29.md`): each character's signature
> resource becomes her gauge, and each former Burst becomes a drain or
> overdrive of that resource. **Furina's fold here is the last of the three**
> — R220 B sequences the folds Kokomi → Klee → Furina, with the shared
> retirement landing last of all. It is not a carve-out from a standing rule
> but the closing case of a ruled roster-wide change. **This packet still decides Furina only**; Klee's
> and Kokomi's bodies belong to that packet and nothing here fixes them.
>
> **What this RETIRES from the E4 packet.** E4's fold of Fanfare into the
> Burst meter and everything downstream of it: the retirement of
> `FANFARE_DECAY_FRACTION` and `FANFARE_CAP_FRACTION`; the orphaning of
> `SALON_FOCUS_PER`; the single-cause "only a Featured performance creates
> Fanfare" rule; the Featured-entitlement tokens; the two-lane persistent
> Spotlight; and the per-character narrowing of `LAW.md:64-66`. E4's §3 ruling
> text, §4 architecture, §7.1 reader triage and §12 build contract are
> superseded in full. **`M52` is re-pointed at this packet's countersign
> items.**
>
> **What this RETIRES from the kickoff and from LAW.** The kickoff's automatic
> Salon — "off-field Hydro application engine … with HP-drain overdraw" (§5) —
> is retired as an automatic engine: the application still happens, but only
> when a member is triggered, deployed-and-performed, or Evoked. The kickoff's
> and LAW's dry-overdraw sentence never described the shipped engine and is
> corrected as hygiene rather than retired as design (§2.7c). LAW's Fanfare
> generation legs — "HP lost / Encore spent / Encore absorbed / Spotlighted
> card played" — are replaced by performance, and the design invariant "every
> point of damage past Block prints exactly 1 Fanfare" is retired with them,
> along with the test that asserts it.
>
> **What this KEEPS.** `FANFARE_DECAY_FRACTION = 0.20` and proportional decay;
> the Focus term `SALON_FOCUS_PER = 10` and its live reader; the Fanfare cap
> as a fraction of max HP; all three shipped Salon verbs (`salon_bow`,
> `salon_rotate`, `salon_perform`) and the FIFO queue they share; the
> full-stage displacement bow, which is already the Evoke this design names;
> the slot cap as a per-player stat raised by a drafted card; Encore unbounded,
> absorbing after Block and before HP, crediting A4 and never A3; and the four
> Guest Star guardrails.
>
> **What this leaves DELIBERATELY UNRESOLVED.** Spotlight. E4 proposed to
> reframe it and this packet does not, because the brief does not mention it
> and because [USER]'s three framing questions are about the Salon, Companions
> and Furina's own kit. Spotlight ships as it is — two modes,
> `SPOTLIGHT_BASE_MULT = 1.5`, the selector card, the relic — and E4's
> evidence that the mode choice has collapsed to a rule (§2.2) stands
> unanswered. **That is a known open hole, named so it is not mistaken for a
> decision.** The 18 `spotlight` rows are untouched by this packet.
>
> **Co-op.** An ally's Companion card play triggers Furina's stage exactly as
> her own does: one member performs and rotates, and an empty Salon does
> nothing extra. This restores an ally-coupled mechanic that E4 removed and
> did not replace, and it is the support-protagonist fantasy the character is
> for. Its real cost is stated rather than discovered: an ally playing three
> Companions has rotated Furina's queue three times without asking, and the
> member she was saving to Evoke is now at the back.
>
> **R177 and R213.** R177's ruled direction was "rebalance the weak plans, NOT
> B1 (fold plans into salon)". This packet is not B1: three named mechanics
> survive with distinct jobs. R177's measured finding that the stage outruns
> its fuel stands and constrains §4.2 — with the automatic upkeep gone, the
> fuel problem changes shape rather than disappearing. R213's sequence
> (Kokomi → Klee → Furina) and the standing freeze on `W10`/`W11` are
> untouched; the Furina slice opens on this countersign.
>
> **The animation contract.** All three contracted binding points survive.
> **Salon = 3 slot-index-keyed slots, duplicates legal** — the trigger's
> rotate is a re-render of the same three indices, which is precisely what the
> shipped `salon_rotate` already does. **Encore-absorbs-before-HP** —
> unchanged; Encore gains a second job, it does not lose its first.
> **Spotlight-is-a-designation-event** — untouched, because Spotlight is
> untouched. The centered-overhead Burst indicator keeps its contract and
> renders Fanfare.

### 3.1 LAW text this needs — PROSPECTIVE, under R213 quarantine

Nothing here is applied. It is drafted so [USER] can see what he would be
signing, and it is `C2`. Four items, and only the second is a real amendment.

**Amendment 1 — the Fanfare generation legs** (`LAW.md:195-207`). The current
bullet names the four live legs as "HP lost / Encore spent / Encore absorbed /
Spotlighted card played" and calls "every point of damage past Block prints
exactly 1 Fanfare" a design invariant. Prospective replacement for those two
sentences:

> Fanfare is minted by the Stage performing, and by nothing else: a member
> triggered by a Companion play mints the small amount, a member Evoked by
> Furina's own card mints the larger one, and a deploy that performs its own
> member mints as a trigger does. Encore spent, Encore absorbed, HP lost and a
> Spotlighted card played mint no Fanfare. Generation remains activity-based
> and never passive, and the no-per-turn-trickle ban is unchanged; what
> changed is which activity counts.

Everything else in the bullet stands: the cap at a fraction of max HP, the
floor verb, `Fanfare Cap +X` as an available explicit verb, and Fanfare as a
global pool on Furina.

**Amendment 2 — Furina's kit-Burst. This is the one that actually amends
LAW.** `LAW.md:266` requires of *every* playable character a "talent-relic +
kit-Burst", and `LAW.md:176-178` states the Burst is kit and not loot: "never
draftable, granted to hand on meter fill, casting empties the whole meter,
re-granted on refill, carries Retain." **That clause requires a castable
kit-Burst card, not merely a Burst meter** — so folding Furina's Burst into
Fanfare and moving the drain onto a drafted Rare is a LAW amendment and not an
implementation choice. Note also `LAW.md:481`, which requires every meter to
carry a bounded/unbounded property with its cap read from `constants.py` and
lists both `fanfare` (bounded) and `burst` (unbounded) — with Furina's Burst
gone, her row in that list is `fanfare` alone, which the clause already
permits. Prospective text, added as a scoped sentence rather than a rewrite:

> **Furina's kit-Burst is her Fanfare meter, and a drain is loot.** She ships
> no kit-Burst card: Fanfare is both her Focus term and her Burst resource, a
> full meter is its own payoff, and the "drain the meter for a giant effect"
> card is a drafted Rare rather than kit. Her centered-overhead indicator
> renders Fanfare. This is scoped to Furina and amends the template's
> "talent-relic + kit-Burst" requirement for her alone. **This is transition
> text and nothing more:** the roster-wide retirement of the kit-Burst
> (`review/active/burst-retirement-2026-08-29.md` §3.2, R220 B) supersedes this
> scoped amendment, and under R220 B's order Furina's fold lands last — so by
> the time this sentence would activate, the other characters' folds have
> already landed and no character still ships a kit-Burst.

*(Hygiene, 2026-08-29: the sentence previously ended "every other character
ships a kit-Burst unchanged", which R220 B's sequence makes false at the moment
this text would activate. Rewritten in place under the hygiene norm; the
amendment's substance is unchanged.)*

**One line on scope, because it will be asked.** The roster-wide retirement of
the shared Burst meter is RULED ([USER], 2026-08-29) and is packeted separately
on `burst-retirement`; **Furina's fold is the last of the three** (R220 B's
order: Kokomi → Klee → Furina, shared retirement last). The
amendment above is written Furina-scoped anyway, so that this packet can be
signed on its own schedule and the roster-wide text replaces it cleanly rather
than the two having to be unpicked from each other.

**Amendment 3 — the Salon overdraw sentence.** Not a design change: LAW's
Encore bullet says "overdraw drains true HP", which is true of Encore
absorption and false of the Salon (§2.7c). The prospective fix is to scope the
clause to Encore explicitly and leave the Salon's dry rule to the constant.
**Hygiene, and it could be a normal commit**; it is listed under `C2` only
because it sits in a bullet [USER] is being asked to read anyway.

**Amendment 4 — what Fanfare is allowed to scale. PROSPECTIVE, DRAFT,
UNCOUNTERSIGNED.** Drafted 2026-08-29 in response to external review relayed
by [USER] (their own GPT chat, no seat authority), which observed that "+1 to
every member numeric" (`SALON_FOCUS_PER`, §4.5) has no exemption written
anywhere and so already reaches Chevalmarin's Encore refund today — before any
energy member is added. The packet recorded that objection at `F1` and did not
settle it; this is the settlement offered for countersign. Prospective sentence,
added to the Fanfare bullet alongside amendment 1:

> **The Focus term scales performance numerics only.** Fanfare scales only
> those values a member's row explicitly designates as performance numerics —
> its damage and its Block. It never scales Energy, Encore, Charge, Fanfare
> itself, card generation, or the number of aura or status stacks a member
> applies.

**Why this wording rather than the relayed one.** The relayed draft read
"Fanfare scales only each member's explicitly designated performance values. It
never scales Energy, Encore, Charge, card generation, or aura counts." The
substance is kept; three things are tightened against the packet's own terms.
"Performance **numerics**" is the term §4.5 and `F8` already use
(`SALON_FOCUS_PER` = "+1 to every member numeric", `:252`), so the invariant
and the constant's own gloss say the same word. The permitted set is named
positively (damage and Block) rather than left to the designation, so a new
member row cannot quietly designate an Encore refund as a "performance value".
And **Fanfare itself** is added to the exclusions, which the relayed list
omits: §4.1's mint is already positive feedback, and a Focus term that scaled a
member's Fanfare mint would compound it. §4.5 carries the per-member
consequences.

---

## 4. The subsystems

§1.1a settled Fanfare generation, deploy tempo, the empty-stage rule, the
Burst's shape and co-op. Those are stated below as RULED and carry no picks.
What remains open is stated as numbered picks, **Claude's recommendation
always item (1)**.

### 4.1 Fanfare generation — RULED

**A member performing mints Fanfare. Nothing else does.** A trigger mints the
small amount; an Evoke mints the larger; a deploy that performs its own member
mints as a trigger does. Deliberate Encore spend mints nothing by itself — it
mints through the performance it buys.

All four shipped legs retire: `FANFARE_PER_HP_LOST` (`:240`),
`FANFARE_PER_ENCORE_SPENT` (`:241`), `FANFARE_PER_ENCORE_ABSORBED` (`:242`)
and `FANFARE_PER_SPOTLIGHT_CARD` (`:259`). With them goes the "all Encore loss
is progress" invariant and
`test_every_point_past_block_prints_exactly_one_fanfare`.

**Why this is the right cause, restated for the record.** Fanfare scales the
members and the members mint Fanfare when they perform, so the loop closes on
itself and the player's lever is *how often the stage performs* — which is
Companion density, deploy cards and Evoke cards, all draft and sequencing
decisions (D2: acquisition, conversion and timing are steerable). It is the
answer to "what is the payoff for Featured?" turned into "what is the payoff
for playing the board?" It is a positive feedback loop, and the decay in §4.5
is its brake; the two are a single design and neither is sound without the
other.

**The two small/large amounts are prototype seeds**, not derived values, and
they wait on the slice. Their *ordering* is ruled: trigger < Evoke, because
Evoke costs a member.

### 4.2 The Salon redraft — roster, size, and the deploy rules

**Deploy tempo and the empty stage — RULED.** Most deploy cards deploy a
member **and** make that member perform once immediately, so the card does
something on the turn it is played. Deploying onto a full stage **Evokes the
front member** to make room — which, as §2.2 shows, is the shipped
displacement bow at `effects.py:1436-1438` under a new name. A Companion
played with an empty Salon **does nothing extra**, and under D4 that must be
visible: the engine already emits `salon_perform_whiffed` and
`salon_rotate_whiffed` for exactly this, so the machinery is a display
question and not a rules one.

That trio does more work than it looks. It gives deploy cards immediate value
(the tempo problem), it makes the third slot matter (overcrowding is now a
decision with a payoff rather than a loss), and it gives the player a second
way to Evoke without drafting an Evoke card — which matters at the starter,
where there is one.

**The roster.** [USER] named the shape: "damage / block / scaling / (at high
rarity) energy, just like Defect does". Today's three cover damage, Block and
aura-application; there is no scaling member and no energy member. The redraft
also has to give each member **two** effects — a trigger effect and an Evoke
effect — where today each has a tick and a bow, which is very nearly the same
thing.

| member | trigger effect | Evoke effect (expends) |
|---|---|---|
| Crabaletta | Hydro damage to a random enemy | a large single hit, scaling hard on Fanfare |
| Usher | Block | a large Block, scaling hard on Fanfare |
| Chevalmarin | small damage **and** applies Hydro | Hydro to ALL enemies **and** refunds Encore — an *alternative* effect rather than a scaled one |

Chevalmarin is the template for "alternative effects": her Evoke is not a
bigger version of her trigger, it is a different shape. That is the texture
the brief asks for, and one member already has it.

**The two gaps.** A *scaling* member — one whose trigger makes the next
member's performance bigger, or that grows itself each time it performs — is
the Plasma-shaped hole, and it is the member that makes a deep stage worth
building rather than a wide one. An *energy* member at high rarity is the
second, and it needs care: it is a per-turn energy faucet on a board, the most
dangerous thing in this packet. Rare, one member, and probably a conditional
trigger.

**Keep the roster small.** Three today; five is the ceiling this packet
recommends. A member is not a card — it is permanent board vocabulary the
player must learn and the display must render, and the legibility argument
dies at seven.

**Size and the cap lever.** `SALON_MEMBER_SLOTS = 3` with `salon_cap_up` as
the Capacitor analogue, and **exactly one card in the pool raises it**
(`casting_call`, `:104-105`). Under the reframe the slot count means something
different: with an automatic tick, slots are throughput; with
trigger-and-rotate, slots are *variety* — how many different effects one
Companion run walks through — and now also *headroom*, since a full stage
means the next deploy Evokes. R177's "the stage outruns its fuel" finding
(four slots measured worse, 16.7% → 14.7%, because half of all upkeeps arrived
unfunded) was measured on the automatic tick; with no upkeep there is no
unfunded upkeep, so it does not transfer directly. That argues for the cap
lever being *more* draftable, not less.

**Picks — F1. The member roster.**

1. **Five members: the three existing, re-specified as trigger-versus-Evoke,
   plus one scaling member and one Rare-gated energy member.** *(Claude's
   recommendation.)*
2. Four: the three existing plus a scaling member. Energy deferred until the
   scaling member has been played, on the grounds that an energy faucet on a
   board is the riskiest thing here and should not arrive with an untested
   loop underneath it.
3. Three: re-specify the existing three and add none. The redraft is the
   trigger/Evoke split alone.
4. Six or more, with a member pool the draft samples from rather than a fixed
   cast.

**Picks — F2. Slot count and the cap lever.**

1. **Slots stay 3; `salon_cap_up` gains a second carrier at uncommon so the
   Capacitor analogue is actually draftable.** *(Claude's recommendation.)*
2. Slots stay 3 and the cap lever stays one common card, unchanged.
3. Slots drop to 2 with the cap lever more common — a smaller default board
   with growth as the payoff, which sharpens both "which member is front" and
   the deploy-Evokes rule.
4. Slots go to 4 by default. Explicitly note that this is the change R177
   measured as worse, under an upkeep rule that no longer exists.

### 4.3 The trigger rule

The mechanism ships as a pair — `salon_perform` then `salon_rotate` — which is
literally what `change_the_bill` does today (`:472-473`). The trigger is that
pair, fired by a hook on Companion play rather than by a card.

**Which member.** Front, then rotate to the back. That is the FIFO end every
other Salon verb already uses — `salon_bow` takes leftmost, a deploy into a
full stage displaces leftmost — and the docstring's reason for choosing
leftmost is that "the player already knows which member is next out, because
the deploy rule taught them" (`effects.py:1908-1917`). One order, one lesson,
and under §4.2's full-stage rule the deploy teaches it harder than before.

**The §2.7b constraint bites here.** On a one-member stage, rotate is a no-op
and the same member is triggered every turn forever. Not a bug — it is the
honest early-game state — but it means **no design element may price itself on
the rotation**. Rotation buys variety on a full stage and nothing at all on a
stage of one, and a body priced only against a three-member stage is unpriced
against the board a starter deck actually has.

**How many per Companion play.** Once. A Companion that triggers twice is a
Companion doing Furina's job, and the delete-test (LAW: deleting Furina's
cards from a winning deck must gut it) gets harder the more the Companion half
runs itself.

**Picks — F3. Which member the trigger performs.**

1. **The front member performs, then rotates to the back.** *(Claude's
   recommendation — one queue, one order, and the deploy rule already teaches
   which end is which.)*
2. The front member performs and does **not** rotate; rotation stays a card
   verb the player pays for. The stage becomes a thing you aim deliberately
   rather than a wheel that turns.
3. The player chooses which member performs on each Companion play. Maximum
   control, a modal on every Companion play — a real click-count cost and a
   co-op latency question.
4. A random member performs. Cheapest to build, and it fails D2.

**Picks — F4. How often the trigger fires.**

1. **Once per Companion card played, unbounded per turn.** *(Claude's
   recommendation — the bound is your hand, a resource the player already
   manages.)*
2. Once per Companion played, capped at N per turn, so a Companion-flood turn
   cannot walk the whole company twice.
3. Once per turn regardless of how many Companions are played — which makes
   Companion density worthless past the first card, and is listed only so it
   is rejected explicitly.

### 4.4 The Evoke rule

**Which member.** The front, again — `_op_salon_bow` already takes leftmost
and calls itself "the Defect-evoke analogue". Using the same end for trigger,
Evoke and full-stage displacement is what makes `salon_rotate` the single
aiming verb for all three, and that property is what keeps the two hooks
complementary rather than two systems to track.

**What "much stronger Fanfare scaling" means as a shape.** Today the Focus
term adds `held_fanfare // SALON_FOCUS_PER` to every member numeric,
identically for tick and bow. Three shapes for making Evoke scale harder, and
the pick is between shapes rather than numbers:

- a **steeper rate** — Evoke reads at a smaller divisor, so the same held
  meter buys twice the bonus;
- a **multiplier** — Evoke adds the same Focus term N times, keeping one
  divisor and one number to explain;
- a **different base** — Evoke's printed number is already large (14 against a
  6 trigger today) and Fanfare scales it proportionally rather than additively.

The multiplier shape is the legible one: there is a single Focus number on
screen, the trigger uses it once and the Evoke uses it N times, and the face
prints "×3" without the player doing division.

**Alternative effects.** Chevalmarin already has one, and it is the better
texture. At least one member in the final roster should Evoke into a *shape
change* rather than a bigger number, because D8 says archetypes differ in how
turns unfold and not in the label on a bigger number — and a board where every
Evoke is "the same thing but bigger" is exactly the failure D8 names.

**The Encore price.** The `encore_cost` field exists and gates cards, and
exactly two rows use it (`:299`, `:539`). Evoke cards should pay it: Encore is
the direction currency in [USER]'s own sentence, and spending it to Evoke is
precisely "spent down to direct the Stage via Evoke-style plays". This is also
where D3 bites — an Evoke that pays a big Block *and* advances the engine at
full rate without a binding cost is a subsidy, and the Encore price is the
binding cost.

**Picks — F5. Which member Evoke expends.**

1. **The front member — the same end as the trigger, the same end
   `salon_bow` takes, and the same end a full-stage deploy displaces.**
   *(Claude's recommendation.)*
2. The player chooses. More control, a modal on every Evoke, and it breaks the
   "one order, one lesson" property that §4.2's full-stage rule now depends on.
3. Evoke takes the *back* member, so trigger and Evoke consume from opposite
   ends. Interesting, and it doubles what the player must track.

**Picks — F6. What "much stronger Fanfare scaling" means.**

1. **A multiplier on the same Focus term — Evoke applies it N times where the
   trigger applies it once, with N printed on the face.** *(Claude's
   recommendation: one divisor, one number on screen.)*
2. A steeper rate — a second, smaller divisor for Evokes. Two numbers to
   explain.
3. Proportional scaling on the Evoke's larger printed base. Biggest ceiling,
   hardest to forecast off a face.
4. No extra scaling: Evoke is distinguished purely by alternative effects, and
   Fanfare scales trigger and Evoke identically.

**Picks — F7. The Encore price on Evoke.**

1. **Every Evoke card carries a printed `encore_cost`, varying by card.**
   *(Claude's recommendation.)*
2. Evoke costs Encore only on the cards that also pay Block, so the D3 price
   lands exactly where the subsidy would be.
3. Evoke costs energy only; Encore stays purely a defensive buffer and "spend
   it to direct the Stage" moves onto a different family.

### 4.5 Fanfare as Focus, and as the payoff

Both halves ship. `SALON_FOCUS_PER = 10` adds +1 to every member numeric per
10 held Fanfare, read live at `effects.py:1365`. `FANFARE_DECAY_FRACTION =
0.20` decays the held meter proportionally. Neither needs building; both need
setting against each other, which is the actual work.

**What "every member numeric" is allowed to mean — the scaling invariant.
PROSPECTIVE, DRAFT, UNCOUNTERSIGNED** (§3.1 amendment 4; drafted 2026-08-29
against external review relayed by [USER], no seat authority). As written,
`SALON_FOCUS_PER` scales *every* number a member produces, and neither §4.2 nor
`F8` exempts anything — so it already reaches Chevalmarin's Encore refund
today, and it would reach an energy member's payout the moment `F1` seats one.
The proposed invariant:

> **The Focus term scales performance numerics only.** Fanfare scales only
> those values a member's row explicitly designates as performance numerics —
> its damage and its Block. It never scales Energy, Encore, Charge, Fanfare
> itself, card generation, or the number of aura or status stacks a member
> applies.

**What it excludes, member by member, against the §4.2 roster:**

| member | scaled by Focus | **excluded** |
|---|---|---|
| Crabaletta | trigger damage; Evoke's single hit | — (nothing on this row is off-limits) |
| Usher | trigger Block; Evoke's large Block | — |
| Chevalmarin | trigger's small damage | the **Hydro application** on the trigger (a stack count, not a numeric); on the Evoke, the **all-enemy Hydro application** and the **Encore refund** — this is the one live row the invariant changes today |
| scaling member (`F1`, prospective) | any damage or Block it prints itself | its **buff to another member's performance** — a modifier is not a performance numeric, and Focus scaling the modifier would apply Focus twice to the same hit |
| Rare energy member (`F1` opt. 1, prospective) | any damage or Block it prints | its **energy payout**, entirely — which is the objection's specific point, and it is what makes `F1` option (1) survivable rather than an unbounded faucet |

Card bodies are out of scope: this binds the Focus term applied to *member*
performances, not what a drafted card does with the meter (§4.6's drain reads
the held value directly and is unaffected).

**The arithmetic, and the ceiling problem.** The Fanfare cap is
`FANFARE_CAP_FRACTION × maxHP` = 0.5 × 78 = **39**, so the Focus term reaches
**+3** and stops. **There is no separate Focus cap constant** — `:372`'s
"+3 / +4" is a comment (§2.1). And **no card in the pool raises the Fanfare
cap**: `raise_fanfare_cap` appears on zero rows (§2.4). So today a maxed
Fanfare meter is worth +3 to every member numeric, full stop, and there is no
way to want more.

Under §1.1a item 3 that number *is* the payoff, which raises the question
directly: is +3 enough? On today's members it takes Crabaletta's trigger from
6 to 9 and, at an Evoke multiplier of ×3 (F6 pick 1), her Evoke from 14 to 23.
That is a real, felt difference and it is defensible as a seed — but it is a
ceiling reached by a meter that then has nowhere to go, and "nowhere to go" is
where the never-drain playstyle stops being interesting. **This is F9.**

**Decay applies at the cap — RULED by [USER]'s stated tension.** A juiced
meter needs steady performing to stay juiced; that is the point. Proportional
decay at 20% means a meter at 39 loses about 8 a turn and one at 10 loses 2:
the brake tightens as the meter grows, which is the right shape against §4.1's
positive-feedback mint, and it means holding the cap costs roughly eight
Fanfare of re-earned performance every turn. That is a real throughput demand
on the stage, and it is what keeps "maxing the meter is its own payoff" on the
right side of D2 (§2.6).

**The decay preview is a D4 obligation, not a nicety.** A player deciding
whether to Evoke now or next turn is deciding against a number that will be
smaller next turn by an amount they cannot compute in their head. §4.7 carries
it.

**Picks — F8. The Focus scaling shape.**

1. **Keep the shipped shape: +1 to every member numeric per `SALON_FOCUS_PER`
   held, additive, applied once on a trigger and N times on an Evoke per F6.**
   *(Claude's recommendation — it ships, it is tested, and it is the Defect
   grammar [USER] named.)*
2. Per-member-type rather than flat, so the scaling member scales faster than
   the Block member. More texture, more to read.
3. Proportional rather than additive (+10% per `FOCUS_PER`), which scales
   high-rarity members harder for free and makes forecasting worse.

**Picks — F9. The Fanfare ceiling, now that the ceiling is the payoff.**

1. **Keep `FANFARE_CAP_FRACTION = 0.5` (a cap of 39, Focus +3) as the
   prototype seed, and give the pool one or two `raise_fanfare_cap` carriers
   so a deck that wants a higher ceiling can draft one.** *(Claude's
   recommendation — the verb exists, the op ships at `effects.py:1863`, LAW
   already calls `Fanfare Cap +X` an available explicit verb, and it turns a
   dead ceiling into a build decision.)*
2. Raise `FANFARE_CAP_FRACTION` outright so the base ceiling is higher, and
   add no carriers. One constant moves, nothing is drafted.
3. Keep the cap at 0.5 and add no carriers: +3 is the ceiling, permanently,
   and the never-drain line tops out early by design.
4. Lower `SALON_FOCUS_PER` instead, so the same cap buys more Focus tiers —
   more granularity, and a number the tooltips already interpolate.

**Picks — F10. The decay rate seed.**

1. **Keep `FANFARE_DECAY_FRACTION = 0.20` as the seed and measure before
   moving it.** *(Claude's recommendation — it is the shipped value, and
   moving it is a `CONSTANTS_VERSION` event that buys nothing before the slice
   runs.)*
2. Lower it (10–15%), because the automatic tick that used to feed the meter
   is gone and the meter now climbs more slowly, so 20% may outrun it.
3. Raise it, or make it flat-per-turn rather than proportional, to sharpen the
   pressure on holding a full meter.

### 4.6 The Rare drain card

§1.1a item 3 removes the Burst card, the threshold, the overdrive and the
loan. What replaces them is smaller and better placed: **a drafted Rare that
drains the whole Fanfare meter for a giant effect.**

**Why the Salon rare tier is the right home.** `salon` has **2 rare rows**
against 15 uncommon (§2.4) — the thinnest rare tier of the four archetypes,
and a hole that predates this packet. A drain card is exactly the shape a Rare
should be: it needs a full meter to be worth drafting, it is a decision the
player makes once per fight at most, and taking it changes how the whole deck
is played (it converts the never-drain line into a build-to-a-moment line).
One or two candidates, no more — a third makes draining the default and the
never-drain line dies.

**What it does with the meter.** It reads the *held* Fanfare, not a threshold:
the card is playable at any value and its payoff scales with what you have, so
there is no gate to be locked out by and no "grant on fill" machinery. That is
also what keeps it loot rather than kit under the amended LAW clause (§3.1
amendment 2): it is drafted, it is not granted, and casting it is not the only
thing the meter is for.

**`let_the_people_rejoice` is the obvious raw material and also the obvious
casualty.** It is rare, cost 0, `kit_card: true`, `requires:
burst_energy_full`, and its body is already 8 AoE damage with a
`1_per_4_fanfare` bonus plus 6 Encore (`:836-838`). It already reads Fanfare.
What has to go is `kit_card`, the `burst_energy_full` gate, and the cost of 0
— a drafted Rare that drains a meter is not a free card. It is also the one
Furina row codegen cannot generate ("intentionally hand-written kit
machinery", STATE), so re-authoring it as an ordinary drafted row would
plausibly *close* that block and take Furina's manifest to 84 of 84. That is a
real secondary benefit and it is why the recommendation is re-author rather
than retire.

**Picks — F11. What happens to `let_the_people_rejoice`.**

1. **Re-author it in place as the Rare drain card: drop `kit_card` and the
   `burst_energy_full` gate, give it a real cost, keep the name and the art,
   and scale its body off the whole drained meter.** *(Claude's
   recommendation — it keeps a name [USER] already approved, it reuses the
   art, and it plausibly closes the last codegen block on Furina's sheet.)*
2. Retire the row entirely and author a new Rare drain card with a new id and
   new art. Cleanest lineage, an art ask, and the codegen block stays.
3. Keep `let_the_people_rejoice` as a kit card with its cost of 0, re-gated on
   Fanfare rather than Burst — which preserves a kit-Burst in all but name and
   makes LAW amendment 2 unnecessary. Listed because it is the minimal-change
   option and because it is the one [USER]'s own words argue against.

**Picks — F12. How many drain cards, and what shape.**

1. **Two: one that drains for damage and one that drains for Block or
   survival, so the drain is a plan and not a single card you either see or
   do not.** *(Claude's recommendation.)*
2. One drain card only. Tightest, and it makes the whole build-to-a-moment
   line depend on a single Rare.
3. Two, but one of them at uncommon so the plan is reachable without a Rare —
   note this makes draining much more common and puts the never-drain line
   under real pressure.

### 4.7 Legibility — what the player actually sees

[USER]: "this needs to be obviously legible to the player." D4 makes it a
defect if it is not; D9 makes it a starter obligation.

**The deploy card face.** A deploy card puts a member on the board, and that
member has two effects the player will never see printed anywhere else. Under
§4.2 the card now also performs the member and may Evoke another one, so the
face is carrying three rules. That is genuinely a lot of text and it is the
sharpest D5 tension in the packet — the honest framing is that a deploy card
is the character's vocabulary lesson, and the alternative is a keyword the
player has to hover.

**The state display, per member.** Each occupied slot must show which member
it holds, what its trigger does *at the current Focus value*, and which one is
front. The mod already interpolates the constants into displayed strings since
`EB-86`, so a repricing moves the constant and the tooltip follows; that
machinery is the right one and it extends.

**The Fanfare meter.** A number, its Focus tier (+1 / +2 / +3), and next
turn's value after decay. Without the preview, an Evoke-now-or-later decision
is made against an uncomputable number, which is an invisible feed under D4.
The meter now also *is* the Burst gauge, so it renders in the centered-overhead
creature-space slot (`LAW.md:508-510`) — one gauge where there were two, and
not a new binding point.

**Picks — F13. What a deploy card face prints.**

1. **Both member lines — trigger and Evoke — in full, plus the perform-on-
   deploy clause. The full-stage Evoke rule is a character rule shown in the
   Salon keyword, not reprinted on every deploy.** *(Claude's recommendation:
   D4 permits a character rule as the carrier, and reprinting it on ten cards
   is what makes the faces unreadable.)*
2. The trigger line in full, the Evoke line as a keyword with detail in the
   member's board tooltip. Shorter faces, one hover.
3. Neither member line on the card: the deploy names the member and the
   member's board entry carries both. Shortest faces, most hidden.

**Picks — F14. The per-member state display.**

1. **Each slot shows the member, its trigger effect resolved at the current
   Focus, and a front-of-queue marker.** *(Claude's recommendation.)*
2. As (1), plus the Evoke effect resolved at current Focus — everything
   visible, a busier board.
3. Member identity and front marker only; numbers on hover.

**Picks — F15. The Fanfare meter.**

1. **Current value, Focus tier, and next turn's value after decay, rendered in
   the overhead Burst slot.** *(Claude's recommendation.)*
2. Current value and Focus tier only; decay explained once in the keyword and
   not previewed. Cleaner, and it fails the D4 forecast test.
3. As (1) plus turns-to-cap at the current performance rate. Most informative,
   most numbers, and the rate is a guess.

### 4.8 Co-op — RULED

An ally's Companion card play triggers Furina's stage exactly as her own does:
one member performs, then rotates; an empty Salon does nothing extra. Same
hook, different seat, no new machinery beyond a seat check.

This restores an ally-coupled mechanic. E4 retired both of Furina's — the
cross-player selector pass and partner-coupled Fanfare — and named the result
as a real loss against Appendix A.4's mandate that she have one; this is a
cleaner coupling than either, because it needs no partner-state plumbing and
it makes her board a thing the table interacts with.

The cost, stated: an ally can walk your queue. Under F3 (1) the front member
matters, so an ally playing three Companions has rotated your stage three times
without asking. That is real, it is the price of the coupling, and it is a
tension rather than a defect — but it is the first thing to watch in co-op
play.

Reaction credit (`LAW.md:64-66`) is untouched: a teammate's cross-player
reaction credits the triggering player exactly as today, and Furina's meter is
unaffected either way because reactions no longer feed anything of hers (§3).

---

## 5. The starter kit

Ten cards. D9's obligation is that the starter and the relic teach the central
verbs and one recurring tension from fight one. The reframe has three verbs —
**deploy → trigger → Evoke** — and the target is that all three fire inside
the first two turns.

What ships today (`tier0/content/characters/furina.yaml:49-59`): 3×
`soloists_solicitation` (Attack 1, 6 damage), 3× `stage_presence` (Skill 1, 6
Block), 1× `regal_bearing` (Skill 1, 3 Block + Weak 1), 1× `aria_of_recompense`
(Skill 1, gain 5 Encore), 1× `salon_debut` (Skill 1, deploy a **random**
member), 1× `an_invitation` (Skill 0, Exhaust, generate a common Companion).
Two of the ten are replaced at run start by the randomized Fontaine ensemble.

| verb | taught by | delta |
|---|---|---|
| **deploy** | `salon_debut` | **CHANGE the member to a named one, and add the perform-on-deploy clause.** A11 made it random on 2026-07-28 to separate the starter from the Common Surintendante Chevalmarin. Under the reframe, *which* member is on the board is the whole trigger decision, and you cannot plan around a coin flip (D2). The A11 separation is recoverable by making the Common the second copy of a named member rather than the only way to name one. The perform clause makes the card pay on the turn it is played, per §4.2. |
| **trigger** | `an_invitation` → any Companion | **NONE on the card.** It already generates a Companion, and playing that Companion is the trigger. The teaching is structural: deploy on turn 1, Companion on turn 2, watch the member perform. |
| **Evoke** | **ABSENT today** | **See F16.** No starter card Evokes, and the Encore-spender family `F3` does not exist — frozen in `Win11` behind the pilot's Encore opportunity-cost repair (STATE). |
| the tension | `aria_of_recompense` (gain 5 Encore) versus an Evoke card's `encore_cost` | The recurring tension D9 asks for, in one sentence: **hold Encore as Block, or spend it to Evoke.** |

**The Evoke question is a genuine pick and not an obvious add**, because §4.2
gave the starter a second route to the verb: with three slots and enough
deploys, deploying onto a full stage Evokes the front member without any Evoke
card at all. A starter with four deploys teaches Evoke by overcrowding. That
is elegant and it is slow — it takes four Salon cards to fire once — so the
trade is real.

**Picks — F16. How the starter teaches Evoke.**

1. **Add one cheap Evoke card with a printed `encore_cost`, displacing one
   copy of `stage_presence`.** *(Claude's recommendation — it is the only way
   the Encore tension appears in the starter at all, and D9 asks for the
   tension by fight one, not by fight four.)*
2. Teach Evoke by overcrowding only: add a second deploy card instead, and let
   the third deploy of a fight Evoke the front member. No new verb on a face,
   a slower lesson, and no Encore tension in the starter.
3. Both: one Evoke card and one extra deploy, at a cost of two of the ten
   slots. The fullest lesson and the largest starter change.

Under (1) the delta is **one parameter and one card**: `salon_debut` gains a
named member and the perform clause, and one cheap Evoke card joins the ten.
Eight of ten cards are unchanged, which is deliberate — the slice should be
about the new sentence, not a new deck. The relic is untouched by this section.

**Note against E4.** E4's §5.2a split the Encore spend into *two* cards (a
lane move and a command) because bundling them made graded lines ambiguous
about which verb was bought. That reasoning does not transfer: there is no
lane to move here, so Evoke is a single verb and one card isolates it cleanly.

---

## 6. The testable slice, under R213

### 6.1 Flags

The house convention is a compile-time MSBuild property plus an id prefix:
`dotnet build klee-mod/KleeCode -p:PrototypeCards=true`, every prototype row's
id starting `proto_`, and the classes not compiled at all in a release build
(`OPERATIONS.md`, "Prototype surface (`EB-147`)").

| flag | scope | default |
|---|---|---|
| `FURINA_REFRAME` | master; C# compile symbol under `-p:PrototypeCards=true`, sim-side a module constant in the reframe module, **not** in `constants.py` | OFF |
| `FURINA_REFRAME_MANUAL` | members stop auto-playing; the Companion-play trigger hook fires; deploy-performs and deploy-onto-full-Evokes | OFF |
| `FURINA_REFRAME_EVOKE` | the Evoke verb and its Fanfare multiplier; the Encore price through `encore_cost` | OFF |
| `FURINA_REFRAME_METER` | Fanfare generation moves to performance; the separate Burst meter and its four feeds retire | OFF |
| `FURINA_REFRAME_STARTER` | the §5 starter deltas | OFF |

**The honesty note, before any table is quoted.** Staging a prototype *card
row* bumps no stamp — prototype rows never enter tier0's card index. But
`FURINA_REFRAME_MANUAL` and `FURINA_REFRAME_METER` are **engine** behaviour,
and a default-off engine flag bumps no stamp only while it is off. **Turning
either on is a `CONSTANTS_VERSION` event**, and every number measured with a
flag on is measured in a new world, not comparable to the standing baseline
`review/active/sitting-reads-2026-08-26-c20-d18-p11.md`. Any landed step
re-baselines the whole twelve-arm table, not the three Furina rows (E4 §7).

### 6.2 The prototype rows

Small, and every one a `proto_` row that enters no pool:

1. **A named deploy with a perform clause** — `proto_salon_debut_named`, the
   §5 delta.
2. **An Evoke card** — cheap, `encore_cost` printed, Evokes the front member
   with the F6 multiplier.
3. **A second Evoke card with an alternative effect** — Evoking Chevalmarin
   into the all-enemy aura and the Encore refund, so the slice can ask whether
   "alternative" reads differently from "bigger".
4. **A drain card** — the §4.6 Rare, so the build-to-a-moment line has one
   live witness against the never-drain line.

None enters `docs/furina-cards.yaml`'s draftable pool, and the quarantine that
refuses a `KLEEMOD-PROTO_…` grant from outside a prototype build is proven
live on every release build since `0.2.1209` (STATE).

### 6.3 The prediction slate — SKELETON, predictions BLANK

Under R212, prediction slates are DRAFTED by Claude from written design intent
and committed before any run. **The slots are drafted here; the predicted
values are blank, because every one depends on a §4 pick that is [USER]'s.**
This slate is not countersignable until F1–F16 are answered; it is here so the
shape is fixed before the numbers are, which is the point of pre-registration.

**Slot 1 — does the board read as a board?**
*Predicted:* ⟨blank — depends on F3, F13, F14⟩.
*Falsified if:* blind forms describe the Salon as a passive that happens to
them rather than as something they made perform; **or** no form names which
member was front as a reason for a line taken.
*Decision it changes:* falsification returns F3 and F14 — either the
front-of-queue marker is not doing its job, or the trigger needs to be a
choice rather than a rotation.

**Slot 2 — is trigger-versus-Evoke a real decision?**
*Predicted:* ⟨blank — depends on F6, F7⟩.
*Falsified if:* `closeness` fails on a matched pair of boards built so that
Evoking now and triggering twice more are within one card of each other
(R213 F); **or** both graders take the same line on both boards.
*Decision it changes:* falsification returns F6 and F7 — the Evoke multiplier
is wrong, or the Encore price is not a real cost.

**Slot 3 — does Encore feel like two things?**
*Predicted:* ⟨blank — depends on F7, F16⟩.
*Falsified if:* no form names holding Encore as Block as a reason for
declining an Evoke, across a set of boards where holding is correct on at
least one.
*Decision it changes:* falsification returns F7 — Encore is not the right
currency for Evoke and the price moves to energy.

**Slot 4 — is a full meter felt as a payoff?**
*Predicted:* ⟨blank — depends on F8, F9, F10, F15⟩.
*Falsified if:* on a staged board at or near the cap, no form names the Focus
bonus as a reason for a line taken; **or** graders cannot say what the meter
is worth to them without being told.
*Decision it changes:* falsification returns F9 and F15 — either +3 is too
small to be its own payoff and the ceiling has to move, or the meter is not
legible enough for the player to price it.

**Slot 5 — is the never-drain line a real alternative?**
*Predicted:* ⟨blank — depends on F11, F12⟩.
*Falsified if:* on a staged board holding a full meter with a drain card in
hand, every grader drains; **or** graders decline and cannot say what they
gain by declining.
*Decision it changes:* falsification returns F12 — the drain card is
dominant, and either its payoff or the meter's standing value is mispriced.

**Slot 6 — is the Encore-spending Evoke family worth its price? — DRAFT,
unrun, added after the slate was drafted.** Prompted by external review
relayed by [USER] (their own GPT chat, no seat authority). Slot 2 matches an
Evoke against *triggering twice more*; nothing matches it against the **other**
way to Evoke. Under §4.2 a deploy onto a full stage Evokes the front member to
make room, and the ruled text prices that at nothing: the deploy Evokes the old
front, lands a replacement, and performs the replacement, all for the card's
energy. A dedicated Evoke card pays a printed `encore_cost` under `F7` pick 1,
expends the front, and puts nothing back — the stage comes out one member
lighter. If that asymmetry is as large as it reads, the family [USER]'s brief
calls central ("Encore … spent down to direct the Stage via Evoke-style
plays") is strictly inferior to a deploy card on every full stage.

*The matched comparison:* one staged board, full stage, both a full-stage
deploy card and a dedicated Evoke card in hand, built so the two lines are
within one card of each other on the turn.

*Predicted — DRAFT, derived from the ruled text, not blank:* a **majority of
blind graders take the deploy line**, and **no form names an advantage the
dedicated Evoke has** that the deploy does not (beyond aiming a specific
member, which `F5` pick 1 also denies it). This is a directional prediction
only; it is not countersignable until `F1`–`F16` are answered, like the five
slots above.

*Falsified if:* graders split on the pair, **or** any form names holding the
board size, the Encore spend, or the Evoke's alternative effect as the reason
the dedicated Evoke is the better line.

*Decision it changes:* confirmation returns `F7` and §4.2's full-stage rule
together — either the deploy's free Evoke has to carry a cost (Encore, or a
reduced performance), or the dedicated Evoke family needs something the deploy
cannot give it. Falsification retires the objection.

**Required boards, from §2.7b.** At least one staged board carries **exactly
one Salon member**, because that is the board on which rotation is a no-op and
any positional pricing is zero — and it is the board a starter deck actually
has. And at least one carries a **full stage with a deploy in hand**, because
the deploy-Evokes rule is new law and has never been played — and slot 6 asks
that same board to carry a **dedicated Evoke card in hand beside the deploy**,
so the two Evoke routes are read against each other on one turn.

**Who grades:** the Codex seat, blind, per `EB-149`, two graders per turn,
every graded line replayed per `EB-170`.

### 6.4 The whole-fight blind-play gate

Whole-fight blind play on a dev build is the **automatic** gate after any arm
ADVANCEs — `EB-188`'s door, accepted live. It is mandatory here for a reason
specific to this design: **every question this packet asks is a cadence
question.** Whether the stage performs often enough without a passive tick,
whether 20% decay outruns generation, whether a full meter arrives before the
fight is over, and whether the never-drain line is a plan or a theory — none
is answerable on a staged turn. Staged boards can only say whether a single
decision is legible and close. The reader migration (§7) does not begin until
a whole fight has been played blind.

Live blocker, noted: the installed build `0.2.1416+proto` does not boot, and
the last runnable install is the release package `0.2.1357` (STATE); the fix is
in flight on `kokomi-blind-run`. Nothing in this packet is gated on it, but the
slice's first live step is.

---

## 7. Blast radius under THIS design

A fresh census, not E4's triage. E4's §7.1 planned to CUT scalar `per Fanfare`
bodies by default, on the grounds that under a two-payment meter that empties
on cast, "the longer you wait the bigger this gets" is no longer a plan the
game supports. **Under this design it is exactly the plan the game supports.**
Fanfare is a held, decaying Focus meter that scales the whole board, so a
scalar `per Fanfare` body is a card that rewards a high held meter — which is
the never-drain playstyle's own payoff. E4's triage is superseded rather than
adopted, and the reason is a design change, not a change of mind.

**The 11 meter-reading rows** (§2.4, listed by id and line). All eleven
compile and all eleven read a meter that still means what it meant: a held,
decaying, capped non-negative integer. **The rate changes and the ceiling does
not.** With generation moved onto performance, the meter climbs when the stage
runs and stalls when it does not, so a `fanfare_at_least_N` gate opens on a
different schedule — later for a Companion-poor deck, earlier for a
Companion-rich one. A real repricing question, and a sheet edit, which is a
`CONSTANTS_VERSION` event under LAW's material-card-sheet-edit rule. It happens
**after** the architecture has a verdict.

One of the eleven is `let_the_people_rejoice` itself, which F11 disposes of
directly.

**The 30 `fanfare`-tagged rows.** Nineteen of the thirty are tagged fanfare
without reading the meter. Under E4 those became the "Conductor" bucket. Here
they need no bucket: they are cards about the flux cycle, and the flux cycle
survives — Encore still goes up and down, and now it goes down for a second
reason. No re-authoring is implied by the architecture. Individual rows may
still be bad cards; that is a sheet question, not a reframe question.

**The 26 `salon` rows — the expensive half, and larger than the Fanfare
side.** Every salon row was written against a board that acts by itself. The
power riders survive (`salon_deploy_block` `:684`, `salon_bow_block` /
`salon_bow_encore` `:595-596`), and so does anything keyed on deploying or
bowing — the deploy-performs and deploy-Evokes rules make those riders *more*
live, not less. What breaks is any row whose value is "you have members" rather
than "you make members act": a card that pays per member per turn pays nothing
per turn now. **No count is asserted here** — identifying which of the 26
depend on the automatic tick is a row-by-row read and the first task of the
migration step, not a claim this packet makes.

**The 18 `spotlight` rows.** Untouched. Spotlight is deliberately unresolved
(§3), so nothing here moves a Spotlight row, and the collapse-rule finding
stands open against them.

**The Burst surface.** Four constants stop applying to Furina
(`BURST_PER_SKILL_TAG`, `BURST_PER_REACTION`, `SALON_TICK_BURST`,
`BURST_PER_ENCORE_SPENT`) and `burst_max: 70` leaves `furina.yaml:25`. Note
that the first two are **roster-wide constants that other characters still
read**, so the change is a Furina-scoped guard, not a deletion — exactly the
distinction E4's item 7 drew. The kit list at `furina.yaml:29` empties, and the
codegen manifest's one blocked row is resolved one way or the other by F11.
Her Burst-gauge skin becomes her Fanfare gauge, which is a re-skin of a
contracted slot rather than a new binding point.

**Tests.** 37 test files reference salon, 32 fanfare, 18 spotlight across a
190-file suite; 16 / 10 / 6 pin the plan name as a quoted string literal (E4
§7). This design renames nothing, so the string-literal subset survives
mechanically — the expensive half of E4's blast radius does not apply. What
breaks is behavioural: every test asserting a member acted at turn start, and
`test_every_point_past_block_prints_exactly_one_fanfare`, which dies under §4.1
exactly as it did under E4 and for the same reason. Add to that every test
reading Furina's Burst meter.

**The re-baseline.** Any landed step is the whole twelve-arm table, never the
three Furina rows — "a bump makes every arm of the table discontinuous, for
every character" (E4 §7). Under R207 that is one window per step where
attribution matters, and here it does: the whole question is which of the three
mechanics the reframe fixed.

---

## 8. Independence and grading roles

- **[USER] authored the direction.** §1.1 and §1.1a are his, verbatim, across
  four messages. Every design call below them is a numbered pick returned to
  him.
- **Claude authored this packet.** Every row is `authored_by: [claude]`. There
  is no GPT-authored row in it — the doctrine seat has not seen it.
- **The Codex seat doctrine-gates this packet and grades Claude's rows**, and
  that happens **after** [USER] reads it, per the seat's scarcity: GPT-played
  runs are paced per five-hour window and a sitting plans around them rather
  than assuming them (STATE). Under R217 C independence is by model family,
  author against grader; Claude authoring and GPT grading satisfies it.
- **No fresh-Claude read is owed on this packet.** E4 needed one because the
  seat had authored rows inside it and cannot review its own text. Here there
  are no GPT-authored rows, so a fresh-Claude read would be Claude reading
  Claude — the "no third family" problem ([USER], 2026-08-29) — and buys
  nothing. If the seat later authors a row into this packet, the read becomes
  owed at that moment and not before.
- **`EB-190`'s authorship record applies:** whatever the seat contributes at
  the doctrine gate is recorded as its family on the row it touches, and a row
  the seat authored is re-derived Claude-side before Claude grades anything
  built from it — the repair pattern Klee round 3 established.

**The limit, stated rather than assumed.** The doctrine gate is independent of
the *statement* and not of the *implementation*. What it can catch is a
statement that contradicts LAW, contradicts another statement here, or names a
thing the shipped surface cannot show. It cannot certify that the build will be
right. That is what §6.4's whole-fight gate is for.

---

## 9. What returns to [USER]

### 9.1 The countersigns

**C1 — the §3 ruling text.** One signature covers the architecture, the fold of
Furina's Burst into Fanfare, the retirement list, the keep list, the co-op
rule, and the explicit statement that Spotlight is left unresolved. Signing C1
re-points `M52` from E4's C1–C3 onto this packet and supersedes E4's §3, §4,
§7.1 and §12 on paper.

**C2 — the prospective LAW text at §3.1.** Three items, PROSPECTIVE under
R213's quarantine. **Amendment 2 is the real one**: `LAW.md:266` requires
every character to ship a kit-Burst and `LAW.md:176-178` says the Burst is kit
and not loot, so moving Furina's drain onto a drafted Rare amends LAW rather
than merely implementing a design. The roster-wide retirement is RULED and
packeted separately on `burst-retirement`, and Furina's fold is the last of
the three (R220 B); this amendment is drafted Furina-scoped anyway so that C2 can be
signed on its own schedule and the roster-wide text replaces it cleanly.
Amendment 1 rewrites the Fanfare generation legs. Amendment 3 is hygiene and
can be signed independently.

### 9.2 The picks — one line each, recommendation is always (1)

| id | § | the question |
|---|---|---|
| **F1** | 4.2 | How many Salon members, and does the roster gain a scaling member and a Rare energy member? |
| **F2** | 4.2 | Do the slots stay at 3, and does the cap lever get a second carrier? |
| **F3** | 4.3 | Which member does a Companion play trigger — front-then-rotate, front-and-stay, player's choice, or random? |
| **F4** | 4.3 | How often may the trigger fire — once per Companion, capped per turn, or once per turn? |
| **F5** | 4.4 | Which member does Evoke expend — front, player's choice, or back? |
| **F6** | 4.4 | What does "much stronger Fanfare scaling" mean — a multiplier on the Focus term, a steeper rate, proportional, or none? |
| **F7** | 4.4 | Does Evoke cost Encore on every card, only on the Block-paying cards, or not at all? |
| **F8** | 4.5 | Does the Focus term keep its shipped shape, go per-member-type, or go proportional? |
| **F9** | 4.5 | Now that the ceiling is the payoff: keep the cap at 39 (+3) and add drafted cap-raisers, raise the constant, leave it fixed, or lower `SALON_FOCUS_PER` instead? |
| **F10** | 4.5 | Does the 20% decay hold as the seed, drop, or rise? |
| **F11** | 4.6 | What happens to `let_the_people_rejoice` — re-author it in place as the Rare drain card, retire and replace it, or keep it as a cost-0 kit card re-gated on Fanfare? |
| **F12** | 4.6 | How many drain cards, and does one of them sit below Rare? |
| **F13** | 4.7 | What does a deploy card face print, now that it carries three rules? |
| **F14** | 4.7 | What does each occupied slot show — member, live trigger number, front marker, and does the Evoke number join them? |
| **F15** | 4.7 | Does the Fanfare meter preview next turn's value after decay? |
| **F16** | 5 | Does the starter teach Evoke with a card, by overcrowding, or both? |

**Evidence added after drafting — external review, [USER]-relayed** (from
[USER]'s own GPT chat; no seat authority, and it changes no recommendation
here). Three rows drew a specific objection, recorded so the pick is made
against it:

- **`F1` — argues for option (2), the four-member roster.** §4.5's Focus term
  adds +1 to **every member numeric**, and nothing in §4.2 or `F8` exempts an
  energy payout or Chevalmarin's Encore refund, so a Rare energy member arrives
  Focus-scaled and, under `F4` pick 1 (triggers unbounded per turn), on an
  unbounded number of Companion plays; add the energy member only after it is
  settled that Energy and resource refunds are never Focus-scaled. **Settled in
  draft since:** §3.1 amendment 4 and §4.5 now carry a prospective scaling
  invariant ("the Focus term scales performance numerics only … never Energy,
  Encore, Charge, Fanfare itself, card generation, or aura/status stacks"),
  which excludes the energy payout and Chevalmarin's Encore refund. It is
  PROSPECTIVE and uncountersigned, so it does not by itself move the `F1`
  recommendation — but if it is signed, option (1)'s objection is answered.
- **`F13` — argues for option (2), trigger line in full and Evoke as a
  keyword.** The recommendation's own text concedes the face is "carrying three
  rules" and calls it "the sharpest D5 tension in the packet"; moving the Evoke
  line to the member's board tooltip is the cheaper half to hide.
- **`F14` — argues for option (2), the slot also showing the Evoke result.**
  Taken with `F13` (2) this puts each effect in exactly one place, and it puts
  the Evoke number on the persistent board — which is where a player standing
  over a generic Evoke card has to forecast it from.

### 9.3 What this packet does NOT ask, and why

**Spotlight.** The brief does not mention it, and folding it in would mean
asking [USER] to decide the fate of 18 cards inside a packet about a different
subsystem. The evidence that its mode choice has collapsed to a rule is on the
record and unanswered; it should be the next Furina question. Named in §3 as
deliberately unresolved so that silence is not mistaken for a decision.

**Klee's and Kokomi's Bursts.** The roster-wide retirement is RULED and lives
in its own packet on `burst-retirement`. Furina's fold here is the last of the
three under R220 B's order; this packet decides Furina only and its LAW text is scoped to say so.

---

## 10. Register changes this packet OWES

> **LANDED AS `M59` BY R220** (2026-08-29). The `M54` item 2 reserved was
> minted in the meantime by the KURAGEMEM001 blind run, so the sixteen picks
> carry `M59`; `M52` is re-pointed as item 1 asks, and item 6's sequencing is
> superseded by R220 B's order (Kokomi → Klee → Furina for the folds, shared
> retirement last). Pointer only — the text below stands as written.

Not made here. This branch is docs-only and does not touch `QUEUE.md`,
`BACKLOG.md`, `RULINGS.md`, `STATE.md` or `tools/lint_register_ids.py` — the
R219 slate branch owns those and is unmerged. What is owed when they next open:

1. **`M52` re-pointed.** It currently carries E4's C1 (the §3 ruling text and
   its seven retirements), C2 (the prospective LAW text at E4 §3.1/§3.2) and
   C3 (the §7.1 P7 triage plan), plus the co-op consequence. All four are
   superseded. `M52` becomes: countersign this packet's §3 ruling text and its
   §3.1 prospective LAW text.
2. **One new `M` row for the picks** — next free id is **`M54`** — carrying
   F1–F16 as one slate, per R206 as amended by R212 (one batch per sitting,
   assembled by Claude, recorded as ONE slate under ONE ruling).
3. **The ruling id.** §3's draft is `R2xx`; next free is **`R220`**. The
   ruling should record §1.1a's four answers as ruled, since they are [USER]'s
   verbatim words and belong in a commit message and a ruling rather than only
   in a packet.
4. **E4's ids.** E4 minted none of its own — it was written entirely against
   `M52` and cited existing `EB` rows, so nothing of E4's needs retiring from
   the registers beyond the `M52` re-point. E4's file stays in
   `review/active/` as the record; a later pass may move it once `M52` is
   signed against this packet.
5. **STATE's "Furina E4 — PACKET CLOSED, COUNTERSIGN OPEN" bullet** needs
   rewriting to point at this packet and to record that the Furina slice is now
   gated on `M52` (re-pointed) and `M54`.
6. **A pointer to the roster-wide Burst retirement**, which is RULED and
   packeted on `burst-retirement`
   (`review/active/burst-retirement-2026-08-29.md`). That packet owns its own
   register rows, its own ruling id and the LAW text that supersedes §3.1's
   Furina-scoped amendment 2. What is owed *here* is only the cross-reference:
   whatever STATE bullet describes the Furina slice should name Furina's fold
   as the last of that ruling's three characters (R220 B).
7. **Two hygiene fixes, both normal commits under the hygiene norm**, owed on
   whichever branches next touch those files: the kickoff's Salon
   dry-overdraw sentence (§2.7c), and `docs/furina-cards.yaml:13`'s header
   comment claiming 78 cards against a real 84.
8. **No `EB` row is minted by this packet.** The §2.7 findings are design
   constraints and doc corrections, not engineering defects. Next free `EB` id
   is **`EB-194`** and it stays free.

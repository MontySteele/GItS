Status: SUPERSEDED by review/active/kokomi-brief-2026-09-01.md

# Kokomi playtest triage — [USER]'s manual solo run, 2026-08-31

> **What this is.** House triage of [USER]'s notes from a manual solo Kokomi
> playtest on 2026-08-31. Each claim is checked against the repo and given one
> of three verdicts: **confirmed defect** (a `BACKLOG.md` row), **design call**
> (a numbered ask for [USER], `T1`–`T6` in §4 — they stay here, not in
> `QUEUE.md`, because the slate goes to [USER] and GPT first), or **not a
> defect** (named as such, with the evidence).
>
> Nothing here changes a sheet, a constant, a stamp or a ruling. Where [USER]
> delivered taste ("companion card spam feels uninteresting"), the ask is what
> to DO about it — never whether he is right.

> **Lifecycle: SUPERSEDED (2026-09-01)** — the kit this triage examined is being replaced under the Kokomi brief; the T1 to T6 asks are moot, the BACKLOG rows it minted stand.

---

## 1. The played world, established before anything else

**[USER] played `0.2.1786+proto.dirty` — a DEV build with BOTH prototype arms
compiled in.** Every conclusion below is conditioned on that.

Read from the install, read-only:

```
C:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2\mods\klee\manifest.json
  "version": "0.2.1786+proto.dirty"
```

(the game directory comes from `klee-mod/local.props`; `klee-mod/build/deploy.ps1:228`
writes `<GameDir>\mods\klee`). The three files beside it are dated
**2026-08-30 21:30** — the phase-1 pack, untouched since.

### 1.1 Why that package was still installed

`review/qa/bt3-w5-2026-08-30/record.md` says so in as many words. Phase 2 of
the 2026-08-30 window reused phase 1's pack rather than rebuilding it, and its
teardown block reads:

> ```
> mods\klee manifest version: 0.2.1786+proto.dirty
> ```
> The mod package is deliberately NOT reverted: `0.2.1786+proto.dirty` was
> phase 1's product and this window reused it without rebuilding.
> `deploy.ps1` restores the release build before any measured run or handoff
> (R217 D).

So the restore rule fires **before a measured run or a handoff**. A manual
solo playtest is neither. The dev package was left installed by design, and
the next person to launch the game got it. That is **`EB-257`** below.

### 1.2 What a manual player sees on that build — and the quarantine question

The brief asked whether a quarantined arm being reachable by a manual player
is itself a finding. **It is a finding about the WORLD, but it is not a
quarantine breach**, and the reason matters.

**"Seat-guarded" in `EB-225` does not mean "only a test seat can reach it."**
`tools/lint_prototype_patch_scope.py`'s own docstring defines its two rules:

> (a) CHARACTER SCOPE. The patch returns early unless the creature it is about
> belongs to the arm's character. …
> (b) SEAT GUARD. Every resolution of the local seat goes through the guarded
> form. `LocalContext.GetMe(` is red on this surface unless it sits inside a
> `try` …

That is a **crash-safety** lint, bought after `EB-194` and `EB-221` took whole
runs down. It says nothing about who may play the arm.

**The real quarantine is MEMBERSHIP, and it holds.** `KokomiCardPool.cs:78-113`:
prototype rows go into `KokomiOffPoolCards`, which `FilterThroughEpochs`
subtracts from `GetUnlockedCards` — *"the SOLE path into reward rolls, the shop
and card transforms"* — so no `proto_…` row can be offered. The sim says the
same at `tier0/content/loader.py:780-783`: *"`_card_index` is still not
populated with prototypes, so pools, rewards, drafts and digests remain
structurally unable to see them."*

**But the Kurage memory is not a card. It is the base kit, and it is
unconditional on a `+proto` build.** `klee-mod/KleeCode/Powers/Prototype/KurageMemory.cs:130`
is `public static readonly bool AlwaysOn = true;`, and
`klee-mod/KleeCode/Kokomi.cs:110-119` swaps starter slot eleven under
`#if PROTOTYPE_CARDS`. There is no seat check, no attend flag, no opt-in.
`KURAGECAD-W1` proved exactly this five ways on the same package
(`record.md`, *"every one of the 22 wire snapshots carries a populated
`kurage_memory` block with `base_kit: true`"*).

**Conclusion.** [USER] seeing Muster cost-transformation live is the arm
working as built, on the build that was installed. The finding is not "the
quarantine leaked"; it is **"a manual session inherited a dev world with no
signal that it had"** — `EB-257`.

### 1.3 What that world differs from a release build in

| | release `0.2.1357` | what [USER] played |
|---|---|---|
| Kokomi starter slot 11 | `Bake-Kurage` (basic) | **`To the Front!`** (common, a Muster) |
| Bake-Kurage | a card you play to summon | **always on the field, every fight, from turn 1** |
| Kurage memory queue | absent | **live** — Muster enrols at 3× cost, 1 Charge per Exhaust |
| Klee Spark alt-cost rows | absent | compiled in (irrelevant to a Kokomi run) |

Sources: `Kokomi.cs:97-121`, `KurageMemory.cs:314-317`,
`tier0/content/loader.py:882-960`, `tier0/constants.py:714-735`.

---

## 2. Claim-by-claim verdicts

Numbering follows [USER]'s notes.

### B1 — "To the Front! can appear in card rewards even though it's a starter card"

**CONFIRMED, and it is broader than the prototype build. → `EB-255`.**

*Is there a starter-exclusion rule anywhere?* **No rule. There is a stated
INVARIANT, and it is false on two live rows.** `tier05/draft.py:2539-2541`:

> Spec §4 asks for commitment emerging from *what has been drafted*, and the
> starter was not drafted. **Rarity separates the two exactly: every starter
> card is basic and basic never appears in the draftable pool.**

That sentence is the whole exclusion mechanism in both engines. There is no
`starter:` flag on any sheet row.

- **Sim.** `tier05/rewards.character_pool` declares itself *"the single source
  of truth for 'which ids can be offered to this character'"* (`rewards.py:57-65`),
  and its entire filter is four tests (`:66-88`): is it a companion, is it a
  kit card, is its rarity in `RARITY_ODDS`, does it belong to this character.
  **No starting-deck test.** `RARITY_ODDS = {"common", "uncommon", "rare"}`
  (`constants.py:1398`) — and `constants.py:1399-1403` states outright that
  *"Absence from `RARITY_ODDS` is what makes a card invisible to draft, reward
  and shop generation — that absence is the mechanism, not a gap."* `basic`'s
  absence is the only thing keeping the four printed starters out.
- **C#.** `KokomiCardPool.FilterThroughEpochs` subtracts exactly one set,
  `KokomiOffPoolCards.Ids` (the kit Burst and the prototype rows). The class
  docstring says it plainly (`KokomiCardPool.cs:21-22`): *"Every generated card
  is reward-eligible today."* `ToTheFront` sits **unguarded** in
  `KokomiCardRoster.cs:81` with no `#if PROTOTYPE_CARDS` anywhere in that file,
  while the starter slot that consumes it *is* guarded.

**The fix pattern exists on the same flag and was simply not applied here.**
Both engines already substitute the *offered* Oath under the flag —
`loader._pool_substitutions` (`loader.py:996-1001`) and
`KurageMemory.SwapOfferedOath` (`KokomiCardPool.cs:51-63`). Both forgot the
offer side of the *starter* swap. The engine even records half the thought:
`tier0/engine/effects.py:3765-3768` worries that the DROPPED `bake_kurage`
becomes unreachable under the flag, and never asks the mirror question about
the ADDED card becoming doubly reachable.

*Which engine leaked it?* **Neither, and both.** Nothing anywhere implements a
starter exclusion, so the rule holds only as long as every starter is `basic`.
Two rows break it:

| row | rarity | where it starts | draftable |
|---|---|---|---|
| `to_the_front` (`docs/kokomi-cards.yaml:170`) | **common** | Kokomi starter slot 11, **prototype builds only** | yes |
| `an_invitation` (`docs/furina-cards.yaml:362`) | **common** | Furina's SHIPPED starter (`tier0/content/characters/furina.yaml:70`; `Furina.cs:71`) | yes |

(`an_invitation` is in her reward pool too — `FurinaCardRoster.cs:19`.) So this
**already ships on Furina** and is not a prototype-only condition. The
prototype flag brought it to Kokomi.

A third crack, for completeness: Kokomi's two starter Companions
(`gorou_inuzaka_charge`, `sayu_daruma_gift` / `shinobu_grass_ring_bond`) are
also `rarity: common`, not basic. They are kept out of her personal reward pool
by `c.is_companion` rather than by rarity — so *"every starter card is basic"*
is false three ways, and only one of the three is currently caught.

*Was it noticed?* Half of it. `tier0/constants.py:731-734`, on the starter swap:

> Rarity Common, which is Furina's `an_invitation` precedent (a Common already
> sits in a printed starter), so no Basic twin is owed.

The precedent was checked; what nobody asked is whether that Common is also in
the reward pool. It is.

*The measurable consequence.* `draft._committed_share` excludes basics
precisely so the starting deck is not read back as a drafting finding — the
comment records that with basics in, adaptive drafting "converged" on
demolition in 100% of runs. `an_invitation` carries `archetypes: [spotlight]`
and is **not** basic, so Furina's commitment number is contaminated by one
starter card today. `to_the_front` carries `archetypes: [commander]` and does
the same to Kokomi under the flag.

**Contrast, and it is the fix's shape.** Klee's arm does this correctly:
`loader._starter_ids` substitutes `proto_pop_spark` and `proto_kaboom_sink` —
`proto_` ids, structurally invisible to every pool. Kokomi's substitutes a real
draftable common.

The *engineering* half — the invariant is unlinted and the metric is
contaminated — is `EB-255`. **Whether a starter is ALLOWED in the reward pool
is a design call: `T6`.**

---

### B2 — "Muster permanently reduces the cost of the transformed card? I thought it was only for the turn"

**The behaviour is CORRECT and designed in both engines. The FACE is wrong. → `EB-254`.**

*Duration, as built.* Rest of **combat**, on that instance — not the turn, and
not the run.

- **C#**, `klee-mod/KleeCode/Powers/KokomiConscript.cs:177-191`:
  > `// Cost is a MODIFIER on the instance, applied for the rest of the`
  > `// combat.` … `recruit.EnergyCost.AddThisCombat(delta, reduceOnly: false);`

  `AddThisCombat`, not `AddThisTurn`. No end-of-turn reset, no shuffle reset.
- **Sim**, `tier0/engine/effects.py:4375-4382`: it rewrites `recruit.cost`
  itself on a `copy.deepcopy` combat token. It deliberately does **not** touch
  `cost_delta_this_turn` or `cost_set_this_combat`, the two dated modifiers
  `tier0/engine/combat.py:339-349` reads.
- The mechanisms differ and the asymmetry is documented at
  `KokomiConscript.cs:121-130`; it exists so the memory price rule gets the
  discounted number on both sides.

*Is permanence designed?* Yes, and it is load-bearing. The memory price rule,
`review/active/kokomi-kurage-memory-2026-08-29.md:1044-1049`:

> A Muster's own −1 counts on the **recruit's** entry, because the recruit is
> the card that Exhausted. **Temporary combat discounts are ignored by
> construction** — the price is read off the card, never off `combat.card_cost`.

The ruled design expressly classes the Muster −1 as part of the recruit's face
and NOT a temporary discount. Making it turn-scoped would move the memory
price rule with it.

*So why did [USER] read it as a surprise?* **Because the keyword prints no
duration and four sibling faces in the same pool print one.** The Muster tip,
`klee-mod/KleeCode/Cards/KokomiRiderTips.cs:204-207`:

> `[gold]Muster N[/gold]: transform N cards in your hand into random Inazuma`
> `[gold]Companion[/gold] cards. Each costs 1 less and [gold]Exhausts[/gold].`

Against these, all shipped, all Kokomi/Companion faces:

- `HonorGuard.cs:47` — *"Companion cards cost 1 less **this turn**."*
- `CraneWing.cs:44` — *"… Companion cards cost 1 less **this turn**."*
- `FriendlyVisit.cs:40` — same
- `AllHands.cs:51` — **both in one sentence**: *"Muster 2, adding the units to
  your hand. Companion cards cost 1 less **this turn**. Gain 2 Charge."*

`AllHands` is the sharpest case: one card prints two −1 discounts, one
qualified and one not, and the reader is expected to infer that the unqualified
one outlasts the turn. A reader trained by the other three reads the bare
"costs 1 less" as the same duration with the clause elided. That is exactly
what [USER] did.

**Distinct from `EB-248`.** `EB-248` is *"the memory's price cannot be derived
from the printed face"* — the queue view showing 3 against a printed 2. This is
the *card's own cost line* carrying no duration. They share a root (the −1 is
invisible in its scope) and fixing one does not fix the other. `EB-248` is
annotated in §3.2 rather than re-minted; the face's missing duration clause is
new and is `EB-254`.

---

### B3 — "Bake Karate still attacks every turn. The memory mechanic was supposed to replace its attack damage, not supplement it."

**NOT A DEFECT on the mechanic. The memory was never ruled to replace the
pulse — it supplements it, deliberately.** The *confusion* is real and is
`EB-247`'s cost; see §3.2.

*The ruled intent*, `review/active/kokomi-kurage-memory-2026-08-29.md:177-181`:

> The jellyfish's own end-of-turn action **stays**, and stops reading the bank
> entirely. It is keyed to the **type of the last card Kokomi played this
> turn** …

with the table: **Attack → 4 damage flat; Skill → 5 Block; Power → PICK C**.
What retired is the *Charge multiplier*, not the attack (`:186-190`,
*"The per-Charge multiplier is gone. `KURAGE_PULSE_PER_CHARGE = 3` retires"*).
And v4 makes it fire MORE often (`:1319-1323`): *"Its pulse therefore fires at
every turn end from turn 1 onward."* R219 D at `STATE.md:522-527` says the same.

*As shipped*, the two live at opposite ends of the turn and cannot conflict:

- memory fires at **turn start** — `KurageMemory.cs:101`
  (`FireTiming = "turn_start"`); sim twin `tier0/engine/combat.py:895-897`
- the pulse fires at **turn end** — `KuragePowers.cs:99 FirePulse`, which under
  the flag delegates to `KurageMemory.Pulse` (`KuragePowers.cs:104-116`) and
  still runs a pulse; sim twin `tier0/engine/effects.py:4279-4285`

Nothing in either engine gates the pulse on whether a memory fired.

**[USER] is not a fourth witness to `EB-247` — it is a different report, on a
different axis.** `EB-247` is a *text-vs-behaviour* mismatch **inside** the
pulse (the buff prints `4 + 3×Charge`, the pulse runs flat 4 / 5 Block);
its acceptance is a wording fix. [USER]'s is a *behaviour-vs-expectation*
claim **across two mechanics**. Closing `EB-247` would leave the jellyfish
attacking every turn and playing memories, and [USER]'s note would still stand.

**But the two do join, and the join is worth recording on the row.** The stale
buff text is the most likely reason a player believes the jellyfish's attack is
the Charge-scaling engine the memory was supposed to replace — and, as §2.B4
shows, it also hides the one escape from the soft lock. That is §3.2's
annotation.

---

### B4 — "Gore - Forward Unto Victory is really strong. When mustered, 0 cost and gives a better version of '2 plating'?" + the Act 1 soft lock

**Every factual half of this is CORRECT. The soft lock is arithmetically real.
The fix is a design call → `T3`.**

#### The card

`docs/inazuma-companions.yaml:39-41` (id `gorou_heart_of_the_clan`; "Gore" is
"Gorou"):

```yaml
- {id: gorou_heart_of_the_clan, name: "Gorou — Forward Unto Victory", star: 4,
   rarity: uncommon, role_c: buffer, element: geo, cost: 1, type: skill,
   effects: [{op: block, amount: 3}, {op: apply_power, power: metallicize, amount: 2, target: self}]}
   # The standing banner: 2 Block a turn while the fight lasts.
```

Face (`GorouHeartOfTheClan.cs:51`): *"Gain 3 Block. At the start of your turn,
gain 2 Block."* Upgrade (`docs/kokomi-upgrades.yaml:289`): `{power_amount: +1}`,
Metallicize 2 → 3.

#### "0 cost when mustered" — correct, twice over

`tier0/constants.py:654-655`: `CONSCRIPT_COST_DELTA = -1` … *"a conscripted
card costs 1 less (floor 0) and gains Exhaust."* So a mustered recruit at
printed cost 1 costs **0**, and gains Exhaust.

And on the memory queue it is free as well: the price is 3× the recruit's own
entry cost, and the recruit's entry cost is 0 — `3 × 0 = 0 Charge`. The packet
names this case in advance (`:3913`, *"a 0-cost Companion that prints
Exhaust — the free-replay case ([USER]'s own Gorou example) at price 0"*), and
`KURAGECAD-W1` measured it live: `K6` recorded *"2 of 3 fires at price 0"*.

#### "a better version of 2 plating" — correct, and on the record as intended

Plating is the base-game reference power (`tier0/engine/refpowers.py`), and it
is what this very boss wears.

| | **Plating 2** (`refpowers.py:1389-1393`, `:1435-1453`) | **Metallicize 2** (`powers.py:127-128`, `CompanionPowers.cs:583-618`) |
|---|---|---|
| grant timing | turn **END** | turn **START** |
| decay | −1 per turn from round 2 | **none** |
| lifetime yield | 2 + 1 = **4 Block, then gone** | **2 Block every turn, forever** |
| stacking | re-stacks, still decays | adds, never decays |
| Dexterity / Frail | exempt (raw) | exempt (raw) — NC-11 / R116 |

`CompanionPowers.cs:585-593` says the timing choice out loud:

> tier0's grants it at turn START … **start-of-turn Block survives the
> block-reset and is therefore strictly better, which is priced into every
> number her sheet was measured with. Changing it to end-of-turn is a BALANCE
> change and needs a re-measure, not a bugfix.**

So Metallicize 2 is a **strictly dominant** Plating 2: same magnitude, better
timing, no decay. [USER]'s phrasing is exact.

#### The soft-lock arithmetic — STATIC ANALYSIS, the game was not launched

**The boss.** `tier05/content/act1_pool.yaml:170-195` and
`docs/current/dossiers/enemies/lagavulin-matriarch.md`. 222 HP, sleeps 3, then
a fixed four-beat ring forever: Slash 19 · Disembowel 9×2 · Slash 2 (12 dmg +
12 block) · Soul Siphon (**+2 Str to her, −2 Str AND −2 Dex to the player,
neither decaying**). The dossier's table:

| Lap | Slash | Disembowel | Slash 2 | Lap total |
|---|---|---|---|---|
| 1 | 19 | 18 | 12 | **49** |
| 2 | 21 | 22 | 14 | **57** |
| 3 | 23 | 26 | 16 | **65** |
| 4 | 25 | 30 | 18 | **73** |

Her damage grows **+8 per 4-turn lap**; her heaviest single beat (Disembowel)
grows **+4 per lap**.

**Assumptions, stated.** Kokomi HP 80 (`tier0/content/characters/kokomi.yaml:17`).
The player plays a 0-cost mustered *Forward Unto Victory* once per turn from
turn 1. Card Block (3) is `Move`-typed and IS eaten by the Dex drain;
Metallicize Block is `Unpowered` and is **immune** to it (NC-11 / R116,
`refpowers.py:192-193`). Block clears at player turn start; Metallicize grants
at turn start. The boss's own Plating 12 is `UNIMPLEMENTED (§10.9)` in the
modelled fight and is ignored, as the sheet ignores it.

Block on turn *t* = `2·(t−1)` + `max(0, 3 − 2·SoulSiphons)`.

| t | her beat | dmg | block | HP (from 80) |
|---|---|---|---|---|
| 1–3 | Sleep | 0 | 3/5/7 | 80 |
| 4 | Slash | 19 | 9 | 70 |
| 5 | Disembowel | 18 | 11 | 63 |
| 6 | Slash 2 | 12 | 13 | 63 |
| 8 | Slash | 21 | 15 | 57 |
| 9 | Disembowel | 22 | 17 | 52 |
| 12 | Slash | 23 | 22 | 51 |
| 13 | Disembowel | 26 | 24 | 49 |
| **16** | Slash | 25 | **30** | **49** |
| 17 | Disembowel | 30 | 32 | 49 |
| 21 | Disembowel | 34 | 40 | 49 |

**From turn 16 the player takes zero damage, permanently, and the margin
widens without bound.** Block grows +2/turn (+8/lap); her per-turn peak grows
+1/turn (+4/lap). Block wins forever. Total HP lost before the crossover:
**31 of 80.**

**And she cannot be killed.** Player Strength goes −2/lap unbounded, so card
damage floors at 0, against 222 HP that regains 12 Block every fourth turn. If
the player plays only Gorou (a Skill), the memory pulse takes the **Skill**
branch — 5 Block, zero damage (`KurageMemory.cs:79 PulseBlock = 5`). **Damage
output is exactly 0. Unwinnable AND unloseable: a true infinite stall.**

**The one escape, and it is hidden.** The pulse's Attack branch is
`KURAGE_PULSE_BASE = 4`, **flat and Strength-independent**
(`effects.py:4284`, `KuragePowers.cs:39`). Since the mustered Gorou costs 0,
the player can play it *and* end the turn on any Attack, keying a 4-damage
pulse — roughly 16/lap less her 12 Block ≈ 12 net/lap ≈ 19 laps ≈ 76 turns to
grind out 222 HP. **The fact that makes this escape findable is the one
`EB-247`'s stale buff text hides**, since that text still advertises
`4 + 3×Charge`.

**Feasibility caveat, stated rather than skipped.** The loop does not need a
per-turn Gorou. Metallicize is permanent, so **one play per lap already matches
her +8/lap scaling**. But it does need a repeatable Muster source: the memory
enrols once per instance (`Card.kurage_remembered`, packet `:1031-1033`) and
`kurage_fire` removes the token from combat, so one Muster buys one free replay,
not an engine. Multiple Muster cards — which is exactly the "companion card
spam" deck [USER] describes in §4 `T1` — supply it.

**No instrument could have caught this**, and that is the executable half:
neither engine has any stall / no-progress detector, and the tier-0.5 model of
this boss is missing the one mechanic (Plating 12) that changes the early
arithmetic. → **`EB-256`**. The design fix is `T3`.

---

### B5 — "Pearl Bulwark is basically a starting card?"

**CORRECT. Design call → `T4`.**

| card | id | rarity | cost | face | upgraded |
|---|---|---|---|---|---|
| **Coral Guard** (starter, ×4) | `coral_guard` | basic | 1 | Gain **5** Block | **8** |
| **Pearl Bulwark** | `jade_bulwark` | common | 1 | Gain **6** Block | **8** |

Sheet rows: `docs/kokomi-cards.yaml:127-128` and `:248-249`. Upgrades:
`docs/kokomi-upgrades.yaml:18` (`coral_guard {block: +3}`) and `:67`
(`jade_bulwark {block: +2}`). Printed faces are **byte-identical strings** —
`CoralGuard.cs:44` and `JadeBulwark.cs:44` both read
`"Gain {Block:diff()} [gold]Block[/gold]."`.

So Pearl Bulwark is her starter Defend at +1 Block, with **no rider**, and
**upgraded the two cards are exactly the same card**. Kokomi's full starter is
4 × Water's Edge, 4 × Coral Guard, Gorou — Inuzaka All-Round Defense, Sayu —
Muji-Muji Daruma (randomised with Shinobu), slot 11, Tactical Retreat
(`Kokomi.cs:97-121`).

This is not an accident — the sheet says so at `:250`:

> Graceful Retreat parity exactly (6 at common, under Klee's Hide and Seek) —
> the stability character does NOT get a hidden block subsidy.

It is a deliberately plain rate benchmark, and `:941` calls it *"the pool's
clean Block-rate"* anchor that other rows are priced against. **So the row is
doing a job; what [USER] is reporting is that the job is invisible from the
reward screen.** That is a design call, not a defect — `T4`.

---

### B6 — "Lots of very wordy cards have sentences when keywords would suffice (E.g. Salvage the Line, Undertow)"

**SPLIT: Salvage the Line is confirmed and is a textbook keyword candidate;
Undertow is already at budget and should NOT be compressed.** The policy
question is `T5`; one small face defect falls out and is `EB-258`.

([USER] made the same point on 2026-08-26: *"Cards in the mod generally have a
LOT of words compared to cards in the base game."* —
`review/active/kokomi-playtest-notes-2026-08-26.md` §B. This is the second
report.)

#### The machinery that already exists

Two separate keyword surfaces, both live:

- **Real `CardKeyword` enum members** with auto-rendered labels and hover tips
  — `klee-mod/KleeCode/Cards/KleeKeywords.cs`: `ElementalSkill`, four
  `Applies<Element>`, `Bomb`, `Confiscated`, nine reaction previews, three
  Salon members; plus base-game `Exhaust` and `Sly`.
- **Hover-tip keywords** — a loc title row plus a body built live in C#,
  registered at `klee-mod/KleeCode/KleeMod.cs:246-281`: `KLEEMOD-MUSTER`,
  `KLEEMOD-CHARGE`, `KLEEMOD-CHARGE_RIDER`, `KLEEMOD-KURAGE_PULSE_RIDER`,
  `KLEEMOD-GARMENT_RIDER`, `KLEEMOD-BURST`. `KleeSelfCheck` rule R20 already
  enforces that every `KLEEMOD-` constant has a `.title` row.

**The precedent is R78, and it is written down** —
`tools/gen_klee_cards.py:4204-4209`:

> R78 (Neap Tide v2.1): the grammar is a KEYWORD now. Every conscript card used
> to restate the whole rule … on nine cards, which is ~90 characters of
> identical text per face and the reason several of them were at text budget.
> "Muster N" says it once …

with the discipline that comes with it (`:4212-4215`): *"DEVIATIONS WRITE OUT
ONLY THE DEVIATION, which is the half that makes the keyword worth having."*

Both faces are **machine-generated**, so any change here is a codegen edit, not
a card edit (`gen_klee_cards.py:6585-6589`, `:2252-2265`, `:577-579`, `:6803`).

#### Salvage the Line — CONFIRMED

`shell_of_sanctuary`, `docs/kokomi-cards.yaml:476-480`; face at
`ShellOfSanctuary.cs:51`, **173 characters stripped of markup, four sentences**:

> Draw {Cards} card{s}. **Choose a card from your Exhaust pile; put it on top
> of your draw pile. It gains Exhaust.** Gain 2 Charge. Gain {Block} Block.

The bolded clause is **114 characters — over half the face — for ONE op**
(`{op: recall_to_draw, amount: 1, from: exhaust}`), and the generator emits it
identically for every future card that uses the verb. That is R78's exact
profile (~90 chars, repeated). **No keyword for retrieval exists** — no
`CustomEnum`, no `KLEEMOD-RECALL` row — although the verb already has a C# home
(`Powers/RecallFromExhaust.cs`) and a marker interface (`IExhaustRetriever`).
A `Salvage N` keyword would take the face to roughly **86 characters, a ~50% cut**.

**But the project's own standard says not yet, and the reason is on the record.**
`gen_klee_cards.py:6576-6580`:

> The gained Exhaust is the whole reason the card is priced as a loan and not
> as a second copy, so it is printed, not left to a keyword the player has to
> notice on the returned card.

That was written when this was *"THE FIRST EXHAUST-RETRIEVING ROW IN THE REPO"*
(`kokomi-cards.yaml:485-486`), and it still is: **instance one of one.** R78
earned Muster its keyword at nine carriers. So the honest reading is: the
candidate is real and the trigger has not fired — mint it when the second
retriever ships. That is `T5` option (1)'s cost, stated up front.

#### Undertow — NOT the example [USER] wanted

`docs/kokomi-cards.yaml:593-596`; face at `Undertow.cs:54`, **144 characters
stripped**:

> Deal {CalculatedDamage} damage, already including the cards Exhausted. If 3
> or more cards are Exhausted: draw 1 card. Sly: Gain 1 Energy.

Clause by clause:

1. *"already including the cards Exhausted"* — **leave it.** This is `EB-164`'s
   ruled grammar (a face states its scaling once), it is the shortest form of
   the statement, and `KokomiRiderTips.cs:57-64` records that cutting a face to
   a bare marker on the strength of a live number is what created the L4b
   legibility defect in the first place.
2. *"If 3 or more cards are Exhausted: draw 1 card."* — no threshold keyword
   exists anywhere in the project (`_EXHAUST_PILE_BAR`, `_CHARGE_BAR`,
   `_FANFARE_BAR`, `_ENCORE_BAR` all render bespoke English at
   `gen_klee_cards.py:571-586`). But the sheet itself measures this clause at
   **15.3% of attack plays** (`kokomi-cards.yaml:606-608`), so it is a better
   candidate for **deletion than for compression**. That is a design call, in
   `T5`.
3. *"Sly: Gain 1 Energy."* — already keyworded, already minimal.

**Verdict: Undertow is at a reasonable budget and no keyword should be minted
for it.** [USER]'s instinct about the *class* is right; this particular card is
not the instance.

#### One defect falls out — `EB-258`

Undertow prints **`Gain 1 Energy` un-gold-tagged**, where every sibling
resource on her faces is `[gold]`-wrapped (`SaltLine.cs:44` `[gold]Exhaust[/gold]`,
`DriftwoodCharm.cs:48` `[gold]Charge[/gold]`). The project already has a name
for this class — `gen_klee_cards.py:584-586`: *"[gold] like its Fanfare/Charge
siblings above — `swelling_overture` shipped the only un-golded resource
keyword on a face (SYS-9)."* This is a second instance, and the comment's
"only" is now false. → **`EB-258`**.

---

### B7 — "The Sly and Exhaust play styles feel disjoint, like they're fighting each other rather than cooperating, and Exhaust starts with better support"

**Both halves are true, and the first is TRUE BY CONSTRUCTION — it is written
into LAW. Design call → `T2`.**

*Why they fight.* A card leaves the hand exactly one way. **Sly fires on
DISCARD** — `docs/current/atlas/tier0-engine.md:148-155`, *"Authored riders
resolve inline in the discard loop … the one trigger site in
`effects._op_discard`"*. **Charge accrues on EXHAUST** —
`tier0/constants.py:477`, `CHARGE_PER_EXHAUST = 1`, *"universal rule: every
card through the exhaust funnel"*. So every card sent to Sly is a card that did
not pay Charge, and vice versa. They are not merely separate; they are
**mutually exclusive per card**.

*And that is deliberate.* `tier0/constants.py:490-496`, on the two exhaust
meters:

> **LAW 5 hands the card/energy economy — draw, energy, cycling, selection — to
> the Discard/Sly lane as a MONOPOLY, so the exhaust verb has no economy rider
> to be paid in. What it has instead is these two meters.** Strip either one
> and the exhaust lane is a lane that spends cards and buys nothing, because
> the law already gave away the thing it would otherwise buy.

Two lanes, two disjoint currencies, by law. [USER] is describing the law
working. The ask is whether the law is still the right one — `T2`.

*"Exhaust starts with better support" — quantified from the starter and the
sheets.*

| | **Exhaust lane** | **Sly lane** |
|---|---|---|
| starter relic | **Pearl of Wisdom** — `CHARGE_PER_EXHAUST` on every exhaust (`Kokomi.cs:124-133`, `PearlOfWisdomRelic.cs`) | **none** |
| starter cards feeding it | **Gorou — Inuzaka All-Round Defense** (`exhaust: true`, `docs/inazuma-companions.yaml:29`); under the proto flag also **To the Front!**, whose recruits all gain Exhaust | **Tactical Retreat** (draw 1 / discard 1) — described on its own row as *"the SLY-TEACHER basic"* (`docs/kokomi-cards.yaml:144-148`) |
| meter payment | **two** — `CHARGE_PER_EXHAUST = 1` and `KOKOMI_BURST_PER_EXHAUST = 2`, described as *"one wage in two currencies"* | **none** — the lane is paid in cards and energy instead |
| pool rows touching it | **31 of 76** | **16 of 76** |

So the gap is real on every axis: 1 starter card and no relic and no meter,
against 1–2 starter cards, the starter relic, and both meters. **And the proto
build widens it** — slot 11 stops being Bake-Kurage (a Charge teacher she plays)
and becomes To the Front!, a Muster whose recruits all Exhaust.

---

## 3. What gets filed

### 3.1 New `BACKLOG.md` rows — `EB-254` … `EB-258`

Minted here, ceiling bumped 252 → 258 in the same commit
(`tools/lint_register_ids.py`), all five in `OPEN_IDS`. `EB-253` is not minted
by this triage and is left unused.

| id | one line | from |
|---|---|---|
| `EB-254` | the Muster keyword prints its −1 with no duration, while four sibling faces print `this turn` | B2 |
| `EB-255` | *"every starter card is basic"* is an unlinted invariant, false on two live rows, and it contaminates `_committed_share` | B1 |
| `EB-256` | an unwinnable-and-unloseable stall is reachable and no instrument can see it | B4 |
| `EB-257` | a dev `+proto` package survives a window teardown into an unattended manual session with no signal | §1 |
| `EB-258` | a second un-golded resource keyword on a face (SYS-9), and the comment saying there is only one | B6 |

The exact rows as committed are in `BACKLOG.md`.

### 3.2 Annotations on existing rows — no new id

**`EB-247`** (*the jellyfish's text disagrees with its pulse — three
witnesses*). [USER]'s "the memory was supposed to replace its attack" is **not
a fourth witness** — different axis (§2.B3). Two things attach to the row as
evidence rather than scope:

1. **The confusion cost is now measured on a human.** The stale
   `4 + 3×Charge` text is the most plausible reason a player concludes the
   jellyfish's attack is the Charge engine the memory replaced. Closing the row
   as written removes that reading.
2. **The stale text also hides the only escape from `EB-256`'s stall.** The
   Attack branch is flat 4 and Strength-independent, which is the one line of
   damage a Strength-drained deck still has. A player reading `4 + 3×Charge`
   on a bank the boss has drained sees no reason to try it (§2.B4).

**`EB-248`** (*a discounted memory entry's price is not derivable from the
printed face*). B2 is the **adjacent** gap, not this one: `EB-248` is the queue
view printing 3 against a face printing 2; `EB-254` is the card's own cost line
carrying no duration. Shared root — the Muster −1 is invisible in its scope —
and neither fix closes the other. Recorded here so a future reader does not
merge them.

### 3.3 Not a defect

- **B3, the jellyfish's attack.** The memory supplements the pulse by ruling
  (R219 D; packet §2 and §12.2). Both engines implement the ruled table. No row.
- **The prototype arm being reachable by a manual player.** Not a quarantine
  breach — membership quarantine holds, `EB-225` is a crash-safety lint, and the
  base kit is unconditional on a `+proto` build by design (§1.2). What IS filed
  is the world-signalling gap, `EB-257`.

---

## 4. The design half — numbered asks for [USER]

These stay in this packet. Under `R206`/`R212` the slate is assembled once and
goes to [USER] and GPT together; nothing here mints a `QUEUE.md` row yet.
Defaults are marked where a default is defensible.

---

### `T1` — Companion spam has no payoff (the headline)

**[USER]:** *"the Muster loop 'works as designed', but companion card spam
feels uninteresting, and so the loop has no payoff."*

**Why this is the load-bearing one.** Three independent readings now say the
same thing from three directions:

- **[USER], 2026-08-26** (exploratory): *"Inazuma companion cards are mostly
  'block or do a little damage', nothing terribly interesting, so the Muster
  usually is just 'hope you get some block'."*
- **`KURAGECAD-W1`, 2026-08-31** (blind, `review/qa/bt3-w5-2026-08-30/record.md`):
  three UNREACHED slots on **one cause** — *"the Charge was never scarce. The
  enriched stress deck over-samples enrolment and under-samples scarcity."*
  If the fuel is never scarce, the Muster loop has no cost, and a loop with no
  cost has no decision in it.
- **`M67` / R227, 2026-08-30**: Kokomi slice 2 RETIRED. All four Charge-priced
  arms retired as authored under R226's clause (*no card prints a Charge
  price*), and the Charge question moved **whole** into the memory program.

So the Muster loop currently has: no scarce input (W1), no printed price
(R226), and no payoff the player can name ([USER], twice). **`T1` is the
question of what the loop is FOR.**

**Options.**

1. **Make the fuel scarce.** Keep the loop and put the pressure back on Charge —
   fewer accrual sources, or a real spend the player chooses between. This is
   what `KURAGECAD-W1` says is untested, not what it says is wrong: the run
   could not measure scarcity because the deck never created any.
   Cost: another registered read before any design moves.
2. **Make the recruits interesting.** The complaint is about the CARDS, not the
   verb. Raise the Inazuma companion pool's ceiling so a Muster is a draw from
   a pool worth drawing from. Connects to `R234`'s companion program — which is
   running Mondstadt first, in parallel, and would reach Inazuma later.
3. **Make the payoff explicit.** Muster currently pays in Block and in memory
   entries. Give the loop a named terminal reward the player is building
   toward, so "spam companions" becomes "assemble a formation".
4. **Narrow the loop.** Fewer Muster cards, each doing more — so the deck cannot
   become spam because the verb is not repeatable enough to spam.
5. **Do nothing yet; measure first.** Run `EB-229`'s memory-cadence read on a
   DEVELOPED deck (the kurage packet defers exactly this) before any design
   move, on the grounds that no option above has evidence separating it.

**Claude's read, offered not taken:** (5) then (2). `KURAGECAD-W1`'s own
diagnosis is that the instrument, not the design, is what failed, and (2) is
the option that addresses the sentence [USER] actually wrote twice — the cards
are boring — rather than the loop that contains them.

---

### `T2` — Sly and Exhaust are disjoint by law; is the law still right?

**[USER]:** *"The Sly and Exhaust play styles feel disjoint, like they're
fighting each other rather than cooperating, and Exhaust starts with better
support."*

§2.B7 establishes: they are mutually exclusive per card (discard vs exhaust are
the two disposal routes), and **LAW 5** deliberately gives the card/energy
economy to Sly as a **monopoly** while paying Exhaust in two meters instead.
The support gap is 1 starter card / 0 relics / 0 meters / 16 pool rows for Sly
against 1–2 starter cards / the starter relic / two meters / 31 pool rows for
Exhaust.

**Options.**

1. **Keep LAW 5, close the starter gap only.** Give Sly a starter-side hook
   (a second Sly teacher, or a Sly clause on the starter relic) so the two lanes
   open level. Smallest change; does not touch the law.
   *(marked DEFAULT — it is the only option that answers the half of [USER]'s
   sentence that is a measurable asymmetry rather than a design thesis.)*
2. **Bridge them deliberately.** Mint rows that pay BOTH — a discard that also
   fuels Charge, or an Exhaust that also rings the Sly bell. This is a partial
   repeal of LAW 5's monopoly clause and the constant comments say so out loud;
   it is a LAW amendment, [USER]'s only.
3. **Separate them harder.** Accept the disjointness and make it a real
   archetype fork: two decks, one character, and stop trying to make a hybrid
   playable. Costs the middle of the draft.
4. **Retire one lane.** Sly is 16 of 76 rows and has no meter. Cutting it
   concentrates the character; it also deletes the Assist archetype.
5. **Rebalance the wage instead.** Leave the lanes alone and move
   `KOKOMI_BURST_PER_EXHAUST` / `CHARGE_PER_EXHAUST`. **Flagged as a trap:**
   `constants.py:497-503` records that these two are *"one wage in two
   currencies, so they move together or the reason moves with them"*, and the
   Burst fold (`EB-199`) is already going to move one of them.

---

### `T3` — Gore's strength, and the Act 1 soft lock

**[USER]:** *"I ended up soft locked on the act 1 boss (Lagavulin Matriarch).
There was no way to scale damage, but I could endlessly loop Gore - Forward
Unto Victory for more block than its attack scaled."*

§2.B4 confirms the arithmetic: **unwinnable and unloseable, permanently, from
turn 16 at 49/80 HP.** Three separate properties combine, and a fix can attack
any of them.

**Options — the COST angle.**

1. **Price the recruit.** The stall needs a *0-cost* repeatable body; it exists
   because `CONSCRIPT_COST_DELTA = -1` floors a cost-1 Companion at 0, and the
   memory then prices `3 × 0 = 0`. Floor the memory price at 1 Charge
   regardless of cost. Narrow, and it puts a real cost back on the free replay
   the packet already flagged at `:3511`.
2. **Floor the conscript discount at 1** so no mustered Companion is ever free.
   Wider — it touches every Muster, and `EB-183`'s subsidy question is open on
   the same surface.

**Options — the LOOP angle.**

3. **Cap Metallicize.** A stack ceiling on the power. Blunt, and it prices a
   card by capping a base-game-shaped power rather than by changing the card.
4. **Move Metallicize to end-of-turn**, matching tabletop Plating.
   **Flagged:** `CompanionPowers.cs:585-593` says explicitly this *"is a
   BALANCE change and needs a re-measure, not a bugfix"* — it re-prices every
   number on the Inazuma companion sheet.
5. **Make the grant non-stacking** (refresh to the highest, do not add), which
   turns the card from an engine into a buff and kills the loop at the root
   without touching the number.

**Options — the BOSS / SYSTEM angle.**

6. **Give the Matriarch an anti-turtle clause.** She is described in her own
   dossier as *"the anti-turtle clock"*, and against unbounded raw Block she is
   not one. A scaling unblockable beat, or a Block-strip on Soul Siphon.
7. **A general stall rule** — after N turns of no HP change on either side,
   something gives. Systemic; affects every fight and every character.
8. **Implement her Plating 12.** Listed `UNIMPLEMENTED (§10.9)` in
   `act1_pool.yaml`. Does not fix the stall (Plating is gone once she wakes) but
   the modelled fight is currently not the shipped one, which is why no sim run
   would have found this.

**Claude's read, offered not taken:** (1) + (5). Both are narrow, neither
re-prices a sheet, and together they remove the two properties the stall needs
(a free repeatable body, and an unbounded accumulating grant) without touching
the boss or the engine. (6) and (7) are real and are bigger than this playtest.

---

### `T4` — Pearl Bulwark's rarity and slot

**[USER]:** *"Pearl Bulwark is basically a starting card?"*

He is right (§2.B5): 1 for 6 Block against the starter's 1 for 5, no rider, and
**upgraded they are the identical card**. The sheet's own defence is that it is
the pool's clean Block-rate benchmark — a real job, but one the player cannot
see from a reward screen.

**Options.**

1. **Keep it, and accept that a plain rate row is a legitimate common.** The
   base game ships these. *(marked DEFAULT if the benchmark job is judged worth
   a pool slot.)*
2. **Give it a rider** so it is a choice rather than a rate. Costs the benchmark
   — every card priced against it re-prices with it, and the sheet says nine
   rows read off it.
3. **Cut it** and let the benchmark live as a comment rather than a card.
   Frees a common slot for something with a decision in it.
4. **Move the benchmark off the pool.** Keep an unshipped reference row that
   pricing reads, and ship something else in the slot. Cleanest conceptually,
   most machinery.

---

### `T5` — The keywording policy

**[USER]:** *"Lots of very wordy cards have sentences when keywords would
suffice (E.g. Salvage the Line, Undertow)."* Second report; the first was
2026-08-26.

§2.B6 shows the machinery already exists — two keyword surfaces, six
`KLEEMOD-` hover-tip keywords, ~20 `CardKeyword` enum members, a loc merge and
a self-check. **The question is the POLICY, because the two examples pull
opposite ways:** Salvage the Line has a 114-character generated clause that is
a textbook R78 candidate but is instance *one of one*, and Undertow is already
at budget with its longest clause protected by `EB-164`'s own ruling.

So this is not "compress the wordy cards". It is: **what is the standing rule
for when a repeated clause becomes a keyword, and does anything enforce it?**

**Options.**

1. **Mint `Salvage N` now**, accepting the generator's stated objection (the
   printed Exhaust is why the card is priced as a loan). Fixes the one card
   [USER] named. Costs a keyword carried by a single card — which R78's own
   argument says is exactly when a keyword is *not* worth having.
2. **Set the trigger and wait.** Write the rule down — *a verb earns a keyword
   at its Nth carrier* — and mint `Salvage` when the second retriever ships.
   Cheap now, and it makes the next case automatic instead of a debate.
3. **A measured pass first.** [USER]'s own 2026-08-26 routing already asked for
   this and it was never run: *"the card-text word count per card vs the base
   game, as a measured table before any grammar pass is scoped."* One table,
   no game time, and it turns "lots of wordy cards" into a ranked list — which
   is what tells us whether Salvage is typical or an outlier.
   *(marked DEFAULT, with (2) riding it — it is owed from the last playtest,
   costs nothing, and every other option is better chosen with it in hand.)*
4. **A standing rule with a lint.** A character/clause ceiling per rarity, with
   `tools/` enforcement, so the next sheet cannot regress. The repo's own
   pattern for this class is `lint_face_scaling.py` (`EB-164`).
5. **A full compression pass, roster-wide**, minting whatever keywords fall out.
   Largest; ~239 faces, every one a face-defect preflight surface.

**Riding on this, a separate small call:** Undertow's *"If 3 or more cards are
Exhausted: draw 1 card"* fires on **15.3% of attack plays** by the sheet's own
measurement. Cutting the clause is a shorter face AND one less thing to read
for a rider that mostly does not happen. Keep / cut is [USER]'s.

---

### `T6` — May a starter card appear in the reward pool?

Raised by `EB-255`. The invariant *"every starter card is basic and basic never
appears in the draftable pool"* is written in `draft.py` and false on two rows
today — `an_invitation` (**shipped**, Furina) and `to_the_front` (prototype,
Kokomi). `EB-255` makes it visible and stops the metric contamination; **what
the rule should BE is the call.**

**Options.**

1. **Enforce the invariant.** Every starter is `basic`; give `to_the_front` and
   `an_invitation` basic twins, or move them out of the starters. Restores the
   rule the drafter already assumes.
2. **Retire the invariant, keep the behaviour.** A starter may be a common and
   may be re-offered; fix `_committed_share` to exclude by *starter membership*
   rather than by rarity. **Note the follow-on:** Klee's prototype arm uses
   `proto_` ids specifically so this cannot happen, so this option makes the
   two arms inconsistent on purpose.
3. **Split the difference:** a starter may be a common, but a common that sits
   in a starter is excluded from that character's reward pool. One flag, one
   filter, both engines. *(marked DEFAULT — it keeps every existing card and
   every existing rarity, and it is the option that matches what [USER]
   expected to happen.)*
4. **Do nothing.** Getting a second copy of a good 0-cost enabler is a fine
   reward. Then `EB-255` narrows to the metric fix alone.

---

## 5. Sequencing — where this run sits

This was an **EXPLORATORY** manual run, and it does not consume the
confirmatory protocol.

The chain `R175` fixed, restated at `docs/current/QUEUE.md:32-34` and
`STATE.md:846-848`:

```
exploratory contact  ->  S4-G6 band declaration  ->  S4-G14 confirmatory protocol
   (DONE)                (next gate)                  (table time, [USER]'s)
```

- **Exploratory contact has now happened twice** — 2026-08-26 on `0.2-1159`
  (`review/active/kokomi-playtest-notes-2026-08-26.md`) and this run on
  `0.2.1786+proto.dirty`. Neither is graded against anything; both are sources
  of understanding, per the protocol's own re-anchor note
  (`docs/current/playtest/kokomi-playtest-protocol.md`, R115).
- **The next gate is `S4-G6`** — Kokomi's HP stability band, declared from
  design intent, with its provenance recorded, **before** the confirmatory run
  and **never revisable against it** (`DEC-D5` clauses 2–4). Its MECHANISM is
  ruled: **Claude drafts it from written intent and [USER] countersigns**
  (R231, under the R212 ladder). The band itself is still owed.
- **`S4-G6` is scheduled AFTER the Kokomi fold** (`STATE.md:847-848`). This
  playtest does not move that: the fold is R220 B's first of three, and a band
  declared against a pre-fold Kokomi would be declared against a character
  about to change.
- **`S4-G14`**, the confirmatory protocol run, stays blocked on `S4-G6` and on
  the `N1` attribution remnant (`EB-53`), and is [USER]'s table time.

**What this triage contributes to that chain:** nothing that consumes a gate,
and one thing that constrains the next one. `EB-257` says a manual Kokomi
session can land on a dev `+proto` world without knowing it — and `S4-G6`'s
band is measured against a build. **The confirmatory run must be taken on a
RELEASE package, stamped in its own record**, or the band is declared against a
world that includes the memory arm. That is a precondition, not a pick.

---

## 6. What could not be verified statically

Named rather than glossed, per the house rule.

1. **Whether [USER]'s run actually held a repeatable Muster source.** The
   soft-lock arithmetic in §2.B4 needs one (the memory enrols once per
   instance). His deck composition is not recorded — no seed, no session
   record, no wire snapshot: a manual run writes none. The arithmetic is
   verified; the *specific* run that produced it is not reconstructable.
2. **Which act he met the Matriarch in.** He says Act 1;
   `docs/current/dossiers/enemies/lagavulin-matriarch.md:7` places her in
   **Act 2 — Underdocks** (act index 1) in the decompiled game, while
   `tier05/content/act1_pool.yaml` models her as *"§10.5 second Act-1 boss"*.
   The dossier and the sim's own pool file disagree on the act label. It does
   not change the arithmetic; it may mean an act-numbering mismatch worth a
   look. **Not filed** — one unverified observation, and naming the disagreement
   here is the cheaper record.
3. **Whether the version string is visible in-game.** `EB-257` assumes a player
   has no in-game signal that they are on a `+proto` build. The manifest
   `version` field is read by the game's mod list, but whether it is *rendered*
   where a player looks was not checked without launching.
4. **The exact live sequence of his Gore loop.** Static analysis only, per the
   brief. The turn table in §2.B4 is derived from the dossier's published
   scaling and the two engines' code, not observed.
5. **Whether Soul Siphon's Dex drain is implemented in the C# mod's own path.**
   The sim's model is `act1_pool.yaml`'s and the dossier's is the decompile's;
   the shipped fight is the base game's own boss and was not re-read from the
   assembly for this triage.

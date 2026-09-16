Status: RECORD (deploy live looks; feasibility only, nothing measured)

# proofs-9, lane 0: the faces and pages half

**Build:** installed `0.2.3541+proto.dirty`, read off
`C:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2\mods\klee\manifest.json`,
`min_game_version` `0.111.0`, BaseLib `3.4.7`, arms
`klee,companion,kokomi,furina-stage,teyvat`, `TeyvatFrame` ON. The installed
`klee.dll` is byte-identical to `klee-mod/dist/klee/klee.dll`
(md5 `475EAF7BEB07027D793D2D80F7F2461C`), so the build under test is the one
main just deployed.

**Lane 0 only**, the owner's profile, port 15526, no `--lane` flag and no
`GITS_LANE` anywhere. Another agent held lane 1 (pid 12100) for most of this
job; nothing here touched its process, its log or its sidecar, and every kill
was `understudy.embark --teardown` killing the pid this job's own sidecar
recorded (27844, then 41464, then 3200). No `taskkill /IM` was issued. The
bridge was **already installed by the deploy** and is recorded as pre-existing
in every one of this job's reversibility ledgers ("shared, left in place");
nothing here deployed, rebuilt, staged or validated anything, and no register
row, `LAW.md`, `EXPERIMENTS.md`, `QUEUE.md` or `STATE.md` line was edited.

**Frames:** `review/qa/proofs-9-lane0-2026-09-16/`, with
`frames-manifest.jsonl`. 8c's frames are tracked, so these are committed too.

---

## The honesty preamble

**Nothing in this record is a measurement.** There is no pre-registration, no
blind grading, no slate and no register row, and nothing below is comparable to
any soak, any run, or any other board.

**Almost every board read here was written by hand.** Cards were granted with
`give_card`, a relic with `give_relic`, powers and debuffs with `set_power`,
energy with `set_energy`, HP with `set_hp` on both sides to keep a board alive
or to end a fight a hand-built deck could not win, and one event was moved into
place with `force_next_event`. `bridge.GRANT_GUARDRAIL` is the governing
sentence and it is printed on every one of those answers.

So each section carries the one screen, page row or wire field its row's
acceptance sentence names, and a verdict on whether that sentence is true on
this build. A PASS means "the sentence the row owed is true here, on a board
built to ask it" — never that the card is good, balanced or fun. **No code was
changed in this job**, by rule, and the driver (`drv.py`, `nav.py` and the
numbered step scripts) is scratch and is not committed, as proofs-6, -7 and -8a
did with theirs.

Three limits, stated rather than left to be noticed:

1. **`n = 1` everywhere.** One enchant screen, one Smith, one mode chooser.
2. **A frame proves a pixel, not a judgement**, and on this machine a frame
   proves less than it should — see "the apparatus" below.
3. **Three items are short of their full acceptance** (`EB-84`, and the screen
   `EB-774` and `EB-783` were read on), and each says so in its own section
   rather than rounding up.

**Board writes, counted off the three archived `godot.log`s**
(`understudy/logs/godot/20260916-143343-27844.log`, `-145626-41464.log`,
`-151244-3200.log`):

| run | `set_hp` | `set_power` | `set_energy` | `give_card` | `give_relic` | `force_next_event` | `hover` |
|---|---|---|---|---|---|---|---|
| Klee `NDSL23161SCB` | 17 | 3 | 3 | 10 | 1 | 1 | 5 |
| Furina `JT9WFFZZDN8G` | 38 | 6 | 15 | 12 | 0 | 0 | 0 |
| Kokomi `5XQ47KYYF17K` | 2 | 1 | 2 | 5 | 0 | 0 | 0 |

**Three embarks, three teardowns, no crash and no stall.** Across all three
archived logs: `AssetLoadException` 0, `Element limit reached` 0, `NCardTrail`
0, `Expected BoundObject to be a SpineSprite` 0.

## The one-line verdicts

| # | item | verdict |
|---|---|---|
| A1 | `EB-610` the Spark sources line prints beside the Spark row | **PASS** |
| A2 | `EB-287` the Bomb merging clause on the tip **and** the glossary | **FAIL** (glossary half) |
| A3 | `EB-670` Feint's headline folds its condition on a no-draw carry-out morning | **PASS** |
| A4 | `EB-752` Ka-pow! prints the relic term with The Boot granted | **PASS** |
| A5 | the stage markup item (#576 item 6) | **PASS** |
| A6 | the "play by page text" item (#576 item 7) | **PASS** |
| A7 | `EB-334` the Plan line equals the morning's number under Vulnerable | **PASS** |
| A8 | the Stage starter's printed name `Take the Stage` | **PASS** |
| B1 | `EB-774` one arm sentence across consecutive screens of one fight | **PASS**, on the Fanfare row |
| B2 | `EB-775` Let the People Rejoice previews the live stage, not a stale spend | **PASS** |
| B3 | `EB-780` the chooser's option faces print folded numbers, Weak too | **FAIL** (Weak not folded) |
| B4 | `EB-783` the four Stage readers print a tip, not a literal 0, off the board | **PASS**, on a deck screen |
| C1 | `EB-734` a second chooser in one run carries the tag | **PASS**, on the Smith |
| C2 | `EB-84` the other three `GAME_RULES` shapes | **PARTIAL** (one of three) |
| C3 | `EB-65` the four Furina power badges | **FAIL**, and it is an ART row |
| C4 | `EB-445` Stoke the Fuse's badge prints the spend | **PASS** |
| C5 | `EB-755` two Bombs in one turn print in set-off order with ordinals | **PASS** |
| C6 | `EB-498` a companion face with a conditional clause previews | **PASS** |
| D | `EB-776` Salon Solitaire draws the NOPE placeholder | **PASS** — does not reproduce |

## The runs

| # | stamp / pid | character | seed | what it was for |
|---|---|---|---|---|
| 1 | `20260916-143343` / 27844 | Klee, A0 | `NDSL23161SCB` | A1, A2, A4, C1, C2, C4, C5, C6, D (Klee half) |
| 2 | `20260916-145626` / 41464 | Furina, A2 | `JT9WFFZZDN8G` | A5, A6, A8, B1–B4, C3, D |
| 3 | `20260916-151244` / 3200 | Kokomi, A3 | `5XQ47KYYF17K` | A3, A7 |

`EB-763`'s run-history warning printed on every launch (1,329 → 1,331 files,
51.0 MB) and **nothing here deleted or edited the owner's store**. The lane-0
`godot.log` archived by each teardown is genuinely lane 0's — `log_path`
resolving a `None` instance to `%APPDATA%` is the right answer for lane 0,
which is the other half of proofs-8a's §16 finding.

---

## A1. `EB-610` — the Spark sources line — **PASS**

Klee fight 2, round 2, one turn with **two** sources: `Fischl — Nightrider`, a
Hexerei card (`EB-642`'s Spark), and then `Jumpy Dumpty` + `Ka-pow!`, whose
set-off paid Pounding Surprise. The wire:

```json
[{"source": "companion:personal/play", "amount": 1, "card": "Fischl — Nightrider"},
 {"source": "relic:pounding_surprise/explosion", "amount": 1, "card": "Ka-pow!"}]
```

and the page, hung under the row whose number it explains — the **power** shape
(`Spark 7 (buff)`), which is the shape this build sends and the one that used to
print nothing:

```
- Spark 7 (buff) — A resource. Cards that print a Spark price spend it.
    - This turn: +1 Fischl — Nightrider, +1 an explosion.
```

Both sources named, one copy, beside the Spark row. That is the row's
acceptance.

*One thing the line does not do, raised below rather than here:* the earlier
turn's opening-bank source dropped out of the sentence once a new source landed
(§"defects" 4).

## A2. `EB-287` — the Bomb merging clause — **FAIL on the glossary half**

The two halves disagree on one screen, which is what the row's acceptance
("tip and glossary say merging") forbids. Klee fight 1, round 1, one page:

The **keyword tip** on the card rail — `ArmKeywordTips.ForBomb`, the C# half
#576 built — carries it:

> *Bomb* — A charge on an enemy: grows 4 a turn, and goes off when Set off or
> as a Mine; **a second Bomb joins the first**. Block stops it. …

The **page's own glossary**, twenty lines further down the same page, does not:

> - **Bomb** — A charge on an enemy: each grows 4 a turn, and goes off when Set
>   off or as a Mine. Block stops it. Only Vulnerable and the HP cap move it.
>   If the enemy dies with it on, it moves to a survivor.

This is not a surprise — PR #576's own "Not done" says the
`blindplay_notes.py` row was left — but the row's acceptance names both, so the
row is not met. **Candidate row:** *`EB-287` — `blindplay_notes.METER_RULES`'s
`Bomb` glossary row has no merging clause while `ArmKeywordTips.ForBomb` does;
the two print on the same page (`understudy/blindplay_notes.py:1267-1270`).*

## A3. `EB-670` — Feint's headline on a carry-out morning — **PASS**

Kokomi fight 1. Two Plans were written on the Bake-Kurage on turn 1 (`Ambush`
and `War Council`, neither of which draws), and on turn 2 the jellyfish carried
both out before anything was played. `resolutions` was empty — nothing had been
played this turn — and Feint, granted into hand on that morning, printed:

```
Deal 15 damage. If a Plan was carried out this turn, deal 15 damage instead. Plan: Deal 15 damage.
```

The headline is the **branch** number, not the else-branch — the shape the row
was filed on (`Deal 5` printed while the hit was 10). Played immediately:

```
- **Feint**
  1. **Wooden Shield Hilichurl Guard** -- 15
```

**Face and hit agree on a no-draw morning**, which is the acceptance word for
word. (Both numbers carry Vulnerable 1 on the target; the point is that the two
agree, not the 15.)

## A4. `EB-752` — the relic term beside Ka-pow!'s number — **PASS**

`give_relic THE_BOOT` (the new op) answered
`give_relic THE_BOOT: 2 -> 3 relics; queued`, and the relic reached the page's
own relic list. Ka-pow!'s face then read:

```
- **Ka-pow!** [Pyro] — cost 0, attack
    Retain. Set off. Deal 4 damage. (+1 **The Boot** on an unblocked hit)
```

— the term printed beside the number, naming the relic. And the hit proved it:
a Set off with two charges landed `11`, `8`, then Ka-pow!'s own line at **5**,
not the written 4.

## A5. The stage markup item (#576 item 6) — **PASS**

The three renderer literals the look found raw are all folded. Furina fight 1,
after a Spend emptied Usher:

```
  - **Usher** joined the stage at 3 Fanfare, and stands in the lead seat.
  - **Usher** left the stage: emptied by a Spend, so it takes a Bow.
  - **Usher** took a Bow: Furina gains 4 Block.
```

Counted rather than eyeballed: across the stage pages rendered in that fight,
`[gold]` occurs **0** times, and a regex for any `[tag]` / `[/tag]` returns the
empty set.

## A6. The "play by page text" item (#576 item 7) — **PASS on the page side, and the bridge is unchanged as designed**

Both halves were exercised, in order.

**The raw page spelling posted straight to the bridge is still refused**, which
is what #576 says it left alone:

```
play_card mode="Spend 3: deal 13 instead"
-> error: Card 'Curtain Rise' has no mode matching 'Spend 3: deal 13 instead'.
   Modes: 'Deal 7 damage' | '[gold]Spend[/gold] 3: deal 13 instead'
```

**The page's own door resolves it and the play lands.** `targeting.posted_mode`
run against the live sheet:

```
posted_mode('Curtain Rise', 'Spend 3: deal 13 instead') -> '[gold]Spend[/gold] 3: deal 13 instead'
```

and posting that string:

```
{"status": "ok", "message": "Playing 'Curtain Rise' targeting Leaf Slime (M)"}
```

So a caller naming the mode the page prints gets through, which is the fix's
claim. *A defect next door is in §"defects" 1: the option card's own TITLE
renders the raw markup on screen.*

## A7. `EB-334` — the Plan line against the enemy's current state — **PASS**

Kokomi fight 1, `set_power <enemy> VULNERABLE_POWER 2`, three Plan faces read
in the same hand on the same board:

| card | sheet Plan number | printed |
|---|---|---|
| `Ambush` | 12 | **18** |
| `Feint` | 10 | **15** |
| `War Council` | 5 | **7** |

Every one is the sheet number folded against the target's Vulnerable, which is
R246's rule and `EB-599`'s D default yielding. Then the morning, off
`kokomi_plans.carried_out`:

```json
{"card": "Ambush", "number": 18, "line": "Bake-Kurage: Ambush, 18",
 "moved": [{"target": "Wooden Shield Hilichurl Guard", "amount": 18}],
 "kind": "damage", "asked": 12}
```

**The Plan line printed 18 and the morning dealt 18.** Acceptance met. (War
Council printed 7 and the beat removed 10 HP — 7 plus a named `Tamakushi
Casket` rider of 3, which the page prints as its own clause.)

## A8. The Stage starter's printed name — **PASS**

`give_card KLEEMOD-PROTO_FS_SALON_DEBUT` answered
`queued 1x 'Take the Stage'`, i.e. **the id did not move and the printed name
did**, which is R179's cosmetic test. The Furina starting deck read

```
Freminet — Pers, Deploy! / Soloist's Solicitation ×2 / Lynette — Enigmatic Feint /
Stage Presence ×2 / Regal Bearing / Curtain Rise / Take the Stage / Rising Applause
```

— `Take the Stage` and `Curtain Rise` side by side in one starter kit, sharing
no word, and no `Salon Début` anywhere on the arm.

## B1. `EB-774` — one arm sentence across consecutive screens of one fight — **PASS, and the word read is Fanfare**

**Said plainly first: no Companion card reached a screen in this run**, so the
row's own named word was not the one read. What was read is the *other* row
keyed on the same latch (`EB-728`'s `Fanfare`), whose two readings are as far
apart as the Companion row's two, and which printed on every screen.

Five consecutive screens of one fight, all after the first combat began, all
printing the same sentence:

| screen | the `Fanfare` glossary row |
|---|---|
| combat, round 1 | *A performer's own bar. Attacks hit your Block, then the lead performer's Fanfare, then you. No cap.* |
| the mode chooser overlay | same, byte for byte |
| a second mode chooser overlay | same |
| the rewards screen after the fight | same |
| the card-reward screen under it | same |

The rewards screen is the one the row's next action names, and it holds. Before
any combat, the **Neow** screen printed the shipped reading instead
(*"Furina's own meter … this run has no stage"*), which is PR #566's disclosed
D/E default — a screen that has never been able to answer keeps the reading
every page had before the latch — and it is recorded here rather than filed.

## B2. `EB-775` — Let the People Rejoice previews the live stage — **PASS**

Two readings, both on the turn a Spend of 3 had already fired.

**(a) the stale-spend shape, which is the row's own.** Immediately after
`Curtain Rise+`'s Spend emptied Usher of 3 Fanfare, with the stage empty, the
Rare granted into hand read:

> Spend all Fanfare on stage. **Deal 0 damage to ALL enemies.** Every performer
> takes a Bow, then returns at 1. Exhaust.

0, not the remembered 3. The stack pops to 0 outside a play.

**(b) it reads the bars, not zero.** With Weak cleared and performers put back:

| stage | printed |
|---|---|
| Usher 1 | **Deal 1 damage to ALL enemies** |
| Usher 1 + Crabaletta 1 | **Deal 2 damage to ALL enemies** |

(An earlier read of the one-performer board under `Weak 3` printed 0, which is
`1 × 0.75` rounded down and not a defect.)

## B3. `EB-780` — the chooser's option faces — **FAIL: the upgrade is carried, Weak is not**

Furina fight 1, `set_power player WEAK_POWER 3`, `Curtain Rise+` granted
upgraded and played to open the mode chooser. The **hand** and the **chooser**
do not agree:

| | mode 0 | mode 1 |
|---|---|---|
| the hand's face (`Curtain Rise+`) | Deal **7** damage | Spend 3: deal **12** instead |
| the chooser's option bodies | Deal **10** damage | Spend 3: deal **16** instead |

10 and 16 are the **upgraded sheet literals**; 7 and 12 are those literals with
Weak 3 folded in (`10 × 0.75 = 7.5 → 7`, `16 × 0.75 = 12 → 12`). So #566 (d)'s
built half works — the option now carries the parent's vars and takes the
parent's upgrade, which is why it says 10 rather than the unupgraded 7 — but
the fold that makes a hand face true of the board does not reach it. The row's
acceptance is *"an upgraded, Weak-folded chooser prints the hand's numbers"* and
it does not.

**Candidate row:** *`EB-780` — the mode chooser's option bodies print the
parent's UPGRADED literals but not the board's terms: under Weak 3 an upgraded
Curtain Rise reads 7/12 in hand and 10/16 in the chooser
(`klee-mod/KleeCode/Cards/ModalChoice.cs`, `CreateMatchingOption`).*

## B4. `EB-783` — the Stage readers' tip off the board — **PASS, on a deck screen rather than Neow**

**What the screens were, plainly.** The card-reward roll after fight 1 offered
*Stage Combat / Grand Entrance / Warm Reception* and no reader, and the Neow
page prints no card faces at all, so neither of the row's two named screens
could be made to carry a reader. What was used instead is the **rest-site Smith
deck chooser at act 1 floor 8** — out of combat, with all four readers granted
into the deck at Neow. All four printed, each with its own rule and the
off-board clause:

```
- **Ousia Surge** — cost 1, attack
    Deal 0 damage, the lead performer's Fanfare.
    *What this number is* — The number is the lead performer's Fanfare. There is
    no stage outside combat, so the number above reads 0.
- **Pneuma Refrain** …  *What this number is* — The number is the back performer's Fanfare. There is no stage outside combat, …
- **Final Bow** …      *What this number is* — The number is the lead performer's Fanfare, which this Bow spends. There is no stage outside combat, …
- **Let the People Rejoice** … *What this number is* — The number is every performer's Fanfare added up and spent. There is no stage outside combat, …
```

and the conditional half holds in the other direction: the **same tip in
combat**, on Final Bow in hand during fight 1, printed the rule and **no**
disclaimer:

```
*What this number is* — The number is the lead performer's Fanfare, which this Bow spends.
```

Four rules, four correct ones, the clause only where there is no board. The row
is met on its substance; the two screens it names are not the two that were
reachable, and that is stated rather than rounded up.

## C1. `EB-734` — a second chooser in one run carries the tag — **PASS, and the second chooser is the Smith**

**What this is not:** a second ENCHANT chooser. `SELF_HELP_BOOK` refuses a
second visit and `SPIRALING_WHIRLPOOL` was not in reach, exactly as proofs-8a
left it. What was opened is the **second deck chooser of the run**, the rest
site's Smith at act 1 floor 7, with an already-enchanted card in the deck — the
condition the row's next action asks for.

The run: `force_next_event SELF_HELP_BOOK`, the Mondstadt dressing *The Guild
Desk's Returned Copy*, **Read the Back** taken, and `Ka-pow!` enchanted with
Sharp 2. Two floors later the Smith's chooser row:

```json
{"name": "Ka-pow!", "type": "Attack", "description": "Retain. Set off. Deal 6 damage.",
 "enchantment": {"id": "SHARP", "name": "Sharp", "description": "Increases damage on this card by 2.",
                 "amount": 2, "shows_amount": true},
 "keywords": ["Set off", "Sharp", "Retain", "Applies Pyro"]}
```

and the page above it:

```
- **Ka-pow!** [Pyro] (Sharp 2) — cost 0, attack
    Retain. Set off. Deal 6 damage.
    Written: Retain. Set off. Deal 4 damage.
    Upgraded: Retain. Set off. Deal 9 damage.
    *Sharp* — Increases damage on this card by 2.
```

**A chooser row carries the tag its hand entry carries** — on the wire
(`enchantment` plus the `Sharp` keyword) and on the page (`(Sharp 2)` beside the
title), with the enchanted description 4 → 6 to prove it is the same card. The
other nine rows printed no tag, which is the comparison that makes it worth
anything.

## C2. `EB-84` — the other three eligibility shapes — **PARTIAL: one of three**

**The attack trio on a mod attack — PASS.** *Read the Back* (`Sharp`,
`CanEnchantCardType == Attack`) opened on a deck of four Strikes, four Defends,
`Jumpy Dumpty` (Skill) and `Ka-pow!` (Attack). The chooser offered **exactly
five rows**: the four Strikes and `Ka-pow!`. No Defend, no `Jumpy Dumpty`, and
the mod attack was offered on the same terms as the base ones.

**The other two were not reached, and the reason is the gate the row names.**
`SELF_HELP_BOOK` takes ONE of its three options per visit and refuses a second
visit in the run; its three are Sharp-on-Attack, Nimble-on-Block (watched in
proofs-8a) and Swift-on-Power. So `souls_power` → local Exhaust has no door in
this event at all, and the no-override trio (`Swift`) is the third option,
which was **locked** on this deck for the same reason it was locked in
proofs-8a — no Power in the deck — and would in any case have cost the visit
the attack shape used. Reaching the remaining two wants either two runs, or a
deck seeded with a Power and an Exhaust card *before* the force.

## C3. `EB-65` — the four Furina power badges — **FAIL, and the cause is settled**

The four were placed by hand on a Furina Stage combat board and confirmed on
the wire as
`Fortissimo Guard 2`, `Courtroom Drama 2`, `Quick Change 2`, `Unheard
Confession 2` (`SALON_DEPLOY_BLOCK_POWER`, `CROSS_EXAMINATION_POWER`,
`FIRST_ATTACK_DRAW_POWER`, `FANFARE_DELTA_BLOCK_POWER`), and framed at 4 s and
again at 90 s after landing.

**They are not flat grey and they are not the placeholder.** Each draws a
distinct **landscape card-portrait illustration** shrunk into a badge slot: a
castle on a spire, a jellyfish over a fountain, a dark crown, a constellation
diagram (`eb65-badge-row.png`). None of the four reads as a sigil at badge size,
and none carries an icon a player could name.

That is exactly the hypothesis PR #576's REPORT wrote down — *"a portrait
downsampled into one reads as a flat colour field"* — settled in the only
direction a live look can settle it: **it is the art and not the code.** The
paths resolve, the pck has the files, `KleePowerIcons.cs:293-304` is doing what
it says. The row's acceptance ("four badges read as sigils") is **not met**, and
its next action is an art bill (R212 rank 1) rather than a C# change.

Beside it, the same grain one row over: Klee's mod relic `Pounding Surprise`
draws as a **square card-art panel** in the relic row while the two base-game
relics beside it draw as cut-out sigils (`ebD-klee-relic-row.png`). Same
pipeline question, different register row.

**The log says nothing about any of this:** across the Furina lane-0 boot,
`pck resource missing` 0 hits, `furina/powers` 0 hits, `AssetLoadException` 0.
The only `Missing sprite` line in the whole log is the base game's
`'snake_ring' in relic_outline_atlas`.

## C4. `EB-445` — Stoke the Fuse's badge — **PASS**

The badge is a pixel and needed a frame; see "the apparatus" for how one was
got. `eb445-stoke-the-fuse-badge-X.png`: the card in hand carries the Energy
badge **`0`** and, beside it, the pink Spark price badge reading **`X`**. Not
the gate, not `1`.

The page half, which the row records as already true, held in the same frame's
board:

```
- **Stoke the Fuse** — cost all your Sparks (1 to play), skill
```

## C5. `EB-755` — two Bombs in one turn, in set-off order, with ordinals — **PASS on both surfaces**

`Jumpy Dumpty+` (Bomb 11) then `Jumpy Dumpty` (Bomb 8) on the same enemy in one
turn. The **C# badge tooltip**, read raw off the wire — the string
`ProtoBombPower.cs:473` builds and `ProtoBombPower.Ordinal` numbers:

```
Bomb 19 — Set off here deals 19 Pyro damage, in 2 hits, making 2 Sparks.
Bomb sizes here, oldest first: 1st 11 / 2nd 8, growing each turn, …
```

and the page, unchanged from it:

```
Bomb 19 (buff) — … Bomb sizes here, oldest first: 1st 11 / 2nd 8, …
```

The order is the set-off order: the 11 was placed first, prints first, and
`Ka-pow!` then set them off **11, 8** in that order (§A4). A three-charge board
later in the same fight printed `1st 3 / 2nd 11 / 3rd 8, including 1 Mine`. A
lone charge earlier in the run printed no ordinal, which is the row's other
half.

*Caveat, stated:* the badge half is the C# string read off the wire, not a
photograph of the tooltip — the tooltip needs a mouse this harness does not
have, and the enemy badge is outside what a frame captures here.

## C6. `EB-498` — a companion face with a conditional clause previews — **PASS**

`Shinobu — Thundergrust` (`Deal 8 damage. If you are below half HP, deal 5
additional damage.`) on a board built to move both numbers: player HP set to 20
of 78 (the condition true), `Strength 3` on the player, `Vulnerable 3` on the
target. The face printed:

```
Deal 16 damage. If you are below half HP, deal 12 additional damage.
```

`(8+3) × 1.5 = 16`, `(5+3) × 1.5 = 12`. Played immediately:

```
- **Shinobu — Thundergrust**
  1. **Wooden Shield Hilichurl Guard (2)** -- 6     (the Overloaded reaction)
  2. **Wooden Shield Hilichurl Guard (2)** -- 16
  3. **Wooden Shield Hilichurl Guard (2)** -- 12
```

**The printed number matches the hit, on both clauses.** The `FoldedBlockVar`
twin held on the same board: `Noelle — Breastplate` printed `Gain 8 Block. If
you are below half HP, gain 6 additional Block.` under Dexterity 2, against a
sheet of 6 and 4. *A defect on that card's other line is in §"defects" 2.*

## D. `EB-776` — Salon Solitaire's icon — **PASS: it does not reproduce**

Asked three ways on the Furina Stage run, as the coordinator's note asks.

1. **The log.** `%APPDATA%\SlayTheSpire2\logs\godot.log`, 402,423 bytes, the
   whole boot: `ethereal_spotlight` — **no hits**. `pck resource missing` —
   **no hits**. The two `NOPE` hits in the file are
   `Progress parse: … Unknown card ID: CARD.SNECKO-NOPE`, a base-game card id in
   the owner's profile, nothing to do with this relic.
2. **The frame.** `ebD-furina-relic-row.png` (from the Neow screen,
   `ebD-furina-neow-screen-1280.png`): the relic row draws a **gilded
   spotlight on a tripod with a cyan lens** — the `ethereal_spotlight` art, at
   relic-row size, cut out and readable. Not the NOPE placeholder. The Klee
   comparison (`ebD-klee-relic-row.png`) draws its three relics too.
3. **The powers.** `EB-65`'s four badges (§C3) share the `furina/` namespace and
   produce **no** log lines of either kind either — so the two are not the same
   defect: the relic resolves and draws its sigil, and the four powers resolve
   and draw the wrong *kind* of image.

The relic is fine on `0.2.3541`. What changed between #570's read and this one
is not established here; the honest statement is that on this build, on this
boot, it draws.

## The apparatus: `EB-788` has a route around it

**`PrintWindow` on this machine captures a fraction of the game window.** A
frame of a live combat (`apparatus-printwindow-same-screen-1280.png`) shows the
run header and Klee's sprite in the upper left and **uniform background
everywhere else** — no enemy, no card hand, no badges. 8c read this as "missing
the bottom"; it is worse than that.

**`GITS_UNDERSTUDY_CAPTURE_ROUTE=copyfromscreen` captures the whole window.**
The same screen, seconds later
(`eb445-stoke-the-fuse-copyfromscreen-1280.png`): the full 3841×2160 board —
relic row, both enemies with their status badges, Furina's/Klee's power badge
row, the End Turn button, and **the entire card hand with its cost badges**.
Every frame in this record that proves anything was taken on that route, and it
is what made `EB-445` and `EB-65` answerable at all.

So `EB-788`'s bound is a bound on the **default** route, not on frames. Worth
writing into `understudy/frames.py` beside the existing warning; not changed
here, by rule.

---

## Defects found that are not on any row above

Raised, not filed — a register row is [USER]'s to mint or Claude's under the
hygiene rule, and this is a record.

1. **The mode chooser's option card prints raw BBCode in its TITLE, in the
   running game.** `mode-option-title-markup.png`: the title banner reads
   `[gold]Spend[/gold] 3: deal 13 instead`, tags and all, while the body one
   line below reads `Spend 3: deal 13 instead` with the word correctly gold.
   The wire agrees (`"name": "[gold]Spend[/gold] 3: deal 13 instead+"`), and the
   blind page folds it, so **the only surface showing the tags is the one a
   sighted player reads.** This is PR #566 (d)'s disclosed default — "the
   option's title stays the authored literal" — meeting the fact that the
   authored literal contains markup. Repro: play any `choose_one` Furina card
   whose mode label carries a `[gold]` tag and look at the chooser.

2. **The page's `Written:` line prints the FOLDED branch number.** On
   `Noelle — Breastplate`, whose sheet is `block 6` then `block 4`:

   ```
   Gain 8 Block. If you are below half HP, gain 6 additional Block.
   Written: Gain 6 Block. If you are below half HP, gain 6 additional Block.
   ```

   The first clause un-folds correctly (8 → the written 6); the branch clause
   does not (6 → 6, where the sheet says 4). So the "card's own written face,
   off its sheet" is a face the sheet does not have, for any row carrying a
   `FoldedBlockVar` / `FoldedDamageVar` branch. Repro: grant
   `KLEEMOD-PROTO_MC_NOELLE_BREASTPLATE`, set Dexterity 2, read its hand row.

3. **The Spark sources line drops a source once a later one lands.** Klee fight
   1: turn start printed `This turn: +1 your opening bank` with `Spark 1`. After
   a set-off the row read `Spark 3` and the line read `This turn: +2 an
   explosion` — the opening bank's +1 gone from both the sentence and the wire's
   `spark_sources`, so the listed sources sum to 2 against a bank of 3. Either
   the opening bank is not a "this turn" source, in which case the first page
   should not have said so, or it is, in which case it should still be there.

4. **`player.master_deck` rows carry neither `keywords` nor `enchantment`.** The
   four Stage readers granted into the deck printed their `description` and
   nothing else; the same cards in a `card_select` carried four keyword rows
   each, and `Ka-pow!` carried its `enchantment` object in the Smith chooser but
   not in `master_deck`. A reader of the deck payload cannot see an enchantment
   the run has. Same family as 8c's draw-pile finding.

5. **The `?` room's Ancient rule and nothing else surprising.** Not a defect:
   recorded because it cost time. On the Klee run a forced `SELF_HELP_BOOK`
   survived one Monster floor and opened on the first `?`, with
   `force_event`'s own translation line printing the Mondstadt dressing on
   arrival (`GUILD_DESKS_RETURNED_COPY`, *The Guild Desk's Returned Copy*) —
   `EB-767` working again, third round running.

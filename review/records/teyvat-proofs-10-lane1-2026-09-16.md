Status: RECORD (deploy proofs, lane 1 half; feasibility only, nothing measured)

# proofs-10, lane 1: the Klee and Furina Stage half — eleven items on `0.2.3581+proto.dirty`

**Nothing here is measured or quotable.** No pre-registration, no blind grading, no slate, no
register row, no re-baseline, no stamp. Nothing was deployed, rebuilt, staged, validated or
committed to the main checkout; no BACKLOG row was edited; the owner's game profile, the Steam
userdata and the run-history store were not touched, and no save file was edited by hand.
**Almost every board below was written by hand.** Cards were granted into decks and hands that
no draft offered, gold was granted, enemy HP was dropped to 1 to close fights a hand-built deck
could not win, energy was topped up for the same reason, and `set_power` placed a Strength, a
Dexterity and a Weak so a fold would be unambiguous — plus the `set_hp player 50 -> 1` that item
1 exists to arrange. Every write is counted in "The board writes" below. A tour here reaches a
**face** — a printed number, a wire field, a page line, a pixel — and never a number anyone may
quote. `bridge.GRANT_GUARDRAIL` governs: *nothing measured on such a board is comparable to any
soak, any run, or any other board.*

**Two `n = 1` limits, stated rather than left to be noticed.** One enchant event per run, one
mode chooser per reading, one death. And **item 1's audio half cannot be checked from here at
all** — this agent has no ears; §1 says exactly what was and was not observed rather than
rounding up.

**Lane discipline.** Lane 1 only, port 15527, the disposable profile
(`%LOCALAPPDATA%\gits-lanes\lane1`). A `tasklist | findstr SlayTheSpire2` before the first
launch showed **no process at all**. Launch 1's embark then reported a game already up
(pid 28380, lane 0's, started between that check and the launch) and **reused the shared bridge
rather than rewriting a dll that game held**; nothing here ever touched that process, its
window, its log or its sidecar, and no focus or z-order change was made. Every kill was
`understudy.embark --teardown --lane 1`, which kills the pid its own sidecar recorded (7716,
then 13032). No `taskkill /IM` was issued, and both frames were captured **by pid**. After the
last teardown `tasklist` showed no `SlayTheSpire2.exe` at all.

**Installed, off `mods\klee\manifest.json`:** `0.2.3581+proto.dirty`, `min_game_version`
`0.111.0`, BaseLib `3.4.7`. The installed `klee.dll` is byte-identical to
`klee-mod/dist/klee/klee.dll` (md5 `e3322a6340b70b802a847b49c2ca2da5`), so the build under test
is the one main just shipped. The manifest's own description names Klee, Furina, reactions and
Companion cards and **does not name Kokomi**, which matches the deploy's arms
(`klee,companion,furina-stage,teyvat`, Kokomi OFF): **no Kokomi run was embarked from this
lane.**

**Frames:** `review/qa/proofs-10-lane1-2026-09-16/`, two frames with
`frames-manifest.jsonl`. **EB-788's fix is live and the manifest row says so:** both rows carry
`"complete": true` with `"complete_note": "the frame covers the whole client area"`,
`client_size` `3842 2160`, `render_extent` `3842 2160`, `render_scale` `[1.0, 1.0]`, route
`printwindow`. Neither frame is a crop.

## The one-line verdicts

| # | item | verdict |
|---|---|---|
| 1 | `EB-159` a modded player's death is heard and waited for | **PASS on the waited-for half, NOT PROVEN on the sound** |
| 2 | `EB-787` a Nimble Barbara prints Block 7 and rider 3 | **PASS** |
| 3 | `EB-789` + `EB-793` the enchanted face in a pile row and a `master_deck` row | **PASS**, both |
| 4 | `EB-791` no raw `[gold]` on a mode card's title in-game | **PASS** |
| 5a | `EB-792` the intent caveat no longer contradicts the breakdown line | **PASS** |
| 5b | `EB-795` `Written:` prints the sheet's literal on a branch face (6 and 4) | **PASS** |
| 6 | `EB-794` the shop removal grid marks the picked row `selected: true` | **PASS** |
| 7 | `EB-796` the Spark sources line lists every source of the fight | **PASS**, across two turns |
| 8 | `EB-287` the Bomb tip AND the glossary row both say a second Bomb joins | **PASS** |
| 9 | `EB-780` an upgraded Curtain Rise under Weak 3 prints one pair | **PASS on the row's acceptance; a second, contradicting pair prints in the option TITLES — off-list 1** |
| 10 | `EB-779` the chooser hint does not say `confirm`, one `choose` resolves | **PASS**, both halves |
| 11a | `EB-734` a chooser row carries the tag its hand entry carries | **PASS**, on the shop's removal grid |
| 11b | `EB-84` the no-override (`Swift`) shape on a mod Power | **PASS** |
| 11c | `EB-84` the `souls_power` → local Exhaust shape | **NOT DONE — no door in this event** |

## The launch table

**Two embarks, both lane 1, both on port 15527.** The driver is scratch (`drv.py`, `nav.py` and
short step scripts), kept out of the tree as proofs-6 through -9 kept theirs; it opens the run
with `understudy.embark` and then drives the wire directly, with `blindplay observe` / `act` for
every page reading. **No stall, no crash, no `DIAG` line, no truncated archive and no epoch
blocker on either launch.**

| # | stamp | pid | character | seed | act | what it was for |
|---|---|---|---|---|---|---|
| 1 | `20260916-163917` | 7716 | Klee | `1GQ14VG4JFT4` | LIYUE | items 1, 2, 3, 5a, 5b, 6, 7, 8, 11a |
| 2 | `20260916-165037` | 13032 | Furina Stage | `5R5818GEATCJ` | LIYUE | items 4, 9, 10, 11b |

Both teardowns archived **lane 1's own** `godot.log` (`EB-785` still holds):
`understudy/logs/godot/20260916-163917-7716.log` line 193 and
`understudy/logs/godot/20260916-165037-13032.log` line 194 both open
`User Data Directory: C:/Users/Monty/AppData/Local/gits-lanes/lane1/SlayTheSpire2`.

## The board writes, counted

Read off each launch's own archived `godot.log` (`[GItS] debug_state:` / `[GItS] give_card:`),
which is the mod's record rather than the driver's arithmetic. **The mod logs a write that MOVED
a value and not one that did not**, so the driver issued more calls than these lines count —
repeat `set_hp <enemy> 1` on a body already at 1, and repeat `set_energy 3` on full energy, are
the two shapes that leave no line. Every logged write is listed rather than summarised, because
there are few enough to list.

| launch | the writes, in order |
|---|---|
| 1 Klee | `give_card` Barbara → Deck; `give_card` Noelle → Deck; `force_next_event LIYUE SELF_HELP_BOOK`; `set_power CORPSE_SLUG_1 STRENGTH 0→3`; `set_power player DEXTERITY 0→2`; `give_card` Ka-pow! → Hand; `give_card` Jumpy Dumpty → Hand; `give_card` Ka-pow! → Hand; `set_hp CORPSE_SLUG_0 8→1`; `set_energy 0→3`; `give_card` Courtroom Drama → Deck; `set_hp SEAPUNK_0 45→1`; `give_gold 900 (99→999)`; `set_hp player 50→1` |
| 2 Furina | `give_card` Curtain Rise (upgraded) → Hand; `set_power player WEAK 0→3`; `set_power player WEAK 3→0`; `set_power player WEAK 0→3`; `set_hp SEAPUNK_0 39→1`; `set_energy 2→3`; `give_card` Courtroom Drama → Deck; `force_next_event LIYUE SELF_HELP_BOOK`; `set_hp SLUDGE_SPINNER_0 38→1`; `set_energy 3→3` |

`skip_act` was **not** used on either launch, so no floor was skipped and no roll was suppressed.

## 1. `EB-159` — a modded player's death — PASS on the wait, NOT PROVEN on the sound

The row's acceptance is *"a modded death is heard and waited for"*. Those are two claims and
this look can answer one of them.

**The board.** Launch 1, act 1 floor 5, Klee against one `SLUDGE_SPINNER_0` whose intent was an
8-damage `OIL_SPRAY_MOVE`. `set_hp player 50 -> 1` (**1 write, disclosed**), Block 0, then
`end_turn`. **The speed override was turned OFF first** (`set_speed(False)`, back to the
captured `FastMode=Fast`, `TimeScale=1`) so nothing below is a 3× compression of the wait.

**What the wire says.** Polled every ~0.12 s from the `end_turn`:

| t (s) | `state_type` | player HP |
|---|---|---|
| 0.05 – 1.16 | `monster` | 1 |
| 1.31 | `game_over` | 0 |

The wire flips from HP 1 to HP 0 and from `monster` to `game_over` in the SAME poll, so **the
wire cannot show a death wait**: there is no HP-0-still-in-combat window on it to measure. That
is the honest bound on this half, and it is why the frame below is the reading rather than a
timing table.

**What the screen says, at the poll where the wire first said `game_over`**
(`frame-20260916-164937-eb159-modded-player-death.png`, captured by pid 7716):

- the header reads **`0/62`**;
- the **client is still on the combat board**, not the game-over screen: the Sludge Spinner is
  still drawn at `33/33`, the `Enemy Turn` banner is still up, the retained `Ka-pow!` is still in
  hand, the floating **`8`** from the killing hit is still on screen;
- **Klee's body is still drawn**, under the red death vignette, with her health bar replaced by
  the word **`Dead`**.

So at the instant the game's own state says the run is over, the client is **holding on the
combat board with the modded body drawn and marked dead** — which is the behaviour a non-zero
reported death length produces and is what a spine-less body did not get before `#582`. That is
the "waited for" half, observed rather than inferred from code.

**The sound is NOT PROVEN and cannot be from here.** `ModdedPlayerDeathSeam.Cover` calls
`SfxCmd.PlayDeath(entity.Player)` and writes no log line, the game logs no SFX, and this agent
has no audio. The archived log's death path is clean and complete and that is all it can say:

```
[INFO] CHARACTER.KLEEMOD-KLEE has lost to encounter ENCOUNTER.SLUDGE_SPINNER_WEAK. That's 2 losses
[INFO] CHARACTER.KLEEMOD-KLEE has died to a MONSTER.SLUDGE_SPINNER. That's 2 losses
```

with no exception, no Harmony error and no `AssetLoadException` anywhere near it. **A person at
the machine is what the audio half wants**, and it is one `set_hp player 1` and one end turn
away.

## 2. `EB-787` — a Nimble Barbara moves the Block and never the rider — PASS

`give_card` is the wrong door for this: **it takes no enchantment parameter**
(`bridge.give_card(card_id, count, upgraded, pile)`) and `debug_state` has no enchant op, so the
face was reached the long way, through the event.

Launch 1: `give_card KLEEMOD-PROTO_MC_BARBARA_FRONT_ROW_SEAT` into the deck at Neow, then
`force_next_event SELF_HELP_BOOK` and the Liyue dressing *Six Contracts to a Better You* at
floor 2. Option 2, **Read a Random Passage — "Choose a Skill to Enchant with Nimble 2"** — and
Barbara picked out of the six-row chooser.

| reading | before | after |
|---|---|---|
| the card's printed face | `Hexerei. Gain 5 Block. Apply Hydro twice. Whenever a Bomb goes off this turn, gain 3 Block.` | **`… Gain 7 Block … gain 3 Block.`** |
| `enchantment` on the wire | absent | `{"id": "NIMBLE", "name": "Nimble", "amount": 2, "shows_amount": true}` |
| Block actually gained when played | — | **7** (`player.block` 0 → 7 on the play, no Dexterity on that board) |

**The printed Block moved 5 → 7 and the rider stayed at 3**, which is the row's acceptance word
for word, and the payout matched the face. The sheet is `docs/prototype-surface.yaml:368`
(`block: 5`, `mc_front_row_seat` amount `3`).

## 3. `EB-789` and `EB-793` — one face, in the pile and in the deck list — PASS, both

Same enchanted Barbara, read in three places on the same run.

**`EB-793`, the `master_deck` row.** The thinness the row was filed on is gone on every row of
every screen read this round — a `master_deck` row now carries `id`, `type`, `cost`,
`star_cost`, `description`, `rarity`, `is_upgraded`, `keywords` and `pile`. On the enchanted
copy it also carries the enchantment:

```json
{"id": "KLEEMOD-PROTO_MC_BARBARA_FRONT_ROW_SEAT", "name": "Barbara — Front Row Seat",
 "rarity": "Common", "is_upgraded": false,
 "description": "Hexerei. Gain 7 Block. Apply Hydro twice. Whenever a Bomb goes off this turn, gain 3 Block.",
 "keywords": [… "Hexerei", "Nimble", "Block", "Applies Hydro"],
 "enchantment": {"id": "NIMBLE", "name": "Nimble", "amount": 2, "shows_amount": true},
 "pile": "Deck"}
```

That is `id`, `is_upgraded`, `keywords` and `enchantment` live, which is the acceptance.

**`EB-789`, the pile row against the hand row.** In the next fight Barbara was dealt into hand,
read, played, and read again out of the **discard pile**. The two rows are the same face:

| field | hand row | discard-pile row |
|---|---|---|
| `id` | `KLEEMOD-PROTO_MC_BARBARA_FRONT_ROW_SEAT` | same |
| `description` | `… Gain 7 Block …` | **`… Gain 7 Block …`** |
| `is_upgraded` | `false` | `false` |
| `keywords` | `Sparks from your Companion, Bomb, Hexerei, Nimble, Block, Applies Hydro` | **identical, Nimble included** |
| `enchantment` | `NIMBLE 2` | **`NIMBLE 2`** |

**Pile and hand print one face**, and the face they print is the enchanted one (7, not the
sheet's 5) — which is the exact defect the row was opened on (Gain 5 in the pile, Gain 7 in hand
a turn later). The draw pile was read on the same state and carries the same shape
(`{"id": "DEFEND_IRONCLAD", …, "rarity": "Basic", "is_upgraded": false, "keywords": […],
"pile": "Draw"}`).

## 4. `EB-791` — no raw markup on a mode card's title, in the game — PASS

Launch 2, Furina Stage, act 1 floor 1. An upgraded `Curtain Rise` played into its mode chooser.

**On the wire**, mode B's name is now `"Spend 3: deal 13 instead+"` — the `[gold]` / `[/gold]`
pair proofs-9 read there is gone.

**On the screen** (`frame-20260916-165245-eb791-eb780-curtain-rise-mode-chooser.png`, captured
by pid 13032, whole client area): the right-hand option card's title banner draws
**`Spend 3: deal 13 instead+`** with no bracket anywhere on it, while the body line an inch
below renders the same word `Spend` in gold. The left card reads `Deal 7 damage+`. That is the
row's acceptance — *no generated mode-face title carries a rich-text tag* — met on the one
surface it was ever visible on, the pixels.

*The title is still wrong about its NUMBER, which is a different defect and is off-list 1 below.*

## 5. `EB-792` and `EB-795`

### 5a. `EB-792` — the intent caveat — PASS

Launch 1, act 1 floor 1, two Corpse Slugs. `set_power CORPSE_SLUG_1 STRENGTH_POWER 3` (**1
write**) so the feed would carry a fold:

```json
{"label": "6x2", "breakdown": {"base_damage": 3, "folded_damage": 6, "repeats": 2,
                               "total_damage": 12, "modifiers": ["Strength"]}}
```

The page's intent line prints the fold — *"the game folded **Strength** into that: it is 3 on
the move and 6 after — 6 x 2 is 12 if every hit lands"* — and the italic paragraph at the foot
of "The other side" now reads:

> *An intent's number is the one figure the game draws on that icon … An enemy carrying Strength
> whose figure does not move is the game's own figure not moving — **and where the feed carries
> the game's own base, the figure its hooks arrived at and the models it folded in, the clauses
> printed beside that intent above name all three, so what is inside the number is read off the
> game rather than guessed at here.***

The sentence the row was filed on — *"the feed carries no base, no modifier list and no
breakdown"* — is **not on the page**. A board with a breakdown never prints the no-breakdown
sentence, which is the acceptance.

### 5b. `EB-795` — the `Written:` line on a branch face — PASS

Same board. `give_card KLEEMOD-PROTO_MC_NOELLE_BREASTPLATE` into the deck and
`set_power player DEXTERITY_POWER 2` (**1 write**) so the printed face would differ from the
sheet's. The hand row on the blind page:

```
- **Noelle — Breastplate** — cost 1, skill
    Gain 8 Block. If you are below half HP, gain 6 additional Block.
    Written: Gain 6 Block. If you are below half HP, gain 4 additional Block.
    (the line above this one is what the board is printing now; this is the card's own written
     face, off its sheet -- the difference is the board's.)
```

**`Written:` reads 6 and 4**, which is `docs/prototype-surface.yaml:576` exactly
(`{op: block, amount: 6}` and the branch `{op: block, amount: 4}`), against the board's folded 8
and 6. proofs-9 lane 0 read that same line as "6 … 6", the branch clause un-folded; it is
un-folded correctly now. A second, un-arranged instance landed later the same run on the
enchanted Barbara: printed `Gain 7 Block`, `Written: … Gain 5 Block`, the sheet's literal
against the Nimble face.

## 6. `EB-794` — the removal grid marks the picked row — PASS

Launch 1, act 1 floor 4, a Liyue shop with a `card_removal` item, bought for 75 gold after
`give_gold 900` (**1 write**) on a 13-card deck.

| reading | value |
|---|---|
| prompt | `Choose a card to Remove.` |
| `screen_type` | `select` |
| `card_select.cards` length / `grid_total` / `grid_complete` | 13 / 13 / `true` |
| after `select_card index=3` | **`{"name": "Strike", "selected": true}`**, and every other row `false` |
| `can_confirm` | `false` → **`true`** |
| after `confirm_selection` | `master_deck` 13 → 12, the Strike gone |

**A removal grid marks the picked row live**, which is the acceptance, and the mark is on the
right row: one row `selected: true`, the pick armed, and the confirm removed that card. This is
proofs-9's defect 4 (no row ever carrying `selected: true` on the removal grid, only on the
Smith's) closed.

## 7. `EB-796` — the Spark sources line keeps the whole fight — PASS

Launch 1, act 1 floor 1, Klee, a spend-free fight. The relic in play is `Pounding Surprise`
(*whenever a Bomb goes off, gain 1 Spark*).

| moment | bank | the page's sources line |
|---|---|---|
| turn 1, before anything | `Spark 1` | `So far this fight: +1 your opening bank.` |
| turn 1, after `Jumpy Dumpty` + `Ka-pow!` (one explosion) | `Spark 2` | **`So far this fight: +1 your opening bank, +1 an explosion.`** |
| **turn 2**, after a second Jumpy Dumpty and two more explosions | `Spark 4` | **`So far this fight: +1 your opening bank, +3 an explosion.`** |

The third row is the one that matters: **the turn-1 opening bank is still in the sentence on
turn 2**, which is precisely the filter the row removed (`GitsSparkSourcesState` keeping only
the newest turn). Every gain behind the current bank is listed and the listed gains sum to the
bank (1 + 3 = 4) on a fight where nothing was spent. The page also says "So far this fight:", the
wording the row's **Built** note promises.

## 8. `EB-287` — the Bomb tip and the glossary row both say it — PASS

Launch 1, same page, both readings on one screen.

**The keyword tip**, under `Jumpy Dumpty` in the hand:

> *Bomb* — A charge on an enemy: grows 4 a turn, and goes off when Set off or as a Mine; **a
> second Bomb joins the first.** Block stops it. …

**The glossary row**, under "Words on this screen":

> **Bomb** — A charge on an enemy: each grows 4 a turn, and goes off when Set off or as a Mine;
> **a second Bomb joins the first.** Block stops it. …

**Tip and glossary both say merging**, in the same words, which is the acceptance. (The two
differ by one word elsewhere — the glossary says "each grows 4 a turn" where the tip says "grows
4 a turn" — which is the plural row reading naturally and is not the clause the row is about.)

## 9. `EB-780` — an upgraded chooser under Weak — PASS on the acceptance

Launch 2. `give_card 'Curtain Rise' upgraded=True` into hand and `set_power player WEAK_POWER 3`
(**2 writes**). The sheet is `docs/prototype-surface.yaml:1656`, base 7 / 13.

**The hand, read both ways, to fix what the right answer is:**

| board | `Curtain Rise` | `Curtain Rise+` |
|---|---|---|
| no Weak | `Choose one: Deal 7 damage \| Spend 3: deal 13 instead.` | `… Deal 10 damage \| … deal 16 instead.` |
| Weak 3 | `… Deal 5 damage \| … deal 9 instead.` | **`… Deal 7 damage \| … deal 12 instead.`** |

so the upgraded, Weak-folded pair is **7 and 12** (10 × 0.75 = 7.5 → 7; 16 × 0.75 = 12).

**The chooser, opened from that hand:**

```json
[{"id": "…CURTAIN_RISE_MODE_A", "name": "Deal 7 damage+",            "description": "Deal 7 damage",            "is_upgraded": true},
 {"id": "…CURTAIN_RISE_MODE_B", "name": "Spend 3: deal 13 instead+", "description": "Spend 3: deal 12 instead", "is_upgraded": true}]
```

and on the frame the two option cards' **bodies** read `Deal 7 damage` and
`Spend 3: deal 12 instead`, with the `12` drawn in the green the game uses for a moved number,
above the parent `Curtain Rise+` still showing `Deal 7 … deal 12` behind them. **The option
faces print the hand's numbers**, which is the row's acceptance and is `#590`'s combat-preview
declaration working: the off-pile face runs the board's hooks now.

**What the row does not cover, and what the screen still does:** the option cards' **titles**
print `Deal 7 damage+` and `Spend 3: deal 13 instead+` — the sheet's literals with a bare `+`
glued on — one line above bodies reading 7 and **12**. So the screen prints **two pairs**, 7/13
and 7/12, and they disagree. That is off-list 1 rather than a failure of this row, which asks
about the faces; it is named here because a reader of this section would otherwise think the
screen is clean.

## 10. `EB-779` — the Spend mode chooser's hint, and one `choose` — PASS, both halves

Same chooser. The italic note the page prints under the two rows is now:

> *One `choose` takes your answer here and closes this screen: there is no confirm button on
> this chooser and no second command to say. Read the options before you choose — the one you
> name resolves immediately.*

**The word `confirm` as an instruction is gone** (it survives only inside "there is no confirm
button"), and the verb list offers `choose "<card title>"` and `choose <number>` and nothing
else. That is proofs-9's residual half — three false clauses telling a seat to say `confirm`
first — closed.

**And one `choose` resolved it:**

```
$ blindplay act "choose 1"
{"ok": true, "verb": "choose", "post": {"action": "select_card", "index": 0},
 "printed": {"card": "Deal 7 damage+", "text": "Deal 7 damage"}, "refusal": ""}
Took: Deal 7 damage+ — Deal 7 damage.
```

and the next state had **no `card_select` at all**, with the Seapunk at 39 from 46 — **7**, the
Weak-folded number the body printed and not the title's 13. No `confirm` was sent and none was
refused.

## 11. `EB-734` and `EB-84`, as their rows narrow them

### 11a. `EB-734` — a chooser row carries the tag its hand entry carries — PASS

The row's next action is *open a chooser while an ENCHANTED card is in the deck*. `give_card`
cannot grant an enchantment (§2) and `SELF_HELP_BOOK` refuses a second visit, so what was opened
is **the run's second deck chooser**: the shop's removal grid at floor 4, two floors after the
enchant, with the Nimble Barbara in the deck. Its row:

```json
{"id": "KLEEMOD-PROTO_MC_BARBARA_FRONT_ROW_SEAT", "name": "Barbara — Front Row Seat",
 "description": "Hexerei. Gain 7 Block. …", "index": 10, "selected": false, "on_screen": true,
 "enchantment": {"id": "NIMBLE", "name": "Nimble", "amount": 2, "shows_amount": true},
 "keywords": [… "Nimble" …]}
```

and the page above it:

```
- **Barbara — Front Row Seat** [Hydro] (Nimble 2) — cost 1, skill
    Hexerei. Gain 7 Block. Apply Hydro twice. Whenever a Bomb goes off this turn, gain 3 Block.
    Written: Hexerei. Gain 5 Block. Apply Hydro twice. Whenever a Bomb goes off this turn, gain 3 Block.
```

**The tag is on the wire and on the page**, with the enchanted 7 against the written 5 proving
it is the same card — and **the other twelve rows of that grid carry no tag at all**, which is
the comparison that makes it worth anything. (This is the same answer lane 0 reached on the
Smith's grid; it is a second screen, on a mod card, in a second run.)

### 11b. `EB-84` — the no-override (`Swift`) shape — PASS

Launch 2, Furina. `give_card KLEEMOD-COURTROOM_DRAMA` into the deck **before** the event page
opened, then `force_next_event SELF_HELP_BOOK` and the Liyue dressing at floor 3. With a Power
in the deck the third option — *Read the Entire Book — "Choose a Power to Enchant with Swift
2"* — was **unlocked**, where every earlier look found it locked.

Taking it landed the enchantment with **no chooser screen at all** (see off-list 3), and the
deck row after:

```json
{"id": "KLEEMOD-COURTROOM_DRAMA", "type": "Power", "rarity": "Uncommon",
 "description": "Your first Elemental Reaction each turn applies 1 Vulnerable and 1 Weak to its
                 target. The Vulnerable moves that hit. Draw 2 cards the first time this is played.",
 "enchantment": {"id": "SWIFT", "name": "Swift", "amount": 2, "shows_amount": true}}
```

**A mod Power is eligible for `Swift` on the game's own terms** — the shape `GAME_RULES` calls
"no card-level restriction at all" — and the enchantment's rider is folded into the printed
face (*"Draw 2 cards the first time this is played."* appended). The honest limit: with exactly
one eligible card there was **no deck screen to read**, so the eligibility is read off the
result rather than off a list of offers. Two of `EB-84`'s four shapes are now watched (this one
and lane 0's attack trio), plus proofs-8a's Nimble-on-Block, which this round also re-saw: the
Nimble chooser offered **six rows of thirteen** — four `Defend`s, Barbara and Noelle — and
excluded `Jumpy Dumpty` (a Skill that gains no Block), `Courtroom Drama` (a Power) and every
Attack. Three of four.

### 11c. `EB-84` — the `souls_power` → local Exhaust shape — NOT DONE

`SELF_HELP_BOOK` offers three options and they are Sharp-on-Attack, Nimble-on-Skill and
Swift-on-Power. **There is no Souls' Power door in this event at all**, so no number of runs of
this event reaches that shape; it needs `SPIRALING_WHIRLPOOL` or another grantor, and neither was
in reach. This is the same wall lane 0 hit and it is structural, not a budget miss.

## Defects found that are not on any row above

Raised here, not filed — a register row is [USER]'s to mint or Claude's under the hygiene rule,
and this is a record.

1. **A mode card's TITLE prints the SHEET LITERAL, not the board's number, and appends a bare
   `+`.** On the frame and on the wire, the chooser's right-hand card is titled
   `Spend 3: deal 13 instead+` directly above a body reading `Spend 3: deal 12 instead`. The
   13 is `docs/prototype-surface.yaml:1665`'s label, unupgraded and unfolded; the 12 is the
   board's. The unupgraded card does it too (`Spend 3: deal 13 instead` over
   `Spend 3: deal 9 instead` under Weak 3), so the title is the raw label in every case and the
   `+` is glued on by the upgrade naming rather than by the label. **This is worse than
   proofs-9's defect 1, which the blind page stripped invisibly:** the blind page prints the
   title too, so a seat reads
   `- **Spend 3: deal 13 instead+** (upgraded) — cost 0, skill` / `Spend 3: deal 12 instead`
   and has two numbers for one option. `EB-791` fixed the markup in that label; the number is
   the other half. **Repro:** Furina Stage run, `set_power player WEAK_POWER 3`, play an
   upgraded `Curtain Rise`, read the option titles against their bodies.
   Frame: `review/qa/proofs-10-lane1-2026-09-16/frame-20260916-165245-eb791-eb780-curtain-rise-mode-chooser.png`.

2. **`SELF_HELP_BOOK`'s option locks do not re-evaluate while the page is open.** On launch 1 the
   Swift option was locked (no Power in the deck); `give_card KLEEMOD-COURTROOM_DRAMA` put a
   Power in the deck, the next `get_state` showed it in `master_deck` with `"type": "Power"`, and
   the option stayed `"is_locked": true`. On launch 2 the same grant made **before** the event
   page opened left it unlocked. So the lock is computed once at open. Not necessarily a bug —
   but it is a fact any driver arranging an eligibility shape has to know, and it cost this round
   one visit.

3. **An enchant offer with a single eligible card resolves with no screen.** Taking
   "Read the Entire Book" with one Power in the deck produced **no `card_select` state at all**:
   the next state was the event's `Proceed` page with the enchantment already on the card. A
   driver waiting for a chooser waits forever, and a look that wanted to *read* the offer list
   gets nothing to read. Seeding two eligible cards is the workaround.

4. **`frames.capture` labels every frame `lane0` unless the caller says otherwise.**
   `understudy/frames.py:712` is `"instance": instance or "lane0"`, and `instance` defaults to
   `""`. Both frames in this record were captured **by lane 1's pid, from a process with
   `GITS_LANE=1` set**, and both manifest rows say `"instance": "lane0"`. The pid field is right,
   so the row is not unrecoverable — but the one field a reader would use to tell which lane a
   frame is of is wrong by default, which is the same class of defect `EB-785` closed for the log
   archive.

## What could not be done, and why

- **`EB-159`'s audio half.** No ears here; §1 says what was observed instead and names the
  one-line repro for a person at the machine.
- **`EB-84`'s `souls_power` shape.** No door in the only enchant event in reach (§11c).
- **A second enchant chooser in one run.** `SELF_HELP_BOOK` still refuses a second visit and
  `SPIRALING_WHIRLPOOL` was not in reach; `EB-734` was answered on the removal grid instead, and
  says so.
- **Nothing was framed except the two frames named.** Every other claim in this record is wire
  payload, page text, or a line in an archived log, each checkable against the file or field named
  beside it. Pages and state snapshots were kept in the session scratchpad, which is not the tree,
  and the driver (`drv.py`, `nav.py`) is scratch and is not committed, as proofs-6 through -9 did
  with theirs.

## What else the round learned, for the next driver

- **`give_card` cannot grant an enchantment and `debug_state` has no enchant op.** Every
  enchanted face is reached through `SELF_HELP_BOOK`, one option per run, so a round that wants
  one should decide which of the three options it is spending the run on before it forces the
  event — and should grant whatever card that option needs **before the page opens** (off-list 2).
- **A Weak / Dexterity board is the cheapest fold rig.** One `set_power` on the player makes
  every printed number on every card differ from its sheet, which is what the `Written:` line,
  the upgrade preview and the chooser's preview all need to be readable at all.
- **The hand is at `state["player"]["hand"]`, not under `battle`.** `battle` carries only
  `round`, `turn`, `is_play_phase` and `enemies`; `hand`, `draw_pile`, `discard_pile`,
  `exhaust_pile`, `master_deck`, `status`, `relics` and `energy` are all on `player`. A card row's
  playability is `can_play` / `unplayable_reason`, not `is_playable` (which does not exist and
  reads `None`).
- **`set_hp <enemy> 1` plus `set_energy 3` plus one Attack is the whole fight-closing idiom**, and
  the mod logs only the writes that MOVED a value, so a repeat costs nothing and leaves no line.
- **The wire cannot see a death animation.** HP 1 → 0 and `monster` → `game_over` land in the
  same poll at 0.12 s resolution; the client is a whole death animation behind the wire at that
  moment. Frame it, do not time it.

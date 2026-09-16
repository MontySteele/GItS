Status: RECORD (deploy proofs, lane 1 half; feasibility only, nothing measured)

# proofs-9, lane 1: the #569 wire fields, #574's three fixes, the grant ops and six rows

**Nothing here is measured or quotable** — no pre-registration, no blind grading, no slate, no
register row, no re-baseline. Nothing was deployed, rebuilt, staged or committed to the main
checkout; the owner's game profile, the Steam userdata and the run-history store were not
touched, and no save file was edited by hand. **Twice over, nothing here is comparable to
anything.** `skip_act` is not rng-neutral and says so — the floors it skips never roll — and it
was used once. And **most of the boards below were written by hand**: cards granted into decks
and hands that no draft offered, relics and potions granted straight into the inventory, gold
granted, enemy HP dropped to 1 to close fights the deck could not win, player HP topped up as
life support, and `set_power` used to place a Strength, a Hydro aura and to clear a Vulnerable
so a re-application would be unambiguous. Every write is counted in "The board writes" below.
A tour here reaches a **face** — a wire field, an event's text, a page's rows — and never a
number. `bridge.GRANT_GUARDRAIL` governs: *nothing measured on such a board is comparable to
any soak, any run, or any other board*.

**Another agent was driving lane 0 (pid 41464) throughout**, and nothing here ever touched its
process, its log or its sidecar. Every kill was `understudy.embark --teardown --lane 1`, which
kills by the pid its own sidecar records; no `taskkill /IM` was issued and the one frame was
captured **by pid**. A `tasklist | findstr SlayTheSpire2` before the first launch showed **no
process at all**, so nothing was running that a lane sidecar could not claim.

**Installed, off `mods\klee\manifest.json`:** `0.2.3541+proto.dirty`, `min_game_version`
`0.111.0`, BaseLib `3.4.7`, arms `klee,companion,kokomi,furina-stage,teyvat`, `TeyvatFrame`
ON. The installed `klee.dll` is byte-identical to `klee-mod/dist/klee/klee.dll`
(md5 `475eaf7beb07027d793d2d80f7f2461c`), so the build under test is the one main just shipped.

**Frames:** `review/qa/proofs-9-lane1-2026-09-16/` (one, and its README says what it is).

## The one-line verdicts

| # | item | verdict |
|---|---|---|
| 1 | The #569 wire fields, every reflection seam non-null on a live board | **PASS**, all six |
| 1a | `EB-607` `intents[].breakdown` | **PASS** |
| 1b | `EB-323` `intents[].target_side` | **PASS**, all three values seen |
| 1c | `EB-447` `player.master_deck` on non-combat states | **PASS** |
| 1d | `EB-350` `card_select.cards` + `grid_complete` / `grid_total` past 25 rows | **PASS**, on the removal grid AND the Smith's |
| 1e | `EB-374` `card_reward.alternatives`, the `sacrifice` verb, `alternative_index` | **PASS** |
| 1f | `EB-349` / `EB-611` `player.resolutions` | **PASS**, both halves |
| 2 | #574's three | |
| 2a | `EB-784` Slippery Bridge prints `{HpLoss}` matching the click cost | **PASS** |
| 2b | `EB-785` a lane-1 teardown archives LANE 1's `godot.log` | **PASS**, three teardowns |
| 2c | `EB-786` the two Curtain Rise mode faces show portraits in `card_atlas` | **PASS** |
| 3 | `hp_settled` true on map screens (#576) | **PASS** |
| 4 | The grant ops `give_relic` / `give_potion` / `give_gold` | **PASS** |
| 5 | `EB-116` Pael's Eye extra turn reopens Courtroom Drama's window | **PASS** |
| 6 | `EB-684` Flex Potion's fold is gone next turn | **PASS** |
| 7 | `EB-459` Neow's Arcane Scroll under Kokomi adds a card | **PASS** |
| 8 | `EB-363` The Future of Potions under all three arms | **PASS**, all three |
| 9 | `EB-779` bridge half | **MIXED — the bridge half PASSES, the page's hint half FAILS** |

## The launch table

**Three embarks, all lane 1 (the disposable profile), all on port 15527.** The driver is
scratch (`drv.py`, `climb.py`), kept out of the tree as proofs-6, -7 and -8a kept theirs; it
opens the run with `understudy.embark` and then drives the wire directly. **No stall, no crash,
no `DIAG` line, no truncated archive, and no epoch blocker on any of the three** — the recovery
proofs-8a needed twice was not needed once.

| # | stamp | pid | character | seed | acts | what it was for |
|---|---|---|---|---|---|---|
| 1 | `20260916-143341` | 12100 | Klee | `AQMK5A19HZZA` | MONDSTADT → INAZUMA (one `skip_act`) | items 1, 2a, 3, 4, 5, 6, and `EB-363`'s Klee arm |
| 2 | `20260916-145729` | 39624 | Kokomi | (A3) | LIYUE | item 7, item 1d on a real removal grid, `EB-363`'s Kokomi arm |
| 3 | `20260916-150046` | 39476 | Furina | `64WJ72QL8Z14` | MONDSTADT | items 2c, 9, `EB-363`'s Furina arm |

## The board writes, counted

Read off each launch's own archived `godot.log` (`[GItS] debug_state:` / `[GItS] give_card:`
lines), which is the mod's record rather than the driver's arithmetic. A `give_card` line is
one CARD, so a single ten-card call is ten lines.

| launch | `set_hp` | `set_power` | `set_energy` | `give_relic` | `give_potion` | `give_gold` | `give_card` | `force_next_event` | `skip_act` |
|---|---|---|---|---|---|---|---|---|---|
| 1 Klee | 27 | 5 | 12 | 3 | 3 | 1 | 35 | 2 | 1 |
| 2 Kokomi | 4 | 0 | 3 | 1 | 2 | 1 | 28 | 1 | 0 |
| 3 Furina | 1 | 0 | 3 | 0 | 2 | 0 | 2 | 1 | 0 |

## 1. The #569 wire fields — every seam non-null

The whole point of the item is that these seams **fail silently**: they answer null and the
page falls back to what it printed before, so a deploy that leaves them null looks like a
no-op. None of them is null on this build.

### 1a. `EB-607` — `battle.enemies[].intents[].breakdown` — PASS

Launch 1, act 1 floor 1, one `NIBBIT_0` (Wooden Shield Hilichurl Guard). Before any write:

```json
{"type": "Attack", "target_side": "you", "label": "12",
 "breakdown": {"base_damage": 12, "folded_damage": 12, "repeats": 1,
               "total_damage": 12, "modifiers": []}}
```

`set_power NIBBIT_0 STRENGTH_POWER 3` (**1 `set_power` write**, disclosed) and the same field
moved with it:

```json
{"label": "15",
 "breakdown": {"base_damage": 12, "folded_damage": 15, "repeats": 1,
               "total_damage": 15, "modifiers": ["Strength"]}}
```

That is the row's acceptance — *the page moves as the feed moves* — and the page moved with it,
printing the fold clause the PR describes:

> Intent: Aggressive (Attack) — the number on its icon is 15 — This enemy intends to Attack for
> 15 damage. — the game folded **Strength** into that: it is 12 on the move and 15 after

A second, un-arranged reading landed on launch 1's act-2 elite, `INFESTED_PRISM_0`, with **no
board write at all**: `base_damage: 15, folded_damage: 25, modifiers: ["Tainted"]` against a
printed label of 25. So the fold is read off the game's own modifier list and not off Strength
alone.

### 1b. `EB-323` — `intents[].target_side` — PASS, and all three values were seen

- `Attack` → `"you"` (the Hilichurl above, and the Prism).
- `Defend` → `"its own side"` (`INFESTED_PRISM_0`).
- **`Buff` → `"its own side"`** (`INFESTED_PRISM_0`, later in the same fight) — which is the
  exact case the row was filed on (`Empower (Buff)` naming nobody on a board of three).

The page prints it with the refusal the PR promised beside it: *"this part lands on its own
side, and the feed carries no target for an intent part, so this page cannot say which body"*.
`breakdown` is correctly **absent** on the Defend and the Buff parts. **No board write.**

### 1c. `EB-447` — `player.master_deck` on non-combat states — PASS

`master_deck` is present and correct on **every** screen read this round: `event` (Neow, 10
cards), `map` (10), `rewards`, `card_reward`, `card_select`, `rest_site`, `shop`, and inside
combat as well. The count was checked against a known quantity rather than against itself: on
launch 1 a 10-card Klee starter plus `give_card` of 10 + 10 + 10 read back **40**, then 39
after a Slippery Bridge removal, then 39 with one row upgraded in place. On launch 2 an 11-card
Kokomi deck plus 28 granted cards read **39**, then **38** after a shop removal. The map screen
the row names reads the master deck and not the last fight's pile union: no `Dazed` appeared,
and the list is the run's own.

*One thing a reader should know, not a defect on this row:* a `master_deck` row carries only
`name`, `cost`, `star_cost` and `description`. No `id`, no `rarity`, no `upgraded`, no
`keywords`. That is the same thinness 8c raised about `draw_pile`; it is listed again under
"defects found that are not on any row" because it bounds what the row can be used for.

### 1d. `EB-350` — the grid carries every card — PASS, on a real removal grid

**The removal grid.** Launch 2, act 1 floor 3, a shop with a `card_removal` item, bought for 75
gold after `give_gold 900` (**1 write**, disclosed) on a deck inflated to 39 by `give_card`:

| reading | value |
|---|---|
| prompt | `Choose a card to Remove.` |
| `card_select.cards` length | **39** |
| `grid_complete` | **true** |
| `grid_total` | **39** |
| `player.master_deck` length | **39** |

That is 39 rows where the pre-fix build printed 25, and the two numbers agree with the
harness's own count. `select_card index=36` — a row **eleven past the old viewport** — answered
*"Toggling card selection: Kurage's Oath"* and `confirm_selection` removed it: the deck went
39 → 38. So the off-screen click through `OnCardClicked` works on a live grid.

**And the Smith's grid, on the other launch.** Launch 1, act 2 floor 9 rest site: 39 rows,
`grid_complete: true`, `grid_total: 39`, prompt `Choose a card to Upgrade.`, `select_card
index=38` → `confirm_selection` → a `Defend+` in the master deck. Both screens, both past 25.

*One small disagreement between the two screens, raised below:* on the **upgrade** grid the
selected row came back `selected: true`; on the **removal** grid no row carried `selected:
true` even though `can_confirm` had flipped to true and the confirm then removed the right
card. One visit each, so this is a single observation on each side.

### 1e. `EB-374` — the reward screen's other button, by name — PASS

`give_relic PAELS_WING` (**1 write**) at Neow, then the first fight's card reward:

```json
"alternatives": [{"index": 0, "name": "Skip"}, {"index": 1, "name": "Sacrifice"}]
```

and the blind page's verb list carried `sacrifice` beside `skip`, which is the half a seat
reads. `skip_card_reward` with `alternative_index: 1` answered *"Taking the card reward's
alternative: Sacrifice"* and the screen closed with the deck unchanged at 10 — a sacrifice and
not a take. **The relic half landed too:** the second sacrifice, at the potions event's card
reward two floors later, paid out — relics went from four to five with **Meal Ticket** added,
which is Pael's Wing's own *"Every 2 sacrifices, obtain a Relic"*. `skip_card_reward` with no
argument still answered *"Taking the card reward's alternative: Skip"*, so the default caller
is unmoved.

### 1f. `EB-349` + `EB-611` — `player.resolutions` — PASS, both halves

**The ledger is live.** Every card played this round filed a row: `card_id`, `card`,
`auto_played`, `carried`, `overflowed`, and `hits` with `target` / `amount` / `blocked` /
`combat_id`. It clears at turn start (read empty on the first read of each new turn).

**`EB-611`, the multi-hit random Set off.** Launch 1, act 2 floor 7, one `SPINY_TOAD_0` carrying
`PROTO_BOMB_POWER 24` placed by three Jumpy Dumptys. `Rapid Fire`
(`KLEEMOD-PROTO_KO_RAPID_FIRE`, *"4 times: Set off a random enemy and deal 3 damage to it."*)
filed **ten ordered hits** in one row — three at 8 (the bombs going off) then seven at 3 — and
the page numbered every one of them:

```
- **Rapid Fire**
  1. **Spiny Toad** -- 8
  2. **Spiny Toad** -- 8
  3. **Spiny Toad** -- 8
  4. **Spiny Toad** -- 3
  …
  10. **Spiny Toad** -- 3
```

The row's acceptance says "four ordered lines"; what this board produced is ten, because the
Set off half fired as well. **The honest limit: the board had ONE enemy on it**, so the *random
target selection* was not exercised — what is proven is that a multi-hit Set off files each hit
in order with its amount, which is the defect the row was opened on (only the after-state
printed). A hallway of three would be a better board and was not reached.

**`EB-349`, the auto-played turn.** `give_relic WHISPERING_EARRING` (**1 write**) — *"Vakuu
plays your first turn"* — then the next fight's turn 1. Five rows, every one
`"auto_played": true`, with the hits filed:

```
- **Jumpy Dumpty** *(the game played this one, not you)*
  Nothing this page can count landed off it.
- **Strike** *(the game played this one, not you)*
  1. **Ovicopter** -- 6
- **Kaboom!** *(the game played this one, not you)*
  1. **Ovicopter** -- 7
```

with the page's closing note: *"The rows above are the turn the game took for you: what it
played, what it aimed at, and what each hit did. An empty hand or unspent energy on the board
below is that turn, not a fault."* That is the Vakuu turn the row asks for, and a seat can
reconcile it.

## 2. #574's three

### 2a. `EB-784` — the Slippery Bridge prints `{HpLoss}` — PASS

Launch 1, act 2 **INAZUMA**, floor 8, forced past the `TotalFloor > 6` gate (the first force at
`TotalFloor=3` was refused by name and printed the gate, which is `force_event`'s own guard
working). The page opened as **`TIDEWORN_CAUSEWAY_AT_MUSOUJIN_GORGE`, *The Tideworn Causeway at
Musoujin Gorge***:

| page | the Hold On row printed | HP before → after |
|---|---|---|
| INITIAL | "Lose **3** HP as the line saws through your grip. …" | 46 → 43 (**3**) |
| HOLD_ON_1 | "Lose **4** HP as the line saws through your grip. …" | 43 → 39 (**4**) |
| HOLD_ON_2 | "Lose **5** HP as the line saws through your grip. …" | not taken |

**The row's acceptance is "page two prints 4" and page two prints 4, and the click cost 4.**
That is the defect proofs-8a found — page two saying 3 while the click cost 4 — gone. The
Cut It Loose row re-rolled correctly across pages too (`Kaboom!` → `Defend` → `Strike`).
**No board write in this section.**

### 2b. `EB-785` — a lane-1 teardown archives lane 1's own log — PASS, three times

Each of the three teardowns copied a log aside, and each one opens with lane 1's tree:

```
User Data Directory: C:/Users/Monty/AppData/Local/gits-lanes/lane1/SlayTheSpire2
```

- `understudy/logs/godot/20260916-143341-12100.log` — line 194.
- `understudy/logs/godot/20260916-145729-39624.log` — line 193.
- `understudy/logs/godot/20260916-150046-39476.log` — line 1.

Against proofs-8a, where five of six archives opened with `C:/Users/Monty/AppData/Roaming/
SlayTheSpire2` — lane 0's tree — this is the row's acceptance met: *a lane-1 archive is lane
1's*. Each archive's contents corroborate it: the Furina launch's archive carries the Furina
mode-chooser lines and no Klee prototype faces, and lane 0 was up and being driven by another
agent the whole time.

### 2c. `EB-786` — both Curtain Rise mode faces draw a portrait — PASS

Launch 3 (Furina Stage), act 1 floor 2, `Curtain Rise` played into a mode chooser:

```json
"cards": [{"id": "KLEEMOD-PROTO_FS_CURTAIN_RISE_MODE_A", "name": "Deal 7 damage", …},
          {"id": "KLEEMOD-PROTO_FS_CURTAIN_RISE_MODE_B", "name": "[gold]Spend[/gold] 3: deal 13 instead", …}]
```

**The log half.** The lane's own live `godot.log`, 1,258 lines over the whole launch:

| line | count |
|---|---|
| `AtlasResourceLoader: Missing sprite … curtain_rise_mode_a` / `_b` **in `card_atlas`** | **0** |
| `AtlasResourceLoader: Missing sprite` (any) | **1** — `'snake_ring' in relic_outline_atlas`, at boot, the same pre-existing line 8a and 8c report |
| `AssetLoadException` | 0 |
| `Element limit reached` | 0 |
| `NCardTrail` | 0 |
| `Expected BoundObject to be a SpineSprite` | 0 |

Against 8c, where the two `furina/kleemod-proto_fs_curtain_rise_mode_a` / `_b` lines were
exactly what a log carried, those lines are gone.

**The pixel half.** `review/qa/proofs-9-lane1-2026-09-16/eb786-curtain-rise-mode-chooser.png`,
captured by pid 39476. Both mode cards carry the parent's illustration (`art_of:
aria_of_recompense`) in the portrait window. That is the mechanical claim and the only one made
off the frame. **The frame is also where off-list finding 1 is read.**

## 3. `hp_settled` on map screens — PASS

proofs-8a's §13 reported the flag **false on every `rewards`, `card_reward` and `map` screen**,
26 of 26, and called it over-broad. On this build it is **true** on all of them. Every read
this round, across three launches:

| screen | `hp_settled` |
|---|---|
| `map` (including the first map after a kill) | **true**, every read |
| `rewards` / `card_reward` immediately after a kill | **true** |
| `event`, `card_select`, `rest_site`, `shop`, in combat | **true** |

Not one `false` was seen anywhere this round, which is worth saying plainly rather than only as
a pass: the flag no longer refuses to promise an HP figure on the one screen a reader most
wants to trust it. Nothing here exercised the *inside-a-fight-that-is-over* window the flag
exists for, so this look says the over-broad reading is gone and does not re-prove 8a's §13
kill-screen case.

## 4. The grant ops — PASS

Each returned, each named its own before/after, and each was confirmed on the next state rather
than on the answer. All three are **grants, not sets**, and `give_gold` is the one the row is
explicit about:

| op | call | answer | next state |
|---|---|---|---|
| `give_gold` | `amount 137` on 99 gold | `"99 -> 236 gold; queued …"`, `granted: 137` | `player.gold` **236** |
| `give_relic` | `PAELS_WING` | `"1 -> 2 relics; queued"` | `relics` gained `PAELS_WING` |
| `give_relic` | `PAELS_EYE`, `ARCANE_SCROLL`, `WHISPERING_EARRING` | same shape | each appeared |
| `give_potion` | `FLEX_POTION`, no slot | `"0 -> 1 potions"` | belt slot 0 |
| `give_potion` | `FIRE_POTION`, `slot: 1` | `"1 -> 2 potions at slot 1"` | belt slot 1 |

Every call carries its `why` into the mod's own log (`[GItS] debug_state: give_potion
SWIFT_POTION 0 -> 1 slot -1 (queued) | why: proofs-9 lane 1 live look EB-363 gate`), which is
how the board-writes table above was built. `debug_state_info` lists all thirteen ops.

**These ops are why five of this record's rows are answerable at all.** proofs-8a's "what could
not be done" named `EB-459`, `EB-363`, `EB-116` and `EB-684` as blocked on exactly this, and
they are all done below.

## 5. `EB-116` — the extra-turn reaction window — PASS

The row wants the window seen reopening, and this is the first time it has been watched rather
than pinned headless. Launch 1, act 1 floor 1, Klee, on a board that is disclosed in full:
`give_relic PAELS_EYE`, `give_card KLEEMOD-COURTROOM_DRAMA` into hand, `give_card
KLEEMOD-KABOOM` into hand (Klee's Ironclad starter Strikes apply no Pyro, so a base Strike
produces no reaction), `set_power NIBBIT_0 HYDRO_AURA_POWER 1` twice to seed the reaction, and
`set_power NIBBIT_0 VULNERABLE_POWER 0` / `WEAK_POWER 0` once to clear the first turn's marks so
a second application could not be mistaken for the first.

| turn | what happened | enemy status after |
|---|---|---|
| 1 | Courtroom Drama played (`CROSS_EXAMINATION_POWER 1` on the player). Hydro aura seeded, `Kaboom!` played → **Vaporize** | `Vulnerable 1`, `Weak 1` — the window fired |
| — | both marks cleared by hand; end turn | `Strength 3` only |
| 2 | **nothing played**, end turn → Pael's Eye fires | — |
| 2 (extra) | hand exhausted (five cards in the exhaust pile), round counter still 2, player HP unchanged, enemy did not act | — |
| 2 (extra) | Hydro aura seeded, `Kaboom!` played → **Vaporize** | **`Vulnerable 1`, `Weak 1`** |

So on the extra turn the once-per-turn window **reopened** and Courtroom Drama's Vulnerable
applied — the failure `ReactionEffects.MarkExtraTurnStart` exists to prevent
(`DealerReactionsThisTurn[dealer]` still 1, `NoteFirstReaction` skipped, the x1.5 dropped). The
hit's own number moved with it: `player.resolutions` filed `Kaboom!` at **15** on the extra
turn against 7 on its face. The `ReactionTriggeredThisTurn`-false half the row names is not
directly readable on the wire; what is readable is its consequence, and the consequence is
right. **Board writes in this section: 3 `set_power`, 0 `set_hp`.**

## 6. `EB-684` — Flex Potion's fold — PASS

Launch 1, same fight. `give_potion FLEX_POTION`, then used in combat:

| moment | raw `player.status` | a Strike's printed face |
|---|---|---|
| before | `SPARK_POWER 1`, `CROSS_EXAMINATION_POWER 1` | `Deal 6 damage.` |
| after `use_potion slot 0` | + `STRENGTH_POWER 5`, `FLEX_POTION_POWER 5` | **`Deal 11 damage.`** |
| next turn | `SPARK_POWER 1`, `CROSS_EXAMINATION_POWER 1` — **neither row present** | **`Deal 6 damage.`** |

The row's acceptance is *faces fold the Strength the body has*, and next turn the body has none
and the face folds none. The defect (the next turn's faces still folding a +5 that had expired)
does not reproduce. **Board writes in this section: 1 `set_hp` life-support top-up before the
end turn; none of it touched the reading.**

## 7. `EB-459` — Neow's Arcane Scroll under Kokomi — PASS

The row's next action is exactly what was done: *with `give_gold` / `give_relic` landing, grant
the scroll's relic directly and read the deck*. Launch 2, Kokomi, at floor 1 before anything
else:

```
before: 10 cards — Strike x4, Defend x4, Kurage's Oath, Slack Water
give_relic ARCANE_SCROLL -> "1 -> 2 relics"
after:  11 cards — … + Nereid's Ascension
```

**Nereid's Ascension** is `docs/kokomi-cards.yaml:208`, `rarity: rare`, `archetypes: [priest,
generic]` — a Rare **from Kokomi's own pool**, which is the row's acceptance word for word. Its
live face is the prototype one (*"At the start of your turn, the Bake-Kurage carries out your
first Plan twice."*).

A second, unforced instance turned up on launch 3: **Furina's Neow rolled Arcane Scroll** and
taking it added a card to her deck as well. So the grant path reads the arm's pool on two of
the three arms this round. **Board writes: 1 `give_relic`.**

## 8. `EB-363` — The Future of Potions under all three arms — PASS

proofs-8a marked this NOT DONE because the gate is `Players.All(Potions.Count() >= 2)` and no
bridge op could fill a belt. `give_potion` closes that: two potions granted, one
`force_next_event`, one walk to a `?`.

| arm | launch | dressing reached | rows on the selection |
|---|---|---|---|
| **Klee** | 1, act 1 MONDSTADT | `Confiscation, With Compensation` | **3** — `Long Fuse+`, `Tinder Toss+`, `Fish Blasting+` (Upgraded Common Attacks) |
| **Kokomi** | 2, act 1 LIYUE | `The Bureau of Reclaimed Medicine` | **3** — `Vanguard+`, `Rally+`, `Salt Line+` (Upgraded Common Skills) |
| **Furina Stage** | 3, act 1 MONDSTADT | `Confiscation, With Compensation` | **3** — `Tidal Flourish+`, `Stage Combat+`, `Undercurrent+` (Upgraded Common Attacks) |

**No empty selection under any arm**, which is the acceptance. Kokomi's is the one the row was
filed from (Kokomi r5 run 3) and it is the one that pays three rows from her own pool. Both
dressings printed both of their option rows with the potion each would cost and that potion's
own hover tip. `PR #543`'s widening ladder has now been looked at live for the first time.
**Board writes: 2 `give_potion` and 1 `force_next_event` per arm.**

## 9. `EB-779` — the Spend mode chooser — MIXED

**The bridge half, which is what this item is, PASSES.** Launch 3, Furina Stage, act 1 floor 2.
`Curtain Rise` opened its chooser (`card_select.screen_type: "choose"`, `can_confirm: false`,
`can_cancel: false`). **One `choose` closed it:**

```
$ blindplay act "choose 1"
{"ok": true, "verb": "choose", "post": {"action": "select_card", "index": 0}, "refusal": ""}
Took: Deal 7 damage — Deal 7 damage.
```

and the next state had **no `card_select` at all** and the enemy at 32 from 39 — the mode
resolved for its 7. No `confirm` was sent and none was needed. So the live answer to the
question #566 left open is settled: on `NChooseACardSelectionScreen` as the mode chooser uses
it, `ExecuteSelectCard` lands the press that takes the answer, and **one `choose` suffices**.
The page's verb list is right about this already — it offers `choose` and does **not** offer
`confirm`.

**The other half of the item FAILS, and it is a real residual defect.** The item asks that
*the page's hint does not say `confirm`*, and the page's hint still does. Printed above the
rows on this very screen:

> *Choosing here arms a pick; it does not close the screen. Say `confirm` after `choose` to
> take it, and until you do this chooser stays open and every other command is refused. If
> `confirm` is refused, say `choose` again on the same option — one chooser in the game takes
> its answer on the second `choose` and has no confirm button at all.*

Three of those clauses are false on this screen: choosing here **does** close the screen, a
`confirm` is **not** needed, and the chooser does **not** stay open. `#566`'s added sentence
(the second-choose fallback) is the safety net, not the fix — a seat reading top to bottom is
still told to say `confirm` first, which is the eight-refusals-a-run behaviour the row was
opened on. The note is one constant,
`understudy/blindplay_notes.py:683` (`CHOOSER_CONFIRM_NOTE`), printed on every chooser; with
the bridge half now settled it can be split so the `choose`-closes-it screens get a sentence
that is true of them. **Not fixed here** (no code was changed in this job, by rule).

**Repro:** Furina Stage run, play `Curtain Rise`, read the italic note under the two mode rows,
then say `choose 1` and read the next state.

## Defects found that are not on any row above

Raised here, not filed — a register row is [USER]'s to mint or Claude's under the hygiene rule,
and this is a record.

1. **A mode card's TITLE prints its raw markup.** `KLEEMOD-PROTO_FS_CURTAIN_RISE_MODE_B` sends
   `"name": "[gold]Spend[/gold] 3: deal 13 instead"` on the wire, and the frame shows the same
   string drawn **on the card in the game** — `[gold]Spend[/gold] 3: deal 13 instead` — while
   the description line an inch below it renders the same word correctly in gold. Mode A is
   unaffected because its label carries no markup. The blind page is unaffected too: it strips
   the tags, so this is invisible to a seat and visible only to a person at the screen, which is
   why 3 seat rounds did not catch it. Source: the label in
   `docs/prototype-surface.yaml:1665` (`{label: "[gold]Spend[/gold] 3: deal 13 instead"}`) is
   used as the mode card's NAME, where the description goes through the cleaner and the name
   does not. **Repro:** play `Curtain Rise`; the right-hand mode card's title.
   Frame: `review/qa/proofs-9-lane1-2026-09-16/eb786-curtain-rise-mode-chooser.png`.

2. **The intent section's closing caveat now contradicts the line above it.** On the same page
   where `EB-607`'s new clause prints *"the game folded **Strength** into that: it is 12 on the
   move and 15 after"*, the italic paragraph at the foot of "The other side" still reads:
   *"An enemy carrying Strength whose figure does not move is the game's own figure not moving
   — the feed carries no base, no modifier list and no breakdown, so nothing here can say which
   parts are inside a given number."* The feed now carries all three. The caveat was right
   before #569 and is wrong after it. **Repro:** any combat page with an attacking enemy.

3. **`player.master_deck` rows are thin.** `name`, `cost`, `star_cost`, `description` and
   nothing else — no `id`, no `rarity`, no `upgraded`, no `keywords`, where a hand row carries
   all of them. So a reader can count the deck (which is `EB-447`'s acceptance and it holds) but
   cannot tell two same-named copies apart, cannot see rarity, and reads `Defend+` only because
   the `+` happens to be in the printed name. This is the same shape 8c raised for `draw_pile`.

4. **The removal grid does not mark the selected row.** On the Smith's upgrade grid,
   `select_card index=38` came back with that row `selected: true` and `can_confirm: true`
   (which is `EB-263`'s acceptance). On the shop's **removal** grid, `select_card index=36`
   answered *"Toggling card selection: Kurage's Oath"* and `can_confirm` flipped to `true`, but
   **no row in `card_select.cards` carried `selected: true`** — and the confirm then removed the
   right card. So the pick is armed and correct, and a page that reads `selected` to show a
   reader what they have armed would show nothing on this screen. One visit on each grid.

5. **`snake_ring` is still missing from `relic_outline_atlas`.** One `AtlasResourceLoader:
   Missing sprite 'snake_ring' in relic_outline_atlas` at boot in every launch, exactly as 8a
   reported. Unchanged, and named again only so it is not mistaken for something this round
   introduced.

## What could not be done, and why

- **`EB-611`'s random targeting.** The multi-hit Set off was read on a **one-enemy** board, so
  the ordered hits are proven and the *random choice between bodies* is not. A hallway of two or
  three with bombs on more than one of them would settle it and was not reached.
- **`EB-676`'s original kill-screen case was not re-run.** Item 3 asked about map screens and
  that is what was read; the `false`-then-settled window on a kill turn with a late HP change
  (8a §13) was not rebuilt.
- **Nothing was framed except the mode chooser.** Every other claim in this record is wire
  payload, page text, or a line in a log, each checkable against the file or field named beside
  it. The pages and state snapshots were kept in the session scratchpad, which is not the tree,
  and the driver (`drv.py`, `climb.py`) is scratch and is not committed, as proofs-6, -7 and -8a
  did with theirs.

## What else the round learned, for the next driver

- **The grant ops make a whole class of row cheap.** Four rows proofs-8a listed as unreachable
  — the potions event's gate, Neow's Arcane Scroll, Pael's Eye, Flex Potion — were each one
  `give_*` call and a few minutes. Anything gated on *holding* a thing is now a five-line setup.
- **`force_event` prints its gate on a refusal and that is the fast path.** The first
  `SLIPPERY_BRIDGE` force refused with `TotalFloor=3` against `TotalFloor > 6` and listed every
  fact the gate reads, so the fix was "climb four floors", decided in one call rather than by
  trial.
- **`skip_act` raises the ACT but not the total floor.** Launch 1 skipped from MONDSTADT to
  INAZUMA and `TotalFloor` stayed at 3, so a floor-gated event still needs the climbing. A
  driver reaching for `skip_act` to satisfy a `TotalFloor` gate will be refused.
- **A Klee starter produces no Elemental Reaction.** The starter's Strikes are
  `STRIKE_IRONCLAD` and apply no Pyro; only a `KLEEMOD-` attack does. Any reaction check on a
  Klee run needs one granted Klee attack plus a `set_power *_AURA_POWER` on the target — two
  writes, and worth knowing before spending a fight on it.
- **`Whispering Earring` is the auto-played turn on demand.** One `give_relic` and the next
  fight's turn 1 is Vakuu's, which is the only board `EB-349`'s auto-play half can be read on.
- **Pael's Eye's extra turn is legible on the wire without a flag:** the round counter does not
  advance, the player's HP does not move, and the previous hand appears whole in the exhaust
  pile. That triple is how a driver knows the extra turn happened.

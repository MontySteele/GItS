Status: RECORD (deploy proofs; feasibility only, nothing measured)

# proofs-8a: the Teyvat events and the new bridge fields, looked at live

**Nothing here is measured or quotable** — no pre-registration, no blind grading, no slate,
no register row. Nothing was deployed, rebuilt or committed to the main checkout; the owner's
game profile, the Steam userdata and the run-history store were not touched, and no save file
was edited by hand. **Twice over, nothing here is comparable to anything.** `skip_act` is not
rng-neutral and says so — the floors it skips never roll, so every act-scoped stream is read
from a different position afterwards, this run's own earlier floors included. And most of the
boards below were **written by hand**: `set_hp` to keep an act-1 starter deck alive on an
act-3 map, `set_hp` on enemies to end fights the deck could not win, `set_power INTANGIBLE` on
the player as life support, and `set_power` to place a Constrict and a Thorns for one
deliberate correctness check. Every write is counted in its own section. A tour here reaches a
**face** — an event's text, its options, a page's rows — and never a number.

**Another agent was driving lane 0 (Klee, Kokomi and Furina embarks) throughout**, and other
agents were building in sibling worktrees, so every boot below was under concurrent load.
Nothing here ever killed a process it had not launched: every teardown was
`understudy.embark --teardown --lane 1`, which kills by the pid its own sidecar records.

**Installed, off `mods\klee\manifest.json`:** `0.2.3480+proto.dirty`, `min_game_version`
`0.111.0`, BaseLib `3.4.7`, arms `klee,companion,kokomi,furina-stage,teyvat`, `TeyvatFrame`
ON. The installed `klee.dll` is byte-identical to `klee-mod/dist/klee/klee.dll`
(md5 `d8e209a6f0a60323c699926660df66eb`), so the build under test is the one main just shipped.

## The one-line verdicts

| # | row | verdict |
|---|---|---|
| 1 | `EB-769` PUNCH_OFF at harness speed AND at the game's own | **PASS on both** |
| 2 | TRIAL Reject page + Double Down | **PASS** |
| 3 | TINKER_TIME to DONE through two chassis | **PASS** |
| 4 | COLOSSAL_FLOWER third reach, both ways | **PASS** |
| 5 | BATTLEWORN_DUMMY, the LOSS branch | **PASS** |
| 6 | `EB-363` THE_FUTURE_OF_POTIONS under the three arms | **NOT DONE** |
| 7 | `EB-770` SLIPPERY_BRIDGE prints the card NAME | **PASS** |
| 8 | `EB-767` a dressed id resolves and opens dressed | **PASS** |
| 9 | `EB-682` an Ancient room prints its option rows | **PASS** |
| 10 | `EB-459` Neow's Arcane Scroll under Kokomi | **NOT DONE** |
| 11 | `EB-740` every Neow option prints its rules text | **PASS** |
| 12 | `EB-716` a POTION row and a RELIC row, kind + text | **PASS** |
| 13 | `EB-676` `hp_settled` on a kill with a late HP change | **PASS, with one over-broad reading** |
| 14 | Self-Help Book: `EB-734` / `EB-263` / `EB-84` / `EB-181` | **PARTIAL** |
| 15 | `EB-269` a self-targeted potion used live | **PASS** |
| 16 | the log and page hygiene set | **MIXED** (see §16) |

## The launch table

**Fifteen embarks, all Ironclad, all lane 1 (the disposable profile), all on port 15527.** The
driver is scratch (`drv.py` and four tour scripts, kept out of the tree as proofs-6 and
proofs-7 kept theirs); it opens the run with `understudy.embark` and then drives the wire
directly. **Boot walls are not reported this round** — the runs were opened through the
`embark` CLI rather than a Session this driver held, and that CLI does not print one, so a
number here would be invented. What IS countable is below.

| # | stamp | seed | act list | what it was for |
|---|---|---|---|---|
| 1 | `20260916-112208` | — | — | **BLOCKED at the menu**: `no_embark_path … pending_epoch_ids ["IRONCLAD2_EPOCH"]` |
| 2 | `20260916-112242` | `CUJS90223999` | LIYUE / INAZUMA / SUMERU | items 7, 8, 11, 13, 14, 15, 9 (Neow) |
| 3 | `20260916-114734` | `72CJPBE7R5CJ` | MONDSTADT / INAZUMA / FONTAINE | items 9 (Orobas), 4(a) |
| 4 | `20260916-115801` | `8TB5F9JEVK4P` | LIYUE / NATLAN / FONTAINE | item 12, item 9 (Pael); PUNCH_OFF missed |
| 5 | `20260916-122604` | `9R01QM7EPJUZ` | MONDSTADT / NATLAN / SUMERU | items 4(b), 3, 5, and the shop for `EB-274` |
| 6 | `20260916-123639` | — | — | **BLOCKED at the menu again**, by lane 1's own play |
| 7 | `20260916-123705` | `WPLH2R37QFKZ` | LIYUE / NATLAN / FONTAINE | item 2 (PASS); PUNCH_OFF missed — the act's `?` rooms ran out |
| 8–12 | `124235`, `124306`, `124328`, `124350`, `124422` | 5 fresh rolls | **MONDSTADT** every time | looking for a Liyue act 1 for item 1, and not finding one |
| 13 | `20260916-124459` | `WPLH2R37QFKZ` (**pinned**) | LIYUE / NATLAN / FONTAINE | the Punch-Off page reached; the driver clicked the wrong row (Nab) and had to re-run |
| 14 | `20260916-124636` | `WPLH2R37QFKZ` (pinned) | LIYUE / … | **item 1(a), the fight at Instant / 3x** |
| 15 | `20260916-124853` | `WPLH2R37QFKZ` (pinned) | LIYUE / … | **item 1(b), the fight at the game's own speed** |

**Stalls and fuse firings: one.** Launch 2's first boot stalled and `EB-766`'s fuse caught it
by name, waited out Steam's teardown and relaunched into a good menu:

> `WARN lane lane1: boot looks STALLED after 48s -- the root endpoint answers, the state
> endpoint has been silent for 44s, godot.log is 145877 bytes and the profile marker is
> present (last 22s without growth). Killing and relaunching (EB-766).`
> `lane lane1: waited 9.4s after the previous kill before launching`

No other stall over fifteen launches, no `DIAG` line, no truncated archive, no crash, and no
`AssetLoadException` in any lane-1 log. Five of the fifteen (8–12) bought nothing but the
fact that five fresh rolls in a row gave MONDSTADT act 1, which is why item 1 ended up
running on a **pinned seed** instead. `EB-763`'s run-history warning printed on every launch and the store stayed
tiny (1 to 4 files) because the lane's profile was deleted twice — nothing here touched the
owner's store.

**The epoch blocker, and the recovery that proofs-7 said was closed, is OPEN again and it
works.** Launch 1 hit the same wall proofs-7 ended on. The standing rule was applied — delete
`%LOCALAPPDATA%\gits-lanes\lane1` whole and relaunch — and this time `instances.seed_profile`
re-seeded from a lane-0 tree whose epoch had been revealed by a person, so the lane came up
clean. Launch 6 hit it a second time, now earned by lane 1's **own** play (these tours beat
act bosses), and the same delete cleared it again. So: **the disposable-profile escape hatch
recovers as long as lane 0 itself is not parked**, which is exactly the condition proofs-7
identified. No save file was edited, and no permission rule was asked for.

## 1. EB-769 — the Punch-Off

**Reaching it took the seed.** PUNCH_OFF is dressed on Liyue only and its gate is
`TotalFloor >= 6`, so the run has to be six floors deep *and* still have a `?` room ahead of
it on a Liyue act-1 map. Four consecutive fresh embarks rolled MONDSTADT act 1, and two
earlier Liyue runs walked past the act-1 boss without meeting another `?`. The fix was to
re-embark on a **recorded Liyue seed** — `--seed WPLH2R37QFKZ`, whose map has `?` rooms at
floors 4 and 7 — and to climb to floor 6 **without spending a `?`**, so floor 7's was still
there to force into. That recipe is worth keeping; it is the difference between one launch and
five.

The page opened as **`GUYUN_STONE_CONSTRUCTS`, *The Guyun Stone Constructs***, printing both
rows with their text:

```
- **Nab**
    Add Injury (curse) to Deck. Obtain a random Relic.
    · **Injury** — Unplayable.   · **Unplayable** — Unplayable cards cannot be played.
- **I Can Take Them**
    Enter combat against 2 Punch Constructs for greater rewards: obtain a random Relic, a
    random Potion, and a standard combat reward. Each Punch Construct starts off slightly
    damaged, missing between 2 and 9 HP.
```

**(a) At harness speed — `FastMode=Instant`, `TimeScale=3` — PASS.** "I Can Take Them" put the
run straight into combat against **two Punch Constructs at 47 HP each**, and the fight ran to
its reward screen:

| reading | value |
|---|---|
| wall clock, click to reward screen | **17.0 s** |
| entered combat | yes |
| wire reads over 2 s, or that raised | **0** |
| `godot.log` growth across the whole fight | **10,312 bytes** |
| `Element limit reached` in the lane's log | **0** |
| `AssetLoadException` | **0** |
| `Expected BoundObject to be a SpineSprite` | **0** |
| `NCardTrail` catch line | **0** |

That 10 KB is the number that matters against the history: the 2026-09-15 spin this row was
opened for wrote **2.56 GB** in about two minutes, and proofs-6's three attempts at Instant
produced a 66 MB log, a 512 MB log and a process that vanished inside 20 s. The process
answered every single state read at sub-100 ms throughout. **PR #542's bound on the swing loop
and the blunt VFX holds at Instant / 3x.**

**One honest caveat on the board:** the driver's life support was on during this fight
(`set_hp` top-ups and `set_power INTANGIBLE` on the player, and `set_hp 1` on the constructs
so the fight would close), so **17.0 s is not a reading of how long this fight takes** — it is
a reading of how long the process took to get through it without spinning. The row is about
the spin, not the fight.

**(b) At the game's own speed — PASS.** The same seed, the same floor-7 force, with
`POST /api/v1/gits/speed {"enabled": false}` first, so the wire read
`enabled: false, fast_mode: "Fast", time_scale: 1` — the harness's Instant / 3x override off
and the game running on the profile's own setting. Stating that precisely rather than calling
it "1x": `TimeScale` is 1, and `FastMode` is `Fast` because that is what the captured original
was, and restoring the original is what turning the override off means.

| reading | at Instant / 3x | at the game's own speed |
|---|---|---|
| wall clock, click to reward screen | 17.0 s | **45.0 s** |
| wire reads over 2 s, or that raised | 0 | **0** |
| `godot.log` growth across the fight | 10,312 B | **14,819 B** |
| `Element limit reached` | 0 | **0** |
| `AssetLoadException` | 0 | **0** |
| `Expected BoundObject to be a SpineSprite` | 0 | **0** |
| `NCardTrail` catch line | 0 | **0** |

**So `EB-769`'s acceptance is met on both readings and this is the first time it has been.**
The fight completes, the process answers every state read at sub-100 ms all the way through,
no `Element limit reached` line appears at either speed, and the log grows by kilobytes rather
than gigabytes. The 2.7x wall-clock difference between the two is the animations playing,
which is the point of the two arms: at Instant nothing is skipped that hides the spin, and at
the game's own speed nothing is rushed past it.

Pages `item1-punchoff-instant-initial` / `-fightover` and `item1-punchoff-onex-initial` /
`-fightover`. **Board writes across the two Punch-Off fights: 31 + 73 `set_hp` and 1 + 2
`set_power`** — the running life support, most of it spent on the six floors of climbing
before the event rather than inside it.

## 2. TRIAL's Reject page and the Double Down popup — PASS

Launch 7, seed `WPLH2R37QFKZ`, act 3 **FONTAINE**, floor 19, reached by one `skip_act` and
three re-forces of `TRIAL` (see "what else the round learned"). The page opened as
**`EMPTY_SEAT_IN_THE_GALLERY`, *The Empty Seat in the Gallery***, and **Decline the Summons**
was taken — the branch proofs-7 never opened:

| page | rows |
|---|---|
| INITIAL | **Take the Empty Seat** — "Sit on the jury. One case is called, and you deliver its verdict." / **Decline the Summons** — "Try to leave the gallery." |
| **REJECT** | **Take the Seat After All** — "Sit on the jury. One case is called." / **Walk Out of the Opera** — "Push past the gardes and leave Fontaine's justice behind. This ends the run." |

The Walk Out row is `@pages.REJECT.options.DOUBLE_DOWN`, and it matches
`docs/current/dossiers/content/event-faces/glory-fontaine-2026-09-14.md:250` word for word.

**The Double Down popup is real and the wire shows it.** Clicking Walk Out did not end the run
straight away — the state became

```json
{"state_type": "menu", "menu_screen": "popup", "message": "Popup active.",
 "options": [{"name": "yes", "enabled": true}, {"name": "no", "enabled": true}]}
```

— a yes/no confirmation, which is the popup the row asks for, and the blind page correctly
refused to render it (`TOOL-BLOCKED: menu … this is a menu, not a play screen`) because a
popup is not a play screen. The run ended there, which is the option's own printed promise.
Pages `item2-trial-initial`, `item2-trial-reject`, `item2-trial-doubledown`.

**Board writes in this section: none.** (The launch as a whole spent 301 `set_hp` and 11
`set_power` writes on life support over about forty floors of walking; none of them touched
this event.)

## 3. TINKER_TIME to DONE — PASS

Launch 4, seed `9R01QM7EPJUZ`, act 3 **SUMERU**, floor 9, reached by `skip_act` twice and one
`force_next_event TINKER_TIME`. The page opened as its Sumeru dressing
**`KSHAHREWAR_WORKBENCH`, *The Kshahrewar Workbench***, and every page of it was clicked
through to the end:

| page | rows printed | clicked |
|---|---|---|
| 1 | **Choose a Frame** — "Pick one of the two frames on the bench." | Choose a Frame |
| 2 | **Ward Plate** — "Create a Skill. (Gain 8 Block.)" / **Field Array** — "Create a Power." | Ward Plate |
| 3 | **Surplus Charge** — "Gain 2 energy." / **Improvised Patch** — "Add a random card into your Hand. It's free to play this turn." | Surplus Charge |
| 4 | **Proceed** | Proceed, and the run went back to the map |

That is the **two chassis** the row asks for, on the Sumeru workbench, and the event closed to
its DONE state rather than stopping at the chassis page as proofs-7 did. Pages
`item3-tinker-p1` … `-p4`. **Board writes in this section: none.**

## 4. COLOSSAL_FLOWER, the third reach, BOTH ways — PASS

The event ladders 35 / 75 / 135 gold against 5 / 6 / 7 HP, and the third page swaps the deep
option's name for the relic. Both branches of that third page were taken, on different faces
and different launches:

| launch / face | level 1 | level 2 | level 3 rows | taken | result |
|---|---|---|---|---|---|
| 2, Inazuma, `WISTERIA_WELL_OF_CHINJU_FOREST` | Skim the Petals (35 g) / Reach Deeper (−5 HP) | 75 g / −6 HP | **Skim the Petals — Gain 135 Gold** / **Enter the Bud's Heart — Lose 7 HP. Obtain the Wisteria Core.** | Enter the Bud's Heart | HP 67 → 60, relics 3 → 4, the page's own tip named **Pollinous Core** — "Every 4 turns, draw 2 additional cards." |
| 4, Natlan, `BLOOM_OF_TEQUEMECAN` | Tap the Nectar (35 g) / Reach Deeper (−5 HP) | 75 g / −6 HP | **Tap the Nectar — Gain 135 Gold** / **Reach the Bloom's Heart — Lose 7 HP. Obtain the Bloom's Heart.** | Tap the Nectar | gold + 135, then a Proceed page |

**proofs-7's title mismatch did NOT recur.** Every one of the eight option clicks across the
two faces came back naming the option that was printed — `Reach Deeper` → "Choosing event
option: Reach Deeper", `Enter the Bud's Heart` → "Choosing event option: Enter the Bud's
Heart", `Tap the Nectar` → "Choosing event option: Tap the Nectar", `Proceed` → "Choosing
event option: Proceed". No page arrived already past its INITIAL screen, and no option was
printed `Proceed` while resolving as something else. proofs-7 saw that once and did not
reproduce it; this round did not see it in eight tries. Pages `item4-colossal-flower-l1..l4`
and `item4b-colossal-p1..p4`. **Board writes in this section: none.**

## 5. BATTLEWORN_DUMMY, the LOSS branch — PASS

Launch 4, act 3 Sumeru, floor 10. The page is **`KSHAHREWAR_PROVING_CAGE`, *The Kshahrewar
Proving Cage***, and it printed its three settings word for word:

- **Setting 1** — "Fight a 75 HP dummy. Procure 1 random Potion."
- **Setting 2** — "Fight a 150 HP dummy. Upgrade 2 random cards."
- **Setting 3** — "Fight a 300 HP dummy. Obtain a random Relic."

Setting 1 was taken and then **deliberately lost**: the life support was switched off, nothing
was played, and the driver only ended turns. The dummy carried `Time Limit` and the wire
counted it down on the enemy's own status block —

```
turn 0: [('Battle Friend V1.0', 75, ['Time Limit:3'])] hp=70
turn 1: [('Battle Friend V1.0', 75, ['Time Limit:2'])] hp=70
turn 2: [('Battle Friend V1.0', 75, ['Time Limit:1'])] hp=70
dummy fight left combat after 3 end-turns: event
```

— the fight ended on its own at zero, the run came back to the event, and the page served a
single **Proceed**. The belt still held 2 potions afterwards, so the Setting 1 prize was
**not** paid: that is the defeat branch and not the victory one. This is the branch proofs-7
could not reach, and reaching it needed **no HP write at all** — the timer, not the player's
death, is what loses this fight, which is the fact proofs-7 was missing. Pages
`item5-dummy-initial`, `item5-dummy-after`. **Board writes in this section: none.**

*One thing the loss page does not show:* the wire's `event.body` is `null` on every event page
this round, so the face file's `@pages.DEFEAT.description` ("The proctor's count runs out with
the construct still on its feet…") is on the screen but not on the wire and not on the blind
page. That is the shape of the event payload rather than anything this round changed; no row is
minted for it.

## 6. EB-363 THE_FUTURE_OF_POTIONS under the three arms — NOT DONE

Not attempted live. The reason is in "What could not be done" below: the gate wants two
potions in the belt, a `skip_act` tour starts with an empty one, and there is no bridge op
that grants a potion — so this is one dedicated launch per arm and the round's launches went
elsewhere. **`PR #543`'s widening ladder is still unlooked-at live**, exactly as proofs-6 and
proofs-7 left it, and nothing this round argues for or against it.

## 7. EB-770 SLIPPERY_BRIDGE — PASS, and it found a defect next door

Launch 2, seed `CUJS90223999`, act 1 **LIYUE**, forced at **floor 8** — `TotalFloor > 6` and a
removable card in the deck, which is the gate `force_event --list` now prints beside the id.
proofs-7 spent two embarks on this and never got past the refusal; with the gate printed it
took one force. The page opened as **`ROPE_BRIDGE_BELOW_DUNYU_RUINS`, *The Rope Bridge Below
Dunyu Ruins***, and **the first option printed the card's name**:

```
- **Let It Fall**
    Armaments is removed from your deck.
    · **Armaments** — Gain 5 Block. Upgrade a card in your Hand.
```

— the name, plus the card's own hover tip. **Hold On** was then taken once: HP 80 → 77 (the
first price, 3), the reroll fired, and the first option came back naming a *different* card,
**Defend is removed from your deck.** `EB-770`'s acceptance is met on both readings — the name
is printed, and it is re-printed correctly after the reroll. Pages `item7-slippery-bridge`,
`item7-slippery-bridge-page2`. **Board writes in this section: none.**

### The defect this section found: every dressed Hold On page understates the price

The base event's price is `3 + NumberOfHoldOns` (`SlipperyBridgeMirror.cs`,
`CurrentHpLoss`), and the base game's own text carries it as the `{HpLoss}` var —
`tools/data/sts2_base_events.json` registers `HpLoss` in `key_vars` for
`pages.HOLD_ON_0.options.HOLD_ON_1.description` and for every later Hold On page.

**The six Teyvat dressings hard-code the number 3 instead.** Live, on the second page, with
the next Hold On priced at 4, the option still read:

> **Hold On** — Lose 3 HP as the wet rope scours your palms. …

and in the generated file, `klee-mod/KleeCode/Teyvat/TeyvatEventsGenerated.cs:1350`
(`ROPE_BRIDGE_BELOW_DUNYU_RUINS.pages.HOLD_ON_0.options.HOLD_ON_1.description`) is
byte-identical to the INITIAL one at :1340. A scan of the generated file finds all
**six** SLIPPERY_BRIDGE faces — `CUT_ROPE_BRIDGE_ABOVE_CIDER_LAKE`,
`ROPE_BRIDGE_BELOW_DUNYU_RUINS`, `ROPE_LINE_OVER_ARDRAVI_VALLEY`,
`BALLAST_CHECK_ON_THE_MEROPIDE_LIFT`, `TIDEWORN_CAUSEWAY_AT_MUSOUJIN_GORGE`,
`ROPE_CROSSING_AT_COATEPEC` — carrying **nine identical Hold On descriptions each, none of
them containing `{HpLoss}`**.

**Cause hypothesis:** the face files author one Hold On line with the literal price in it
(`docs/current/dossiers/content/event-faces/underdocks-liyue-2026-09-14.md:341`, "Lose 3 HP as
the wet rope scours your palms…"), and `tools/gen_teyvat_events.py` copies that one line into
all nine page keys, so the var that the base text uses is lost. **Repro:** force
SLIPPERY_BRIDGE past floor 6, take Hold On once, read the second page's Hold On row — it says
3, and the click costs 4. **Not fixed here.**

## 8. EB-767 — a dressed id resolves to the base and opens on the dressed page — PASS

Launch 2, act 1 Liyue. `python -m understudy.force_event SIX_CONTRACTS_TO_A_BETTER_YOU`
printed the translation line, out loud, before it wrote anything:

```
DRESSED: SIX_CONTRACTS_TO_A_BETTER_YOU is Liyue's face on SELF_HELP_BOOK; forcing
SELF_HELP_BOOK, which is the id the act's pending list holds (the dressing is swapped in
at PullNextEvent).
FORCED: SELF_HELP_BOOK in act LIYUE (index 8 -> slot 2, moved=True)
```

and two `?` rooms later the page that opened was **`SIX_CONTRACTS_TO_A_BETTER_YOU`, *Six
Contracts to a Better You***. That is the acceptance exactly: a dressed id forces
SELF_HELP_BOOK and lands on the dressed page. This is the live half proofs-7 owed. Page
`item8-self-help-book-dressed`. **Board writes in this section: none.**

## 9. EB-682 — an Ancient room prints its option rows on the blind page — PASS

Three Ancient rooms were rendered through `understudy.blindplay observe` off the live state,
and each printed every option row with its text and its keyword tips:

- **Neow** (`NEOW`, `is_ancient: true`, act 1 floor 1, launch 2) — three rows, each with its
  relic's rules text and the keyword tips for Energy, Greed, Eternal and Unplayable.
- **Orobas** (`OROBAS`, act 2 **Inazuma**, launch 3, reached by `skip_act`) — three rows:
  *Electric Shrymp* "Enchant a Skill with Imbued.", *Driftwood* "You may reroll each card
  reward once.", *Archaic Tooth* "Transform Bash into Break.", with tips for Imbued, Bash,
  Vulnerable and Break. Page `item9-act2-ancient`.
- **Pael** (`PAEL`, act 1 floor 17, launch 4) — page `item9-act1-ancient-pael`.

`TANX` and `NONUPEIPE` were also met and answered on Fontaine and Sumeru. None of the three
rendered pages was empty and none fell back to a bare Proceed, which is the failure `EB-682`
exists for. **Board writes in this section: none.**

## 10. EB-459 — Neow's Arcane Scroll under the Kokomi arm — NOT DONE

**Five Neow screens were read this round and none of them offered Arcane Scroll.** The Neow
offer is a roll, every run this round was Ironclad, and the bridge has no op that grants a
relic or seeds the offer (see "What could not be done"). What can be said is narrow and is
said as such: the relic **is** in this build's pool — an Ancient handed an Ironclad run
*Arcane Scroll — "Upon pickup, obtain a random Rare Card to add to your Deck."*, and the
blind page printed it under **Your relics** with that text. Whether it draws from Kokomi's
pool under her arm is untested.

## 11. EB-740 — every Neow option prints its rules text — PASS on what was rolled

Launch 2's Neow, rendered blind:

```
# Neow
- **Booming Conch**
    At the start of Elite combats, draw 2 additional cards and gain Energy.
    · **Energy** — Energy is used to play cards from your Hand.
- **Kaleidoscope**
    Obtain 2 card rewards from other characters.
- **Cursed Pearl**
    Receive Greed. Gain 333 Gold.
    · **Greed** — Unplayable. Eternal. …
```

Every row carries its rules text, and the wire behind it carries `relic_name` and
`relic_description` on each option (`relic_description` for Kaleidoscope is the longer "Upon
pickup, obtain 2 card rewards from other characters."). Launch 4's Neow did the same.
**Lead Paperweight itself was never rolled** in five Neow screens, so the row's named example
is not the one that was checked; what is checked is the rule the example stands for — no Neow
option printed a blank description in any Neow screen this round. **Board writes: none.**

## 12. EB-716 — a reward screen prints each row's KIND and its TEXT — PASS

One page carries both halves the row asks for. Launch 4, act 2 Natlan elite, page
`t3-elite-rewards-1`:

```
# What the fight left behind
You have 744 gold.
- **41 Gold** — gold
- **15 Gold** — gold
- **Energy Potion** — potion
    Gain 2 Energy.
- **Bag of Preparation** — relic
    At the start of each combat, draw 2 additional cards.
- **Add a card to your deck.** — card
```

The **relic** row's text is the new `relic_description` field: the wire's item reads
`{"type": "relic", "relic_id": "BAG_OF_PREPARATION", "relic_name": "Bag of Preparation",
"relic_description": "At the start of each combat, draw 2 additional cards."}`. The **potion**
row's is `potion_description`. Across 182 pages rendered this round the reward-item kinds seen
were `gold`, `potion`, `relic`, `card` and `special_card`, and every potion and relic row
printed its kind and its text. **Board writes: none.**

## 13. EB-676 — `hp_settled` on a kill with a late HP change — PASS, with an over-broad reading

**What was arranged, disclosed.** A true Constrict-carrying enemy was not hunted for; instead
the two HP-loss shapes were placed by hand on one fight (launch 2, act 1 Liyue, floor 12, two
enemies):

1. `set_power player CONSTRICT_POWER 3` — the wire then showed `Constrict 3` on the player's
   status block, and the end-of-turn tick landed (HP 90 → 76 over that turn, enemy attacks
   included). **1 `set_power` write.**
2. `set_hp <enemy> 1` on both enemies and `set_power <last enemy> THORNS_POWER 3`, so the
   **last** HP change of the fight lands at the instant of the killing blow. **2 `set_hp`
   writes, 1 `set_power` write.**

So this is the row's fallback reading and it is named as such: **an end-of-turn / on-kill
HP-loss on the kill turn, not an enemy that applies Constrict from its own kit.** Constrict
itself was proved to apply and tick; it was not what killed anything.

**The result.** The killing blow landed, the screen became `rewards`, and the flag was right:

```
after-kill-0  rewards  hp=82  settled=False
  reason: the fight is over but its combat state has not been dropped yet, so
          end-of-turn effects belonging to it may still land in this figure
```

read eight times over eight seconds, never flipping. The **next screen's HP was 82 as well** —
so the number the kill screen showed was in fact the settled one, and the flag was
conservative rather than wrong. That is `EB-676`'s acceptance: the kill screen's HP equalled
the next screen's HP, and where it could not promise that, it said so in words.

### The over-broad reading, worth a look

`hp_settled` stays **false on the map screen too**, and on every post-combat `rewards` and
`card_reward` screen, with the same sentence. Across the 36 states captured this round the
split is clean:

| screen | `hp_settled` |
|---|---|
| `event`, `treasure`, `card_select` | **true**, every time (10 of 10) |
| `rewards`, `card_reward`, `map` | **false**, every time (26 of 26) |

`vendor/STS2_MCP/gits/GitsSettledHp.cs:126-131` says clause (2) — combat state stands AND
combat is over — "is the r26 window and nothing else: during a live fight the second half is
false, and **off the map the first half is**". The map reads say that second assumption does
not hold on this build: `CombatManager.Instance.CurrentCombatId` is still non-null while the
run stands on the map after a fight. The flag is therefore never true on a map, which is where
a reader most wants to trust an HP figure. It is the safe direction and no number was wrong,
but a flag that is permanently false outside an event room says less than it is meant to.
**Not fixed here.** Repro: finish any fight, walk to the map, read `player.hp_settled`.

## 14. The Self-Help Book — PARTIAL

Launch 2, act 1 Liyue, on the dressed page from §8. The initial page printed the three
enchant offers with their keyword tips, and the third was **locked** because the deck held no
Power:

```
- **Read the Back** — Choose an Attack to Enchant with Sharp 2.   · Sharp — Increases damage on this card by 2.
- **Read a Random Passage** — Choose a Skill to Enchant with Nimble 2.   · Nimble — Increases Block gained from this card by 2.
- **Read the Entire Book** — Choose a Power to Enchant with Swift 2.   (is_locked: true)
```

- **`EB-84`, the eligibility shapes — one of four watched, and it holds.** *Nimble on a
  GainsBlock card only:* the chooser opened on exactly four rows — three `DEFEND_IRONCLAD` and
  one `ARMAMENTS` — and offered **no** other Skill in the deck; `FEEL_NO_PAIN`, a Power, was
  not offered, and nor was any Attack. The deck at that moment held four block-gaining Skills
  minus the one the bridge event had removed, which is exactly the three Defends plus
  Armaments. A second shape was seen by accident on Fontaine: the Ancient `TANX` opened an
  enchant chooser prompting *"Choose 3 cards to Enchant"* whose rows were **Attacks only**
  (Strike+, four Strikes, Bash). The two remaining shapes — souls_power's local Exhaust and
  the no-override trio — were not exercised; one visit does not show four shapes.
- **`EB-263`, the picker marks the pick — PASS.** Every row arrived `selected: false` and
  `can_confirm: false`; `select_card index=0` came back *"Toggling card selection: Defend"* and
  the next read showed row 0 `selected: true`, rows 1–3 `selected: false`, and `can_confirm`
  flipped to `true`. Pages `item14-enchant-chooser`, `item14-enchant-chooser-selected`.
- **`EB-181`, the card face carries `enchantment` — PASS.** Two floors later, in the next
  fight, the enchanted Defend's hand entry read
  `"enchantment": {"id": "NIMBLE", "name": "Nimble", "description": "Increases Block gained
  from this card by 2.", "amount": 2, "shows_amount": true}`, its printed description had moved
  from "Gain 5 Block." to **"Gain 7 Block."**, and it carried the Nimble keyword tip. The
  unenchanted Defend beside it in the same hand had no `enchantment` key and still read "Gain
  5 Block.", which is the comparison that makes the reading worth anything.
- **`EB-734`, the chooser rows carry the same tag the hand entry carries — NOT DONE.** This
  needs a **second** enchant chooser opened while an already-enchanted card is in the deck, so
  its row can be compared with the hand entry. `SELF_HELP_BOOK` refuses a second visit in the
  same run, and the one other enchant door in reach (`SPIRALING_WHIRLPOOL`) gates on the deck
  holding a Spiral-enchantable card. It was not set up before the lane moved on.

**Board writes in this section: none.**

## 15. EB-269 — a self-targeted potion used live through the wire — PASS

Launch 2, act 1 Liyue, floor 12, in combat, one call:

```
potions before: [('Swift Potion', 0, 'AnyPlayer'), ('Colorless Potion', 1, 'AnyPlayer'), ('Fire Potion', 2, 'AnyEnemy')]
hand size before: 5
use_potion slot 0 -> {'status': 'ok', 'message': "Using potion 'Swift Potion' from slot 0 on self"}
potions after: [('Colorless Potion', 1), ('Fire Potion', 2)]
hand size after: 8
```

The belt went 3 → 2, the answer says **on self** rather than asking for a target, and the
potion's printed effect ("Draw 3 cards.") happened — the hand went 5 → 8. One potion consumed,
which is what the row asks for. **Board writes in this section: none.**

## 16. The hygiene set

**Read the warning under this list before quoting any archived log: the teardown archives the
WRONG LANE's file.** Everything below is read off the **live** lane-1 `godot.log`
(`%LOCALAPPDATA%\gits-lanes\lane1\SlayTheSpire2\logs\godot.log`) while the lane was up, plus
the one archived copy that is genuinely lane 1's.

- **`EB-274` — a shop with no `Expected BoundObject to be a SpineSprite`. PASS.** Launch 4,
  act 3 Sumeru, floor 16: the shop opened and rendered (page `item16-shop`: eight cards with
  costs, types and prices, a **Parrying Shield** relic at 236 gold with its rules text, and
  the removal service). The live lane-1 `godot.log` at that moment — 3,046 lines, 322 KB,
  after a boot, a shop, an act skip, two acts and roughly a dozen fights — carried **0**
  occurrences of `Expected BoundObject to be a SpineSprite`.
- **`EB-275` — a fight with no `AtlasResourceLoader: Missing sprite`. PASS on lane 1.** The
  same live log carried **0** of them, over every fight that run played. (The archived copies
  do carry one `'snake_ring' in relic_outline_atlas` at boot and two
  `furina/kleemod-proto_fs_curtain_rise_mode_a` / `_b` in `card_atlas` — but those files are
  **lane 0's game**, not this lane's, for the reason in the warning below, so they are not
  this round's reading and are not counted against this row. They are worth a look by whoever
  owns lane 0's Furina rounds: those two card faces are missing from the shipped `card_atlas`.)
- **`EB-292` — NCardTrail's catch line.** `grep -c NCardTrail` over the live lane-1
  `godot.log` and over the lane-1 archive: **0**. The catch never fired this round.
- **`AssetLoadException` and `Element limit reached`: 0** in the live lane-1 log, over every
  launch, the Punch-Off included.
- **`EB-435` — the lone-lane embark reads its own seed and logs under its lane.** Every launch
  read its seed back off the wire and recorded it in its own lane-1 sidecar
  (`understudy/logs/embark-<stamp>.json`, `instance: lane1`, `port: 15527`), and every
  `godot.log` read was `%LOCALAPPDATA%\gits-lanes\lane1\SlayTheSpire2\logs\godot.log`.
  **`seed_read_back_crossed`: 0** across every log written today, with lane 0 up and embarking
  its own Klee / Kokomi / Furina runs at the same time.
- **`EB-191` — `seed_not_honoured`.** **0** across every launch this round.
- **`EB-510` — doubled `Your hand` / `The other side` headings.** `blindplay.observe` runs
  `assert_one_page` before it returns, so a doubled section comes back as a refusal rather than
  a page. **182 pages were rendered off live state this round and 0 were refused**, and no page
  sha needed recording.
- **`EB-325` — the page's map block against the harness's reachable set.** Three act-1 map
  screens compared, and all three agree exactly, in kind and in order:

  | page | "Where you can go next" | `next_options` on the wire |
  |---|---|---|
  | floor 5 | Monster (path 1), Unknown (path 2) | `[(0,'N','Monster'), (1,'?','Unknown')]` |
  | floor 6 | Monster (path 1) | `[(0,'N','Monster')]` |
  | floor 7 | Monster (path 1), Unknown (path 2), RestSite (path 3) | `[(0,'N','Monster'), (1,'?','Unknown'), (2,'R','RestSite')]` |

  The page's *"floors ahead"* block is a wider listing (every room on the floor, not the
  reachable ones) and is not what this compares.

### The defect this section found: a lane-1 teardown archives LANE 0's `godot.log`

`EB-766` copies the session's `godot.log` aside at teardown so a round's evidence survives
Godot's rotation. On a **lane-1** teardown it copies the wrong file.

**The evidence is in the copies themselves.** Every archive this round written under one of my
lane-1 stamps opens with

```
User Data Directory: C:/Users/Monty/AppData/Roaming/SlayTheSpire2
```

— lane 0's tree, the owner's own `%APPDATA%` — while the one copy taken *during* a session, by
the boot fuse (`20260916-112242-28916-stall1.log`), correctly opens with

```
User Data Directory: C:/Users/Monty/AppData/Local/gits-lanes/lane1/SlayTheSpire2
```

Five of six archives are the other lane's game. It is why an **Ironclad** run's "own" log
appeared to load two **Furina prototype card faces**: those were lane 0's Furina embark,
running beside mine.

**Cause, and it is two lines.** `understudy/embark.py:580` rebuilds the session for the
teardown as `soak.Session(stamp, do_setup=False, intent="")` — **with no `instance=`** — and
`understudy/soak_session.py:653-659`'s `log_path` resolves a `None` instance to
`Path(os.environ["APPDATA"])`, i.e. lane 0. That contradicts the rule stated in the same
file's own `__init__` (soak_session.py:247-248): *"`None` MEANS 'WHATEVER THIS THREAD IS
ALREADY ON' -- not 'lane 0'."* `teardown` does bind the thread (`bridge.use(...)` at
`embark.py:570`), so the lane is known; `log_path` just does not ask.

**Repro:** `python -m understudy.embark --character IRONCLAD --lane 1`, play anything, then
`python -m understudy.embark --teardown --lane 1`, and read the first "User Data Directory"
line of the file the teardown names. **Fix shape (not applied here):** pass the recorded lane
into the rebuilt session, or make `log_path` fall back to `bridge.current_instance()` rather
than to `APPDATA`. This is the same family as `EB-210` / `EB-435` — a per-process fact read
from a process-wide place — and it matters because a lane-1 round that files a log-based
finding is filing it against somebody else's game.

## What could not be done, and why

- **`EB-363` THE_FUTURE_OF_POTIONS under the three arms (item 6)** — the gate is
  `Players.All(Potions.Count() >= 2)` and a run that `skip_act`s into act 2 or 3 starts with an
  empty belt, so the shape needed is: embark under the arm, skip, fight until the belt holds
  two, then force. That is one whole launch per arm and the round's launches went on items 1
  to 5 instead. Nothing here contradicts `PR #543`; it is simply unlooked-at, exactly as
  proofs-6 and proofs-7 left it.
- **`EB-459` Neow's Arcane Scroll under Kokomi (item 10)** — five Neow screens were read this
  round and **none of them rolled Arcane Scroll**; the Neow offer is a roll and there is no
  door in the bridge that sets it. (The relic itself did turn up, from an Ancient, on an
  Ironclad run, so the relic exists in the pool this build ships.) Reaching this needs either
  luck or a `give_relic` op the bridge does not have — `GitsDebugState.cs` has
  `set_resource`, `set_energy`, `set_hp`, `set_block`, `set_power`, `clear_hand`, `hover`,
  `unhover`, `force_next_event` and `skip_act`, and **no relic or gold write at all**. That
  also puts `RELIC_TRADER`, `RANWID_THE_ELDER` and `WELCOME_TO_WONGOS` out of reach of a
  short tour, since their gates want five tradable relics or 100 gold.
- **`EB-734` (item 14's first half)** — needs a second enchant chooser opened with an
  already-enchanted card in the deck; see §14.
- **Three of `EB-84`'s four eligibility shapes** — one visit shows one or two; see §14.
- **`EB-269`'s other half is not owed and was not done** — only one potion was used, which is
  what the row asks.

## What else the round learned, for the next driver

- **A forced event is not safe until you stand on it.** A `?` room that serves some *other*
  event moves the act's cursor past the one you forced: on Fontaine a forced
  `BATTLEWORN_DUMMY` was overtaken by `BALLAST_CHECK_ON_THE_MEROPIDE_LIFT` and then
  `SOUNDING_THE_BERYL_SHELF` two `?` rooms running. The fix that worked is to **re-force
  before every `?` step**, which costs one extra op per floor and nothing else. This is beside
  proofs-7's Ancient finding, not instead of it — the Ancient rule held again here on
  Inazuma (`PAEL`), Fontaine (`NONUPEIPE`) and Sumeru (`TANX`).
- **A `?` node is not necessarily an event room at all.** One `?` on Fontaine opened a
  **treasure** room, and two on Liyue resolved into nothing this driver saw at all — the run
  simply stood on the next floor's map. So "walk to the next `?`" is not the same as "reach
  the forced event", and a driver must compare the `event_id` it arrived at rather than assume.
- **`?` rooms are scarce, and a `?` spent early is one the force cannot use.** Liyue's act-1
  map on seed `WPLH2R37QFKZ` has `?` rooms only at floors 4 and 7, and PUNCH_OFF's gate wants
  floor 6. Two launches were lost by climbing through both before forcing. Climb on `N`, `R`,
  `T`, `$`, `E` and save the `?`.
- **Some `?` nodes on the map are Ancients and the wire says so before you walk.**
  `choose_map_node` answers *"Traveling to Ancient at (3,0)"*, so a driver can tell an Ancient
  from an event room at the moment it steps, instead of after.
- **A rebuilding enemy defeats `set_hp` softening if anything is played in between.** An act-3
  `AXEBOT_0` set to 1 HP climbed back to 44 over thirteen rounds because the driver's first
  playable card was a Skill. `set_hp` and the attack have to be adjacent.
- **The dummy fight is lost on a timer, not on a death.** `Time Limit` counts down on the
  enemy's own status block and the fight ends itself at zero. proofs-7 thought a loss needed
  `set_hp player 1`; it needs nothing at all.

Frames were not captured this round — the evidence is page text and wire payloads, both of
which are checkable against the file and line named beside them. The 182 rendered pages and
their state snapshots were kept in the session scratchpad, which is not the tree; the driver
itself (`drv.py`, `tour1.py`, `tour2.py`, `camp4*.py`) is scratch and is not committed, as
proofs-6 and proofs-7 did with theirs. No register was edited, no row retired, and no C#
changed.

Status: RECORD (deploy live looks; feasibility only, nothing measured)

# proofs-10, lane 0: the Kurage Memory half

**Build:** installed `0.2.3581+proto.dirty`, read off
`C:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2\mods\klee\manifest.json`,
`min_game_version` `0.111.0`, BaseLib `3.4.7`. The installed `klee.dll` is
byte-identical to `klee-mod/dist/klee/klee.dll`
(md5 `E3322A6340B70B802A847B49C2CA2DA5`), so the build under test is the one
main just deployed.

**Arms `klee,companion,furina-stage,teyvat`, and the Kokomi overhaul arm is
OFF.** That is the whole reason this job exists: `KurageMemory.IsLive` is
`!KokomiOverhaul.Enabled && IsKokomi`, so this is the only deploy shape on
which the memory is live at all. It was live — every combat page carried a
"The Bake-Kurage's memory" block and `player.kurage_memory` was populated on
every read.

**Lane 0 only**, the owner's profile, port 15526, no `--lane` flag and no
`GITS_LANE` anywhere. Another agent held lane 1 (pid 7716, launched 16:39:17,
after this lane's game); nothing here touched its process, its log or its
sidecar, and the one kill was `understudy.embark --teardown` killing the pid
this job's own sidecar recorded (28380). No `taskkill /IM` was issued. The
bridge was **already installed by the deploy** and is recorded as pre-existing
in this job's reversibility ledger ("shared, left in place"); nothing here
deployed, rebuilt, staged or validated anything, and no register row, `LAW.md`,
`EXPERIMENTS.md`, `QUEUE.md` or `STATE.md` line was edited. After teardown,
`Get-Process SlayTheSpire2` listed 7716 alone.

**One caveat about that, and it is the job's worst finding:** the FIRST frame
this job took was a frame of **lane 1's game**, not lane 0's, because
`frames.capture` defaults to `pid=None` and takes whichever
`SlayTheSpire2.exe` window Windows hands it. It was deleted unread-into-the-
record and re-taken pinned to pid 28380. See "defects" 1. Nothing was written
to, focused or moved on lane 1; the call reads pixels and nothing else.

**Frames:** `review/qa/proofs-10-lane0-2026-09-16/`, with
`frames-manifest.jsonl`. One frame, cited by §4b, and committed.

---

## The honesty preamble

**Nothing in this record is a measurement.** There is no pre-registration, no
blind grading, no slate and no register row, and nothing below is comparable to
any soak, any run, or any other board.

**Most of the board read here was written by hand.** Six cards were granted
with `give_card` (`Field Promotion`, `All Hands`, `Bake-Kurage`, `Water's
Edge`, two `Gorou — Inuzaka All-Round Defense`), two enemies were set to 1 HP
with `set_hp` to end a fight a hand-built deck was not going to finish quickly,
and one event was moved into place with `force_next_event SELF_HELP_BOOK`.
`bridge.GRANT_GUARDRAIL` is the governing sentence and it printed on every one
of those answers. So each section below carries the one page row or wire field
its row's acceptance sentence names, and a verdict on whether that sentence is
true on this build. A PASS means "the sentence the row owed is true here, on a
board built to ask it" — never that the card is good, balanced or fun.

**No code was changed in this job**, by rule, and the driver (`drv10.py`) is
scratch and is not committed, as proofs-6 through -9 did with theirs.

Three limits, stated rather than left to be noticed:

1. **`n = 1` everywhere.** One boot, one embark, one enchant, one frame.
2. **EB-248's third surface, the in-game gauge STRIP, was not read as text.**
   The strip's label is a hover-rendered pixel and this harness has no mouse;
   what was read is the page and the wire, plus the strip's one-line `reading`
   field. Said here rather than rounded up — see §3.
3. **The `EB-790` acceptance is about CARD ids, and one KLEEMOD RELIC id still
   warns.** The item passes on its own sentence and the relic is filed
   separately (§"defects" 2) rather than folded into the verdict.

**Board writes, counted off the archived `godot.log`**
(`understudy/logs/godot/20260916-163737-28380.log`):

| run | `set_hp` | `set_power` | `set_energy` | `give_card` | `give_relic` | `force_next_event` |
|---|---|---|---|---|---|---|
| Kokomi `KNNUBD8HBLAB` | 2 | 0 | 0 | 6 | 0 | 1 |

**One embark, one teardown, no crash and no stall.** In the archived log:
`AssetLoadException` 0, `Element limit reached` 0, `NCardTrail` 0,
`Expected BoundObject to be a SpineSprite` 0.

## The one-line verdicts

| # | item | verdict |
|---|---|---|
| 1 | `EB-790` a lane-0 boot logs no `Unknown card ID` / `Unknown CardModel ID` for any KLEEMOD- id | **PASS** (0 of 680 unknown-id warnings are ours) |
| 2 | `EB-247` the memory's buff, tip and docket agree with the wire's `pulse_kind`, and the number promised is the number dealt | **PASS** |
| 3 | `EB-248` a Muster-discounted queue entry's price is derivable from what the queue prints | **PASS**, with the zero-price case noted |
| 4a | `EB-789` / `EB-793` an enchanted card's pile and `master_deck` rows print the enchanted face | **PASS**, both |
| 4b | `EB-788` the capture fix gives a complete frame on this machine | **PASS** (`complete: true` at `render_scale` 1.5) |

## The run

| stamp / pid | character | seed | ascension | what it was for |
|---|---|---|---|---|
| `20260916-163737` / 28380 | Kokomi, A3 | `KNNUBD8HBLAB` | 3 | every item |

`EB-763`'s run-history warning printed on the launch (1,332 files, 51.0 MB) and
**nothing here deleted or edited the owner's store**.

---

## 1. `EB-790` — a boot with the old save logs no `ValidationError` for one of ours — **PASS**

The owner's profile is the one that holds the retired id
`KLEEMOD-PROTO_FR_SALON_DEBUT_NAMED` (`EB-726`), which is what made this row.
The lane-0 boot's own `godot.log`, archived by teardown:

```
$ grep -c "Unknown card ID: CARD.KLEEMOD\|Unknown CardModel ID: CARD.KLEEMOD"
0
$ grep -in SALON_DEBUT
(no hits)
```

**Zero.** Not "few" — the string does not occur.

The boot is not quiet, and that is the comparison that makes the zero worth
something. It logs **719 `ValidationError` lines**, of which 680 are unknown
card or CardModel ids, and every one of them is the base game's, from the
owner's long save:

| `Message = Unknown … ID` | count |
|---|---|
| `CardModel` | 378 |
| `card` | 302 |
| `Relic` | 25 |
| `character` | 9 |
| `Potion` | 4 |
| `encounter` | 1 |

and the unknown-card ids group by base-game prefix, with no KLEEMOD prefix
among them:

```
Unknown card ID:       AUTOMATON 6, AWAKENED 64, CHAMP 1, HERMIT 47,
                       HEXAGHOST 29, SLIMEBOSS 73, SNECKO 76
Unknown CardModel ID:  AUTOMATON 18, AWAKENED 75, CHAMP 1, GUARDIAN 2,
                       HERMIT 51, HEXAGHOST 33, SLIMEBOSS 81, SNECKO 82,
                       + ~20 singletons (CARD.DUCK_AND_COVER, CARD.JUMPY_DUMPTY,
                       CARD.KABOOM, CARD.POP, CARD.QUICK_FINGERS, the TAR_*
                       tarot family, …)
```

Those singletons are the *other two* mods installed beside ours
(`STS2AutoSlayMod`, `quick_fingers`) and the base game's own retired ids; none
carries a `KLEEMOD-` prefix. `docs/retired-card-ids.yaml`'s 54 hidden aliases
do the job they were built for.

**The one KLEEMOD `ValidationError` in the whole file is a RELIC, not a card:**

```
[WARN] Progress parse: ValidationError { Severity = Warning, Path = DiscoveredRelics,
       Message = Unknown RelicModel ID: RELIC.KLEEMOD-TAMANOOYAS_CASKET, IsFatal = False }
```

That is the Tamakushi Casket, Kokomi's relic, which this deploy's arm set does
not register — the same "the arm is off, the id is not in ModelDb, the save
still has it" shape the row was filed on, one namespace over. The row's
acceptance names card ids and is met. The relic is §"defects" 2.

*The save was never touched.* This item read a log and nothing else.

## 2. `EB-247` — text and `pulse_kind` agree on every page of one fight — **PASS**

The row's own words: *"text and `pulse_kind` agree on every page of one
fight."* Four surfaces were read, together, at three states of the pulse, on
fight 1 and fight 2 of one run:

* the **persistent buff** on the board header (`KuragePowers.cs`),
* the **fielding tip** — `Bake-Kurage`'s `Bake-Kurage pulse` hover tip
  (`KokomiRiderTips.PulseBody`), granted into hand for the read,
* the **end-of-turn docket** — the page's "At the end of this turn the
  jellyfish will …" line,
* the **wire** — `player.kurage_memory.{pulse_kind, pulse_amount, pulse_unit}`.

The buff, which does not change, states the three rates:

> *Bake Kurage 1 (buff)* — At the end of your turn, the jellyfish answers the
> last card you played this turn. **After an Attack: it deals 4 damage** and
> applies Hydro to a random enemy. **After a Skill: it grants 5 Block.** After
> a Power: it banks 1 Charge. **If you played no card at all, it does nothing.**

and the other three move together with it:

| state | wire | tip | docket |
|---|---|---|---|
| nothing played | `none` / 0 / `none` | *"You have played nothing yet this turn: no pulse."* | *"will do nothing, because you have played no card this turn"* |
| a Skill played (`Coral Guard`) | `skill` / 5 / `block` | *"Last card played: skill. The next pulse is 5 block."* | *"will give you 5 Block"* |
| an Attack played (`Water's Edge`) | `attack` / 4 / `damage` | *"Last card played: attack. The next pulse is 4 damage."* | *"will deal 4 Hydro damage"* |

Three states × four surfaces, no disagreement, and the tip's rule paragraph
quotes the same three rates the buff does — `4 damage and Hydro / 5 Block /
1 Charge` — with **no `4 + 3x Charge` anywhere**, which is the retired
arithmetic the row was filed on. `KokomiRiderTips.PulseBody` reads
`KurageMemory.Forecast`, the same triple `Snapshot` publishes, so tip, docket
and wire cannot fork.

**The number it promises against the number it deals.** Fight 1, turn 1, the
cleanest beat in the run because it is the only card played:

1. Board: `Leaf Slime (S)` at **12/12**.
2. `Water's Edge` played on it — the page's own resolution row:
   `1. **Leaf Slime (S)** -- 6`. Leaf Slime **6/12**.
3. Page and wire both promise **4** (`attack` / 4 / `damage`; *"will deal 4
   Hydro damage"*).
4. `end turn`. Next page: `Leaf Slime (S) [A] — FRONT — HP 2/12`.

**6 − 4 = 2. The pulse promised 4 and dealt 4.** It is not Charge-scaled and
does not claim to be: the bank was `Charge: 0` on that turn and later in the
same fight stood at 3, 4, 6 and 7 with the promise still reading 4.

*One nuance, recorded rather than filed.* Mid-resolution — with `Field
Promotion`'s Muster chooser open, after the card had left the hand but before
the transform confirmed — the wire read `pulse_kind: none`. The page at that
moment was the chooser and printed no docket line, so no two surfaces
disagreed; the moment simply has no reading. Both went to `skill` the instant
the chooser closed.

## 3. `EB-248` — a discounted entry's price, derivable from what the queue prints — **PASS**

The mechanism is `KurageMemory.PriceText`: `"{price} Charge, cost {cost} x 3"`,
or `"free"` at price 0. It reached the page. Four entries were put in one queue
by hand, deliberately spanning the cases:

```
- Charge: 7
- Next to fire: **Coral Guard** — costs 3 Charge — it fires at the start of your next turn.
- Opening the memory shows "Gain 1 Charge when a card of yours Exhausts", and then
  the whole memory, front first:
  1. **Coral Guard** — 3 Charge, cost 1 x 3 — aims at random
  2. **Kujou Sara — Tengu Stormcall** — free — aims at Twig Slime (M)
  3. **Water's Edge** — 3 Charge, cost 1 x 3 — aims at random
  4. **Itto — Superlative Superstrength** — 6 Charge, cost 2 x 3 — aims at random
- Charge runs out at #4 (**Itto — Superlative Superstrength**): that one and
  everything behind it are held until the bank catches up.
```

Every priced row carries its own derivation — `3 Charge, cost 1 x 3`,
`6 Charge, cost 2 x 3` — and the wire agrees row for row
(`{"name": "Coral Guard", "cost": 1, "price": 3, …}`,
`{"name": "Itto — Superlative Superstrength", "cost": 2, "price": 6, …}`).

**The discounted entry is row 2, and it is the row this item exists for.**
`Kujou Sara — Tengu Stormcall` arrived from `Field Promotion` — *"Muster 1, **at
cost 0**"* — and its hand face said so in as many words:

> **Kujou Sara — Tengu Stormcall** [Electro] — cost 0, skill …
> *The cost printed on this card is 1; it is showing 0 here.*

It enrolled by rule 2 (it Exhausts) at `cost: 0, price: 0`, i.e. at the
discount and not at the printed 1 — `NoteMusterRecruit`'s stamp doing exactly
what §11.4 asks — and the queue printed it as **free**, with the "Next to fire"
line later reading *"costs nothing"*. A reader of the queue can say what the
entry costs without leaving the page.

**And the price the page printed is the price the bank paid.** With `Charge: 7`
and `Coral Guard` at the front at `3 Charge`, `end turn` fired it at the next
turn start — the page marked the replay *"(the game played this one, not
you)"* — and the bank read **4** on the next page. 7 − 3 = 4, the printed
number, to the unit.

**Two things this section does not claim.**

*The strip was not read as text.* `PriceText` also feeds `StripText`, the
in-game gauge label, which renders on hover; this harness has no mouse and the
committed frame shows the strip as a card thumbnail with the bank number under
it, not its label. What stands in for it is the wire's one-line `reading`
field, which moved correctly throughout
(`"Charge 0 / 3 — Coral Guard blocked"` → `"Charge 3 / 3 — Coral Guard fires
next turn"` → `"Charge 4 / 0 — Kujou Sara — Tengu Stormcall fires next turn"`).

*The zero case prints the answer but not the arithmetic.* `free` is a price and
is derivable in the trivial sense, but it is the only row on the page that
does not show its `cost x 3` — and it is precisely the row where the discount
did the most work. Raised in §"defects" 4 rather than held against the row.

## 4a. `EB-789` / `EB-793` — the enchanted face in the pile and in `master_deck` — **PASS on both**

`force_next_event SELF_HELP_BOOK` → the Mondstadt dressing *The Guild Desk's
Returned Copy* on floor 3 → **Read a Random Passage** (`Nimble`, Skills) →
`Coral Guard` enchanted with **Nimble 2**. `Coral Guard`'s written face is
`Gain 5 Block`, so the enchanted face is `Gain 7 Block` — the same shape
`EB-789` was filed on.

**`EB-793` — `master_deck`, read out of combat**, on the event screen
immediately after the enchant. Four `Coral Guard` rows, and the deck list
**splits the enchanted copy into its own row**:

```json
{"id": "KLEEMOD-CORAL_GUARD", "name": "Coral Guard", "is_upgraded": false,
 "description": "Gain 7 Block.",
 "keywords": [{"name": "Nimble", …}, {"name": "Block", …}],
 "enchantment": {"id": "NIMBLE", "name": "Nimble", "amount": 2, "shows_amount": true},
 "pile": "Deck"}
{"id": "KLEEMOD-CORAL_GUARD", "name": "Coral Guard", "description": "Gain 5 Block.",
 "keywords": [{"name": "Block", …}], "pile": "Deck"}      ← ×3, unenchanted
```

The row's acceptance is *"a `master_deck` row carries id, is_upgraded, keywords
and enchantment live"* and all four are on it. That closes proofs-9's
§"defects" 4, which found `master_deck` rows carrying neither `keywords` nor
`enchantment`.

**`EB-789` — the pile.** Fight 2, floor 4. The enchanted copy in hand printed

```
- **Coral Guard (3)** (Nimble 2) — cost 1, skill
    Gain 7 Block.
    Written: Gain 5 Block.
    *Nimble* — Increases Block gained from this card by 2.
```

It was played (Block went 0 → **7**, the printed number), which put it in the
discard pile, and the pile row is the hand row:

```json
discard_pile: {"name": "Coral Guard", "id": "KLEEMOD-CORAL_GUARD", "is_upgraded": false,
               "description": "Gain 7 Block.",
               "keywords": [{"name": "Nimble", …}, {"name": "Block", …}],
               "enchantment": {"id": "NIMBLE", …}}
draw_pile:    {"name": "Coral Guard", "id": "KLEEMOD-CORAL_GUARD", "is_upgraded": false,
               "description": "Gain 5 Block.",
               "keywords": [{"name": "Block", …}], "enchantment": null}
```

**Pile and hand print one face**, which is the row's acceptance word for word,
and the unenchanted copy sitting in the draw pile at `Gain 5 Block` is the
comparison that makes it worth something. `pile_description` was `null` on
every row — the pile's own face and the hand's face were the same string here,
so the field had nothing to keep.

## 4b. `EB-788` — a complete frame on this machine — **PASS**

One frame, default route (`route_requested: "auto"`), pinned to lane 0's pid,
of the fight-1 combat board. The manifest row, quoted rather than summarised:

```json
{"record": "frame",
 "path": "review\\qa\\proofs-10-lane0-2026-09-16\\frame-20260916-164503-eb788-kokomi-combat-default-route.png",
 "size": "3840 2160", "client_size": "3840 2160", "render_extent": "5760 3240",
 "render_scale": [1.5, 1.5],
 "complete": true, "complete_note": "the frame covers the whole client area",
 "route": "printwindow", "route_requested": "auto",
 "pid": 28380, "instance": "lane0",
 "context": {"screen": "combat", "act": 1, "floor": 2, "seed": "KNNUBD8HBLAB"}}
```

**`complete: true`, on `printwindow`, at the exact 1.5× the row's scope
names** — client 3840×2160, render extent 5760×3240. That is the defect's own
condition, met and handled: #589's oversize sentinel canvas measured the extent
and resampled it back to the client size instead of keeping the top-left two
thirds.

And the picture agrees with the flag. The frame shows the full board: the run
header with seed `KNNUBD8HBLAB`, Kokomi and her Bake-Kurage with the 6/20 Burst
bar, **both enemies with their HP bars and aura badges** (`2/12` with Hydro 1,
`23/27` with Electro 2), the memory strip and its `7` at the left, the End Turn
button at the right, and **the entire card hand with its cost badges** —
`Water's Edge`, `Gorou — Inuzaka All-Round Defense`, `Coral Guard`,
`Kujou Sara — Crowfeather Cover`, `Thoma — Blazing Barrier`. The hand is what
the row's acceptance names, and it is there.

*No comparison run was taken against `copyfromscreen`*, because #589's claim is
about the default route and the default route answered.

---

## Defects found that are not on any row above

Raised, not filed — a register row is [USER]'s to mint or Claude's under the
hygiene rule, and this is a record.

1. **`frames.capture` picks an arbitrary game window, so a two-lane sitting can
   frame the wrong lane.** `understudy/frames.py:635` defaults `pid=None`, and
   `build_script` then matches by IMAGE NAME (`SlayTheSpire2.exe`). This job's
   first capture, taken from the lane-0 worktree while lane 0 held pid 28380,
   returned **lane 1's Klee run** — seed `1GQ14VG4JFT4`, HP `50/62`, `Ka-pow!`
   in hand — where lane 0 was Kokomi on `KNNUBD8HBLAB` at `57/80`. It came back
   `status: ok`, `complete: true`, `3842 2160`: nothing in the answer says it is
   the wrong game. The manifest row it wrote recorded `"pid": null` and an
   `instance` and `context` **copied from the caller**, so the row asserted
   `lane0` / `KNNUBD8HBLAB` over a picture of neither. The frame was deleted and
   re-taken with `pid=28380`. Two halves worth fixing: `capture` could resolve
   the pid from the caller's lane sidecar when none is given (the sidecar has it
   — `reversibility-*.json` n=3 carries `"pid": 28380`), and a frame taken with
   `pid=None` while more than one `SlayTheSpire2.exe` is up could at minimum
   carry a warning on its row. This is the same family as the lane hazards in
   `operations/understudy-seats.md`, which cover the bridge, the deploy and the
   log cursor but not the camera. Repro: run two lanes, call
   `frames.capture()` with no `pid`.

2. **A KLEEMOD RELIC id still warns on every boot, and `EB-790`'s machinery
   does not cover relics.** `Unknown RelicModel ID:
   RELIC.KLEEMOD-TAMANOOYAS_CASKET`, once per boot, on the owner's profile,
   `Path = DiscoveredRelics`. The cause is arm shape, not retirement — the
   Tamakushi Casket is Kokomi's relic and the `kokomi` arm is off on this
   deploy — but the effect is exactly `EB-790`'s: a save remembers an id the
   running ModelDb has no model for, and warns. `docs/retired-card-ids.yaml`
   and the `retired-card-ids` lint are card-only, so an arm-gated relic (and a
   retired one, when there is one) has no alias to hide behind. One line per
   boot, `IsFatal = False`.

3. **A create-mode Muster never stamps its recruit's discount, so the recruit's
   memory entry is priced off the undiscounted face.**
   `klee-mod/KleeCode/Powers/KokomiConscript.cs:128` calls
   `KurageMemory.NoteMusterRecruit` only inside the sacrifice branch — create
   mode `continue`s above it, correctly skipping `NoteMuster` (no sacrifice, no
   rule-1 memory) but skipping the recruit's cost stamp with it. Live: `All
   Hands` (*"Muster 2, **adding the units to your hand**"*) produced `Itto —
   Superlative Superstrength`, whose hand face read *"cost 0 … The cost printed
   on this card is 2; it is showing 0 here"*, and whose rule-2 entry enrolled at
   `{"cost": 2, "price": 6}` and printed **`6 Charge, cost 2 x 3`**. The
   comparable sacrifice-mode recruit in the same queue (`Kujou Sara — Tengu
   Stormcall`, from `Field Promotion`) enrolled at `{"cost": 0, "price": 0}`.
   So §11.4's *"a Muster's own −1 counts on the RECRUIT's own entry"* holds for
   sacrifice-mode Musters and not for create-mode ones, and the same card can
   be worth 3 or 6 Charge depending on which card mustered it. Repro: play
   `All Hands`, then play a recruit it created, and read
   `player.kurage_memory.queue`.

4. **`PriceText` drops the derivation at price 0.**
   `KurageMemory.cs:1261-1264` returns the bare string `"free"` when
   `price == 0`, so the one queue row whose price a reader most needs explained
   — the fully discounted one — is the one row that does not print
   `cost N x 3`. On the live page: `2. **Kujou Sara — Tengu Stormcall** —
   free — aims at Twig Slime (M)`, beside three rows that each show their
   arithmetic. `EB-248`'s own scope sentence is *"could not be derived from the
   face"*, and a card printing cost 1 in hand against an entry printing `free`
   is that shape in miniature. `free — cost 0 x 3` would cost four words.

5. **Not a defect, recorded because it cost time.** `blindplay act` matches card
   titles exactly, and every Companion title carries an em dash (U+2014). Passed
   through a Git-Bash single-quoted argument the character survives; passed
   through a `for` loop or any construct that re-encodes it, it does not, and
   the refusal is the generic *"nothing here is called …"*. The reliable form is
   `sys.argv` assembled in Python with an explicit `\u2014`.

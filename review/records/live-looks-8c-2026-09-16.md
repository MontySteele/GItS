Status: RECORD (deploy live looks; feasibility only, nothing measured)

# Live looks 8c — the four leftovers from 8b

**Build:** installed `0.2.3480+proto.dirty`, read off `mods\klee\manifest.json`,
arms `klee,companion,kokomi,furina-stage,teyvat`, BaseLib 3.4.7, game
v0.111.0 — the same install 8b read, and nothing here deployed, rebuilt or
staged anything. **Lane 0 only**, the owner's profile, port 15526.

**Runs.** One embark on lane 0, torn down after: `S0MEFFP7PMNA` (Klee, A0,
act 1 floors 1–7), granted `proto_mi_gorou_war_banner`,
`proto_mc_barbara_front_row_seat`, `proto_mc_diona_shaken_not_purred` and
`proto_mc_noelle_i_got_your_back` into the starting deck at embark. Then **two**
runs of `understudy/scenarios/furina-hover-states.yaml`, each with its own
setup (never `--no-setup`), also on lane 0: the first stopped on a defect, the
second is green. Three game launches in all, **no crash and no stall**, and no
`manual_epoch_reveal_required` on any menu.

**Lane 1.** Another agent held lane 1 (pid 40640) when this job started.
Nothing here touched it, and it was gone before this job's own teardown: its
log was copied out at 12:52 (`understudy/logs/godot/20260916-124853-40640.log`)
and lane 0 was torn down at 13:03. Every kill in this job was by this job's own
pid (25068, then 29412, then 39840); no `taskkill /IM` was issued and no frame
was captured by image name.

**Frames:** `review/qa/live-looks-8c-2026-09-16/`.

---

## The honesty preamble

8b's preamble governs this document unchanged, and it is repeated rather than
cited because it is the frame every line below sits in.

**Most of what is read here was written by hand.** Cards were granted through
`give_card`, a debuff set through `debug_state`, an enemy's HP dropped to 1 to
get past a fight and reach a map node. `bridge.GRANT_GUARDRAIL` is the
governing sentence: *nothing measured on such a board is comparable to any
soak, any run, or any other board*.

So this record contains **no numbers that compare anything**. Per row it
carries the one screen or the one number that row's acceptance sentence names,
and a verdict on whether that sentence is true in the running game. A PASS
means "the sentence the row owed is true on this build, on a board built to ask
it" — never that the card is good, balanced, legible or fun. **No code was
fixed in this job**, by rule.

Three limits, stated rather than left to be noticed:

1. **`n = 1` everywhere.** One banner, one enchant screen, one shop.
2. **A frame proves a pixel, not a judgement.** Every claim made off a frame
   below is mechanical (this region changed; this region contains no
   character) and nothing else.
3. **One of the four is still NOT DONE**, and its reason is named rather than
   softened.

**One file changed outside this record**, and it is a hygiene fix rather than a
finding: `understudy/scenarios/furina-hover-states.yaml` now addresses
`Salon Début` by id rather than by title, because two live cards answer to that
title and the wrong one was played. The reason is under `EB-652` below and is
written into the file itself.

---

## The four leftovers

### `EB-415` — Gorou, General's War Banner, upgraded — **PASS**

**Which arm offers it.** Not the Furina Stage arm. The row is
`proto_mi_gorou_war_banner` at `docs/prototype-surface.yaml:1360`, declared
`character: klee`, so it is a Companion row on the Klee/companion prototype
arm; it was granted into a Klee run's starting deck at embark.

The acceptance sentence is *"Dexterity after the banner ends equals Dexterity
before it, upgraded or not."* Read on the upgraded face, which is the one that
leaked:

| when | `player.status` rows, raw off the wire |
|---|---|
| before the play | `SPARK_POWER` only — **no `DEXTERITY_POWER` row at all** |
| on the play (round 1) | `DEXTERITY_POWER` **3**; `WAR_BANNER_POWER` 2, *"You have 3 more Dexterity. Lasts for 2 turns, then takes 3 back."* |
| round 2 | `DEXTERITY_POWER` **3**; `WAR_BANNER_POWER` 1, *"… Lasts for 1 turn, then takes 3 back."* |
| round 3, clock ended | `SPARK_POWER` only — **no `DEXTERITY_POWER` row**, and no banner |

Dexterity before **0**, Dexterity after **0**, on the face that grants 3. The
leak the row was filed on (1 permanent Dexterity a play) is gone, and the
badge names the banked number rather than the arm's constant — which is
`EB-415`'s own build doing what its doc comment says
(`klee-mod/KleeCode/Powers/Prototype/CompanionOverhaulInazuma.cs:159-246`:
`Granted` is banked in a `DynamicVar` at `AfterPowerAmountChanged` and handed
back at `Tick`).

The unupgraded face was in the same hand and was deliberately **not** played,
so nothing here confounds the two.

### `EB-673` — a Weak-or-Shrink on the player — **PASS**, on a real source

**Which I did, plainly: both.** The Kin Priest is a boss and was not reached.
But fight one of this run opened on a **Shrinker Beetle** whose Strategic
intent is a debuff on the player, so the general case was answered by the
game's own application first, and a hand-set `Weak` second.

Raw `player.status` rows, the dump the row asks for, after the Beetle acted:

```
{"id":"SHRINK_POWER","name":"Shrink","amount":-1,"type":"Debuff",
 "description":"While Shrinker Beetle is alive, you deal 30% less damage
  with every hit you land, a Skill's damage too.","keywords":[]}
```

and after `set_power player weak 2`:

```
{"id":"WEAK_POWER","name":"Weak","amount":2,"type":"Debuff",
 "description":"Attacks deal 25% less damage for 2 turns.","keywords":[]}
```

Both reached the player's printed status line on the same page:

```
- Shrink -1 (debuff) — While Shrinker Beetle is alive, you deal 30% less …
- Weak 2 (debuff) — Attacks deal 25% less damage for 2 turns.
```

**Which filter drops a row, named exactly.** `understudy/qa_packet.py:1417`,
`_powers`. It has exactly one drop:

```python
name = _text(s.get("title")) or label(s.get("name"))
if not name:
    continue
```

A status row is dropped **when and only when the wire gives it neither a
`title` nor a `name`** — there is no type filter, no amount filter and no
allow-list, so a debuff with a printed name cannot be dropped by this function.
Every row read on this build carried a non-empty `name`, which is why nothing
was dropped. The row's suspicion ("skips rows with no printed name?") is the
right reading of the code; what this look adds is that on this build the
condition is not met by an ordinary enemy-applied debuff.

**The r32 Silk shape, now listed.** With `Shrink -1` and `Weak 2` both
standing, Strike printed `Deal 3 damage` against a written 6 — the same "the
number moved and nothing said why" shape r32 reported at 6 → 4, except that
here both causes are on the status line above it.

**Not covered, and it is the half that keeps the row open:** the Kin Priest's
own **Orb of Weakness** specifically. Those are the powers whose wire row may
carry a blank name, and only the boss can produce one.

### `EB-38`, shop half — **NOT DONE**, with the reason narrowed and one new fact

A real shop was reached (act 1 floor 6, walked to with Winged Boots), so this
is no longer 8b's "no shop node was reachable". It is a harder stop.

**What the frames say.** Two frames 0.6 s apart of the shop, by pid. Across the
3841x2160 window 149,985 pixels differ at a >0 threshold — but at a
>8-per-channel threshold the change collapses to ~1,300 pixels in **one
cluster**, x 480–720 by y 240–720. Cropped and brightened 8x, that cluster is a
**lantern flame on the cave wall** left of the shelf. It is not a character.

**There is no character portrait in the shop's viewport at all.** The left
column (cave wall, lantern, a skull), the bottom strip and the right third were
each cropped and read: shelf, prices, relics, wall. The shelf content is taller
than the window — the second card row is cut off at the bottom edge — so the
screen scrolls, and the merchant-side portrait is outside the captured
rectangle. **This harness has no input device and the bridge has no scroll or
camera op**, so the frame the row asks for cannot be taken from here. One
downscaled frame is committed as
`eb38-shop-screen-no-portrait.png` to show what the screen is.

**The new fact, and it is worth the row's while.** The mod's own log proves
the idle attached on this very visit —
`%APPDATA%\SlayTheSpire2\logs\godot.log`, in order:

```
[INFO] [BaseLib] Auto-converted 'res://klee/model/character_sprite.tscn'
       from Sprite2D to NMerchantCharacter
[INFO] [klee] merchant portrait is not a Spine rig; skipping the merchant's
       idle animation (the idle animation, and nothing else). EB-274.
[INFO] [klee] gentle idle attached to the merchant portrait (spine-less
       character; the base cast keeps its own rig). EB-38.
```

So `StaticPortraitIdle.Attach` ran at the shop, found a spine-less portrait and
armed the breath (`klee-mod/KleeCode/Vfx/StaticPortraitIdle.cs`). What is
**not** shown is the pixels, and the row's acceptance is [USER] eyes-on, which
a log line is not. The honest state is: the code path fires at the shop; the
shop half of "all three breathing live" is still owed, and owing it needs a
person at the screen or a driver with an input device, not another bot run.

### `EB-652` — the Salon panel's hover states — **PASS** on the row's acceptance, and a finding under it

The row's acceptance is *"the scenario green live, four frames taken."* Both
halves are now true, and it took two runs because the first one found a defect.

**Run one stopped, and here is exactly where.** With its own setup (not
`--no-setup`), the scenario reached a real combat, granted its four cards, set
energy to 6 and issued all three `play` steps — and then failed its first
`expect`:

```
FAILED expect / power: salon member is 2, expected 3
```

Step 10 of 22, before the first `wait`, so **none** of the four capture windows
was reached. The cause is in the run's own `godot.log`:

```
[STS2 MCP][GItS] give_card: granted KLEEMOD-SALON_DEBUT to Hand   (x3)
[INFO] Player 1 playing card KLEEMOD-PROTO_FS_SALON_DEBUT (no target)
[INFO] Player 1 playing card KLEEMOD-SALON_DEBUT (no target)
[INFO] Player 1 playing card KLEEMOD-SALON_DEBUT (no target)
```

The first of the three plays went to the **Stage arm's** Début, not the shipped
one. Two live cards print the title `Salon Début` on this build —
`klee-mod/KleeCode/Cards/Furina/Generated/SalonDebut.cs` and
`klee-mod/KleeCode/Cards/Prototype/Generated/ProtoFsSalonDebut.cs` — which is
precisely the pair 8b recorded as `EB-739`'s standing caveat, and
`understudy/scenario.py:555` (`find_card`) resolves **an id first and a title
second**. The scenario's `give` steps name the id; its `play` and `hover` steps
named the title. So the scenario was addressing a card by a name two cards
answer to, and got the wrong one. **That is a real defect and it is fixed in
this PR**, as a hygiene fix: the three `play` steps and the `Salon Début`
`hover` step now name `KLEEMOD-SALON_DEBUT`, agreeing with the `give` steps
above them, with the reason written into the file.

**Run two is green.**

```
PASS: 2 expect step(s) held
```

and all four capture windows were framed, by pid, off lane 0:
`eb652-w1-standing-panel.png`, `eb652-w2-hover-companion.png`,
`eb652-w3-hover-deploy-full-stage.png`, `eb652-w4-hover-spotlight.png`. Each
was taken 4 s into its window, triggered off the bridge's own
`debug_state: hover` line in `godot.log`, so each frame is tied to the hover it
claims (`KLEEMOD-CHEVREUSE_INTERDICTION_FIRE`, then `KLEEMOD-SALON_DEBUT`,
then `KLEEMOD-ETHEREAL_SPOTLIGHT`, in the file's order).

**What the frames show, mechanically and only mechanically.** The Salon panel
**does draw** under the `furina-stage` arm: three member chips carrying icons
and numbers (shield 2, sword 4, shield 2) over a bar reading `0`. Above it sit
the Stage's own bar (`0 > Usher 3 > 73`) and the shipped Burst bar (`15/70`) —
the second of which is 8b's `EB-745` caveat 2, unchanged. The panel band
differs between **every** pair of the four frames (20,000–35,000 pixels of a
185,400-pixel band), so something moves on every hover.

**Two things this record will not claim.** (1) The change cannot be attributed
to the hover from these frames, because Furina's own idle animation overlaps
the same band. (2) **No printed word — `FRONT`, `PERFORMS` or `LEAVES` —
appears on any chip in any of the four frames.** That is a claim about the
captured rectangle and not about the panel, because of the limit in the next
paragraph. Whether the four states read is [USER]'s call on the frames, which
is what this row exists to enable.

**A limit in the apparatus, found here and worth its own line.** The card hand
is drawn at the bottom of every combat screen and **is absent from every frame
this job captured**, Klee's and Furina's alike. So `PrintWindow` at 3841x2160
is not reaching the bottom of the game's UI on this machine. The panel's lowest
drawn element (the `0` bar) sits about 40 px above the captured rectangle's
bottom edge, and the footer `EB-652` names — *"the front member's replacement
price, always a row and dim by default"* — would be drawn **below** it, i.e.
outside the frame. So the bright-footer half of the row is framed only if that
footer is above the bar, and this record cannot tell which.

---

## Also asked, cheaply: `EB-742` — an enchant screen and Nimble

**The defect reproduces, and it is worse than the row's scope sentence.**

`force_event SELF_HELP_BOOK` (no gate) arrived as the Mondstadt dressing **The
Guild Desk's Returned Copy** and said so on the way in, which is `EB-767`'s
translation working. Its second option is *"Choose a Skill to Enchant with
Nimble 2."*

**The chooser offered seven cards: four Defends and all three of the named
rows** — `Barbara — Front Row Seat`, `Diona — Shaken, Not Purred`,
`Noelle — I Got Your Back`. Gorou's War Banner, a Skill in the same deck that
gains no Block, was **not** offered, so the detector is discriminating rather
than offering every Skill.

Nimble 2 was taken on Barbara. In the next fight the deck copy's face read:

```
Hexerei. Gain 7 Block. Apply Hydro twice.
Whenever a Bomb goes off this turn, gain 5 Block.
```

against the unenchanted `Gain 5 Block … gain 3 Block`. **Both numbers moved.**
Played from Block 0, it gave exactly **7**.

That is the concrete cost of the declaration the row names —
`klee-mod/KleeCode/Cards/Prototype/Generated/ProtoMcBarbaraFrontRowSeat.cs:68`,
`new BlockVar("PowerAmount", 3m, ValueProp.Move)` — and it is a different
defect from the one the row's scope sentence describes. The scope says the
`BlockVar` is what makes the card *look* like a Block card to the offer
detector; but the same file at line 80 carries a real block op
(`CreatureCmd.GainBlock(... CalculatedBlock ...)`), so the card is a Block card
and the offer would stand anyway. **The live defect is that one Nimble 2 lands
on the rider as well as on the card's own Block** — +2 immediately and +2 again
on every rider trigger. `EB-742`'s next action ("the three declare a plain var")
is the right fix; its acceptance ("GainsBlock false on the three") would be
wrong for Barbara on this evidence, because she genuinely gains Block.

The same read on `Diona — Shaken, Not Purred` and `Noelle — I Got Your Back`
was not taken — one enchant screen offers one enchantment. Their faces carry
the same shape (`Gain 6 Block` plus a rider), so the same question is open on
both and this record does not answer it.

---

## Defects found that are not on any row above

Raised here, not filed — a register row is [USER]'s to mint or Claude's under
the hygiene rule, and this is a record.

1. **The wire's `draw_pile` rows print the UNENCHANTED face.** With the
   Nimble-2 Barbara sitting in the draw pile, `player.draw_pile` printed
   `Hexerei. Gain 5 Block … gain 3 Block`; the same card, drawn into hand one
   turn later, printed `Gain 7 Block … gain 5 Block`. A page or a pilot reading
   the draw pile is reading a face the run no longer has. The draw-pile rows
   are also thin — `name`, `cost`, `star_cost`, `description` and nothing else
   — where a hand row carries `id`, `upgraded` and `keywords`.
2. **A scenario step addressed a card by a title two live cards answer to**,
   and got the wrong one. Named in full under `EB-652` above; fixed in this PR
   for the one file that hit it. The general shape is open: any scenario or
   turn file naming `Salon Début` by title has the same ambiguity while both
   ids ship, which is `EB-739`'s caveat with a concrete failure behind it now.
3. **`PrintWindow` is not capturing the bottom of the game window** on this
   machine — the card hand is missing from every frame taken in this job, on
   two different characters and three different screens. `understudy/frames.py`
   already warns that existence and dimensions are not verification; this is a
   second case of that. It bounds what any frame-based row can be answered
   with, `EB-652`'s footer and `EB-38`'s portrait included.
4. **The owner's progress save carries a retired card id and the game warns at
   every boot.** Twice in each launch's `godot.log`:
   `Progress parse: ValidationError { … Unknown card ID:
   CARD.KLEEMOD-PROTO_FR_SALON_DEBUT_NAMED, IsFatal = False }` and the same for
   `DiscoveredCards`. That is the reframe arm's id, which `EB-726` took out of
   the tree on 2026-09-16; the profile still references it. Not fatal, and
   nothing here touched the save.

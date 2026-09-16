Status: RECORD (deploy live looks; feasibility only, nothing measured)

# Live looks 8b — the deploy looks owed by the built-and-pinned rows

**Build:** installed `0.2.3480+proto.dirty`, read off
`mods\klee\manifest.json`, arms `klee,companion,kokomi,furina-stage,teyvat`,
BaseLib 3.4.7, game v0.111.0. **Lane 0 only**, the owner's profile. Another
agent held lane 1 throughout; nothing here touched it.

**Runs.** Three embarks on lane 0, each torn down after:
`SPW3BMYJ00WW` (Klee, A0), `0BK2QK5BVK3W` (Kokomi, A3),
`R9RDN1FJJ5YZ` (Furina, A2).

**Frames:** `review/qa/live-looks-8b-2026-09-16/` (8 frames + a manifest +
a README naming each one).

---

## The honesty preamble, and it is the whole frame of this document

**Every board in here was written by hand.** The cards were granted through
`give_card`, the powers and the HP through `debug_state`, the energy set to 9
so a turn could hold the whole check. `bridge.GRANT_GUARDRAIL` says what that
means and it is the governing sentence here: *nothing measured on such a board
is comparable to any soak, any run, or any other board* — not to another row in
this table, not to itself on another turn, and not to anything anybody has
measured before.

So this record contains **no numbers that compare anything**. What it contains
is, per row, the one screen or the one number that row's acceptance sentence
names, and a verdict on whether the sentence is now true in the running game.
A PASS means "the sentence the row owed is true on this build, on a board built
to ask it" — never that the card is good, balanced, legible or fun. A FAIL
means the sentence is not true and names the file I suspect; **no code was
fixed in this job**, by rule.

Three further limits, stated rather than left to be noticed:

1. **Several rows were not reachable at all** on a hand-built board, because
   the thing they need is a relic, a potion or a screen that only a run can
   hand you. Those are NOT DONE with the reason, never "probably fine".
2. **A frame proves a pixel, not a judgement.** Where I claim something about a
   frame it is a mechanical claim (this region changed; this badge is uniform
   grey; this sentence is present) and nothing else.
3. **`n = 1` everywhere.** One offer screen, one act sequence, one carry-out.
   A row whose acceptance is a tendency is not answered by this record.

---

## Boots, stalls and crashes

Three game boots on lane 0, **no crash and no stall**. `godot.log` carried no
unhandled exception from the game itself on any of the three. Two engine-log
findings that are not crashes but are defects, both new:

- **`kurage memory: no local seat in this combat (InvalidOperationException:
  Local player not found in combat.); drawing nothing.`** — seven times in the
  Klee run and at **every combat start** in the Kokomi run, logged *before*
  `Creating NCombatRoom`. `klee-mod/KleeCode/Vfx/Prototype/KurageMemoryCard.cs:266`.
  This is why `player.kurage_memory` read `{}` on every page (see `EB-247`).
- **`[STS2 MCP] HandleGetState: System.ArgumentOutOfRangeException ... at
  EventSynchronizer.GetEventForPlayer ... at McpMod.BuildEventState`** — twice
  on the Furina run, on the Event Room path. Vendored
  (`vendor/STS2_MCP/`), so a request upstream rather than a local edit.

A `-stall1` godot log at 11:22:42 in `understudy/logs/godot/` belongs to lane
1's process, not to this job.

---

## The table

One line per row: verdict, the evidence, and for a FAIL the file I suspect.

### Klee arm

| row | verdict | evidence |
|---|---|---|
| `EB-733` | **PASS** | Pocket Match into a Hydro aura over a Bomb 5 printed `*Reaction preview: Vaporize* — The Set off takes the Hydro aura first, so the 1.5x is the Bomb's. This card's own 5 lands 5.` Played: the body went 22 → 10, i.e. 7 (the Vaporized Bomb) + 5 (the card's own). The preview named the number that landed. |
| `EB-722` | **PASS** | The buff strip read `Witches' Circle: Bomb 3 (buff) — Whenever you play a Hexerei card, place a Bomb 3 on a random enemy.` The number is prefixed by what it counts. |
| `EB-721` | **PASS** | Under a standing aura the header says why it differs: `Bomb 7, with Vaporize (buff) — Set off here deals 7 Pyro damage with Vaporize. Bomb sizes here, oldest first: 5`; and against a Vulnerable body `Bomb 19 ... deals 19 Pyro damage after Vulnerable, in 2 hits ... sizes, oldest first: 8 / 5`. |
| `EB-710` | **PASS** (the timing half) | A Vaporize that fired during the ENEMY's turn reached the next page under its own header: `Nothing has reacted yet this turn. These landed after you ended your last turn: — **Vaporize** on **Leaf Slime (M)**, off Klee. *(since you ended your last turn)*`. An Overloaded off a **played** Set off was also named on the next page. **Not covered:** the Electro-Charged-off-Shinobu's-Ring case specifically — the relic never dropped. |
| `EB-754` | **PASS** | `Baron Bunny 1 (buff) — The next time an enemy attacks you, take 3 less damage and deal 8 Pyro damage to ALL enemies.` A number, no `{Damage}`. |
| `EB-610` | **FAIL** | The **wire** carries it: `player.spark_sources = [{"source":"relic:pounding_surprise/explosion","amount":1,"card":"Pocket Match"},{"source":"companion:personal/play","amount":2,"card":"Barbara — Front Row Seat"}]`, and `blindplay.observation()` folds it correctly to `[{"name":"an explosion","amount":1},{"name":"Barbara — Front Row Seat","amount":2}]`. **The page never prints it.** Suspect `understudy/blindplay_render.py:1586` — the `if name == "Spark" and c.get("spark_sources")` sub-line is emitted only inside the METERS loop, and on this build Spark comes over the wire power-shaped, so it renders as a `Spark 3 (buff)` status row and `combat["meters"]` is `null`. |
| `EB-752` | **NOT DONE** | The Boot never dropped and the bridge has no relic-grant op (`debug_state` ops are `set_resource / set_energy / set_hp / set_block / set_power / clear_hand / hover / unhover / force_next_event / skip_act`). |
| `EB-470` | **PASS** | After Lisa — Lightning Rose, the round-2 page (the player's own turn) showed `Vulnerable 1 (debuff)` on the enemy. |
| `EB-399` | **PASS** | Same read — the stack was on the body at the next observe, not only inside the tick. |
| `EB-389` | **PASS** | Under `Lightning Fang 2 (buff) — Your Attacks apply Electro INSTEAD of the element they print`, Pocket Match's face read `[Electro] ... Deal 8 damage` with `Written: ... Deal 5 damage` beneath it and a `*Element overridden*` clause. The applied element is readable off the face. |
| `EB-337` | **PASS** | `Blazing Barrier 6 (buff) — 6 Block left` at Block 17; setting Block to 2 moved the line to `Blazing Barrier 2 (buff) — 2 Block left`. The mark reads `min(Amount, Block)` live. |
| `EB-338` | **PASS** | Barbara — Let the Show Begin♪ (Gain 6 Block, Apply Hydro — no hit) printed `*Reaction preview: Electro-Charged* — Hydro meets Electro: the reacted enemy gains 4 Poison...` plus `*Applies Hydro* — ... Another aura: consumed, and an Elemental Reaction triggers.` The consumption is named and no multiplier is claimed for a card with no hit. |
| `EB-339` | **PASS** | Every Spark-priced face carries `Its 1 Spark is a price, not an Energy cost: an effect that makes a card free to play, or cuts its cost to 0, covers Energy only, and the 1 Spark is still spent.` The sentence is unconditional, so the 0-Energy case is covered by construction; the Vexing Puzzlebox board itself was not reachable. |
| `EB-336` | **PASS** | Player 62/62, Block 0, no Block source in play; one enemy at 2 HP wearing `Mine 3`, intent Attack 12. Ended the turn: the Mine killed it and the 12 never landed — **HP 62/62 after**. |
| `EB-287` | **FAIL** (partial) | Merging IS stated on the ENEMY BADGE: `Bomb 9 (buff) — Set off here deals 9 Pyro damage, in 2 hits ... Bomb sizes here, oldest first: 5 / 4, including 1 Mine`. But the **Bomb keyword tip** the row names carries no merging clause at all: `A charge on an enemy: grows 4 a turn, and goes off when Set off or as a Mine. Block stops it. Only Vulnerable and the HP cap move it. If the enemy dies with it on, it moves to a survivor.` Suspect `klee-mod/KleeCode/Cards/Prototype/ArmKeywordTips.cs:248-265` (`ForBomb`) — the "a second Bomb joins the first" sentence the row records as built is not in the string. |
| `EB-395` | **PASS** | Jumpy Dumpty (Bomb 8, Mine-3-on-ALL rider) + Pop! (Bomb 5) on one body merged to `Bomb 13 ... sizes, oldest first: 8 / 5 ... and dropping Mine 3 on ALL enemies when they go off`. Ka-pow! set it off (43 → 26 = 13 + 4) and the badge afterwards read `Mine 3 (buff) ... including 1 Mine`. The rider paid on the stack. |
| `EB-394` | **PASS** | `Careful Now — Retain. Gain Block equal to your largest Bomb when played, up to 10.` |
| `EB-361` | **PASS** | Tip half: every Bomb badge and keyword ends `If the enemy dies with it on, it moves to a survivor.` Live half: body A (Bomb 5 + Mine 4) died to its own Mine, and body B — which had none of A's charges — read `Bomb 9 (buff) ... sizes, oldest first: 9` the next morning (A's 5, grown 4 at turn start). |
| `EB-445` | **recorded** (page half stands, C# half still owed) | Cost slot: `Stoke the Fuse — cost all your Sparks (1 to play), skill`; body `Spend all your remaining Sparks. Your largest Bomb grows by 3 per Spark spent.` The page says *all*. The in-game badge was not read separately. |
| `EB-605` | **recorded** (page half PASS, C# badge clause still owed) | See `EB-721`'s two badge strings — the headline names Vulnerable and the reaction where it disagrees with the sizes list. |

### Kokomi arm

| row | verdict | evidence |
|---|---|---|
| `EB-699` | **PASS** | `Tengu Stormcall 1 (buff) — Next turn, your Attacks deal 5 additional damage.` One name per thing. |
| `EB-698` | **PASS** | Turn one: `Soumetsu 2 (buff) — At the end of your turn, deal 8 Cryo damage to ALL enemies. 2 turns left; on the last, 16 more.` Turn two, before the big number lands: `Soumetsu 1 (buff) — ... 1 turn left; on the last, 16 more.` |
| `EB-697` | **PASS** | A played Slack Water: the reaction row read `**Electro-Charged** on **Seapunk**, off Slack Water` — the card, not the pet — and the relic answer was named separately (below). |
| `EB-696` | **PASS** | Under Shrink 1 and Vigor 8, Heizou printed `Deal 9 damage`, exactly as Slack Water (attack, base 4) printed 8 and Feint (attack, base 5) printed 9 — one folding convention on one screen. Face also carries the ordering clause: `Counts 4 for each Swirl made before it this turn.` A Swirl fired and was named on the page. |
| `EB-687` | **PASS** | `Opening Gambit — Deal 5 damage. Plan: Apply 1 Vulnerable to ALL enemies. Doubles the damage of the next Plan carried out with this one.` The condition (damage) is on the card. |
| `EB-686` | **PASS** | With exactly one card in the draw pile, no selection screen opened and the player said it: **frame** `eb686-auto-take-bubble.png` — *"Only one card left to look at: Slack Water taken."* The line is a speech bubble (`ScryTake.Announce`), so it is on the screen and NOT on the wire or the blind page — the acceptance is met in the game. |
| `EB-659` | **PASS** | Under Frail 2 the face read `Coral Bulwark — Gain 4 Block. Plan: Gain 6 Block and apply 1 Weak.` The carry-out next morning: `Bake-Kurage: Coral Bulwark, 6 — the 6 is Block; the clause asked for 8.` Printed 6, delivered 6. |
| `EB-660` | **PASS** | `Feint — ... Plan: Deal 10 damage.` |
| `EB-695` | **PASS** | A played Slack Water produced its own page section: `## What your relics answered with — **Tamakushi Casket** 3 on **Seapunk**.` (twice on that play). No relic hit went unnamed. |
| `EB-773` | **PASS** | Queue holding `Coral Bulwark`, `Feint` (10, front), then a third Feint written while the front body held 3 HP. The page: `3. **Feint** — target may be dead by then: **Seapunk** has 3 HP, and the 10 already queued ahead of this one covers it`. |
| `EB-522` | **PASS** | `Well Laid` printed `Deal 2 damage` with the rule beside it (`2, plus 3 for each Plan the Bake-Kurage carried out at the start of this turn; it carried out 0`) and dealt 2 (11 → 9). On a Vulnerable-2 body under Vigor the same card printed 12 and `Riptide+` printed 15 against a written 12 — the folded number is live, and the page prints its own caveat about a standing damage buff. |
| `EB-247` | **NOT DONE** — and a defect found | `player.kurage_memory` was `{}` on every page of every fight, and the Charge meter reports `max: 0`. `godot.log` says why, at every combat start: `kurage memory: no local seat in this combat (InvalidOperationException: Local player not found in combat.); drawing nothing.` — `klee-mod/KleeCode/Vfx/Prototype/KurageMemoryCard.cs:266`, logged before `Creating NCombatRoom`. There is no memory surface on a proto-armed Kokomi run to read the printed text against `pulse_kind`. |
| `EB-248` | **NOT DONE** | Same cause. No entry ever enrolled, so no price string was printed to derive. |
| `EB-334` | **FAIL** — and it is a rule conflict, not a display bug | Feint's Plan clause printed `Plan: Deal 10 damage`; the carry-out next morning, against a body wearing `Vulnerable 2`, was `Bake-Kurage: Feint, 15 — the 15 is damage; the clause asked for 10` and 15 HP left the body. The printed Plan line and the morning's number are **not** equal under Vulnerable. This is deliberate: `klee-mod/KleeCode/Powers/Prototype/KokomiPlan.cs:3033-3038` (`PlanDamageVar`) says in as many words that **`EB-599` removed the target fold** — "Nothing of the TARGET's is folded here any more: the Plan lands next morning, against whatever that body wears then". So `EB-334`'s acceptance sentence and `EB-599`'s decision contradict each other and one of them has to give; that is a call, not a fix. |
| `EB-335` | **PASS** (the printing half) | `Tide Wall+ — Gain 4 Block. Plan: Gain 4 Block for each Plan carried out with it.` and `Shell Guard+ — Gain 5 Block. Until your next turn, whenever the Tamakushi Casket strikes, gain 4 Block.` Both print, both fold Frail on the immediate half. Blocking a real act-2 turn with them was not reached. |
| `EB-316` | **PASS** | `Bake-Kurage: Coral Bulwark, 6 ... **Inside the same beat: Tamakushi Casket 3 on Seapunk.**`, and the wire's `kokomi_plans.carried_out[0].riders = [{"source":"Tamakushi Casket","amount":3,"target":"Seapunk"}]`. |
| `EB-317` | **PASS** | The page: `The Bake-Kurage carried these out at the start of this turn, front first: - Bake-Kurage: Coral Bulwark, 6 ... - Bake-Kurage: Feint, 15 ... - Bake-Kurage: Feint, 15`, with the HP each body lost under each. The same strings ride `kokomi_plans.carried_out[*].line`. |
| `EB-670` | **FAIL** (mitigated) | Scenario run: War Council written as a Plan, ended the turn, carry-out drew nothing (`Bake-Kurage: War Council, 5`), then Feint read **before any play**: `Deal 5 damage. If a Plan was carried out this turn, deal 10 damage instead.` The headline is 5 on a morning where a Plan HAD carried out; the hit then killed an 8-HP body, so it was the 10. **Mitigation, and it matters:** the face now prints the condition AND the alternative number, so a reader is not misled the way the r26 seat was. The headline is still not refreshed. Suspect the conditional's preview var on `klee-mod/KleeCode/Cards/Prototype/Generated/ProtoKkFeint.cs` — the condition is not evaluated at preview time. |
| `EB-684` | **NOT DONE** | No Flex Potion was in the run and there is no potion-grant op. The general question (does a preview read stale Strength) was not asked, because a hand-set Strength has no expiry clock and would answer a different question. |
| `EB-673` | **PASS** (general case) | `Weak 2 (debuff) — Attacks deal 25% less damage for 2 turns.` and `Frail 2 (debuff) — Gain 25% less Block from cards for 2 turns.` both printed on the player's status line the moment they were set. The `qa_packet._powers` name filter no longer drops them. **Not covered:** the Kin Priest's own Orb of Weakness and the r32 Silk case — the boss was not reached, and those are the powers whose printed name may still be blank. |
| `EB-441` | **FAIL** on the row's sentence, **PASS** on preview-truth | Under Vigor 8 and Shrink 1, `Kurage's Oath` — a **skill** — printed `Deal 7 damage to ALL enemies` against `Written: Deal 3`. `(3 + 8) x 0.7 = 7.7`. Played: both bodies lost exactly 7 and the Vigor was consumed. So the face and the hit AGREE, and the display defect the row was filed on is gone; what remains is that a Skill takes Vigor at all, which is the rule the row's acceptance ("a Skill face never folds Vigor") asserts should not happen. That is a design call, not a rendering fix. |
| `EB-360` | **PASS** | Every buff line named its owner card on sight: `Tengu Stormcall 1`, `Soumetsu 2`, `Lightning Rose 3`, `Blazing Barrier 6`, `Baron Bunny 1`, `Witches' Circle: Bomb 3`, `Front Row Seat 3`. |
| `EB-348` | **PASS** | The relic keyword prints the rule: `Tamakushi Casket — Your relic. Each debuff you apply is a 2 Hydro hit on that enemy: it reacts, takes its Vulnerable, and re-arms Hydro.` Live: the strike read **2** on a body with no Vulnerable and **3** on a body wearing Vulnerable 2 — both derivable from that sentence. |

### Furina Stage arm (`-p FurinaStage`)

| row | verdict | evidence |
|---|---|---|
| `EB-735` | **PASS** | `## Your stage` — `Block 0 · after the acts: Block 3 · lead: Usher 3 · Furina 62/78` / `middle: Chevalmarin 1 · back: Crabaletta 1`, with an arrival line per performer and, later, a bow line: `**Crabaletta** took a Bow: 8 to Corpse Slug (1).` |
| `EB-743` | **PASS** | The act lines name effect and seat exactly as the row asks: `**Usher** performed: Furina gains 3 Block.` / `**Chevalmarin** performed: 4 across every enemy, and Hydro on each.` / `**Crabaletta** performed: 5 to Corpse Slug (1).` / `**Usher** left the stage: emptied by a hit, so no Bow.` / `**Crabaletta** left the stage: emptied by a Spend, so it takes a Bow.` |
| `EB-744` | **PASS** | The arm's glossary on an arm page is Fanfare / Lead performer / Back performer / Bow / Spend / Raise. **No Encore row.** Each performer's act is printed on the Bow row: `Usher: 4 Block. Chevalmarin: Hydro on all. Crabaletta: 8 damage.` The reward screen's Companion row carries the Stage's sentence, not the Salon's: *"On Furina's stage playing one performs the front member, then sends it to the back; an empty stage performs nobody."* |
| `EB-745` | **PASS**, with two caveats worth reading | No Fanfare buff and no Encore power appeared in any status list across the run. The wire's `player.resources` still **lists** `KLEEMOD_FANFARE` and `KLEEMOD_ENCORE` at `0` — registered meters that are never granted, which I read as meeting the row rather than breaking it. **Caveat 1:** a hand-granted shipped `Salon Début` DOES still grant `Salon Member 3 (buff)` under the arm, with the full shipped Encore glossary on it — the arm's guard is the offer filter (`EB-736`), not the grant site. **Caveat 2:** the in-game HUD still draws the shipped Burst bar (`0/70`, later `15/70`) above Furina under the arm, on a board with no shipped card played — see `eb65-power-badges-and-nope-relic.png` and `eb652-salon-panel-standing.png`. |
| `EB-746` | **PASS** | `Curtain Rise — Choose one: Deal 7 damage \| Spend 3: deal 13 instead.` with `*Spend* — Chosen on play, never automatic.` Both taken from one board: the first play resolved the plain mode; the second opened the chooser (`# Choose a card.` listing both) and the Spend mode was chosen and confirmed, over-spending a bar of 2 and paying the Bow. |
| `EB-747` | **PASS** | On an empty stage, before any play: `Ousia Surge — Deal 0 damage, the lead performer's Fanfare.` Played it: the body stayed at 24/38. `Pneuma Refrain — Gain 0 Block, the back performer's Fanfare.` |
| `EB-737` | **PASS** — exactly the acceptance | Under Weak 2: `Curtain Rise — Choose one: Deal 5 damage \| Spend 3: deal 9 instead.` (from 7/13). `Tidal Flourish` 3/6 (from 5/9). Under Frail 2: `Interposition — Choose one: Gain 3 Block \| Spend 2: gain 7 instead.` (from 5/10). Both branches of every conditional fold. |
| `EB-738` | **PASS** | Both Corpse Slugs read `27` and `26` immediately before and immediately after summoning Chevalmarin and Crabaletta. No enemy number moved on play. |
| `EB-736` | **PASS** at `n = 1` | The one card offer this run reached: `Understudy` (a `proto_fs_` row), `Quick Change` (a retired-free shipped row), `Duet` (a Companion-family row). No Encore, Spotlight or Salon row, and no shipped meter on the header. One screen is one screen. |
| `EB-739` | **PASS**, with a live caveat | The Stage's Refill prints as `Rising Applause — Raise 5 Fanfare on the back performer.` No two faces on the offer screen shared a name. **Caveat:** the shipped `Salon Début` and the Stage's `Salon Début` are both live ids on this build and print the same title (`Salon Début (1)` / `Salon Début (2)` when both are in hand). They are held apart only by `EB-736`'s offer filter; if a shipped Salon row ever reaches an offer, `EB-739`'s defect recurs with that pair. |
| `EB-742` | **NOT DONE** | No enchant screen was reached, and the three cards (`ProtoMcBarbaraFrontRowSeat`, `ProtoMcDionaShakenNotPurred`, `ProtoMcNoelleIGotYourBack`) were not in the run's deck, so there was nothing for an enchant screen to offer Nimble on. |
| `EB-398` | **PASS** | The shipped deploy card's face: `Salon Début — Add 1 random Salon Member to your Salon. **It performs at once.**` |
| `EB-348` | (see the Kokomi table) | The Casket is Kokomi's relic; it was read there. |
| `EB-415` | **NOT DONE** | Gorou — General's War Banner was not tested; the Furina run was torn down before a board could be built for it. It is a two-minute check on the next deploy: play the upgraded banner, read Dexterity, run the clock out, read it again. |
| `EB-65` | **FAIL** | Four of the six are grantable on this build (`Fortissimo Guard`, `Courtroom Drama`, `Quick Change`, `Unheard Confession`); `Stagehands` and `The Gallery Stirs` are **not live card ids** (`give_card` refuses both by name). All four powers landed and printed their text on the page. Their **badges render as flat, uniform grey squares with no icon** — see `eb65-power-badges-blank-crop.png`, taken ~90 s after the powers landed so it is not a fade-in. The four PNGs ARE in the deployed pck (`klee.pck.contract.txt` lists `res://furina/powers/{fortissimo_guard,courtroom_drama,quick_change,unheard_confession}.png`) and the paths are wired at `klee-mod/KleeCode/Powers/KleePowerIcons.cs:293-304`, so the miss is downstream of both. Worth noting while looking: the source PNGs under `ImageGen/images/furina/powers/` are **card-portrait illustrations**, not badge sigils. |
| `EB-652` | **PARTIAL** | `understudy/scenarios/furina-hover-states.yaml` **would not run** on the attach path: `scenario run --no-setup` against a game already standing in a combat answered `NOT RUN: no combat screen was ever reached` — the runner's driver expects to reach the fight itself. So the four frames the row asks for were not taken. What I did instead, by hand: three shipped `Salon Début`s under the Stage arm, and the shipped Salon panel **does still draw** (three member chips under Furina, `eb652-salon-panel-standing.png`). A `hover` on a Companion through the bridge changed **151,603 pixels** between the two frames, so the hover path is alive under the arm. Two frames, not four, and no reading taken on either. |

### Any arm

| row | verdict | evidence |
|---|---|---|
| `EB-161` | **NOT DONE** | The Mods row is on the main menu's Mods screen. Nothing in this harness can click a main-menu button — `blindplay` drives run screens only and there is no menu verb. It needs a person, or a driver that does not exist. |
| `EB-38` | **PASS** (rest site) / **NOT DONE** (shop) | Two frames of the rest site 0.6 s apart. Across the whole 3842x2160 window **16,230 pixels differ, and every one of them is inside the portrait's bounding box** — nothing else on the screen moved. That is a mechanical statement that the spine-less portrait is animating at the rest site; whether it reads as breathing is [USER]'s. No shop node was reachable before the run ended, so the shop half is still owed. |
| `EB-220` | **PASS** | `eb220-meter-cost-badges.png`: Pocket Match carries a pink Spark badge reading `1` beside its red `0` energy badge, and the Spark meter draws beside the energy gem at the bottom left. Every priced card in the hand shows its meter and its price at combat size. |
| `EB-300` | **NOT DONE** | Requires driving a controller. This harness posts to a bridge; it has no input device. |
| `EB-296` | **NOT DONE** | Requires a mouse drop onto the pet. Same reason. |
| `EB-116` | **NOT DONE** | Pael's Eye never fell. The row's own gate says it costs a run and a relic roll. |

---

## Defects found that are not on any row above

Raised here, not filed — a register row is [USER]'s to mint or Claude's under
the hygiene rule, and this is a record.

1. **Raw rich-text markup reaches the blind page's stage section.** The page
   printed `joined the stage at 3 [gold]Fanfare[/gold]`,
   `Furina gains 3 [gold]Block[/gold]`, `[gold]Hydro[/gold] on each`,
   `took a [gold]Bow[/gold]` and `A [gold]Spend[/gold] rider cannot fire at
   all`. `EB-246`'s rule is that the game's markup is folded out of every
   printed name and body; these are **literals written by the renderer**, so
   the fold never gets a chance. `understudy/blindplay_render.py:1415-1428`,
   plus whatever `STAGE_ACT_EFFECTS` / `STAGE_BOW_EFFECTS` inline.
2. **The bridge's mode labels carry markup the page has already stripped.**
   Playing `Curtain Rise` with `mode: "Spend 3: deal 13 instead"` — the text
   the page prints — was refused: *"has no mode matching ... Modes: 'Deal 7
   damage' | '[gold]Spend[/gold] 3: deal 13 instead'"*. A caller that names a
   mode off the page cannot match the bridge's list. (`blindplay`'s own
   `choose` path goes through the chooser screen and is unaffected.)
3. **The `Salon Solitaire` relic renders the `NOPE` placeholder** in the relic
   row — visible top-left in `eb652-salon-panel-standing.png` and
   `eb65-power-badges-and-nope-relic.png`. It is the Stage arm's own new
   relic and its icon has no file behind it.
4. **`Final Bow` printed `Gain 2 Block, its Fanfare` on an EMPTY stage**, where
   there is no lead performer to take a Bow. `Ousia Surge` and `Pneuma Refrain`
   both correctly printed `0` on the same board, so this reader is out of step
   with its two neighbours.
5. **`Ka-pow!` under Lightning Fang prints both elements.** The title reads
   `[Electro]`, an `*Element overridden*` clause explains it, and then an
   `*Applies Pyro*` keyword row still follows underneath.
6. The two engine-log findings in the Boots section
   (`KurageMemoryCard.cs:266`, and the vendored bridge's
   `BuildEventState` / `EventSynchronizer.GetEventForPlayer` out-of-range).

---

## What could not be done, and why

- **Anything needing a relic or potion this harness cannot grant:** `EB-752`
  (The Boot), `EB-684` (Flex Potion), `EB-116` (Pael's Eye). `debug_state` has
  no relic or potion op, and hand-forcing one would be a different question
  anyway.
- **Anything needing an input device:** `EB-300` (controller), `EB-296` (mouse
  drop), `EB-161` (the main-menu Mods row).
- **Anything needing a screen the runs did not reach:** `EB-742` (an enchant
  screen), `EB-38`'s shop half, `EB-673`'s Kin Priest, `EB-335`'s act-2 turn,
  `EB-415` (out of run time).
- **`EB-247` / `EB-248`** are blocked by a live defect rather than by
  reachability, and that defect is named above.
- **`EB-652`** is blocked by the scenario runner's attach path, also named
  above.

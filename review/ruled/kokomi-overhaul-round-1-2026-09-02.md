Status: RULED R237 2026-09-02

# Kokomi overhaul, round one: what the seats found

Ruled R237 by [USER]'s own run of 2026-09-02, whose words are in that commit's message: pick 1 took option 2, the Tide re-priced on the seats' arithmetic (Oath to +8, and a second Rising Tide in the starter; draft 3 in the slice document); pick 2 took option 1, the Inazuma companions, now built, are the second element.

Written 2026-09-02, the night her prototype first ran. Prototype stage, so
nothing here is a measurement (R217 G): the seats' words are feedback for
iteration, the defect rows are the deliverable, and your act-one run is the
gate (`review/active/kokomi-overhaul-slice-1-2026-09-01.md` §6).

## 1. What ran

- Build `0.2.1921+proto.dirty` with three arms on: the Klee overhaul with
  its round-one fixes, the Mondstadt companion prototype, and Kokomi's slice
  one (PR #252, all 33 rows, merged as plumbing). Validation green; the soak
  as Kokomi read `fights=3 defects=0`.
- Two seats played act-one runs blind. Codex (gpt-5.6-sol, seed
  `AU4C7763TAW5`, 80 actions, two long fights closed and a third under way
  at the budget; `review/qa/blindplay/kokomi-overhaul-r1-codex/`, with the
  per-turn wire in `wire.json`). The Opus seat (the author's own family, so
  not an independent read; seed `UNT2Z7S6TXQM`, 112 actions, three fights
  won, then killed on floor 7 by the Two-Tailed Rat summoner;
  `kokomi-overhaul-r1-opus/`). No crash, no soft-lock, no stalled screen in
  nine fights counting the soak. The Qwen seat is staged turns only and did
  not run.
- One reading the build took that changed the paper: a Plan resolves after
  the draw, not before it, because the engine has no seam between the
  energy reset and the draw; the slice document now says so.

## 2. What the testers said, against your four questions

Subjective. The questions are yours to answer, not theirs.

1. **Hold or surge.** Both found the bet and both priced it against itself.
   Codex: Kurage's Oath and Rising Tide "became mostly dead after the first
   combo because their combined benefit was too small relative to Exert,
   lost healing, and defensive needs"; it surged on enemy buff turns and
   otherwise held. Opus did the arithmetic out loud: "Kurage's Oath is 1
   energy + 2 HP for 5 stored damage, and Water's Edge is 1 energy for 6
   immediate damage. The signature mechanic is worse than the basic attack
   unless you are stacking two or more builders into one outlet on a turn
   nobody is hitting you." It felt the tension "every turn" and said "every
   time I did the arithmetic honestly the boring line won." The one turn it
   landed three builders and an outlet together, off an Energy Potion, "felt
   genuinely great."
2. **Exert.** Real, and the reason the bet loses: "Tide costs HP or tempo now
   for damage later, and later may not come." Codex called Oath dead for the
   same reason. Neither ignored it as a tax; both avoided it.
3. **The pulse as a heal button.** The two runs disagree, and the disagreement
   is the watch item you named. Codex, playing Coral Guards first, left its
   two hallway fights at 63 and 62 of 80 after entering at 64: fully healed,
   every time, which is exactly the thing to watch. Opus, playing forward,
   left fights at 48, 35 and 25 and died; the pulse's 8 per fight did not
   keep up with damage taken on purpose. Both found the pulse hard to read:
   Codex "Mend timing remained confusing", Opus took the Casket's "Mends you
   2" as broken at full HP because the never-above-entry bound is printed
   nowhere. The pulse budget itself is not on the wire yet, so "fights ending
   with budget unspent" cannot be counted from these runs (EB-273).
4. **Never wanted to play.** Codex: Oath, Rising Tide until the Tide was
   there, and Breaker at 2 energy. Opus: Reading the Tide (a blank below 5
   Tide), Undertow (a blank at 0), and "the Hydro aura, which did nothing at
   all across four fights", because her own pool holds no second element.
   That last is slice one by design; the Commander loop's companions are the
   second element, and Opus's one Sayu card was the only reaction it saw.

Two more reads worth your eye. Opus on the deck's shape: four builders to
three outlets in a sixteen-card deck meant "twice I banked 15+ and had
nothing to spend it with; twice I drew Undertow at Tide 0 and held a blank",
and it would draft "outlets before builders" next time. Both on repetition:
by the fourth fight turns reduced to Coral Guard, Water's Edge, end turn;
enemy Empower turns were the interesting ones because those are when the
bank is right. The Ironclad comparison the gate asks for was not run tonight.

## 3. Defects, filed

Rows EB-272 to EB-278 in `docs/current/BACKLOG.md`, with four older rows
widened. The ones that lie to a player: no arm keyword prints a definition,
so Exert, Tide, Surge and Mend are learned by watching numbers move
(EB-272); a Strength gain silently becomes Tide, so Fysh Oil printed
Strength and granted none (EB-276); an upgraded prototype card is identical
to its base, so the Light Door did nothing visible (EB-277); Reading the
Tide and Undertow are playable blanks at low Tide (EB-278). Instruments:
her Tide and pulse budget are not on the wire (EB-273). From the game log
while the Opus seat played: the shop's merchant character throws a swallowed
exception on entry (EB-274) and every new prototype card logs a missing
sprite because no art is staged (EB-275); neither is a crash. Widened:
self-targeted potions cannot be used through the render, now Skill Potion
too (EB-269); enemies are renumbered when one dies (EB-271); sold-out shop
slots lose their names and shop cards print no cost (EB-268). None blocks
your run; EB-272 and EB-276 are the two to read around.

## 4. What is installed right now

The three-arm dev build, `0.2.1921+proto.dirty`, on purpose, so your run
needs no deploy; Klee's round-one fixes are in it. To put the release build
back at any time: `klee-mod\build\deploy.ps1`. Do not hand it to a co-op
partner.

## 5. Picks

1. **The Tide's price.** Both seats say one Oath into one Surge loses to two
   basic attacks, and the bank only pays when two builders and an outlet
   land on a quiet turn. (1) *Leave the numbers; your run and question 1
   decide, as the gate says* [default]. (2) Re-price before your run, on the
   seats' arithmetic: Oath to Tide +7 so one builder into one outlet at
   least matches two Water's Edges, with the HP still paid.
2. **A second element in her own pool.** The Hydro aura reacts with nothing
   she owns, so the React half of her fights arrives only through drafted
   companions. (1) *Leave it; the Inazuma companions now being built are the
   designed answer, and the Commander loop is the watch item you named*
   [default]. (2) Give one slice-one Kokomi card an off-element line now.

Then: one act-one run, three or four fights including an elite, and the four
answers from §6 of the slice document, a sentence each.

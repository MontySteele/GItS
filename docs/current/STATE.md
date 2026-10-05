# STATE

What ships and what is next, rewritten 2026-09-23 after the design and
process review (R276, the last R number; `review/ruled/*-review-2026-09-23.md`).
Open picks for [USER] are in [`QUEUE.md`](QUEUE.md), engineering to-dos in
[`BACKLOG.md`](BACKLOG.md), rules in [`LAW.md`](LAW.md). The older narrative is
frozen in [`workstreams.md`](workstreams.md).

## Mod build environment (pinned)

Slay the Spire 2 **v0.111.0** (`41cef1ea`, buildid `24724944`, branch
`public-beta`), MegaDot v4.5.1, BaseLib **3.4.7.0**, .NET SDK 9.0.316, PCK
contract `roster-pck-v3`, package `klee` **v0.2**, deploy stamp
**`MAJOR.AUTO`**. **Installed: `0.2.4218`** (2026-10-02, main after legacy cleanup stage 6).

**The current kits are the release build** (2026-09-28). [USER]: "The current
character builds are much more progressed than the old prototypes were, even
though it's still a work in progress. Let's go ahead and make all 3 current
builds the active release builds to avoid this confusion."
Every build carries them, unmarked: a plain `dotnet build`,
`klee-mod\build\deploy.ps1`, and the `-Package` handoff zip. **The
round's build is `tools/deploy_round.py`** (`deploy.ps1`, then the bridge).
The old shipped kits are gone from both engines (legacy cleanup stages 5
and 6, `review/active/legacy-cleanup-2026-10-01.md`): their C#, their sheets
(`docs/*-cards.yaml`, `*-upgrades.yaml`, the companion sheets), the arm
switches in C# and in the sim, and the engine pieces only their cards used.
There is one C# test configuration, and the tier0 sim always runs the current
kits; its calibration bands, measured on the shipped kits, are retired until a
kit reaches Balance (pick 5). Every card is a `proto_` row on
`docs/prototype-surface.yaml` (`operations/prototype.md`). **`+proto` now
marks only a build that differs from the release**: `deploy_proto.ps1
-TeyvatFrame`, and the Teyvat frame is on hold (below). Each C# pool IS its
prototype roster (legacy cleanup stage 4): the `proto_` rows are every pool's
`GenerateAllCards`, the roster is the offer, and the 78 / Ancient / co-op
counts are pinned (`KleeTests/Prototype/PoolCountTests.cs`); the companion
roster is prototype rows only, Fontaine's sixteen ported as they are (pick 4,
`proto_mf_`).
**Last release package: `0.2.1357`**
(2026-08-29), which predates the ruling and carries the old kits.

## Roster

| id | display | HP | nation | element | stage | draftable pool |
|---|---|---|---|---|---|---|
| `klee` | Klee | 70 | Mondstadt | Pyro | Prototype (at the finish line) | 78 |
| `kokomi` | Sangonomiya Kokomi | 80 | Inazuma | Hydro | Prototype | 78 |
| `furina` | Furina | 78 | Fontaine | Hydro | Prototype (the Salon's Tab built; awaiting [USER]'s play) | 24 |
| `varka` | Varka | 80 | Mondstadt | Anemo | Prototype (combo pass built) | 78 |

**Every kit's pool target is 78 standard draftable cards**, plus its Ancient
rewards and multiplayer cards; a smaller pool reads more reliable than it will
be. Starter basics are never changed without [USER]'s pick; every kit's
starter is the base Strike x4 and Defend x4 plus two cards of its own ([USER],
2026-09-28: "The characters' kits should all use basic Strike and Defend.").

## The kits (Paper, then Prototype, then Balance; `operations/stage-gate.md`)

- **Klee: at the finish line.** Brief `review/active/klee-brief-2026-09-01.md`.
  The pool is 78; two seat rounds read it; [USER]'s co-op run (A0, 2026-09-24)
  was "very fun ... the loop basically works"; the whole-pool balance review
  shipped (`review/records/klee-balance-2026-09-25.md`), and idle-vs-short Sparks
  is ruled "watch". Seat rounds in acts 2 and 3 (2026-09-26, Opus seats at
  [USER]'s request): five whole runs, two wins, fixes in #697 and #701;
  `review/records/klee-later-acts-2026-09-26.md`, one pick open (the React
  loop's aura supply). [USER]'s solo verdict run (2026-10-01, died mid act 2
  on a three-elite route, "misplays on my part"): "no bad notes here, Klee
  seems to work basically as designed and the core gameplay loop was indeed
  fun and interesting, with a challenge around bomb management"; Sparks
  "only really matter if you're trying to let your bombs cook ... I never
  really felt pressed for them." **The status package (2026-10-01, ruled,
  built):** `review/active/klee-status-package-2026-10-01.md`. Eight cards in
  (Dazed on the fair loaders, Confiscated on the busted ones, and the payoffs
  that read them), eight cut, and Albedo's Klee stand-in is now Dust of
  Purification; the pool stays 78, 24 / 33 / 21. **Its sec.5, defence in the
  status pile (2026-10-01, ruled, built):** Up in Smoke! (Weak to ALL, a
  Dazed), Behind Jean's Desk (14 Block, a Confiscated) and Kitchen Alchemy
  (exhaust a status, ALL enemies lose 2 Strength) in for Fish-Flavored Bait,
  Nova Burst and Spinning Sparkler; still 78, 24 / 33 / 21. Both engines.
  Seat rounds on it (2026-10-02, `review/records/casket-and-klee-defence-round-2026-10-02.md`
  and the overnight forced-deck round, `review/records/klee-forced-defence-round-2026-10-02.md`):
  Kitchen Alchemy was unplayable as written and is now "ALL enemies lose 1
  [2] Strength; exhaust every status in your hand, they lose 1 more for
  each" (#830); after the forced-deck seats, Behind Jean's Desk is 11 [14],
  Up in Smoke! costs 0 and Kitchen Alchemy's upgrade adds Retain (#831).
  The tuned three were read on the same seeds
  (`review/records/klee-tune-and-smoke-round-2026-10-02.md`): Behind Jean's
  Desk settled (strong), Up in Smoke! fair, Kitchen Alchemy dead (played 2
  times in about 26 hands). Klee has won 0 of the 9 seat runs since the
  status package; she loses on Block at the boss turn, and Sparks pile up
  unspent. The final pass is ruled and built in both engines
  (`review/active/klee-final-pass-2026-10-02.md`): HP 70; Cover Your Ears!
  in (0 Energy, 2 Sparks, Exhaust: ALL enemies lose 6 [8] Strength this
  turn), Where Did I Put It? out; Blast Shield Common; pool 78, 24 / 33 /
  21. Its seat round (`review/records/klee-final-pass-round-2026-10-02.md`,
  0.2.4228, same seeds): both runs cleared act 1 for the first time, one
  lost the act-2 boss with it at 11/321; seats now draft defence and spend
  their Sparks in act 2. An Opus check on the same seeds
  (`review/records/klee-opus-check-round-2026-10-02.md`): one run won,
  Klee's first seat win since the status package; the other died in act 2
  short of Block, as the Sonnet runs did. Next, the finish line: [USER] plays one full run on
  this build; fun through act 3 moves Klee to Balance. **The Mondstadt
  companion review (2026-10-03, ruled, built;
  `review/active/mondstadt-companions-2026-10-03.md`):** Stellaris Phantasm,
  Breastplate, Wind Spirit Creation and Fiery Rain retuned; Klee's 13
  Klee-only companions resolved (4 to the shared pool, 6 cut, 3 into her own
  pool for Second Surprise, Solitary Confinement and Once More!). Klee stays
  78, 24 / 33 / 21; the shared Mondstadt roster is 39; no stand-ins remain.
- **Kokomi: Plan stays; the cards change.** Brief
  `review/active/kokomi-brief-2026-09-01.md`. New rule for the brief: the
  now-line answers this turn, the Plan line buys something only a head start
  can buy, never the same effect at two sizes. Next build: rewrite the 13
  same-effect-bigger Plan cards (Kurage's Oath included), re-aim the five
  per-Plan payoffs so at least half reward something other than volume, and
  every damaging card of hers applies Hydro (Skills too; basics unchanged).
  Pool stays 39 for this pass. Then two seats, then [USER] plays (a central
  rule changed). **The Casket pass (2026-09-28, ruled):** the Tamakushi
  Casket counts the Plans the Bake-Kurage carries out and deals Open the
  Casket (1, Retain: Strength equal to the count, then empty it; it was 0
  and Exhaust until 2026-10-01, the four-kit review's Kokomi pick 1);
  its debuff strike is gone. Feint and Sango Isshin pay per carry-out this
  turn, six rows cut, thirteen added: the pool is 46 (plus three co-op).
  Shell Guard, whose strike clause the pass left dead, was re-aimed by the
  main session to "Gain 5 Block, plus 1 for each point in the Casket".
  Record: `docs/notes/prototype-surface-provenance.md`. **The cleanup pass
  (2026-09-29):** both Sonnet runs died to act-2 bosses short of Block, so
  Shell Guard is a Common and Tide Wall's Plan gains a flat 6 under the
  intent; Scout Ahead and Song of Pearls are cut; Feint, Press the Advantage
  and Driftglass hit harder. The pool is 44 (24 / 15 / 5). Brief §6.
  **The feed pass (2026-09-29)**, on [USER]'s act-1 death ("her cards are
  weirdly 'expensive'"; "some Plan cards need to go to 0 cost"): five 0-cost
  Plan-only Commons (Bubble Ward, Nip, Jellyfish Drift, Current Read, Brine
  Sting), eight now-and-Plan Commons moved to Uncommon, Coral Bulwark a plain
  8 Block, Exposed Flank cut. The pool is 48 (20 / 23 / 5). Brief §6. Its
  seat round (`review/records/kokomi-feed-round-2026-09-29.md`): energy is no
  longer the wall, Block still is; one seat reached the act-3 boss.
  **Expansion batch one (2026-09-29, ruled):** [USER] on the feed-pass
  build: "I like it!"; card art redone (#770, no leg crops). Paper
  `review/active/kokomi-expansion-2026-09-29.md`: four decks (Plan volume,
  the Big Plan reading Energy paid, Tide Control, Dusk Guard), 22 cards (12
  Uncommon, 10 Rare), Watatsumi's Grace replaces The Clouds Like Waves
  Rippling; pool to 69. **Batch one is built** in both engines (the
  22 rows, seven Powers, four Plan clauses, the `kokomi` op; readings and
  the upgrades the paper leaves open in the provenance note, "expansion
  batch one"); the pool is 69 (20 / 35 / 14). Its sim (paper §5,
  `tools/kokomi_expansion_sim.py`, n = 400 paired, seed 7, stock priest
  pilot): the stylised act 1 is lost at the first elite by every pilot
  (0 to 0.2% act won), so the deck read is the full-deck gauntlet (every
  act-1 elite and boss and act-2 boss at full HP). After the main
  session's round (Undertide Lance 6 / 12, Grand Design 1 per Energy paid,
  Brace+ cost 0 accepted): Plan volume 57.8% of fights won, Tide Control
  51.5, the default drafter 50.1, Dusk Guard 48.4, Big Plan 47.7 (10.1
  behind); every act-2 boss is lost. With Grand Design granted Big Plan
  still trails volume (47.1 against 56.1). Dusk Guard with Grace and Coral
  Crash never carries 30 Block into the enemy turn (0.1% of turns); 9.8% of
  its gauntlet fights pass turn 15 (others about 1%), on too little damage
  rather than a wall. All Streams Flow to the Sea is now cost 1 [0] and
  regains the Energy paid for the Plans it cancels; still dead in the sim (7
  plays in 252 fights, each multiplying its Plan to about 4 carry-outs --
  the stock pilot rarely has 2 Plans waiting and a Plan card left).
  **The payoff pass (2026-10-01, ruled):** on the co-op complaint ("no
  payoff for playing lots of Plans", "short on block"), Second Thoughts is
  cut ("an undo is a dead draw") and two Uncommons join: Kurage Canopy (Block
  per carry-out) and Coral Tithe (the Casket into Energy and cards). The pool
  is 70 (19 / 37 / 14). Brief §6; provenance note, "Kokomi payoff pass".
  **Pool completion (2026-10-01, ruled at the defaults):** paper
  `review/active/pool-completion-2026-10-01.md` sec.4 and sec.6, built in
  both engines: Tidal Screen (Common), seven Rares (Spring Tide, Kurage
  School, Shoal of Spears, Patient Tide, Sea's Reproach, Tidal Rebuke,
  Watatsumi Resistance), two co-op cards (Tactical Relay, Kurage's Mercy),
  Coral Crash to Common 1 [0]; her second Ancient, Divine Strategy, game-side.
  The pool is 78 (21 / 36 / 21) plus five co-op cards and two Ancients.
  Provenance note, "Pool completion, 2026-10-01"; sec.7's sim checks wait
  (BACKLOG). **The status batch (2026-10-01, ruled):** paper
  `review/active/kokomi-status-batch-2026-10-01.md`, built in both engines.
  Six cards that answer statuses through the hand a Plan sees after the
  draw (Kelp Wall, Tidecleanse, Sea Glass Harvest and its Sea Glass token,
  Turning Tide, Flotsam Surge, Abyssal Salvage) and Riptide Ruin, the Rare
  in the cut Coral Sanctuary's place, a second status source; Rally, Pearl
  Diver, Battle Plan, Feigned Retreat, Moon Signal, Chain of Command and All
  Streams Flow to the Sea cut. The pool is 78 (21 / 36 / 21). A Plan line
  under a now-line prints "Or plan:" ("Or dusk plan:"), the starter's
  included; a Plan-only card keeps "Plan:". The Plan tip opens "Instead of
  the line above".
  Provenance note, "Kokomi status batch, 2026-10-01". Next: [USER] plays.
  **A Plan stays open (2026-10-01, ruled, built):** paper
  `review/active/kokomi-delay-pays-2026-10-01.md`. When the Bake-Kurage
  carries out a Plan from a two-line card, it is its Plan line (default)
  or its now-line at printed size; Plan-only and Dusk Plans are unchanged; no
  number moved. **Pick 5 (a), ruled the same day:** "Plans carry out on their
  Plan line; click a waiting Plan to flip it." No screen: a click on a
  waiting two-line Plan in the Plan strip flips it during her turn (a synced
  game action), and the bridge's verb is `flip <n>`. **The Casket pays more
  than once (four-kit review, Kokomi pick 1):** Open the Casket costs 1 and
  has no Exhaust; What the Tokoyo Returns fetches it from the draw or discard
  pile. [USER]: "if it's repeatable, it should probably cost energy, though,
  to make this a real choice and not just button mashing when it comes up?"
  Provenance notes, "A Plan stays open (Kokomi), 2026-10-01" and "Kokomi:
  the Casket repeats, and the flip, 2026-10-01". Its seat round
  (`review/records/casket-and-klee-defence-round-2026-10-02.md`, fixed seeds
  with an Ironclad control): her first whole-run win, one act further on
  both seeds, still about half the control's damage per turn on the same
  boss; no seat flipped a Plan.
  **The big-Plan pass (2026-10-04, built):** on a friend's solo run (every
  Rare read as weak next to 0-cost Plans under Casket Strength), Strength
  affects Masterstroke's Plan 3 times and Surging Shoal's Plan twice; the
  Casket is unchanged. The expansion sim does not move (Big Plan 44.5
  against volume 54.5; its pilot holds little Strength), so the sim's gap
  has another cause. No seat round yet. Provenance note, "Kokomi big-Plan
  pass, 2026-10-04".
  Next: [USER] plays (a central rule changed; co-op with a friend may stand
  in); the damage gap is a paper after that run.
- **Furina: the Salon's Tab is built (2026-10-05).** The research proposal (`review/active/furina-research-proposal-2026-10-05.md`, sec.2 rules, sec.16 slice and curtain call, sec.17's two edits) replaces the re-founded Stage in place; [USER]: "the current one built overnight can be discarded". Furina pays HP for power: Drain spends HP down to a line at half the HP she entered combat with, Repay returns drained HP, every HP lost or repaid prints 1 Fanfare, and every drained HP returns when combat ends. Three guest seats; four guests. The pool is the starter and 24 cards, not 78. Relics and potions are Opera Glasses, Grand Theater Program and Bottled Applause, beside Salon Solitaire ("At the end of your turn, Repay 2."). The tier0 arm runs on `tier0/engine/furina_tide.py`. Not deployed. Next: [USER]'s play (a rule change), then a seat round. Provenance note, "Furina: the Salon's Tab, 2026-10-05". The v2 build is in git; the v1 Stage is the tag `furina-stage-frozen-2026-10-04`.
- **Furina: frozen (2026-10-04).** [USER]: "Let's freeze Furina's current build as-is for now, with the expectation that it gets shelved once we have a better idea." No card or rule changes to the current Stage build. The re-founding (`review/active/furina-refounding-2026-10-03.md`, ruled, sec.8 and sec.9) is being built as a sim-only slice; if it finds a strong structure, it replaces this build. The history below is the frozen build's.
- **Furina: the Stage, first run cleared.** Brief
  `review/active/furina-stage-brief-2026-09-08.md`; the Guest Cast paper
  `review/active/furina-guest-batch-2026-09-25.md`. Draft-3 rules (Bow on any
  exit, the fade, recasts add), eight Guest Stars with art and stage bodies.
  [USER]'s first solo Stage run beat A2 (2026-09-26): "the core concept is
  sound". The balance review that followed is
  `review/records/furina-balance-2026-09-26.md` (the front stayed exempt from
  the fade until the fade pass below; the turn predictor becomes cues on the
  performers). The supporting
  pool (`review/active/furina-supporting-pool-2026-09-26.md`, ruled at the
  defaults and swept) brought the pool to 78 (#692, #693, #694). Eleven Opus
  seats read it (2026-09-26): a Solo win from act 2, three whole runs dying at
  the act-3 boss, fixes in #696, #698, #699, #701, #702 and #703, Lyney and Stage Whisper
  reworked; `review/records/furina-pool-seat-round-2026-09-26.md`. **The
  Stage starter (2026-09-28):** [USER], "Typically we'd include 4 strikes, 4
  defends and 2 actually useful cards that teach the character's core
  mechanics - this seems like an unnecessary power spike." It is now the base
  Strike x4, Defend x4, Curtain Rise and Rising Applause; Take the Stage
  ("Summon a random performer with 3 Fanfare. Draw 1 card.", tentative until
  the balance pass's pool audit) and Regal Bearing (Block 5, Weak 1; upgraded
  6 and 2) are Commons, so the pool was 80 (78 after balance pass one). The
  shipped sheet and starter do not move. **The audit pass (2026-09-29)**, on
  [USER]'s ask for "a dedupe / audit / balance pass on Furina, aimed at
  polishing the existing core systems": Gala Dinner, A Rapt Audience and Scene
  Change cut (pool 78 -> 75); Ensemble Piece, Improvised Number, Ousia Surge,
  Pneuma Refrain, Final Bow, Bring the House Down and Grand Deluge raised;
  brief §17. **The fade pass (2026-09-29)**, on [USER]'s "make Fanfare deplete
  faster, but make that depletion more impactful. Keep her Block cards
  generally weak but her Spend cards strong": rule 12 is now a quarter of
  every performer's Fanfare, rounded down, the front's included ("What about
  a percentage fade, say 25%?"); Held Applause, Echoing Hall and Eternal
  Applause cut (pool 75 -> 72); the Spend modes of Curtain Rise, Tidal
  Flourish, Quick Cue, Spirited Aria and Grand Entrance, and Bravura's and
  Bring the House Down's per-point rates, raised; brief §18. After [USER]'s
  run on the new fade ("keeping him in the front was actually hard";
  Sigewinne "strictly fanfare-negative"), Wriothesley holds the front while
  on stage and Sigewinne is a free medic who heals the front performer
  (brief §18, guest paper rule 2 and table). **Pool completion (2026-10-01,
  ruled at the defaults):** paper `review/active/pool-completion-2026-10-01.md`
  sec.5, built in both engines: Aria for One, Interval Bell, Casting Agent
  (Uncommon), The Last Act, Critics' Darling, Star Turn (Rare), appended; her
  twelve old-kit cards stay (pick 3a). Her second Ancient, Center of
  Attention, is game-side. The pool is 78 (23 / 35 / 20). Klee's second
  Ancient, Alice's Masterpiece, landed in the same build. Provenance note,
  "Pool completion, 2026-10-01". **The rules pass (2026-10-01, ruled):**
  paper `review/active/furina-rules-pass-2026-10-01.md`, built in both
  engines. A Spend pays the back performer first, then forward, refused only
  when the whole stage holds less ([USER]: "Agreed, spending start
  back-forwards"); only a card or potion she plays summons on an empty stage;
  the front no longer regains 1 (The Curtain Never Falls keeps its 2);
  Wriothesley is "Always your front performer". Palais Ledger is "Your Spends
  cost 1 less Fanfare"; Center of Attention lost its short-bar clause. Her
  twelve old-kit rows are prototype rows (legacy cleanup pick 3): Singer of
  Many Waters gives the front 6 Fanfare, Opening Number, Leading Lady and
  Endless Waltz replace the three Companion feeders, eight are ported as
  they are. The pool stays 78 (23 / 35 / 20), every row a `proto_fs_` row.
  Quick Cue's Spend deals 11; five faces trimmed; brief §3, §6, §12 and §19.
  Provenance note, "Furina rules pass, 2026-10-01".

- **Varka: the Oath rework is built (Prototype, 2026-09-29).** Paper
  `review/active/varka-paper-kit-2026-09-28.md`, every pick ruled ([USER]:
  "I'm good with all of these Varka defaults"). A new character with no
  switch of his own (collapsed 2026-10-01): he compiles in every build.
  80 HP, 99 gold;
  starter base Strike x4, Defend x4, Windbound Execution (since 2026-10-03:
  cost 0, 4 [6] Anemo to one enemy) and one of four starter-only Knights,
  one per element, rolled per run; starting relic
  Boreas's Fang. The rules (`klee-mod/KleeCode/Powers/Prototype/VarkaOath.cs`,
  sim twin `tier0/engine/varka_oath.py`, live for a Varka seat): one Oath count
  per element, counted per card; his current element is his last Knight's,
  or since the open Oath (2026-09-30, [USER]: "Yep, let's ship it and see if
  anything breaks") the last Pyro, Hydro, Cryo or Electro any card of his
  applied, and his cards read only its Oath; a Swirl he makes pays that element (Pyro 3
  damage, Hydro 3 Block, Cryo 1 Vulnerable, Electro 3 to ALL); the Fang adds
  Four Winds' Ascension to his hand the first time each combat he gains Oath
  (since 2026-10-03: cost 2 with Retain, like Regent's Sovereign Blade, 10
  [13] Anemo then 3 [4] per Oath).
  His status bar shows the current element's Oath; the seat page prints the
  current element, all four counts and the Swirl payout. Pool 41 (15 / 18 /
  8), nine Knights. Absorb, the Winds and Knights' Muster are retired. The
  Lisa floor moved to 4 [5] after the R6 sim (#768). Per-row readings:
  `docs/notes/prototype-surface-provenance.md`, "Varka: the Oath rework".
  Batch one's round (`review/records/varka-round-1-2026-09-29.md`) read the
  old design. The Oath build's seat round
  (`review/records/varka-oath-round-2026-09-29.md`): two seats, one won the
  run, one died in act 2. Next: [USER] plays.
  The open-Oath round (`review/records/varka-open-oath-round-2026-10-01.md`):
  one win, one loss to the act-2 Entomancer elite.
  **The expansion (2026-10-01, ruled):** paper
  `review/active/varka-expansion-2026-10-01.md`, [USER]: "Agreed on all four.
  You're good to proceed." Each element has a job (its Swirl payout's) and
  two payoffs that read its own Oath by name; the Knight pass gives each
  element one defensive Knight; Muster is six cards. **Sec.3 is built** in
  both engines: 37 cards (5 / 17 / 15), the Knight pass (Diluc, Gleeful
  Songs, Heart of the Abyss, Suppressive Barrage, Awakening re-aimed), Noelle
  a Geo Knight that keeps his element, Downburst's fresh spread (pick 3a).
  The pool is 78 (20 / 35 / 23), thirteen pool Knights. Readings:
  provenance note, "Varka expansion, 2026-10-01". His seven relics and three
  potions (sec.4) are built too (#787). The sec.5 paired sim (#789) and two
  Sonnet seats (`review/records/varka-expansion-round-2026-10-01.md`) ran.
  **Element identities (2026-10-01, ruled):** paper
  `review/active/varka-element-identities-2026-10-01.md`, [USER]: "Overall
  looks reasonable, though Violet Storm looks undertuned" (raised to 8 [11],
  an Attack). Built in both engines: Electro draws and hits low, discards
  into Energy in the middle and spends at Rare (Charged Lunge, Short Circuit,
  Chain Lightning, Thundering Verdict at X, Violet Storm, in place of
  Updraft, Pressure Front, Unfurled Banner and Four Winds' Accord);
  Retaliating Tide replaces Unbroken Tide; Wildfire Oath is one big hit
  (since 2026-10-03 it deals his Pyro Oath to each enemy he applies Pyro
  to, and Short Circuit discards 2, draws 2 [3] and gains 1 Energy:
  provenance note, "Varka Wildfire Oath and Short Circuit, 2026-10-03"); a
  card that would switch his element says so on hover, and the element he
  left shows beside his badge for the turn. Pool still 78 (20 / 35 / 23).
  The sim: Electro mono still 21.7 behind the default drafter in act 1, and
  the stock pilot never sequences a discard into Short Circuit's Energy or
  Chain Lightning's discount, so the sim does not read Electro's middle.
  Readings and the tables: provenance note, "Varka element identities,
  2026-10-01".
  **Defence (2026-10-01, ruled):** paper
  `review/active/varka-defence-2026-10-01.md`, [USER]: "Everything else
  looks good!" Built in both engines: Gale Mantle (C, 5 [8] Block plus half
  his total Oath), Gust Ward (U, 0: 4 [6] Block, draw 1) and Windborne
  Resolve (U, Power: 5 [7] Block whenever his element changes) replace
  Squall, Four Banners and Favonian Standard; Oathbound Aegis gives half his
  total Oath at turn end, uncapped, upgrade cost 2 to 1; Tailwind Guard
  unchanged. Boreas's Fang makes the starter Knight's element current on
  his first turn, so the badge shows it from turn one. Pool still 78 (20 /
  35 / 23). The Block probe: the default drafter's act-3 elite Block over
  incoming 0.55 to 0.60 (the paper's bar was 0.72), the switch deck's 0.53
  to 0.66, Hydro mono 1.49 at most; act-3 boss turn-cap stalls rose; the
  stock drafter never takes Gust Ward. Readings and the tables: provenance
  note, "Varka defence, 2026-10-01".
  **The starter seat round (2026-10-03,
  `review/records/varka-starter-round-2026-10-03.md`):** on the rebalance
  round's two seeds, both runs reached the final boss and died there (last
  round: act 2 and floor 42); Windbound was no seat's NEVER AGAIN, and
  holding Ascension became a named decision.
  **The combo pass is built (2026-10-04,
  `review/active/varka-combo-pass-2026-10-04.md`, RULED, all four picks):**
  five generic Block cards out (Gale Mantle, West Wind Shield, Knightly
  Guard, Tailwind Guard, Oath of the Knights); Pyro's Exhaust engine in
  (Stoke the Flames, Ember Cleave, Pyre Oath) and Cryo's status payoffs
  (Shatter, Deep Freeze); Unwavering Banner reworded to pay 1 Oath when it
  holds a switch; Baron Bunny's hit to a random enemy; Charge of the Knights
  cost 1, Lion's Fang and Four Winds' Ascension upgrade to cost 1, Kaeya and
  Razor Attacks, two faces reworded. Pool 78 (20 / 35 / 23). The sim missed
  the paper's "Pyro and Cryo up" bar (Pyro -15, Cryo flat; the stock pilot
  prices an Exhaust at nothing) and Deep Freeze's upgrade (cost 0) is the
  builder's proposal: provenance note, "Varka combo pass, 2026-10-04".
  Next: the paper's two-seat round, then [USER]'s next Varka run.

**Klee's and Furina's own relics and potions** (paper
`review/active/relics-potions-klee-furina-2026-09-27.md`, ruled at the defaults
with the two Rare potions raised) are built behind their arms, which every build
carries since 2026-09-28: seven relics and
three potions each, the Silent borrow gone under the arm, Dodoco Tales repaired
and The Curtain Never Falls rebuilt for the Stage (Salon Solitaire's Orobas
upgrade now). Arm off, both pools are as they shipped; Kokomi keeps the Silent
borrow until her review pass. Next: a seat round with the relics given at
embark.

**The element port, phase one (2026-09-28)** (`review/ruled/element-home-review-2026-09-28.md`
§3, §4, §7.1, §7.3; [USER]: "That makes sense"). Anemo and Geo no longer
consume the aura they act on: a hit on a fresh aura reacts and leaves it
standing, spent; a hit on a spent aura pays nothing until the aura's own
element refreshes it. Swirl keeps the aura, spreads spent copies to every
enemy lacking it, refreshes the aura (full duration, fresh, no reaction) on
every enemy already wearing it (amended 2026-10-01) and deals a flat 2 to
every enemy; Crystallize gives its 4
Block and keeps the aura. The badge and the reaction preview say when an aura
is spent, and every reaction reports one event (reaction, target, dealer,
source kind). **2026-10-03: spent removed.** [USER]: "Should we get rid of
the concept of elements being 'spent' after a swirl? It seems to generate
confusion." then "agreed ... please proceed". Every reaction now consumes its
aura, Swirl and Crystallize included. A Swirl still pays what it paid (the
flat 2 to every enemy and Varka's payout) and spreads ordinary fresh copies
to the other enemies (one already wearing the element refreshes; another
aura is replaced). A copy is an application with no trigger, so it never
reacts by itself. Because copies are fresh, a Swirl that hits ALL enemies
pays once per enemy still wearing an aura when its Anemo hit lands. The
badge's spent face, the spent previews and `CrystallizeKeepsAura` are gone;
one switch is left, `-p:SwirlPays=false` (`klee-mod/KleeCode/Elements/TriggerRules.cs`),
sim twin `C.SWIRL_PAYS`, off until its retest. Downburst lost its "copies
arrive fresh" clause; its new rider (2026-10-04) is "If it Swirls, gain 2
Oath of the element Swirled." Next: phase two
(Burning and Dendro, `BACKLOG.md`).

All three prototypes start with no companion card. Whether each starts with
one comes back after the kits, with the reaction display (`EB-410`) and the
companion slot as a real draft choice.

## The Teyvat run frame: on hold

Built and behind `TeyvatFrame`, OFF in every release package; nothing
deleted, no further work. Six dressed faces (two nations per act), 122
dressed events, 149 dressed enemy slots, 27 music slots
(`operations/act-assets.md`, `operations/media.md`). It is off in every
build, dev included: [USER] dropped the whole arm because the first draft
(image, music and enemy art replacement) "wasn't very interesting". A later
item is to "figure out what we actually want to do with those assets". It comes back only as
**elemental enemies**: when the three kits are done, a short brief on
elemental shields goes to [USER] before any build.

## Live cell

Measurement law binds only at Balance; nothing is there today, so
`EXPERIMENTS.md` is dormant. The stamps below describe the shipped world and
the calibration bands are retired until Balance (2026-10-01, legacy cleanup
pick 5). Stamps read live via `tier05/cells.py`
(`PILOT_WEIGHTS_VERSION` 6).

| stamp | value | source | what this value covers |
|---|---|---|---|
| `RT` `RUNTEMPLATE_VERSION` | **13** | `tier0/constants.py` | `EB-83`: Wood Carvings joins the act-1 event pool. |
| `D` `DRAFTER_VERSION` | **18** | `tier0/constants.py` | `EB-28`: Salon deploy priced through `STATIC_SALON_MEMBER_VALUE = 1.5`. |
| `P` `POLICY_VERSION` | **11** | `tier05/draft.py` | R207's scorer-literacy window. |
| `C` `CONSTANTS_VERSION` | **22** | `tier0/constants.py` | Undercurrent costs 1 (2026-09-25). |

The standing twelve-arm baseline (`review/records/sitting-reads-2026-08-26-c20-d18-p11.md`)
is an `RT12` read and owes a re-baseline (`BACKLOG.md` `EB-195`).


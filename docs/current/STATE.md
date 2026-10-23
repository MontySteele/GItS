# STATE

What ships now and what is next. How a kit got here is in the papers and
records named below and git (last long copy:
`git show 3ce4f8c35:docs/current/STATE.md`); per-card readings in
`docs/notes/prototype-surface-provenance.md`. Picks for
[USER]: [`QUEUE.md`](QUEUE.md); to-dos: [`BACKLOG.md`](BACKLOG.md); rules:
[`LAW.md`](LAW.md); stage procedure: `operations/stage-gate.md`. Card
numbers live on the sheet.

## Release pass (ruled 2026-10-19)

[USER] took GPT's release review's five defaults ("Agreed all around"):
freeze Klee's and Varka's mechanics (wording and preview fixes only); Furina
stays a launch candidate; Kokomi's bounded finish comes next and Yae stays in
beta; elements, stories and the Abyss are kept, not grown. The pass stops when
newcomers can reach and understand the fun. Feedback comes through Workshop
comments and telemetry. Newcomer round 1 (`review/records/newcomer-round-1-2026-10-19.md`):
all five newcomers found and named their kit's central loop and would play
again. The gaps were Furina's refund amount, Yae's planting rule and Dawn Prayer
order, and Swirl's contribution (Klee, Varka). Round 2 runs on the same seed
after Furina's refund display and the Yae check.
Go-live pins to Steam's default `public` branch, not `public-beta`: on
2026-10-21 `public` is buildid 23811903 (2026-06-18) and `public-beta`
24724944 (2026-08-13), which the mod is built against. A compatibility check
against `public` is next ([USER]: "we should do a check against the public
version rather than the beta, and pin against that for the go-live").
Go-live save safety is built (2026-10-22, `operations/workshop.md`, "Save
safety"): the beta keeps its own save folder, and a Teyvat run hidden by
turning the mod off comes back once the mod is on and no run is open.

## Mod build environment (pinned)

Slay the Spire 2 **v0.111.0** (`41cef1ea`, buildid `24724944`, branch
`public-beta`), MegaDot v4.5.1, BaseLib **3.4.7.0**, .NET SDK 9.0.316, PCK
contract `roster-pck-v3`, package `klee` **v0.2**, deploy stamp
**`MAJOR.AUTO`**.

- **Build:** `tools/deploy_round.py` (the release build, every kit, unmarked,
  plus the seat bridge); `--staging` for a Balance kit's `<kit>-next` branch
  (`+next`). It prints the installed version.
- **Cards:** every card is a `proto_` row on `docs/prototype-surface.yaml`
  (`operations/prototype.md`); counts pinned in
  `KleeTests/Prototype/PoolCountTests.cs`.
- **The sim** (`tier0`, `tier05`) is a rules twin; balance is measured on
  the real game.
- **Last release package:** the friends-only Workshop beta **0.3.8**
  (2026-10-19), per the change note in the local, untracked
  `.workshop/beta/workshop.json` (`operations/workshop.md`). The older
  `0.2.1357` (2026-08-29) predates the current kits.

## Roster

| id | display | HP | nation | element | stage | draftable pool |
|---|---|---|---|---|---|---|
| `klee` | Klee | 70 | Mondstadt | Pyro | Balance | 78 |
| `kokomi` | Sangonomiya Kokomi | 80 | Inazuma | Hydro | Balance | 78 |
| `furina` | Furina | 78 | Fontaine | Hydro | Balance | 78 |
| `varka` | Varka | 80 | Mondstadt | Anemo | Balance | 78 |
| `yae` | Yae Miko | 72 | Inazuma | Electro | Prototype | 78 |

- Every kit: 78 draftable cards, two Ancient cards (one from Darv's Dusty
  Tome, one from Orobas's Archaic Tooth replacing a starter card), its own
  relics (seven each for Klee, Kokomi, Furina and Yae) and three potions.
  Co-op cards: Klee, Kokomi (five) and Varka (five); Furina has none since
  the Stage rework, Yae none yet.
- Every starter is the base Strike x4 and Defend x4 plus two cards of its
  own; basics change only on [USER]'s pick. No kit starts with a shared
  Companion; Varka's Knights are his own Companions and count as Companions
  for every synergy.
- **Card frames, stages 1 and 2 built** (`review/active/card-frames-2026-10-19.md`,
  `KleeCode/CardFrameColors.cs`): each kit tints its frame (Klee red-orange,
  Furina deep blue, Kokomi pearl coral, Varka teal, Yae magenta) and every
  Companion shows a nation pip; [USER] reviewed the tints in game
  (2026-10-21). Stage 2 (frame art and an Energy orb per kit, PR #1509)
  was reviewed and approved by [USER] in game.
- **Inazuma Companions** (`review/active/inazuma-companions-2026-10-18.md`,
  `review/active/pool-sweep-2026-10-18.md` sec.3): 34 cards (8 / 15 / 11);
  Musou no Hitotachi is a 3-cost Rare in place of Baleful Omen, Euthymia's
  upgrade is Innate. Unseen in game.
- **Next character shortlist** ([USER], 2026-10-21): "Zhongli > Nahida >
  Mavuika > Columbina", which covers every element save Cryo and every
  nation but Snezhnaya. Kokomi reached Balance on 2026-10-23; next, a
  Zhongli paper alongside a Yae taste audit.

## The kits

**Klee: Balance.**
- **Rules** (`review/active/klee-brief-2026-09-01.md` sec.3): Bombs grow 2 at
  the start of her turn and go off only to a *Set off* card or a Mine
  answering an attack. Each Bomb that goes off gives a Spark, which some cards
  cost; she opens with 3.
- **Pool:** 78 (25 / 32 / 21). Ancients: Alice's Masterpiece (Tome), Jumpy
  Dumpty Mk.Omega (Tooth on Jumpy Dumpty).
- **Process:** frozen on `main`; card and rule changes go to `klee-next` and
  arrive by promotion; text-only fixes (no number, no rule) land on `main`.
- **Latest record:** `review/records/klee-suite-6-2026-10-16.md` (mean 41.0,
  two runs won). Exquisite Compound is still not taken (0 of 7) and is
  first on her next card pass.
- **Visuals** (`review/active/klee-visual-paper-2026-10-12.md`,
  `tools/klee_rig`): rendered from the official model, which never leaves
  the scratchpad; 0.72 of an adult. Style G (painted shading, ground shadow)
  is being built.
- **Next:** [USER]'s A3 to A5 runs; the deck is left alone until outside
  feedback.

**Kokomi: Balance** (2026-10-23). Her test drive was a newcomer's: a big
Kokomi fan who does not usually play Slay the Spire played her on beta
0.3.12 and had fun. [USER]: "Kokomi passed the vibe check - she's approved
for Balance." That run sent no data (0.3.12 shipped without the uploader).
- **Rules** (`review/active/kokomi-brief-2026-09-01.md` sec.2): a card with a
  Plan line can be played on the Bake-Kurage instead (a Companion only if it
  prints one); it is carried out at the start of her next turn, after the
  draw. Clicking a waiting Plan flips it to the now-line. The Plans view
  (`Vfx/Prototype/KokomiPlanView.cs`, the peek button) is unseen in game.
- **Starter relic:** the Tamakushi Casket gains 1 Block whenever she Plans
  a card (Stings and Wards included) or plays a Companion (face-up or
  planned), never on a carry-out; the Watatsumi Casket gains 2 (both since
  the defence pass, 2026-10-22; the boss ramp had them at 2 and 3). A Plan card
  played face-up pays nothing (2026-10-20, [USER]: "2 was definitely the
  intent, and we should figure out a different Block solution if needed").
- **Jellyfish:** Stings and Wards are generated, cost 0, Ethereal and
  Exhaust, with a Plan line. A Ward draws 1 and its Plan draws 1 (2
  upgraded), no Block; Watchful Shoal adds damage to Stings only.
- **Pool:** 78 (20 / 38 / 20); relics and potions in
  `review/active/kokomi-relics-potions-2026-10-15.md`. Ancients: Divine
  Strategy (Tome), Princess of Watatsumi (Tooth on Kurage's Oath).
- **Latest built, unseen in game:** card paper v2
  (`review/active/kokomi-cards-2026-10-18.md`) and pool sweep sec.2.
- **Story built** (`review/active/kokomi-story-2026-10-16.md`,
  `Story/KokomiStory.cs`): events and the Public Address curse. Her lines
  (select, combat, Ancients, the Architect) are pick 3, open.
- **Parked:** Nereid's Ascension carries her burst's name only (no HP
  scaling, healing or jellyfish refresh). [USER]: "Let's flag this as a
  possible change on Kokomi and otherwise leave it alone."
- **Latest:** Ward draws, the Casket pays per card Planned or Companion
  played (`review/records/kokomi-yae-round-2026-10-19.md`); [USER]'s co-op runs
  2026-10-18.
- **Finish pass built** (`review/active/kokomi-cards-2026-10-18.md` sec.7,
  ruled all (a)): Battle Formation (Rare Power, 2): "At the start of your
  turn, if 2 or more of your Plans were carried out, gain [E] [and draw 1
  card]. Stings and Wards don't count." Grand Design (Rare Skill, 1): "Plan
  up to 3 [4] cards from your Hand. They cost 0. Draw 1 card for each.
  Exhaust." The Plan tip's new sentence is not built: at 134 characters it
  does not fit the tip ceilings (player box 100, seat tip 135).
- **Upgrade pass built** (`review/active/kokomi-next-2026-10-19.md`, "The
  weak-card and upgrade pass"): a Plan card's upgrade moves both lines where
  it can (Ambush, Read the Field, Pincer, Second Wave, Opening Gambit, Tidal
  Screen, Kelp Wall, Kurage's Wake, Spearhead, Joint Orders, Coordinated
  Strike, Turnabout, Juuga); War Council is Weak 2 [3], Plan 2 Energy [and
  draw 1]; Sea Glass Harvest 8 [11] Block with a Sea Glass preview; Steady
  Tide 9 [12], Plan draw 3 [4]; Sangonomiya's Orders+ adds an upgraded
  Companion; Crystal Collapse with none played plays a random Common one;
  Brine Sting counts for The Shape of Water. Tide Wall and Flank say they
  read intent when carried out; At Water's Edge's badge shows when it is
  spent.
- **Balance audit built** (`kokomi-next-2026-10-19.md`, 2026-10-21, "Agreed
  all around"): Princess of Watatsumi's Plan is 5 [8] to ALL three times;
  War Banner's upgrade adds Block only; Sea Glass Harvest transforms the
  Hand only. Its suite (`review/records/kokomi-balance-suite-2026-10-21.md`):
  36.4 mean, under base on damage in every act (0.76 in act 3).
- **Act-3 tempo built** (same paper, 2026-10-21): Watchful Shoal 5 [7],
  Following Current 4 [5].
- **Boss ramp and Casket built** (same paper, 2026-10-21, "Got it, let's
  try that"), after suite 2 (36.0 mean; boss damage a turn at hallway
  level): Kurage Vanguard deals 2 more each turn; the Casket paid 2 Block a
  counted play (Watatsumi 3) until the defence pass.
- **Taste audit built** (`review/active/kokomi-taste-audit-2026-10-21.md`,
  2026-10-21, "Agreed on all 5 defaults"): ten cards that were someone else's
  now speak her verbs. Shoal Call and Kurage Bloom Plan their Stings (the
  Casket pays per Sting); Resolve of Watatsumi adds 2 [3] to each carried-out
  Plan's hits and Block; Coral Crash, Undertow, Suffocating Deep and Sea's
  Reproach read intent; Watatsumi's Grace gains 3 [4] Block per Plan waiting;
  Flotsam Surge has a Plan line; Riptide Ruin hits once more per Plan carried
  out. Unseen in game.
- **Defence pass built** (`kokomi-next-2026-10-19.md`, 2026-10-22), after
  [USER]'s run (HP lost a normal fight 1.2 / 0.0 / 1.1 % by act, against
  Klee 2.9 / 7.9 / 16.5 and Furina 6.1 / 10.3 / 18.2; damage normal).
  [USER]: "I think it's fine for the Casket to pay on 0-cost cards as an
  intended loop, but I think 2 block per plan is making them too strong.
  Let's try 1a, 3a, and reducing the Casket to 1 again." The Casket is 1
  Block a counted play again (Watatsumi 2); Watatsumi's Grace and Kurage
  Canopy say "Stings and Wards don't count", and Canopy adds its Ward at
  the start of her turn if 2 or more Plans were carried out (Battle
  Formation's read); Tide Wall's Plan is 4 [6] Block plus the intent.
  Unseen in game.
- **Process:** frozen on `main`; card and rule changes go on `kokomi-next`
  with a suite record; text-only fixes land on `main`.
- **Next:** outside feedback (Workshop comments, telemetry); the deck is
  left alone until then.

**Furina: Balance** (2026-10-15).
- **Rules** (`review/active/furina-research-proposal-2026-10-05.md` sec.2):
  - **Drain** spends HP, never to 0. Each combat she has a Drain buffer of 1/4
    of her Max HP (Lyney adds 10); her own Drains may go past it, a guest's
    stop at it. At combat end only the HP drained within the buffer returns.
  - **Repay** returns drained HP, the past-line part first; HP a Repay
    cannot return becomes Block.
  - **Fanfare:** every HP lost or repaid prints 1.
  - **Guests:** three seats (four with Ensemble Cast). A Guest Star exhausts.
    At the end of her turn the guests act, oldest first. A fourth summon
    pushes the oldest off: it acts once, then leaves. A second copy of a
    guest moves it to the newest seat and it acts once.
- **Pool:** 78 (23 / 35 / 20); the smallest Block pool of any character.
  Starter relic Salon Solitaire ("At the end of your turn, Repay 1."),
  upgrade The Curtain Never Falls; relics and potions in
  `review/active/furina-card-pass-2026-10-15.md`. Ancients: Center of
  Attention (Tome), All the World's a Stage (Tooth on Rising Applause). Sim
  twin `tier0/engine/furina_tide.py`. Parked: Wriothesley's rarity.
- **All the World's a Stage+ gains Retain**, as Rising Applause+ does
  (2026-10-19: "the Ancient card should keep Retain as long as the starter
  does"; 2026-10-23: "Yes to Archaic Tooth; let's send it.").
- **Process:** frozen on `main`; changes go on `furina-next` with a suite
  record.
- **Latest record:** `review/records/furina-suite-4-2026-10-16.md` (mean
  40.4, two runs won). Its HP figures are before the Curtain Call refund and
  count her own Drains (GPT recheck, 2026-10-19): after the refund she loses
  7.7 / 12.8 / 14.9% of max HP a normal fight against base 8.8 / 14.9 / 10.0,
  so only act 3 is high.
- **Story built** (`review/active/furina-story-2026-10-15.md`,
  `Story/FurinaStory.cs`): events, lines and the Stage Fright curse. Seen
  in play (2026-10-23).
- **Next:** make her HP legible (which HP comes back after the fight, which
  Drain stays a cost, why Repay gives Block below full HP), not a buff; the
  co-op check owed at a finish line.

**Varka: Balance.**
- **Rules** (`review/active/varka-paper-kit-2026-09-28.md` sec.3;
  `VarkaOath.cs`, sim twin `tier0/engine/varka_oath.py`):
  - **Oath:** one count per element.
  - **Current element:** that of his last Knight, or of the last Pyro, Hydro,
    Cryo or Electro any card of his applied. His cards read only its Oath; a
    card that would change it says "(Makes X current)" in combat.
  - **Swirl:** a Swirl he makes gains 1 Oath of the element Swirled; with
    Boreas's Fang it also pays his current element (Pyro 5 damage, Hydro 3
    Block, Cryo 1 Vulnerable, Electro 3 to ALL).
  - **Display:** the Oath dial by the Energy orb
    (`Vfx/Prototype/VarkaOathDial.cs`), four element pips, the current one
    lit; his Oath badge is hidden on his status strip but stays on the model
    for the seat page.
- **Starter:** Four Winds' Ascension and one of four starter Knights, rolled
  per run; Windbound Execution is retired. Boreas's Fang: "At the start of
  each combat, your starting Knight's element becomes your current element.
  Your Swirls also pay it." Wolf's Gravestone (Orobas upgrade) adds an
  upgraded Ascension, free that turn, on his first Oath gain each combat.
- **Pool:** 78 (20 / 36 / 22), thirteen pool Knights. Ancients: All Four
  Winds (Tome); Dandelion Gale (Tooth, replacing Four Winds' Ascension): 10
  Anemo to ALL, then 3 per current Oath to each, Retain, 2 [1]; an upgraded
  Ascension becomes an upgraded Gale. Deep Freeze has no Retain.
- **Process:** frozen on `main`; card changes go through `varka-next` with a
  suite record; text-only fixes may land on `main`.
- **Latest record:** `review/records/varka-fang-next-suite-2026-10-19.md`
  (mean 48.0, three wins; Fang Pyro 5, power upgrades, rarity sweep;
  promoted 2026-10-19). Four upgraded powers were offered and never taken
  (Unwavering Banner, Absolute Zero, Eye of Stormterror, Wildfire Oath).
- **Next:** a base-five control round on the suite seeds with today's
  harness (is he above the bar?), after the public launch; no major nerf
  before it ([USER], 2026-10-19).

**Yae Miko: Prototype** (`review/active/yae-proposal-2026-10-12.md`; the
Stellar-Conduct nod is parked). Code: `proto_ym_` rows,
`Powers/Prototype/YaeShrine.cs`, `YaeAnnotations.cs`, sim twin
`tier0/engine/yae_shrine.py`, harness `tools/yae_expansion_sim.py`.
- **Shrine:** cards plant Sakura, cap 3 (Sakura Channeling: "You can have 2
  more Sakura"). Each acts at turn end, on Last Bloom (a withering Sakura
  strikes once more) and on Tenko ("Every Sakura acts now. Refresh them to at
  least 3 turns."): Sakura (Thunder) strikes for 1 + 2 per Level, Foxfire
  Sakura to ALL, Kitsune Sakura is the Block decoy. An aimed strike is one
  hit.
- **Levels** (`review/active/yae-sakura-levels-2026-10-17.md`): a plant
  comes in at its card's Level. A plant into a full shrine feeds (or
  replaces) the Sakura closest to withering; another kind takes the higher of
  the two Levels. No Level cap; Fox's Mooncall adds +1 per copy to all.
- **Annotations** (`review/active/yae-design-axes-2026-10-14.md`,
  `yae-review-r3-2026-10-14.md`): Red Ink, Fox Fire, Deadline Extension;
  distinct ones coexist on a Sakura, and Red Ink on a planting card passes to
  its Sakura. Edits skip cards an Annotation would do nothing on and reach
  Published cards. The Masterpiece is one enchantment: a permanent Published
  stack plus one temporary slot. Starter relic: "After an elite or boss
  fight, you may Publish an Annotation" (a combat reward row).
- **Pool:** 78 (20 / 39 / 19; Sakura Channeling went Uncommon 2026-10-23), official art. Relic offer: Meditations, her
  seven and Enlightened Blessing. Ancients: Yakan Evocation (Tooth; a Sesshou
  Sakura that keeps the starter's Annotations and strikes as it lands), Yae
  Publishing House (Tome) (`review/active/yae-ancients-relics-2026-10-16.md`).
  Starter change built (#1393, `review/active/yae-draft-pass-2026-10-17.md`).
- **Latest:** the Kitsune and Edit pass
  (`review/active/yae-block-edit-pass-2026-10-19.md`), seat-played
  (`review/records/yae-round-2026-10-19b.md`): Block per turn now at or over
  base; act-1 tempo is what is left (HP lost 1.27x base, damage 0.80).
- **Next:** [USER]'s playtest. Act-1 tempo is at base (R10 to 10-19b: 3.23
  turns and 18.8 damage a turn against base 3.37 and 18.6) with about 1 HP a
  fight left over, and The Kin took 4 of her 6 act-1 boss losses; her pool pass
  looks at defence there, not damage. Then an archetype paper on [USER]'s three
  identities (priestess, kitsune and familiar, writer), keeping the Edit side
  from carrying the kit. Watch Sakura Grove with Kitsune (Levels 10-15).

## Elements

- Every reaction consumes its aura, Swirl and Crystallize included. A Swirl
  deals 2 to every enemy and spreads fresh copies of the aura
  (`review/ruled/element-home-review-2026-09-28.md`). `-p:SwirlPays` is on
  (`Elements/TriggerRules.cs`, sim `C.SWIRL_PAYS`).
- **Next:** phase two, Burning and Dendro (`BACKLOG.md`).

## The Spiral Abyss mode: built and played by [USER] (2026-10-21)

A fourth main-menu mode (`klee-mod/KleeCode/Abyss/`); its button opens the
normal character select and runs count for ascension. Before each act's
Ancient a page offers three Blessings (a co-op party agrees on one) and the
enemies take one of the passed Shadows at random; each lasts the Whole run or
This act. Pools: 14 Blessings, 12 Shadows
(`review/active/spiral-abyss-pools-2026-10-12.md`,
`review/ruled/abyss-pools-2-2026-10-12.md`). Blessings show as relics,
Shadows as an "Abyss Shadows" relic and enemy badges. Seat records:
`review/records/spiral-abyss-round-*`.
Nothing pending. The old Teyvat frame stays off behind `TeyvatFrame`
(`operations/teyvat-frame.md`).

## Live cell

The sim stamps below describe the sim's world; they do not gate kit balance.
Stamps read live via `tier05/cells.py` (`PILOT_WEIGHTS_VERSION` 6). The last
column names the change that last bumped each stamp; the `D` and `C` ones
were about content retired since (the Salon, the shipped Undercurrent).

| stamp | value | source | what this value covers |
|---|---|---|---|
| `RT` `RUNTEMPLATE_VERSION` | **13** | `tier0/constants.py` | `EB-83`: Wood Carvings joins the act-1 event pool. |
| `D` `DRAFTER_VERSION` | **18** | `tier0/constants.py` | `EB-28`: Salon deploy pricing (the Salon is retired). |
| `P` `POLICY_VERSION` | **11** | `tier05/draft.py` | R207's scorer-literacy window. |
| `C` `CONSTANTS_VERSION` | **22** | `tier0/constants.py` | Undercurrent costs 1 (2026-09-25; the shipped card is retired). |

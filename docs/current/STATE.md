# STATE

What ships now and what is next. Nothing else: the history of how a kit got
here is in its brief, its papers, `docs/notes/prototype-surface-provenance.md`
and git (the last long copy: `git show 66e9a9bb:docs/current/STATE.md`).
Picks for [USER]: [`QUEUE.md`](QUEUE.md); to-dos: [`BACKLOG.md`](BACKLOG.md);
rules: [`LAW.md`](LAW.md); stage procedure: `operations/stage-gate.md`.

## Mod build environment (pinned)

Slay the Spire 2 **v0.111.0** (`41cef1ea`, buildid `24724944`, branch
`public-beta`), MegaDot v4.5.1, BaseLib **3.4.7.0**, .NET SDK 9.0.316, PCK
contract `roster-pck-v3`, package `klee` **v0.2**, deploy stamp
**`MAJOR.AUTO`**.

- **Build:** `tools/deploy_round.py` (the release build, every kit, unmarked,
  plus the seat bridge); `--staging` for a Balance kit's `<kit>-next` branch
  (`+next`). It prints the installed version.
- **Cards:** every card is a `proto_` row on `docs/prototype-surface.yaml`
  (`operations/prototype.md`); the 78 / Ancient / co-op counts are pinned in
  `KleeTests/Prototype/PoolCountTests.cs`.
- **The sim** (`tier0`, `tier05`) runs the current kits as a rules twin. It
  does not gate balance; balance is measured on the real game.
- **Last release package:** `0.2.1357` (2026-08-29), which predates the
  current kits.

## Roster

| id | display | HP | nation | element | stage | draftable pool |
|---|---|---|---|---|---|---|
| `klee` | Klee | 70 | Mondstadt | Pyro | Balance | 78 |
| `kokomi` | Sangonomiya Kokomi | 80 | Inazuma | Hydro | Prototype | 78 |
| `furina` | Furina | 78 | Fontaine | Hydro | Prototype | 78 |
| `varka` | Varka | 80 | Mondstadt | Anemo | Balance | 78 |

- Every kit: 78 draftable cards, plus two Ancient cards (one from Darv's
  Dusty Tome, one from Orobas's Archaic Tooth replacing a starter card).
  Klee and Kokomi have co-op cards; Varka's five are being designed
  ([USER]: "now is actually a great time to design 5 co-op cards for
  Varka"); Furina has none since the Stage rework.
- Every starter is the base Strike x4 and Defend x4 plus two cards of its own.
  Starter basics change only on [USER]'s pick. No kit starts with a Companion.
- **Character five is Yae Miko** (`review/active/yae-proposal-2026-10-12.md`,
  ruled; the Stellar-Conduct nod is parked). **Card stage, Paper:** the card
  paper `review/active/yae-card-paper-2026-10-13.md` (readings, starter,
  relic, a 30-card first batch, three answers to the Sakura scaling
  question, picks open in `QUEUE.md`). Her rows are a sim-only staging sheet
  (`docs/yae-staging.yaml`, `loader.STAGING_SHEETS`), her rules twin is
  `tier0/engine/yae_shrine.py`, and `tools/yae_expansion_sim.py` is the
  smoke harness. No C# until the picks are ruled.

## The kits

Per-card readings: `docs/notes/prototype-surface-provenance.md`.

**Klee: Balance.**
- **Rules** (`review/active/klee-brief-2026-09-01.md` sec.3): Bombs grow 2 at
  the start of her turn and go off only to a *Set off* card or a Mine
  answering an attack. Each Bomb that goes off gives a Spark, which some cards
  cost; she opens with 3.
- **Pool:** 78 (25 / 32 / 21); seven relics, three potions. Ancients: Alice's
  Masterpiece (Tome) and Jumpy Dumpty Mk.Omega (Tooth on Jumpy Dumpty).
- **Process:** frozen on `main`; card and rule changes go to `klee-next`
  and arrive by promotion. Text-only fixes (no number, no rule) land on
  `main` directly (`docs/current/operations/stage-gate.md`, 2026-10-13).
- **Records:** `review/records/klee-suite-4-2026-10-08.md` and
  `review/records/klee-user-run-2026-10-11.md`.
- **Visuals** (`review/active/klee-visual-paper-2026-10-12.md`): rendered
  from the official model, which never leaves the scratchpad
  (`tools/klee_render`, `tools/klee_rig`). Stance A in combat, stance B at
  the merchant and select, 0.72 of an adult; the bomb is a thrown projectile.
  Style G (painted shading, ground shadow) is being built.
- **Next:** [USER]'s A3 to A5 runs, which read her deep scaling; the deck is
  left alone until outside feedback.

**Kokomi: Prototype.**
- **Rules** (`review/active/kokomi-brief-2026-09-01.md` sec.2): a card with a
  Plan line, or any Companion, can be played on the Bake-Kurage instead. It
  is carried out at the start of her next turn, after the draw; clicking a
  waiting Plan flips it to the now-line. A planned Companion is carried out
  after the Bake-Kurage applies Hydro to its target.
- **Starter relic:** the Tamakushi Casket gains 3 Block at the start of her
  turn while a Plan is waiting, after the Block clear and before Plans
  resolve. Its upgrade, the Watatsumi Casket, gains 3 for each Plan waiting.
- **Jellyfish:** Stings and Wards are generated, cost 0, Ethereal and
  Exhaust, and have a Plan line.
- **Pool:** 78 (20 / 38 / 20), five co-op cards. Ancients: Divine Strategy
  (Tome) and Princess of Watatsumi (Tooth on Kurage's Oath).
- **Latest:** round 4 on 2026-10-13 (five seats, 0.2.5263) was 1/5 won,
  with three runs at an act-3 boss, and Wards were made in every lane
  (`review/active/kokomi-review-r4-2026-10-13.md`). Its A-list is built:
  Moon's Reflection is unplayable while the Exhaust Pile is empty, Opening
  Gambit's and Second Wave's now-line no longer spends Vigor, the brief's
  Casket line reads start of turn, and three page fixes (a copy a play adds
  takes the next number, the difference line names only what moved, and
  `--define` reads a power on the board). The rider-power sentence did not
  fit the 125-character power ceiling (BACKLOG).
- **Next:** [USER]'s picks on review r4; the default is his own finish-line
  run.
- **Possible change, parked:** Nereid's Ascension carries her burst's name
  only (no HP scaling, healing or jellyfish refresh, unlike the other three
  kits' bursts). [USER]: "Let's flag this as a possible change on Kokomi and
  otherwise leave it alone."

**Furina: Prototype.**
- **Rules** (`review/active/furina-research-proposal-2026-10-05.md`, sec.2):
  - **Drain** spends HP, never to 0. Each combat she has a Drain buffer of 1/4
    of her Max HP (Lyney adds 10); her own Drains may go past it, a guest's
    stop at it. At combat end only the HP drained within the buffer returns.
  - **Repay** returns drained HP, the past-line part first; most Repay cards
    pay Block, Vigor or damage for HP a Repay could not return.
  - **Fanfare:** every HP lost or repaid prints 1.
  - **Guests:** three seats (four with Ensemble Cast). A Guest Star exhausts.
    At the end of her turn the guests act, oldest first. A fourth summon
    pushes the oldest guest off: it acts once, then leaves. A second copy of
    a guest moves it to the newest seat and it acts once.
- **Pool:** 78 (23 / 35 / 20). Relics: Salon Solitaire ("At the end of your
  turn, Repay 1."), its upgrade The Curtain Never Falls, Opera Glasses, Grand
  Theater Program; one potion, Bottled Applause. Ancients: Center of
  Attention (Tome) and All the World's a Stage (Tooth on Rising Applause).
  Sim twin `tier0/engine/furina_tide.py`.
- **Latest:** the overnight wave (`review/records/furina-wave-2026-10-13.md`,
  1 win in 6) shipped its text and display fixes (#1202). Her Block pool is the
  smallest of any character (12 cards, 41 Block printed; census in the record).
- **Since:** the pool review (`review/active/furina-pool-review-2026-10-13.md`,
  #1211) and the Guest Star package
  (`review/active/furina-guest-package-2026-10-13.md`, #1214) are built and
  deployed.
- **Next:** [USER]'s playtest of that build. Her new model (#1241) is wired in
  once the guest pose fixes are approved. Parked: Wriothesley's rarity.

**Varka: Balance.**
- **Rules** (`review/active/varka-paper-kit-2026-09-28.md` sec.3;
  `VarkaOath.cs`, sim twin `tier0/engine/varka_oath.py`):
  - **Oath:** one count per element.
  - **Current element:** that of his last Knight, or of the last Pyro, Hydro,
    Cryo or Electro any card of his applied. His cards read only its Oath; a
    card that would change it says "(Makes X current)" in combat.
  - **Swirl:** a Swirl he makes gains 1 Oath of the element Swirled, and
    while he holds Boreas's Fang it pays his current element (Pyro 3
    damage, Hydro 3 Block, Cryo 1 Vulnerable, Electro 3 to ALL).
- **Starter:** Strike x4, Defend x4, Four Winds' Ascension and one of four
  starter Knights, rolled per run (2026-10-13, [USER]: "I don't want to give
  him two starting effects, so if we do (a), then I'd want to knock
  Windbound Execution out of his starting deck and make Four Winds'
  Ascension his second starter instead"; "Starter - (a)"). Windbound
  Execution is retired. Boreas's Fang: "At the start of each combat, your
  starting Knight's element becomes current. Your Swirls also pay your
  current element." ([USER]: the Swirl bonus "is basically a second starter
  relic untied to his actual relic"). Wolf's Gravestone, its Orobas upgrade,
  says the same and adds an upgraded Ascension, free that turn, on his first
  Oath gain each combat.
- **Pool:** 78 (20 / 35 / 23), thirteen pool Knights, his own relics and
  three potions. Ancients: All Four Winds (Tome), and Dandelion Gale from the
  Archaic Tooth, replacing Four Winds' Ascension: 10 Anemo to ALL, then 3
  per current Oath to each, Retain, 2 [1]; an upgraded Ascension becomes an
  upgraded Gale ([USER]: "let's have the upgrade make it AoE and also reduce
  the cost to 1 when upgraded", then "the ancient starts at 2, and upgrading
  it at a campfire (or replacing an already-upgraded Ascension) takes it to
  1"). Deep Freeze lost Retain ([USER]: "I think we should drop Retain").
- **Latest:** [USER]'s playtest passed (2026-10-13: "Ok, a solid run on
  Varka! Not too hard, but also not a total cakewalk. I think he's ready to
  move to Balance, officially."). The starter, Fang, Gale and Deep Freeze
  change (`varka-starter-fang-2026-10-13`) is the last change before the
  freeze. The pool audit (2026-10-13) then changed six cards: Blazing
  Charge, Kindled Edge, Chain Lightning, Tempest of the Four Winds,
  Downburst and Eula: Icetide Vortex.
- **Next:** per `operations/stage-gate.md` he is frozen on `main` once that
  change merges. Later card changes go through `varka-next` with a suite
  record; text-only fixes may land on `main`. Then his story, events and
  visual checks in game, and the two-seat round on the starter change.

## Elements

- Every reaction consumes its aura; Swirl and Crystallize included.
- A Swirl deals 2 to every enemy and spreads fresh copies of the aura (phase
  one: `review/ruled/element-home-review-2026-09-28.md`).
- `-p:SwirlPays` is on (`Elements/TriggerRules.cs`, sim twin
  `C.SWIRL_PAYS`).
- **Next:** phase two, Burning and Dendro (`BACKLOG.md`).

## The Spiral Abyss mode: built, not yet played

A fourth main-menu mode (`klee-mod/KleeCode/Abyss/`).
- **Entry:** a Spiral Abyss button opens the normal character select; runs
  count for ascension.
- **The page:** before each act's Ancient a full-screen page offers three
  Blessings, and the enemies take one of the passed Shadows at random. A
  co-op party agrees on one Blessing.
- **Durations:** each entry lasts the Whole run or This act. The pools are 14
  Blessings and 12 Shadows (papers `review/active/spiral-abyss-pools-2026-10-12.md`
  and `review/ruled/abyss-pools-2-2026-10-12.md`).
- **Display:** each Blessing is a relic; Shadows show as an "Abyss Shadows"
  relic and as badges on enemies.
- **Tests:** `KleeTests/SpiralAbyss*Tests.cs`, `AbyssOverlayTests.cs`,
  `AbyssPoolsTwoTests.cs`.
- **Next:** [USER]'s live checks of the screen and the act change, then one
  solo and one co-op seat; Klee and Varka are the test pair. The old Teyvat
  frame stays off behind `TeyvatFrame` (`operations/teyvat-frame.md`).

## Live cell

The sim stamps below describe the sim's world; they do not gate kit balance.
Stamps read live via `tier05/cells.py` (`PILOT_WEIGHTS_VERSION` 6).

| stamp | value | source | what this value covers |
|---|---|---|---|
| `RT` `RUNTEMPLATE_VERSION` | **13** | `tier0/constants.py` | `EB-83`: Wood Carvings joins the act-1 event pool. |
| `D` `DRAFTER_VERSION` | **18** | `tier0/constants.py` | `EB-28`: Salon deploy priced through `STATIC_SALON_MEMBER_VALUE = 1.5`. |
| `P` `POLICY_VERSION` | **11** | `tier05/draft.py` | R207's scorer-literacy window. |
| `C` `CONSTANTS_VERSION` | **22** | `tier0/constants.py` | Undercurrent costs 1 (2026-09-25). |

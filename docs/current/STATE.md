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
| `varka` | Varka | 80 | Mondstadt | Anemo | Prototype, Balance after [USER]'s playtest | 78 |

- Every kit: 78 draftable cards, plus two Ancient cards (one from Darv's
  Dusty Tome, one from Orobas's Archaic Tooth replacing a starter card) and
  its co-op cards.
- Every starter is the base Strike x4 and Defend x4 plus two cards of its own.
  Starter basics change only on [USER]'s pick. No kit starts with a Companion.
- **Character five is Yae Miko** (`review/active/yae-proposal-2026-10-12.md`,
  ruled; the Stellar-Conduct nod is parked). Her card stage starts once Varka
  reaches Balance.

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
- **Latest:** round 3 on 2026-10-13 was 0/5, but Stings were made and
  played in every run and her mean HP leaving the act-1 boss rose from 22 (round
  1) to 49 of 80 (`review/active/kokomi-review-r3-2026-10-13.md`). Its A-list is
  built (#1218): Opening Gambit's and Second Wave's window text, Bubble Ward
  6 [9], Kurage Canopy makes a Ward per carried-out Plan, and page receipts
  for hand-full discards and Ethereal Exhausts. Albedo, Solar Isotoma is now
  2 [3] Geo damage to ALL enemies per Attack played this turn (#1219).
- **Next:** round 4 (five seats, 0.2.5263) read for Wards made and played;
  [USER] ruled (b) on review r3.
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
- **Next:** a card-pool review on [USER]'s playtest: Block first, then the
  conditional cards and the ones never taken. Otherwise she is left alone.

**Varka: Prototype, near Balance.**
- **Rules** (`review/active/varka-paper-kit-2026-09-28.md` sec.3;
  `VarkaOath.cs`, sim twin `tier0/engine/varka_oath.py`):
  - **Oath:** one count per element.
  - **Current element:** that of his last Knight, or of the last Pyro, Hydro,
    Cryo or Electro any card of his applied. His cards read only its Oath; a
    card that would change it says "(Makes X current)" in combat.
  - **Swirl:** a Swirl he makes pays his current element (Pyro 3 damage,
    Hydro 3 Block, Cryo 1 Vulnerable, Electro 3 to ALL).
- **Starter:** Windbound Execution and one of four starter Knights, rolled
  per run. Boreas's Fang adds Four Winds' Ascension the first time each
  combat he gains Oath.
- **Pool:** 78 (20 / 35 / 23), thirteen pool Knights, his own relics and
  three potions. Ancients: All Four Winds (Tome) and Dandelion Gale (Tooth on
  Windbound Execution).
- **Latest:** the last pass (`review/ruled/varka-last-pass-2026-10-12.md`)
  gave twelve always-skipped cards a floor and cut five costs. The overnight
  wave on it (`review/records/varka-wave-2026-10-13.md`, 1 win in 5) found no
  design problem; Four Winds' Ascension is the first number to watch.
- **Next:** [USER]'s playtest, then Balance (`operations/stage-gate.md`),
  then his visuals, story and events, as Klee had.

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

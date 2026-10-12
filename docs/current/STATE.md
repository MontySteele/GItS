# STATE

What ships and what is next. Picks for [USER]: [`QUEUE.md`](QUEUE.md);
to-dos: [`BACKLOG.md`](BACKLOG.md); rules: [`LAW.md`](LAW.md). Each kit keeps
its current rules, pool and next step. Pass-by-pass history left on
2026-10-08 and is in git (`git show bf073df4:docs/current/STATE.md`); Furina's
v1 Stage is at tag `furina-stage-frozen-2026-10-04`; older narrative:
[`workstreams.md`](workstreams.md).

## Mod build environment (pinned)

Slay the Spire 2 **v0.111.0** (`41cef1ea`, buildid `24724944`, branch
`public-beta`), MegaDot v4.5.1, BaseLib **3.4.7.0**, .NET SDK 9.0.316, PCK
contract `roster-pck-v3`, package `klee` **v0.2**, deploy stamp
**`MAJOR.AUTO`**. `tools/deploy_round.py` prints the installed version.

**The current kits are the release build** (2026-09-28; [USER]: "Let's go
ahead and make all 3 current builds the active release builds to avoid this
confusion."). Every build carries them, unmarked: a plain `dotnet build`,
`klee-mod\build\deploy.ps1` and the `-Package` handoff zip. **A round's build
is `tools/deploy_round.py`** (`deploy.ps1`, then the bridge); a Balance kit's
staging build is `deploy_round.py --staging` (`+next`). The old shipped kits
are gone from both engines (legacy cleanup stages 5 and 6,
`review/active/legacy-cleanup-2026-10-01.md`). Every card is a `proto_` row on
`docs/prototype-surface.yaml` (`operations/prototype.md`); each C# pool is its
roster, and the 78 / Ancient / co-op counts are pinned in
`KleeTests/Prototype/PoolCountTests.cs`. The tier0 sim always runs the current
kits; its calibration bands are retired, and the sim does not gate kit balance
(the measurement ruling, 2026-10-05). **Last release package: `0.2.1357`**
(2026-08-29), which predates the ruling and carries the old kits.

## Roster

| id | display | HP | nation | element | stage | draftable pool |
|---|---|---|---|---|---|---|
| `klee` | Klee | 70 | Mondstadt | Pyro | Balance (`klee-next` promoted 2026-10-11) | 78 |
| `kokomi` | Sangonomiya Kokomi | 80 | Inazuma | Hydro | Prototype | 78 |
| `furina` | Furina | 78 | Fontaine | Hydro | Prototype (the Salon's Tab; pool-75 rulings and the block gap built) | 78 |
| `varka` | Varka | 80 | Mondstadt | Anemo | Prototype (combo pass built) | 78 |

**Every kit's pool target is 78 standard draftable cards**, plus its Ancient
rewards and multiplayer cards; a smaller pool reads more reliable than it will
be. Starter basics are never changed without [USER]'s pick; every kit's
starter is the base Strike x4 and Defend x4 plus two cards of its own ([USER],
2026-09-28: "The characters' kits should all use basic Strike and Defend.").
No kit starts with a companion card; that returns after the kits, with the
reaction display (`EB-410`) and the companion slot as a draft choice.

## The kits (Paper, then Prototype, then Balance; `operations/stage-gate.md`)

Per-card readings for every kit: `docs/notes/prototype-surface-provenance.md`.

- **Klee: Balance (ruled 2026-10-03; [USER]: "Agreed all around!").** Brief
  `review/active/klee-brief-2026-09-01.md` (sec.3, the rules: Bombs grow at the
  start of her turn and go off only to a *Set off* card or a Mine answering an
  attack; each Bomb that goes off gives a Spark, which some cards cost). Pool
  78 (25 / 32 / 21; Boom Badge to Common, [USER] 2026-10-07:
  "Agreed on Boom Badge, but let's keep powers out of Common and leave Secret
  Base at Uncommon."); seven relics of her own and three potions. **Promoted
  2026-10-11 without a suite record** ([USER]: "personally I think the current
  builds are all much better than the old frozen one and I'm about ready to
  override the previous frozen build with the current characters"): `klee-next`
  reached `main` in one PR (#940) and the suite requirement was waived for that
  promotion only. She stays at Balance; later changes again go to `klee-next`
  and reach `main` by promotion (`operations/stage-gate.md`). Latest suite
  record `review/records/klee-suite-4-2026-10-08.md`. What the promotion
  carried: the scaling pass (`review/active/klee-scaling-pass-2026-10-05.md`;
  Secret Base places a Bomb 4 [6] each turn, Boom Badge Retains and does not
  stack); the tempo paper (`review/active/klee-tempo-paper-2026-10-07.md`;
  [USER]: "I personally found Blast Shield and Kitchen Alchemy quite useful in
  my runs, so I'm not sure I buy that they should go. Otherwise agreed."): out
  It Wasn't Me!, Sorry, Jean..., Grounded, Sit Tight, Experiment in Progress;
  in Simmer, Taste Test, Tinkering, Dodoco Tag, Explosive Spark; the design
  review (`review/active/klee-design-review-2026-10-08.md`; [USER]: "Nope, this
  all looks good. I'm now in agreement with all picks."): Bombs grow 2 a turn,
  3 opening Sparks, every drafted Bomb or Mine placer prints 2 bigger; in Fire!
  Fire! and Blasting Spree; out Playdate and Pop! (Pop! stays off-pool for Klee
  Can Explain!); 2026-10-11 ([USER]: "Confiscated is too punishing"; "Lisa's
  Treats also underwhelmed"; "should we tag Confiscated with Exhaust?"): Fish
  Blasting 9 [12] to ALL and a Dazed, Lisa's Treats one Confiscated,
  Confiscated Exhausts; Tinder Toss 5 [8] to ALL; Alice's Detonator adds
  Alice's Mine (0, Ethereal, Exhaust, a Mine 10 [15]) each turn, Sentry Mode's
  shape; the Commons pass (`review/active/klee-commons-pass-2026-10-11.md`,
  seven numbers) and the Uncommons and Rares pass
  (`review/active/klee-upper-pass-2026-10-11.md`, all defaults): ten numbers,
  Exquisite Compound moves each Bomb (no merge), Tag Along and Adventure Club
  choose 1 of 3 and 2 of 4; Stoke the Fuse aims at an enemy. [USER]'s run
  2026-10-11 on 0.2.4969 ("Overall much improved!"; a fair act-3 death,
  `review/records/klee-user-run-2026-10-11.md`) reworked Alice's Recipe: cost
  3, "Whenever you place a Bomb or Mine, your other Bombs and Mines grow by
  2 [3]." **Next:** [USER]'s higher-ascension (A3 to A5) runs, which read her
  deep scaling.
- **Kokomi: Prototype, re-founded 2026-10-12.** Brief
  `review/active/kokomi-brief-2026-09-01.md` (sec.2, the rules). A card with
  a Plan line, or any Companion card, can be played on the Bake-Kurage
  instead, and it is carried out at the start of her next turn, after the
  draw; a click on a waiting Plan flips it to the now-line
  (`review/active/kokomi-delay-pays-2026-10-01.md`). The re-founding
  (direction `review/active/kokomi-design-pass-2026-10-11.md`, cards
  `review/active/kokomi-card-paper-2026-10-12.md`, both ruled) retired the
  Casket's count, Open the Casket and Dusk: the Tamakushi Casket now gains 3
  Block at the end of her turn while a Plan is waiting (the Watatsumi Casket
  5). Ethereal is the base keyword and a written card is not lost to it.
  Stings and Wards are her generated jellyfish (Ethereal, Exhaust; cost 0
  with a Plan line since the jellyfish build, below).
  A written Companion is carried out at its printed rate after the
  Bake-Kurage applies Hydro to its target; Gorou's four are her own cards
  with their own Plan lines. Pool 78 (21 / 37 / 20) plus five co-op cards
  and two Ancients. The build before it is tagged
  `kokomi-casket-frozen-2026-10-12`. Three seat rounds and a forced test
  ran on 2026-10-12 (`review/records/kokomi-round-{1,2,3}-2026-10-12.md`,
  `kokomi-growth-test-2026-10-12.md`): 0 wins in 32; act 1 her safest yet;
  act-2 bosses the wall (her own damage 45% of base; an Ironclad control
  died there too); act-3 own-card damage about 62% of base. Watchful Shoal
  is now "Your Stings deal 3 additional damage. Your Wards gain 3
  additional Block." (a growth test, reversible). The jellyfish build
  (`review/active/kokomi-jellyfish-growth-2026-10-12.md`, ruled at all
  defaults) makes Stings the Silent's Shivs with a Plan line (Sting 0: 4 [6],
  Plan 3 [4] to ALL; Ward 0: 4 [6] Block, Plan 1 [2] Weak to ALL), prices
  the generators at the Silent's rates (Shoal Call is Blade Dance), makes
  Endless Shoal the Uncommon "a Sting per Plan carried out", and adds All
  Streams Flow to the Sea (Rare) and The Shape of Water (Uncommon); Measured
  Breath and Spring Tide are cut. Telemetry counts Stings made, played,
  written and lost per fight. Next: a Kokomi seat round on that build, then
  [USER]'s run on it.
- **Furina: Prototype, the Salon's Tab (2026-10-05).** Her rules are the
  research proposal (`review/active/furina-research-proposal-2026-10-05.md`,
  sec.2 rules, sec.16 slice and curtain call, sec.17's two edits); [USER]:
  "the current one built overnight can be discarded". Furina pays HP for
  power: Drain spends HP, never to 0; each combat she has a Drain buffer of
  1/4 of her Max HP, rounded down, counted in HP drained, so a hit never
  uses it up, and her Drain line is her HP less the buffer left (2026-10-11,
  replacing the entry-HP line of 2026-10-09; Lyney adds 10 to the buffer),
  her own Drains may go past it (a
  guest act's Drain stops at it, the drain-line round 2026-10-09), and when
  combat ends only the HP drained within the buffer returns (A Five-Century Act
  returns the rest too). Repay returns drained HP, the past-line part first;
  every HP lost or repaid prints 1 Fanfare. The Repay floor: most Repay cards
  pay Block, Vigor or damage for the HP a Repay could not return (the Drain
  line rule and the Repay floor, ruled 2026-10-09, records pick 1 and 2).
  Three guest seats (four with Ensemble
  Cast); eleven guests. The guest rule
  (`review/active/furina-pool-growth-2026-10-09.md` sec.3, ruled 2026-10-09):
  a Guest Star exhausts and has no effect on summon; when its guest leaves (a
  fourth summon, or Final Bow) its card goes to the discard pile; a second
  copy moves its guest to the newest seat and it acts once (2026-10-11); a
  guest a fourth summon pushes off a full stage acts once, then leaves
  (2026-10-11: "(b) a guest who's pushed out takes a bow"); at the end of her turn
  the guests act oldest first, then Showstopper Spends 5 and they act again,
  then Salon Solitaire Repays; an upgrade raises a guest's line or act. The
  pool is the starter and 78 cards (23 / 35 / 20 since the diversity pass,
  built 2026-10-11 at all five defaults,
  `review/active/furina-diversity-pass-2026-10-11.md`: two guest styles,
  Headliner, Leading Lady, Full House and Packed House in, Gentle Current,
  Surging Waters, Pay the Tab and Sold Out cut, Bravura 7 Hydro per 3 spent,
  Tutti! and Wriothesley Common, four floors; Guest Star: Navia moved
  Rare to Uncommon 2026-10-10, "I lean more towards putting Navia to
  Uncommon first"; Standing Ovation Common again, "Spend half your
  Fanfare", 2026-10-11), built from that paper's
  sec.5 less Endless Waltz (cut 2026-10-09), plus the block gap's four
  (Velvet Curtain, Private Box, The Masquerade, The Show Must Go On; drain-line
  round pick 2, ruled 2026-10-09: "Yeah, agreed - let's plug the block gap
  now"; she had 7 Block cards in 74), and with the round's card
  numbers (Standing Ovation Uncommon, Bravura+ base 10, Crabaletta 20,
  Soloist's Solicitation 6, Commanding Gaze 2 Vulnerable, Freminet's act
  Block, Neuvillette cost 1 and act on all HP lost); Overdraft gives its
  Energy next turn (the build's loop ruling). Relics: the
  starter Salon Solitaire ("At the end of your turn, Repay 1."; 2 before the
  2026-10-09 playtest trim), its Orobas upgrade The Curtain Never Falls
  (Repay 2; Ancient, never rolled), and two reward
  relics, Opera Glasses and Grand Theater Program; one potion, Bottled
  Applause (`FurinaRelicPool.cs`, `ArmPotions.cs`). Sim twin
  `tier0/engine/furina_tide.py`. Latest round
  `review/records/furina-pool75-round-2026-10-09.md` (pool 75: 1 win in 7,
  four deaths in act 2 with the Drain half locked; Fable review; picks
  ruled; picks 1-3 built 2026-10-09; Soothing Waters keeps no Repay floor,
  which closed the one loop the floor made). The Spend paper
  (`review/active/furina-spend-paper-2026-10-10.md`): "Spend up to X" on
  Tidal Flourish, Spirited Aria, Crashing Waves and Hold the Stage, and
  Navia's act Spends half the bank and Freminet's a quarter (pick 2,
  ruled 2026-10-10); the rest built at the paper's defaults, picks open on
  #1014. The Spend outlet paper
  (`review/active/furina-spend-outlet-2026-10-12.md`, ruled 2026-10-12, all
  defaults): Spirited Aria spends up to 12, Crashing Waves and Hold the Stage
  up to 16; Packed House is a Skill, "Gain 5 [8] Block, plus 1 for every 4
  Fanfare you have."; Rising Applause+ gains Retain, with a when-to-play tip.
  Next: a seat round ([USER]:
  "Yes - let's test it with a seat"). At her
  finish line, re-ask her motion look (`AS2-B5`, dropped
  from QUEUE 2026-10-08; plan `git show 762e94d9^:docs/animation-sprint-2-plan.md`).
- **Varka: Prototype, the combo pass built (2026-10-04).** Rules
  `review/active/varka-paper-kit-2026-09-28.md` sec.3
  (`klee-mod/KleeCode/Powers/Prototype/VarkaOath.cs`, sim twin
  `tier0/engine/varka_oath.py`). 80 HP, 99 gold; starter base Strike x4,
  Defend x4, Windbound Execution (0: 4 [6] Anemo) and one of four
  starter-only Knights, one per element, rolled per run; starting relic
  Boreas's Fang, which adds Four Winds' Ascension (2, Retain: 10 [13] Anemo
  then 3 [4] per Oath) the first time each combat he gains Oath. One Oath
  count per element; his current element is that of his last Knight or of the
  last Pyro, Hydro, Cryo or Electro any card of his applied, and his cards
  read only its Oath. A Swirl he makes pays that element (Pyro 3 damage,
  Hydro 3 Block, Cryo 1 Vulnerable, Electro 3 to ALL). Pool 78 (20 / 35 / 23),
  thirteen pool Knights; his own relics and three potions. Latest records
  `review/records/varka-solo-check-2026-10-07.md` (1 win of 5 on the base
  seeds) and `review/records/varka-offers-round-2026-10-08.md` (all five
  reached act 3, none won; Pyro and Cryo payoffs offered and passed, Pyro
  taken at 10%). The Pyro pass is built
  (`review/active/varka-pyro-pass-2026-10-11.md`: Ashen Oath gives Strength)
  and Pyro paper 2 on top of it
  (`review/active/varka-pyro-reactions-2026-10-12.md`: Ember Cleave is Setup
  Strike in Pyro, Stoke the Flames powers the next Pyro Attack this turn,
  the Exhaust rider is retired); next a two-seat Varka round.

## Elements

Every reaction consumes its aura, Swirl and Crystallize included; there is no
spent aura (2026-10-03, [USER]: "Should we get rid of the concept of elements
being 'spent' after a swirl? It seems to generate confusion." then "agreed ...
please proceed"). A Swirl deals a flat 2 to every enemy and spreads ordinary
fresh copies of the aura to the other enemies (one already wearing the element
refreshes; another aura is replaced); a copy is an application with no
trigger (phase one: `review/ruled/element-home-review-2026-09-28.md`). One
switch is left, `-p:SwirlPays=false` (`Elements/TriggerRules.cs`), sim twin
`C.SWIRL_PAYS`, on to match since 2026-10-08 (#967) and compared by
`lint_constant_parity`. Next: phase two (Burning and
Dendro, `BACKLOG.md`).

## The Teyvat run frame: on hold

Built behind `TeyvatFrame`, off in every build; nothing deleted, no further
work (`operations/teyvat-frame.md`). [USER]: the first
draft "wasn't very interesting". It returns only as **elemental enemies**: a
short brief on elemental shields goes to [USER] when the kits are done.

## The Spiral Abyss mode: built, not yet played

The fourth menu mode (`review/active/spiral-abyss-pools-2026-10-12.md`) is
built under `klee-mod/KleeCode/Abyss/`: a "Spiral Abyss" button beside Custom
(solo and co-op host) opens the Custom screen with the `SpiralAbyss` modifier
ticked and locked; before each act's Ancient the run shows a page of three
Blessings, the enemies take one of the two passed Shadows on a seeded roll,
and all eight of each apply through the modifier's hooks, saved with the run.
Riptide was rewritten before the build ([USER], 2026-10-12): "Riptide sounds
insanely dangerous for enemies that open with a single very high hit as a block
check; the rest all look good." The act's element is Hydro, Pyro, Electro for
acts 1 to 3. Headless pins: `KleeTests/SpiralAbyssTests.cs`. Next: the live
check listed in the build PR, then one solo and one co-op seat on the mode.

## Live cell

A kit at Balance is measured on the real game (`EXPERIMENTS.md`, "Kit balance
is measured on the real game", ruled 2026-10-05); the sim stamps below do not
gate it. They describe the shipped world, and the calibration bands are retired
(2026-10-01, legacy cleanup pick 5). Stamps read live via `tier05/cells.py`
(`PILOT_WEIGHTS_VERSION` 6).

| stamp | value | source | what this value covers |
|---|---|---|---|
| `RT` `RUNTEMPLATE_VERSION` | **13** | `tier0/constants.py` | `EB-83`: Wood Carvings joins the act-1 event pool. |
| `D` `DRAFTER_VERSION` | **18** | `tier0/constants.py` | `EB-28`: Salon deploy priced through `STATIC_SALON_MEMBER_VALUE = 1.5`. |
| `P` `POLICY_VERSION` | **11** | `tier05/draft.py` | R207's scorer-literacy window. |
| `C` `CONSTANTS_VERSION` | **22** | `tier0/constants.py` | Undercurrent costs 1 (2026-09-25). |

The standing twelve-arm baseline (`review/records/sitting-reads-2026-08-26-c20-d18-p11.md`)
is an `RT12` read; its re-baseline (`EB-195`) is parked (`BACKLOG.md`).

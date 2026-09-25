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
**`MAJOR.AUTO`** with the `+proto` dev mark. **Installed: `0.2.3684+proto`**
(2026-09-18). Arms: `-p:PrototypeCards=true` (the three prototype kits),
`-p:FurinaStage=true` (the Stage), `-p:TeyvatFrame=true` (the frame); every
arm ships OFF in a release package. **Last release package: `0.2.1357`**
(2026-08-29).

## Roster

| id | display | HP | nation | element | stage | draftable pool |
|---|---|---|---|---|---|---|
| `klee` | Klee | 62 | Mondstadt | Pyro | Prototype | 49, to 48, then grows to 78 |
| `kokomi` | Sangonomiya Kokomi | 80 | Inazuma | Hydro | Prototype | 39 |
| `furina` | Furina | 78 | Fontaine | Hydro | Prototype | 26 (14 Stage cards) |

**Every kit's pool target is 78 standard draftable cards**, plus its Ancient
rewards and multiplayer cards; a smaller pool reads more reliable than it will
be. Starter basics are never changed.

## The three kits (Paper, then Prototype, then Balance; `operations/stage-gate.md`)

- **Klee: the kit works; finish it.** Brief
  `review/active/klee-brief-2026-09-01.md`. Next build: Tripwire, Explosive
  Frags, Where Did I Put It? and Big Bounce together; cut Long Fuse,
  Explosives Workshop, Sugar Rush, Kindling and Catalytic Converter; Hexerei
  becomes "Companion" (any companion card gives a Spark, and the three readers
  read any companion play); Sparks and the opening bank of 1 stay; the brief,
  relic and Ancient residue fixed. Then the pool grows toward 78. Done: two
  seats, then one full run by [USER] on a pool at or near 78; fun through act
  3 moves her to Balance.
- **Kokomi: Plan stays; the cards change.** Brief
  `review/active/kokomi-brief-2026-09-01.md`. New rule for the brief: the
  now-line answers this turn, the Plan line buys something only a head start
  can buy, never the same effect at two sizes. Next build: rewrite the 13
  same-effect-bigger Plan cards (Kurage's Oath included), re-aim the five
  per-Plan payoffs so at least half reward something other than volume, and
  every damaging card of hers applies Hydro (Skills too; basics unchanged).
  Pool stays 39 for this pass. Then two seats, then [USER] plays (a central
  rule changed).
- **Furina: the Stage, to playtest level.** Brief
  `review/active/furina-stage-brief-2026-09-08.md`. Next build: Spend needs
  the full price and a bow comes only from an exact emptying; Spend and the
  readers take from the back performer (the bank), the lead is the shield;
  about ten Stage cards (two or three Powers, two empty-stage answers, a
  Pneuma/Ousia Rare); her starter matches the brief (no companion cards);
  Ancient, drain-code and display residue fixed. Then two seats, then
  [USER]'s first Stage run.

All three prototypes start with no companion card. Whether each starts with
one comes back after the kits, with the reaction display (`EB-410`) and the
companion slot as a real draft choice.

## The Teyvat run frame: on hold

Built and behind `TeyvatFrame`, OFF in every release package; nothing
deleted, no further work. Six dressed faces (two nations per act), 122
dressed events, 149 dressed enemy slots, 27 music slots
(`operations/act-assets.md`, `operations/media.md`). It comes back only as
**elemental enemies**: when the three kits are done, a short brief on
elemental shields goes to [USER] before any build.

## Live cell

Measurement law binds only at Balance; nothing is there today, so
`EXPERIMENTS.md` is dormant. Stamps read live via `tier05/cells.py`
(`PILOT_WEIGHTS_VERSION` 6).

| stamp | value | source | what this value covers |
|---|---|---|---|
| `RT` `RUNTEMPLATE_VERSION` | **13** | `tier0/constants.py` | `EB-83`: Wood Carvings joins the act-1 event pool. |
| `D` `DRAFTER_VERSION` | **18** | `tier0/constants.py` | `EB-28`: Salon deploy priced through `STATIC_SALON_MEMBER_VALUE = 1.5`. |
| `P` `POLICY_VERSION` | **11** | `tier05/draft.py` | R207's scorer-literacy window. |
| `C` `CONSTANTS_VERSION` | **22** | `tier0/constants.py` | Undercurrent costs 1 (2026-09-25). |

The standing twelve-arm baseline (`review/records/sitting-reads-2026-08-26-c20-d18-p11.md`)
is an `RT12` read and owes a re-baseline (`BACKLOG.md` `EB-195`).


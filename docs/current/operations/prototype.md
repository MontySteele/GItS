## Prototype surface (`EB-147`) — quarantined, dev-only

`docs/prototype-surface.yaml` is ONE staging sheet for cards being TRIED, for
every character at once (each row names its owner with `character:`, and every
id starts `proto_`). A separate dev-only generator builds it; the default
generator run does not touch it.

**C# FIRST, sim at Balance.** A new kit rule is implemented in the C# mod
(`klee-mod/`) behind the prototype switch and nowhere else, and the Python sim
(tier0 / tier0.5) is brought up only once the rule survives the Prototype gate.
The switch is the MSBuild property `PrototypeCards`, which defines the
`PROTOTYPE_CARDS` compile constant
(`klee-mod/KleeCode/KleeCode.csproj:30-31`, mirrored for the headless tests at
`klee-mod/KleeTests/KleeTests.csproj:36-37`), driven by
`-p:PrototypeCards=true` on the build and by `klee-mod\build\deploy_proto.ps1`.
The sim's job before Balance is degenerate-loop and dead-card detection off the
sheet draft, which needs no engine mirror; a two-engine build before the rule
is settled is a tax on the stage that wants taste, not numbers.

```sh
.venv/Scripts/python tools/gen_prototype_cards.py           # emit the dev-only C#
.venv/Scripts/python tools/gen_prototype_cards.py --check   # staleness gate (CI lane)
dotnet build klee-mod/KleeCode -p:PrototypeCards=true       # the DEV build
```

**Deploying a dev build** — `klee-mod\build\deploy_proto.ps1`, from the
art-bearing main checkout, game closed. It is `deploy.ps1` plus three things:
`gen_prototype_cards.py --check` first, `-p:PrototypeCards=true` on the build,
and a package stamped `MAJOR.AUTO+proto` (`+proto.dirty` when dirty) so a dev
build is identifiable on sight. It runs the SAME `validate.ps1`, whole;
`-PrototypeBuild` relaxes exactly one rule — S3 accepts the `+proto` mark,
which every other path refuses by name. Prototype rows are off-pool, so
ordinary play is unchanged. **To restore the release build run
`klee-mod\build\deploy.ps1`**: it overwrites the same `mods\klee`, and the
absence of `+proto` in the in-game version is the confirmation. Do that before
any measured run, handoff or co-op session. No `-Package` switch, deliberately
— a dev build is never handed to a peer.
**After every dev deploy, run `python -m understudy.soak --runs 1 --character
KLEEMOD-KLEE --max-fights 3` and read `fights=3 defects=0` before any
registered run (R225).**

**A face may be on the ROW too** (`EB-215`). `gen_klee_cards` renders a card's
text from its BODY, and a Power's per POWER ID, which is what stops a shipped
face drifting from what the card does — so a prototype that rewrites a shipped
power's clause could not say so without moving the shipped card's face with
it. A row states its own face with `description:`, emitted into the same
`Localization` list every shipped row uses. There is no loc merge and no
second channel; `description:` is the prototype surface's field alone and no
`docs/*-cards.yaml` row may carry it.

**An upgrade is on the ROW** (`EB-213`). Shipped deltas live in
`docs/<character>-upgrades.yaml` keyed by shipped id; a `proto_` key there
would give the deletion rule below a second file to remember, so a prototype
row carries `upgrade: {<key>: <delta>}` itself. `gen_prototype_cards.py`
registers it into the merged delta index before emitting, and everything after
that is the shipped path — same expressibility check, same `OnUpgrade`, same
campfire — with `tier0/content/upgrades.py` merging the same block so both
engines read one place. A row that declares nothing is base-only; a declared
delta the emitter cannot express STOPS the run, like an inexpressible body.

**Staging a row** — edit the sheet, regen, dev-build, then grant it by id from
a scenario (`give: {card: KLEEMOD-PROTO_..., pile: hand}`); template and
preconditions in `understudy/scenarios/eb147-prototype-grant.yaml`. A row the
emitter cannot express STOPS the run by name: a prototype that cannot be
printed cannot be tried.

**A dev build also MIGRATES three shipped rows (`EB-218`, R224).** Under the
same flag pair — `C.SPARK_ALT_COST_ENABLED` in sim, `-p:PrototypeCards=true`
in C# — Klee's three hybrid Spark spenders (`powder_charge`, `hold_the_line`,
`smoke_and_sparks`) are swapped out of the offerable pool for Spark-only twins:
0 Energy, the same printed Spend 2, same rarity, same body. It rides
`C.SPARK_ALT_POOL_SUBS` like the other substitutions, so a dev build shows the
twins and a release build cannot reach them; flag off, the pool is
byte-identical to shipped (`tier0/tests/test_eb218_hybrid_migration.py`).

**A dev build can also REPLACE MONDSTADT'S COMPANION POOL.** Third arm, third
property, same terms as the second:

```sh
dotnet build klee-mod/KleeCode -p:PrototypeCards=true -p:CompanionOverhaul=true
klee-mod\build\deploy_proto.ps1 -KleeOverhaul -CompanionOverhaul   # both arms
```

`-p:CompanionOverhaul=true` defines `COMPANION_OVERHAUL`, which moves
`KleeMod.Powers.CompanionOverhaul.Enabled`; the sim twin is
`C.COMPANION_OVERHAUL`. With it on, the companion reward slot, the shop channel
and the Featured Banner all read the approved workshop's rewritten Mondstadt
Universals (`proto_mc_` rows, `C.MONDSTADT_OVERHAUL_POOL_IDS`) and the 17
shipped Mondstadt rows cannot be offered; Inazuma and Fontaine are untouched.
The seam is ONE property in each engine — `CompanionPool.All` and
`loader.companion_roster_replacement` — because the banner and the slot must
never read different rosters (R64). Flag off, both are byte-identical to
shipped (`tier0/tests/test_companion_overhaul.py`,
`klee-mod/KleeTests/Prototype/CompanionOverhaulTests.cs`). **Unlike the Klee
overhaul this arm is built in BOTH engines**, because it needed no new op: every
row is written in the grammar the sheets already speak and its nine powers ride
the two turn hooks the engine already runs.

**THE DELETION RULE (R213 B).** *Once a slice is accepted or rejected, its rows
LEAVE the surface.* Accepted rows are re-authored onto the owning character's
real sheet — ruled numbers, stamp bump, art — and deleted here in the same
commit; rejected rows are deleted outright, with the reasoning in the slice's
packet under `review/`, never as a commented-out row. **This is never a second
permanent pool**, and an empty file is the healthy state.

What the quarantine is: without `-p:PrototypeCards=true` the classes are not
compiled at all, so no release build, no pck and no ordinary run can reach one;
under the flag they go into each character's OFF-POOL list (in the pool so
`CardModel.Pool` resolves, out of `GetUnlockedCards` so no reward roll or
transform can produce one). The rows never enter tier0's card index, so no run
template, digest or balance report sees them, and the sheet is excluded by name
from `lint_sheet_stamp` and `card_distinctness_report` — **staging a row bumps
no stamp**. Still checked: the tier0 schema validators, the codegen,
`lint_generated_structure` and `lint_pool_membership`.
Depth: `docs/current/atlas/klee-mod-cards.md` §7.

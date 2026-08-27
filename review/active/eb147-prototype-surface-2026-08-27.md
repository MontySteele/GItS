# EB-147 — the quarantined prototype surface

**Built 2026-08-27 on `eb147-prototype-surface`. Authorised by R213 B
(`1050f67`). Nothing here changes a number on any existing sheet, and nothing
here is measurement evidence.**

---

## 1. What a prototype row is, in plain English

A prototype row is a card we want to **try**, not a card we are shipping.

Everything on `docs/klee-cards.yaml` and its siblings is ratified: its numbers
were ruled, its stamp was bumped, its art was commissioned, and a run measured
against it means something. That process is right for a card we believe in and
completely wrong for a card we are asking a question about. R213's diagnosis
was that every character had converged on "a bigger damage or Block number",
and the fix is to try things — which means we need somewhere to put a card
that is half an idea, play it once at the real game, and then most of the time
throw it away.

That is this surface. One file, `docs/prototype-surface.yaml`, for **every**
character at once; each row says which character it belongs to. Every id
starts `proto_`.

**A prototype row is deleted, not kept.** Once its slice is accepted or
rejected, its rows leave the file. Accepted means it gets re-authored onto the
owning character's real sheet — with ruled numbers, a stamp bump and art — and
deleted from here in the same commit. Rejected means deleted outright, with
the reasoning going into that slice's packet under `review/`, not into a
commented-out row here. **The healthy state of this file is empty**, and it is
empty today. If a row has sat here across two slices, that is a process defect,
not a backlog item.

## 2. How to stage one

Four steps.

1. **Write the row** into `docs/prototype-surface.yaml`. Minimum shape:

   ```yaml
   - id: proto_kokomi_tidecall     # must start proto_
     name: Tidecall (Prototype)
     character: kokomi             # klee | furina | kokomi
     cost: 1
     type: skill
     rarity: common
     effects:
       - {op: block, amount: 5}
       - {op: draw, amount: 1}
   ```

2. **Generate the C#**: `python tools/gen_prototype_cards.py`.
   If the emitter cannot express the row it **stops, by name, with the
   reason**. That is deliberate — a prototype that cannot be printed cannot be
   played, and a slice that reached [USER] with a card that does not exist is
   the failure this refusal prevents.

3. **Build a DEV build**:
   `dotnet build klee-mod/KleeCode -p:PrototypeCards=true`.
   Without that property the prototype classes are not compiled at all.

4. **Grant it by id** from a scenario:
   `give: {card: KLEEMOD-PROTO_KOKOMI_TIDECALL, pile: hand}`.
   Template: `understudy/scenarios/eb147-prototype-grant.yaml`.

Then, when the slice is graded: **delete the rows, regen, commit.**

## 3. The commands

```sh
python tools/gen_prototype_cards.py            # emit the dev-only C#
python tools/gen_prototype_cards.py --check    # staleness gate (now in the CI lane)
dotnet build klee-mod/KleeCode -p:PrototypeCards=true    # dev build
dotnet build klee-mod/KleeCode                           # release build: no prototypes
python -m understudy.scenario run understudy/scenarios/eb147-prototype-grant.yaml \
    --why "EB-147: does the grant door reach a quarantined row"
```

These are also written into `docs/current/OPERATIONS.md` under "Prototype
surface (`EB-147`)", together with the deletion rule; the deletion rule is
additionally the first thing in the sheet's own header.

## 4. What the quarantine actually is

R213 B lists six requirements. Each is a place in the code, and each has a
test. Nothing is enforced by discipline alone.

| R213 B asks for | Where it happens | Proved by |
|---|---|---|
| a separate prototype YAML, rows carrying their character | `docs/prototype-surface.yaml`; `loader.py:31` (`PROTOTYPE_SHEET`); `character:` required by `loader.prototype_cards` | `test_fixture_row_validates_under_the_card_schema`, `test_bad_prototype_rows_are_refused_by_name` |
| a dev-only codegen profile; the default run does not emit them | `tools/gen_prototype_cards.py` is a separate script; `PROFILES` / `PLAN_BUILDERS` untouched | `test_dev_profile_emits_the_row`, `test_default_generator_run_emits_no_prototype` |
| the emitted C# registers into no reward pool | `PrototypeCards.cs` (`#if PROTOTYPE_CARDS`) → each character's **off-pool** list, which `FilterThroughEpochs` strips from `GetUnlockedCards` | `test_prototype_cards_are_off_pool_in_every_character` |
| absent from reward pools, release packaging and ordinary runs | `KleeCode.csproj` `Compile Remove` unless `PrototypeCards=true`; rows never enter `loader._card_index` | `test_release_build_does_not_compile_the_prototype_classes`, `test_prototype_rows_never_enter_the_sim_card_index` |
| ignored by digests, balance reports, distinctness and stamps | one structural exclusion (out of `_card_index`) + two named ones: `lint_sheet_stamp.EXCLUDED`, `card_distinctness_report.EXCLUDED_SHEETS` | `test_version_stamps_cannot_see_the_prototype_surface`, `test_distinctness_report_cannot_see_the_prototype_surface` |
| still checked for schema, codegen and runtime legality | `loader.prototype_cards` runs `Card.from_dict` + the shipped validators; the codegen refuses an inexpressible row; `lint_generated_structure` and `lint_pool_membership` cover the emitted `.cs` | `test_an_inexpressible_prototype_row_stops_the_run`, `test_the_emitted_prototype_passes_the_structural_gate` |

The strongest of these is the compile exclusion. A shipped mod does not contain
the classes, so there is no id for a reward, a transform or a hand-typed
console entry to resolve. **Measured live**, with a fixture row staged:
`ProtoKokomiTidecall` is present in `klee.dll` after
`-p:PrototypeCards=true` and absent after a default build.

The second-strongest is that the rows never enter tier0's card index. That
index is the single thing every pool, run template, reward roll, digest and
balance report reads, so their exclusion needs no filter and no maintenance —
the rows simply are not there.

**Off-pool, not poolless.** A prototype IS in its character's pool, and that is
required rather than a compromise. `CardModel.Pool` falls through to
`MockCardPool` and throws `"You monster!"` in a shipped build, on **draw or
preview**, so a card in no pool crashes the moment a staged turn deals it. The
engine's own split — in `GenerateAllCards` so `Pool` resolves, out of
`GetUnlockedCards` so nothing can generate it — is the shape the kit cards and
the companions already use.

## 5. What is proven, and what is deferred

**Proven in this branch** (all green): the 20 tests in
`tier0/tests/test_prototype_surface.py`, the full suite, `run_lints --lane ci`
(23 lints), and both C# builds. Additionally proven by hand with a fixture row
staged and then reverted: the dev build compiles a real prototype card, the
default build of the same tree omits it from the DLL, all 23 CI lints stay
green (including `pool-membership`, which sees the card as pooled), the sheet
digest does not move, and the distinctness report does not see the sheet.

**Deferred: the live run.** `understudy/scenarios/eb147-prototype-grant.yaml`
is committed unrun — another lane owns the game today. It asks the smallest
question that matters: can a card in no pool, no release build and no stamp
still be put in a hand by id and played, with the numbers its row prints? If
the answer is no, every slice built on this surface is built on nothing, so it
should be the first thing run when the game is free. Its three preconditions
(stage the fixture, regen, dev-build) are written into its own header, with
the fixture row verbatim.

Running it once against a **default** build is a bonus proof of the quarantine
from the outside: the grant is refused because the id does not exist.

**A note on the fixture.** The shipped surface is EMPTY and the tests write a
temporary sheet per test. The alternative — a permanent clearly-marked fixture
row — was rejected because it is precisely the second permanent pool R213 B
forbids, one row deep, and it would be the row nobody ever deletes. The cost is
stated rather than hidden: with an empty surface the committed C# only proves
that an empty surface compiles, so the real-card compile is the manual step
recorded above rather than a suite assertion (the suite has no game assembly to
build against).

## 6. Names chosen, and what they were chosen over (R179)

All three are provisional and cosmetic; the lints proved so.

- **`docs/prototype-surface.yaml`** — over `docs/prototype-cards.yaml`. Not
  taste: `lint_sheet_stamp.PATTERNS` and `card_distinctness_report.SHEETS` both
  glob `docs/*-cards.yaml`, so the `-cards` spelling would have silently
  enrolled the surface in the stamp law and the distinctness instrument. Both
  tools now ALSO exclude the file by name, so a later rename cannot re-enrol it
  by accident — but the name is the first line of defence and should stay.
- **`PrototypeCards=true` / `PROTOTYPE_CARDS`** — over `-p:Dev=true` and
  `DEBUG`-style names. It says what it switches on rather than how important it
  is, and it cannot collide with a configuration name.
- **`KleeMod.Cards.Prototype.Generated`, `Cards/Prototype/Generated/`** — the
  existing `Cards/<Character>/Generated/` shape with `Prototype` where the
  character goes, which is what makes the one-line `Compile Remove` glob
  possible. Alternative considered: per-character `Cards/<Character>/Prototype/`,
  rejected because it needs three globs and three roster classes to say one
  thing.
- **The `proto_` id prefix** — chosen over "just check for collisions". Both
  are implemented; the prefix is the one that also makes the deletion rule
  greppable (`git grep proto_ docs/` answers "did the last slice leave?").

## 7. One thing that is [USER]'s, not mine

**Does the quarantine need a clause in `LAW.md`?** R213 said explicitly that
LAW was not amended by it and that the question returns at the sitting. My
read, offered as a pick and not a decision: the engineering makes a prototype
row *unable* to reach a stamp, so nothing in LAW is currently being relied on
for that. What LAW cannot say for us is the human half — that **no number
measured on a prototype row is ever quotable**, in a packet, a register or a
commit message, even informally. Guardrail-7 covers bot numbers and the
scenario harness carries its own no-comparison guardrail, but neither is
addressed to a prototype specifically. If you want that written down, it is a
one-sentence amendment and it is yours.

I also did **not** add a `slice:` field to the card schema (which would have
let the tooling answer "which rows belong to the slice being graded"). That is
a shared-surface change under R92-3b, needing a cross-session note, and the
deletion rule works without it — slice membership lives in the sheet's comments
and in each slice's packet. Worth revisiting only if a slice ever gets big
enough that a grep is not enough.

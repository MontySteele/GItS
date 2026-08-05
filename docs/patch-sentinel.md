# Patch sentinel

`tools/patch_sentinel.py` — built 2026-08-05 (Surplus Dispatch 2, S12).

## The problem it exists for

Every base-game number this project measures against came out of the DLL on
some particular day. Those extracts live in `game_ref/`, which is gitignored,
expensive to rebuild, and carries hand-written review layers on top of the
machine-generated rows — so in practice it is a **stored baseline**, not a
cache we re-derive.

Slay the Spire 2 patches. When MegaCrit moves a cost, a rarity, a starting
deck or a relic number, nothing in this repo fails. The baseline simply stops
describing the shipped game, and every anchor normalised against it quietly
becomes a claim about a version nobody is playing. That is a **silent** class
of defect, and this repo's standing answer to that class is to turn the catch
into a check that runs on its own.

The sentinel is the alarm. It re-extracts the watched surfaces from the DLL
that is installed **right now** and prints where they disagree.

## What it checks

| Surface | Baseline | Fields compared |
| --- | --- | --- |
| `cards` | `game_ref/<char>.json` for each canon pool that has one | every field the extractor records: cost, type, rarity, `vars`, `upgrades`, `cmds`, `generic_cmds`, `powers`, `orbs`, `keywords`, `target`, `exhaust`, `innate`, `mp_only`, `body_lines` — plus cards added to / removed from the pool |
| `characters` | `game_ref/<char>_char_facts.yaml` | `StartingHp`, starting-deck **size**, starting-relic **count** — all five canon characters since 2026-08-05 |
| `relics` | `.sentinel/relics.json`, blessed by the tool itself | rarity, printed `vars`, `cmds`, `generic_cmds`, `powers`, `orbs`, relic-pool membership, `body_lines` — plus relics added/removed |
| `dll` | `.sentinel/dll.json` | size + sha256 of the assembly |

The `dll` surface is the cheap one and the honest one: it fires when the game
patches **at all**, including patches that move something no other surface
watches.

## What it cannot see

Stating this plainly matters more than the table above, because a green
sentinel is otherwise easy to over-read.

- **Card and relic TEXT.** Never extracted, by design (IP rule, `.gitignore`
  line 28). A wording change, a clarification, a keyword rename in the
  localisation strings — all invisible here.
- **Behaviour that lives in method bodies.** The sentinel reads declarations
  and call vocabularies. If a patch changes *when* an effect fires without
  changing which commands are called or how many lines the file has, nothing
  moves. `body_lines` is a crude tripwire for exactly this, not a guarantee.
- **Anything with no baseline.** Potions, events, encounters, monsters, acts,
  enchantments, badges, map generation. The `characters` surface only watches
  characters that have a `char_facts` baseline; the `cards` surface
  only watches pools with a `game_ref/<char>.json`. Unwatched surfaces are
  reported as notes ("not watched"), never as clean.
- **What a starting relic DOES, for three of the five.** Cracked Core channels
  an orb, Bound Phylactery summons a pet, Divine Right grants Stars — tier0
  has none of those three concepts, so those sheets name the relic under
  `unmodelled_starting_relics` and the surface watches only that the COUNT is
  still one. If MegaCrit rewrote Cracked Core to channel two orbs, nothing
  here would move.
- **Anything on a CI runner.** No game install and no `game_ref/` there, so CI
  can only prove the tool runs.
- **Relics before the first bless.** No relic baseline existed anywhere in this
  repo, so the first run *establishes* one from whatever is installed that day
  and reports nothing. A relic patch that predates the first bless is already
  invisible and always will be.

## Running it

```
python tools/patch_sentinel.py                     # advisory report, exit 0
python tools/patch_sentinel.py --surfaces cards    # one surface
python tools/patch_sentinel.py --redact            # digests instead of names
python tools/patch_sentinel.py --json out.json     # machine-readable findings
python tools/patch_sentinel.py --bless             # re-take the snapshots
python tools/patch_sentinel.py --strict            # exit 1 on any drift
```

Needs `ilspycmd` and a local install; `klee-mod/local.props` supplies the game
path, same as the extractor. Set `GITS_ILSPY_TREE=<dir>` to reuse a decompiled
tree between runs instead of decompiling each time.

`--strict` exists for a future caller that wants a gate. **Nothing in CI may
use it**, and the "no game installed" path exits 0 even under `--strict` —
absence of the game is not drift.

## Reading the output

```
cards/Ironclad: 2 finding(s) -- 1 added, 1 changed
  upstream changed cards/Ironclad/<Name>.cost: baseline says 2, DLL says 1
  upstream ADDED cards/Ironclad/<Name>
```

Three things to know:

- **`schema` findings come first in importance.** They mean the baseline and
  the current extractor do not produce the same record shape — usually because
  our own extractor grew a field, not because the game changed. The tool then
  compares only the shared fields and says so, rather than reporting the whole
  pool as drifted.
- **A finding is a pair of values, never prose.** Card text is not read at any
  point, so a finding can only ever be a field name plus a number or a list.
- **`--redact` before you paste.** Entry names are base-game identifiers. They
  print in the terminal because a terminal is a local artifact; anything that
  lands in a doc, a ticket or a CI log should use `--redact`, which substitutes
  a stable `id#xxxxxxxx` digest that still compares across runs.

## The standing rule

> **Findings are alarms for a [USER]-gated pass. They are never auto-acted on.**

Nobody — human or agent — should react to a sentinel finding in the run that
discovers it. Upstream changing a number is not a bug report against whatever
work happens to be in flight, and "fix the drift" is not a well-defined action:
depending on the finding the right answer may be to re-extract a baseline, to
re-measure an anchor, to relabel every number taken before the patch, or to do
nothing at all. That is a ruling, and rulings are the user's.

The concrete protocol:

1. The sentinel reports. It changes nothing in `game_ref/` — it only ever
   writes `.sentinel/`, its own snapshots.
2. The findings go to the user with a count and a surface breakdown.
3. The user decides whether a re-baseline pass happens, and what it covers.
4. Only then does anyone re-run the extractor, and the pass records which
   measurements were taken pre-patch.

`--bless` is the one write, and it is the destructive one: it overwrites the
relic and DLL snapshots with the current game, which **erases** any relic drift
that had not yet been reviewed. Do not bless as a way of clearing a report.

## CI

Job `patch-sentinel` in `.github/workflows/repo.yml`, `continue-on-error: true`
and never a merge gate. It runs the synthetic-fixture tests for the diff core
and then invokes the tool, which prints `skipped -- no local game install`.
That skip is the correct result on a runner; the job's purpose is to catch an
import error or a broken CLI on the fresh clone, not to answer the question the
tool was built for. The real answer only exists on a machine that owns the
game.

## First run, 2026-08-05

Baselines in `game_ref/` (5 canon card pools, 2 character fact sheets) matched
the installed DLL field-for-field: **zero card findings, zero character
findings**. The relic and DLL snapshots were established on that run, so both
start from a clean slate by construction. Per the standing rule above, no
finding was acted on — there were none to act on.

## Character coverage completed, 2026-08-05 (R105)

`defect_char_facts.yaml`, `necrobinder_char_facts.yaml` and
`regent_char_facts.yaml` were written from the same decompiled read the other
two use, so the `characters` surface now watches **five of five** instead of
two. Re-run against the installed DLL on the day they landed: **zero
findings**.

| | HP | deck size | starting relics |
| --- | --- | --- | --- |
| Defect | 75 | 10 | 1 (Cracked Core — unmodelled) |
| Necrobinder | 66 | 10 | 1 (Bound Phylactery — unmodelled) |
| Regent | 75 | 10 | 1 (Divine Right — unmodelled) |

These three are **baseline only**: no sheet builder consumes them, there is no
`char_real_defect.yaml`, and no anchor is measured against them. They exist so
that a patch moving Necrobinder's 66 is loud instead of silent.

The third relic spelling, `unmodelled_starting_relics`, was added for them.
All three starting relics do something tier0 has no vocabulary for, and the
two alternatives were both worse: leave the sheets at zero relics and let the
sentinel manufacture a finding every run, or invent a hook name nothing
implements. Naming the relic keeps the count honest and the claim narrow.

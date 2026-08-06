# vendor/ — third-party source we carry, pinned

This directory did not exist before the Understudy sprint (2026-08-04). It is
opened by [USER] ruling 1 of `docs/archive/understudy-p0-findings.md`: *ADOPT STS2MCP
as a pinned vendored fork.* The house had no vendoring precedent, so the rules
below are the precedent, and they are deliberately narrow.

## What may live here

Third-party **source** that we build ourselves, under a license that permits
it, pinned to an exact upstream commit. Nothing else.

Explicitly not here, and each refusal is a decision:

- **No binaries.** `*.dll` is gitignored repo-wide and stays that way. A
  vendored component is source we compile; if we cannot compile it we do not
  carry it. (This is the whole force of ruling 1: the Nexus release binary
  0.4.0 predates our game build, and only source-from-HEAD matches it.)
- **No decompiled MegaCrit material.** `.gitignore` already refuses
  `sts2_decompiled/`, `game_assets/`, `game_ref/`. Vendoring is for other
  people's *published* source, not for the game's.
- **No copyleft that reaches our tree.** STS2-Agent was declined in P0 partly
  on AGPL-3.0; GItS is a public repo and that is a decision well above a
  sprint's pay grade. MIT/BSD/Apache-2.0 only, and the license file travels
  with the source.
- **No unpinned upstream.** "Latest" is not a version. R70 already paid for
  what unpinned build identity costs a lockstep co-op project.

## The shape every component takes

```
vendor/<Name>/
  PROVENANCE.md          <- upstream URL, pin sha, license, what we pruned,
                            what we changed, and how to refresh the pin
  UPSTREAM_MANIFEST.tsv  <- sha256 + status per carried file (generated)
  LICENSE                <- upstream's, verbatim, never edited
  <upstream files...>    <- byte-identical to the pin unless marked otherwise
  gits/                  <- OUR additions, never upstream's, every file
                            carrying a `GItS LOCAL ADDITION` header
```

Local edits to an upstream file are allowed but must be (a) marked in-file
with the literal `GItS LOCAL EDIT`, (b) listed in `PROVENANCE.md`, and (c)
recorded as `gits-modified` in the manifest. The default is zero of them;
today there is exactly one, and it is one line long.

## The gate

`tools/lint_vendor_pin.py` checks the curated claim in **both** directions —
the same pattern art_lint L11 and validate.ps1's `$pckDeferred` use, and for
the same reason. A manifest that only checked "the files I listed are still
there" would not notice a file quietly added to the tree, and prose alone
does not stop a snapshot from drifting off its pin. It is wired into CI and
into `tier0/tests/test_vendor_pin.py`.

Regenerate the manifest deliberately, never reflexively:

```
python tools/lint_vendor_pin.py --write
```

If that command's diff is larger than the change you meant to make, the
snapshot has drifted and the diff is the finding.

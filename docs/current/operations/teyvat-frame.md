## The Teyvat run frame: docs on hold

The frame is paused (`STATE.md`, "The Teyvat run frame: on hold"). Its code,
generators, tests and ledgers stay; its long operations docs were folded into
this pointer on 2026-10-08 (project review 2026-10-08, pick 3). The full text
is in git at commit `0bbcd8b8` (also tag `furina-v2-sim-slice-2026-10-08`):

```
git show 0bbcd8b8:docs/current/operations/media.md       # music + still portraits
git show 0bbcd8b8:docs/current/operations/act-assets.md  # act background, rest site, map art
git show 0bbcd8b8:docs/current/operations/codegen.md     # its three "Teyvat" sections
```

A code comment citing `media.md` sec.N, `act-assets.md` or the Teyvat parts of
`codegen.md` means that commit's text. What still holds today:

- Media is Tier F: files live in gitignored roots on the art-bearing main
  checkout; only the ledgers (`media/MUSIC.tsv`, `ACT.tsv`, `PORTRAITS.tsv`) and
  tools are tracked. Music slots per face: `combat`, `elite`, `boss`, `map`; global:
  `menu`, `shop`, `rest` (`tier0/tests/test_music_ledger_gate.py`).
- Generators, each with `--check`: `tools/gen_teyvat_events.py`,
  `tools/gen_teyvat_ancients.py`, `tools/gen_teyvat_creature_scenes.py`,
  `tools/gen_act_placeholders.py`; then `tools/build_pck.ps1`.

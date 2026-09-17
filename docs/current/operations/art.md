## Art pipeline

Tier F art never ships and never enters the repo; only the ledgers
(`art/SOURCES.tsv`, `art/plan.tsv`) and the tools are tracked.

```sh
python3 tools/art_fetch.py && python3 tools/art_process.py [--apply-picks art/picks.tsv]
python3 tools/art_coverage.py            # CI runs it WITHOUT --strict (empty bill on a runner)
python3 tools/art_hunt.py Furina ; python3 tools/art_contact_sheet.py --list
.venv/Scripts/python tools/cut_combat_layers.py klee [--check]
.venv/Scripts/python tools/cut_combat_layers.py --all [--check|--verify]   # 8 configs
.venv/Scripts/python tools/gen_furina_stills.py    # and gen_kokomi_stills.py
.venv/Scripts/python tools/gen_char_icon_outlines.py [--check]   # all three outline halos
.venv/Scripts/python tools/gen_mod_image.py [--check]      # Mods-screen badge, EB-161
```

`cut_combat_layers.py` cuts one illustration into layers behind a hand-digitized
fence config (`tools/combat_layer_fences/<name>.yaml`; `teyvat/<body>.yaml` are
the six bespoke boss rigs, `operations/codegen.md` §Bespoke rigs). `--check`
proves the shipped pixels are what the fences say; `--verify` stacks them back
up at their manifest offsets and diffs against the source, and GATES on that
for a config declaring `recompose_exact: true` — which the six do and configs
#1/#2 never claimed. `--art-root <checkout>` lets a worktree cut against the
main tree's `ImageGen/`, which is the only supported way to reach it (never
link an asset tree into a worktree).

`art/plan.tsv` is UTF-8, LF in the index (`.gitattributes` normalises) — read with `encoding="utf-8", newline=""` and
`rstrip("\r\n")`, or the last column silently stops matching. Depth:
`docs/current/art/` and `docs/current/atlas/tools.md`.

# pck-src — git-tracked text sources for klee.pck

Everything under this directory is copied verbatim into the pck work dir by
`tools/build_pck.ps1` (layout here == layout inside the pack: `klee/...`,
`furina/...`). It exists for text resources — scenes, materials — that are
too large or too editable to live as heredocs inside the build script;
the historical heredoc scenes stay in `build_pck.ps1` until they next need
editing (animation sprint 1 DECISIONS entry).

Rules:
- Text resources only (.tscn/.tres). Pixels stay in ImageGen (Tier F,
  gitignored); reference them by `res://` path — the build copies the PNGs
  in before MegaDot imports.
- NO scripts in scenes. Our assembly builds with plain Microsoft.NET.Sdk
  (no ScriptPath mapping), and the pipeline's standing rule is script-less
  packs: behavior attaches from C# (BaseLib scene conversion + Harmony
  routing), never from `ext_resource type="Script"`.
- Every shipped scene gets a `resource=` line in the contract list at the
  bottom of build_pck.ps1 — validate.ps1 S6c fails a deploy whose staged
  contract omits a source-referenced resource.
- One scene path = one conversion target. Never point two conversion
  registrations at the same .tscn (path-keyed registry; see the
  first-campfire softlock, DECISIONS 2026-07-20).

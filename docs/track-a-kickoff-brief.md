# Track A Kickoff Brief — Role×Tempo Taxonomy and Coverage Lint

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

For: local Code agent (Opus). From: chat session 2026-08-04.
Charter: `docs/axis-validity-session-charter.md` (v0.2, PROPOSED — read §3
before touching anything; this brief is the execution slice of Track A only).
Worktree-per-session (G4 = `SS-G4`). Suite green at every track boundary.

> **STATUS HEADER, added 2026-08-06 by the housekeeping sweep (Track X).**
> **EXECUTED 2026-08-04.** Doc of record for what actually happened is
> `docs/sprint-axis-validity-track-a-log-2026-08-04.md`; the rulings are R90
> (the null's direction), R91 (the tag review, discharging `A-G1`) and R92
> (housekeeping). This brief is **kept live, not archived**, because four
> `tools/` modules cite it by path in their docstrings as the origin of tasks
> `TA-T1`–`TA-T4` (`canon_role_tempo.py`, `suggest_role_tempo_tags.py`,
> `lint_role_tempo_coverage.py`, `role_tempo.py`). Read it as a historical
> execution slice: where it disagrees with the track log or with R90–R92, they
> win. Identifier resolver: `docs/registry/identifiers.md`.

## Standing context you need

- `solve:` already exists on all three sheets, multi-valued, vocabulary
  `frontload|scaling|block|sustain|velocity|utility`. You are EXTENDING it
  (add `support`; `aoe` becomes a modifier tag), not replacing it.
- `tempo_band:` is new: `fight: early|mid|late`, `run: early|late`,
  multi-band legal.
- Tag-through rule (charter A0.1): carriers inherit the roles their
  token/resource cashes into. A carrier inheriting nothing at a band is a
  finding, not a tagging failure — record it, don't force it.
- Floors-only lint; `utility` never linted, never split; floors per-identity
  from declared archetypes (R66: sheet header canonical).

## Work items, in order

**T1 — Canon baseline, DLL-verified.**
Extend `tools/extract_base_game_pool.py` / `build_official_sheet.py` to
emit all five characters from the local `sts2.dll` (game_ref/ stays
gitignored — outputs are local artifacts, never committed; the committed
deliverable is percentages and floors only, no card text). Cross-check
against the wiki-route classification the chat session ran (script logic
below); expect wiki ~4-high on raw counts, agreement on percentages. Flag
any card whose wiki text diverges from DLL text (monthly patches).

**T2 — Classifier + tagging pass.**
Port the chat session's regex classifier as a *first-pass suggester* only
(`tools/suggest_role_tempo_tags.py`): rules keyed on effect ops for GItS
sheets, on card text for canon. Known regex misses to fix from the chat
run: `$Dexterity`→block, `@IE/@SE/@ST` energy/star glyphs→velocity,
`$Plating`→block, "Another player"/"an ally"→support. Then apply
tag-through by hand-auditable table: token → roles it cashes into
(salon_member, guest_star, bomb, bake_kurage, fanfare, encore, charge).
Write suggested tags to a REVIEW column, not the sheet — [USER] gate A-G1
closes before tags land canonically.

**T3 — Baseline + floors.**
`docs/role-tempo-baseline.md`: (solve × tempo × rarity) matrix, all five
canon characters, percentages, per-identity. Machine-readable floors file
derived per declared archetype. Necrobinder is Furina's designated
summon-economy anchor — break his summon-payoff shape out explicitly.

**T4 — `tools/lint_role_tempo_coverage.py`.**
Fails a pool when a declared archetype is under-floor in a mandatory cell.
Floors-only (no card can fail). Joins the lint battery + CI. First run
grades the charter's pre-registered predictions P1/P2 — record grades in
the sprint log before reading anything else into the results. **P1's null
is binding:** if Furina's fanfare cells pass as authored, STOP, surface,
do not proceed to floors adjustment.

## Non-goals (hard)

No balance values move. No card is authored, reworked, or re-rarity'd. No
new keyword, op, or subsystem. No `combat_role` field — extend `solve`.
No drafter reads (DRAFTER 13 runs in parallel; you never touch prices).
No canon card text committed to the repo (IP rule, .gitignore:28).

## Instruments (D4)

Every prediction in this track names the lint or the baseline sheets as
its instrument — both see the change. Nothing here is sim-predicted;
support cells in particular are play-session-graded only and get NO
prediction registered in this track.

## Stop-and-surface

Tag-through ambiguities (a token whose payoff set is arguable), any cell
where per-identity floors would fail a canon character itself (that means
the floor derivation is wrong), and anything touching shared schema
(cross-session note required required before it lands).

# Animation Sprint 2 — Execution Log

Governing doc: docs/animation-sprint-2-plan.md. Opened 2026-07-24.
DECISIONS entry: "Animation sprint 2 opens: the Funnel Contract".
Predecessor: docs/animation-sprint-1-log.md (CLOSED 2026-07-24).

## Track A — Ledger, contract, art intake

Status: **COMPLETE.**

- A1 ✅ Sprint-1 log closed. B4 (Klee motion) and E4 (VFX timing) marked
  APPROVED 2026-07-24; both Klee layers are now FROZEN. No captures existed
  for either — recorded as "approved live, no capture", NOT backfilled, per
  the plan's explicit instruction. D4 (Salon), C4-Encore (gauge placement)
  and the badge-strip verdict recorded as FAILED with the *reasons* written
  out, since the reasons bind this sprint more than the verdicts do. A
  verdict table plus a forward pointer to this sprint sits at the foot of the
  sprint-1 log; every sprint-1 [USER] item is now struck through.
- A2 ✅ Funnel Contract written into klee-mod/DECISIONS.md, and the
  cross-session note pointer dropped in the Furina stream's channel
  (docs/furina-fanfare-sprint-log.md, "CROSS-SESSION NOTE IN"). The note
  states what the visual layer is bound to, what is explicitly free to
  change, and precisely what would require a note back — rather than asking
  the kit stream to do anything.
  - Checked while writing it: the kit stream's Track F-D (live C#) is **not
    started**, so `Powers/FurinaResources.cs` is untouched by that sprint
    today. This sprint edits its display call sites. Noted in both directions.
- A3a ✅ **Full-res source resolved; the risk branch did not fire.** The
  supplied 227×440 render is the Wikipedia article image
  (`File:Furina (Genshin Impact).png`). It is 227×440 at **both** en and zh
  wikipedia — fair-use reduced, and the zh credit chain terminates at a
  press-release article, so there is no full-resolution copy anywhere on that
  path. But the artwork *itself* is the official HoYoverse character-card
  render, and the repo has already held it at full resolution since the art
  sprint: **`art/raw/Furina_Card_2.png`, 1080×2160.** Identity confirmed on
  four independent features — closed calm smile (not the open grin of the
  sibling `Furina_Card.png`), black shorts (the sibling's are white), sword
  held down-left in her right hand, and the same coat-back spread. Wikipedia's
  copy is that render with the branded plate removed.
  - Consequence at intake: [USER] never has to choose between softness and a
    different render. **See B1 for the correction** — the cut ends up running
    off the WIKIPEDIA cutout, not the full-res twin, because that twin carries
    a branded plate behind the character and the shipped layers are downscaled
    to a 240x280 box anyway. The full-res twin is used for the B4 stills.
- A3b ✅ **Member art: only one viable source exists, and [USER] picked it.**
  A File:-namespace hunt returns **no individual full-body render** for any of
  the three members ("Gentilhomme Usher" → 2 unrelated hits, "Crabaletta" → 1,
  "Chevalmarin" → 21 hits all belonging to an unrelated amusement-park
  location). The gameplay preview GIF is 480×270 and unusable. The only asset
  in which the three read as three *different creatures* is
  **`art/raw/Salon_Members_Summon.png` (420×720)** — top-hatted octopus
  (Usher), ruffed seahorse (Chevalmarin), big crab (Crabaletta).
  - [USER] pick 2026-07-24 (contact sheet
    `docs/animation-sprint-2-a3-intake.png`): **cut that into three
    freestanding silhouettes.** No frames, no square crops.
  - Recorded for contrast, because it is the D4 failure in one line: what
    ships today is three 500×380 *gameplay screenshots* — a figure on a sand
    dune, an item on a stand, a speck on a green field. At combat scale they
    are three identical blue smudges. That is why D4 failed, and it is why
    silhouette-first is the redesign's premise rather than a style choice.

## Track B — Furina model rebuild

Status: **CODE COMPLETE — [USER] motion look pass pending (B5).**

- B1 ✅ **Cutter generalized, then Furina cut.** `tools/cut_klee_combat_layers.py`
  (one artwork, hard-coded) became `tools/cut_combat_layers.py <character>`
  reading `tools/combat_layer_fences/<character>.yaml`. Klee's fences are
  config #1 and `cut_combat_layers.py klee --check` re-cuts into a temp dir and
  diffs: **12/12 outputs byte-identical**, so the generalization provably did
  not disturb shipped art. The old single-purpose tool is deleted.
  - **Source choice, and a correction to the intake note.** A3a established
    that `Furina_Card_2.png` (1080x2160) is the full-res twin, and the intake
    write-up said the cut would run at 4.75x. On contact with the work that
    turned out to be the wrong call, and the reason is worth recording: the
    full-res twin has the **branded plate composited behind it** (logo,
    emblem, border), so cutting from it means first building a matte to strip
    that plate — and the two automatic mattes tried both failed. The
    **Wikipedia file is already a clean alpha cutout**, which is exactly what
    the cutter wants, and the shipped combat layers live in a 240x280 box, so
    227x440 → 280 tall is a **downscale (0.64x), not a compromise**. The
    full-res twin still earns its keep on B4's stills, which need crops rather
    than cutouts. Net: no quality lost anywhere, and a matte problem avoided.
  - Layers as shipped, z back→front: **coat_back / sword / body / hat**,
    matching the plan's proposal. The render is a SINGLE connected component —
    zero satellites — so the free-floater pass found nothing and every
    boundary is hand-fenced, exactly as the plan predicted for a clean cutout.
  - **Deviation, validated against the art (Klee's B1 precedent).** The sword
    layer is the hilt / guard / hydro-emblem assembly ONLY. The thin lower
    blade is a ~3px cyan line from (67,270) to (92,336) *embedded in the coat
    train with navy on both sides*; moving it independently would tear a 70px
    seam for an element two pixels wide at combat scale. It rides the coat
    instead, and the scene keeps sword and coat drifting in the SAME direction
    so hilt and blade never visibly shear apart. The bright ornate assembly is
    what the glow-pulse reads on, which is what the plan wanted from the
    "Dodoco-analog".
  - **Method note, recorded because eyeballing failed twice.** Digitising by
    eye put a seed in background and traced the blade running down-RIGHT when
    it runs down-LEFT. The shipped fences are MEASURED off the artwork: the
    leg/coat boundary is the first navy pixel scanning out from the leg centre
    column, and the sword's extent is the cyan-glow mask. Two leaks were then
    caught by the tool's own seed assertion (a corridor between the sword and
    coat fences; a join at her ankle where the coat column touches her sock)
    rather than by inspection — the assertion is doing real work.
  - Acceptance: the at-rest composite reads as the original artwork, and a
    worst-case displacement render (coat −6,+2 / sword −3,+2 / body +2,−2 /
    hat +4,−3) shows **no holes** — the fill-behind inpainting is sized right.
- B2 ✅ `pck-src/furina/model/combat.tscn` — she joins Klee on the git-tracked
  scene channel and comes OFF the build_pck.ps1 heredoc for her combat model.
  `Furina.CreateCustomVisuals` is now the same three-step loud-fallback chain
  Klee ships (combat.tscn → combat_model.png → null), and `CustomVisualPath`
  is `combat.tscn ?? combat_visuals.tscn`.
  - Scope note: the `combat_visuals.tscn` heredoc is **kept**, not deleted.
    The plan says "delete the heredocs" and in the same sentence says the
    static `combat_visuals.tscn` becomes "the loud-fallback chain exactly as
    Klee.cs ships" — those cannot both hold, and Klee's shipped chain keeps
    it. Kept the fallback; flagging the reading in case the intent was other.
  - The animation router needed **ZERO changes** to drive her rig, which is
    sprint-1's architecture paying out exactly as predicted.
- B3 ✅ Motion identity — theatrical, not bouncy. idle **3.5s**: poised body
  sway, coat counter-sway, hat micro-tilt (±0.026 rad on its own slower
  phase), sword glow-pulse + slight drift. attack **0.55s**: flourish lunge
  with contact at **0.15s = AttackAnimDelay**, coat and hat trailing the
  torso. hurt: recoil + **hydro-blue** flash on Body only (0.42, 0.78, 1.0) —
  explicitly not Klee's red. death **1.2s**: stage exit — a slight bow, a
  fall, a fade, terminal (death → End, no auto-return).
- B4 ✅ **Re-centred stills at every surface**, via `tools/gen_furina_stills.py`:
  combat_model.png (240x280 static fallback), select_portrait + locked
  (132x195), char_icon (88x88), map_marker (49x64), selection_splash
  (1920x1200). Every framing is computed from the render's **alpha bounding
  box, never the image frame** — which is the actual bug behind the off-centre
  complaint. The locked portrait is now the same crop as the unlocked one,
  desaturated and darkened, so the two cannot drift apart again (they were
  separate crops before). SOURCES.tsv rows for all six were **re-pointed** to
  the new provenance rather than left claiming the old one.
- B5 ⏳ **[USER] motion look pass** (same protocol as Klee's B4).

## Track C — Gauge re-layout + per-character skins

Status: **CODE COMPLETE — acceptance rides the B5/D5 playtest.**

- C1 ✅ **Overhead = Burst, everywhere.** The anchor is now a named constant
  (`OverheadBurstAnchor`, creature-space (0, −300)) with the convention
  written at the definition. A useful measurement fell out of B2: Klee's
  tallest layer tops out ~−277 and **Furina's rig tops out at exactly −280**,
  so the anchor Klee's C4 pass fixed clears her too with label room — the
  standardised slot needed no per-character tuning at all. Furina's Burst
  (max 70) now renders there. **Encore's overhead instantiation is REMOVED** —
  there is no Encore spec in GaugeBridge any more, and a comment at the
  deletion point says where it went and why.
- C2 ✅ **Parameter-driven skins, one scene.** `GaugeSpec` grew a `GaugeSkin`
  (fill colour, track colour, optional ribbon plate, optional cap-icon
  texture) applied at Setup. `gauge.tscn` gained the optional nodes those
  parameters drive: `%Ribbon` + `%RibbonTailL/R` (a banner with swallow-tail
  ends) and `%CapIcon`. Klee's skin is **fuse-and-bomb** — a warm fuse burning
  along a dark track toward a bomb cap (`klee/powers/bomb.png`). Furina's is
  the **hydro ribbon**, deliberately sharing its language with the D-track
  stage ribbon so her two hydro meters read as one family and neither reads
  as Klee's. Every skin node is optional in the scene, so an older pck renders
  a plain working bar instead of throwing.
  - **Decision logged per C2's instruction:** the scene-variant fallback
    (`gauge_klee.tscn` / `gauge_furina.tscn`) was **not needed**. Parameters
    reached far enough because the bridge can set any node property, including
    textures. The fallback stays pre-authorized if a future skin outgrows it.
- C3 ✅ Refresh funnels unchanged (contract §2). Burst's gauge refresh used to
  ride the now-retired badge apply, so it is explicit in `SyncMeters` — the
  overhead meter still tracks every sync moment.

## Track D — Salon stage (the D4 redesign)

Status: **CODE COMPLETE — [USER] layout/composition pass pending (D5),
capture mandatory.**

- D1 ✅ `pck-src/furina/ui/salon_stage.tscn` **replaces** `salon.tscn` (the old
  scene is deleted, not orphaned). A shallow stage arc with a lit lip sits
  beside Furina; three slot POSITIONS on the arc each hold a freestanding
  member mini-sprite — **no frame, no square crop**. Empty slot = ghost
  outline on the stage floor (the one sprint-1 idea that read, restyled to the
  stage language).
- D1a ✅ **Member sprites** (`tools/cut_salon_members.py`), from the
  [USER]-picked summon art. Hand-digitised silhouettes, after two automatic
  mattes failed (a row-median background model keys holes straight through the
  crab; a quadratic gradient fitted to known-background patches still calls
  72% of the card foreground, because the lavender lower background and the
  crab's white shell sit at the same luminance). **Usher** and **Chevalmarin**
  read cleanly at 72px on both light and dark backdrops.
  - ⚠️ **CRABALETTA IS THE WEAK ONE — flagged for D5.** She runs off the card
    frame on BOTH the right and the bottom, so a whole-creature silhouette is
    not extractable from this art. The full visible remainder was tried first
    and rejected: at stage scale it is a featureless pale blob. Shipped
    instead as her raised **claw**, which is unmistakably crustacean and
    cannot be confused with an octopus or a seahorse. It satisfies "three
    distinguishable silhouettes" but it is an object where the other two are
    creatures. If parity matters she needs better source art, and none exists
    on the wiki today.
- D2 ✅ States. Active: spotlight pool (soft ellipse) + subtle beam under the
  sprite. Dry (Encore below tick cost): pool and beam dim, sprite desaturates.
  Deploy: per-slot pop; the sprint-1 cascade queue survives (one
  AnimationPlayer, queued pops).
- D3 ✅ **Encore ribbon** beneath the arc, in C2's Furina skin — the members
  visibly stand ON their fuel. Drain to zero plays the flash pulse AND dims
  the whole stage (`%StageDim`), which is the causality the old layout could
  not show. Refresh sites: the contract §2 trio (gain/spend/absorb) plus
  `SyncMeters`.
- D4 ✅ `SalonVisualsBridge` reworked to **slot-index-keyed identity**, per
  Funnel Contract §1. `SalonMemberPower` gained a read-only `CompanyOf` (a
  copy, so a display can never mutate the company), and slot i renders
  whatever the company reports at index i. **Duplicates render as
  duplicates**; nothing assumes distinct members or in-order deploy. This
  retires sprint-1 D1's fixed member→slot assignment, which silently assumed
  both. Still GaugeBridge-skeleton, still RemoteTransform2D tracking, still
  the NCombatUi.Activate postfix, non-Furina guard intact.
- D5 ⏳ **[USER] layout/composition pass. Capture required.** The acceptance
  question is silhouette legibility at glance distance — and per the plan's
  own risk list, the pass must include **a three-of-one-member stage on
  purpose**, since duplicate rendering was never exercised before.

## Track E — Badge diet

Status: **DIET COMPLETE (E1/E3) — E2 icon pick OPEN, see below.**

- E1 ✅ Inventory and classification. Furina applied **three** meter badges:

  | badge | ambient home after C/D | verdict |
  |---|---|---|
  | `EncoreMeterPower` | the Salon stage ribbon (D3) | **RETIRE** |
  | `FurinaBurstMeterPower` | the overhead gauge (C1) | **RETIRE** |
  | `FanfareMeterPower` | none | **KEEP** |

  The rule is the Burst-badge precedent from sprint 1: a meter that gains an
  ambient home loses its badge, because two surfaces for one number is what
  made the strip unreadable. Both retired classes stay **registered** for save
  compatibility with mid-combat saves written before the retirement — the
  established pattern, not a new one.
- E3 ✅ **Count after diet: 3 → 1.** Fanfare is the sole keeper, and the
  parallel kit redesign demoting it to a read-only momentum stat makes a badge
  the *right* home for it rather than a consolation prize. No new
  player-visible label was added by this sprint, so no naming/lore surface
  arose; the retained Fanfare strings are unchanged and already audited.
- E2 ⏳ **OPEN — [USER] icon pick, and it needs sourcing first.** With one
  keeper the ask collapses to a single icon, but Furina has **no power-icon
  register of her own at all** (`ImageGen/images/furina/` has no `powers/`
  directory — which is precisely why her badges were borrowing Klee's). The
  natural register is her talent/constellation sigil set, which is
  purpose-built icon art; that is an art hunt plus a [USER] pick, and art
  picks are [USER]-gated by standing rule. Not invented unilaterally.

## Track F — VFX

- F1 ✅ `pck-src/furina/vfx/spotlight_shine.tscn` + `SpawnSpotlightShine`: a
  beam from above with a pool at her feet and rising motes, on the Spotlight
  **designation** event. Sprint-1 E-recipe verbatim — autoplay, self-freeing
  method track, 4s timer leak guard. The trigger sits inside
  `SpotlightSystem.Designate` **after** its early-out, so the beam marks an
  actual designation rather than a re-assert of the mode already in force.
  Contract §3 says designation is a single funnel, so one call covers every
  entry point and no spam guard is needed. The kit's signature moment had zero
  visual until now.
- F2 / F3 — **not started** (stretch, gated on A–E being green; E2 is open).

## Track G — Sprint-1 debt

- G1 ✅ `Vfx/TrackedDisplayBridge.cs` — the common skeleton, extracted AFTER
  D's rework landed so it covers the shape that ships rather than the dead one.
  It holds the keyed `Registry<TKey>` (IsInstanceValid staleness), `Spawn`
  (instantiate into CombatVfxContainer, warn once on a missing scene), and
  `Track` (RemoteTransform2D). Both bridges use it; what to read, what to draw
  and when to animate stayed in the concrete bridges. A skeleton, not a
  framework.
- G2 ✅ `KleeAnimationRouter` → **`CreatureAnimationRouter`** (file renamed via
  git mv, all references updated). Its doc comment now states the true scope:
  it serves every modded creature whose visuals carry an `%AnimationTree` —
  which Furina's rig proved by needing zero code changes.

## Two pre-existing blockers found and fixed on the way

Neither is sprint work; both silently blocked the deploy gate, so they are
recorded rather than quietly patched.

1. **`build/deploy.ps1` threw on EVERY invocation** since commit `1afee5d`
   ("Add -Package handoff zip"). That commit added a `[switch]$Package`
   parameter, and PowerShell variables are case-insensitive, so the
   pre-existing local `$package = Join-Path $root 'Klee'` was assigning a
   String to a SwitchParameter. Fixed by renaming the local to `$packageDir`,
   with a comment naming the collision.
2. **Validate S5 raised two false positives** that failed the gate, from
   commit `0b33ffd`. S5 scans whole source lines for BBCode; the line
   `[Cards.FurinaRiderTips.FanfareKey + ".title"] = ...` passes its loc-value
   filter on `.title"]`, and then `[Cards` reads as an unknown tag. Fixed by
   scanning **only string literals** — BBCode can only ever occur inside one.
   This removes a false-positive class without weakening the gate: a real
   `[Block]` inside any loc string is still caught.

Also noted, not changed: `validate.ps1` invokes `python -m tools.*` (S7a), so
the gate only resolves that module when run with the REPO ROOT as the working
directory. Run from `klee-mod/` it fails with a ModuleNotFoundError that reads
like a missing game_ref. Deploy from the repo root.

## Gates

- `dotnet build`: 0 errors.
- pck rebuilt, build id `20260724-194530+e3852e7`; contents verified — all of
  `furina/model/combat.tscn`, `furina/ui/salon_stage.tscn`,
  `furina/vfx/spotlight_shine.tscn`, the four Furina layer PNGs and the three
  member sprites are present, and the retired `furina/ui/salon.tscn` is gone.
- `validate.ps1` (via deploy, from the repo root): **OK** — all S-checks green.
- Full suite: **696 passed**.
- Deployed to the game directory.

## Open [USER] items

- **B5** — Furina motion look pass. The build is already deployed: boot and
  fight as Furina. Idle should read poised rather than bouncy (the hat tilt
  and the sword's glow pulse are the tells), the lunge should land with the
  damage numbers, hits should flash BLUE not red, and death should bow and
  fade once.
- **D5** — Salon stage layout/composition. **Capture mandatory.** Judge
  silhouette legibility at glance distance, and deploy **three of one member**
  deliberately to exercise duplicate rendering for the first time.
  Crabaletta's claw is the known weak silhouette — see D1a.
- **E2** — Furina's icon register for the one surviving badge (Fanfare).
  Needs an art hunt first; she has no power-icon register at all today.
- **F2** — Klee spark motes, [USER]-optional by origin. Not started.

---

# Track E follow-up — the icon register (2026-07-24, same day)

E2 asked for "Furina's icon for the one surviving badge". Answering it meant
sweeping the register, and the sweep found the badge strip was the small half
of the problem. Written up in full at `docs/icon-gap-2026-07-24.md`.

**What the sweep found.** Six powers had NO icon case at all and rendered the
base-game placeholder — the same gap the earlier companion sweep left behind,
missed because that sweep framed itself as "summons" and these are not
summons. Fifteen of Furina's powers wore Klee's textures. The number that
matters: **ten distinct Spotlight powers all rendered the same icon**, because
the switch matched the `SpotlightPower` BASE class, so the register only
*named* four of them and the count was never taken.

Two adjacent surfaces were checked and are clean: both relics resolve, and all
78 Furina card portraits resolve (the apparent 5-card gap is 2 roster helpers
and 3 guest cards whose art lives under `cards/companions/`). Klee's own kit
was already complete.

**Landed.** All 21 icons fetched from Furina's and the companions' own talent
and constellation sigils, processed, wired and deployed. `KleePowerIcons` now
names every power individually. The `SpotlightPower` base case is deliberately
GONE: a future subclass should fall to the placeholder, which reads as "no art
yet", rather than inherit a sibling's sigil, which reads as intentional.
`EncoreMeterPower` and `FurinaBurstMeterPower` were dropped from the register
entirely — E1 retired both as displays, nothing applies them, and they are now
listed in `KleePowerIcons.IconExempt` with the reason.

**Two structural defects found in passing, both pre-existing, both fixed.**

1. *Two producers claimed one out-path.* B4 moved Furina's six stills onto
   `gen_furina_stills.py` but left the five old `plan.tsv` rows live. Both
   halves bit: `art_fetch` rewrote their `SOURCES.tsv` provenance back to
   `Furina Profile.png` — a ledger that lied about where the shipped bytes
   came from, and it got COMMITTED that way — and the next `art_process` run
   would have silently overwritten the re-centred art with the old off-centre
   crops, undoing B4's own [USER] verdict. Caught by luck: a fetch happened to
   run. Rows retired, provenance restored, and **art_lint L11** now fails on
   any plan row whose out-path a generator owns. Verified by negative test
   that all three of its branches fire (collision, stale entry, missing
   generator) and that a clean plan stays clean. Proof the stills survived:
   re-running the generator reproduces all six shipped files byte-identically.

2. *`plan.tsv` was read as cp1252.* `read_plan` opened it with no explicit
   encoding, so on Windows the em dash in `Constellation Hear Me — Let Us
   Raise the Chalice of Love!.png` decoded to `â€"`, the mangled title went to
   the wiki API, and the row came back `MISSING on wiki` — which reads as a
   bad guess when the title was exactly right. Every non-ASCII wiki title has
   always failed this way here. Three opens now pass `encoding="utf-8"`.

**And a new boot check.** `KleeSelfCheck` **R13** reflects over every concrete
`PowerModel` in the assembly and fails if it has no icon mapping or names a
path absent from the merged pck. Neither half of this gap was visible to any
existing check, because a wrong or missing icon does not throw — it just
draws. R13 is what makes deleting the `SpotlightPower` base case safe.

**Gates.** Build 0 errors; pck rebuilt `20260724-202049+41cab5a`, 5.96 MB →
7.08 MB, all 15 Furina and 6 shared icons verified present inside the pack;
`validate: OK`; **740 passed**; deployed.

Note for the next run: `deploy.ps1` does NOT build the pck — it stages a
prebuilt `klee-mod/assets/klee.pck`. Run `tools/build_pck.ps1` first or you
will deploy yesterday's pack against today's dll, which is exactly what R13
would then report at boot. Also seen once: `tier05/tests/test_parallel_runs.py`
failed 3/5 when pytest ran under CPU contention from a concurrent pck build,
and passed cleanly in isolation and on a quiet re-run. Load-sensitive, not a
regression — but do not run the suite alongside a build.

## Open [USER] items after this pass

- **B5**, **D5**, **F2** — unchanged, see above.
- **E2** is now a PICK rather than a hunt. Seven icons are shortlisted on
  `art/contact_sheet_assets.html` (batch `assets`, native size): Fanfare
  itself, the four weak marks (Friendly Visit, Study Buddy, Standing Ovation,
  Ovation Trickle — these four have no good source and are flagged for
  re-hunt, not presented as good), plus Frozen and Shattering Pressure where
  there are two real options. Rank 1 is provisionally live for all seven.
  Export from the sheet, then
  `python tools/art_process.py --apply-picks art/picks.tsv`.
- **NEW, open:** should the ten Spotlight powers keep ten distinct icons, or
  share one family mark plus their own counters? Shipped as distinct on the
  sprint-1 reading that legibility failures came from indistinctness, but the
  opposite case is real at badge size, and the family relationship may be what
  a player needs to read first. Collapsing is a one-line change. Recorded as a
  choice, not decided.

---

# Playtest 1 (2026-07-25) — three defects from the live co-op run

First [USER] playtest of the deployed sprint-2 build (Furina + Klee co-op, pck
`20260724-210020+7260590`, confirmed from the run's own godot.log). Verdict on
the sprint as a whole was "graphical quality is much improved"; three specific
defects came back. All three are fixed below. None of the three was visible to
any existing gate, which is the through-line worth keeping.

## 1. "Ovation gauge had no numbers"

The Encore ribbon under the Salon stage. The number was NOT missing — the
bridge sets `%RibbonLabel` on every refresh and always has. It was being
DRAWN AND THEN COVERED.

The ribbon's value label hung *below* the ribbon at stage-local y 26..44. With
the stage anchored at creature-relative (-104, -30) that put the label at
creature y -4..+14 — under her feet, in the band `NCreatureStateDisplay` owns.
That band is not ours to draw in. Decompiling the layout confirms the collision
is structural, not a near miss:

- `NHealthBar.UpdateLayoutForCreatureBounds` spans the HP bar across the full
  bounds width, and Furina's `%Bounds` is 240 wide.
- The same method pins the block badge to `bounds.GlobalPosition.X - halfWidth`
  — the LEFT edge of that box. The Salon stage sits at x -104. They are the
  same piece of screen.

Fix, both halves in this pass: the label moved up ONTO the ribbon
(`salon_stage.tscn`, y 8..28, centered, font 12 -> 14, outline 4 -> 5), and the
whole stage lifted from y -30 to y -52 so no part of it reaches the state
display's band. Both are layout changes and both feed **D5**, which is still
open — the capture should now include a shot with Encore > 0 so the number is
in frame.

Why no gate caught it: every check we have asks whether a thing was *set*.
`%RibbonLabel` was set. Occlusion is a property of two subtrees that never
reference each other, and only one of them is ours.

## 2. Character icon shifted off its square

`character_icon.tscn` (both characters) was authored as a bare `TextureRect` at
a hardcoded 88x88 with default top-left anchors and zero offsets. That only
lands correctly if the game's slot happens to be exactly 88x88 with the same
origin. `Character.Icon` returns a `Control` that the game parents into its own
box, so the box's size is the game's business, not ours.

Fixed to full-rect anchors, so the icon adopts whatever box it is handed;
`stretch_mode = 5` (KEEP_ASPECT_CENTERED) keeps the art square inside it. A
`custom_minimum_size` of 88x88 is the floor — if a slot ever hands us a
zero-size parent, the icon stays 88x88 instead of collapsing to invisible,
which is the failure mode full-rect anchors introduce if you stop there.

Note the producer: these two scenes are heredocs in `tools/build_pck.ps1`, NOT
files in `pck-src`. Editing the copies under `dist/pck-work` would have been
silently reverted on the next build. Same one-producer-per-out-path rule the
Track E follow-up wrote down, hit from the other direction.

## 3. Characters do not turn to face their target

Reported against the Act 2 Kaiser Crab. That encounter is the one that breaks
the assumption: `KaiserCrabBoss.FullyCenterPlayers` is `true` and it fills
slots `crusher` and `rocket` on BOTH sides of the centered party. Attacking the
left one, the whole party lunged right.

This is a GAP, not a signal we failed to consume. Decompiling v0.107.1,
**nothing in the base game mirrors a creature**: `NCreature`,
`NCreatureVisuals`, `CreatureAnimator` and `NCombatRoom.PositionPlayersAndPets`
carry no facing, flip, or direction concept anywhere. Every base character is a
Spine skeleton drawn facing right, and with enemies always to the right that
has been sufficient. So there is no hook to consume — the behaviour has to be
built, and it is ours to build because the rigs are ours.

Shipped as `KleeCode/Vfx/CreatureFacing.cs`. Three decisions worth keeping:

- **The mirror is on a new `%Facing` node, not on `%Rig`.** The rig is
  animated, and `Visuals/Facing/Rig:position` carries the attack lunge. A
  node's own position track is expressed in its PARENT's space, so mirroring
  the rig would flip the art and leave the lunge travelling right — a moonwalk.
  The pivot goes above the animated node so the travel mirrors too. Both combat
  scenes were re-parented and all track paths rewritten (`Visuals/Rig` ->
  `Visuals/Facing/Rig`; 29 tracks Furina, 25 Klee).
- **Not `Visuals.Scale`.** NCreature owns that — `ScaleTo`,
  `SetDefaultScaleTo`, `OstyScaleToSize` all write it and `UpdateBounds` reads
  it back to place the hitbox and intent. A sign flip there inverts the hitbox.
- **The hook is a prefix on `AttackCommand.Execute`, not on the damage
  funnel.** `CreatureCmd.Damage`'s six-argument overload is the single funnel
  every damage path reaches (all nine overloads delegate to it) and it carries
  both dealer and targets, so it looks like the obvious choice — but `Execute`
  awaits `CreatureCmd.TriggerAnim` BEFORE dealing damage. Turning there would
  flip the sprite at the moment of impact, after the character had already
  lunged the wrong way. That is worse than not turning at all. The cost of
  turning at wind-up instead is one reflected private method
  (`AttackCommand.GetPossibleTargets`), cached, with a one-shot warning and a
  no-op fallback if a future version removes it.

Facing is the mean of the live targets' x, not `targets[0]`: a centered
encounter is precisely where an AoE spans both sides, and picking the first
would make the turn depend on iteration order rather than on where the damage
goes. A 24px dead zone keeps self-targets and stacked creatures from twitching.

Scoped by construction: `%Facing` exists only in our convention scenes, so
every base creature and every other mod's is untouched and the lookup returns
null.

**[USER] ruling, 2026-07-25 — accepted as first pass.** "As long as the art
flips 180 (so you can tell which enemy you're pointed at), I think that passes
for a first-pass attempt." A horizontal mirror is what shipped, so the bar is
met. Two consequences of hooking the attack rather than the targeting cursor,
both left as-is under this ruling: the turn PERSISTS (she faces the last thing
she hit; there is no return-to-neutral), and non-damaging plays do not turn her
at all. Pointing at the hovered target would track intent more tightly at the
cost of swinging back and forth while the player is still choosing a card —
not attempted, recorded as the alternative if the crab fight argues for it.

**This one wants a [USER] look**, and it belongs to **B5** rather than being
its own gate — it changes what the attack animation does. Klee attacking left
mirrors Dodoco to her other side; whether that reads as "turned around" or as
"the wrong Klee" is a taste call, and the crab fight is the place to judge it.

## New boot check: a bridge's node contract

All three defects share a shape with the Track E icon gap: a bridge written to
be inert when its node is missing (`GetNodeOrNull`, no throw) has the right
runtime posture and the wrong debugging one. A dropped or renamed node turns
the feature off and looks exactly like "the feature does nothing".

`KleeSceneTelemetry` now carries a `RequiredNodes` list and warns at boot for
any convention scene missing a node a bridge depends on — `%Facing` and
`%AnimationTree` in both combat scenes, `%RibbonLabel` in the Salon stage,
`%ValueLabel` in the shared gauge. Read from `SceneState`, so it stays
side-effect free and does not instantiate (which would trip BaseLib's
conversion postfix — the reason that file never instantiates anything).

## Gates

Build 0 errors. `validate` S1-S6 pass. **Not deployed**: the game was running
during this pass and `deploy.ps1` refuses while it holds the dll. The pck IS
rebuilt (`20260725-000439+7260590`, 7,083,856 bytes) and carries all three
scene changes. Run `klee-mod\build\deploy.ps1` from the repo root once the game
is closed.

`validate` S7 is red on 2 pytest failures in `tier05/tests/test_runner.py`
(`kurage_traces`). These are NOT from this pass — this pass touched no Python.
They come from a Kokomi telemetry change that is uncommitted in the working
tree from a parallel session (`tier05/kurage_telemetry.py` untracked,
`tier05/runner.py` modified); the failing line is a `+` line in that diff. Left
alone rather than fixed from here.

## Also found, not fixed: three card arts are missing

The playtest log carries three `No card art at ...` warnings that predate this
pass: `spotlight_center_stage.png`, `spotlight_guest_cast.png`,
`confiscated.png`. Those cards are rendering the BETA placeholder. This
corrects the Track E gap list, which recorded card art as clean — that sweep
checked that every card RESOLVES a portrait path through the register, which is
a different question from whether the file is on disk. Needs a plan.tsv row and
a hunt; not started.

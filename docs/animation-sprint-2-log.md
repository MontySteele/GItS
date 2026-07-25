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

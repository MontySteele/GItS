# Companion art pass — pipeline + plan.tsv addendum (2026-07-21, chat + user)

Method: chat hunted sources and built contact sheets + crop prototypes;
user did eyes-on. This doc carries the AUTO defaults (mechanical, chat) and
marks every taste call as USER-OWED (chat can't vibe-check newer
companions — Dahlia/Prune/Durin postdate its knowledge).

## 1. New pipeline capability: `cover_autocrop` mode + autocrop_card_art.py

tools/autocrop_card_art.py (landed) turns splash/Wish art (float-in-void,
~2048x1024) into card-filling art. Two alpha thresholds: high (~200) finds
the opaque FIGURE and centers on it; low (~10) includes faint FX so the
splash isn't clipped. Sources > card size => pure downscale, no quality
loss. Validated: v2 figure-centering visibly recentered Kaeya (was pulled
right by an ice-blade); left already-centered figures (Neuvillette, Diona)
untouched — correct behavior.

Asks for the Code session:
- Add `cover_autocrop` as a plan.tsv MODE alongside cover/contain/raw.
  Register-gate it: splash/wish/tcg registers only; NEVER item icons
  (those stay `contain`).
- Default margin **6% (tight)**. User reviewed tight vs 14% on the full
  set; tight wins everywhere (medium only adds dead canvas — wide-FX chars
  fill the frame at tight, compact chars are identical). Keep margin a
  param; 6% is the default, not a constant.
- Thin-FX tips (Barbara's staff, Bennett's flare) MAY clip the frame edge
  by design — that's a wisp, not the figure. Do not widen the frame to
  chase them.

## 2. Companion register decision (USER-RATIFIED): Wish art, COVER-autocropped

The 16 companions use their **Wish splash**, `cover_autocrop` with **fit:
cover** (fill the frame, crop overflow), EXCEPT the contain-fallback list
below. Rationale: cover makes the figure large and card-filling by
reclaiming the aspect-ratio dead space that `contain` leaves as
transparent bands; user reviewed contain-vs-cover on the lopsided cases
and ruled cover the default ("bigger figures"). This is the deliberate
"companions feel like a reward" look. (Supersedes both the round-1
frameless-Portrait lean AND the interim contain default — the progression
was Portrait -> contain-Wish -> cover-Wish as the crop got smarter.)

Pipeline: `cover_autocrop` gains a **fit: cover|contain** flag,
defaulting to cover. Cover scales to fill 500x380 and center-crops on the
FIGURE (high-alpha center), so overflow trims peripheral splash, not the
character. Margin flag still applies (6%) but matters less under cover.

### Clip-severity scan (chat, mechanical) — a POINTER, not a verdict
Measures how much of the content envelope overflows under cover. HIGH
overflow usually = trimming empty margin / FX tips, NOT the figure
(Chevreuse scanned 24% but renders great). Use it to decide WHERE to look,
then eyeball:
  - Low (<12%, cover safe, chat-cleared): Albedo, Bennett, Diona, Freminet,
    Kaeya, Nicole, Sucrose.
  - Flagged for a look (>12% overflow — MOST are fine, confirm by eye):
    Barbara (21%h — the musical staff is the real clip risk, clearest
    contain candidate), Charlotte (24%h), Chevreuse (24%h — renders fine),
    Dahlia (17%h), Fischl (26%h), Lynette (19%h), Neuvillette (18%w —
    renders fine), Prune (16%h), Durin (21%w).

### Contain-fallback list (USER-RATIFIED 2026-07-21)
Default is **cover** for all 16 companions EXCEPT:
  - **Dahlia — CONTAIN.** Cover clips his head/hat offscreen; contain
    keeps the full figure. The one confirmed figure-clip in the set.
All other flagged characters (Barbara, Durin, Prune, Chevreuse,
Neuvillette, Charlotte, Fischl, Lynette) PASS the user's taste test on
cover — the clip-severity "REVIEW" flags were envelope/FX-tip overflow,
not figure clipping, exactly as noted. Barbara's staff clip is accepted
as dynamic. Characters outside chat's knowledge window (Dahlia handled
above, Durin/Prune) are user-confirmed on-model.

## 3. Per-card differentiation (multi-card characters)

Chevreuse/Lynette/Charlotte/Freminet/Neuvillette have 3 cards each;
several others have 2. One strong source per character; differentiate
sibling cards by CROP (full-body on the signature card, tighter
bust-crops on the others), NOT by dragging in a weaker second source.
Dedupe lint: same-source-different-crop WITHIN one character is LEGAL
(sibling cards of one companion are meant to share a look); the lint's
cross-card collision rule targets DIFFERENT cards that should feel
distinct. Add that carve-out when the dedupe lint lands.

## 4. Klee splash re-process (USER-APPROVED: apply everywhere)

`cover_autocrop` retroactively improves the Klee splash keeps that also
float-in-void. Re-process (was `cover`, becomes `cover_autocrop` @ 6%):
- elemental_ecstasy/"Sweet Dreams" (Birthday 2025)
- big_badda_boom (Klee Wish)
- sparkly_explosion (Birthday 2021) [round-2 keep]
- any other splash/birthday-register Klee card the mode's register-gate
  catches — the session should sweep, not hand-list.
Item-icon cards (contain) are untouched. Re-render is deterministic; no
new taste pass needed unless a crop lands badly (flag if so).

## 5. Deferred Klee companion-synergy cards (from round 2) — now unblockable

best_friends_forever / borrowed_brilliance / study_buddy / friendly_visit
were deferred to THIS pass because they should depict companions. With the
companion Wish sources now fetched, they can draw from the relevant
companion's autocropped art (e.g. a Klee+companion pairing, or the copied
companion's splash). Still USER taste — list them for the same eyes-on
batch. friendly_visit's earlier source 404'd; use a companion source
instead.

## Open / owed summary
- USER: the 4 Portrait-fallback taste calls (Durin/Dahlia/Prune/Chevreuse/
  Neuvillette) + the 4 synergy-card companion pairings.
- CODE: cover_autocrop mode + register gate; dedupe same-source-crop
  carve-out; Klee splash re-sweep; render companion rows once calls land.
- Nothing here blocks the build sequence.

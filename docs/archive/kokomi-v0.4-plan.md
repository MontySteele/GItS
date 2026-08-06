# Kokomi v0.4 — O4 Salvage + Lore Overlay (GOVERNING PLAN)

> **Lifecycle: ARCHIVED** — superseded; kept verbatim as a record and never updated. Status index: `docs/registry/identifiers.md` §15.

**Status:** [USER]-ratified 2026-07-26; handed to the Kokomi Code
workstream. The plan text below is the design-chat output archived
verbatim (§0–§6). The ruling answers to §5 are recorded in
"§7 Rulings as given" at the bottom — that section is the authority where
it and the draft text disagree.

**OVERLAY, NOT REPLACEMENT.** The v0.3 charge-curve world executed and is
the base: Regent-shape commons, the riptide reader (renamed in §3), the
divisor /2, the starter S3 swaps, and the R53 Strike-parity basic all
STAND. This plan lands targeted deltas on top. No wholesale revert
anywhere in this doc.

---

## 0. Governing inputs

R51 (elite axes A2+A6, stability band, debuff texture), R52 (batch
closure), R53 (Strike-parity basic; v0.3 committed AS PROPOSED with an
identity-divergence flag).

Sheetpass report v0.2/v0.3, esp. §6.4 (A2>A1 violated + TOO_STRONG by the
fast-cycle Garment) and §6.5 watchlists (Garment uptime permanence; priest
pilot regret 15.1%).

This session's rulings-in-principle: **O1 REJECTED** (instrument
redefinition / post-hoc re-declaration — R33 culture), **O2 = reserve
fallback** (splash 7 / turns 2), **O4 = primary arm** (below).

Standing rules: one variable per window; cross-session worknote before any
shared-loader/schema change; naming audit is [USER]-only; KNOB_READS; dose
cells are diagnostics (R14).

## 1. The O4 thesis (mechanics)

The v0.3 rescue worked by making the Burst a **metronome** — guaranteed
periodic output, which the instrument correctly reads as frontload and
which borrows Furina's structural answer. O4 moves the periodic output to
where canon keeps it, and returns the Burst to a window:

1. **Bake-Kurage becomes a persistent summon.** Replaces the one-shot
   basic's body: play it, the jellyfish takes the field for D turns
   (`KURAGE_DURATION`, propose 3) and pulses at turn end: deal
   (`KURAGE_PULSE_BASE` 2 + Charge/`KURAGE_PULSE_DIVISOR` 4) to a random
   enemy, apply hydro, and grant `KURAGE_PULSE_BLOCK` 2 Block (party-wide
   in co-op). The pulse reads the bank — small early, growing all fight:
   an A2 signature delivering the fight-1 survival math that meter 10 was
   buying. Card keeps +1 Charge on play. All five constants are knobs.
   - *Engine:* Salon-member summon precedent; new op `summon_kurage` +
     pulse hook. Worknote REQUIRED before landing (shared schema).
   - *Skittish note:* the pulse eats the first-hit gate some turns; her
     multi-hit turns (pulse + shoal + attacks) are the real answer — no
     special-casing.
2. **Meter returns toward a real Burst.** Re-open the bracket at
   **15 / 20 / 25** on the O4 world (the v0.3 grid's 10 is the floor
   comparator, not an arm). Canon check on record: her burst is expensive
   and hard-funded — burst-reliant damage with low energy generation is
   her documented profile; a metronome is anti-canon, a costly window is
   canon.
3. **Ceremonial Garment gains the canon riders** (state unchanged
   otherwise):
   - While the Garment holds, her attack cards also grant
     `GARMENT_ATTACK_BLOCK` 2 Block (party-wide in co-op) — her burst's
     actual behaviour (attacks damage AND restore the party), translated
     under the healing law via the Charlotte precedent. Feeds the
     stability band exactly where R51 put the healer fantasy.
   - **Tamakushi Casket link** (canon A1 passive): casting the Garment
     while the Kurage is fielded refreshes the Kurage's duration. The
     E↔Q loop, verbatim.
4. **Relic rename** (consequence of 3): the starting relic currently wears
   "Tamakushi Casket" but carries the conversion laws. The name moves to
   the Garment↔Kurage refresh where canon puts it; the relic becomes
   **"Everlasting Moonglow"** (her signature catalyst; held-item fiction)
   — alt candidate "Pearl of Wisdom". [USER] picks at audit. Mechanics of
   the relic unchanged (exhaust→Charge, Strength→Charge).

## 2. Measurement plan (windows, in order)

- **W1 — priest pilot audit.** INSTRUMENT, NO CARD CHANGES. Regret doubled
  7.7→15.1% in v0.3; audit reader/burn ordering (riptide-class reads vs
  exhaust sequencing) and Garment-window play. Any pilot fix lands and the
  v0.3 world is RE-MEASURED once so W2 has a clean baseline. (Some of
  priest-32% vs commander-49% may be misplay; do not tune cards against a
  misplaying pilot.)
- **W2 — the O4 arm.** Kurage summon + Garment riders + meter bracket
  15/20/25, 300 runs/plan minimum, priest + commander, then 500-run
  confirm on the chosen meter. Pre-registered predictions: (a) starter A1
  falls below A2; (b) TOO_STRONG clears at archetype median; (c) act-1
  clear lands 35–50% at meter 20–25; (d) the Garment-uptime watchlist
  retires by construction. Misses on (a)/(b) at every meter step → fall
  back to O2 and the constraint conversation becomes honest.
- **W3 — lore overlay lands** (renames + flavor voice + pool gloss).
  Measurement-neutral by construction: display names and comments only;
  ids stay stable EXCEPT `riptide_strike` (see §3), which renames id-level
  before W2 so the arm is born with the right name. Lints re-run
  (unique-names, strict-domination, decksize).

## 3. Lore overlay (this session's lore-pass outputs)

**The rotation reframe (voice law for the sheet).** Exhaust in her fiction
is ROTATION, never sacrifice: units rotate off the field, rested and
whole; Charge is the strategic position each executed maneuver buys. Her
doctrine is minimal casualties; the sacrifice voice is the one reading
that breaks the character. Sweep every comment and future card face for it
(`grand_conscription`'s "the army becomes fuel" is the marked example).
`tactical_recall` is the exemplar voice.

**The conscription rename family.** Forced service is Shogunate behaviour;
the resistance were volunteers. Op name `conscript` stays (internal);
display family moves to Muster/Enlist/Rally:

- `conscription_notice` → "Call to Arms"
- `to_the_front` → keeps name (an order, not an imposition)
- `mass_mobilization` → "Rally the Isles"
- `grand_conscription` → "General Muster of Watatsumi"
- `field_promotion`, `reinforcements` → keep (already rotation-voiced).

**The pool is the peace, not her army** (framing note in the companion
sheet header). The roster spans every Inazuma faction — resistance
(Gorou), Shogunate (Sara, Raiden), Yashiro (Thoma, Sayu's Shuumatsuban),
Arataki Gang (Itto, Shinobu) — post-Decree Inazuma answering Watatsumi's
call. This explains the non-resistance names, sharpens Sara (the opposing
field commander, now allied), and gives Raiden her best gloss.

**Raiden gloss flips from irony to reconciliation.** Musou no Hitotachi is
the Vision Hunt's execution strike; "bitterest irony" has her fishing for
the weapon that killed her people. New gloss: the peace's crowning proof —
the Shogun's blade defends Watatsumi now. [USER] decides at audit whether
the card keeps the execution art's name or takes a less charged Raiden
move; both framings defensible, the irony one retired.

**Renames** (candidates; naming audit is [USER]-only):

- `riptide_strike` → `all_streams_flow` ("All Streams Flow to the Sea") —
  **MANDATORY-CLASS**: Riptide is Tartaglia's signature mechanic, a
  cross-character collision inside Genshin. Her C5 name means exactly what
  the card does. Id-level rename, before W2.
- `jade_bulwark` → "Pearl Bulwark" (jade is Liyue-coded; Watatsumi is
  coral and pearl).
- The "of the Deep" triple (mercy/vigil/epiphany): vary the family —
  candidates "Mercy of the Currents", vigil keeps (it's the ward's name
  and it's earned), `epiphany_of_the_deep` → "Pearl of Wisdom" IF the
  relic doesn't take it.
- `sayu_yoohoo_windwheel` → "Sayu — Yoohoo Art: Fuuin Dash" (formal art
  name).
- `depths_judgment`: "Judgment" is Fontaine-coded; candidate "Sango
  Isshin" — verify against wiki at audit.

**Header audit ask:** the sheet's "verified" list includes "The Moon's
Beauty," which did not corroborate; re-verify the whole verified-names
header against the wiki. The wiki is the instrument, not anyone's memory
(mine misfired on her C2 this session).

**Private-characterization renames** (user direction, this session): two
support cards trade simplistic external names for the private Kokomi — the
drained introvert, the secret novel reader, the wish for quiet. Both are
flavor-layer only; effects unchanged:

- `tide_reading` → "Stolen Chapter" (Block 2, draw 1: she steals a moment
  with the book she'd never admit to; the draw IS the page).
- `moon_signal` → "A Moment Alone" (0-cost cycle: the social battery
  resets — set down the noise, recover one clear thought).
- Optional third if the audit wants it: `undertow_shuffle` → "Daydream of
  a Quiet Life" (draw 3 discard 2: the life she imagines, mostly let go).
  Offered, not required.

**Affirmed as-is** (for the audit's speed): Bake-Kurage, Water's Edge,
Sango Prayer, Gorou's banner identity + always-enlists (R52 N3),
Muji-Muji Daruma, Sanctifying Ring, Blazing Barrier, Crimson Ooyoroi,
Tengu Stormcall, Superlative Superstrength, and Sara's Stormcall as the
deliberate Flawless Strategy exerciser (the "Sara's buffs are wasted on
Kokomi" truism, mirrored).

## 4. Non-goals

- No revert of v0.3 numbers outside the meter bracket (R53 basic stays 6;
  Regent commons stay; divisor /2 stays unless W2 says the Kurage pulse +
  divisor together run hot — then divisor is the FIRST knob back,
  pre-registered here).
- No healing amendment (R52: none planned, ever).
- No taunt/redirect op (Itto's logged gap stays logged).
- No art/animation (Garment/Kurage showpieces go to the animation sprint's
  queue as candidates only).
- No act-2/3 weight-setting (A3 constants stay gated at freeze).

## 5. Ruling asks

1. Ratify O1 rejected / O2 reserve / O4 primary, and the W1→W2→W3
   sequencing.
2. Kurage constants + Garment riders as knobs (KNOB_READS: every constant
   above is named and exercised).
3. Meter bracket 15/20/25 for W2; chosen meter ratified on the 500-run
   confirm.
4. §3 renames incl. the two private-characterization cards (and whether
   the optional third lands); Raiden gloss + name disposition;
   relic/Tamakushi swap.
5. Prediction (c)'s acceptance band 35–50%: confirm this is the target
   neighborhood, with anchors (Furina 57 / IC 59) as the ceiling-side
   reference, not the requirement.

## 6. Definition of done

W1 pilot audit closed with re-measured v0.3 baseline; W2 arm run with
predictions graded IN WRITING against §2 (hits and misses both); meter
chosen or O2 fallback invoked; W3 overlay landed with lints green;
DECISIONS.md entries for the O-ruling, the rename batch, and the voice
law; suite green at root; [USER] closes asks 1–5.

---

## 7. Rulings as given (2026-07-26) — THE AUTHORITY

Asks 1–5 were put to [USER] before any code landed. Answers:

- **Ask 1 — RATIFIED as written.** O1 rejected / O2 reserve / O4 primary;
  W1→W2→W3 sequencing stands.
- **Ask 2 — RATIFIED as written.** Kurage constants ship at the proposed
  defaults (`KURAGE_DURATION` 3, `KURAGE_PULSE_BASE` 2,
  `KURAGE_PULSE_DIVISOR` 4, `KURAGE_PULSE_BLOCK` 2,
  `GARMENT_ATTACK_BLOCK` 2), all as exercised knobs.
- **Ask 3 — RATIFIED as written.** Meter bracket 15/20/25 for W2; chosen
  meter ratified on the 500-run confirm.
- **Ask 4 — RULED, with two departures from the draft:**
  - Relic becomes **"Pearl of Wisdom"**, NOT "Everlasting Moonglow". The
    §3 conditional therefore resolves against `epiphany_of_the_deep`,
    which needs a different candidate — brought to the W3 audit.
  - Raiden **keeps "Musou no Hitotachi"**; the reconciliation gloss lands
    and the "bitterest irony" framing is retired.
  - The optional third private-characterization rename **LANDS**:
    `undertow_shuffle` → "Daydream of a Quiet Life".
  - All other §3 renames proceed as drafted, subject to the wiki
    re-verify.
- **Ask 5 — CONFIRMED.** 35–50% is the target neighbourhood for
  prediction (c); Furina 57 / IC 59 are ceiling-side reference, not
  requirement.

### Measurement convention (established in W1, binding for this sprint)

The v0.3 numbers of record (priest 32% act-1 / 2.0% run; commander 49% /
1.6%; generic 26% / 0.4%; assist 20% / 0.0%) are **`--realistic`**
numbers at **500 runs, default seed**:

```
python -m tier05.runner --character kokomi --archetype <plan> \
    --runs 500 --realistic
```

The committed world reproduces those four pairs exactly under that
invocation. A **bare-loadout** run of the same committed world reads
priest 3% / commander 4% act-1 — the relic/potion layer is most of the
act-1 clear. Any v0.4 number compared against the v0.3 record must use
`--realistic` or it is comparing two different worlds.

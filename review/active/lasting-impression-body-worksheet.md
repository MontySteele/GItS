# `lasting_impression` body worksheet — commissioned at the R130 sitting

**The commission (S4-G9 item 7, [USER] 2026-08-07: "Agree, needs a rework"):**
the card's scaling line effectively deleted with the invisible-rule world —
`raise_fanfare_cap +5` is headroom on a ceiling read-at-cap measures under 1%
of turns reaching, and `gain_encore 4` alone is a body no common needs a
sitting for. The track's own text: "what this card needs is a body, and that
is a ruling." This worksheet proposes reader-clause bodies; the pick is
[USER]'s (QUEUE `S4-G9r`).

**Shipped shape** (`docs/furina-cards.yaml:210-211`): cost 1 skill, common,
fanfare, exhaust — `raise_fanfare_cap 5` + `gain_encore 4`. Upgrade
`{fanfare_cap: +2}`.

**Constraints the candidates honour:** R6 (a full Fanfare-floor grant is a
rare-POWER payoff — a common cannot print it); the ratified commons tier
rate (readers at `1_per_4_fanfare`, never the payoff slots' `1_per_2` —
R130 item 6); the ratified reader clamp (R130 item 5); cost 1 / common /
exhaust unchanged (the sitting commissioned a body, not a reprice).

## Candidate A — the Block reader (recommended)

`effects: [raise_fanfare_cap 5, gain_encore 4, block 0 + 1_per_4_fanfare]`

The exact clause the Track 2.4 veto took OFF the starter, landing where the
brief always wanted reader density: a non-starter common that only fanfare
decks draft. At the meter's working range (~12–16) it pays 3–4 Block — a
real body at common, and the card finally touches the meter it raises.
Upgrade re-derivation: keep `{fanfare_cap: +2}`, or move to `{encore: +2}`
if the cap delta reads as dead weight after measurement.
Cost: zero new grammar (the clause exists on three shipped commons).

## Candidate B — the Encore reader

`effects: [raise_fanfare_cap 5, gain_encore 2 + 1_per_4_fanfare]`

The flat 4 becomes a scaling line: 2 at an empty meter, 5–6 in range. The
"impression" compounds — Encore now, more Encore the louder the crowd. The
self-synergy with its own cap raise is the thematic argument; the risk is
the low end (2 Encore on turn 1 is worse than today's 4, so the card gets
drafted later than an enabler wants). Needs a grammar check: the
`bonus_formula` clause on `gain_encore` has no shipped precedent.

## Candidate C — do least: body by number

`effects: [raise_fanfare_cap 5, gain_encore 6]`

No reader clause — concede the scaling line and pay the honest flat rate
(6 ≈ the two-thirds point between `held_breath`'s 4 and the rare readers'
range). Cheapest, but it makes the card a worse `an_invitation` and leaves
the cap line as the only fanfare-facing text. Listed for completeness, not
recommended.

## Measurement before ratification (house rule: no unmeasured changes)

One rework-sim shot per candidate (the `klee_rework_sim` idiom: patch the
card index in-process), fanfare + generic arms, 150 runs each, reporting
offered/picked rate and run winrate vs shipped. The fire-rate instrument
(`exp_fanfare_compensation` NEW_READERS) takes candidate A/B's clause for
free. Numbers come back to this worksheet before the pick ratifies.

*Provenance: S4-G9 item 7 (R130 commission); read-at-cap <1% —
`effects.py` comment, attached to the D8/Fanfare instrument set per the
R130 item-1 disposition; name pending the S4-G11 lore audit.*

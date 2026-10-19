# varka-next, 2026-10-19: Boreas's Fang pays Pyro 5

Varka is a Balance kit, so his rules on `main` are frozen. This change is
staged on the `varka-fang-next` branch and reaches `main` only through a
promotion PR that carries the suite record: the kit on the base-five baseline
seeds through act 3, plus the telemetry report, with each prediction below
graded (`docs/current/operations/stage-gate.md`; `docs/current/EXPERIMENTS.md`,
"Kit balance is measured on the real game": one line per change, in its own
paper, written before the suite runs).

**Ruled 2026-10-19.** [USER]: "Yeah, let's do (a) all around and then test
the impact of the relic overall."

- Pick 1 (a): the Fang's Pyro payout goes from 3 to 5 damage to the enemy
  Swirled. Electro (3 to ALL), Hydro (3 Block) and Cryo (1 Vulnerable) are
  unchanged.
- Pick 2 (a): Cryo stays and gets measured; the run telemetry tags every Fang
  payout.
- Pick 3 (a): this staging branch, the predictions below written down first,
  then a five-seat suite.

## 1. The Pyro payout, 3 to 5

`VarkaLaw.SwirlPyroDamage` (C#) and `SWIRL_PYRO_DAMAGE` (the sim,
`tier0/engine/varka_oath.py`) are both 5; `tools/lint_constant_parity.py`
holds them equal. Every face that names it reads the constant: the Pyro Oath
badge ("Your Swirls deal 5 damage to that enemy."), the current-element tip,
the Swirl preview's "Swirl pays Pyro: 5 damage" line (#1483), and Twin Gales'
seat-page line. The seat page's own copy (`understudy/blindplay_board.py`,
`blindplay_notes.py`) and the English localization reference follow.

The baseline, from a census of his telemetry before the change (14 runs from
round 5 on 2026-10-13 to 2026-10-19, 316 fights, 866 Swirls): Pyro was current
for 18.6% of Swirls and paid 3.0 each; Electro paid 4.49 a Swirl (1.46 enemies
alive on average), Hydro 3.03 Block, Cryo 1.01 Vulnerable. The Fang's damage
was 4.1% of his total (1,869 of 45,573). At the same Pyro share, +2 a Pyro
Swirl adds about 320 damage over those runs, under one percentage point.

## 2. Fang telemetry

The fight record gains six fields for a Varka seat (`PlayTelemetry`, its
"Boreas's Fang" section; `understudy/README.md` names them):
`fang_payouts_by_element`, `fang_damage_by_element`, `fang_damage_blocked`,
`fang_block`, `fang_vulnerable` and `fang_vulnerable_bonus_damage`. Every
older field is unchanged; the payout's damage still files under `"(Swirl)"`
in `damage_by_source`. `tools/telemetry_report.py --tempo` prints the payouts
per element, the damage, Block and Vulnerable per payout, and the Fang's
share of damage dealt.

The Vulnerable bonus rule: a hit any seat is credited with on an enemy wearing
Vulnerable is read as 1.5x, so its bonus is the hit minus the hit over 1.5
(HP plus Block, the `amp_bonus_damage` rule). The Fang gets the share of that
enemy's stacks it put there; when the stacks fall (the turn-end decay) its
count falls in the same ratio, and stacks from another source dilute it.

## Predictions

Graded by the suite on the five baseline seeds, against the last Varka suite
(`review/records/varka-next-suite-1-2026-10-15.md`: end floors 40, won, 48,
48, won).

- **P1.** Pyro-current Fang payouts average 5.0 damage a payout (nominal;
  read off `fang_damage_by_element` over `fang_payouts_by_element`, so
  overkill, enemy Block and kills by the Swirl itself pull it below 5 and
  Vulnerable pushes it above).
- **P2.** Varka's end floors on the five seeds stay within the range of
  suite 1; no seed ends more than one act below its suite-1 floor.
- **P3.** The Fang's share of Varka's total damage rises by under 2
  percentage points from the 4.1% baseline.
- **P4** (descriptive, no threshold). The Vulnerable bonus damage per Cryo
  payout is reported.

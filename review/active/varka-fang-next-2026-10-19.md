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

## 3. The power upgrade pass (added 2026-10-19)

[USER], 2026-10-19: "You do have a habit of making too many powers just
decrease their cost by 1 on upgrade though" and "Since we're already planning
a Varka run, I'm fine with doing a Powers pass on him now."

The census before the pass: of Varka's 23 Power upgrades, 10 were Innate only
and 4 were a cost cut only. Base Ironclad has 2 Innate-only and 4 cost-only of
17; Silent 3 and 3 of 18. After the pass Varka has 3 and 3: Boreas Unbound,
Twin Gales and Azure Fang's Oath keep Innate; Retaliating Tide, Oathbound
Aegis and The Order Answers keep their cost cut.

The eight upgrades that changed (the upgraded text is in brackets):

| Card | Was | Now |
|---|---|---|
| Unwavering Banner | Innate | "gain 1 [2] Oath of your current element instead" |
| Wildfire Oath | Innate | "deal damage equal to your Pyro Oath [plus 3] to it" |
| Absolute Zero | Innate | "deal damage equal to your Cryo Oath [plus 3] to it" |
| Lupical | Innate | "shuffle [an upgraded] copy of it into your Draw Pile" |
| Weathervane | Innate | "It becomes your current element. [Gain 1 Oath of it.]" (the brief's "[and you gain 1 Oath of it]", shortened to fit the 20-character upgrade-clause lint) |
| Eye of Stormterror | Innate | "The first 3 [4] times you Swirl each turn, draw 1 card." |
| West Wind's Blessing (co-op) | Innate | "each other player gains 1 Energy [and draws 1 card]" |
| Comrades of the Expedition (co-op) | cost 2 [1] | "gain 1 [2] Oath of your current element" |

Each of the seven is ONE power per card, so a plain and an upgraded copy
show one badge (`UpgradeTwinPower`, the icon declutter's shape: Amount is
every copy, `UpgradedCopies` the upgraded ones). Each copy adds its own:

- Unwavering Banner: a held switch pays 1 per plain copy and 2 per upgraded
  copy, once a play (plain plus upgraded pays 3; two plain copies now pay 2,
  where the old one-of-a-kind Banner paid 1).
- Wildfire Oath, Absolute Zero: still one hit per application; the Oath per
  copy (a second copy doubles, as before) plus 3 per upgraded copy.
- Lupical: one shuffled copy per copy, as before; an upgraded copy's is
  always upgraded, a plain copy's follows the played card.
- Weathervane: one choice a turn however many copies; a chosen element gains
  1 Oath per upgraded copy, none on a cancel.
- Eye of Stormterror: every copy draws 1 on each of the first 3 Swirls a
  turn, as before; upgraded copies also draw on the 4th.
- West Wind's Blessing: the energy is 1 per copy, as before; each upgraded
  copy also draws each other player 1 card.

Comrades is a stack bump (`power_amount`). Eye of Stormterror's 4 is
`VarkaLaw.EyeOfStormterrorSwirlsUpgraded`, which
`tools/lint_constant_parity.py` holds equal to the sim's. The sim (`tier0/engine/varka_oath.py`) counts the
upgraded copies under `_plus` names. Tests: `VarkaPowerUpgradeTests` (C#),
`tier0/tests/test_varka_power_upgrades.py` (sim).

- **P5.** Upgrade pass: no single upgraded power changes Varka's end floors on
  the suite seeds on its own; the suite's floors stay within his last
  Varka-next suite range (P2 covers it).
- **P6** (descriptive, no threshold). The suite reports how often each of the
  eight changed powers was taken and how often it was upgraded.

## 4. The rarity sweep (added 2026-10-19)

[USER], 2026-10-19: "I had not noticed that Varka's powers are basically all
rares. Can we do a sweep over that now as well?" Rarity moves only; no number
or text changed.

- Rare to Uncommon (Powers): Converging Winds, Dawn Wind's March, Weathervane.
- Uncommon to Rare (Skills): Grand Master's Order, Rally to the Banner.

The census before the sweep: Rare 25 = 16 Powers (2 of them co-op) + 8
Attacks + 1 Skill; Uncommon 38 = 7 Powers + 11 Attacks + 20 Skills. The base
characters (the `game_ref` pools) have 9 to 10 Rare Powers, 5 to 11 Rare
Skills and 20 to 27 Rares. After: Rare 24 (13 Powers, 8 Attacks, 3 Skills),
Uncommon 39 (10 Powers). His 78-card solo pool goes from 20 / 35 / 23 to
20 / 36 / 22 (`PoolCountTests`, `STATE.md`).

- **P7** (descriptive, no threshold). The suite reports how often each of the
  five moved cards was offered and how often it was taken.

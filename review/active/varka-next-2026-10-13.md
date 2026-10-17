# varka-next, 2026-10-13: two card changes from round 5

Varka is a Balance kit, so his cards on `main` are frozen. These two changes
are staged on the `varka-next` branch and reach `main` only through a
promotion PR that carries the suite record: the kit on the base-five baseline
seeds through act 3, plus the telemetry report, with each prediction below
graded (`docs/current/operations/stage-gate.md`). The source is
`review/records/varka-round-5-2026-10-13.md`, "What to change" 3 and 4.

## 1. Eula: Icetide Vortex becomes an Attack

`proto_vk_eula_icetide_vortex` was a Skill that only deals damage. The other
damage Knights (Kaeya: Heart of the Abyss, Amber: Sharpshooter, Diluc) are
Attacks. Its cost (1) and numbers (8 [11] Cryo damage, 1 Cryo Oath for each
enemy with a Cryo aura) are unchanged. Source: lane 1.

What changes in the game: anything that counts or boosts Attacks now sees it.
That covers Lisa: Infinite Circuit's +3 Block for each Attack played this
turn, the base game's Attack counters and Attack bonuses (relics, Vigor,
Slow), and the "no Attacks" debuffs, which now stop it. In the sim it now
deals damage as an Attack hit (`source == "attack"`). Strength does not change. The game applies
Strength to any card damage dealt as a move (`ValueProp.Move`, the
`StrengthPower` decompile), so Eula already got it as a Skill. Skill counters
stop seeing it.

**Prediction:** Eula's pick rate and its damage per play rise slightly, and
no suite metric moves by more than the suite-to-suite spread.

## 2. Twin Gales: a matched element pays twice

`proto_vk_twin_gales` (Rare Power) read "Your Swirls pay both your current
element and the element they Swirl." When the Swirled element was already
the current one, the Swirl paid once, so the card added nothing. It now
reads:

> Your Swirls also pay the element they Swirl. If it's your current element,
> it pays twice.

The rule: Boreas's Fang (or Wolf's Gravestone) pays the current element, as
before, and Twin Gales always pays the Swirled element on top. A matched
element therefore pays twice. Without a Fang, Twin Gales pays the Swirled
element once. Crosscurrent and Stormterror's Scale still multiply the whole
Swirl. The seat page's line for a matched Swirl reads "Cryo (2 Vulnerable)
twice". Source: lanes 1 and 2 (lane 2's worst card, twice).

**Prediction:** Twin Gales stops being a dead pick in a one-element deck. Its
take rate rises, and runs that hold it deal more Swirl payout damage per
fight. Each Swirl gains one extra payout of the Swirled element, and that
extra is multiplied with the rest of the Swirl: two extra payouts under
Stormterror's Scale or Crosscurrent, four with both (the two multiply,
`VarkaOath.cs`). Corrected 2026-10-15: the first wording said "at most one
payout per Swirl", which the multipliers break (GPT review, relayed by
[USER]).

## 3. Tempest Charge: a Swirl-chain finisher

`proto_vk_tempest_charge` printed Rising Gale's exact text at 1 Energy for 8
against Rising Gale's 0 for 4. Cleanup pick 1 (a), ruled 2026-10-15 ([USER]:
"we can ship the event branch; looks good to me!"): "Deal 12 [16] Anemo
damage. Costs 1 less for each Swirl this turn." (#1329)

**Prediction:** Tempest Charge is played after at least one Swirl in most of
its plays (cost 0 or less than printed), and its pick rate in the suite is no
lower than the old copy's. Varka's end floors and act-by-act HP stay within
the suite-to-suite spread; this is a role change, not a power change.

## Promoted 2026-10-15

Suite record: `review/records/varka-next-suite-1-2026-10-15.md` (2 wins, all
five runs to act 3; Eula and Tempest Charge SPLIT, Twin Gales ungraded).
[USER]: "On Varka - yes, let's promote".

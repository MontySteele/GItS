# Kokomi arm: text rewrite (from the 2026-09-25 census, `textpass/kokomi.md`)

TEXT ONLY. Numbers and behaviour stay the same, with ONE exception: Battle Plan,
below. Keep every `{Var:diff()}` token where the old text had one. The numbers
shown here are base values.

| Surface | New text |
|---|---|
| Plan tip (ForPlan) | Play the card on the [gold]Bake-Kurage[/gold] to save this for the start of your next turn instead. Plans go off in the order you made them. |
| Bake-Kurage badge (ProtoBakeKuragePower) | Enemies can't target it. It holds your [gold]Plans[/gold] until your next turn. |
| Plan badge (PendingPlansPower) | Carries out {N} [gold]Plans[/gold] at the start of your next turn, in order. |
| Opening Gambit | Deal 5 damage. [gold]Plan[/gold]: Apply 1 [gold]Vulnerable[/gold] to ALL enemies. Your next Plan deals double damage. |
| Second Wave | Gain 4 [gold]Block[/gold]. [gold]Plan[/gold]: Your next Plan is carried out twice. |
| Scout Ahead | Draw 1 card. [gold]Plan[/gold]: Draw 1 card for each Plan after this one. |
| Moon's Reflection | Choose a card in your [gold]Exhaust Pile[/gold]. Next turn, carry out its [gold]Plan[/gold], or play it if it has none. |
| Moon's Reflection prompt | Choose a card. Next turn its Plan is carried out, or it's played if it has none. |
| Read the Field | Look at the top 4 cards of your draw pile. Put 1 into your hand and the rest on the bottom. [gold]Plan[/gold]: Gain 10 [gold]Block[/gold]. |
| Breakwater | (keep the codegen's "Play on the Bake-Kurage." lead) [gold]Dusk[/gold] [gold]Plan[/gold]: Gain 5 [gold]Block[/gold], and 3 more for each Plan waiting. |
| Feint | Deal 5 damage, or 10 if a [gold]Plan[/gold] was carried out this turn. [gold]Plan[/gold]: Apply 1 [gold]Vulnerable[/gold]. |
| Feigned Retreat | Gain 6 [gold]Block[/gold]. [gold]Plan[/gold]: Deal 9 damage, or 14 if you lost no HP since playing this. |
| Chain of Command | Deal 3 damage for each [gold]Companion[/gold] you played this turn. [gold]Plan[/gold]: Deal 6 damage for each Companion you play this turn. |
| Tide Wall | Gain 4 [gold]Block[/gold]. [gold]Plan[/gold]: Gain [gold]Block[/gold] equal to the damage the enemy intends next turn. (Upgraded: "…intends next turn, plus 3.") |
| Well Laid | Deal 4 damage. Deals 4 additional damage for each debuff on the enemy. |
| Riptide | Deal 9 damage to ALL enemies. Enemies with a debuff take 4 additional damage. [gold]Plan[/gold]: Gain 1 [gold]Energy[/gold] and draw 1 card. |

- **The Plan tip's old sentences are deleted from the tip,** and nothing replaces
  them. They covered Strength folding, Vulnerable timing, "a carry-out is not a
  hit", and front non-Minion targeting. They are edge cases, and the seat glossary
  may keep a short line on targeting if a seat needs it.
- **Dusk timing is stated only in the Dusk tip.** The two badges above no longer
  repeat it.
- **Chain of Command.** The Plan is carried out next turn and counts the turn it
  was written, which is "this turn" from the player's seat. Check this against the
  code (the `last turn` counter at carry-out time). If the count is not the
  write-turn's Companions, STOP and report.
- **Battle Plan: a code fix, not a text fix.** Its ruled face (PR #649, [USER]'s
  review) is "Plan: Next turn, your Attacks deal 3 additional damage." The power it
  grants, `NextAttackDamagePower`, expires after the FIRST Attack
  (`KokomiOverhaulPowers.cs` around line 390). The face is the ruling. Make the
  Plan grant +3 to every Attack for that whole turn, the same way Coordinated
  Strike's Plan uses `AttackUpThisTurnPower`, and delete or retire
  `NextAttackDamagePower` if nothing else uses it. Mirror the change in the sim
  twin, and add a test for 2 Attacks in one turn.
